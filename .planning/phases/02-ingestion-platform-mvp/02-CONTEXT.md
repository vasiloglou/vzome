# Phase 2: Ingestion Platform MVP - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning
**Source:** Derived from roadmap, Phase 1 design artifacts, and current repo architecture

<domain>
## Phase Boundary

Implement the first reusable ingestion framework for external materials-data
sources inside `materials-discovery/`. This phase should land the runtime
package structure, adapter interfaces, provider registry wiring, QA reporting,
and the first wave of source adapters needed to prove the canonical raw-source
staging model from Phase 1.

This phase is an implementation phase. It should create executable code and
tests for the ingestion platform MVP, but it should not yet replace the current
operator-facing `mdisc ingest` behavior end to end. Full normalization into
pipeline-ready reference phases belongs to Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Locked architecture from Phase 1
- **D-01:** The new multi-source ingestion runtime must live under
  `materials_discovery/data_sources/`.
- **D-02:** The canonical raw-source contract must stay separate from the
  existing processed `IngestRecord` contract in `common/schema.py` during this
  phase.
- **D-03:** `mdisc ingest` remains the stable operator-facing CLI entrypoint.
  Phase 2 may add new internal code paths, manifests, and config fields, but it
  must not break the existing CLI contract.
- **D-04:** `backends/` remains a thin runtime-mode bridge rather than becoming
  the home for provider-specific source ingestion logic.
- **D-05:** The Phase 2 source priority is locked to `HYPOD-X`, `COD`,
  `Materials Project`, `OQMD`, and `JARVIS`.
- **D-06:** The adapter posture is mixed by design:
  `HYPOD-X` should use a snapshot-oriented direct path,
  `COD` should use CIF/structure-conversion handling,
  `Materials Project` should use a direct API path,
  `OQMD` should keep both direct and OPTIMADE-compatible room in the design,
  and `JARVIS` can use either direct or OPTIMADE depending on runtime maturity.

### Scope for this phase
- **D-07:** The Phase 2 MVP must satisfy `DATA-03`, `DATA-04`, and `OPS-04`.
- **D-08:** The MVP should create one shared adapter interface that supports
  source listing, fetch/load, normalization into canonical raw-source records,
  and provenance capture.
- **D-09:** The MVP should include one first-class OPTIMADE adapter path, even
  if not every Phase 2 source uses OPTIMADE as its primary implementation.
- **D-10:** The MVP must emit QA artifacts that cover duplicates, missing core
  fields, invalid compositions, malformed structures, and schema drift against
  the canonical raw-source contract.
- **D-11:** The MVP should preserve the existing file-backed operator model:
  JSON/JSONL artifacts under `data/`, manifests under `data/manifests/`, and no
  database dependency.

### Compatibility and migration
- **D-12:** Existing HYPOD-X ingest behavior is the regression anchor. New code
  should generalize it without losing the current fixture/pinned workflow.
- **D-13:** The new runtime code may extend configuration and backend selection,
  but changes should be additive and default-safe for existing system configs.
- **D-14:** Phase 2 should build the raw-source staging and QA layer needed for
  Phase 3 normalization into pipeline-compatible reference phases; it should not
  collapse raw-source records directly into `IngestRecord`.
- **D-15:** Tests should emphasize adapter contracts, canonical raw-source
  schema validation, QA metric behavior, registry resolution, and CLI
  compatibility.

### the agent's Discretion
- The exact split between `data_sources/schema.py`, `data_sources/registry.py`,
  `data_sources/optimade.py`, and provider modules
- Whether the first OPTIMADE path is implemented as a reusable client wrapper,
  a concrete adapter base class, or both
- The exact CLI/config extension for choosing source adapters and raw-source
  staging outputs, so long as current configs remain compatible
- The exact QA report file shape, as long as the required metrics and manifest
  lineage are explicit

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 1 design authority
- `.planning/phases/01-program-charter-and-canonical-data-model/01-DATA-CONTRACT.md` — canonical raw-source record and mandatory provenance/license/QA fields
- `.planning/phases/01-program-charter-and-canonical-data-model/01-SOURCE-REGISTRY.md` — provider priority, adapter-family mapping, and tooling inventory
- `.planning/phases/01-program-charter-and-canonical-data-model/01-INTEGRATION-DESIGN.md` — package layout, artifact layout, and `mdisc ingest` bridge design
- `.planning/phases/01-program-charter-and-canonical-data-model/01-RESEARCH.md` — broader provider and tooling landscape

### Program controls
- `.planning/PROJECT.md` — program framing and constraints
- `.planning/ROADMAP.md` — Phase 2 goal, deliverables, and sequencing
- `.planning/REQUIREMENTS.md` — `DATA-03`, `DATA-04`, and `OPS-04`
- `.planning/STATE.md` — current milestone and phase history

### Existing subsystem and runtime seams
- `materials-discovery/README.md` — current CLI/operator summary
- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md` — existing real-mode hardening constraints
- `materials-discovery/developers-docs/architecture.md` — package boundaries and artifact flow
- `materials-discovery/developers-docs/backend-system.md` — registry and adapter patterns already in use
- `materials-discovery/developers-docs/pipeline-stages.md` — ingest-stage behavior and downstream expectations
- `materials-discovery/developers-docs/configuration-reference.md` — `SystemConfig` and `BackendConfig` constraints
- `materials-discovery/developers-docs/data-schema-reference.md` — schema conventions and manifest patterns
- `materials-discovery/developers-docs/contributing.md` — repo-local development and test expectations

### Current code seams
- `materials-discovery/src/materials_discovery/cli.py` — stable CLI seam and manifest writes
- `materials-discovery/src/materials_discovery/backends/registry.py` — current runtime-mode adapter registry
- `materials-discovery/src/materials_discovery/backends/types.py` — protocol style for adapter contracts
- `materials-discovery/src/materials_discovery/common/schema.py` — existing config and processed-record schemas
- `materials-discovery/src/materials_discovery/common/io.py` — file IO helpers
- `materials-discovery/src/materials_discovery/common/manifest.py` — manifest-writing pattern
- `materials-discovery/src/materials_discovery/data/connectors/base.py` — minimal existing ingest connector seam
- `materials-discovery/src/materials_discovery/data/ingest_hypodx.py` — current narrow ingest path
- `materials-discovery/src/materials_discovery/data/normalize.py` — current HYPOD-X-shaped normalization seam
- `materials-discovery/src/materials_discovery/data/qa.py` — current QA baseline

</canonical_refs>

<specifics>
## Specific Ideas

- Start with framework-first implementation, then land provider adapters in the
  same phase rather than designing a large abstraction with no concrete users.
- Treat `HYPOD-X` as the regression anchor and `COD` plus one OPTIMADE-capable
  provider as the proof that the design is truly multi-source.
- Keep the plan concrete about files to add, tests to write, and how provider
  adapters register into runtime selection.
- Make QA outputs first-class artifacts, not just in-memory checks.

</specifics>

<deferred>
## Deferred Ideas

- Full projection of canonical raw-source records into processed
  reference-phase artifacts — Phase 3
- End-to-end pipeline benchmarking with richer data — Phase 4
- Data-lake style cross-source analytics — Phase 5
- LLM corpus extraction from external source records — Phase 6+

</deferred>

---

*Phase: 02-ingestion-platform-mvp*
*Context gathered: 2026-04-03*
