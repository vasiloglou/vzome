# Phase 5: Candidate/Reference Data Lake and Analysis Layer - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the platform analytically useful, not just executable. Deliver a canonical
local lakehouse layout with catalog discovery, cross-lane comparison utilities,
operator-facing analytics notebooks, and one unified end-to-end runbook. This
phase does not reorganize the existing directory structure — it formalizes what
exists and adds the analysis and operator tooling layer on top.

Requirements: `PIPE-04` (source-aware reference-phase enrichment for proxy hull,
XRD matching, and report generation) and `PIPE-05` (operator-facing runbook for
ingestion, execution, benchmarking, and result inspection).

</domain>

<decisions>
## Implementation Decisions

### Lakehouse layout and registry design
- **D-01:** Keep the existing directory layout (`data/external/sources/`,
  `data/external/reference_packs/`, `data/manifests/`, `data/reports/`,
  `data/calibration/`, `data/execution_cache/`, `data/benchmarks/`,
  `data/registry/`). No directory reorganization.
- **D-02:** Add per-directory `_catalog.json` files that self-describe each
  artifact directory's contents. A top-level rollup aggregates them.
- **D-03:** The top-level rollup is generated on demand via `mdisc lake index`
  (produces `data/lake_index.json`). Not auto-updated by pipeline stages in
  Phase 5. Not committed to git.
- **D-04:** Each `_catalog.json` entry includes: artifact type, directory path,
  schema version, record count, last-modified timestamp, lineage pointers
  (run/config/reference-pack provenance), size on disk, and staleness flag
  (e.g. calibration older than latest benchmark run).

### Cross-lane comparison scope and output
- **D-05:** Primary comparison axis for Phase 5 is **system-vs-system** (e.g.
  Al-Cu-Fe vs Sc-Zn). Other axes (source-vs-source, backend-vs-backend,
  run-vs-run) are deferred.
- **D-06:** Comparison output is dual-format: structured JSON artifact
  (e.g. `data/comparisons/al_cu_fe_vs_sc_zn.json`) for programmatic use, plus
  CLI table printed to stdout for operator quick-look.
- **D-07:** Comparison granularity is gate-level plus aggregate metric
  distributions (mean, min, max, std for key metrics). Not per-candidate detail.
  Release gate pass/fail deltas, summary stat differences.
- **D-08:** Comparison is a new CLI subcommand: `mdisc lake compare`. Requires
  explicit benchmark pack paths (no auto-discovery).

### Analytics surface
- **D-09:** Dual analytics surface: Jupyter notebooks in
  `materials-discovery/notebooks/` for exploration and deep dives, CLI commands
  for routine operator queries.
- **D-10:** Phase 5 CLI commands under `mdisc lake`:
  - `mdisc lake stats` — lake summary (artifact counts, systems, sources,
    latest runs)
  - `mdisc lake compare` — cross-lane comparison (D-08)
  - `mdisc lake index` — rebuild catalog rollup (D-03)
- **D-11:** Three starter notebooks ship in Phase 5:
  - Source contribution analysis — which source contributed the most
    high-priority candidates for a given system
  - Cross-run drift detection — how results change between runs with different
    reference packs or timestamps
  - Metric distribution deep dive — stability/OOD/XRD distributions for a
    system, and how they shift across configurations

### End-to-end runbook
- **D-12:** Phase 5 produces a single unified runbook covering the full workflow:
  ingestion, reference pack assembly, pipeline execution, benchmarking,
  comparison, and analytics.
- **D-13:** Runbook lives at `materials-discovery/RUNBOOK.md` (top-level, high
  visibility).
- **D-14:** Runbook includes copy-pasteable command blocks throughout — operators
  can run sections directly.
- **D-15:** Runbook includes troubleshooting sections (source adapter timeouts,
  re-running single stages, inspecting stale catalog entries, etc.).

### the agent's Discretion
- Exact `_catalog.json` schema fields beyond the decided minimum
- Internal implementation of staleness detection heuristics
- Notebook visualization library choices (matplotlib, plotly, etc.)
- Exact comparison JSON schema shape
- Whether `mdisc lake` is a Click group or subcommand routing
- Ordering and sectioning within RUNBOOK.md beyond the decided workflow sequence

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Program controls
- `.planning/PROJECT.md` — overall program framing and constraints
- `.planning/ROADMAP.md` — Phase 5 goal, deliverables, and sequencing
- `.planning/REQUIREMENTS.md` — `PIPE-04` and `PIPE-05` definitions
- `.planning/STATE.md` — current execution history and active decisions

### Prior-phase authority
- `.planning/phases/01-program-charter-and-canonical-data-model/01-CONTEXT.md` — canonical data model decisions
- `.planning/phases/02-ingestion-platform-mvp/02-CONTEXT.md` — ingestion runtime and adapter decisions
- `.planning/phases/03-reference-phase-integration-with-current-pipeline/03-CONTEXT.md` — source-registry bridge and projection decisions
- `.planning/phases/04-reference-aware-no-dft-materials-discovery-v1/04-CONTEXT.md` — benchmark pack, reference pack, and comparability decisions

### Existing artifact layout and schemas
- `materials-discovery/src/materials_discovery/data_sources/schema.py` — CanonicalRawSourceRecord, SourceSnapshotManifest, SourceQaReport, ReferencePackManifest
- `materials-discovery/src/materials_discovery/data_sources/storage.py` — path helpers for source snapshots and reference packs
- `materials-discovery/src/materials_discovery/data_sources/manifests.py` — manifest builders for source artifacts
- `materials-discovery/src/materials_discovery/data_sources/reference_packs.py` — reference pack assembly and loading
- `materials-discovery/src/materials_discovery/common/manifest.py` — ArtifactManifest with benchmark_context
- `materials-discovery/src/materials_discovery/common/pipeline_manifest.py` — pipeline-level manifest aggregation
- `materials-discovery/src/materials_discovery/common/benchmarking.py` — BenchmarkRunContext, CalibrationProfile, BenchmarkCase
- `materials-discovery/src/materials_discovery/common/schema.py` — CandidateRecord, DigitalValidationRecord, config models

### Report and ranking code
- `materials-discovery/src/materials_discovery/diffraction/compare_patterns.py` — compile_experiment_report(), release gates, evidence blocks, priority tiers
- `materials-discovery/src/materials_discovery/hifi_digital/rank_candidates.py` — calibrated ranking with provenance

### CLI and operator seams
- `materials-discovery/src/materials_discovery/cli.py` — stage orchestration, manifest writes, existing subcommands
- `materials-discovery/scripts/run_reference_aware_benchmarks.sh` — Phase 4 benchmark runner
- `materials-discovery/developers-docs/reference-aware-benchmarks.md` — Phase 4 benchmark runbook

### Existing operator docs (to consolidate into RUNBOOK.md)
- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md` — real-mode hardening milestones
- `materials-discovery/README.md` — current operator entrypoints
- `materials-discovery/developers-docs/configuration-reference.md` — config progression and examples

</canonical_refs>

<specifics>
## Specific Ideas

- Formalize what exists rather than reorganize — the 7+ artifact directories
  are already baked into Phase 1-4 code and moving them would be pure churn.
- The `_catalog.json` per-directory pattern gives local discoverability (each
  directory is self-describing) while `lake_index.json` gives the global view.
- `mdisc lake` as a CLI group keeps the new commands namespaced and consistent
  with the existing `mdisc` entrypoint.
- Notebooks should load data from the same paths the CLI uses — no parallel
  data access patterns.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `data_sources/storage.py` path helpers: can be extended with catalog-aware
  directory scanning
- `common/manifest.py` ArtifactManifest: already has run_id, config_hash,
  output_hashes, benchmark_context — good lineage source for catalog entries
- `common/pipeline_manifest.py`: aggregates stage manifests — useful for
  staleness detection across stages
- `common/benchmarking.py` BenchmarkRunContext: carries lane identity
  (reference_pack_id, source_keys, backend_mode) — comparison input
- `diffraction/compare_patterns.py` compile_experiment_report(): release gates
  and summary stats are the comparison metrics source
- `scripts/run_reference_aware_benchmarks.sh`: existing runner to reference
  from RUNBOOK.md

### Established Patterns
- File-backed JSON/JSONL artifacts with schema version headers
- Stage-level manifests with SHA256 output hashes
- Benchmark packs as high-level indexes referencing stage manifests
- Click-based CLI with subcommand groups

### Integration Points
- `mdisc lake` commands integrate into existing `cli.py` Click group
- `_catalog.json` files written alongside existing artifacts without changing
  existing write paths
- Notebooks read from `data/` using the same path conventions as CLI code
- RUNBOOK.md consolidates existing docs without replacing them

</code_context>

<deferred>
## Deferred Ideas

- Auto-updating catalog on every pipeline stage run — upgrade from on-demand
  in a future phase
- Source-vs-source, backend-vs-backend, and run-vs-run comparison axes — add
  after system-vs-system proves useful
- Auto-discovery of benchmark packs for comparison — add convenience after
  explicit-path workflow is stable
- Interactive notebook dashboard or web UI for analytics
- LLM evaluation notebooks — Phase 7+

</deferred>

---

*Phase: 05-candidate-reference-data-lake-and-analysis-layer*
*Context gathered: 2026-04-03*
