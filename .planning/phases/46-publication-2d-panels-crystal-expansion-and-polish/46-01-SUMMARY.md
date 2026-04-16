---
phase: 46-publication-2d-panels-crystal-expansion-and-polish
plan: "01"
subsystem: materials-discovery/visualization
tags: [matplotlib, publication-figures, rdf, diffraction, screening, viz]
dependency_graph:
  requires:
    - Phase 45 plotly_3d.py (labels.py import pattern established)
    - materials-discovery/src/materials_discovery/visualization/labels.py (ORBIT_COLORS, SHELL_NAMES)
    - materials-discovery/data/screened/sc_zn_screened.jsonl
    - materials-discovery/data/calibration/sc_zn_screen_calibration.json
    - materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json
  provides:
    - PUB_STYLE dict (6 keys for publication-quality matplotlib style)
    - screening_scatter() returning Figure with threshold lines (VIZ-03)
    - rdf_plot() returning Figure with 5 shell-peak annotations (VIZ-04)
    - diffraction_plot() returning Figure with 12 XRD vlines (VIZ-05)
    - test_matplotlib_pub.py with 10 unit tests
  affects:
    - Phase 46 Plan 03 (notebook integration will import these functions)
tech_stack:
  added:
    - matplotlib (via [viz] extra, already declared in Phase 45)
    - numpy (via [viz] extra, already declared in Phase 45)
  patterns:
    - plt.rc_context(PUB_STYLE) context manager for style isolation
    - numpy vectorised pairwise distance matrix (upper triangle via triu_indices)
    - try/except ImportError guard at module top (mirrors plotly_3d.py)
key_files:
  created:
    - materials-discovery/tests/test_matplotlib_pub.py (293 lines, 10 tests)
  modified:
    - materials-discovery/src/materials_discovery/visualization/matplotlib_pub.py (284 lines, was 7-line stub)
    - materials-discovery/Progress.md (changelog row + diary entries)
decisions:
  - "rdf_plot uses orbit library (100 unique sites) not raw.json (52 points with duplicates) to avoid zero-distance pairs that would spike the first histogram bin"
  - "diffraction_plot accepts pre-computed peaks list, not CandidateRecord directly, so caller controls simulate_powder_xrd_patterns invocation"
  - "plt.rc_context(PUB_STYLE) used per-function rather than a global rcParams mutation to ensure each function is self-contained and testable in isolation"
  - "axvline/axhline used for threshold boundaries in screening_scatter (not axvspan) — consistent with plan spec and testable via get_lines()"
metrics:
  duration: "~10 minutes"
  completed: "2026-04-16T14:29:24Z"
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 2
requirements_satisfied: [VIZ-03, VIZ-04, VIZ-05]
---

# Phase 46 Plan 01: matplotlib_pub.py 2D Publication Figures Summary

**One-liner:** Full matplotlib_pub.py replacing the Phase 45 stub — PUB_STYLE dict, three figure functions (screening_scatter, rdf_plot, diffraction_plot) with vectorised RDF computation and import guard, backed by 10 passing unit tests.

## What Was Built

### matplotlib_pub.py (284 lines)

The Phase 45 placeholder (7 lines, no-op) was replaced with a fully functional implementation:

**Import guard:** `_PUB_AVAILABLE` / `_PUB_IMPORT_ERROR` set at module top in a `try/except ImportError` block. `_require_pub()` raises `ImportError` with `"materials-discovery[viz]"` install hint.

**PUB_STYLE dict:**
```python
{"font.family": "sans-serif", "figure.dpi": 300, "savefig.dpi": 300,
 "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False}
```

**screening_scatter (VIZ-03):** Reads `sc_zn_screened.jsonl` (only shortlisted records), reads `sc_zn_screen_calibration.json` for thresholds, scatters candidates using `ORBIT_COLORS["tsai_zn4"]`, draws `axvline` (min_distance_threshold, dashed) and `axhline` (max_energy_threshold, dotted). Title includes shortlisted/passed/total counts from calibration JSON. Returns Figure.

**rdf_plot (VIZ-04):** Loads 100-site orbit library (NOT raw.json), converts fractional positions to centered Cartesian, computes 4950 pairwise distances via numpy broadcasting (`diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]`), histograms at 0.1 A bins, annotates 5 shell-peak axvlines from mean-radius per orbit using SHELL_NAMES colors. Returns Figure.

**diffraction_plot (VIZ-05):** Accepts pre-computed `peaks` list (each with `"two_theta"` and `"intensity"` keys), renders as `ax.vlines` stem plot. Returns Figure.

All functions use `plt.rc_context(PUB_STYLE)` and return Figure without calling `plt.show()`.

### test_matplotlib_pub.py (293 lines, 10 tests)

Following the `test_plotly_3d.py` pattern with real data fixtures:

| Test | What it verifies |
|------|-----------------|
| `test_pub_style_keys` | PUB_STYLE has all 6 required keys |
| `test_screening_scatter_returns_figure` | Returns matplotlib.figure.Figure |
| `test_screening_scatter_has_threshold_lines` | axes has 2+ Line2D with dashed/dotted linestyles |
| `test_screening_scatter_title_has_counts` | Title contains "4", "20", "30" |
| `test_rdf_plot_returns_figure` | Returns matplotlib.figure.Figure |
| `test_rdf_plot_has_shell_annotations` | axes has exactly 5 constant-xdata vlines |
| `test_rdf_plot_no_zero_distance_spike` | 0-1 Angstrom bins have zero count (orbit library, not raw.json) |
| `test_diffraction_plot_returns_figure` | Returns matplotlib.figure.Figure |
| `test_diffraction_plot_has_12_peaks` | LineCollection has exactly 12 segments |
| `test_import_guard` | Monkeypatched _PUB_AVAILABLE=False raises ImportError matching r"materials-discovery\[viz\]" |

All 10 tests pass in 0.28-0.30s. Full suite: 399 passed (1 pre-existing unrelated failure in test_llm_replay_core.py for checkpoint lifecycle).

## Deviations from Plan

None — plan executed exactly as written.

The ANTI-PATTERNS listed in the plan were all observed:
- rdf_plot uses orbit library (100 unique sites), not raw.json
- Threshold values always read from calibration JSON, never hardcoded
- No `plt.show()` inside any library function — returns Figure
- Import guard present at module top

## Known Stubs

None. All three functions are fully implemented and return live matplotlib Figure objects with real data wired.

## Self-Check

### Files exist:

- [x] `materials-discovery/src/materials_discovery/visualization/matplotlib_pub.py` — 284 lines, full implementation
- [x] `materials-discovery/tests/test_matplotlib_pub.py` — 293 lines, 10 tests
- [x] `materials-discovery/Progress.md` — updated with changelog row and diary entries

### Commits exist:

- 16d840c7 feat(46-01): implement matplotlib_pub.py with screening_scatter, rdf_plot, diffraction_plot
- 2aa6ac59 feat(46-01): add test_matplotlib_pub.py with 10 unit tests and update Progress.md

## Self-Check: PASSED
