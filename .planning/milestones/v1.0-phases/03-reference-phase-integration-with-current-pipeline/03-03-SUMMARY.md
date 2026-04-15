---
phase: 03-reference-phase-integration-with-current-pipeline
plan: 03
subsystem: materials-discovery
tags: [integration, pipeline, hull-proxy, report, no-dft, regression, materials-discovery]
requires: [03-01, 03-02]
provides:
  - source-backed real-mode pipeline smoke coverage
  - downstream projected-reference regression checks for hull_proxy and report
  - explicit no-DFT ingest guard plus deterministic validated-artifact cleanup
affects: [phase-03-completion, phase-04-planning, PIPE-01, OPS-03]
tech-stack:
  added: [dynamic source-backed test configs]
  patterns: [isolated dynamic system slugs for integration tests, explicit no-dft ingest guards, test-lane cleanup for deterministic suites]
key-files:
  created:
    - .planning/phases/03-reference-phase-integration-with-current-pipeline/03-03-SUMMARY.md
  modified:
    - materials-discovery/tests/test_active_learn.py
    - materials-discovery/tests/test_hull_proxy.py
    - materials-discovery/tests/test_real_mode_pipeline.py
    - materials-discovery/tests/test_report.py
    - materials-discovery/Progress.md
key-decisions:
  - "Run source-backed integration smokes under a unique system_name so they do not clobber the legacy Al-Cu-Fe artifact lane."
  - "Keep the explicit no-DFT ingest guard in integration coverage where the full bridge path is exercised."
  - "Clean stale validated artifacts in test_active_learn so the full suite remains deterministic after integration runs."
patterns-established:
  - "Dynamic source-backed configs inherit the real-mode baseline and override only the ingest seam plus artifact root."
  - "Projected processed rows can be generated inline in tests and consumed directly by hull_proxy without committed fixtures."
requirements-completed: [DATA-05, PIPE-01, OPS-03]
duration: 27min
completed: 2026-04-03
---

# Phase 3 Plan 03: Prove Pipeline Compatibility And No-DFT Guardrails Summary

**End-to-end source-backed pipeline coverage, projected-row downstream regression checks, and explicit ingest no-DFT protection**

## Performance

- **Duration:** 27 min
- **Started:** 2026-04-03T10:00:00-04:00
- **Completed:** 2026-04-03T10:27:00-04:00
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added a source-backed real-mode pipeline smoke test that dynamically builds a
  `source_registry_v1` config, stages local fixture data, and runs the full
  `ingest -> report` flow.
- Added targeted downstream coverage proving projected/enriched processed rows
  remain compatible with `hull_proxy` and that `report` stays green after a
  source-backed ingest path.
- Added an explicit no-DFT ingest guard in integration coverage and hardened
  `test_active_learn.py` so stale validated artifacts do not leak across runs.
- Re-ran the full subsystem test suite successfully after the integration
  changes.

## Task Commits

1. **Task 1: Add a source-backed real-mode pipeline smoke test** - `7290e34f` (`test`)
2. **Task 2: Add targeted downstream compatibility coverage for projected reference phases** - `7290e34f` (`test`)
3. **Task 3: Lock the no-DFT boundary and offline bridge behavior in tests** - `7290e34f` (`test`)

## Verification

- `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py tests/test_hull_proxy.py tests/test_report.py tests/test_ingest_source_registry.py tests/test_ingest.py`
- `cd materials-discovery && uv run pytest`

Both verification commands passed, with the full subsystem suite ending at `105 passed`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Dynamic source-backed integration smoke initially overwrote the shared `Al-Cu-Fe` processed reference-phase lane**

- **Found during:** Full-suite verification after the first Wave 3 implementation pass
- **Issue:** The new source-backed integration smoke reused the legacy `Al-Cu-Fe` system slug, which changed the processed reference-phase file that unrelated downstream tests expect.
- **Fix:** Moved the dynamic integration smoke and report regression to an isolated `Al-Cu-Fe-SourceRegistry` system name so the source-backed lane stays separate from the legacy baseline.
- **Files modified:** `materials-discovery/tests/test_real_mode_pipeline.py`, `materials-discovery/tests/test_report.py`
- **Verification:** `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py tests/test_hull_proxy.py tests/test_report.py tests/test_ingest_source_registry.py tests/test_ingest.py` and `cd materials-discovery && uv run pytest`
- **Committed in:** `7290e34f`

**2. [Rule 3 - Blocking] Full-suite active-learn regression was reading stale validated artifacts from prior runs**

- **Found during:** Full-suite verification after the integration smoke landed
- **Issue:** `test_active_learn.py` aggregated all matching validated files under `data/hifi_validated/`, so prior test runs could inflate the validated candidate count.
- **Fix:** Cleared the current system’s stale validated files at the start of the test helper before generating fresh validated inputs.
- **Files modified:** `materials-discovery/tests/test_active_learn.py`
- **Verification:** `cd materials-discovery && uv run pytest`
- **Committed in:** `7290e34f`

---

**Total deviations:** 2 auto-fixed
**Impact on plan:** Both fixes were determinism blockers in the verification lane only. They tightened the suite without changing production behavior or phase scope.

## Issues Encountered

None beyond the auto-fixed verification blockers documented above.

## Next Phase Readiness

- Phase 3 is complete: source-backed reference-phase ingest now feeds the
  existing no-DFT pipeline through the stable CLI.
- Phase 4 can focus on improving the discovery workflow itself instead of
  bridge infrastructure, because the new ingestion seam is now protected by
  end-to-end and downstream regressions.

## Self-Check: PASSED

- Verified commit `7290e34f` exists in git history.
- Verified focused Wave 3 commands and the full `materials-discovery` pytest suite pass.
