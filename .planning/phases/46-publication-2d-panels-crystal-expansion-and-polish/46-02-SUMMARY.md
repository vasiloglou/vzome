---
phase: 46-publication-2d-panels-crystal-expansion-and-polish
plan: "02"
subsystem: materials-discovery/visualization
tags: [plotly, crystal-expansion, supercell, visualization, tdd]
dependency_graph:
  requires:
    - "Phase 45 Plan 01: plotly_3d.py, labels.py, [viz] extra"
    - "materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json"
  provides:
    - "expansion_figure() for 2x2x2 periodic approximant tiling view"
    - "test_expansion.py with 8 passing unit tests"
  affects:
    - "materials-discovery/src/materials_discovery/visualization/expansion.py"
    - "materials-discovery/tests/test_expansion.py"
tech_stack:
  added: []
  patterns:
    - "plotly Scatter3d with per-point RGBA colors for opacity encoding"
    - "itertools.product for n^3 cell offset generation"
    - "customdata for test-accessible per-point metadata"
key_files:
  created:
    - materials-discovery/tests/test_expansion.py
  modified:
    - materials-discovery/src/materials_discovery/visualization/expansion.py
    - materials-discovery/Progress.md
decisions:
  - "Per-point opacity encoded via RGBA color strings, not marker.opacity list, because plotly Scatter3d marker.opacity is scalar-only in v6.6"
  - "Numeric opacity stored in customdata (1.0 or 0.3 per point) for test verification without RGBA string parsing"
  - "ONE trace per orbit (5 total), not 40 — all 8 cells concatenated into single trace per orbit to keep legend clean"
  - "_hex_to_rgba() helper converts ORBIT_COLORS hex palette to RGBA strings for central/surrounding opacity distinction"
metrics:
  duration: "249s"
  completed: "2026-04-16"
  tasks: 2
  files: 3
requirements: [ENRICH-02]
---

# Phase 46 Plan 02: Crystal Expansion Figure Summary

**One-liner:** `expansion_figure()` implements 2x2x2 supercell tiling of the Sc-Zn Tsai motif with 5 Scatter3d traces (800 total sites), central cell opacity=1.0 and surrounding cells opacity=0.3 encoded via RGBA color strings.

## What Was Built

`expansion_figure(orbit_lib_data, n_cells=2)` in `materials-discovery/src/materials_discovery/visualization/expansion.py` generates a plotly `go.Figure` showing how the Sc-Zn quasicrystal approximant motif tiles into a larger periodic structure.

Key behaviors:
- Generates `n_cells^3 = 8` cell offsets via `itertools.product(range(2), repeat=3)`
- Creates ONE `go.Scatter3d` trace per orbit (5 total) — all 8 cells concatenated, not 40 separate traces
- Coordinate math: `x = (fp[0] + n1) * a - mc_cart[0]` for each fractional position + cell offset
- Central cell `(0,0,0)`: RGBA alpha=1.0 (fully opaque); surrounding 7 cells: alpha=0.3 (30% opaque)
- Per-point opacity stored in `customdata` for test verification
- Uses `ORBIT_COLORS` from `labels.py` for colorblind-safe orbit palette
- Figure title: `"Sc-Zn Periodic Approximant -- 2x2x2 Expansion"`
- Import guard: `_EXPANSION_AVAILABLE` flag; `_require_expansion()` raises `ImportError` with `"materials-discovery[viz]"` install hint

8 unit tests in `test_expansion.py` cover: figure type, trace count (5), total sites (800), opacity encoding (customdata), trace names (SHELL_NAMES values), title contains "Periodic Approximant", hover text includes "central" and "cell (", and import guard raises correct error.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] plotly Scatter3d marker.opacity rejects list values**

- **Found during:** Task 1 execution — first test run
- **Issue:** `plotly 6.6.0` `scatter3d.Marker.opacity` is a scalar-only property. The plan specified building a list `[1.0, 1.0, ..., 0.3, 0.3, ...]` and passing it as `marker=dict(opacity=opacities)`. This raises `ValueError: Invalid value of type 'builtins.list' received for the 'opacity' property of scatter3d.marker`.
- **Fix:**
  - Added `_hex_to_rgba(hex_color, alpha)` helper to convert `ORBIT_COLORS` hex values to `rgba(R,G,B,A)` strings
  - Changed `marker=dict(color=colors)` where `colors` is a per-point list of RGBA strings
  - Added `customdata=opacity_data` storing the numeric opacity (1.0 or 0.3) per point for test verification
  - Updated `test_expansion_figure_central_cell_opacity` to use `trace.customdata` instead of `trace.marker.opacity`
- **Files modified:** `expansion.py`, `test_expansion.py`
- **Commits:** `531b525e` (implementation), `290972a2` (tests + fix)

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Implement expansion.py with expansion_figure | 531b525e | expansion.py |
| 2 | Write test_expansion.py and update Progress.md | 290972a2 | test_expansion.py, expansion.py (rgba fix), Progress.md |

## Verification Results

1. `uv run python -c "from materials_discovery.visualization.expansion import expansion_figure"` — OK
2. `uv run pytest tests/test_expansion.py -x -q` — 8 passed in 0.18s
3. Full suite — 400 passed (1 pre-existing failure in `test_llm_replay_core.py` unrelated to this plan)

## Known Stubs

None — expansion.py is fully implemented.

## Self-Check: PASSED

- `materials-discovery/src/materials_discovery/visualization/expansion.py` — FOUND
- `materials-discovery/tests/test_expansion.py` — FOUND
- `materials-discovery/Progress.md` — FOUND (updated)
- Commit `531b525e` — FOUND
- Commit `290972a2` — FOUND
