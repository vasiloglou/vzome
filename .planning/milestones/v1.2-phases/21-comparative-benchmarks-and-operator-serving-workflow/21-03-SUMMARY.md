---
phase: 21-comparative-benchmarks-and-operator-serving-workflow
plan: 03
subsystem: llm
tags: [llm, benchmarks, docs, runbook, configs, operator-workflow, pytest]
requires:
  - phase: 21-comparative-benchmarks-and-operator-serving-workflow
    provides: runnable serving benchmark CLI with strict smoke behavior and shared-context launch/evaluate execution
provides:
  - committed hosted and benchmark example configs
  - operator-facing runbook and developer docs for serving benchmarks
  - final benchmark workflow regression coverage across shared CLI and real-mode tests
affects: [phase-21, llm-serving-benchmark, operator-benchmarks, docs, configs]
tech-stack:
  added: []
  patterns: [committed operator benchmark specs, evaluation-primary specialist benchmarks, smoke-first operator runbooks]
key-files:
  created:
    - materials-discovery/configs/systems/al_cu_fe_llm_hosted.yaml
    - materials-discovery/configs/llm/al_cu_fe_serving_benchmark.yaml
    - materials-discovery/configs/llm/sc_zn_serving_benchmark.yaml
  modified:
    - materials-discovery/RUNBOOK.md
    - materials-discovery/developers-docs/configuration-reference.md
    - materials-discovery/developers-docs/llm-integration.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/tests/test_cli.py
    - materials-discovery/tests/test_real_mode_pipeline.py
    - materials-discovery/Progress.md
key-decisions:
  - "The committed Al-Cu-Fe benchmark example shows the full hosted/local/specialized matrix, while Sc-Zn stays a thinner compatibility spec instead of pretending to be a second deep proof."
  - "Specialized benchmark targets remain evaluation-primary in the shipped examples and docs, with Zomic-native specialized generation deferred to a later milestone."
  - "Operator docs emphasize strict smoke-first benchmarking, no silent fallback, and explicit interpretation of quality, cost, latency, and operator friction."
patterns-established:
  - "Serving benchmark specs live under `configs/llm/` and reference standard acceptance-pack and campaign-spec artifact paths rather than benchmark-only shadow artifacts."
  - "The operator runbook and developer docs now describe the same benchmark lifecycle: smoke preflight, strict failure posture, full comparison run, and artifact cleanup."
requirements-completed: [LLM-17, OPS-10]
duration: 5min
completed: 2026-04-05
---

# Phase 21 Plan 03: Operator Serving Workflow Summary

**Phase 21 now ships benchmark-ready hosted/local/specialized example specs plus the runbook and developer-doc guidance needed to operate the serving comparison workflow safely.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-05T07:19:26Z
- **Completed:** 2026-04-05T07:24:03Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Added a committed hosted Al-Cu-Fe config and benchmark specs for Al-Cu-Fe and Sc-Zn that match the shipped serving-benchmark contract.
- Documented smoke-only benchmarking, strict failure behavior, no-silent-fallback rules, artifact paths, and the evaluation-primary specialist role across the runbook and developer docs.
- Closed the phase with a green shared CLI/real-mode regression slice and a green full repo test suite.

## Task Commits

1. **Task 1 RED: benchmark example coverage** - `e81a59b0` `test(21-03): add failing benchmark example coverage`
2. **Task 1 GREEN: benchmark example configs** - `2eef5011` `feat(21-03): add serving benchmark example configs`
3. **Task 2 GREEN: operator workflow docs** - `b5451afb` `docs(21-03): add serving benchmark operator workflow`

## Validation Results

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_real_mode_pipeline.py -x -v`
  - Result: `16 passed in 24.42s`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v`
  - Result: `31 passed in 29.95s`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
  - Result: `410 passed, 3 skipped, 1 warning in 37.07s`
- `git diff --check`
  - Result: clean before summary commit

## Decisions Made

- The hosted example stays placeholder-safe and lane-simple on purpose: it proves the benchmark surface without implying a secret managed setup flow or a second hosted lane registry.
- The committed benchmark specs point at standard acceptance-pack and campaign-spec locations so operators can adopt them directly after `llm-approve` and acceptance-pack generation instead of translating from test-only examples.
- The docs interpret benchmark output as a tradeoff surface, not a single winner: hosted, local, and specialized targets are meant to be compared across quality, cost, latency, and operator friction together.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The new repo-level benchmark example regression initially failed once after the example files were added because the temporary campaign-spec fixture directories were not created before writing test artifacts.
- I fixed the fixture setup immediately inside `materials-discovery/tests/test_real_mode_pipeline.py`, and the committed-example validation test then passed cleanly.

## User Setup Required

None - the committed benchmark examples use placeholder-safe artifact and endpoint paths, and the verification path stays fully offline in CI.

## Next Phase Readiness

- Phase 21 now has the full operator benchmark surface: typed contracts, strict execution, committed example specs, and matching docs.
- The milestone can move to closeout, audit, or the next planning step without additional serving-benchmark plumbing work.

## Self-Check

PASSED

---
*Phase: 21-comparative-benchmarks-and-operator-serving-workflow*  
*Completed: 2026-04-05*
