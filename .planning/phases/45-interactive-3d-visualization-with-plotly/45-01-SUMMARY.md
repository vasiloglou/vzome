---
phase: 45-interactive-3d-visualization-with-plotly
plan: "01"
subsystem: materials-discovery/visualization
tags: [plotly, 3d-visualization, orbit-figure, shell-figure, scipy, convexhull, viz-deps]
dependency_graph:
  requires:
    - "materials-discovery/src/materials_discovery/visualization/labels.py (Phase 44)"
    - "materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json"
  provides:
    - "materials-discovery/src/materials_discovery/visualization/plotly_3d.py"
    - "materials-discovery/src/materials_discovery/visualization/matplotlib_pub.py"
    - "materials-discovery/src/materials_discovery/visualization/expansion.py"
    - "materials-discovery/tests/test_plotly_3d.py"
    - "[viz] optional-dependencies group in pyproject.toml"
  affects:
    - "materials-discovery/src/materials_discovery/visualization/__init__.py"
    - "materials-discovery/pyproject.toml"
tech_stack:
  added:
    - "plotly>=6.0 (Scatter3d, Mesh3d interactive figures)"
    - "scipy>=1.13 (ConvexHull for polyhedral shell cages)"
    - "kaleido>=1.0 (static export — deferred to future)"
    - "nbformat>=4.2.0 (plotly Jupyter mime-type rendering)"
    - "matplotlib>=3.9 (matplotlib_pub.py Phase 46 stub)"
  patterns:
    - "try/except ImportError guard at module top for optional viz dependencies"
    - "ConvexHull.simplices -> Mesh3d + edge wireframe Scatter3d pattern"
    - "legendgroup for per-shell marker+cage+wireframe toggling"
    - "Mean radial distance shell ordering with orbit name as tiebreaker"
key_files:
  created:
    - "materials-discovery/src/materials_discovery/visualization/plotly_3d.py"
    - "materials-discovery/src/materials_discovery/visualization/matplotlib_pub.py"
    - "materials-discovery/src/materials_discovery/visualization/expansion.py"
    - "materials-discovery/tests/test_plotly_3d.py"
  modified:
    - "materials-discovery/src/materials_discovery/visualization/__init__.py"
    - "materials-discovery/pyproject.toml"
    - "materials-discovery/Progress.md"
decisions:
  - "Shell ordering computed dynamically from mean radial distance; orbit name as tiebreaker for sort stability"
  - "matplotlib_pub.py and expansion.py stubs intentionally NOT exported from __init__.py until Phase 46 populates them"
  - "plotly_3d functions exported conditionally from __init__.py via try/except so base package remains importable when [viz] not installed"
  - "orbit_figure and shell_figure accept orbit_lib_data dict directly (loaded by load_orbit_library) rather than RawExportViewModel — avoids design-orbit vs anchor-orbit namespace mismatch"
metrics:
  duration: "3 minutes"
  completed: "2026-04-16"
  tasks_completed: 2
  tasks_total: 2
  files_created: 4
  files_modified: 3
  tests_added: 16
  tests_passing: 16
  full_suite_result: "611 passed, 3 skipped, 1 warning"
---

# Phase 45 Plan 01: Plotly 3D Visualization Module Summary

**One-liner:** Interactive 3D Tsai cluster visualization with orbit-colored Scatter3d and shell-decomposed ConvexHull cage figures using plotly 6.0, scipy ConvexHull, and a [viz] optional-dependencies group.

## What Was Built

### plotly_3d.py (primary deliverable)

Three public functions implementing VIZ-01, VIZ-02, and the ENRICH-03 import contract:

- `load_orbit_library(path: Path) -> dict` — loads the orbit-library JSON from disk with FileNotFoundError on missing file.
- `orbit_figure(orbit_lib_data: dict) -> go.Figure` — returns a figure with exactly 5 `go.Scatter3d` traces (one per anchor orbit), colorblind-safe palette from `labels.ORBIT_COLORS`, uniform marker size=8, and hover text in `"{label} ({orbit}) - {species} - {shell_name}"` format. 100 total sites across 5 orbits.
- `shell_figure(orbit_lib_data: dict) -> go.Figure` — returns a figure with shells sorted ascending by mean radial distance from motif center. Each shell has a markers trace, a `go.Mesh3d` ConvexHull cage at opacity=0.15, and a `go.Scatter3d` edge wireframe — all sharing a `legendgroup` for interactive toggling. Shell order: tsai_zn6 (5.97A) < tsai_zn7 (6.13A) < tsai_zn5 (6.57A) < tsai_sc1 (6.73A) < tsai_zn4 (7.73A).

Module-top try/except ImportError guard sets `_VIZ_AVAILABLE` and `_VIZ_IMPORT_ERROR` at import time; `_require_viz()` raises with clear `"uv pip install 'materials-discovery[viz]'"` instructions when plotly/scipy are absent.

### matplotlib_pub.py and expansion.py

Phase 46 placeholder stubs — docstring only, no functions, not exported from `__init__.py`.

### pyproject.toml [viz] group

New optional-dependencies group:
```toml
viz = [
  "plotly>=6.0",
  "matplotlib>=3.9",
  "kaleido>=1.0",
  "scipy>=1.13",
  "nbformat>=4.2.0",
]
```

### __init__.py conditional export

Added try/except block that conditionally exports `orbit_figure`, `shell_figure`, `load_orbit_library` into `__all__` when plotly is installed; silently passes when it is not.

### test_plotly_3d.py (16 unit tests)

All acceptance criteria covered:
- `test_orbit_figure_has_five_traces` — 5 Scatter3d traces
- `test_orbit_figure_trace_colors` — ORBIT_COLORS values match trace colors
- `test_orbit_figure_hover_text` — format check + tsai_zn7 + "Zn inner shell" presence
- `test_orbit_figure_marker_size` — marker.size == 8
- `test_orbit_figure_total_points` — sum == 100
- `test_shell_figure_shell_ordering` — first="Zn middle shell", last="Zn outer shell"
- `test_shell_figure_has_mesh3d_traces` — >= 5 Mesh3d traces
- `test_shell_figure_legendgroup` — each legendgroup has Scatter3d markers + Mesh3d cage
- `test_shell_figure_mesh3d_opacity` — opacity == 0.15
- `test_shell_figure_edge_wireframe` — Scatter3d lines traces exist
- `test_import_error_message` — monkeypatch _VIZ_AVAILABLE=False -> ImportError matches "materials-discovery[viz]"
- `test_matplotlib_pub_importable` — import succeeds
- `test_expansion_importable` — import succeeds
- `test_viz_extra_declared` — tomllib parse confirms all 5 packages in [viz]
- `test_load_orbit_library` — real file -> dict with base_cell, motif_center, orbits (5 entries)
- `test_load_orbit_library_missing_file` — FileNotFoundError for nonexistent path

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

- `materials-discovery/src/materials_discovery/visualization/matplotlib_pub.py` — intentional Phase 46 placeholder, docstring only, no functions. Plan 01 explicitly calls this out as a stub.
- `materials-discovery/src/materials_discovery/visualization/expansion.py` — intentional Phase 46 placeholder, docstring only, no functions. Plan 01 explicitly calls this out as a stub.

Both stubs are importable as Python modules. Neither is exported from `__init__.py`. Both will be populated in Phase 46.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | ff6dd95c | feat(45-01): create plotly_3d.py, matplotlib_pub.py stub, expansion.py stub; add [viz] deps |
| Task 2 | a0dd4669 | test(45-01): add test_plotly_3d.py with 16 unit tests covering VIZ-01, VIZ-02, ENRICH-03 |

## Self-Check: PASSED

- plotly_3d.py: EXISTS
- matplotlib_pub.py: EXISTS
- expansion.py: EXISTS
- test_plotly_3d.py: EXISTS
- [viz] group in pyproject.toml: EXISTS (verified by test_viz_extra_declared)
- Commit ff6dd95c: EXISTS
- Commit a0dd4669: EXISTS
- All 16 tests: PASS
- Full suite: 611 passed, 3 skipped, 1 warning
