---
phase: 39-guided-design-evaluation-and-visualization-tutorial
plan: 01
subsystem: documentation
tags: [docs, tutorial, materials-discovery, zomic, vzome, sc-zn]

requires:
  - phase: 37
    provides: locked Sc-Zn tutorial path and artifact contract
  - phase: 38
    provides: refreshed narrative baseline and current cross-links
provides:
  - Checked guided tutorial for the Sc-Zn Zomic-backed design -> evaluate -> visualize workflow
  - Docs index link for the new tutorial page
  - Required materials-discovery progress log entry for the tutorial work
affects: [materials-discovery-docs, onboarding, milestone-v1.7]

tech-stack:
  added: []
  patterns:
    - single-example operator tutorial
    - geometry-authority-chain documentation
    - same-change materials-discovery progress logging

key-files:
  created:
    - .planning/phases/39-guided-design-evaluation-and-visualization-tutorial/39-01-SUMMARY.md
    - materials-discovery/developers-docs/guided-design-tutorial.md
  modified:
    - materials-discovery/developers-docs/index.md
    - materials-discovery/Progress.md
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md

key-decisions:
  - "Keep the tutorial on one Sc-Zn Zomic-backed example instead of broadening to a second chemistry."
  - "Teach interpretation from the checked snapshot even when the batch outcome is hold/watch rather than promotion-ready."
  - "Use the existing vZome/Zomic toolchain by documenting the `.zomic` -> raw export -> orbit-library -> candidate authority chain."

patterns-established:
  - "Tutorial docs should show one runnable path, one artifact table, and one interpretation layer instead of scattering examples across multiple systems."
  - "Geometry docs should explicitly separate editable source geometry from downstream derived materials artifacts."

requirements-completed: [OPS-19, OPS-20, OPS-21]

duration: 9min
completed: 2026-04-15
---

# Phase 39 Plan 01: Guided Design, Evaluation, and Visualization Tutorial Summary

**Sc-Zn Zomic-backed tutorial for design, evaluation, artifact reading, and vZome handoff**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-15T04:14:07Z
- **Completed:** 2026-04-15T04:23:13Z
- **Tasks:** 3
- **Files modified:** 3 materials-discovery docs, plus planning metadata after completion

## Accomplishments

- Created `materials-discovery/developers-docs/guided-design-tutorial.md` with one runnable Sc-Zn Zomic-backed workflow from `export-zomic` through `report`.
- Added stage-by-stage artifact tables and read-only `jq` inspection snippets so the tutorial teaches what to inspect, not just what to type.
- Taught the current evidence surface honestly: the checked snapshot stays in `hold` / `watch`, and the tutorial explains why.
- Added an explicit geometry authority chain so readers know the `.zomic` file is still the editable design source.
- Wired the tutorial into the docs index and updated `materials-discovery/Progress.md` in the same change set required by repo policy.

## Task Commits

Each task was committed atomically where it changed repo state:

1. **Task 1: Create the Phase 39 planning packet** - `6fb819ca` (`docs(39): plan guided tutorial phase`)
2. **Task 2-3: Publish the tutorial, index link, and Progress update** - `0b8592f8` (`docs(39): add guided design tutorial`)

## Files Created/Modified

- `materials-discovery/developers-docs/guided-design-tutorial.md` - new guided tutorial with commands, artifact paths, interpretation notes, and visualization guidance.
- `materials-discovery/developers-docs/index.md` - documentation-map link to the new tutorial.
- `materials-discovery/Progress.md` - changelog row and diary entry for the Phase 39 tutorial work.
- `.planning/phases/39-guided-design-evaluation-and-visualization-tutorial/39-01-SUMMARY.md` - execution summary and closeout for plan 39-01.
- `.planning/PROJECT.md` - advanced the milestone state to all phases complete.
- `.planning/ROADMAP.md` - marked Phase 39 complete.
- `.planning/REQUIREMENTS.md` - marked OPS-19, OPS-20, and OPS-21 complete.
- `.planning/STATE.md` - recorded that all v1.7 phases are complete and the milestone is ready for lifecycle work.

## Decisions Made

- Keep the tutorial on one Sc-Zn example instead of widening the scope.
- Use exact checked snapshot values only where they help the reader interpret current artifacts, and date them inline.
- Describe visualization through the existing desktop Zomic editor and export chain rather than inventing a new viewer path.

## Deviations from Plan

No material deviations. The user-facing docs change landed as one coupled commit so the tutorial, docs-index link, and required `Progress.md` update stayed together.

## Issues Encountered

None.

## Auth Gates

None.

## Known Stubs

None. The tutorial teaches the current shipped path without adding new code or new visualization exporters.

## User Setup Required

Local Java is still required for the Zomic export path. The tutorial points readers to the runbook for extra MLIP setup when they move beyond the checked path.

## Verification

- `git diff --check`
- grep checks for the tutorial command chain, artifact paths, interpretation keywords, docs-index link, and Progress entry
- `cd materials-discovery && uv run pytest tests/test_cli.py -q` -> `18 passed`

## Next Phase Readiness

All planned v1.7 phases are complete. The milestone is ready for audit and archival.

## Self-Check: PASSED

- Found `39-01-SUMMARY.md`.
- Found the tutorial commit `0b8592f8`.
- Verified `guided-design-tutorial.md`, `index.md`, and `Progress.md` landed together.
- Verified OPS-19, OPS-20, and OPS-21 are now marked complete in `.planning/REQUIREMENTS.md`.

---
*Phase: 39-guided-design-evaluation-and-visualization-tutorial*
*Completed: 2026-04-15*
