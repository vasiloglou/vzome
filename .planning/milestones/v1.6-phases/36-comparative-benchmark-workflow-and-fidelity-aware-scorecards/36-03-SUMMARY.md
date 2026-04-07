---
phase: 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards
plan: 03
subsystem: llm
tags: [external-benchmark, cli, docs, operator-workflow, llm]
requires:
  - phase: 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards
    provides: benchmark execution core, typed summaries, and deterministic llm_external artifacts
provides:
  - operator CLI commands for comparative benchmark execution and inspection
  - a committed example benchmark spec for the Al-Cu-Fe Phase 36 workflow
  - benchmark runbook and discoverability updates across the docs map and command reference
affects: [36-phase-verification, v1.6-milestone-audit, operator-onboarding]
tech-stack:
  added: []
  patterns:
    - benchmark workflows expose one JSON-producing execute command and one human-readable inspect command
    - Phase 34 and Phase 35 artifact families are linked into the Phase 36 operator docs rather than re-explained from scratch
key-files:
  created:
    - materials-discovery/tests/test_llm_external_benchmark_cli.py
    - materials-discovery/configs/llm/al_cu_fe_external_benchmark.yaml
    - materials-discovery/developers-docs/llm-external-benchmark-runbook.md
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/developers-docs/configuration-reference.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/developers-docs/index.md
    - materials-discovery/Progress.md
key-decisions:
  - "The benchmark execute command prints the typed summary JSON directly, while the inspect command provides the operator-friendly scorecard trace."
  - "The shipped example spec stays narrow and advisory, using one curated external arm plus one current internal control."
patterns-established:
  - "Phase 36 docs explicitly frame recommendation lines as milestone evidence rather than automatic checkpoint promotion."
  - "External benchmark inspect surfaces show control identity, family/fidelity slices, control deltas, and recommendation lines without requiring JSONL spelunking."
requirements-progressed: [LLM-32, LLM-33, OPS-18]
duration: 12 min
completed: 2026-04-07
---

# Phase 36 Plan 03: Comparative Benchmark Operator Surface Summary

**CLI-first comparative benchmark execution and inspect workflow with a shipped Al-Cu-Fe example spec and operator runbook**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-07T08:14:00Z
- **Completed:** 2026-04-07T08:26:00Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Added `mdisc llm-external-benchmark` and `mdisc llm-inspect-external-benchmark`
  so operators can run and inspect the Phase 36 comparative benchmark without
  custom Python.
- Added a committed `configs/llm/al_cu_fe_external_benchmark.yaml` example
  that ties together the shipped Phase 34 benchmark pack, one Phase 35
  external target ID, and one internal control arm.
- Added an external benchmark runbook and refreshed the configuration
  reference, pipeline stages guide, and docs index so the workflow is
  discoverable beside the Phase 34 and Phase 35 handoff docs.

## Task Commits

1. **Task 1: Add CLI run and inspect commands for translated comparative benchmarks** - `0071d315` (`feat(36-03): add benchmark cli commands`)
2. **Task 2: Add example benchmark spec and operator documentation for the Phase 36 workflow** - `fb6bf3ab` (`docs(36-03): add benchmark runbook and example spec`)

## Files Created/Modified

- `materials-discovery/src/materials_discovery/cli.py` - Added Phase 36
  execute/inspect commands plus scorecard trace formatting helpers.
- `materials-discovery/tests/test_llm_external_benchmark_cli.py` - Added
  focused CLI coverage for JSON summary output, inspect traces, filtering, and
  repo-standard code-2 failures.
- `materials-discovery/tests/test_cli.py` - Locked root-help discoverability
  for the new benchmark commands.
- `materials-discovery/configs/llm/al_cu_fe_external_benchmark.yaml` - Added
  the shipped example comparative benchmark spec.
- `materials-discovery/developers-docs/llm-external-benchmark-runbook.md` -
  Added the operator runbook for benchmark execution, inspect flow, artifact
  layout, and scorecard interpretation.
- `materials-discovery/developers-docs/configuration-reference.md` -
  Documented the Phase 36 benchmark spec contract.
- `materials-discovery/developers-docs/pipeline-stages.md` - Documented the
  new execute and inspect commands in the command reference.
- `materials-discovery/developers-docs/index.md` - Added the benchmark
  workflow to the docs map and quickstart sequence.
- `materials-discovery/Progress.md` - Logged the Plan 36-03 CLI and docs
  changes per repo policy.

## Validation

- Focused verification command:
  `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_cli.py tests/test_cli.py -x -v`
- Result: `24 passed in 0.53s`

## Decisions Made

- Kept the execute command JSON-first so it remains scriptable and stable for
  later tooling.
- Kept the inspect command human-readable so operators can review one scorecard
  without opening raw JSON or JSONL artifacts directly.
- Shipped one example spec that stays benchmark-first and advisory instead of
  implying automatic follow-on actions.

## Deviations from Plan

None.

## Issues Encountered

None.

## User Setup Required

The example benchmark spec still expects the Phase 35 external target
registration and smoke artifacts to exist before a real benchmark run can
complete. No extra setup is required for the focused CLI verification tests.

## Next Phase Readiness

Phase 36 now has the full operator surface required for verification:
benchmark execution, inspect flow, example config, and runbook coverage all
exist on top of the typed benchmark core.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/36-comparative-benchmark-workflow-and-fidelity-aware-scorecards/36-03-SUMMARY.md`
- Key files verified: `materials-discovery/src/materials_discovery/cli.py`, `materials-discovery/tests/test_llm_external_benchmark_cli.py`, `materials-discovery/developers-docs/llm-external-benchmark-runbook.md`
- Focused validation is green: `24 passed in 0.53s`
