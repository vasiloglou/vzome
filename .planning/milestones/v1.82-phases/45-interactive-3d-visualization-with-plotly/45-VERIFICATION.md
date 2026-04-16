---
phase: 45-interactive-3d-visualization-with-plotly
verified: 2026-04-15T00:00:00Z
status: human_needed
score: 3/4 success criteria verified automatically
human_verification:
  - test: "Open guided_design_tutorial.ipynb, run cells 1 through Section 4, and run the orbit scatter cell (4.1)"
    expected: "An interactive plotly 3D scatter appears with 5 orbit-colored traces in the legend, distinct colorblind-safe colors, and hover text in the format 'Zn7_01 (tsai_zn7) - Zn - Zn inner shell' when hovering a site"
    why_human: "Visual rendering of plotly figures inside Jupyter requires a live kernel and browser; renderer='notebook_connected' cannot be tested headlessly"
  - test: "In the same notebook session, run the shell figure cell (4.2)"
    expected: "A shell-decomposed Tsai cluster figure appears with 5 toggleable shell layers in the legend, semi-transparent ConvexHull polyhedral cages, visible edge wireframes, and clicking a legend entry hides/shows both the markers and the cage together"
    why_human: "Interactive legend toggling behavior and visual quality of polyhedral cages cannot be verified without a live Jupyter rendering environment"
  - test: "Confirm the existing HTML canvas viewer cell (id=4cbab4b3) still renders its output above the plotly cells"
    expected: "The HTML canvas preview of the checked geometry (from preview_checked_design()) still works and appears before the new plotly cells"
    why_human: "Fallback viewer rendering requires a live kernel execution"
---

# Phase 45: Interactive 3D Visualization with Plotly — Verification Report

**Phase Goal:** The notebook renders interactive publication-quality 3D figures showing orbit-colored atomic sites and shell-decomposed Tsai cluster layers, backed by an installable [viz] optional dependency group
**Verified:** 2026-04-15
**Status:** human_needed (all automated checks pass; 3 items require live Jupyter rendering)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (from ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Notebook produces interactive plotly 3D scatter with per-orbit colorblind-safe colors and hover labels | ? HUMAN | Notebook cells wired correctly; behavioral spot-check on orbit_figure() confirms 5 traces, 100 sites, correct colors. Live render needs human |
| 2 | Notebook produces shell-decomposed Tsai cluster figure with labeled layers and polyhedral cage wireframes | ? HUMAN | shell_figure() produces 5 Mesh3d cages + 5 wireframe Scatter3d lines + 5 marker traces; interactive toggling requires live Jupyter |
| 3 | Visualization modules are importable after pip install "materials-discovery[viz]" | VERIFIED | All imports confirmed; [viz] group in pyproject.toml contains all 5 packages; 16/16 tests pass; full suite 611 passed |
| 4 | Core pipeline never imports plotly or matplotlib — [viz] remains strictly optional | VERIFIED | grep over all src/*.py outside visualization/ shows zero direct plotly or matplotlib imports; __init__.py uses try/except guard |

**Score:** 2/4 automatically verified, 2/4 need human (interactive rendering); all automated evidence is positive

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `materials-discovery/src/materials_discovery/visualization/plotly_3d.py` | orbit_figure, shell_figure, load_orbit_library | VERIFIED | 320 lines; all three functions implemented; try/except ImportError guard at top; ConvexHull cage + wireframe; hovertemplate; legendgroup; opacity=0.15 |
| `materials-discovery/src/materials_discovery/visualization/matplotlib_pub.py` | Phase 46 placeholder stub | VERIFIED | 7 lines; docstring only; "Phase 46 placeholder" present; importable |
| `materials-discovery/src/materials_discovery/visualization/expansion.py` | Phase 46 placeholder stub | VERIFIED | 7 lines; docstring only; "Phase 46 placeholder" present; importable |
| `materials-discovery/tests/test_plotly_3d.py` | 16 unit tests | VERIFIED | 270 lines (>80 min); all 16 tests present and passing in 0.20s |
| `materials-discovery/pyproject.toml` | [viz] optional-dependencies group | VERIFIED | Lines 43-49: viz = ["plotly>=6.0", "matplotlib>=3.9", "kaleido>=1.0", "scipy>=1.13", "nbformat>=4.2.0"] |
| `materials-discovery/notebooks/guided_design_tutorial.ipynb` | 3 new cells in Section 4 (markdown + 2 code) | VERIFIED | Cells a1b2c3d4 (markdown), b2c3d4e5 (orbit code), c3d4e5f6 (shell code) inserted after 4cbab4b3; Section 5 (c2485826) still follows |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `plotly_3d.py` | `visualization/labels.py` | `from materials_discovery.visualization.labels import ORBIT_COLORS, SHELL_NAMES, DEFAULT_ORBIT_COLOR` | VERIFIED | Line 25-29 of plotly_3d.py; pattern matches |
| `visualization/__init__.py` | `plotly_3d.py` | conditional import of orbit_figure, shell_figure, load_orbit_library | VERIFIED | Lines 32-41 of __init__.py; try/except with __all__ extension |
| `tests/test_plotly_3d.py` | `data/prototypes/generated/sc_zn_tsai_bridge.json` | ORBIT_LIB_PATH fixture loads real file | VERIFIED | File exists; test fixture uses Path(__file__).resolve().parent.parent / "data/..." |
| `notebooks/guided_design_tutorial.ipynb` | `plotly_3d.py` | `from materials_discovery.visualization.plotly_3d import orbit_figure, shell_figure, load_orbit_library` | VERIFIED | Cell b2c3d4e5 contains exact import; pattern confirmed |
| `notebooks/guided_design_tutorial.ipynb` | `sc_zn_tsai_bridge.json` | `load_orbit_library(WORKDIR / "data/prototypes/generated/sc_zn_tsai_bridge.json")` | VERIFIED | Cell b2c3d4e5 contains exact path; file exists on disk |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `plotly_3d.orbit_figure()` | orbit_lib_data["orbits"] | load_orbit_library() reads sc_zn_tsai_bridge.json via json.loads(path.read_text()) | Yes — 5 orbits, 100 sites loaded from disk | FLOWING |
| `plotly_3d.shell_figure()` | orbit_lib_data["orbits"] | Same load path; sorts by _compute_mean_radius() | Yes — ConvexHull computed from real coordinates | FLOWING |
| Notebook cell B | fig_orbit | orbit_figure(orbit_lib_data) called with data loaded from real JSON | Yes — behavioral spot-check confirms 5 traces, 100 sites | FLOWING |
| Notebook cell C | fig_shell | shell_figure(orbit_lib_data) reuses data from cell B | Yes — spot-check confirms 5 Mesh3d + 5 wireframe + 5 markers | FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| load_orbit_library returns 5 orbits | `load_orbit_library(Path("data/..."))` | `Orbits: 5, ['tsai_zn7', 'tsai_sc1', 'tsai_zn6', 'tsai_zn5', 'tsai_zn4']` | PASS |
| orbit_figure() returns 5 Scatter3d traces | `len(fig.data) == 5` | `orbit_figure traces: 5` | PASS |
| orbit_figure() covers all 100 sites | `sum(len(t.x) for t in fig.data)` | `Total sites: 100` | PASS |
| shell_figure() produces Mesh3d cages and wireframes | Check Mesh3d and lines counts | `Mesh3d=5, wireframe_lines=5` | PASS |
| shell_figure() shells ordered inner-to-outer | First/last marker trace names | `First: 'Shell 1: Zn middle shell'`, `Last: 'Shell 5: Zn outer shell'` | PASS |
| 16 unit tests pass | `uv run pytest tests/test_plotly_3d.py -x -q` | `16 passed in 0.20s` | PASS |
| Full suite shows no regressions | `uv run pytest tests/ --ignore=test_llm_replay_core.py` | `611 passed, 3 skipped, 1 warning` | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| VIZ-01 | 45-01-PLAN, 45-02-PLAN | Notebook renders interactive plotly 3D scatter with per-orbit distinct colorblind-safe colors and hover labels showing site name and orbit | SATISFIED | orbit_figure() produces 5 Scatter3d traces with ORBIT_COLORS palette, hovertemplate="%{text}<extra></extra>", text format "{label} ({orbit}) - {species} - {shell_name}"; notebook cell calls orbit_figure and fig.show |
| VIZ-02 | 45-01-PLAN, 45-02-PLAN | Notebook renders shell-decomposed Tsai cluster figure with concentric polyhedral shells as separate labeled layers with cage wireframes | SATISFIED | shell_figure() sorts by mean radial distance, produces Mesh3d (opacity=0.15) + Scatter3d lines per shell, all sharing legendgroup; notebook cell calls shell_figure |
| ENRICH-03 | 45-01-PLAN | Visualization modules live inside materials_discovery.visualization and are installable via [viz] optional dependency group | SATISFIED | plotly_3d.py, matplotlib_pub.py, expansion.py, labels.py all in src/materials_discovery/visualization/; pyproject.toml has [viz] with all 5 packages; __init__.py has conditional export |

No orphaned requirements: the REQUIREMENTS.md traceability table maps VIZ-01, VIZ-02, ENRICH-03 all to Phase 45, and all three are claimed in plan frontmatter and verified above.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `visualization/matplotlib_pub.py` | 1-7 | Docstring-only stub | Info | Intentional Phase 46 placeholder, documented in PLAN and SUMMARY; not exported from __init__.py; does not affect Phase 45 goal |
| `visualization/expansion.py` | 1-7 | Docstring-only stub | Info | Intentional Phase 46 placeholder, documented in PLAN and SUMMARY; not exported from __init__.py; does not affect Phase 45 goal |

No blockers. No warnings. The two stub modules are explicitly declared as Phase 46 placeholders in the PLAN frontmatter and are verified importable.

### Human Verification Required

#### 1. Orbit-colored interactive 3D scatter in notebook

**Test:** Open `materials-discovery/notebooks/guided_design_tutorial.ipynb` in Jupyter Lab (`cd materials-discovery && uv run jupyter lab notebooks/guided_design_tutorial.ipynb`). Run cells through the Section 4 preview cell (4cbab4b3). Then run cell 4.1 (b2c3d4e5 — orbit scatter).
**Expected:** An interactive plotly 3D figure appears with 5 legend entries, each a different colorblind-safe color (blue, orange, green, vermilion, sky-blue palette). Hovering any site marker shows hover text in the format "Zn7_01 (tsai_zn7) - Zn - Zn inner shell". All 100 sites render as uniform-size markers. Figure supports rotate, zoom, and pan.
**Why human:** plotly renderer="notebook_connected" requires a live Jupyter kernel and browser to display; the CDN-loaded plotly.js cannot run headlessly.

#### 2. Shell-decomposed Tsai cluster figure in notebook

**Test:** In the same session, run cell 4.2 (c3d4e5f6 — shell figure).
**Expected:** A shell-decomposed figure appears with 5 shell entries in the legend (Shell 1: Zn middle shell through Shell 5: Zn outer shell). Each shell shows markers surrounded by a semi-transparent polyhedral cage (opacity ~15%). Edge wireframes are visible on each cage. Clicking a legend entry toggles that shell's markers AND its polyhedral cage together.
**Why human:** Interactive legend toggling and visual quality of ConvexHull polyhedral faces require a live Jupyter rendering environment.

#### 3. Existing HTML canvas viewer preserved

**Test:** In the same notebook session, confirm cell 4cbab4b3 (preview_checked_design) still renders its HTML canvas viewer output above the plotly cells.
**Expected:** The HTML preview of the checked Sc-Zn geometry still displays, unaffected by the new plotly cells that follow it.
**Why human:** Requires live kernel execution to verify the HTML output cell is not cleared or overwritten.

### Gaps Summary

No gaps found. All automated checks pass completely:
- All 5 phase artifacts exist, are substantive, and are wired
- All 5 key links verified (labels import, __init__ conditional export, test fixture data, notebook import, notebook data path)
- Data flows confirmed through Level 4 trace (real JSON file -> load_orbit_library -> orbit_figure/shell_figure -> notebook cells)
- 16/16 unit tests pass; 611/611 suite tests pass (no regressions)
- All 3 requirements (VIZ-01, VIZ-02, ENRICH-03) satisfied with implementation evidence
- Core pipeline verified free of direct plotly/matplotlib imports
- 3 human verification items remain for live Jupyter rendering quality — these are inherent to interactive notebook visualization and cannot be automated headlessly

---

_Verified: 2026-04-15_
_Verifier: Claude (gsd-verifier)_
