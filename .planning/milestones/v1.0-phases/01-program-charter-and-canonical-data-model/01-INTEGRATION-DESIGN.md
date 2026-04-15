# Integration Design For The Current Pipeline

## Goal

Define how the new multi-source ingestion layer fits into the existing
`materials-discovery` subsystem without breaking:

- the file-backed execution model
- the documented `mdisc ingest` operator entrypoint
- the current processed reference-phase contract
- the explicit no-DFT boundary in required workflows

This document describes the Phase 2 and Phase 3 seams, not the final code.

## Current Ingest Seam

The current implementation is intentionally narrow and HYPOD-X-shaped.

### Actual call chain in `cli.py`

Today `mdisc ingest` performs this flow:

```text
resolve_ingest_backend(mode, ingest_adapter)
  -> backend.info()
  -> backend.load_rows(system_config, fixture)
  -> ingest_rows(system_config, raw_rows, out_path, ...)
  -> build_manifest(stage="ingest", ...)
  -> write data/processed/{slug}_reference_phases.jsonl
```

### What the current seam assumes

The current seam works because the existing ingest protocol is extremely small:

- `backends.types.IngestBackend.load_rows(...) -> list[dict[str, Any]]`
- `data.normalize.normalize_raw_record(...) -> IngestRecord`
- `data.ingest_hypodx.ingest_rows(...)` filters by `system_name`, deduplicates,
  runs QA, and writes processed JSONL

This is the right seam for:

- fixtures
- pinned HYPOD-X snapshots
- a processed reference-phase output

It is not the right seam for a general raw-source staging system because it
assumes provider rows can jump almost directly into the current
`IngestRecord(system, phase_name, composition, source, metadata)` shape.

## Design Principles

### 1. Preserve the operator surface

`mdisc ingest` remains the stable entrypoint. The user should not need to learn
a parallel primary CLI just because the source layer becomes more capable.

### 2. Add a new package boundary instead of overloading old ones

The new source-ingestion stack should live under:

```text
materials-discovery/src/materials_discovery/data_sources/
```

This follows the discuss-phase decision to keep external dataset adapters out of
the current `backends/` and `data/` package trees.

### 3. Keep `backends/` focused on runtime execution modes

`backends/` already owns mock, pinned real, exec, and native execution
selection. It should not become the full registry for dozens of external data
providers.

### 4. Keep the source layer file-backed

Source ingestion should write snapshots, manifests, QA reports, and canonical
JSONL artifacts to disk, just like the rest of the subsystem.

### 5. Keep the no-DFT boundary explicit

Source ingestion may fetch provider-supplied computed values, structures, and
metadata. It must not perform new DFT or high-fidelity simulation work as part
of required ingestion flows.

## Recommended Package Layout

```text
materials_discovery/
  data_sources/
    schema.py              Canonical raw-source models and source manifests
    types.py               Source adapter protocols and info dataclasses
    registry.py            Source registry and adapter resolution by source key
    storage.py             Snapshot paths, attachment storage, hash helpers
    qa.py                  Canonical QA metrics and schema drift checks
    projection.py          Canonical raw-source -> pipeline-ready projection
    manifests.py           Source-specific manifest builders/writers
    adapters/
      hypodx.py
      cod.py
      materials_project.py
      oqmd.py
      jarvis.py
      optimade.py
      cif_conversion.py
      manual_import.py
```

### Role split

| Package | Responsibility | What it should not do |
|---|---|---|
| `data_sources/` | Fetch, snapshot, normalize, QA, and project external data | Own screen/hifi execution or candidate generation |
| `backends/` | Select runtime execution mode adapters for the existing pipeline and a thin ingest bridge | Become the master registry for provider-specific source logic |
| `data/` | Legacy HYPOD-X-shaped ingest helpers and pipeline stage logic | Host the new general source adapter taxonomy |
| `common/` | Shared runtime schemas, IO helpers, and manifest primitives | Immediately absorb the entire raw-source contract before it stabilizes |

## Recommended Filesystem Layout

The new source layer should stay inside the existing workspace-root-relative
artifact model.

```text
data/
  external/
    fixtures/
    pinned/
    sources/
      {source_key}/
        {snapshot_id}/
          snapshot_manifest.json
          raw_rows.jsonl
          canonical_records.jsonl
          qa_report.json
          attachments/
            ...
  processed/
    {system_slug}_reference_phases.jsonl
  manifests/
    {system_slug}_ingest_manifest.json
    source_{source_key}_{snapshot_id}_project_manifest.json
```

### Layout decisions

- Keep source snapshots under `data/external/sources/` because they are external
  provider artifacts, analogous to fixtures and pinned inputs.
- Keep processed reference-phase outputs in `data/processed/`, unchanged.
- Keep operator-facing stage manifests in `data/manifests/`, unchanged.
- Do not reuse `data/registry/` for large source snapshots. That directory
  already has a different role in the current subsystem.

## Manifest Strategy

The current subsystem already uses JSON manifests with hashes, run IDs, config
hashes, and backend version info. The new source layer should follow that style
instead of inventing a different state model.

### New source-side manifests

Phase 2 should add a source-specific manifest model, for example
`SourceSnapshotManifest`, with at least:

- `manifest_id`
- `stage` such as `source_fetch`, `source_normalize`, `source_project`
- `source_key`
- `snapshot_id`
- `adapter_key`
- `adapter_version`
- `created_at_utc`
- `output_hashes`
- `record_counts`
- `license_summary`
- `qa_summary`
- `parent_manifest_id`

### How it connects to existing manifests

- Source fetch and normalization manifests live with the snapshot under
  `data/external/sources/{source_key}/{snapshot_id}/`.
- The existing `mdisc ingest` manifest in `data/manifests/` remains the
  operator-facing manifest for processed reference-phase output.
- That ingest manifest should gain lineage references to the relevant source
  snapshot and projection manifests in Phase 3.

This preserves the manifest habit already established in
`common/manifest.py` without pretending that source fetches are the same thing
as current pipeline stage executions.

## CLI Integration Path

### Phase 2: add the source layer without changing the operator contract

Phase 2 should implement the new `data_sources/` package and allow staged source
snapshots to be created and validated, but it does not need to expose a new
primary CLI to users.

Possible internal flow:

```text
data_sources registry
  -> source adapter fetches snapshot
  -> raw_rows.jsonl
  -> canonical_records.jsonl
  -> qa_report.json
  -> snapshot_manifest.json
```

This can be driven by internal library calls or by a future helper command, but
the main operator promise remains that `mdisc ingest` is the stable front door.

### Phase 3: bridge staged source data into `mdisc ingest`

Phase 3 should preserve the same command:

```text
mdisc ingest --config ...
```

but branch the implementation internally:

```text
if legacy HYPOD-X ingest backend:
    backend.load_rows(...)
    ingest_rows(...)
else if source-registry bridge backend:
    stage or reuse canonical source snapshot
    project canonical_records -> reference-phase records
    write data/processed/{slug}_reference_phases.jsonl
    write standard ingest manifest with source lineage references
```

This is the critical compatibility move: keep the CLI stable while admitting
that the current `load_rows -> normalize_raw_record -> IngestRecord` chain is
too narrow for multi-source ingestion.

## Recommended Config Extension

The cleanest additive schema change is to introduce an optional sibling block to
`backend`, rather than overloading `BackendConfig` with provider-specific query
details.

Recommended direction:

```yaml
system_name: Al-Cu-Fe
template_family: icosahedral_approximant_1_1
species: [Al, Cu, Fe]
composition_bounds: ...
coeff_bounds: ...
seed: 17
default_count: 100

backend:
  mode: real
  ingest_adapter: source_registry_v1

ingestion:
  source_key: materials_project
  snapshot_id: materials_project_2026_04_02_api_default
  adapter_profile: direct_api_default
  reuse_snapshot: true
  source_options: {}
```

Why this is better than packing everything into `BackendConfig`:

- `BackendConfig` currently models runtime execution mode selection.
- Source selection, snapshot reuse, and provider-specific options are a
  different concern.
- An additive `ingestion` block keeps current configs valid and preserves the
  current `SystemConfig` style.

## Role Of `data_sources/` Versus `backends/`

### `data_sources/`

- owns the provider registry
- owns adapter family taxonomy
- owns canonical raw-source schemas
- owns source-specific QA and schema-drift checks
- owns raw snapshot and canonical artifact layout

### `backends/`

- keeps the current `(mode, adapter_name)` resolution pattern
- keeps mock and pinned ingest for current fixtures and regressions
- may gain one or a few bridge adapters such as `source_registry_v1`
- should not gain one registry entry per external provider

This boundary keeps the current `backends/registry.py` from becoming a second
source catalog under the wrong abstraction.

## Walkthrough Against Current Code Seams

### `cli.py`

Current behavior:

- loads `SystemConfig`
- resolves an `IngestBackend`
- calls `backend.load_rows(...)`
- calls `ingest_rows(...)`
- writes the ingest manifest

Design implication:

- keep the command and output path contract
- add an internal branch for staged canonical-source projection
- keep error handling and JSON summary behavior unchanged

### `backends/registry.py`

Current behavior:

- maps `(mode, adapter_name)` to concrete ingest and validation adapters
- defaults `mock` to `hypodx_fixture`
- defaults `real` to `hypodx_pinned_v2026_03_09`

Design implication:

- keep this file focused on runtime mode dispatch
- add at most a thin bridge backend such as `source_registry_v1`
- do not register `materials_project`, `oqmd`, `jarvis`, `cod`, and every
  future provider directly in this table

### `data/ingest_hypodx.py`

Current behavior:

- accepts already-loaded provider rows
- normalizes them through the current HYPOD-X-shaped path
- filters on `system_name`
- deduplicates by `(system, phase_name, composition)`
- writes processed JSONL

Design implication:

- preserve this as the legacy ingest path and regression anchor
- do not generalize it into the canonical raw-source staging layer
- move future provider-specific normalization into `data_sources/`

### `data/normalize.py`

Current behavior:

- expects fields like `system`, `alloy_system`, `phase_name`, and `composition`
- produces `IngestRecord`

Design implication:

- this logic is intentionally source-specific
- forcing COD, Materials Project, OQMD, and JARVIS into this pre-shape would
  recreate HYPOD-X coupling

### `common/schema.py`

Current behavior:

- owns `SystemConfig`, `BackendConfig`, `CandidateRecord`, `IngestRecord`, and
  summary/manifest models

Design implication:

- keep `IngestRecord` as the processed reference-phase contract for now
- add raw-source schemas under `data_sources/schema.py`
- promote shared enums or helpers into `common/` only after the new contract is
  proven stable

## Migration Story

### Step 1: preserve the old path

Keep these working unchanged:

- `hypodx_fixture`
- `hypodx_pinned_v2026_03_09`
- current processed JSONL output path
- current ingest summary and manifest style

### Step 2: add canonical source staging beside it

Phase 2 introduces:

- source adapters under `data_sources/adapters/`
- canonical raw-source records
- source QA reports
- snapshot manifests

At this point the source layer can mature without forcing a rewrite of the
operator-facing ingest command.

### Step 3: add a projection bridge

Phase 3 adds:

- canonical raw-source to reference-phase projection logic
- optional `ingestion` config block
- one bridge path inside `mdisc ingest`

This is when `mdisc ingest` begins using the new source layer behind the same
user-facing command.

### Step 4: keep the no-DFT contract intact

After the bridge lands:

- ingestion still ends at processed reference-phase artifacts
- screening and hifi stages remain the place where validation and ranking occur
- any source-provided energies or metadata remain provenance fields, not new
  required computations

## Highest-Risk Compatibility Points

| Risk | Why it matters | Mitigation |
|---|---|---|
| Overloading `IngestBackend` | The current protocol only returns `list[dict]`, which is too weak for canonical staging | Add a dedicated `SourceAdapter` protocol under `data_sources/types.py` |
| Polluting `backends/registry.py` with provider entries | The abstraction is about execution modes, not provider inventory | Keep provider registry in `data_sources/registry.py`; use only a thin bridge in `backends/` |
| Breaking current config files | Existing YAMLs already validate under `SystemConfig` | Make `ingestion` optional and additive |
| Manifest divergence | The repo already relies on manifests for reproducibility | Reuse the current JSON+hash style and link source manifests into the ingest manifest |
| Structure-format fragmentation | COD, OPTIMADE, MP, OQMD, and JARVIS will not expose identical structure payloads | Keep multiple `structure_representations` in the canonical contract and normalize only what Phase 3 needs |
| Accidental DFT creep | Some sources include computed properties and can tempt scope drift | Keep ingestion as fetch, normalize, QA, and project only |

## Recommended Phase Boundaries

### Phase 2 should deliver

- `data_sources/` package skeleton
- source adapter protocol and registry
- canonical raw-source models
- snapshot storage and QA/reporting
- first-wave adapters

### Phase 3 should deliver

- reference-phase projection from canonical source records
- `mdisc ingest` bridge integration
- source lineage attached to the standard ingest manifest
- preserved operator-facing CLI and no-DFT boundary

## Requirement Alignment

| Requirement | How this design satisfies it |
|---|---|
| `DATA-01` | Leaves a clean path for multiple source families to feed a canonical staging layer |
| `DATA-02` | Preserves provenance, snapshot, license, and lineage as first-class staged artifacts |
| `OPS-03` | Keeps ingestion and projection on the no-DFT side of the system boundary |
| `OPS-04` | Preserves the current `mdisc ingest` CLI while making the new source layer additive |

