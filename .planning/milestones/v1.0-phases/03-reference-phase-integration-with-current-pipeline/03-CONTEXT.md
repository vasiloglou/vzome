# Phase 3: Reference-Phase Integration With Current Pipeline - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning
**Source:** Derived from roadmap, requirements, Phase 1 integration design,
Phase 2 implementation, and current `materials-discovery/` code seams

<domain>
## Phase Boundary

Bridge the new Phase 2 source-staging runtime into the current
`materials-discovery` ingest flow so `mdisc ingest --config ...` can turn
canonical staged source records into the existing processed reference-phase
artifact at:

`data/processed/{system_slug}_reference_phases.jsonl`

This phase should keep the current operator-facing CLI stable while making the
new ingestion layer actually feed the downstream no-DFT pipeline. It should add
projection logic, bridge wiring, manifest lineage, and compatibility coverage.
It should not introduce a database, a new primary operator command, or any new
DFT/high-fidelity computation inside ingest.

</domain>

<decisions>
## Implementation Decisions

### Locked architecture and migration decisions
- **D-01:** The reserved adapter key `source_registry_v1` is the only Phase 3
  bridge selector for the new source runtime. Existing legacy ingest adapters
  such as `hypodx_fixture` and `hypodx_pinned_v2026_03_09` must remain working.
- **D-02:** `IngestRecord` remains the processed reference-phase contract for
  this phase. Phase 3 may enrich `metadata` additively, but it must not replace
  the processed JSONL shape consumed by downstream pipeline stages.
- **D-03:** The projection seam belongs under
  `materials_discovery/data_sources/projection.py`, not inside
  `data/normalize.py` or `data/ingest_hypodx.py`.
- **D-04:** Phase 3 must reuse or stage canonical source snapshots through the
  Phase 2 runtime before projection; it should not bypass `data_sources/`.
- **D-05:** The processed output path, summary shape, exit-code behavior, and
  manifest-writing habit of `mdisc ingest` must stay compatible for both the
  legacy path and the new source-registry path.

### Projection and normalization decisions
- **D-06:** Projection must support both QC/approximant-style `phase_entry`
  records and periodic `structure` / `material_entry` records.
- **D-07:** Structure-rich records that do not carry an explicit phase label
  must still project deterministically by deriving a stable `phase_name`
  fallback from the best available source fields such as provider phase title,
  reduced formula, or source record ID.
- **D-08:** Projection must normalize composition and system matching from the
  canonical source contract rather than requiring providers to mimic the old
  HYPOD-X row shape ahead of time.
- **D-09:** Source-aware tags such as record kind, structure markers, and
  QC-family cues should be carried in additive metadata on the processed output
  so downstream stages remain backward-compatible while richer source context is
  preserved.

### Provenance and quality decisions
- **D-10:** The standard ingest manifest must gain source lineage references for
  the staged snapshot and projected processed artifact in an additive way.
- **D-11:** Phase 3 must satisfy `DATA-05`, `PIPE-01`, and `OPS-03`.
- **D-12:** New bridge tests must stay offline and deterministic. The source
  bridge may support live APIs in production, but Phase 3 verification must rely
  on local snapshot/fixture inputs or inline payloads only.

### the agent's Discretion
- The exact shape of additive lineage fields on `ArtifactManifest`
- Whether the bridge check lives in `cli.py` directly or behind a small helper
  exported from `backends/registry.py`
- The precise priority order for synthetic `phase_name` derivation for
  structure-only records, as long as it is deterministic and documented in code
- The exact names of metadata keys carrying structure tags and QC-family labels

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Program controls
- `.planning/PROJECT.md` — overall program framing and constraints
- `.planning/ROADMAP.md` — Phase 3 goal, deliverables, and sequencing
- `.planning/REQUIREMENTS.md` — `DATA-05`, `PIPE-01`, and `OPS-03`
- `.planning/STATE.md` — current phase status and handoff state

### Phase 1 design authority
- `.planning/phases/01-program-charter-and-canonical-data-model/01-DATA-CONTRACT.md` — canonical raw-source contract and mandatory provenance fields
- `.planning/phases/01-program-charter-and-canonical-data-model/01-SOURCE-REGISTRY.md` — source priorities and adapter inventory
- `.planning/phases/01-program-charter-and-canonical-data-model/01-INTEGRATION-DESIGN.md` — Phase 2/3 bridge design and artifact layout
- `.planning/phases/01-program-charter-and-canonical-data-model/01-RESEARCH.md` — broader source/tooling research

### Phase 2 implementation authority
- `.planning/phases/02-ingestion-platform-mvp/02-CONTEXT.md` — Phase 2 locked decisions
- `.planning/phases/02-ingestion-platform-mvp/02-RESEARCH.md` — runtime shape and adapter strategy
- `.planning/phases/02-ingestion-platform-mvp/02-VALIDATION.md` — current test/verification posture
- `.planning/phases/02-ingestion-platform-mvp/02-01-PLAN.md` — runtime foundation decisions and file seams
- `.planning/phases/02-ingestion-platform-mvp/02-02-PLAN.md` — HYPOD-X/COD staging design
- `.planning/phases/02-ingestion-platform-mvp/02-03-PLAN.md` — direct API and OPTIMADE adapter design

### Existing subsystem docs
- `materials-discovery/README.md` — current operator summary
- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md` — existing real-mode constraints and expectations
- `materials-discovery/developers-docs/architecture.md` — package and artifact flow
- `materials-discovery/developers-docs/backend-system.md` — adapter/registry patterns already in use
- `materials-discovery/developers-docs/pipeline-stages.md` — current ingest command behavior and downstream dependencies
- `materials-discovery/developers-docs/configuration-reference.md` — `SystemConfig` and backend config expectations
- `materials-discovery/developers-docs/data-schema-reference.md` — schema and manifest conventions

### Current code seams
- `materials-discovery/src/materials_discovery/cli.py` — stable ingest command and manifest-writing path
- `materials-discovery/src/materials_discovery/backends/registry.py` — reserved `source_registry_v1` bridge key and current legacy branch
- `materials-discovery/src/materials_discovery/common/schema.py` — `SystemConfig`, `IngestRecord`, `IngestSummary`, and `ArtifactManifest`
- `materials-discovery/src/materials_discovery/common/manifest.py` — standard manifest builder/writer
- `materials-discovery/src/materials_discovery/data/ingest_hypodx.py` — legacy ingest normalization + QA path
- `materials-discovery/src/materials_discovery/data/normalize.py` — HYPOD-X-shaped processed normalization seam
- `materials-discovery/src/materials_discovery/data_sources/runtime.py` — Phase 2 source staging orchestration
- `materials-discovery/src/materials_discovery/data_sources/registry.py` — source adapter registry and reserved bridge key
- `materials-discovery/src/materials_discovery/data_sources/schema.py` — canonical raw-source records and stage summary models
- `materials-discovery/src/materials_discovery/data_sources/qa.py` — current canonical source QA
- `materials-discovery/src/materials_discovery/hifi_digital/hull_proxy.py` — processed reference-phase consumer
- `materials-discovery/src/materials_discovery/hifi_digital/xrd_validate.py` — processed reference-phase consumer

### Current tests
- `materials-discovery/tests/test_ingest.py` — legacy ingest determinism and ordering
- `materials-discovery/tests/test_ingest_real_backend.py` — real/pinned ingest manifest and summary expectations
- `materials-discovery/tests/test_cli.py` — CLI compatibility baseline
- `materials-discovery/tests/test_hull_proxy.py` — reference-phase downstream behavior
- `materials-discovery/tests/test_real_mode_pipeline.py` — end-to-end real/exec pipeline regression

</canonical_refs>

<specifics>
## Specific Ideas

- Build the bridge around the reserved adapter key instead of trying to make
  `SourceAdapter` pretend to be the legacy `IngestBackend` protocol.
- Keep projection deterministic and heavily tested because it is the new
  semantic hinge between multi-source staging and the current no-DFT workflow.
- Use additive metadata rather than schema replacement when preserving source
  tags, QC family labels, and structure provenance.
- Prefer source-backed offline snapshot fixtures or inline payloads in tests so
  Phase 3 verification stays fast and does not rely on live providers.

</specifics>

<deferred>
## Deferred Ideas

- Richer downstream use of source metadata for ranking/reporting heuristics —
  later phases
- Cross-source analytics and data-lake style comparisons — Phase 5
- Operator-facing end-to-end runbook unification — Phase 5
- LLM corpus extraction from projected reference phases — Phase 6+

</deferred>

---

*Phase: 03-reference-phase-integration-with-current-pipeline*
*Context gathered: 2026-04-03*
