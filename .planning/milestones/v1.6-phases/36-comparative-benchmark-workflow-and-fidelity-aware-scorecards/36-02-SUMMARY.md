---
phase: 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards
plan: 02
subsystem: llm
tags: [external-benchmark, scorecards, translated-benchmark, controls, llm]
requires:
  - phase: 34-benchmark-pack-and-freeze-contract
    provides: frozen translated benchmark-set manifests and included benchmark rows
  - phase: 35-external-target-registration-and-reproducible-execution
    provides: immutable external-target registrations, environment manifests, and smoke checks
  - phase: 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards
    provides: typed benchmark contracts and deterministic llm_external storage helpers
provides:
  - benchmark execution for frozen translated benchmark sets across external targets and internal controls
  - deterministic per-target run manifests, raw-response inventories, and case-result inventories
  - fidelity-aware benchmark summaries with shared eligible control deltas and periodic-safe recommendation logic
affects: [36-03-plan, 36-phase-verification, v1.6-milestone-audit]
tech-stack:
  added: []
  patterns:
    - external and internal targets share one benchmark execution flow while keeping distinct lineage fields
    - recommendation lines are driven by the periodic-safe exact or anchored slice even when lossy slices look stronger
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/external_benchmark.py
    - materials-discovery/tests/test_llm_external_benchmark_core.py
  modified:
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Benchmark execution replays frozen translated benchmark manifests instead of rescanning live translation bundles."
  - "Recommendation lines privilege the periodic-safe exact or anchored slice so diagnostic wins on lossy cases cannot overclaim milestone readiness."
patterns-established:
  - "Per-target benchmark artifacts always include run_manifest.json, case_results.jsonl, and raw_responses.jsonl beneath the llm_external benchmark root."
  - "Internal controls reuse serving-lane resolution and LlmServingIdentity while external targets reuse registration and smoke artifacts from Phase 35."
requirements-progressed: [LLM-32, LLM-33]
duration: 13 min
completed: 2026-04-07
---

# Phase 36 Plan 02: Comparative Benchmark Execution Core Summary

**Frozen translated benchmark replay with typed per-target artifacts and periodic-safe-first recommendation scorecards**

## Performance

- **Duration:** 13 min
- **Started:** 2026-04-07T08:00:00Z
- **Completed:** 2026-04-07T08:13:30Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added `llm/external_benchmark.py` with typed benchmark-spec loading, frozen
  benchmark-row replay, prompt rendering, response parsing, and shared
  execution across external targets and internal controls.
- Persisted deterministic per-target benchmark artifacts including run
  manifests, raw responses, case results, benchmark-level smoke metadata, and
  the combined scorecard-by-case inventory.
- Tightened the recommendation layer so periodic-safe exact or anchored slices
  remain the decision surface even when approximate or lossy slices look
  stronger overall.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/external_benchmark.py` -
  Added the Phase 36 benchmark execution and summary core.
- `materials-discovery/tests/test_llm_external_benchmark_core.py` - Added
  focused execution and typed summary coverage for exclusions, smoke failures,
  shared eligible deltas, and periodic-safe recommendation logic.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Re-exported
  the benchmark execution and summary builder surface.
- `materials-discovery/Progress.md` - Logged the Plan 36-02 execution and
  scorecard changes per repo policy.

## Validation

- Focused verification command:
  `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_core.py -x -v`
- Result: `4 passed in 0.26s`

## Decisions Made

- Reused Phase 35 registration, environment, and smoke artifacts instead of
  inventing a second external-target lineage path inside the benchmark module.
- Kept prompt rendering and response parsing as a small benchmark-only registry
  keyed by `prompt_contract_id` and `response_parser_key`.
- Preserved shared eligible control deltas in the typed summary while basing
  recommendation lines on the periodic-safe exact or anchored slice.

## Deviations from Plan

None.

## Issues Encountered

- The first scorecard pass would have allowed lossy-slice wins to over-inflate
  recommendation strength. The summary builder was tightened before sign-off so
  periodic-safe evidence remains the gating signal.

## User Setup Required

None for Plan 02. Tests use monkeypatched runners and fixture artifacts, so no
external model weights are required for validation.

## Next Phase Readiness

Plan 03 can now expose the benchmark through CLI commands, add a committed
example benchmark spec, and document the operator workflow on top of the typed
execution and scorecard artifacts that now exist.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/36-comparative-benchmark-workflow-and-fidelity-aware-scorecards/36-02-SUMMARY.md`
- Key files verified: `materials-discovery/src/materials_discovery/llm/external_benchmark.py`, `materials-discovery/tests/test_llm_external_benchmark_core.py`
- Focused validation is green: `4 passed in 0.26s`
