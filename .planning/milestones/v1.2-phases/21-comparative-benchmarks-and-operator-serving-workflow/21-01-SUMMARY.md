---
phase: 21-comparative-benchmarks-and-operator-serving-workflow
plan: 01
subsystem: llm
tags: [llm, benchmarks, smoke-checks, schema, local-serving, pytest]
requires:
  - phase: 20-specialized-lane-integration-and-workflow-compatibility
    provides: stable generation and evaluation lane lineage across hosted, local, and specialized workflows
provides:
  - typed serving-benchmark spec and result contracts
  - offline smoke-check helpers built on the shipped lane-resolution seam
  - shared-context benchmark storage paths and mixed-system rejection
affects: [phase-21, llm-serving-benchmark, llm-launch, llm-evaluate, operator-benchmarks]
tech-stack:
  added: []
  patterns: [shared-context benchmark specs, explicit smoke checks, operator-tradeoff summaries]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/serving_benchmark.py
    - materials-discovery/tests/test_llm_serving_benchmark_schema.py
    - materials-discovery/tests/test_llm_serving_benchmark_core.py
  modified:
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/storage.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Serving benchmarks are anchored to one shared acceptance-pack context and reject mixed-system targets before execution starts."
  - "Smoke checks reuse `resolve_serving_lane(...)`, `build_serving_identity(...)`, and `validate_llm_adapter_ready(...)` directly so Phase 21 does not invent a parallel serving contract."
  - "Unapproved lane fallback is preserved as a failed smoke artifact with explicit detail instead of raising away operator context."
patterns-established:
  - "Benchmark artifacts live under `data/benchmarks/llm_serving/{benchmark_id}/...` and stay additive to the existing launch/evaluate/compare artifact families."
  - "Serving-benchmark summaries compare operator tradeoffs through preserved per-target metadata instead of synthetic quality backfills."
requirements-completed: [LLM-17, OPS-10]
duration: 8min
completed: 2026-04-05
---

# Phase 21 Plan 01: Serving Benchmark Contract Summary

**Phase 21 now has a typed, shared-context serving-benchmark contract with explicit smoke checks and offline core helpers for hosted, local, and specialized target comparison.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-05T06:53:00Z
- **Completed:** 2026-04-05T07:01:10Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Added typed benchmark spec, smoke-check, target-result, and benchmark-summary models to the LLM schema layer.
- Added stable benchmark artifact helpers under `data/benchmarks/llm_serving/{benchmark_id}/...`.
- Added `load_serving_benchmark_spec(...)` with early mixed-system rejection against the shared acceptance-pack context.
- Added offline smoke-check and summary helpers that reuse the shipped lane-resolution, serving-identity, and readiness seams.
- Verified the new schema and core behavior with focused benchmark tests.

## Task Commits

1. **Task 1 RED: benchmark schema/storage contract tests** - `ee68ab23` `test(21-01): add failing serving benchmark schema coverage`
2. **Task 1 GREEN: serving benchmark schema contracts** - `d2f8ed23` `feat(21-01): add serving benchmark schema contracts`
3. **Task 2 RED: benchmark core helper tests** - `acc086f7` `test(21-01): add failing serving benchmark core coverage`
4. **Task 2 GREEN: serving benchmark core helpers** - `f245f8cd` `feat(21-01): add serving benchmark core helpers`

## Validation Results

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py -x -v`
  - Result: `9 passed in 0.23s`
- `git diff --check`
  - Result: clean before summary commit

## Decisions Made

- The loader resolves relative benchmark paths against the spec file while validating targets against the shared acceptance-pack system set, so later CLI flows can stay spec-relative without sacrificing fairness checks.
- Smoke checks always return typed artifacts, even on readiness or fallback problems, because operator-facing benchmark setup needs visible failure context instead of exceptions with lost lane metadata.
- Benchmark summary recommendations stay intentionally narrow at this stage: fastest, cheapest, and lowest-friction targets are surfaced first while per-target quality metrics remain preserved and explicit.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1 depended on `load_serving_benchmark_spec(...)` before Task 2 formally created the module**
- **Found during:** Task 1 GREEN implementation
- **Issue:** The reviewed plan split required mixed-system loader validation in Task 1, but the module creation step was written under Task 2.
- **Fix:** Created `materials-discovery/src/materials_discovery/llm/serving_benchmark.py` during Task 1 with the loader first, then extended the same module in Task 2 with the smoke and summary helpers.
- **Files modified:** `materials-discovery/src/materials_discovery/llm/serving_benchmark.py`
- **Verification:** Both focused benchmark suites passed green after the staged implementation.
- **Committed in:** `d2f8ed23`, `f245f8cd`

---

**Total deviations:** 1 auto-fixed (1 blocking)  
**Impact on plan:** No scope expansion. The adjustment only repaired the task boundary so the reviewed benchmark contract could land in a coherent order.

## Next Phase Readiness

- Phase 21 Wave 2 can now add the operator-facing `llm-serving-benchmark` CLI on top of a typed spec, explicit smoke artifacts, and stable summary helpers.
- Shared-context validation, no-silent-fallback rules, and offline smoke coverage are already in place, so the CLI wave can focus on orchestration rather than contract repair.

## Self-Check

PASSED

---
*Phase: 21-comparative-benchmarks-and-operator-serving-workflow*  
*Completed: 2026-04-05*
