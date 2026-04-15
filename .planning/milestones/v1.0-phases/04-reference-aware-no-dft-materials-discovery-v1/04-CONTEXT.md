# Phase 4: Reference-Aware No-DFT Materials Discovery v1 - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning
**Source:** Derived from roadmap, requirements, Phase 3 implementation,
current real-mode configs, benchmarking/report seams, and
`materials-discovery/developers-docs/`

<domain>
## Phase Boundary

Turn the existing no-DFT pipeline into a benchmarkable, operator-credible
reference-aware workflow by landing:

- two non-mock benchmark lanes
- explicit multi-source reference-pack inputs
- comparable benchmark/report/manifest outputs across source adapters and
  backend modes
- reproducible scripts and runbooks for source selection and backend selection

This phase is not another ingest-plumbing phase. The Phase 2/3 source runtime
and projection bridge already exist. Phase 4 should use those seams to improve
the actual discovery workflow, ranking/report provenance, and benchmark
reproducibility. It should stay file-backed, preserve the current CLI contract,
and keep the no-DFT boundary explicit.

</domain>

<decisions>
## Implementation Decisions

### Locked benchmark scope
- **D-01:** Phase 4 must satisfy `PIPE-02` and `PIPE-03`.
- **D-02:** The v1 benchmark systems are locked to `Al-Cu-Fe` and `Sc-Zn`.
- **D-03:** `Al-Pd-Mn` and `Ti-Zr-Ni` stay out of Phase 4 benchmark scope unless
  they gain the same minimum package already present for the two selected
  systems: a working non-mock config, a validation snapshot or equivalent
  deterministic validation lane, and a benchmark corpus.
- **D-04:** The benchmarked workflow must use non-mock inputs. Mock mode remains
  a regression lane, not a Phase 4 success lane.

### Input and pack model
- **D-05:** Phase 4 should introduce an explicit **reference pack** artifact for
  multi-source reference-phase inputs instead of encoding multi-source choices
  only in ad hoc docs or one-off script logic.
- **D-06:** A reference pack is an upstream, no-DFT artifact. It should be
  assembled from staged canonical source snapshots and then projected through
  the existing Phase 3 bridge.
- **D-07:** The minimum scientific posture for a Phase 4 reference pack is:
  one QC/approximant-friendly source plus at least one periodic/open materials
  source for the same benchmark system, using deterministic local fixtures or
  pinned artifacts for tests.
- **D-08:** The exact second source may vary by system at implementation time,
  but it must come from the Phase 2 adapter set (`COD`, `Materials Project`,
  `OQMD`, or `JARVIS`) and be captured in pack lineage.

### Provenance and comparability
- **D-09:** Phase 4 should introduce a distinct **benchmark pack** or exact
  equivalent summary artifact for full runs. It must make manifests,
  calibration outputs, report outputs, source-pack lineage, and benchmark-corpus
  lineage comparable across lanes.
- **D-10:** Comparability must be additive. Existing manifests, summaries, and
  candidate JSONL contracts should evolve by adding context fields rather than
  replacing current shapes.
- **D-11:** Ranking and report outputs must surface enough benchmark/reference
  context that an operator can answer:
  "Which reference pack was used?",
  "Which source adapters contributed?",
  "Which backend mode produced this result?",
  and "Which benchmark corpus/calibration profile was loaded?"

### Operator workflow
- **D-12:** The current stage CLI remains the primary interface
  (`mdisc ingest -> ... -> report`). Phase 4 may add benchmark/run helpers and
  docs, but it must not replace the existing stage commands with a new
  orchestration framework.
- **D-13:** Operator-facing benchmark scripts should become multi-system and
  config-driven instead of remaining hard-coded to `al_cu_fe_real.yaml`.
- **D-14:** Tests and committed benchmark fixtures must stay offline and
  deterministic even if production adapters can talk to live sources.

### Comparison matrix
- **D-15:** The minimum comparison matrix for Phase 4 should cover:
  - `Al-Cu-Fe` in a baseline real lane
  - `Al-Cu-Fe` in a richer source-registry/reference-pack lane
  - one additional backend-mode comparison lane already supported in repo
    (`exec` is preferred over `native` for the required minimum because the
    current scripts/tests already exercise it)
  - `Sc-Zn` in a real calibrated lane with the Zomic bridge preserved
- **D-16:** `native` can be included as a bonus lane if it does not destabilize
  the required deterministic verification path.

### the agent's Discretion
- The exact config shape for reference-pack membership, as long as it is
  additive and readable
- Whether benchmark packs are implemented as a dedicated JSON artifact or a
  small additive wrapper around the existing pipeline manifest
- The exact file paths for new benchmark scripts and runbooks
- Whether the pack builder lives under `data_sources/` directly or behind a
  narrowly scoped helper module

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Program controls
- `.planning/PROJECT.md` — overall program framing and constraints
- `.planning/ROADMAP.md` — Phase 4 goal, deliverables, and sequencing
- `.planning/REQUIREMENTS.md` — `PIPE-02` and `PIPE-03`
- `.planning/STATE.md` — current execution history and active decisions

### Prior-phase authority
- `.planning/phases/01-program-charter-and-canonical-data-model/01-INTEGRATION-DESIGN.md` — original package/artifact strategy and ingest bridge design
- `.planning/phases/02-ingestion-platform-mvp/02-CONTEXT.md` — Phase 2 runtime and config decisions
- `.planning/phases/02-ingestion-platform-mvp/02-RESEARCH.md` — source runtime shape and adapter posture
- `.planning/phases/03-reference-phase-integration-with-current-pipeline/03-CONTEXT.md` — source-registry bridge decisions
- `.planning/phases/03-reference-phase-integration-with-current-pipeline/03-01-SUMMARY.md` — projection seam and dedupe behavior
- `.planning/phases/03-reference-phase-integration-with-current-pipeline/03-02-SUMMARY.md` — ingest bridge and source-lineage manifest behavior
- `.planning/phases/03-reference-phase-integration-with-current-pipeline/03-03-SUMMARY.md` — end-to-end source-backed pipeline coverage and no-DFT guardrails

### Existing subsystem docs
- `materials-discovery/README.md` — current operator entrypoints and shipped real configs
- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md` — real-mode hardening milestones and acceptance gates
- `materials-discovery/developers-docs/index.md` — current system/config catalog and benchmark-pack language
- `materials-discovery/developers-docs/architecture.md` — package boundaries, artifact flow, and pipeline manifest model
- `materials-discovery/developers-docs/pipeline-stages.md` — stage behavior and output contracts
- `materials-discovery/developers-docs/backend-system.md` — backend/adapter layers and runtime selection
- `materials-discovery/developers-docs/configuration-reference.md` — config progression and current real/native/exec examples
- `materials-discovery/developers-docs/data-schema-reference.md` — schema conventions and summary models

### Current code and operator seams
- `materials-discovery/src/materials_discovery/cli.py` — stage orchestration, manifest writes, and report-stage pipeline manifest
- `materials-discovery/src/materials_discovery/common/schema.py` — config, summary, and manifest models
- `materials-discovery/src/materials_discovery/common/manifest.py` — manifest builder/writer
- `materials-discovery/src/materials_discovery/common/benchmarking.py` — current benchmark-corpus loading and calibration-profile logic
- `materials-discovery/src/materials_discovery/data_sources/runtime.py` — staged source snapshots and source-registry runtime
- `materials-discovery/src/materials_discovery/data_sources/projection.py` — canonical-source projection into processed reference phases
- `materials-discovery/src/materials_discovery/hifi_digital/rank_candidates.py` — calibrated rank provenance
- `materials-discovery/src/materials_discovery/diffraction/compare_patterns.py` — report payload and release-gate logic
- `materials-discovery/scripts/run_real_pipeline.sh` — current baseline operator script
- `materials-discovery/scripts/run_exec_pipeline.sh` — current exec-mode operator script
- `materials-discovery/scripts/run_native_pipeline.sh` — current native-mode operator script

### Current configs and tests
- `materials-discovery/configs/systems/al_cu_fe_real.yaml` — primary fully provisioned real-mode lane
- `materials-discovery/configs/systems/al_cu_fe_exec.yaml` — existing backend-mode comparison lane
- `materials-discovery/configs/systems/sc_zn_real.yaml` — second benchmarkable system with Zomic bridge
- `materials-discovery/tests/test_real_mode_pipeline.py` — existing end-to-end pipeline regression seams
- `materials-discovery/tests/test_benchmarking.py` — current benchmark-profile coverage
- `materials-discovery/tests/test_hifi_rank.py` — rank-stage calibration and provenance assertions
- `materials-discovery/tests/test_report.py` — report/pipeline-manifest assertions

</canonical_refs>

<specifics>
## Specific Ideas

- Treat `Al-Cu-Fe` and `Sc-Zn` as the only required benchmark systems for this
  phase so the work produces a credible end state instead of a diluted matrix.
- Use the Phase 3 source-registry bridge as the baseline for richer reference
  packs rather than creating a parallel ingest path.
- Separate **reference packs** (input-side curated source bundles) from
  **benchmark packs** (output-side comparable run summaries).
- Reuse the existing stage scripts as the starting point for a more general
  benchmark runner rather than replacing them wholesale.

</specifics>

<deferred>
## Deferred Ideas

- Third and fourth benchmark systems (`Al-Pd-Mn`, `Ti-Zr-Ni`) — later phases
- Rich data-lake style cross-run analytics — Phase 5
- Live-network provider benchmarking as a required CI lane
- LLM integration or evaluation against benchmark packs — Phase 6+

</deferred>

---

*Phase: 04-reference-aware-no-dft-materials-discovery-v1*
*Context gathered: 2026-04-03*
