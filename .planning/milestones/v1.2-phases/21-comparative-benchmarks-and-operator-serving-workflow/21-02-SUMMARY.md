---
phase: 21-comparative-benchmarks-and-operator-serving-workflow
plan: 02
subsystem: llm
tags: [llm, benchmarks, cli, local-serving, evaluation, replay, pytest]
requires:
  - phase: 21-comparative-benchmarks-and-operator-serving-workflow
    provides: typed serving-benchmark spec, smoke artifacts, and shared-context loader validation
  - phase: 19-local-serving-runtime-and-lane-contracts
    provides: lane-aware serving identity and deterministic local-serving resolution
  - phase: 20-specialized-lane-integration-and-workflow-compatibility
    provides: evaluation-primary specialized lane compatibility across compare and replay flows
provides:
  - operator-facing `llm-serving-benchmark` execution path
  - offline hosted/local/specialized benchmark proof reusing shipped launch and evaluate flows
  - early misaligned evaluation-batch rejection before target execution
affects: [phase-21, llm-serving-benchmark, llm-launch, llm-evaluate, llm-compare, operator-benchmarks]
tech-stack:
  added: []
  patterns: [strict smoke-first benchmark orchestration, benchmark-only launch lane override, shared-context launch and evaluation reuse]
key-files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/src/materials_discovery/llm/serving_benchmark.py
    - materials-discovery/src/materials_discovery/llm/launch.py
    - materials-discovery/tests/test_llm_serving_benchmark_cli.py
    - materials-discovery/tests/test_real_mode_pipeline.py
    - materials-discovery/Progress.md
key-decisions:
  - "Benchmark launch targets reuse `resolve_campaign_launch(...)` with an additive `requested_model_lane_override` seam instead of mutating campaign specs on disk."
  - "Evaluation targets must fail before execution when their batch falls outside the shared acceptance-pack context so benchmark fairness is enforced up front."
  - "Benchmark summaries preserve role-specific metrics and artifact paths instead of fabricating parity between launch and evaluation targets."
patterns-established:
  - "The operator benchmark CLI is a thin wrapper over typed core execution that always writes smoke artifacts before deciding whether to continue."
  - "Hosted, local, and specialized benchmark targets reuse the shipped launch/evaluate/compare artifact families rather than introducing benchmark-only result formats."
requirements-completed: [LLM-17, OPS-10]
duration: 11min
completed: 2026-04-05
---

# Phase 21 Plan 02: Serving Benchmark Execution Summary

**Phase 21 now has a real operator benchmark command that can compare hosted, local, and specialized serving lanes over one shared context without bypassing the shipped launch and evaluation workflows.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-04-05T07:04:46Z
- **Completed:** 2026-04-05T07:16:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added the `mdisc llm-serving-benchmark` CLI entrypoint with smoke-only mode, strict failure handling, and summary-path reporting.
- Reused the shipped launch, compare, and evaluate flows inside serving-benchmark execution so launch targets emit standard launch/comparison artifacts and evaluation targets emit standard evaluation summaries.
- Added an offline hosted/local/specialized benchmark proof plus an explicit misaligned-batch regression that fails before any target execution begins.

## Task Commits

1. **Task 1 RED: benchmark CLI coverage** - `9c2ea2cc` `test(21-02): add failing serving benchmark cli coverage`
2. **Task 1 GREEN: benchmark CLI orchestration** - `4810b61e` `feat(21-02): add serving benchmark cli orchestration`
3. **Task 2 RED: benchmark integration proof** - `62ff3df1` `test(21-02): add failing serving benchmark integration proof`
4. **Task 2 GREEN: benchmark execution proof** - `bd2f485e` `feat(21-02): add serving benchmark execution proof`

## Validation Results

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_real_mode_pipeline.py -x -v`
  - Result: `15 passed in 27.82s`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "misaligned_evaluate_batch" -x -v`
  - Result: `1 passed, 10 deselected in 0.57s`
- `git diff --check`
  - Result: clean before summary commit

## Decisions Made

- The CLI stays intentionally thin: it delegates execution to `execute_serving_benchmark(...)`, prints smoke or recommendation lines, and preserves the repo-standard exit-2 error flow without growing a parallel orchestration layer in `cli.py`.
- Launch-role targets reuse standard campaign launch artifacts by writing a benchmark-local `resolved_launch.json`, `launch_summary.json`, and comparison artifact, which keeps replay and compare compatibility honest for later benchmark phases.
- Evaluation-role targets only proceed when their batch is aligned with the shared acceptance-pack context, so the specialized evaluation lane cannot quietly benchmark unrelated slices and distort cross-lane recommendations.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - the new shared-context misalignment guard passed on the first targeted rerun, and the full Wave 2 verify slice stayed green.

## User Setup Required

None - the benchmark proof remains fully offline through monkeypatched provider calls and temporary acceptance-pack/campaign-spec fixtures.

## Next Phase Readiness

- Phase 21 Wave 3 can now focus on committed benchmark configs, runbook/docs polish, and operator workflow coverage on top of a real benchmark command.
- Hosted, local, and specialized lane results already flow through standard artifacts, so the remaining work is documentation and operator-facing workflow hardening rather than core benchmark semantics.

## Self-Check

PASSED

---
*Phase: 21-comparative-benchmarks-and-operator-serving-workflow*  
*Completed: 2026-04-05*
