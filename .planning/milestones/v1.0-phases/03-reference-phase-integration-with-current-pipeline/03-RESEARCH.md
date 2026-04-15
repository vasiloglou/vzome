# Phase 3 Research: Reference-Phase Integration With Current Pipeline

**Phase:** 03  
**Date:** 2026-04-03  
**Goal:** Plan the bridge that turns Phase 2 staged source snapshots into the
existing processed reference-phase artifacts consumed by the current discovery
pipeline.

## Research Question

What do we need to know to plan Phase 3 well so that the team can:

- preserve `mdisc ingest --config ...` as the stable operator entrypoint
- stage or reuse canonical source snapshots through the Phase 2 runtime
- project canonical raw-source records into the existing processed
  `reference_phases.jsonl` contract
- attach source lineage to the ingest manifest
- keep the real-mode no-DFT pipeline green with richer ingested data

## Key Findings

### 1. The Phase 2 runtime is ready, but the bridge is intentionally missing

The new source runtime already stages canonical records, QA reports, and source
snapshot manifests under:

`data/external/sources/{source_key}/{snapshot_id}/`

The missing seam is explicit in the code:

- `materials_discovery.data_sources.runtime.stage_registered_source_snapshot(...)`
  exists and is usable today
- `materials_discovery.backends.registry.resolve_ingest_backend(...)` still
  raises on `source_registry_v1` and says Phase 3 will wire the bridge
- `mdisc ingest` still follows the old path:
  `load_rows -> ingest_rows -> build_manifest`

That means Phase 3 does not need another staging framework. It needs projection
plus a controlled CLI branch that uses the existing runtime.

### 2. Downstream pipeline consumers only require a small processed contract

The real-mode consumers in `hull_proxy.py` and `xrd_validate.py` only rely on
the processed JSONL containing at least:

- `phase_name`
- `composition`

They tolerate extra fields because they read raw JSON rows and pick out the
fields they need. This is important: Phase 3 can preserve the `IngestRecord`
shape while enriching `metadata` additively without rewriting downstream code.

### 3. The safest projection target is still `IngestRecord`, not a new schema

`IngestRecord(system, phase_name, composition, source, metadata)` remains the
minimal processed reference-phase contract. Replacing it in Phase 3 would add
avoidable blast radius across:

- `mdisc ingest`
- reference-phase consumers
- existing tests
- benchmark and manifest assumptions

The correct move is to add a deterministic projection module that converts
canonical staged records into `IngestRecord` rows, not to replace the processed
artifact family.

### 4. Periodic-source records need an explicit phase-label derivation policy

HYPOD-X `phase_entry` records already carry a natural phase label. Periodic
sources such as Materials Project, OQMD, JARVIS, OPTIMADE-backed providers, and
COD-derived structure records often do not.

Phase 3 therefore needs an explicit and deterministic `phase_name` derivation
policy for non-`phase_entry` records. The strongest precedence order, based on
current adapter outputs, is:

1. provider phase label in `common.reported_properties["phase_name"]`
2. provider title such as `source.record_title`
3. `common.formula_reduced`
4. `source.source_record_id`

This keeps the processed output stable and avoids special-casing one provider’s
row shape inside the old HYPOD-X normalization code.

### 5. System matching must move from string-equality to source-aware matching

The legacy ingest path filters with:

`record.system.lower() == config.system_name.lower()`

That is too narrow for the new sources because canonical records carry system
information in several places:

- `common.chemical_system`
- `common.elements`
- `common.composition`

Phase 3 needs a source-aware match helper that can accept records when:

- the normalized element set matches `config.species`
- or the provider chemical-system token normalizes to the same set

This is the key move that makes periodic crystal sources and QC/approximant
sources project into the same processed reference-phase lane.

### 6. Manifest lineage needs an additive extension, not a new manifest family for `mdisc ingest`

The standard ingest manifest is already the operator-facing artifact for the
processed output. The Phase 1 design calls for source lineage references to be
attached to that manifest in Phase 3.

The safest implementation is additive:

- keep `ArtifactManifest` as the manifest type
- add a small optional lineage/metadata field
- populate it only for the source-registry path with:
  - `source_key`
  - `snapshot_id`
  - `snapshot_manifest_path`
  - `canonical_records_path`
  - `qa_report_path`
  - projection counts or projection status

This preserves current consumers while giving operators provenance for the new
bridge path.

### 7. The bridge should branch in the CLI, not force `SourceAdapter` through the old backend interface

The legacy `IngestBackend` protocol is:

`load_rows(config, fixture) -> list[dict[str, Any]]`

That is too weak for Phase 3 because the bridge needs to:

- stage or reuse source snapshots
- access `SourceStageSummary`
- load canonical staged records
- project them to `IngestRecord`
- populate manifest lineage

Trying to make `SourceAdapter` or the source runtime impersonate the old
backend protocol would hide the important semantics. The safer design is:

- keep `source_registry_v1` as the switch
- add a CLI branch keyed on that adapter
- preserve the legacy branch for existing backends

That matches the Phase 1 integration design and keeps the old codepath intact.

### 8. Phase 3 verification should prove full pipeline compatibility, not just ingest success

`PIPE-01` requires the current pipeline to remain green while ingesting richer
external data. That means a good Phase 3 verification set must cover:

- source-registry ingest success
- legacy ingest compatibility
- downstream reference-phase consumers
- at least one end-to-end real-mode ingest -> report smoke using the bridge

The existing `test_real_mode_pipeline.py` is the strongest base for this. It
should be extended or complemented with a source-backed ingest configuration
using offline fixtures or inline payloads.

## Recommended Implementation Shape

### Package and file shape

Phase 3 should add one new module and extend a small number of existing seams:

```text
materials_discovery/
  data_sources/
    projection.py          canonical source records -> IngestRecord rows
  backends/
    registry.py           bridge detection helper; keep reserved adapter
  common/
    schema.py             additive manifest lineage and projection metadata support
    manifest.py           optional lineage-aware manifest builder
  cli.py                  bridge branch in ingest command
```

### Projection responsibilities

`data_sources/projection.py` should own:

- canonical-record filtering for one target system
- deterministic `phase_name` derivation
- source-aware composition normalization
- structure/QC tag extraction into `IngestRecord.metadata`
- dedupe and stable ordering for projected `IngestRecord` rows
- projection summary counts for manifest lineage and CLI summaries

It should not:

- fetch provider data
- write source staging artifacts
- call downstream validation code

### Processed metadata recommendations

The projection layer should preserve richer context in `IngestRecord.metadata`
using additive keys such as:

- `local_record_id`
- `source_key`
- `source_record_id`
- `source_record_url`
- `snapshot_id`
- `adapter_key`
- `record_kind`
- `structure_tags`
- `qc_family`
- `projection_reason`
- `license_category`

This lets the pipeline remain backward-compatible while future phases can start
using richer source context if needed.

## Main Risks

### Risk 1: Projection logic reintroduces HYPOD-X coupling

If Phase 3 reuses `data.normalize.normalize_raw_record(...)` for all providers,
the system will collapse back into the old row-shape assumption.

**Recommendation:** keep projection in `data_sources/projection.py` and map from
canonical source records directly to `IngestRecord`.

### Risk 2: Manifest lineage is bolted on outside the standard ingest manifest

If source provenance only lives in the source snapshot directory, operators will
lose traceability from the main ingest result.

**Recommendation:** add lineage references directly to the standard ingest
manifest as an additive field.

### Risk 3: Structure-rich sources produce unstable or low-value phase labels

If projected `phase_name` values drift run-to-run, downstream tests and
human-readable reference-phase inspection will become noisy.

**Recommendation:** codify a deterministic fallback precedence and test it.

### Risk 4: The bridge path passes ingest tests but breaks real-mode pipeline behavior

The downstream pipeline only surfaces ingest problems later, especially when
reference phases drive hull/XRD behavior.

**Recommendation:** add an end-to-end real-mode source-bridge smoke test plus
targeted `hull_proxy` compatibility checks.

### Risk 5: Scope creep pulls new simulation or online fetches into ingest

Phase 3 is only about fetch/stage/project/provenance on the ingest side.

**Recommendation:** keep tests offline, require source snapshots or inline
payloads for verification, and avoid calling any high-fidelity backends inside
the new ingest branch.

## Recommended Plan Split

### Plan 01 — Projection Core

- add `data_sources/projection.py`
- define deterministic system matching and phase-name derivation
- project canonical records into `IngestRecord`
- lock projection behavior with focused tests

### Plan 02 — CLI Bridge And Manifest Lineage

- wire `source_registry_v1` into `mdisc ingest`
- stage/reuse source snapshots, load canonical records, project them, and write
  the processed JSONL
- add additive source lineage fields to the standard ingest manifest
- prove legacy and bridge paths both work

### Plan 03 — Pipeline Compatibility And Guardrails

- add source-backed offline ingest fixtures/config generation for tests
- prove end-to-end pipeline compatibility through the bridge
- add targeted regression coverage for downstream reference-phase consumers
- verify the no-DFT boundary stays explicit

