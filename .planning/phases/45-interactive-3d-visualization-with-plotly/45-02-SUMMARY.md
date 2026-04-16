---
phase: 45-interactive-3d-visualization-with-plotly
plan: "02"
subsystem: materials-discovery/notebooks
tags: [plotly, 3d-visualization, notebook, orbit-figure, shell-figure, viz-integration]
dependency_graph:
  requires:
    - "materials-discovery/src/materials_discovery/visualization/plotly_3d.py (Phase 45 Plan 01)"
    - "materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json"
  provides:
    - "materials-discovery/notebooks/guided_design_tutorial.ipynb (Section 4 plotly cells)"
  affects:
    - "materials-discovery/Progress.md"
tech_stack:
  added: []
  patterns:
    - "try/except ImportError guard (_PLOTLY_AVAILABLE) in notebook cell for graceful fallback"
    - "renderer=notebook_connected (avoids 3.5MB plotly.js embed per cell)"
    - "load_orbit_library -> orbit_figure -> fig.show pattern"
    - "load_orbit_library -> shell_figure -> fig.show pattern"
key_files:
  created: []
  modified:
    - "materials-discovery/notebooks/guided_design_tutorial.ipynb"
    - "materials-discovery/Progress.md"
decisions:
  - "renderer=notebook_connected used (not renderer=notebook) to avoid 3.5MB plotly.js embed per cell"
  - "Single _PLOTLY_AVAILABLE guard in cell B covers both orbit and shell cells (cell C tests the flag set in B)"
  - "orbit_lib_data loaded once in cell B and reused by cell C (avoids redundant disk read)"
metrics:
  duration: "89 seconds"
  completed: "2026-04-16"
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 2
  tests_added: 0
  tests_passing: 16
---

# Phase 45 Plan 02: Notebook Plotly 3D Integration Summary

**One-liner:** Wired orbit_figure() and shell_figure() from plotly_3d.py into guided_design_tutorial.ipynb Section 4 as three new cells with a graceful ImportError fallback, completing the user-facing VIZ-01 and VIZ-02 deliverables.

## What Was Built

### Notebook Section 4 additions (3 new cells)

All three cells are inserted immediately after the existing `preview_checked_design()` cell (id=4cbab4b3) and immediately before the Section 5 markdown cell (id=c2485826).

**Cell A (markdown, id=a1b2c3d4):** Introduction explaining that the cells render the same 100 anchor-library sites as interactive plotly figures. Includes the fallback install instruction (`uv pip install "materials-discovery[viz]"`).

**Cell B (code, id=b2c3d4e5):** VIZ-01 orbit scatter cell. Contains a `try/except ImportError` guard that sets `_PLOTLY_AVAILABLE`. When `True`, calls `load_orbit_library(WORKDIR / "data/prototypes/generated/sc_zn_tsai_bridge.json")`, then `orbit_figure(orbit_lib_data)`, then `fig_orbit.show(renderer="notebook_connected")`. When `False`, prints three helpful fallback lines.

**Cell C (code, id=c3d4e5f6):** VIZ-02 shell figure cell. Tests `_PLOTLY_AVAILABLE` (set in cell B). When `True`, calls `shell_figure(orbit_lib_data)` (reusing data loaded in cell B), then `fig_shell.show(renderer="notebook_connected")`.

### Design choices

- `renderer="notebook_connected"` avoids embedding 3.5MB of plotly.js per cell — the connected renderer loads from CDN instead.
- `_PLOTLY_AVAILABLE` is a single try/except guard in cell B; cell C tests the same flag. This avoids a second try/except and ensures both cells are in sync.
- `orbit_lib_data` is loaded once in cell B and reused in cell C. Avoids redundant disk I/O and keeps the two cells clearly sequential.
- The existing `preview_checked_design()` cell (HTML canvas viewer) is preserved untouched — the plotly cells augment rather than replace the fallback viewer.

## Deviations from Plan

None — plan executed exactly as written.

## Auth Gates

None.

## Known Stubs

None. All cells produce real figures when `[viz]` is installed. The fallback path is intentional, not a stub.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | 05667c19 | feat(45-02): insert plotly 3D figure cells into notebook Section 4 |
| Task 2 | (checkpoint auto-approved, no separate commit) | Visual verification auto-approved in autonomous mode; 16/16 tests pass |

## Self-Check: PASSED

- Notebook file modified: EXISTS (materials-discovery/notebooks/guided_design_tutorial.ipynb)
- Progress.md updated: EXISTS with 2026-04-16 changelog + diary entries
- Commit 05667c19: EXISTS
- Automated verify script: ALL CHECKS PASSED
- Test suite: 16 passed, 0 failed
- Cell 4cbab4b3 (preview_checked_design) still present: CONFIRMED
- 3 new cells after preview cell (markdown + 2 code): CONFIRMED
- Section 5 (c2485826) still in position after new cells: CONFIRMED
- orbit_figure and notebook_connected in cell B: CONFIRMED
- shell_figure and notebook_connected in cell C: CONFIRMED
- _PLOTLY_AVAILABLE fallback message in cell B: CONFIRMED
