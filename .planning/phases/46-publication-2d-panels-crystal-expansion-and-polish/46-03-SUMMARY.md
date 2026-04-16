---
phase: 46-publication-2d-panels-crystal-expansion-and-polish
plan: "03"
subsystem: materials-discovery/visualization
tags: [matplotlib, plotly, notebook, exports, integration, viz]
dependency_graph:
  requires:
    - "Phase 46 Plan 01: matplotlib_pub.py (screening_scatter, rdf_plot, diffraction_plot)"
    - "Phase 46 Plan 02: expansion.py (expansion_figure)"
    - "Phase 45 Plan 01: plotly_3d.py, _PLOTLY_AVAILABLE guard in notebook"
  provides:
    - "materials_discovery.visualization exports screening_scatter, rdf_plot, diffraction_plot, expansion_figure"
    - "Notebook Section 4.3: Crystal Expansion View (ENRICH-02)"
    - "Notebook Section 5.1: Screening Scatter (VIZ-03)"
    - "Notebook Section 5.2: Pairwise Distance Distribution / RDF (VIZ-04)"
    - "Notebook Section 5.3: Simulated Powder XRD (VIZ-05)"
  affects:
    - "materials-discovery/src/materials_discovery/visualization/__init__.py"
    - "materials-discovery/notebooks/guided_design_tutorial.ipynb"
tech_stack:
  added: []
  patterns:
    - "try/except conditional import blocks following existing plotly_3d pattern"
    - "Notebook cell insertion via Python JSON manipulation"
    - "_PLOTLY_AVAILABLE guard reused from Section 4.1 cell for expansion_figure"
    - "try/except ImportError in notebook cells for matplotlib functions"
key_files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/visualization/__init__.py
    - materials-discovery/notebooks/guided_design_tutorial.ipynb
    - materials-discovery/Progress.md
decisions:
  - "Followed existing plotly_3d try/except pattern exactly for matplotlib_pub and expansion exports — keeps __init__.py consistent and easy to extend"
  - "Expansion cell reuses _PLOTLY_AVAILABLE guard (set by cell b2c3d4e5 VIZ-01) rather than introducing a new guard variable"
  - "Screening/RDF/diffraction cells use separate try/except ImportError per cell for maximum independence and graceful fallback"
metrics:
  duration: "~5 minutes"
  completed: "2026-04-16T14:34:16Z"
  tasks_completed: 2
  tasks_total: 2
  files_created: 0
  files_modified: 3
requirements_satisfied: [VIZ-03, VIZ-04, VIZ-05, ENRICH-02]
---

# Phase 46 Plan 03: __init__.py Exports and Notebook Figure Cells Summary

**One-liner:** Wired screening_scatter, rdf_plot, diffraction_plot, and expansion_figure into visualization/__init__.py via try/except conditional imports, and inserted 5 new notebook cells (1 markdown + 4 code) for Sections 4.3 and 5.1-5.3 of the guided design tutorial.

## What Was Built

### __init__.py (updated)

Two new try/except conditional import blocks added after the existing plotly_3d block:

```python
# Conditionally export matplotlib_pub functions when [viz] extra is installed.
try:
    from materials_discovery.visualization.matplotlib_pub import (
        screening_scatter, rdf_plot, diffraction_plot,
    )
except ImportError:
    pass
else:
    __all__ += ["screening_scatter", "rdf_plot", "diffraction_plot"]

# Conditionally export expansion functions when [viz] extra is installed.
try:
    from materials_discovery.visualization.expansion import (
        expansion_figure,
    )
except ImportError:
    pass
else:
    __all__ += ["expansion_figure"]
```

All 4 functions are now importable from `materials_discovery.visualization` when the `[viz]` extra is installed.

### guided_design_tutorial.ipynb (5 new cells)

**Cell insertions after Section 4.2 shell figure (cell c3d4e5f6):**

| Cell | Type | Content |
|------|------|---------|
| Markdown | markdown | "### Crystal Expansion View" — explains 2x2x2 supercell tiling concept |
| Code (4.3) | code | Calls `expansion_figure(orbit_lib_data)` with `_PLOTLY_AVAILABLE` guard and `renderer="notebook_connected"` |

**Cell insertions after "What the screening numbers mean" (cell a3f1c8e2):**

| Cell | Type | Content |
|------|------|---------|
| Code (5.1) | code | Calls `screening_scatter(screened_path=..., calibration_path=...)` with try/except ImportError |
| Code (5.2) | code | Calls `rdf_plot(orbit_lib_path=...)` with try/except ImportError |
| Code (5.3) | code | Loads top candidate from JSONL, calls `simulate_powder_xrd_patterns`, then `diffraction_plot(peaks=...)` |

Final cell order in Sections 4-6:
```
Cell 14 [a1b2c3d4] — ### Interactive 3D Orbit Visualization (markdown)
Cell 15 [b2c3d4e5] — 4.1 orbit scatter (VIZ-01, sets _PLOTLY_AVAILABLE)
Cell 16 [c3d4e5f6] — 4.2 shell figure (VIZ-02)
Cell 17 [new md]  — ### Crystal Expansion View
Cell 18 [new code] — 4.3 expansion figure (ENRICH-02)
Cell 19 [c2485826] — ## 5. Generate and Screen Candidates
Cell 20 [b1aada31] — generate + screen commands
Cell 21 [a3f1c8e2] — ### What the screening numbers mean
Cell 22 [new code] — 5.1 screening scatter (VIZ-03)
Cell 23 [new code] — 5.2 RDF plot (VIZ-04)
Cell 24 [new code] — 5.3 diffraction plot (VIZ-05)
Cell 25 [12026ea1] — ## 6. High-Fidelity Validation
```

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Update __init__.py exports and insert notebook figure cells | 1389c9d5 | __init__.py, guided_design_tutorial.ipynb, Progress.md |
| 2 | Visual verification checkpoint (auto-approved, autonomous mode) | — | — |

## Verification Results

1. `uv run python -c "from materials_discovery.visualization import screening_scatter, rdf_plot, diffraction_plot, expansion_figure"` — OK
2. `uv run pytest tests/test_matplotlib_pub.py tests/test_expansion.py -x -q` — 18 passed in 0.33s
3. All 5 notebook acceptance criteria pass (grep + json checks)

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. All four functions (screening_scatter, rdf_plot, diffraction_plot, expansion_figure) are fully implemented and call real data files. The notebook cells use real file paths and produce live figures.

## Self-Check

### Files exist:

- [x] `materials-discovery/src/materials_discovery/visualization/__init__.py` — 63 lines, contains all 4 conditional exports
- [x] `materials-discovery/notebooks/guided_design_tutorial.ipynb` — 45 cells (was 40), contains all 5 new cells
- [x] `materials-discovery/Progress.md` — updated with changelog row and diary entry

### Commits exist:

- 1389c9d5 feat(46-03): wire matplotlib_pub and expansion into __init__.py; insert 5 notebook figure cells

## Self-Check: PASSED
