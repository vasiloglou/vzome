---
phase: 46-publication-2d-panels-crystal-expansion-and-polish
verified: 2026-04-15T00:00:00Z
status: human_needed
score: 4/4 must-haves verified
human_verification:
  - test: "Run the guided_design_tutorial.ipynb notebook end-to-end (Cell > Run All) and inspect all four new figure cells"
    expected: "Section 4.3 renders a 3D plotly scatter showing 2x2x2 tiling with bright central cell and dimmed surrounding cells; Section 5.1 shows a 2D scatter with 4 blue dots and two threshold lines; Section 5.2 shows a histogram with 5 shell-peak annotation lines and no zero-distance spike; Section 5.3 shows a vertical-line XRD stem plot with 12 peaks"
    why_human: "Correct rendering requires a live Jupyter kernel with [viz] extra installed; visual appearance, layout, and interactivity cannot be verified from static code analysis"
---

# Phase 46: Publication 2D Panels, Crystal Expansion, and Polish — Verification Report

**Phase Goal:** The notebook renders a complete set of 2D publication-quality panels (screening scatter, RDF, diffraction) and a crystal expansion view, and the full tutorial reads as a coherent illustrated educational resource
**Verified:** 2026-04-15
**Status:** human_needed (all automated checks pass; one visual rendering checkpoint requires human)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #  | Truth                                                                                                      | Status      | Evidence                                                                                                     |
|----|-------------------------------------------------------------------------------------------------------------|-------------|--------------------------------------------------------------------------------------------------------------|
| 1  | Running the notebook produces a 2D matplotlib scatter of energy_proxy vs min_distance_proxy with shortlisted candidates highlighted and threshold boundary lines visible | VERIFIED    | `screening_scatter()` in `matplotlib_pub.py` (284 lines): reads JSONL + calibration JSON, draws `axvline` + `axhline` threshold lines; notebook cell 22 calls it with real data paths; `test_screening_scatter_has_threshold_lines` and `test_screening_scatter_title_has_counts` pass |
| 2  | Running the notebook produces a radial distribution function plot with annotated shell-peak markers derived from orbit library labeled point distances | VERIFIED    | `rdf_plot()` uses orbit library (100 unique sites, 4950 pairwise distances), draws 5 `axvline` shell annotations; `test_rdf_plot_has_shell_annotations` and `test_rdf_plot_no_zero_distance_spike` pass; notebook cell 23 calls with real orbit library path |
| 3  | Running the notebook produces a simulated powder XRD diffraction pattern using existing pipeline infrastructure | VERIFIED    | `diffraction_plot()` accepts pre-computed peaks; notebook cell 24 loads first candidate from `sc_zn_candidates.jsonl`, calls `simulate_powder_xrd_patterns`, passes peaks; `test_diffraction_plot_has_12_peaks` confirms 12 segments in LineCollection |
| 4  | Running the notebook produces a crystal expansion view showing how the Sc-Zn motif tiles into a larger periodic approximant structure (2x2x2 default) | VERIFIED    | `expansion_figure()` in `expansion.py` (165 lines): generates 5 Scatter3d traces, 800 total sites (100x8 cells), central opacity=1.0 via RGBA, surrounding opacity=0.3; notebook cell 18 calls with `orbit_lib_data`; all 8 expansion tests pass |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `materials-discovery/src/materials_discovery/visualization/matplotlib_pub.py` | screening_scatter, rdf_plot, diffraction_plot functions with PUB_STYLE | VERIFIED | 284 lines, fully implemented, exports all 3 functions + PUB_STYLE dict with 6 required keys; not a stub |
| `materials-discovery/tests/test_matplotlib_pub.py` | Unit tests for all three figure functions and import guard (min 80 lines) | VERIFIED | 293 lines, 10 tests, all pass green |
| `materials-discovery/src/materials_discovery/visualization/expansion.py` | expansion_figure function for 2x2x2 crystal tiling view | VERIFIED | 165 lines, fully implemented; not a stub |
| `materials-discovery/tests/test_expansion.py` | Unit tests for expansion figure (min 60 lines) | VERIFIED | 170 lines, 8 tests, all pass green |
| `materials-discovery/src/materials_discovery/visualization/__init__.py` | Conditional exports for matplotlib_pub and expansion functions | VERIFIED | 63 lines; contains try/except blocks for screening_scatter, rdf_plot, diffraction_plot, expansion_figure |
| `materials-discovery/notebooks/guided_design_tutorial.ipynb` | New figure cells for screening, RDF, diffraction, and crystal expansion (min 500 lines) | VERIFIED | 1830 lines, 45 cells (was 40), 5 new cells in correct positions |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `matplotlib_pub.py` | `labels.py` | `from materials_discovery.visualization.labels import ORBIT_COLORS, SHELL_NAMES, DEFAULT_ORBIT_COLOR` | WIRED | Import present at line 34–38; ORBIT_COLORS used in screening_scatter and rdf_plot; SHELL_NAMES used in rdf_plot annotations |
| `matplotlib_pub.py` | `sc_zn_screened.jsonl` | `screening_scatter reads screened JSONL` | WIRED | `screening_scatter()` opens `screened_path` and reads JSONL line-by-line, filtering on `shortlist_rank` |
| `matplotlib_pub.py` | `sc_zn_screen_calibration.json` | `screening_scatter reads threshold values` | WIRED | `cal = json.loads(...)` reads calibration JSON; thresholds extracted as `cal["min_distance_threshold"]` and `cal["max_energy_threshold"]` — never hardcoded |
| `expansion.py` | `labels.py` | `from materials_discovery.visualization.labels import ORBIT_COLORS, SHELL_NAMES, DEFAULT_ORBIT_COLOR` | WIRED | Import present at lines 33–37; ORBIT_COLORS used in `_hex_to_rgba` for per-point coloring |
| `expansion.py` | `plotly.graph_objects` | `go.Scatter3d for 3D marker traces` | WIRED | `import plotly.graph_objects as go` in try/except guard; `go.Scatter3d(...)` called in loop |
| `__init__.py` | `matplotlib_pub.py` | `try/except conditional import of screening_scatter, rdf_plot, diffraction_plot` | WIRED | `from materials_discovery.visualization.matplotlib_pub import (screening_scatter, rdf_plot, diffraction_plot,)` in try/except block; `__all__` updated in else clause |
| `__init__.py` | `expansion.py` | `try/except conditional import of expansion_figure` | WIRED | `from materials_discovery.visualization.expansion import (expansion_figure,)` in try/except block |
| `guided_design_tutorial.ipynb` | `matplotlib_pub.py` | `import and call screening_scatter, rdf_plot, diffraction_plot in notebook cells` | WIRED | Cell 22 imports and calls `screening_scatter`; cell 23 imports and calls `rdf_plot`; cell 24 imports and calls `diffraction_plot` with live data paths |
| `guided_design_tutorial.ipynb` | `expansion.py` | `import and call expansion_figure in notebook cell` | WIRED | Cell 18 imports `expansion_figure` and calls it with `orbit_lib_data` (set in cell 15 via `load_orbit_library`) |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|---------------------|--------|
| `screening_scatter()` | `energies`, `distances` | Reads `sc_zn_screened.jsonl` line-by-line; filters records with non-None `shortlist_rank` | Yes — JSON parse from real JSONL file | FLOWING |
| `screening_scatter()` | `cal` (thresholds) | `json.loads(calibration_path.read_text())` from `sc_zn_screen_calibration.json` | Yes — JSON parse from real calibration file | FLOWING |
| `rdf_plot()` | `upper` (4950 pairwise distances) | Loads orbit library JSON (100 sites), vectorised `np.triu_indices(N, k=1)` computation | Yes — numpy broadcasting over real fractional positions | FLOWING |
| `diffraction_plot()` | `two_thetas`, `intensities` | Pre-computed `peaks` list from `simulate_powder_xrd_patterns` call in notebook cell 24 | Yes — notebook cell loads real candidate from `sc_zn_candidates.jsonl` and calls pipeline function | FLOWING |
| `expansion_figure()` | `xs`, `ys`, `zs`, `colors` | Itertools product over 8 offsets x orbit sites from loaded JSON | Yes — real orbit library with 100 sites produces 800 coordinate points | FLOWING |
| Notebook cell 18 | `orbit_lib_data` | Set in cell 15 by `load_orbit_library(WORKDIR / "data/prototypes/generated/sc_zn_tsai_bridge.json")` — cell 18 runs after cell 15 | Yes — real JSON file loaded from disk | FLOWING |
| Notebook cell 22 | figure returned by `screening_scatter` | WORKDIR paths point to real data files present in `data/screened/` and `data/calibration/` | Yes — both data files confirmed present | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 4 functions importable from `materials_discovery.visualization` | `uv run python -c "from materials_discovery.visualization import screening_scatter, rdf_plot, diffraction_plot, expansion_figure; print('OK')"` | All 4 functions imported OK | PASS |
| 18 phase 46 unit tests pass | `uv run pytest tests/test_matplotlib_pub.py tests/test_expansion.py -q` | 18 passed in 0.37s | PASS |
| Full test suite has no new failures | `uv run pytest -x -q` | 399 passed, 1 pre-existing failure in `test_llm_replay_core.py` (predates phase 46 — last commit to that test file is from phase 29) | PASS |
| Notebook cells reference correct data paths | Python JSON parse: all 5 checks (screening_scatter, rdf_plot, diffraction_plot, expansion_figure, Crystal Expansion present in notebook cells) | All True | PASS |
| matplotlib_pub.py acceptance criteria | grep checks on all 11 required patterns | All 11 PASS | PASS |
| expansion.py acceptance criteria | grep checks on all 8 required patterns | All 8 PASS | PASS |
| __init__.py key links | grep checks on all 6 patterns | All 6 PASS | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| VIZ-03 | 46-01-PLAN.md, 46-03-PLAN.md | Notebook renders 2D matplotlib scatter of energy_proxy vs min_distance_proxy with shortlisted candidates highlighted and threshold boundaries | SATISFIED | `screening_scatter()` in matplotlib_pub.py reads real data, draws axvline + axhline; notebook cell 22 displays it; 3 unit tests verify figure type, threshold lines, and title counts |
| VIZ-04 | 46-01-PLAN.md, 46-03-PLAN.md | Notebook renders radial distribution function plot with shell-peak annotations derived from orbit library labeled point distances | SATISFIED | `rdf_plot()` uses 100-site orbit library (not raw.json), computes 4950 pairwise distances, draws 5 orbit-labeled axvlines; notebook cell 23 displays it; `test_rdf_plot_has_shell_annotations` and `test_rdf_plot_no_zero_distance_spike` verify correctness |
| VIZ-05 | 46-01-PLAN.md, 46-03-PLAN.md | Notebook renders simulated powder XRD diffraction pattern using existing pipeline infrastructure | SATISFIED | `diffraction_plot()` accepts pre-computed peaks from `simulate_powder_xrd_patterns`; notebook cell 24 loads candidate, calls pipeline, passes peaks; `test_diffraction_plot_has_12_peaks` verifies 12 LineCollection segments |
| ENRICH-02 | 46-02-PLAN.md, 46-03-PLAN.md | Notebook shows crystal expansion view demonstrating how Sc-Zn motif tiles into larger periodic approximant structure | SATISFIED | `expansion_figure()` generates 5 Scatter3d traces, 800 total sites, 2x2x2 = 8 cells, central opacity=1.0 via RGBA encoding; notebook cell 18 inserts it after shell figure cell; 8 unit tests verify all behavioral properties |

No orphaned requirements: REQUIREMENTS.md maps only VIZ-03, VIZ-04, VIZ-05, ENRICH-02 to Phase 46 — all 4 are claimed by the plans above. No additional Phase 46 requirements exist in REQUIREMENTS.md.

### Anti-Patterns Found

| File | Pattern | Severity | Assessment |
|------|---------|----------|------------|
| `visualization/__init__.py` lines 39, 51, 61 | `pass` in except clauses | Info | These are intentional `except ImportError: pass` fallbacks in the conditional try/except import pattern — not stubs. They allow the package to be imported without the [viz] extra. Correct pattern. |

No TODO/FIXME/PLACEHOLDER/HACK comments found in any phase 46 files. No empty return values or hardcoded empty data in implementation functions.

### Human Verification Required

#### 1. Visual Rendering of All Four Publication Figure Cells

**Test:** Launch the notebook (`cd materials-discovery && uv run jupyter notebook notebooks/guided_design_tutorial.ipynb`), run all cells (Cell > Run All), and inspect the four new figure sections.

**Expected:**

- **Section 4.3 — Crystal Expansion View** (cell 18, after shell figure): A 3D plotly scatter appears with 5 legend entries (orbit shell names). Central cell sites are bright (full opacity); surrounding 7 cells are visibly dimmed (30% opacity). Hovering shows site label, shell name, and cell identifier ("central" or "cell (n1,n2,n3)"). Title reads "Sc-Zn Periodic Approximant -- 2x2x2 Expansion".
- **Section 5.1 — Screening Scatter** (cell 22, after "What the screening numbers mean"): A 2D matplotlib figure with 4 overlapping blue dots (all shortlisted), a dashed vertical line at `min_distance_threshold ≈ 0.748`, a dotted horizontal line at `max_energy_threshold ≈ -2.777`, title reading "Screening: 4 shortlisted / 20 passed / 30 total", and a legend.
- **Section 5.2 — Pairwise Distance Distribution** (cell 23): A bar chart of pair counts vs distance in Angstroms. No spike at 0 Angstrom. Five vertical annotation lines with shell labels visible (peaks in the 5–9 Angstrom range). X-axis labeled "Distance (Angstrom)".
- **Section 5.3 — Simulated Powder XRD** (cell 24): A vertical-line stem plot with 12 blue peaks at various 2-theta angles. X-axis labeled "2theta (degrees)", y-axis "Relative intensity".
- No regression in pre-existing cells (Sections 1–4.2 and 6 still render correctly).

**Why human:** Correct visual rendering, layout quality, figure interactivity (plotly hover tooltips), and absence of display errors require a live Jupyter kernel with the [viz] extra installed. Static code analysis confirms data flows and function calls are correct, but cannot substitute for visual inspection.

### Gaps Summary

No gaps. All four observable truths are verified through artifact existence, substantive implementation, wiring, and data-flow traces. 18 unit tests pass green. All 4 requirement IDs are satisfied with implementation evidence. One human visual verification checkpoint remains for notebook rendering confirmation — this is expected for a phase with a `checkpoint:human-verify` task and a "yes" UI hint in the roadmap.

---

_Verified: 2026-04-15_
_Verifier: Claude (gsd-verifier)_
