---
phase: 12-replay-comparison-and-operator-workflow
plan: 02
subsystem: llm
tags: [llm, replay, compare, cli, pytest]
requires:
  - phase: 12-replay-comparison-and-operator-workflow
    provides: replay/comparison contracts and deterministic storage helpers
provides:
  - strict llm-replay CLI over recorded launch bundles
  - llm-compare CLI with typed JSON artifacts and concise operator summaries
  - replay-aware candidate/run lineage without changing the existing launch path
affects: [milestone-v1.1-closeout, llm-replay, llm-compare, cli]
tech-stack:
  added: []
  patterns:
    [
      strict replay without override flags,
      typed JSON plus terminal-summary operator outputs,
      additive lineage over existing llm-generate manifests,
    ]
key-files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/src/materials_discovery/llm/generate.py
    - materials-discovery/tests/test_llm_replay_cli.py
    - materials-discovery/tests/test_llm_compare_cli.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/Progress.md
key-decisions:
  - "Replay stays strict in Phase 12: `mdisc llm-replay` accepts a launch summary and does not expose behavioral override flags."
  - "Compare always writes durable JSON artifacts before printing its human-readable terminal summary."
  - "Replay lineage is additive in manifests and candidate provenance so earlier launch contracts remain compatible."
patterns-established:
  - "Operator-facing replay and compare commands stay thin wrappers over the typed replay/compare core helpers established in [12-01-SUMMARY.md](./12-01-SUMMARY.md)."
  - "Phase 12 proof is cumulative: this summary closes the CLI contract before [12-03-SUMMARY.md](./12-03-SUMMARY.md) proves the end-to-end runbook workflow."
requirements-completed: [LLM-09, LLM-11, OPS-07]
duration: 5min
completed: 2026-04-04
---

# Phase 12 Plan 02: Replay and Compare CLI Summary

**Phase 12 turned the replay/comparison contracts into real operator commands: `mdisc llm-replay` for strict reruns and `mdisc llm-compare` for typed outcome comparisons plus readable summaries.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-04T17:30:02Z
- **Completed:** 2026-04-04T17:34:59Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added `mdisc llm-replay --launch-summary ...`, which reuses the recorded launch bundle, emits a fresh replay launch wrapper, records config drift safely, and writes replay-safe candidate paths under the standard candidates root.
- Added `mdisc llm-compare --launch-summary ...`, which writes `outcome_snapshot.json` and a campaign comparison JSON, always compares against the acceptance-pack baseline, and includes the most recent prior launch when present.
- Updated `generate.py` so replayed launches propagate additive replay lineage into run manifests and candidate provenance without changing the original Phase 11 launch flow.
- Added CLI regression coverage for success paths, missing-summary failures, and operator-readable output expectations.

## Task Commits

1. **Plan 02 implementation:** `e67cd281` `feat(12-02): add replay and compare commands`

Plan metadata and the retroactive audit-chain restoration are recorded separately in Phase 15 closure commits.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/cli.py` - Adds `llm-replay` and `llm-compare` as first-class CLI commands.
- `materials-discovery/src/materials_discovery/llm/generate.py` - Carries replay lineage additively into run manifests and candidate provenance when replay metadata is present.
- `materials-discovery/tests/test_llm_replay_cli.py` - Covers strict replay success, config-drift recording, replay-safe output paths, and clear failure behavior.
- `materials-discovery/tests/test_llm_compare_cli.py` - Covers comparison artifact writing, acceptance-pack baselines, prior-launch handling, and concise terminal summaries.
- `materials-discovery/tests/test_cli.py` - Keeps shared CLI registration and missing-summary failure surfaces green.
- `materials-discovery/Progress.md` - Logged the original Plan 02 implementation and verification when Phase 12 shipped.

## Verification

Original focused verification during Phase 12 execution:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py tests/test_cli.py -x -v`
  - Result at ship time: green

Retroactive audit refresh during Phase 15:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py tests/test_cli.py -x -v`
  - Result: `17 passed in 0.37s`

## Decisions Made

- The replay entrypoint is a saved `launch_summary.json`, not a mutable config or a replay-specific YAML.
- Compare produces durable machine-readable artifacts first and human-readable summaries second.
- Missing launch-summary inputs remain operator-facing errors with exit code 2 rather than silent no-ops.

## Deviations from Plan

None.

## Issues Encountered

None. The focused CLI/operator replay and compare tests still pass cleanly under the Phase 15 audit refresh.

## User Setup Required

None. The CLI workflow remains offline-compatible with the mock campaign fixtures.

## Next Phase Readiness

- [12-01-SUMMARY.md](./12-01-SUMMARY.md) captures the contract and helper layer this CLI surface depends on.
- [12-03-SUMMARY.md](./12-03-SUMMARY.md) closes the loop with the offline end-to-end operator regression plus the runbook and developer-doc updates.

Together, [12-01-SUMMARY.md](./12-01-SUMMARY.md), [12-02-SUMMARY.md](./12-02-SUMMARY.md), and [12-03-SUMMARY.md](./12-03-SUMMARY.md) form the full Phase 12 audit chain.

## Self-Check

PASSED

---
*Phase: 12-replay-comparison-and-operator-workflow*
*Completed: 2026-04-04*
