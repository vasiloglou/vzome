---
gsd_state_version: 1.0
milestone: v1.1
milestone_name: milestone
current_phase: 10
current_phase_name: closed-loop-campaign-contract-and-governance
current_plan: 3
status: verifying
stopped_at: Completed 10-03-PLAN.md
last_updated: "2026-04-04T15:00:01.688Z"
last_activity: 2026-04-04
progress:
  total_phases: 3
  completed_phases: 1
  total_plans: 3
  completed_plans: 3
  percent: 100
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-03)

**Core value:** Build one reproducible system where trusted materials data, physically grounded no-DFT validation, and LLM-guided structure generation reinforce each other instead of living in separate prototypes.
**Current focus:** Phase 10 — closed-loop-campaign-contract-and-governance

## Current Position

Current Phase: 10
Current Phase Name: closed-loop-campaign-contract-and-governance
Total Phases: 3
Current Plan: 3
Total Plans in Phase: 3
Phase: 10 (closed-loop-campaign-contract-and-governance) — READY FOR VERIFICATION
Plan: 3 of 3
Status: Phase complete — ready for verification
Last activity: 2026-04-04
Last Activity Description: Phase 10 execution complete — awaiting transition to Phase 11

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**

- Total plans completed: 26
- Average duration: 20 min
- Total execution time: 5.7 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 1 | 9 min | 9 min |
| 2 | 3 | 122 min | 41 min |
| 3 | 3 | 63 min | 21 min |
| 4 | 3 | 38 min | 13 min |
| 5 | 3 | 38 min | 13 min |
| 6 | 4 | 122 min | 30 min |
| 7 | 3 | 69 min | 23 min |
| 8 | 3 | 56 min | 19 min |
| 9 | 3 | 32 min | 11 min |

**Recent Trend:**

- Last 5 plans: P8.02=16min, P8.03=22min, P9.01=12min, P9.02=15min, P9.03=5min
- Trend: stable with quick finishing work on the typed LLM acceptance layer

| Phase 01-program-charter-and-canonical-data-model P01 | 9min | 3 tasks | 8 files |
| Phase 02-ingestion-platform-mvp P01 | 59min | 3 tasks | 15 files |
| Phase 02-ingestion-platform-mvp P02 | 31min | 3 tasks | 11 files |
| Phase 02-ingestion-platform-mvp P03 | 32min | 3 tasks | 11 files |
| Phase 03 P1 | 19min | 2 tasks | 5 files |
| Phase 03 P2 | 17min | 3 tasks | 9 files |
| Phase 03 P3 | 27min | 3 tasks | 5 files |
| Phase 04 P01 | 12 | 2 tasks | 15 files |
| Phase 04 P02 | 18 | 3 tasks | 9 files |
| Phase 04 P03 | 8 | 3 tasks | 8 files |
| Phase 05 P01 | 25 | 2 tasks | 8 files |
| Phase 05 P02 | 5 | 2 tasks | 4 files |
| Phase 05 P03 | 8 | 2 tasks | 6 files |
| Phase 05 P03 | 8 | 3 tasks | 6 files |
| Phase 06 P01 | 24 | 2 tasks | 9 files |
| Phase 06 P02 | 32 | 2 tasks | 8 files |
| Phase 06 P03 | 36 | 2 tasks | 8 files |
| Phase 06 P04 | 54 | 4 tasks | 12 files |
| Phase 07 P02 | 35 | 2 tasks | 13 files |
| Phase 07 P03 | 34 | 3 tasks | 8 files |
| Phase 08 P01 | 18 | 3 tasks | 9 files |
| Phase 08 P02 | 16 | 3 tasks | 7 files |
| Phase 08 P03 | 22 | 3 tasks | 9 files |
| Phase 09 P01 | 12 | 3 tasks | 9 files |
| Phase 09 P02 | 15 | 3 tasks | 8 files |
| Phase 09 P03 | 5 | 3 tasks | 8 files |
| Phase 10-closed-loop-campaign-contract-and-governance P01 | 8min | 2 tasks | 6 files |

## Accumulated Context

### Decisions

Decisions are logged in `PROJECT.md` and the Phase 1 context files. Recent decisions affecting current work:

- [Milestone v1.1]: Start Project 3's next cycle with closed-loop campaign execution rather than local or fine-tuned model serving.
- [Milestone v1.1]: Keep the new campaign workflow operator-governed, approval-gated, and file-backed.
- [Milestone v1.1]: Continue phase numbering from `v1.0`, so the new roadmap begins at Phase 10.
- [Phase 10]: Keep proposals system-scoped, typed over three action families, and dry-run by default.
- [Phase 10]: Support both general-purpose and specialized-materials model lanes in proposal/spec metadata without hard-coding one vendor.
- [Phase 10]: Require a separate approval artifact and a self-contained campaign spec rooted in acceptance-pack, approval, eval-set, and config lineage.
- Phase 1 is contract-design, not adapter implementation.
- The new ingestion layer should live under `materials_discovery/data_sources/`.
- Keep `mdisc ingest` as the stable operator-facing entrypoint while the new source layer integrates behind it.
- [Phase 01-program-charter-and-canonical-data-model]: Keep the canonical raw-source contract separate from the existing processed IngestRecord.
- [Phase 01-program-charter-and-canonical-data-model]: Use materials_discovery/data_sources/ as the provider-ingestion package and keep backends/ as a thin runtime-mode bridge.
- [Phase 01-program-charter-and-canonical-data-model]: Lock Phase 2 priority to HYPOD-X, COD, Materials Project, OQMD, and JARVIS while preserving the broader watchlist and tooling inventory.
- [Phase 02-ingestion-platform-mvp]: Keep built-in source adapter registration explicit so tests can clear and reconstruct the registry deterministically.
- [Phase 02-ingestion-platform-mvp]: Keep `httpx` imports lazy in API adapters so offline pytest runs do not require the ingestion extra to be installed.
- [Phase 03-reference-phase-integration-with-current-pipeline]: Use `source_registry_v1` as the only bridge selector and keep the legacy HYPOD-X ingest path unchanged.
- [Phase 03-reference-phase-integration-with-current-pipeline]: Project canonical source records into additive `IngestRecord` rows rather than replacing the processed reference-phase contract.
- [Phase 03-reference-phase-integration-with-current-pipeline]: Lock manifest lineage to an optional additive field and make cached-snapshot reuse explicit in the bridge path.
- [Phase 03-reference-phase-integration-with-current-pipeline]: Use dynamic thin fixtures/configs for bridge-backed pipeline tests and keep legacy ingest determinism in the final verification sweep.
- [Phase 04-reference-aware-no-dft-materials-discovery-v1]: Lock the required benchmark systems to `Al-Cu-Fe` and `Sc-Zn`.
- [Phase 04-reference-aware-no-dft-materials-discovery-v1]: Introduce explicit reference-pack inputs and benchmark-pack outputs rather than overloading existing manifests.
- [Phase 04-reference-aware-no-dft-materials-discovery-v1]: Make comparability additive across manifests, calibration outputs, ranking provenance, and report outputs.
- [Phase 04]: ReferencePackConfig and ReferencePackMemberConfig live in common/schema.py to avoid circular imports; disk-artifact models in data_sources/schema.py
- [Phase 04]: CLI detects ingestion.reference_pack and routes source_registry_v1 through _ingest_via_reference_pack for multi-source pack assembly before projection
- [Phase 04]: Second source for Al-Cu-Fe benchmark: materials_project (mp_fixture_v1); for Sc-Zn: cod (cod_fixture_v1)
- [Phase 04]: CLI assembles BenchmarkRunContext once from config+lineage and passes it forward; downstream stages do not reconstruct context independently
- [Phase 04]: benchmark_context field on ArtifactManifest is nullable so existing manifest readers remain valid when context is absent
- [Phase 04]: benchmark_pack.json is a high-level index referencing stage manifests/calibration JSONs rather than duplicating their content
- [Phase 04]: Keep benchmark runner as thin config-driven wrapper around mdisc stage commands (no new orchestration framework)
- [Phase 04]: Use benchmark_lane pytest marker to isolate slower E2E tests as a clearly separate lane
- [Phase 04]: Cross-lane comparison: Al-Cu-Fe real vs reference-aware real (same backend mode, different source pack) for maximal source-difference visibility
- [Phase 05]: ARTIFACT_DIRECTORIES covers 17 entries for full artifact inventory completeness (review concern #3)
- [Phase 05]: Hash-based staleness detection (manifest output_hashes) is authoritative; mtime is secondary hint (review concern #1)
- [Phase 05]: All lineage paths are workspace-relative via workspace_relative() (review concern #5)
- [Phase 05]: Lane-centric comparison model: system-vs-system is a preset view; same model supports source-vs-source and backend-vs-backend comparisons (addresses review concern #6)
- [Phase 05]: Dereference benchmark-pack stage_manifest_paths[report] for entry-level metric distributions; graceful fallback to pack-embedded report_metrics when report file missing (addresses review concern #2)
- [Phase 05]: Static notebook tests separated from execution tests using pytest.mark.skipif so structural checks always run without nbformat/nbconvert
- [Phase 05]: RUNBOOK.md at materials-discovery root (per D-13); references developer-docs for deep-dive context rather than duplicating content
- [Phase 05]: Static notebook tests separated from execution tests using pytest.mark.skipif so structural checks always run without nbformat/nbconvert
- [Phase 05]: RUNBOOK.md at materials-discovery root (per D-13); references developer-docs for deep-dive context rather than duplicating content
- [Phase 06-zomic-training-corpus-pipeline]: Inventory rows must stay record-addressable with explicit loader hints so the builder can reopen exact source artifacts without path guessing.
- [Phase 06-zomic-training-corpus-pipeline]: Keep release-tier grading as a dedicated QA step (`pending -> gold/silver/reject`) rather than baking release decisions into converters.
- [Phase 06-zomic-training-corpus-pipeline]: Reserve `exact` fidelity for native or exact-source paths; CandidateRecord conversion defaults to `anchored` unless later equivalence proves otherwise.
- [Phase 06-zomic-training-corpus-pipeline]: Let thin offline CIF fixtures fall back to `parse_cif()` when symmetry metadata is absent instead of requiring richer crystallographic inputs.
- [Phase 06-zomic-training-corpus-pipeline]: The corpus builder dispatches by `loader_hint` first and writes the full audit trail under `data/llm_corpus/{build_id}/`.
- [Phase 06-zomic-training-corpus-pipeline]: Operators build the corpus through `mdisc llm-corpus build --config ...`, not via ad hoc scripts.
- [Phase 07-llm-inference-mvp]: Start with deterministic mock coverage plus one hosted API provider; local-model serving is deferred.
- [Phase 07-llm-inference-mvp]: Keep llm-generate config-driven with optional seed Zomic support, not a free-form chat prompt.
- [Phase 07-llm-inference-mvp]: Preserve rich prompt/raw-output lineage at the run level and keep CandidateRecord provenance lighter by linking back to the run.
- [Phase 07-llm-inference-mvp]: Benchmark `Al-Cu-Fe` and `Sc-Zn` at parse/compile/conversion/screen level in Phase 7; full hi-fi comparison is deferred to Phase 8.
- [Phase 08-llm-evaluation-and-pipeline-integration]: `llm-evaluate` is additive and report-oriented; it does not rerank candidates in this milestone.
- [Phase 08-llm-evaluation-and-pipeline-integration]: `report` prefers `*_all_llm_evaluated.jsonl` when present, while partial evaluation artifacts do not override the default ranked lane.
- [Phase 08-llm-evaluation-and-pipeline-integration]: The downstream deterministic-vs-LLM benchmark lane is now real and should be reused as the acceptance surface for Phase 9.
- [Phase 09-fine-tuned-zomic-model-and-closed-loop-design]: Acceptance metrics are file-backed and computed from the existing Phase 7/8 benchmark artifacts instead of ad hoc notebook logic.
- [Phase 09-fine-tuned-zomic-model-and-closed-loop-design]: `llm-generate` conditioning remains optional and reproducible through eval-set files plus recorded `conditioning_example_ids`.
- [Phase 09-fine-tuned-zomic-model-and-closed-loop-design]: `llm-suggest` is a dry-run advisory command in v1; it does not mutate the active-learning loop automatically.
- [Phase 10-closed-loop-campaign-contract-and-governance]: Keep the Phase 10 campaign contracts additive inside llm/schema.py instead of splitting files during this phase.
- [Phase 10-closed-loop-campaign-contract-and-governance]: Validate campaign-action payload matching with an explicit model_validator rather than a discriminated-union refactor.
- [Phase 10-closed-loop-campaign-contract-and-governance]: Keep proposals and approvals under the acceptance-pack root while campaign specs live under data/llm_campaigns/{campaign_id}.
- [Phase 10-closed-loop-campaign-contract-and-governance]: Make blank artifact identifiers fail fast in storage helpers instead of normalizing into malformed paths.

### Pending Todos

None yet.

### Blockers/Concerns

- Cleanup of `.planning/phases/` was intentionally deferred because `.planning/phases/05-candidate-reference-data-lake-and-analysis-layer/05-CONTEXT.md` is an unrelated local untracked file that should not be moved automatically.

## Session Continuity

Last session: 2026-04-04T05:38:20.388Z
Stopped at: Completed 10-01-PLAN.md
Resume file: None
