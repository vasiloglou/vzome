# Phase 46: Publication 2D Panels, Crystal Expansion, and Polish - Research

**Researched:** 2026-04-15
**Domain:** matplotlib 2D publication figures, crystal expansion tiling, plotly 3D expansion figure
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Shared style dict in matplotlib_pub.py: sans-serif font, 300 DPI, removed top/right spines, pdf.fonttype=42
- Default figure size 6x4 inches for single panels, 10x4 for side-by-side
- Use ORBIT_COLORS from labels.py for shortlisted points, gray for non-shortlisted
- Inline rendering in notebook via fig.show(), save static PNG alongside for markdown tutorial reference
- RDF: compute from raw.json labeled_points pairwise distances using numpy broadcasting, bin at 0.1 Angstrom
- Diffraction: call existing simulate_powder_xrd.py on checked CandidateRecord from sc_zn_candidates.jsonl
- Screening scatter: read checked sc_zn_screened.jsonl directly (20 data points)
- Annotate RDF peaks with orbit shell names from SHELL_NAMES using vertical lines at computed mean radial distances
- Crystal expansion: replicate orbit-library sites at lattice vectors [a,0,0], [0,a,0], [0,0,a] using base_cell from design YAML
- Default 2x2x2 expansion (800 sites from 100 motif × 8 cells)
- Plotly Scatter3d with markers only (no bonds/cages), central cell highlighted with higher opacity
- Label as "periodic approximant tiling" with a note explaining the relationship to true QC

### Claude's Discretion

- Exact axis label wording and annotation placement
- Whether to combine RDF + diffraction into one side-by-side panel or keep separate
- How to handle the simulate_powder_xrd.py API integration if the call signature differs from expectations

### Deferred Ideas (OUT OF SCOPE)

- Publication SVG/PDF export via kaleido (VIZ-F01 — future)
- Animated rotation (VIZ-F02 — future)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VIZ-03 | Notebook renders a 2D matplotlib scatter of energy_proxy vs min_distance_proxy with shortlisted candidates highlighted and threshold boundaries | screening_scatter() uses sc_zn_screened.jsonl (4 shortlisted records) + sc_zn_screen_calibration.json for threshold lines |
| VIZ-04 | Notebook renders a radial distribution function plot with shell-peak annotations derived from raw.json labeled point distances | rdf_plot() uses orbit library fractional positions (100 unique sites), annotates with SHELL_NAMES at per-orbit mean radial distances |
| VIZ-05 | Notebook renders a simulated powder XRD diffraction pattern using existing pipeline infrastructure | diffraction_plot() calls simulate_powder_xrd_patterns([CandidateRecord]) — API verified, returns peaks list |
| ENRICH-02 | Notebook shows a crystal expansion view demonstrating how the Sc-Zn motif tiles into a larger periodic approximant structure | expansion_figure() in expansion.py replicates orbit library sites at offsets n*a for n in {0,1}^3, renders as plotly Scatter3d |
</phase_requirements>

---

## Summary

Phase 46 implements four remaining visualization functions by filling in the stubs created in Phase 45 (`matplotlib_pub.py`, `expansion.py`), wiring them into new notebook cells, and adding appropriate narrative. All dependencies are already installed in the project venv (`matplotlib 3.10.8`, `plotly 6.6.0`, `scipy 1.17.1`, `numpy 2.4.2`). The `[viz]` optional-dependency group is already declared in `pyproject.toml`.

The most important data-model correction from the CONTEXT.md assumptions: `sc_zn_screened.jsonl` contains only **4 records** (all shortlisted, all with identical proxy values), not 20. The screening scatter should read thresholds from `sc_zn_screen_calibration.json` and acknowledge this is a test dataset. For the RDF, `raw.json` labeled_points contain 4 identical copies of 13 unique design-time points; using the 100-site orbit library fractional positions produces a cleaner pairwise-distance histogram. The XRD API is confirmed working: `simulate_powder_xrd_patterns([CandidateRecord])` returns a list of dicts with `peaks` (list of `{two_theta, intensity}`).

**Primary recommendation:** Implement matplotlib_pub.py and expansion.py as pure functions that return figure objects (matplotlib Figure and plotly Figure respectively). Insert notebook cells in sections 5 and 6, and a new section 4.3 for the expansion view. Use orbit library as the canonical source for RDF distances, not raw.json.

---

## Standard Stack

### Core (all already installed in project venv)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `matplotlib` | 3.10.8 | Screening scatter, RDF, diffraction panels | De facto publication-quality 2D scientific figure standard; already in `[viz]` group |
| `numpy` | 2.4.2 | Pairwise distance computation, histogram binning | Already a core dependency |
| `plotly` | 6.6.0 | Crystal expansion 3D figure (`go.Scatter3d`) | Already used in Phase 45 `plotly_3d.py` |
| `scipy` | 1.17.1 | Optional: `cKDTree` for pairwise distances (numpy broadcasting also works) | Already in `[viz]` group |

### No New Libraries Required

All libraries are already installed. The `[viz]` optional group is already in `pyproject.toml` and the venv.

---

## Architecture Patterns

### Recommended Module Structure

```
materials-discovery/src/materials_discovery/visualization/
    __init__.py          # add exports for new functions (phase 46)
    matplotlib_pub.py    # fill in: STYLE, screening_scatter(), rdf_plot(), diffraction_plot()
    expansion.py         # fill in: expansion_figure()
    plotly_3d.py         # existing — do NOT modify
    labels.py            # existing — imports ORBIT_COLORS, SHELL_NAMES
    raw_export.py        # existing — do NOT modify
```

### Pattern 1: Shared matplotlib Style Dict

**What:** A module-level dict `PUB_STYLE` passed to `plt.rc_context()` so every figure respects the same look.
**When to use:** Every `matplotlib_pub.py` function must use this context manager.

```python
# Source: matplotlib rcParams documentation
PUB_STYLE: dict = {
    "font.family": "sans-serif",
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "axes.spines.top": False,
    "axes.spines.right": False,
}

def screening_scatter(...) -> matplotlib.figure.Figure:
    with matplotlib.pyplot.rc_context(PUB_STYLE):
        fig, ax = plt.subplots(figsize=(6, 4))
        ...
    return fig
```

### Pattern 2: Optional-import guard (mirrors plotly_3d.py)

**What:** Wrap the matplotlib/numpy imports in a try/except at module top so `import matplotlib_pub` never fails even without `[viz]` installed.

```python
try:
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    _PUB_AVAILABLE = True
    _PUB_IMPORT_ERROR: str | None = None
except ImportError as exc:
    _PUB_AVAILABLE = False
    _PUB_IMPORT_ERROR = str(exc)

def _require_pub() -> None:
    if not _PUB_AVAILABLE:
        raise ImportError(
            "Publication figures require the [viz] extra. "
            "Install with: uv pip install 'materials-discovery[viz]'. "
            f"Missing: {_PUB_IMPORT_ERROR}"
        )
```

### Pattern 3: Screening Scatter — Data Loading

**What:** Load from `sc_zn_screened.jsonl` (4 shortlisted records) for the highlighted points. Load thresholds from `sc_zn_screen_calibration.json` for the boundary lines. There is no separate "non-shortlisted" JSONL; the scatter shows the 4 shortlisted points only plus threshold lines.

**Data fields verified:**
```python
# Each record in sc_zn_screened.jsonl:
{
    "candidate_id": "md_000006",
    "screen": {
        "energy_proxy_ev_per_atom": -2.778674,
        "min_distance_proxy": 0.751937,
        "passed_thresholds": True,
        "shortlist_rank": 1,
    }
}

# sc_zn_screen_calibration.json:
{
    "max_energy_threshold": -2.776664,
    "min_distance_threshold": 0.747795,
    "passed_count": 20,
    "shortlisted_count": 4,
    "input_count": 30,
}
```

**Implementation note:** All 4 records have identical proxy values (test dataset artifact). The scatter will show 4 overlapping points. Add threshold lines using `ax.axhline` / `ax.axvline` from calibration file. Title should read "Screening Results: 4/30 shortlisted".

### Pattern 4: RDF — Use Orbit Library, Not raw.json Labeled Points

**Critical correction from CONTEXT.md:** `raw.json` labeled_points have 52 entries that are **4 identical copies** of 13 unique design-time points (pent.top.center, pent.top.center#2, …#3, …#4 are all at the same Cartesian coordinates). Pairwise distances among 52 points produce 42 zero-distance pairs and a misleadingly sparse RDF.

**Correct approach:** Load orbit library (`sc_zn_tsai_bridge.json`), convert 100 fractional positions to centered Cartesian (same formula as `plotly_3d.py`), compute all pairwise distances, bin at 0.1 Å.

**Orbit library coordinate conversion (verified):**
```python
# Source: plotly_3d.py _frac_to_centered_cart() pattern
a = orbit_lib_data["base_cell"]["a"]       # 13.7923
mc_frac = orbit_lib_data["motif_center"]   # [0.5, 0.5, 0.5]
mc_cart = [f * a for f in mc_frac]         # [6.896, 6.896, 6.896]

# For site with fractional_position fp:
x = fp[0] * a - mc_cart[0]
y = fp[1] * a - mc_cart[1]
z = fp[2] * a - mc_cart[2]
```

**Orbit shell mean radii (verified from orbit library):**
| Orbit | Shell Name | Mean radius (Å) |
|-------|-----------|-----------------|
| tsai_zn7 | Zn inner shell | 6.13 |
| tsai_sc1 | Sc icosahedron shell | 6.73 |
| tsai_zn6 | Zn middle shell | 5.97 |
| tsai_zn5 | Zn pentagonal shell | 6.57 |
| tsai_zn4 | Zn outer shell | 7.73 |

These mean radial distances are used as the positions of vertical annotation lines in the RDF plot. The pairwise distance histogram (not radial) should be the main chart; vertical lines indicate the shells.

**Numpy broadcasting pairwise distances:**
```python
import numpy as np
coords = np.array([[x,y,z] for each site])  # shape (100, 3)
diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]  # (100, 100, 3)
dists = np.sqrt((diff**2).sum(axis=-1))     # (100, 100)
upper = dists[np.triu_indices(100, k=1)]    # 4950 unique pairwise distances
counts, edges = np.histogram(upper, bins=np.arange(0, upper.max()+0.1, 0.1))
```

### Pattern 5: Diffraction — XRD API

**Verified call signature:**
```python
# Source: diffraction/simulate_powder_xrd.py — verified in venv
from materials_discovery.diffraction.simulate_powder_xrd import simulate_powder_xrd_patterns
from materials_discovery.common.schema import CandidateRecord
import json

with open("data/candidates/sc_zn_candidates.jsonl") as f:
    data = json.loads(f.readline())
candidate = CandidateRecord.model_validate(data)
patterns = simulate_powder_xrd_patterns([candidate])  # list of 1
pattern = patterns[0]
# pattern = {"candidate_id": "md_000001", "peaks": [{"two_theta": 15.4, "intensity": 88.1}, ...], "fingerprint": "..."}
```

`simulate_powder_xrd_patterns` accepts `candidates: list[CandidateRecord]` and `n_peaks: int = 12`. It returns a list of dicts. The returned peaks have already-normalized intensities (max=100).

Alternatively, `sc_zn_xrd_patterns.jsonl` in `data/reports/` already contains 4 pre-computed patterns. The plan may read from either source; calling the function on a candidate is preferred per CONTEXT.md to demonstrate the pipeline.

**Best candidate to use for the diffraction plot:** `md_000012` (top-ranked in `sc_zn_ranked.jsonl`, shortlist_rank=1 in screened.jsonl).

**Rendering with matplotlib stem plot:**
```python
two_thetas = [p["two_theta"] for p in pattern["peaks"]]
intensities = [p["intensity"] for p in pattern["peaks"]]
ax.vlines(two_thetas, 0, intensities, colors="#2563eb", linewidth=1.5)
ax.set_xlabel("2θ (degrees)")
ax.set_ylabel("Relative intensity")
```

### Pattern 6: Crystal Expansion — Coordinate Math

**Verified approach:** The orbit library provides fractional positions. To tile into a 2×2×2 supercell, add lattice-vector offsets (n1,n2,n3) in {0,1}^3 to the fractional coordinates before converting to Cartesian.

```python
import itertools
a = orbit_lib_data["base_cell"]["a"]   # 13.7923
offsets = list(itertools.product([0, 1], repeat=3))  # 8 combinations

all_sites = []
for (n1, n2, n3) in offsets:
    is_central = (n1, n2, n3) == (0, 0, 0)
    for orb in orbit_lib_data["orbits"]:
        orbit_name = orb["orbit"]
        color = ORBIT_COLORS.get(orbit_name, DEFAULT_ORBIT_COLOR)
        opacity = 1.0 if is_central else 0.3
        for site in orb["sites"]:
            fp = site["fractional_position"]
            # Add lattice offset, convert to Angstrom centered at motif
            x = (fp[0] + n1) * a - mc_cart[0]
            y = (fp[1] + n2) * a - mc_cart[1]
            z = (fp[2] + n3) * a - mc_cart[2]
            all_sites.append({...})
```

Total sites: 100 × 8 = 800. Central cell (0,0,0 offset) uses `opacity=1.0`; surrounding 7 cells use `opacity=0.3`. Per CONTEXT.md the desaturated color approach is at the agent's discretion — opacity reduction on the same colors is simplest.

**Output:** `go.Scatter3d` with `mode="markers"`, one trace per orbit per cell is fine but creates 40 traces. Alternatively: one trace per orbit with all 8 cells concatenated (using `None` separators is not needed for markers), with custom `marker.opacity` per point via `marker.opacity` as a list. The list-of-opacity approach is cleaner.

### Pattern 7: Notebook Cell Insertion Points

Based on notebook inspection (40 cells, section 5 is cell 17-19, section 6 is cell 20-22):

| New cell content | Insert after cell ID | Insert before |
|-----------------|---------------------|---------------|
| Screening scatter (VIZ-03) | `a3f1c8e2` ("What the screening numbers mean") | Section 6 heading |
| RDF plot (VIZ-04) | Screening scatter cell (new) | Diffraction cell |
| Diffraction plot (VIZ-05) | RDF cell (new) | Section 6 heading |
| Crystal expansion intro markdown | `c3d4e5f6` (cell 16, VIZ-02 shell figure) | Section 5 heading |
| Crystal expansion code (ENRICH-02) | Expansion intro markdown | Section 5 heading |

Per CONTEXT.md: "Notebook sections 5, 6, and after section 10 need new figure cells." The crystal expansion fits best in Section 4 (after the existing plotly 3D figures) as a natural extension of 3D visualization. Screening scatter and validation-related panels belong at end of Section 5.

### Pattern 8: `__init__.py` Export Updates

Current `__init__.py` exports only `plotly_3d` functions conditionally. For Phase 46, add conditional exports for `matplotlib_pub` and `expansion` using the same pattern:

```python
try:
    from materials_discovery.visualization.matplotlib_pub import (
        screening_scatter,
        rdf_plot,
        diffraction_plot,
    )
    from materials_discovery.visualization.expansion import (
        expansion_figure,
    )
except ImportError:
    pass
else:
    __all__ += ["screening_scatter", "rdf_plot", "diffraction_plot", "expansion_figure"]
```

### Anti-Patterns to Avoid

- **Using raw.json for RDF computation:** Raw labeled_points are 4x-duplicated design-time geometry; use orbit library for correct pairwise distances.
- **Hardcoding thresholds in scatter:** Always read from `sc_zn_screen_calibration.json` so the figure stays correct if data is regenerated.
- **Calling `plt.show()` inside library functions:** Return the Figure object; let the notebook call `fig.show()` (for plotly) or display `fig` inline (for matplotlib, IPython renders it automatically when returned as last expression or via `display(fig)`).
- **Large matplotlib figures in jupyter without `%matplotlib inline`:** The notebook must have `%matplotlib inline` or `matplotlib.use('Agg')` guard; rely on the existing notebook preamble.
- **Putting matplotlib imports at module top without guard:** Must use the same try/except pattern as `plotly_3d.py`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pairwise distances | Custom nested loop | `numpy` broadcasting `coords[:, np.newaxis] - coords` | O(n²) loop in Python is slow; numpy is ~100x faster for 100 sites |
| Histogram binning | Manual bucket counting | `numpy.histogram` | Edge case correctness (bin edges, last bin inclusive) |
| RDF normalization to g(r) | Custom density normalization | Skip — plot raw histogram as "pair count per distance bin" | True g(r) requires number density; for a tutorial plot the raw count histogram is simpler and equally illustrative |
| Crystal expansion offsets | Custom geometry math | `itertools.product([0,1], repeat=3)` + scalar multiply | 3 lines, correct, no geometry bugs |
| Color desaturation for expansion | Custom HSL manipulation | Use `marker.opacity` list in plotly Scatter3d | Plotly native, one dict key |

---

## Common Pitfalls

### Pitfall 1: sc_zn_screened.jsonl Has Only 4 Records (Not 20)

**What goes wrong:** CONTEXT.md says "20 data points" for the scatter. The file has exactly 4 records, all shortlisted, all with identical proxy values.
**Why it happens:** The Sc-Zn dataset uses test/placeholder data with a single prototype seed. Only shortlisted records are written to the screened file; "passed but not shortlisted" records are not persisted.
**How to avoid:** Read from `sc_zn_screened.jsonl` for shortlisted points, read thresholds from `sc_zn_screen_calibration.json`. Acknowledge 4 identical overlapping points in the figure title ("4 shortlisted / 20 passed / 30 total").
**Warning signs:** If scatter code expects 20 rows and tries to zip with a 20-element list, it will error.

### Pitfall 2: raw.json Labeled Points Are 4x Duplicated

**What goes wrong:** Using all 52 raw.json labeled_points for pairwise RDF produces 42 zero-distance pairs and 4× inflated bin counts.
**Why it happens:** Zomic exports each occurrence of a labeled point separately. pent.top.center, pent.top.center#2, #3, #4 are at identical Cartesian coordinates.
**How to avoid:** Use orbit library fractional positions (100 unique sites) for RDF computation.
**Warning signs:** RDF histogram has a huge spike at 0 Å.

### Pitfall 3: Matplotlib Figure Not Displayed in Notebook

**What goes wrong:** `fig` is returned from a library function but nothing appears in the notebook output.
**Why it happens:** matplotlib figures render via side-effect (`plt.show()`) or explicit display; returning from a cell doesn't auto-display unless it's the last expression.
**How to avoid:** In notebook code cells, end with `display(fig)` or `fig` as the last expression (IPython auto-displays). Do NOT call `plt.show()` inside library functions.

### Pitfall 4: CandidateRecord Requires Python 3.11+

**What goes wrong:** `CandidateRecord.model_validate()` raises `Unable to evaluate type annotation 'Position3D | None'` on Python < 3.10.
**Why it happens:** The schema uses union syntax (`|`) from Python 3.10+.
**How to avoid:** Use the project venv which is Python 3.11.15. The notebook should be run with the project venv kernel.

### Pitfall 5: expansion_figure with 800 Points Needs One Trace Per Orbit (Not Per Cell)

**What goes wrong:** Creating 40 traces (5 orbits × 8 cells) with separate plotly traces per cell bloats the legend and slows rendering.
**How to avoid:** Create 5 traces total (one per orbit), concatenate all 800 site positions across all 8 cells. Use `marker.opacity` as a Python list to set per-point opacity (1.0 for central cell, 0.3 for others). Plotly Scatter3d supports list-valued marker opacity.
**Warning signs:** 40 legend entries visible in figure.

### Pitfall 6: Matplotlib PNG Save Path

**What goes wrong:** `fig.savefig(path)` writes relative to cwd, which in Jupyter is the notebook directory.
**How to avoid:** Use absolute paths derived from a `NOTEBOOK_DIR = Path(__file__).parent.resolve()` pattern, OR use the same `paths` dict already established in the notebook (cell 8, `paths = {}`).

---

## Code Examples

### RDF Plot (Core Algorithm)

```python
# Source: numpy documentation + orbit library schema (verified)
import numpy as np
import json

with open("data/prototypes/generated/sc_zn_tsai_bridge.json") as f:
    orb = json.load(f)

a = orb["base_cell"]["a"]          # 13.7923
mc = [f * a for f in orb["motif_center"]]  # [6.896, 6.896, 6.896]

coords = []
orbit_names = []
for o in orb["orbits"]:
    for s in o["sites"]:
        fp = s["fractional_position"]
        coords.append([fp[i] * a - mc[i] for i in range(3)])
        orbit_names.append(o["orbit"])

coords = np.array(coords)  # (100, 3)
diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
dists = np.sqrt((diff ** 2).sum(axis=-1))
upper = dists[np.triu_indices(100, k=1)]  # 4950 unique pairs

bin_width = 0.1
bins = np.arange(0, upper.max() + bin_width, bin_width)
counts, edges = np.histogram(upper, bins=bins)
centers = (edges[:-1] + edges[1:]) / 2
```

### Screening Scatter (Threshold Lines)

```python
# Source: matplotlib documentation + verified calibration file schema
import json
import matplotlib.pyplot as plt

with open("data/screened/sc_zn_screened.jsonl") as f:
    records = [json.loads(l) for l in f]
with open("data/calibration/sc_zn_screen_calibration.json") as f:
    cal = json.load(f)

xs = [r["screen"]["min_distance_proxy"] for r in records]
ys = [r["screen"]["energy_proxy_ev_per_atom"] for r in records]

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(xs, ys, c="#0072B2", s=60, zorder=3, label="Shortlisted (4)")
ax.axvline(cal["min_distance_threshold"], color="#888", linestyle="--", label="Min dist threshold")
ax.axhline(cal["max_energy_threshold"], color="#555", linestyle=":", label="Max energy threshold")
ax.set_xlabel("min_distance_proxy")
ax.set_ylabel("energy_proxy_ev_per_atom (eV/atom)")
ax.set_title(f"Screening: {cal['shortlisted_count']} shortlisted / {cal['passed_count']} passed / {cal['input_count']} total")
ax.legend()
```

### Crystal Expansion (Core Loop)

```python
# Source: plotly documentation + orbit library schema (verified)
import itertools
import plotly.graph_objects as go
from materials_discovery.visualization.labels import ORBIT_COLORS, DEFAULT_ORBIT_COLOR, SHELL_NAMES

a = orbit_lib_data["base_cell"]["a"]
mc = [f * a for f in orbit_lib_data["motif_center"]]
offsets = list(itertools.product([0, 1], repeat=3))  # 8 cells

fig = go.Figure()
for orb in orbit_lib_data["orbits"]:
    orbit_name = orb["orbit"]
    color = ORBIT_COLORS.get(orbit_name, DEFAULT_ORBIT_COLOR)
    shell_name = SHELL_NAMES.get(orbit_name, orbit_name)

    xs, ys, zs, opacities, texts = [], [], [], [], []
    for (n1, n2, n3) in offsets:
        is_central = (n1 == 0 and n2 == 0 and n3 == 0)
        op = 1.0 if is_central else 0.3
        for site in orb["sites"]:
            fp = site["fractional_position"]
            xs.append((fp[0] + n1) * a - mc[0])
            ys.append((fp[1] + n2) * a - mc[1])
            zs.append((fp[2] + n3) * a - mc[2])
            opacities.append(op)
            cell_label = "central" if is_central else f"cell ({n1},{n2},{n3})"
            texts.append(f"{site['label']} — {shell_name} — {cell_label}")

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers",
        marker=dict(size=5, color=color, opacity=opacities),
        name=shell_name,
        text=texts,
        hovertemplate="%{text}<extra></extra>",
    ))
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| matplotlib `ax.stem()` for XRD | `ax.vlines()` + optional `ax.fill_between()` for envelope | vlines is cleaner for sparse peak data; stem creates distracting baseline line |
| Global `matplotlib.rcParams` mutation | `plt.rc_context(STYLE)` context manager | Context manager is scoped; does not mutate global state across imports |

---

## Open Questions

1. **Whether to combine RDF + diffraction as side-by-side panel**
   - What we know: CONTEXT.md leaves this at the agent's discretion; 10×4 figure size is defined for side-by-side
   - What's unclear: Whether side-by-side or separate panels makes the notebook narrative clearer
   - Recommendation: Implement as two separate 6×4 functions (`rdf_plot()`, `diffraction_plot()`); the notebook cell can optionally display them side-by-side using `fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))` pattern

2. **Screening scatter with all 4 points at identical coordinates**
   - What we know: All 4 shortlisted records have energy_proxy=-2.778674 and min_distance_proxy=0.751937 (test dataset)
   - What's unclear: Should the plot use jitter to separate the overlapping points, or show them stacked honestly?
   - Recommendation: No jitter; note in figure subtitle that all 4 have identical proxy values in this test dataset; threshold lines are still informative

3. **Notebook cell for expansion: Section 4.3 vs new Section 4.5**
   - What we know: CONTEXT.md says "after section 10" but expansion fits visually after the 3D figures in Section 4
   - Recommendation: Insert as Section 4.3 ("Crystal Expansion View") immediately after the shell figure cells 15-16, before Section 5 heading

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| matplotlib | VIZ-03, VIZ-04, VIZ-05 | Yes | 3.10.8 | — |
| numpy | VIZ-04 (RDF distances) | Yes | 2.4.2 | — |
| plotly | ENRICH-02 | Yes | 6.6.0 | — |
| scipy | Optional RDF | Yes | 1.17.1 | numpy broadcasting (no fallback needed) |
| sc_zn_screened.jsonl | VIZ-03 | Yes | 4 records | — |
| sc_zn_screen_calibration.json | VIZ-03 thresholds | Yes | current | — |
| sc_zn_tsai_bridge.json (orbit lib) | VIZ-04, ENRICH-02 | Yes | 5 orbits, 100 sites | — |
| sc_zn_candidates.jsonl (CandidateRecord) | VIZ-05 | Yes | 30 records | sc_zn_ranked.jsonl (4 records) |
| simulate_powder_xrd_patterns | VIZ-05 | Yes | verified working | sc_zn_xrd_patterns.jsonl (pre-computed) |

**Missing dependencies with no fallback:** None.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `cd materials-discovery && uv run pytest tests/test_matplotlib_pub.py tests/test_expansion.py -x -q` |
| Full suite command | `cd materials-discovery && uv run pytest -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VIZ-03 | `screening_scatter()` returns matplotlib Figure with 2 threshold lines and shortlisted scatter | unit | `pytest tests/test_matplotlib_pub.py::test_screening_scatter_has_threshold_lines -x` | No — Wave 0 |
| VIZ-03 | `screening_scatter()` uses ORBIT_COLORS for shortlisted markers | unit | `pytest tests/test_matplotlib_pub.py::test_screening_scatter_uses_orbit_colors -x` | No — Wave 0 |
| VIZ-04 | `rdf_plot()` returns matplotlib Figure with 5 vertical annotation lines (one per shell) | unit | `pytest tests/test_matplotlib_pub.py::test_rdf_plot_has_shell_annotations -x` | No — Wave 0 |
| VIZ-04 | `rdf_plot()` histogram has non-zero bins from 1.5 Å onward | unit | `pytest tests/test_matplotlib_pub.py::test_rdf_plot_first_peak_above_1ang -x` | No — Wave 0 |
| VIZ-05 | `diffraction_plot()` returns matplotlib Figure with 12 peaks | unit | `pytest tests/test_matplotlib_pub.py::test_diffraction_plot_has_12_peaks -x` | No — Wave 0 |
| ENRICH-02 | `expansion_figure()` returns go.Figure with 800 total marker points | unit | `pytest tests/test_expansion.py::test_expansion_figure_800_sites -x` | No — Wave 0 |
| ENRICH-02 | `expansion_figure()` central cell sites have opacity 1.0; others have opacity 0.3 | unit | `pytest tests/test_expansion.py::test_expansion_figure_central_cell_opacity -x` | No — Wave 0 |
| all | `matplotlib_pub` importable without viz extra; raises ImportError on function call | unit | `pytest tests/test_matplotlib_pub.py::test_import_guard -x` | No — Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest tests/test_matplotlib_pub.py tests/test_expansion.py -x -q`
- **Per wave merge:** `uv run pytest -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_matplotlib_pub.py` — covers VIZ-03, VIZ-04, VIZ-05
- [ ] `tests/test_expansion.py` — covers ENRICH-02

*(Existing `tests/test_plotly_3d.py` already has `test_matplotlib_pub_importable` and `test_expansion_importable` stubs that will continue to pass.)*

---

## Project Constraints (from CLAUDE.md)

| Directive | Impact on This Phase |
|-----------|---------------------|
| Update `materials-discovery/Progress.md` (changelog + diary) on every change to `materials-discovery/` | Every task that writes a file must append to Progress.md |
| Changelog table: date, short title, brief details column | Follow the existing format |
| Diary section: timestamped entry with what/why/open items | Append under today's heading |

---

## Sources

### Primary (HIGH confidence)

- Direct code inspection: `materials-discovery/src/materials_discovery/diffraction/simulate_powder_xrd.py` — verified function signature and output format
- Direct code inspection: `materials-discovery/src/materials_discovery/visualization/plotly_3d.py` — coordinate conversion pattern, orbit_figure pattern
- Direct data inspection: `sc_zn_screened.jsonl` — 4 records, all with identical proxy values, schema confirmed
- Direct data inspection: `sc_zn_screen_calibration.json` — thresholds and counts confirmed
- Direct data inspection: `sc_zn_tsai_bridge.json` — 100 sites, 5 orbits, base_cell a=13.7923, motif_center=[0.5,0.5,0.5]
- Direct data inspection: `sc_zn_tsai_bridge.raw.json` — 52 labeled_points confirmed as 4 identical copies of 13 unique points
- Runtime verification: CandidateRecord.model_validate() + simulate_powder_xrd_patterns() called in project venv — confirmed working, 12 peaks output
- matplotlib 3.10.8 + plotly 6.6.0 + scipy 1.17.1 confirmed available in project venv

### Secondary (MEDIUM confidence)

- Orbit mean radii computed from orbit library fractional positions: tsai_zn6=5.97Å, tsai_zn7=6.13Å, tsai_zn5=6.57Å, tsai_sc1=6.73Å, tsai_zn4=7.73Å — computed in session, matches Phase 45 test assertions in test_plotly_3d.py

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified in venv
- Architecture: HIGH — based on direct code inspection of existing modules
- Pitfalls: HIGH — data anomalies discovered by direct file inspection
- Test architecture: HIGH — pytest framework and pattern from Phase 45 directly applicable

**Research date:** 2026-04-15
**Valid until:** 2026-06-01 (stable library stack, data files checked into repo)
