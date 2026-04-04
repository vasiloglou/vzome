---
phase: 08-llm-evaluation-and-pipeline-integration
plan: 03
subsystem: llm-pipeline-benchmarking
tags: [llm, benchmarking, downstream-pipeline, docs, operator-script]
requires:
  - phase: 08-llm-evaluation-and-pipeline-integration
    provides: llm-evaluate report integration and additive calibration metrics
provides:
  - downstream deterministic-vs-llm comparison helper
  - operator-facing benchmark runner script
  - offline Al-Cu-Fe and Sc-Zn benchmark regressions
affects: [phase-08, llm, benchmarking, docs, cli]
tech-stack:
  added: [pipeline benchmark helper, lane snapshot script, offline benchmark regression]
  patterns: [stage-calibration snapshots, temporary benchmark configs, two-system parity checks]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/pipeline_benchmark.py
    - materials-discovery/scripts/run_llm_pipeline_benchmarks.sh
    - materials-discovery/tests/test_llm_pipeline_benchmarks.py
  modified:
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/README.md
    - materials-discovery/developers-docs/index.md
    - materials-discovery/developers-docs/llm-integration.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/Progress.md
key-decisions:
  - "Benchmark both deterministic and llm lanes through the same downstream stages, including llm-evaluate, so report-level acceptance metrics stay comparable."
  - "Capture lane stage metrics immediately after each command instead of reading reused calibration paths later, which avoids cross-lane overwrite bugs."
  - "Keep the benchmark offline by injecting temporary llm_evaluate fixture configs rather than requiring new committed system YAMLs."
patterns-established:
  - "Phase 8 benchmark artifact: data/benchmarks/llm_pipeline/{system}_comparison.json."
  - "Operator script pattern: generate temporary benchmark configs -> run both lanes -> snapshot calibrations -> build comparison."
requirements-completed: [LLM-04]
duration: 22min
completed: 2026-04-03
---

# Phase 8: Plan 03 Summary

**Benchmark deterministic vs LLM lanes through the downstream pipeline**

## Performance

- **Duration:** 22 min
- **Completed:** 2026-04-04T01:05:00Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added `llm/pipeline_benchmark.py` to compare deterministic and LLM lanes across `screen`, `hifi-validate`, `hifi-rank`, and `report`.
- Added `run_llm_pipeline_benchmarks.sh`, which writes temporary offline `llm_evaluate` configs, runs both lanes, snapshots per-stage calibration JSON, and writes a comparison artifact under `data/benchmarks/llm_pipeline/`.
- Added offline two-system regression coverage for `Al-Cu-Fe` and `Sc-Zn`, proving the downstream benchmark lane works without network access.
- Refreshed top-level and developer docs so `llm-evaluate` is documented as implemented and the new pipeline benchmark workflow is discoverable.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/pipeline_benchmark.py` - downstream comparison helper and writer
- `materials-discovery/scripts/run_llm_pipeline_benchmarks.sh` - operator benchmark script
- `materials-discovery/tests/test_llm_pipeline_benchmarks.py` - helper and offline two-system benchmark coverage
- `materials-discovery/src/materials_discovery/llm/__init__.py` - exported benchmark helper surface
- `materials-discovery/README.md` - benchmark quickstart refresh
- `materials-discovery/developers-docs/index.md` - status/docs map refresh
- `materials-discovery/developers-docs/llm-integration.md` - Phase 8 implementation notes
- `materials-discovery/developers-docs/pipeline-stages.md` - implemented `llm-evaluate` reference
- `materials-discovery/Progress.md` - required materials-discovery progress update

## Decisions Made

- Benchmarked both lanes through `llm-evaluate` so report-level `llm_assessed_count` and release-gate outputs remain apples-to-apples.
- Avoided committed benchmark-only configs by generating temporary configs with deterministic offline evaluation fixtures inside the script.
- Kept the comparison helper calibration-driven so tests and scripts can avoid reparsing raw report JSON whenever stage metrics already exist.

## Deviations from Plan

- `tests/test_cli.py` did not need new assertions because the dedicated benchmark regression file now covers the Phase 8 CLI orchestration path end to end.

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_pipeline_benchmarks.py tests/test_cli.py -x -v`
- `bash -n /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery/scripts/run_llm_pipeline_benchmarks.sh`
- `git diff --check`

## Next Phase Readiness

Phase 9 can now define acceptance metrics on top of a real, reproducible downstream benchmark lane instead of inventing those metrics in the abstract.

---
*Phase: 08-llm-evaluation-and-pipeline-integration*
*Completed: 2026-04-03*
