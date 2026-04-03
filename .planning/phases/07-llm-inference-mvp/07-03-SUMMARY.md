---
phase: 07-llm-inference-mvp
plan: 03
subsystem: llm-benchmarks
tags: [llm, benchmark, docs, regression, shell]
requires:
  - phase: 07-llm-inference-mvp
    provides: working llm-generate command, mock configs, calibration outputs
provides:
  - deterministic-vs-llm comparison helper
  - operator benchmark runner script
  - offline two-system benchmark regression coverage
  - docs refresh for implemented llm-generate behavior
affects: [phase-07, llm, docs, benchmarks, operator-workflows]
tech-stack:
  added: [benchmark helper module, shell runner, pytest marker]
  patterns: [thin orchestration, calibration-driven comparison, offline mock benchmark lane]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/benchmark.py
    - materials-discovery/scripts/run_llm_generate_benchmarks.sh
    - materials-discovery/tests/test_llm_generate_benchmarks.py
  modified:
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/src/materials_discovery/llm/generate.py
    - materials-discovery/README.md
    - materials-discovery/developers-docs/index.md
    - materials-discovery/developers-docs/llm-integration.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/pyproject.toml
    - materials-discovery/Progress.md
key-decisions:
  - "Use the generation and screen calibration JSONs as the benchmark comparison inputs instead of inventing a new metrics surface."
  - "Treat deterministic generate as a parse/compile-perfect baseline in the comparison helper so deltas stay interpretable."
  - "Keep the benchmark runner as a thin shell wrapper around committed mdisc commands, with comparison JSON written by a short Python helper call."
patterns-established:
  - "Phase 7 operator pattern: deterministic lane first, llm lane second, then compare under data/benchmarks/llm_generate/."
  - "Slow llm benchmark coverage is isolated with pytest.mark.llm_lane so it can be run separately from the default fast lane."
requirements-completed: [LLM-02]
duration: 24min
completed: 2026-04-03
---

# Phase 7: Plan 03 Summary

**Offline deterministic-vs-LLM benchmark proof, operator script, and docs refresh**

## Performance

- **Duration:** 24 min
- **Completed:** 2026-04-03T23:55:00Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- Added `llm/benchmark.py` to compare deterministic and LLM lanes using generation/screen calibration JSONs.
- Added `run_llm_generate_benchmarks.sh` as the thin operator-facing benchmark wrapper with `--systems` and `--count`.
- Added `tests/test_llm_generate_benchmarks.py` with offline benchmark coverage for both `Al-Cu-Fe` and `Sc-Zn`, plus the dedicated `llm_lane` pytest marker.
- Refreshed README and developer docs so `llm-generate` is documented as implemented, including run-artifact behavior and the benchmark runner.
- Re-ran the full `materials-discovery` suite so Phase 7 ends with project-wide green verification.

## Task Commits

This plan was checkpointed as one combined commit after the focused benchmark checks and the final full-suite pass.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/benchmark.py` - comparison helper and writer
- `materials-discovery/scripts/run_llm_generate_benchmarks.sh` - operator benchmark runner
- `materials-discovery/tests/test_llm_generate_benchmarks.py` - offline two-system benchmark tests
- `materials-discovery/src/materials_discovery/llm/__init__.py` - benchmark helper exports
- `materials-discovery/src/materials_discovery/llm/generate.py` - workspace-root seed resolution fix for config-defined seed scripts
- `materials-discovery/README.md` - llm-generate quickstart example and benchmark pointer
- `materials-discovery/developers-docs/index.md` - implemented status for the llm-generate stage
- `materials-discovery/developers-docs/llm-integration.md` - Phase 7 MVP wording and run-artifact details
- `materials-discovery/developers-docs/pipeline-stages.md` - implemented `llm-generate` stage contract
- `materials-discovery/pyproject.toml` - `llm_lane` pytest marker
- `materials-discovery/Progress.md` - required progress update

## Decisions Made

- Kept the comparison model small and explicit: parse, compile, conversion, and screen deltas only.
- Required the benchmark tests to stay offline by monkeypatching compile results while still running the real CLI commands and screen stage.
- Preserved the runner as shell-first so operators can inspect or tweak the exact `mdisc` commands without learning a new wrapper framework.

## Deviations from Plan

- No behavioral deviation. One small follow-up fix was needed during implementation: config-defined `llm_generate.seed_zomic` paths now resolve from the workspace root so the committed `Sc-Zn` mock config matches the documented path semantics.

## Issues Encountered

- The first Sc-Zn benchmark test failed because the fake compile helper assumed every compile call had an artifact root. The fix was to let seed-validation compiles succeed without persisted artifacts, which restored the intended offline benchmark behavior.

## User Setup Required

- Mock benchmark lanes are fully offline.
- The benchmark runner surfaces the Sc-Zn Java requirement explicitly when operators try to run that lane on a machine without a Java runtime.

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_generate_benchmarks.py tests/test_cli.py -x -v`
- `bash -n /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/scripts/run_llm_generate_benchmarks.sh`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
- `git diff --check`

## Next Phase Readiness

Phase 7 now has a usable inference path plus a reproducible offline comparison lane. Phase 8 can focus on richer evaluation and deeper pipeline integration instead of basic generation plumbing.

---
*Phase: 07-llm-inference-mvp*
*Completed: 2026-04-03*
