---
phase: 12-replay-comparison-and-operator-workflow
plan: 03
subsystem: llm
tags: [llm, replay, compare, docs, pytest, runbook]
requires:
  - phase: 12-replay-comparison-and-operator-workflow
    provides: replay/compare contracts and CLI commands
provides:
  - offline end-to-end suggest -> approve -> launch -> replay -> compare regression coverage
  - replay-aware lineage normalization coverage
  - operator docs for strict replay, comparison baselines, and on-disk audit artifacts
affects: [milestone-v1.1-closeout, llm-launch, llm-suggest, llm-approve]
tech-stack:
  added: []
  patterns: [offline closed-loop regression, strict replay auditability, additive operator docs]
key-files:
  created: []
  modified:
    - materials-discovery/tests/test_real_mode_pipeline.py
    - materials-discovery/tests/test_llm_campaign_lineage.py
    - materials-discovery/RUNBOOK.md
    - materials-discovery/developers-docs/llm-integration.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/Progress.md
key-decisions:
  - "Phase 12 replay remains strict: it records config drift for operators but offers no behavioral override knobs."
  - "Comparison always includes the acceptance-pack baseline and includes the prior-launch baseline when one exists."
  - "The operator story should mirror the real CLI sequence rather than teaching helper-level internals."
patterns-established:
  - "Closed-loop LLM work now has a single offline operator proof from suggestion through comparison."
  - "Replay lineage is additive and normalized in the same llm_campaign payload used by launch."
requirements-completed: [LLM-09, LLM-11, OPS-07]
duration: 8min
completed: 2026-04-04
---

# Phase 12 Plan 03: Replay, Comparison, and Operator Workflow Summary

**Phase 12 now closes the loop for operators: suggestions can be approved, launched, replayed, and compared through one documented, offline-safe workflow.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-04T17:35:00Z
- **Completed:** 2026-04-04T17:43:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added an offline end-to-end regression that drives the actual CLI commands from `llm-suggest` through `llm-compare` using the committed mock LLM config.
- Extended campaign-lineage coverage so replay fields survive normalization and downstream manifest propagation without introducing nested lineage payloads.
- Updated the operator runbook and developer docs to explain strict replay, immutable outcome snapshots, acceptance-pack plus prior-launch comparison baselines, and the on-disk audit trail.

## Task Commits

1. **Plan 03 implementation:** `919e968e` `feat(12-03): add replay compare operator workflow`

Plan metadata and execution-state updates are recorded in the docs/state commit for this summary.

## Files Created/Modified

- `materials-discovery/tests/test_real_mode_pipeline.py` - Adds the offline full closed-loop operator regression for suggest, approve, launch, replay, and compare.
- `materials-discovery/tests/test_llm_campaign_lineage.py` - Extends lineage normalization coverage to include `replay_of_launch_id` and `replay_of_launch_summary_path`.
- `materials-discovery/RUNBOOK.md` - Adds the end-to-end closed-loop workflow section, audit-trail locations, and quick-reference entries for the new CLI commands.
- `materials-discovery/developers-docs/llm-integration.md` - Documents Phase 12 replay authority, strict-drift posture, immutable outcome snapshots, and comparison semantics.
- `materials-discovery/developers-docs/pipeline-stages.md` - Adds full CLI contract sections for `mdisc llm-replay` and `mdisc llm-compare`.
- `materials-discovery/Progress.md` - Logs the Phase 12 Plan 03 execution and verification results.

## Verification

Focused checks:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "llm_replay or llm_compare or campaign" tests/test_llm_campaign_lineage.py -x -v`
  - Result: `4 passed, 7 deselected`
- `git diff --check`
  - Result: clean

Full regression sweep:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
  - Result: `374 passed, 3 skipped, 1 warning`

## Decisions Made

- Replay remains strict and bundle-driven in Phase 12; the command records config drift but does not offer override flags.
- Comparison artifacts are anchored to immutable outcome snapshots so historical launch outcomes do not depend on later mutable workspace state.
- The runbook documents the exact CLI sequence operators should use, rather than abstracting the workflow into helper concepts.

## Deviations from Plan

None.

## Issues Encountered

The original focused Phase 12 pytest selector did not pick up the new end-to-end regression because the test name did not match the planned `-k "llm_replay or llm_compare or campaign"` expression. Renaming the test to include the planned selector terms resolved the issue immediately, and the exact planned command then passed.

## User Setup Required

None. The Phase 12 workflow remains offline-compatible with the committed mock config and does not require live providers or Java.

## Next Phase Readiness

- Milestone `v1.1` is now technically complete and ready for milestone audit/closeout.
- The next logical workflow step is `gsd-audit-milestone` or `gsd-complete-milestone`.

## Self-Check

PASSED

---
*Phase: 12-replay-comparison-and-operator-workflow*
*Completed: 2026-04-04*
