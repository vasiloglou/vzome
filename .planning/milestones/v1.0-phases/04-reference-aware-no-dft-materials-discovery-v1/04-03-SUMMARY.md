---
phase: 04-reference-aware-no-dft-materials-discovery-v1
plan: 03
subsystem: testing
tags: [bash, pytest, benchmark, reference-pack, benchmark-pack, materials-discovery, no-dft]

requires:
  - phase: 04-02
    provides: BenchmarkRunContext, write_benchmark_pack, rank provenance embedding, report benchmark surfacing

provides:
  - operator-facing run_reference_aware_benchmarks.sh benchmark runner script
  - reference-aware-benchmarks.md runbook with full prerequisites and artifact docs
  - two-system (Al-Cu-Fe + Sc-Zn) E2E benchmark regression tests marked benchmark_lane
  - downstream rank/report Phase 4 coverage for both benchmark systems
  - cross-lane Al-Cu-Fe comparison test protecting the operator comparison story

affects:
  - Phase 05 (any benchmark analytics or reporting built on top of Phase 4 outputs)
  - Phase 06 (LLM integration — Phase 4 benchmark packs become evaluation inputs)

tech-stack:
  added: []
  patterns:
    - "benchmark_lane pytest marker for the slower two-system E2E lane"
    - "graceful Java/Zomic skip in Sc-Zn tests when Java is absent"
    - "config-driven benchmark runner with --count/--seed/--config-filter/--no-active-learn/--dry-run overrides"

key-files:
  created:
    - materials-discovery/scripts/run_reference_aware_benchmarks.sh
    - materials-discovery/developers-docs/reference-aware-benchmarks.md
    - .planning/phases/04-reference-aware-no-dft-materials-discovery-v1/04-03-SUMMARY.md
  modified:
    - materials-discovery/README.md
    - materials-discovery/developers-docs/index.md
    - materials-discovery/tests/test_real_mode_pipeline.py
    - materials-discovery/tests/test_hifi_rank.py
    - materials-discovery/tests/test_report.py
    - materials-discovery/pyproject.toml
    - materials-discovery/Progress.md

key-decisions:
  - "Keep benchmark runner thin: config-driven wrapper around mdisc stage commands, not a new orchestration framework"
  - "Use benchmark_lane pytest marker rather than silently folding new configs into the existing quick path"
  - "Sc-Zn Java/Zomic skip on absent JVM at runtime (not at import time) to keep CI viable without special env vars"
  - "Cross-lane comparison targets Al-Cu-Fe baseline-real vs reference-aware-real: structure-focused assertions, not exact metric equality"
  - "benchmark_pack path is based on system_name slug (al_cu_fe, sc_zn), not config filename"

requirements-completed:
  - PIPE-02
  - PIPE-03

duration: 8min
completed: 2026-04-03
---

# Phase 4 Plan 03: Ship Benchmark Runbooks And End-To-End Verification Summary

**Config-driven two-system benchmark runner, operator runbook, and 172 tests including Al-Cu-Fe vs reference-aware cross-lane comparison and full Sc-Zn E2E coverage**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-03T15:40:25Z
- **Completed:** 2026-04-03T15:48:25Z
- **Tasks:** 3
- **Files modified:** 8 (5 modified, 3 created)

## Accomplishments

- Committed `run_reference_aware_benchmarks.sh`: config-driven runner for both Phase 4 benchmark lanes with `--count`, `--seed`, `--config-filter`, `--no-active-learn`, `--dry-run` overrides; prints benchmark-pack artifact paths on completion
- Committed `reference-aware-benchmarks.md`: full operator runbook covering prerequisites (Python env, Java/Zomic dependency for Sc-Zn), smoke run commands, config table, reference-pack input paths, benchmark-pack output structure, and regression test commands
- Added `test_al_cu_fe_reference_aware_benchmark_e2e` and `test_sc_zn_reference_aware_benchmark_e2e`: full pipeline E2E tests marked `@pytest.mark.integration @pytest.mark.benchmark_lane`; both assert on ingest pack lineage (pack_id, member_sources), pipeline manifest, and benchmark_pack.json structure; Sc-Zn test gracefully skips generate+ stages when Java is absent
- Extended `test_hifi_rank.py` with Sc-Zn Phase 4 rank coverage and cross-system context-key comparability assertion
- Extended `test_report.py` with Al-Cu-Fe and Sc-Zn report-level benchmark_context coverage plus the final cross-lane comparison test
- Phase 4 fully closes with protected operator comparison story: 172 tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Generalize the benchmark runner and document the operator path** - `2c7e774c` (feat)
2. **Task 2: Add two-system end-to-end benchmark regression coverage** - `a657f2fd` (test)
3. **Task 3: Lock the final comparison story across source/backend lanes** - `4d806fcc` (test)

## Files Created/Modified

- `materials-discovery/scripts/run_reference_aware_benchmarks.sh` - Config-driven Phase 4 benchmark runner with overrides and summary output
- `materials-discovery/developers-docs/reference-aware-benchmarks.md` - Operator runbook for Phase 4 benchmark workflow
- `materials-discovery/README.md` - Phase 4 benchmark runner quickstart section + runbook link
- `materials-discovery/developers-docs/index.md` - Runbook in Documentation Map; Phase 4 configs in Chemical Systems table
- `materials-discovery/tests/test_real_mode_pipeline.py` - Two Phase 4 E2E benchmark tests for Al-Cu-Fe and Sc-Zn reference-aware lanes
- `materials-discovery/tests/test_hifi_rank.py` - Sc-Zn rank context coverage; cross-system context-key comparability
- `materials-discovery/tests/test_report.py` - Al-Cu-Fe/Sc-Zn report context coverage; cross-lane comparison test
- `materials-discovery/pyproject.toml` - `benchmark_lane` pytest marker registered
- `materials-discovery/Progress.md` - Changelog rows and diary entries for all three tasks

## Decisions Made

- Kept the benchmark runner thin — a config-driven wrapper around existing `mdisc` stage commands rather than a new orchestration framework. The plan required this explicitly.
- Used `benchmark_lane` pytest marker to isolate slower E2E tests rather than silently folding them into the existing quick parametrization.
- Sc-Zn Java/Zomic skip is conditional at runtime (not import time): when Java is absent and generate fails, the test skips the generate+ stages but still asserts ingest lineage.
- Cross-lane comparison chose Al-Cu-Fe `real` vs `reference-aware real` (same backend mode, different source pack) — makes source differences maximally visible without MLIP mode differences confounding the comparison.
- Benchmark pack path uses `system_name` slug, not config filename — so both `al_cu_fe_real.yaml` and `al_cu_fe_reference_aware.yaml` write to `al_cu_fe_benchmark_pack.json`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

Phase 4 is fully complete. Deliverables ready for Phase 5:
- Both benchmark systems have committed reference-pack inputs, benchmark-pack outputs, and regression coverage
- The operator benchmark runner is script-accessible and documented
- The cross-lane comparison story is regression-tested
- 172 tests pass, including 7 new benchmark_lane tests

---
*Phase: 04-reference-aware-no-dft-materials-discovery-v1*
*Completed: 2026-04-03*
