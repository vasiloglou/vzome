---
phase: 37-deep-dive-provenance-audit-and-tutorial-scope
plan: 01
subsystem: documentation
tags: [provenance, docs, audit, tutorial-scope, materials-discovery, zomic]

requires:
  - phase: 36
    provides: shipped materials-discovery documentation and v1.6 translated benchmark workflow evidence
provides:
  - Git-backed provenance audit for the podcast deep-dive source document
  - Stale-claim and missing-surface inventory for the Phase 38 refresh
  - Sc-Zn Zomic-backed tutorial scope lock for Phase 39
affects: [phase-38, phase-39, materials-discovery-docs]

tech-stack:
  added: []
  patterns:
    - git-backed documentation evidence packet
    - shipped-only narrative correction checklist
    - single-path tutorial scope lock

key-files:
  created:
    - .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md
    - .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-01-SUMMARY.md
  modified:
    - .planning/STATE.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Phase 37 remains planning-only; materials-discovery/Progress.md remains intentionally unchanged because no materials-discovery files changed."
  - "Phase 39 tutorial anchor is one Sc-Zn Zomic-backed path using checked config and design artifacts."
  - "Phase 38 should soften or date volatile counts and describe the shipped surface through v1.6."

patterns-established:
  - "Evidence packet: downstream documentation phases should refresh claims from git history, milestone audits, current docs, or current source code."
  - "Tutorial lock: the first guided workflow should teach one reproducible Sc-Zn Zomic path before broader chemistry coverage."

requirements-completed: [DOC-01]

duration: 9min
completed: 2026-04-15
---

# Phase 37 Plan 01: Deep-Dive Provenance Audit and Tutorial Scope Summary

**Git-backed deep-dive provenance audit with shipped v1.0-v1.6 deltas and a locked Sc-Zn Zomic tutorial path**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-15T02:42:29Z
- **Completed:** 2026-04-15T02:51:26Z
- **Tasks:** 3
- **Files modified:** 2 planning artifacts, plus GSD state metadata after completion

## Accomplishments

- Created `37-PROVENANCE-AUDIT.md` with the required source provenance ledger, including creation and move commits for `materials-discovery/developers-docs/podcast-deep-dive-source.md`.
- Mapped post-draft shipped workflow deltas from v1.0 through v1.6 so Phase 38 has a current-state correction baseline.
- Inventoried stale quantitative claims, stale capability descriptions, missing shipped command surfaces, and future-work labeling risks.
- Locked Phase 39 to one reproducible Sc-Zn Zomic-backed tutorial path with authority artifacts, command sequence, and evidence commands.
- Kept the phase planning-only: no files under `materials-discovery/` were modified.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the provenance ledger and post-draft shipped delta matrix** - `a67667c2` (docs)
2. **Task 2: Inventory stale claims and missing shipped surfaces for Phase 38** - `4d180864` (docs)
3. **Task 3: Lock Phase 39 tutorial scope and evidence commands** - `bb989e86` (docs)

## Files Created/Modified

- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md` - Git-backed evidence packet, stale-claim inventory, shipped-surface matrix, and tutorial scope lock.
- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-01-SUMMARY.md` - Execution summary and self-check for plan 37-01.
- `.planning/STATE.md` - Updated by the GSD workflow after plan execution.
- `.planning/ROADMAP.md` - Updated by the GSD workflow after plan execution.
- `.planning/REQUIREMENTS.md` - Updated by the GSD workflow to mark DOC-01 complete.

## Decisions Made

- Phase 37 stayed under `.planning/` only. Because `materials-discovery/` was untouched, `materials-discovery/Progress.md` was intentionally not updated.
- Phase 39 should use Sc-Zn as the only worked tutorial system and defer broader chemistry coverage.
- Phase 38 should not preserve exact fast-moving counts unless they come from dated commands; it should describe backend capability with the current `mock` and `real` mode vocabulary plus fixture, exec, and native layers.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Retried task commit after transient git index lock**
- **Found during:** Task 1 (Create the provenance ledger and post-draft shipped delta matrix)
- **Issue:** The first commit attempt hit `.git/index.lock` after overlapping git operations.
- **Fix:** Confirmed no live git process or persistent lock remained, then retried the commit.
- **Files modified:** None beyond the intended audit artifact.
- **Verification:** Commit succeeded as `a67667c2`, and subsequent status checks showed no `materials-discovery/` changes.
- **Committed in:** `a67667c2`

---

**Total deviations:** 1 auto-fixed Rule 3 blocking issue
**Impact on plan:** No scope change. The task commit completed after retry and the planning-only boundary remained intact.

## Issues Encountered

No implementation issues beyond the transient git index lock documented above.

## Auth Gates

None.

## Known Stubs

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 38 can refresh the long-form deep-dive from `37-PROVENANCE-AUDIT.md` without redoing provenance research. Phase 39 has a locked Sc-Zn Zomic-backed tutorial path, artifact set, and command sequence ready for tutorial authoring.

## Self-Check: PASSED

- Found `37-PROVENANCE-AUDIT.md`.
- Found `37-01-SUMMARY.md`.
- Verified task commits `a67667c2`, `4d180864`, and `bb989e86`.
- Verified `materials-discovery/` remains untouched.

---
*Phase: 37-deep-dive-provenance-audit-and-tutorial-scope*
*Completed: 2026-04-15*
