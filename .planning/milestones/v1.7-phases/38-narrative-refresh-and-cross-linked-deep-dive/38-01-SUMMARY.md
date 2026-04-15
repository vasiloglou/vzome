---
phase: 38-narrative-refresh-and-cross-linked-deep-dive
plan: 01
subsystem: documentation
tags: [docs, narrative, materials-discovery, runbooks, cross-links, v1.6]

requires:
  - phase: 37
    provides: provenance audit, stale-claim inventory, and Sc-Zn tutorial scope lock
provides:
  - Refreshed long-form deep-dive narrative aligned to shipped materials-discovery workflow through v1.6
  - Source-of-truth cross-links for current operator and developer docs
  - Explicit shipped-vs-future boundaries for campaigns, checkpoints, visualization, and chemistry expansion
  - Required materials-discovery progress log entry for the narrative refresh
affects: [phase-39, materials-discovery-docs, tutorial-onboarding]

tech-stack:
  added: []
  patterns:
    - workflow-family documentation instead of frozen command counts
    - same-change materials-discovery progress logging
    - shipped-vs-future narrative labeling

key-files:
  created:
    - .planning/phases/38-narrative-refresh-and-cross-linked-deep-dive/38-01-SUMMARY.md
  modified:
    - materials-discovery/developers-docs/podcast-deep-dive-source.md
    - materials-discovery/Progress.md
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md

key-decisions:
  - "Preserve the early geometry and vZome origin story as substantial narrative anchors."
  - "Describe the shipped system through v1.6 as workflow families rather than a seven-command-only pipeline."
  - "Label autonomous campaigns, checkpoint training automation, reverse import or new exporters, and broad chemistry expansion as future work."

patterns-established:
  - "Narrative refreshes should cross-link source-of-truth docs instead of duplicating operator procedures."
  - "Volatile repo-state counts should be removed unless intentionally regenerated and explicitly dated."

requirements-completed: [DOC-02, DOC-03]

duration: 14min
completed: 2026-04-15
---

# Phase 38 Plan 01: Narrative Refresh and Cross-Linked Deep Dive Summary

**Workflow-family deep-dive refresh with source-of-truth cross-links and explicit future-work boundaries**

## Performance

- **Duration:** 14 min
- **Started:** 2026-04-15T04:00:00Z
- **Completed:** 2026-04-15T04:14:07Z
- **Tasks:** 3
- **Files modified:** 2 materials-discovery docs, plus planning metadata after completion

## Accomplishments

- Reframed the stale implementation story into current workflow families that match the shipped `materials-discovery/` surface through `v1.6`.
- Kept the origin story substantial so the history and math-heavy framing still explains why the project is Zomic- and vZome-centered.
- Added current source-of-truth cross-links for the operator runbook, pipeline stages, geometry tutorial, backend notes, and the newer translation and benchmarking docs.
- Removed stale counts and stale system-shape claims, including the old seven-stage, four-layer, and fixed-count descriptions that no longer reflect the repo.
- Updated `materials-discovery/Progress.md` in the same change, including both the changelog row and diary entry required by repo policy.

## Task Commits

Each task was committed atomically where it changed repo state:

1. **Task 1-3: Refresh the narrative, add cross-links, and update Progress.md** - `289cc9d3` (`docs(38): refresh deep-dive narrative`)

Planning refinement before execution was captured earlier in:

- `a7c4b749` (`docs(38): revise plan from review feedback`)

## Files Created/Modified

- `materials-discovery/developers-docs/podcast-deep-dive-source.md` - refreshed narrative, updated cross-links, current command families, and future-work boundaries.
- `materials-discovery/Progress.md` - changelog row and diary entry for the Phase 38 materials-discovery doc refresh.
- `.planning/phases/38-narrative-refresh-and-cross-linked-deep-dive/38-01-SUMMARY.md` - execution summary and closeout for plan 38-01.
- `.planning/PROJECT.md` - advanced the milestone narrative to Phase 39.
- `.planning/ROADMAP.md` - marked Phase 38 complete.
- `.planning/REQUIREMENTS.md` - marked DOC-02 and DOC-03 complete.
- `.planning/STATE.md` - advanced the active phase to Phase 39.

## Decisions Made

- Preserve about half of the original history and math-heavy story rather than replacing it with a purely operational runbook.
- Fold the post-v1.0 serving, checkpoint, translation, and external benchmarking surfaces in prominently enough that the document reads like the current system, not a 2026-03 snapshot.
- Prefer removing stale numeric snapshots unless they are intentionally regenerated and explicitly dated in-line.

## Deviations from Plan

No material deviations. The planned docs work landed as one consolidated repo change so the required `materials-discovery/Progress.md` update stayed coupled to the deep-dive edit.

## Issues Encountered

None.

## Auth Gates

None.

## Known Stubs

None. The doc now explicitly marks future work instead of leaving implied shipped capability gaps.

## User Setup Required

None.

## Verification

- `git diff --check`
- `rg` checks for current command surfaces, cross-links, future-work labels, and stale-string removal
- `cd materials-discovery && uv run pytest tests/test_cli.py -q` -> `18 passed`

## Next Phase Readiness

Phase 39 can now build the guided tutorial from the refreshed narrative and the locked Sc-Zn evidence packet without re-auditing the deep-dive source.

## Self-Check: PASSED

- Found `38-01-SUMMARY.md`.
- Found the Phase 38 docs commit `289cc9d3`.
- Verified `materials-discovery/Progress.md` changed in the same repo edit as the narrative refresh.
- Verified DOC-02 and DOC-03 are now marked complete in `.planning/REQUIREMENTS.md`.

---
*Phase: 38-narrative-refresh-and-cross-linked-deep-dive*
*Completed: 2026-04-15*
