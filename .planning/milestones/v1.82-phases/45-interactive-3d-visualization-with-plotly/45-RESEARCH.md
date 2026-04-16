# Phase 45: Interactive 3D Visualization with Plotly - Research

**Researched:** 2026-04-15
**Domain:** Plotly 3D interactive visualization, scipy ConvexHull, orbit-colored Scatter3d, Tsai shell decomposition
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Import ORBIT_COLORS from labels.py (Phase 44 output) — one Scatter3d trace per anchor-library orbit name
- Hover text shows: site label + orbit name + species + shell name (e.g. "Zn7_01 (tsai_zn7) - Zn - Zn inner shell")
- Labels OFF by default, show on hover — prevents overcrowding
- Uniform marker size=8 for all sites
- Assign shells by computing mean radial distance of each orbit's sites from motif_center (from design YAML), sorted ascending
- Render polyhedral cages with scipy.spatial.ConvexHull for each shell → Mesh3d with opacity=0.15 + edge lines overlay
- Shells toggleable via legendgroup on separate traces
- Two separate plotly figures: orbit-colored scatter (orbit_figure) and shell-decomposed figure (shell_figure)
- New modules inside materials_discovery/visualization/: plotly_3d.py (functional), matplotlib_pub.py (empty stub for Phase 46)
- try/except ImportError at module top with clear "install materials-discovery[viz]" error message
- New [viz] optional-dependencies group in pyproject.toml: plotly>=6.0, matplotlib>=3.9, kaleido>=1.0, scipy>=1.13, nbformat>=4.2.0
- Replace current EMBED_PREVIEW HTML block in notebook with plotly figure cells, keeping EMBED_PREVIEW as fallback when plotly is not installed

### Claude's Discretion

- Exact plotly layout parameters (camera angle, axis labels, title text)
- Whether to add plotly_3d helper functions to __init__.py or keep them as direct imports from plotly_3d
- Number of helper functions vs monolithic orbit_figure() / shell_figure()

### Deferred Ideas (OUT OF SCOPE)

- matplotlib 2D panels (Phase 46)
- Crystal expansion view (Phase 46)
- Static PNG/SVG export via kaleido (future)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VIZ-01 | Notebook renders an interactive plotly 3D scatter with one trace per orbit, distinct colorblind-safe colors, hover labels showing site name and orbit | orbit_figure() using orbit library 100 sites; ORBIT_COLORS from labels.py; Scatter3d confirmed working in uv venv |
| VIZ-02 | Notebook renders a shell-decomposed Tsai cluster figure showing each concentric polyhedral shell as separate labeled layers with polyhedral cage wireframes | shell_figure() using orbit library 5 orbits; ConvexHull verified; 12 hull faces for tsai_zn6; legendgroup toggling verified |
| ENRICH-03 | New visualization modules (plotly_3d.py, matplotlib_pub.py) live inside materials_discovery.visualization and are installable via a [viz] optional dependency group | pyproject.toml has no [viz] group yet; plotly 6.6.0 and scipy 1.17.1 already in .venv; matplotlib 3.10.8 in .venv; kaleido and nbformat NOT installed |
</phase_requirements>

---

## Summary

Phase 45 adds two interactive plotly 3D figures to the guided design tutorial notebook: an orbit-colored Scatter3d of all 100 anchor-library sites (5 traces, one per anchor orbit), and a shell-decomposed figure rendering each of the 5 Tsai cluster shells as site markers plus a ConvexHull Mesh3d cage. Both figures consume the orbit-library JSON (`sc_zn_tsai_bridge.json`) directly rather than the 52-point raw export, because the orbit library provides clean 5-orbit groupings with fractional positions that convert straightforwardly to Cartesian coordinates.

The critical data-namespace finding is that `RawExportViewModel.points` carry **design-time** orbit names (`pent`, `frustum`, `joint`) while `ORBIT_COLORS` in `labels.py` keys on **anchor-library** orbit names (`tsai_zn7`, `tsai_sc1`, `tsai_zn6`, `tsai_zn5`, `tsai_zn4`). The orbit library JSON bridges these namespaces via the `source_design_orbit` field, but the mapping is not one-to-one: the design orbit `pent` maps to three anchor orbits (`tsai_sc1`, `tsai_zn5`, `tsai_zn4`). Both figures must therefore read the orbit library JSON directly — not `RawExportViewModel` — to produce clean per-anchor-orbit traces.

Shell assignment by mean radial distance is feasible and produces a physically sensible ordering. The computed shell sequence (innermost first): `tsai_zn6` (5.97 A), `tsai_zn7` (6.13 A), `tsai_zn5` (6.57 A), `tsai_sc1` (6.73 A), `tsai_zn4` (7.73 A). This ordering is computed, not hardcoded, per the architecture decision. ConvexHull works for all five shells (verified for `tsai_zn6`: 12 triangular faces, 18 unique edges). The `legendgroup` mechanism in plotly correctly toggles both marker and cage traces as a single group.

**Primary recommendation:** Both `orbit_figure()` and `shell_figure()` accept the orbit-library JSON dict (loaded via a `load_orbit_library(path)` helper) as their primary input. The `RawExportViewModel` is not needed for either figure — keep `build_view_model()` as the viewer.py entry point only.

---

## Standard Stack

### Core (verified in uv venv — `materials-discovery/.venv`)

| Library | Installed Version | Required Version | Purpose | Status |
|---------|-------------------|-----------------|---------|--------|
| `plotly` | 6.6.0 | >=6.0 | Scatter3d + Mesh3d interactive figures | Already in venv (transitive) |
| `scipy` | 1.17.1 | >=1.13 | `scipy.spatial.ConvexHull` for shell cage faces | Already in venv (transitive via pymatgen) |
| `matplotlib` | 3.10.8 | >=3.9 | stub for matplotlib_pub.py (Phase 46) | Already in venv |
| `kaleido` | NOT installed | >=1.0 | Static PNG/SVG export (deferred to future) | Must add to [viz] group |
| `nbformat` | NOT installed | >=4.2.0 | plotly mime-type rendering in classic Jupyter | Must add to [viz] group |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `numpy` | >=1.26.4 | Array ops for coordinate conversion (fractional→Cartesian) | Already a core dependency |
| `pydantic` | >=2.8.0 | Existing model layer (ZomicViewPoint, RawExportViewModel) | Read only — not used in new plotly module |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `scipy.spatial.ConvexHull` | `alphashape` | ConvexHull is sufficient; Tsai shells are convex; alphashape adds dependency without benefit |
| `plotly` Scatter3d | `vtk`/`mayavi` | plotly is headless-CI-safe and notebook-native; vtk requires X server |
| `go.Mesh3d` cage | `go.Isosurface` | Mesh3d directly accepts simplex indices from ConvexHull; no field interpolation needed |

**Installation (new [viz] group — add to pyproject.toml):**
```bash
# In pyproject.toml [project.optional-dependencies]:
# viz = [
#   "plotly>=6.0",
#   "matplotlib>=3.9",
#   "kaleido>=1.0",
#   "nbformat>=4.2.0",
#   "scipy>=1.13",
# ]
cd materials-discovery
uv pip install -e ".[viz]"
```

**Note:** `plotly`, `scipy`, and `matplotlib` are already in the venv transitively. Adding them explicitly to `[viz]` makes the group self-contained for users who install without `[mlip]`. `kaleido` and `nbformat` are genuinely new installs.

---

## Data Schemas (CRITICAL for implementation)

### sc_zn_tsai_bridge.raw.json — labeled_points schema

```json
{
  "zomic_file": "/path/to/sc_zn_tsai_bridge.zomic",
  "parser": "antlr4",
  "symmetry": "icosahedral",
  "labeled_points": [
    {
      "label": "pent.top.center",
      "source_label": "pent.top.center",
      "occurrence": 1,
      "position": { "...": "..." },
      "cartesian": [15.326, 17.944, 0.0]
    }
  ],
  "segments": [ "..." ]
}
```

Key fields: `label`, `source_label`, `cartesian` (Angstrom, not centered). `_infer_orbit_name(source_label)` extracts design-time orbit prefix (`pent`, `frustum`, `joint`). There are **52 points** in 3 design-orbit groups: `pent`=20, `frustum`=16, `joint`=16.

### sc_zn_tsai_bridge.json — orbit library schema

```json
{
  "base_cell": {"a": 13.7923, "b": 13.7923, "c": 13.7923, "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
  "motif_center": [0.5, 0.5, 0.5],
  "anchor_orbit_summary": {
    "selected_orbits": ["tsai_zn7", "tsai_sc1", "tsai_zn6", "tsai_zn5", "tsai_zn4"],
    "selected_site_count": 100
  },
  "orbits": [
    {
      "orbit": "tsai_zn7",
      "preferred_species": ["Zn"],
      "source_design_orbit": "joint",
      "sites": [
        {"fractional_position": [0.0, 0.0787, 0.0788], "label": "Zn7_01"}
      ]
    }
  ]
}
```

**5 orbits, 100 total sites:** `tsai_zn7`=24, `tsai_sc1`=24, `tsai_zn6`=16, `tsai_zn5`=24, `tsai_zn4`=12.

**Coordinate conversion (cubic, axis-aligned):**
```python
a = orbit_lib["base_cell"]["a"]          # 13.7923 Angstrom
mc_frac = orbit_lib["motif_center"]       # [0.5, 0.5, 0.5]
mc_cart = [f * a for f in mc_frac]        # [6.8962, 6.8962, 6.8962] Angstrom

# For each site: fractional_position -> centered Cartesian
centered = [(frac[i] * a) - mc_cart[i] for i in range(3)]
```

**motif_center in physical coordinates:** [6.8962, 6.8962, 6.8962] Angstrom.

### Design-orbit to anchor-orbit mapping

| Design orbit | Anchor orbit(s) | Site count |
|---|---|---|
| `joint` | `tsai_zn7` | 24 |
| `pent` | `tsai_sc1`, `tsai_zn5`, `tsai_zn4` | 24 + 24 + 12 = 60 |
| `frustum` | `tsai_zn6` | 16 |

**Critical implication:** `pent` maps to 3 anchor orbits. A label-prefix approach cannot distinguish them. Both figures must read the orbit library JSON directly, iterating `orbit_lib["orbits"]` to get clean per-anchor-orbit site lists.

### Hover text format (verified from CONTEXT.md)

```
"{site_label} ({orbit_name}) - {species} - {shell_name}"
```

Examples (verified from actual data):
- `"Zn7_01 (tsai_zn7) - Zn - Zn inner shell"`
- `"Sc1_01 (tsai_sc1) - Sc - Sc icosahedron shell"`
- `"Zn6_01 (tsai_zn6) - Zn - Zn middle shell"`

---

## Architecture Patterns

### Module structure

```
materials-discovery/src/materials_discovery/visualization/
    __init__.py          # add orbit_figure, shell_figure, load_orbit_library exports
    raw_export.py        # unchanged — ZomicViewPoint, build_view_model
    viewer.py            # unchanged — HTML canvas viewer (fallback)
    labels.py            # unchanged — ORBIT_COLORS, SHELL_NAMES, ORBIT_LABELS
    plotly_3d.py         # NEW: orbit_figure(), shell_figure(), load_orbit_library()
    matplotlib_pub.py    # NEW (empty stub): placeholder for Phase 46
```

### Pattern 1: orbit_figure() — All 100 anchor-orbit sites as Scatter3d traces

**What:** One `go.Scatter3d` trace per anchor-library orbit (5 traces). Sites from orbit library JSON, converted to centered Cartesian. Colors from `ORBIT_COLORS`. Shell name from `SHELL_NAMES` for hover text. Labels off by default (hover only).

**Input:** `orbit_lib_data: dict` (from `load_orbit_library(path)`) and optionally the `ORBIT_COLORS`, `SHELL_NAMES` dicts (imported from labels.py at module level).

```python
# Source: verified against plotly 6.6.0 and orbit library schema
import plotly.graph_objects as go
from materials_discovery.visualization.labels import ORBIT_COLORS, SHELL_NAMES, DEFAULT_ORBIT_COLOR

def orbit_figure(orbit_lib_data: dict) -> go.Figure:
    a = orbit_lib_data["base_cell"]["a"]
    mc_frac = orbit_lib_data["motif_center"]
    mc_cart = [f * a for f in mc_frac]
    fig = go.Figure()
    for orb in orbit_lib_data["orbits"]:
        orbit_name = orb["orbit"]
        species = orb["preferred_species"][0] if orb["preferred_species"] else "?"
        shell_name = SHELL_NAMES.get(orbit_name, orbit_name)
        color = ORBIT_COLORS.get(orbit_name, DEFAULT_ORBIT_COLOR)
        xs, ys, zs, texts = [], [], [], []
        for site in orb["sites"]:
            fp = site["fractional_position"]
            x = fp[0] * a - mc_cart[0]
            y = fp[1] * a - mc_cart[1]
            z = fp[2] * a - mc_cart[2]
            xs.append(x); ys.append(y); zs.append(z)
            texts.append(f"{site['label']} ({orbit_name}) - {species} - {shell_name}")
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode="markers",
            marker=dict(size=8, color=color),
            name=SHELL_NAMES.get(orbit_name, orbit_name),
            text=texts,
            hovertemplate="%{text}<extra></extra>",
        ))
    return fig
```

### Pattern 2: shell_figure() — Shell-decomposed figure with ConvexHull cages

**What:** One scatter + one cage Mesh3d per shell (10 traces total, paired via `legendgroup`). Shells sorted by mean radial distance from motif center. ConvexHull faces → Mesh3d with opacity=0.15. Edge lines → separate Scatter3d in `mode='lines'` within the same legendgroup.

```python
# Source: verified — scipy.spatial.ConvexHull with plotly Mesh3d
import numpy as np
from scipy.spatial import ConvexHull
import plotly.graph_objects as go
from materials_discovery.visualization.labels import ORBIT_COLORS, SHELL_NAMES, DEFAULT_ORBIT_COLOR

def _compute_mean_radius(sites: list[dict], a: float, mc_cart: list[float]) -> float:
    import math
    dists = []
    for s in sites:
        fp = s["fractional_position"]
        dx, dy, dz = fp[0]*a - mc_cart[0], fp[1]*a - mc_cart[1], fp[2]*a - mc_cart[2]
        dists.append(math.sqrt(dx**2 + dy**2 + dz**2))
    return sum(dists) / len(dists) if dists else 0.0

def shell_figure(orbit_lib_data: dict) -> go.Figure:
    a = orbit_lib_data["base_cell"]["a"]
    mc_frac = orbit_lib_data["motif_center"]
    mc_cart = [f * a for f in mc_frac]
    # Sort orbits by mean radial distance
    orbits_sorted = sorted(
        orbit_lib_data["orbits"],
        key=lambda orb: _compute_mean_radius(orb["sites"], a, mc_cart)
    )
    fig = go.Figure()
    for shell_idx, orb in enumerate(orbits_sorted, start=1):
        orbit_name = orb["orbit"]
        species = orb["preferred_species"][0] if orb["preferred_species"] else "?"
        shell_name = SHELL_NAMES.get(orbit_name, orbit_name)
        color = ORBIT_COLORS.get(orbit_name, DEFAULT_ORBIT_COLOR)
        group = f"shell_{shell_idx}"
        pts_list = []
        texts = []
        for site in orb["sites"]:
            fp = site["fractional_position"]
            pts_list.append([fp[0]*a - mc_cart[0], fp[1]*a - mc_cart[1], fp[2]*a - mc_cart[2]])
            texts.append(f"{site['label']} ({orbit_name}) - {species} - {shell_name}")
        pts = np.array(pts_list)
        xs, ys, zs = pts[:, 0], pts[:, 1], pts[:, 2]
        # Site markers
        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs, mode="markers",
            marker=dict(size=8, color=color),
            name=f"Shell {shell_idx}: {shell_name}",
            text=texts,
            hovertemplate="%{text}<extra></extra>",
            legendgroup=group,
        ))
        # ConvexHull cage (only for shells with >= 4 non-coplanar sites)
        if len(pts_list) >= 4:
            try:
                hull = ConvexHull(pts)
                # Mesh3d faces
                i_idx, j_idx, k_idx = hull.simplices[:, 0], hull.simplices[:, 1], hull.simplices[:, 2]
                fig.add_trace(go.Mesh3d(
                    x=xs, y=ys, z=zs,
                    i=i_idx, j=j_idx, k=k_idx,
                    opacity=0.15, color=color,
                    name=f"Shell {shell_idx} cage", showlegend=False,
                    legendgroup=group,
                ))
                # Edge wireframe
                edges = set()
                for simplex in hull.simplices:
                    for e in range(3):
                        edges.add(tuple(sorted([simplex[e], simplex[(e+1)%3]])))
                ex, ey, ez = [], [], []
                for v1, v2 in edges:
                    ex += [pts[v1, 0], pts[v2, 0], None]
                    ey += [pts[v1, 1], pts[v2, 1], None]
                    ez += [pts[v1, 2], pts[v2, 2], None]
                fig.add_trace(go.Scatter3d(
                    x=ex, y=ey, z=ez, mode="lines",
                    line=dict(color=color, width=2),
                    name=f"Shell {shell_idx} edges", showlegend=False,
                    legendgroup=group,
                ))
            except Exception:
                pass  # degenerate hull — skip cage
    return fig
```

### Pattern 3: try/except ImportError guard

```python
# At top of plotly_3d.py
try:
    import plotly.graph_objects as go
    import numpy as np
    from scipy.spatial import ConvexHull
    _VIZ_AVAILABLE = True
    _VIZ_IMPORT_ERROR: str | None = None
except ImportError as exc:
    _VIZ_AVAILABLE = False
    _VIZ_IMPORT_ERROR = str(exc)

def _require_viz() -> None:
    if not _VIZ_AVAILABLE:
        raise ImportError(
            f"Interactive 3D visualization requires the [viz] extra. "
            f"Install with: uv pip install 'materials-discovery[viz]'. "
            f"Missing: {_VIZ_IMPORT_ERROR}"
        )
```

### Pattern 4: Notebook cell integration (Section 4 replacement)

The existing notebook cell `4cbab4b3` calls `preview_checked_design()` which renders the HTML canvas viewer. Phase 45 inserts two new cells immediately after the existing preview cell (do not remove the existing cell — it serves as the `EMBED_PREVIEW` fallback).

```python
# New cell 4.1: Interactive orbit scatter
try:
    from materials_discovery.visualization.plotly_3d import orbit_figure, load_orbit_library
    _PLOTLY_AVAILABLE = True
except ImportError:
    _PLOTLY_AVAILABLE = False

if _PLOTLY_AVAILABLE:
    orbit_lib_data = load_orbit_library(
        WORKDIR / "data/prototypes/generated/sc_zn_tsai_bridge.json"
    )
    fig_orbit = orbit_figure(orbit_lib_data)
    fig_orbit.show(renderer="notebook_connected")
else:
    print("Install plotly: uv pip install 'materials-discovery[viz]'")
    print("Falling back to HTML canvas viewer above.")
```

```python
# New cell 4.2: Shell-decomposed Tsai cluster figure
if _PLOTLY_AVAILABLE:
    fig_shell = shell_figure(orbit_lib_data)
    fig_shell.show(renderer="notebook_connected")
```

### Anti-Patterns to Avoid

- **Using RawExportViewModel for orbit figures:** `RawExportViewModel.points` carry design-time orbits (`pent`/`frustum`/`joint`), not anchor-library orbits. Cannot distinguish `tsai_sc1`, `tsai_zn5`, `tsai_zn4` from label alone.
- **Hardcoding shell order:** Must compute mean radial distance dynamically; do not copy shell order from the IUCrJ 2016 paper.
- **Using `fig.show()` without renderer:** Default renderer is `browser` — always specify `renderer="notebook_connected"` in notebook cells to avoid opening a browser tab.
- **Adding plotly to core imports:** The import guard must be at module top, not inside function bodies, so `_VIZ_AVAILABLE` is set once at import time.
- **Embedding plotly.js per-cell:** `renderer="notebook_connected"` loads from CDN once; never use `renderer="notebook"` (embeds ~3.5 MB per call).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Polyhedral cage faces | Custom face triangulation | `scipy.spatial.ConvexHull` → `.simplices` | ConvexHull handles all degenerate cases; 12 faces for the 16-site tsai_zn6 shell verified |
| Edge extraction from hull | Graph traversal | Iterate `hull.simplices`, collect sorted edge pairs into a set | 3 edges per triangle, deduplicate with `sorted((a,b))` tuple set |
| Colorblind-safe palette | Manual color selection | `ORBIT_COLORS` from `labels.py` (Wong 2011, verified Phase 44) | Palette already exists; do not diverge |
| Orbit JSON loading | Custom parser | `json.loads(path.read_text())` | Schema is flat; pydantic not needed for the orbit library |
| Jupyter notebook rendering | Custom HTML embedding | `fig.show(renderer="notebook_connected")` | CDN-based; no bundle bloat |

---

## Computed Shell Ordering (use as validation check, not hardcoded)

| Shell | Anchor Orbit | Mean Radius | Min Radius | Max Radius | Sites | Preferred Species |
|-------|-------------|-------------|------------|------------|-------|-------------------|
| 1 (innermost) | `tsai_zn6` | 5.97 A | 3.88 A | 8.06 A | 16 | Zn |
| 2 | `tsai_zn7` | 6.13 A | 1.54 A | 10.73 A | 24 | Zn |
| 3 | `tsai_zn5` | 6.57 A | 3.53 A | 9.60 A | 24 | Zn |
| 4 | `tsai_sc1` | 6.73 A | 4.89 A | 8.58 A | 24 | Sc |
| 5 (outermost) | `tsai_zn4` | 7.73 A | 5.62 A | 9.84 A | 12 | Zn |

**Note:** The mean radii are close together for shells 1-4 (5.97–6.73 A). The shell ordering is physically sensible but the shells overlap radially — ConvexHull cages will interpenetrate visually, which is physically correct for this structure.

---

## Common Pitfalls

### Pitfall 1: Notebook blob size from plotly.js embedding

**What goes wrong:** Each `fig.show()` without `renderer="notebook_connected"` embeds the full 3.5 MB plotly.js bundle in the cell output. Two figures = 7 MB added to the .ipynb file.

**Prevention:** Always use `fig.show(renderer="notebook_connected")` in notebook cells. Verified: `notebook_connected` is available in plotly 6.6.0.

**Warning sign:** `.ipynb` file size exceeds 5 MB after adding figure cells.

### Pitfall 2: Design-orbit vs anchor-orbit namespace mismatch

**What goes wrong:** Using `ZomicViewPoint.orbit` (design-time: `pent`/`frustum`/`joint`) to key into `ORBIT_COLORS` (anchor-library: `tsai_zn7`/`tsai_sc1`/`tsai_zn6`/`tsai_zn5`/`tsai_zn4`) produces only `DEFAULT_ORBIT_COLOR` for all points.

**Prevention:** Use orbit library JSON directly; iterate `orbit_lib_data["orbits"]` for both figures. Never use `RawExportViewModel` for orbit-colored figures.

**Warning sign:** All markers appear as the default gray (#6b7280) instead of the Wong palette colors.

### Pitfall 3: ConvexHull degenerate hull for coplanar points

**What goes wrong:** `scipy.spatial.ConvexHull` raises `QhullError` if all points are coplanar or fewer than 4 non-coplanar points exist.

**Prevention:** Wrap `ConvexHull(pts)` in try/except; skip cage rendering if hull construction fails. All 5 orbits in the actual data have enough non-coplanar sites (verified: tsai_zn6 with 16 sites produces 12 faces).

### Pitfall 4: Shell mean-radius ordering ties

**What goes wrong:** Two orbits with nearly identical mean radii (shells 1-4 span 5.97–6.73 A, differences ~0.2–0.4 A) could produce unstable sort order across Python versions.

**Prevention:** Use `key=lambda orb: _compute_mean_radius(...)` with a stable sort (Python's sort is stable). Add `orbit_name` as tiebreaker: `key=lambda orb: (_compute_mean_radius(...), orb["orbit"])`.

### Pitfall 5: Missing nbformat causes ValueError in classic Jupyter

**What goes wrong:** `plotly` raises `ValueError: nbformat is not installed` when `fig.show()` is called inside classic Jupyter Notebook (not JupyterLab) without `nbformat>=4.2.0`.

**Prevention:** Include `nbformat>=4.2.0` in `[viz]` pyproject.toml group. Not currently in the venv.

### Pitfall 6: Wrong import path for matplotlib_pub.py stub

**What goes wrong:** An empty stub `matplotlib_pub.py` that contains just `pass` or a docstring will cause import errors if Phase 46 code tries `from materials_discovery.visualization.matplotlib_pub import something_not_defined_yet`.

**Prevention:** Write the stub with `# Phase 46 placeholder — not yet implemented` at top and no `__all__`. Do not export it from `__init__.py` until Phase 46 adds real functions.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| plotly | orbit_figure, shell_figure | Yes (uv venv) | 6.6.0 | HTML canvas viewer (existing) |
| scipy | ConvexHull cage | Yes (uv venv) | 1.17.1 | Skip cage; markers only |
| matplotlib | matplotlib_pub.py stub | Yes (uv venv) | 3.10.8 | N/A (stub only) |
| kaleido | write_image() (deferred) | No | — | Deferred to future phase |
| nbformat | plotly Jupyter mime type | No | — | Must install via [viz] group |
| numpy | Coordinate arrays | Yes (core dep) | >=1.26.4 | N/A (always present) |

**Missing dependencies with no fallback:**
- `nbformat`: Must be added to `[viz]` group in pyproject.toml — plotly will raise `ValueError` in classic Jupyter without it.
- `kaleido`: Deferred per CONTEXT.md; not needed for Phase 45.

**Missing dependencies with fallback:**
- None blocking for Phase 45 (plotly and scipy already in venv transitively).

---

## Validation Architecture

`workflow.nyquist_validation` is absent from `.planning/config.json` — treat as enabled.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.2.0 |
| Config file | `materials-discovery/pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `cd materials-discovery && uv run pytest tests/test_plotly_3d.py -x` |
| Full suite command | `cd materials-discovery && uv run pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VIZ-01 | orbit_figure() returns go.Figure with 5 traces, correct colors, hover text | unit | `uv run pytest tests/test_plotly_3d.py::test_orbit_figure_has_five_traces -x` | No — Wave 0 |
| VIZ-01 | Each trace uses ORBIT_COLORS color for its anchor orbit | unit | `uv run pytest tests/test_plotly_3d.py::test_orbit_figure_trace_colors -x` | No — Wave 0 |
| VIZ-01 | Hover text format matches "label (orbit) - species - shell_name" | unit | `uv run pytest tests/test_plotly_3d.py::test_orbit_figure_hover_text -x` | No — Wave 0 |
| VIZ-02 | shell_figure() returns go.Figure with shells in radial-distance order | unit | `uv run pytest tests/test_plotly_3d.py::test_shell_figure_shell_ordering -x` | No — Wave 0 |
| VIZ-02 | shell_figure() includes Mesh3d cage traces per shell | unit | `uv run pytest tests/test_plotly_3d.py::test_shell_figure_has_mesh3d_traces -x` | No — Wave 0 |
| VIZ-02 | legendgroup ties marker and cage traces together per shell | unit | `uv run pytest tests/test_plotly_3d.py::test_shell_figure_legendgroup -x` | No — Wave 0 |
| ENRICH-03 | ImportError raised with clear message when plotly not installed | unit | `uv run pytest tests/test_plotly_3d.py::test_import_error_message -x` | No — Wave 0 |
| ENRICH-03 | matplotlib_pub.py exists and is importable | unit | `uv run pytest tests/test_plotly_3d.py::test_matplotlib_pub_importable -x` | No — Wave 0 |
| ENRICH-03 | pyproject.toml [viz] group contains all 5 required packages | unit | `uv run pytest tests/test_plotly_3d.py::test_viz_extra_declared -x` | No — Wave 0 |

### Sampling Rate

- **Per task commit:** `cd materials-discovery && uv run pytest tests/test_plotly_3d.py -x`
- **Per wave merge:** `cd materials-discovery && uv run pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- `tests/test_plotly_3d.py` — covers VIZ-01, VIZ-02, ENRICH-03 (all test cases above)
- Existing `tests/test_zomic_visualization.py` — already covers `build_view_model` and HTML viewer; no changes needed

---

## Code Examples

### load_orbit_library helper

```python
# Source: direct from sc_zn_tsai_bridge.json schema (verified)
import json
from pathlib import Path

def load_orbit_library(path: Path) -> dict:
    """Load the orbit library JSON produced by mdisc export-zomic."""
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"orbit library not found: {resolved}")
    return json.loads(resolved.read_text(encoding="utf-8"))
```

### Cartesian coordinate conversion (cubic cell)

```python
# Source: verified from orbit library schema — base_cell has a=b=c, all angles 90 deg
def _frac_to_centered_cart(frac: list[float], a: float, mc_cart: list[float]) -> list[float]:
    return [frac[i] * a - mc_cart[i] for i in range(3)]
```

### Edge extraction from ConvexHull for wireframe

```python
# Source: verified — scipy ConvexHull .simplices are triangular face indices
def _hull_edge_lines(pts, hull):
    """Return flat x/y/z arrays for Scatter3d lines with None separators between edges."""
    edges = set()
    for simplex in hull.simplices:
        for e in range(3):
            edges.add(tuple(sorted([simplex[e], simplex[(e+1) % 3]])))
    ex, ey, ez = [], [], []
    for v1, v2 in edges:
        ex += [pts[v1, 0], pts[v2, 0], None]
        ey += [pts[v1, 1], pts[v2, 1], None]
        ez += [pts[v1, 2], pts[v2, 2], None]
    return ex, ey, ez
```

### __init__.py export additions

```python
# Add to existing imports in materials_discovery/visualization/__init__.py
from materials_discovery.visualization.plotly_3d import (
    load_orbit_library,
    orbit_figure,
    shell_figure,
)

# Add to __all__
__all__ = [
    # ... existing exports ...
    "load_orbit_library",
    "orbit_figure",
    "shell_figure",
]
```

**Note:** Do NOT add any imports from `matplotlib_pub.py` to `__init__.py` until Phase 46 adds real functions. An empty stub should not be exported.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Orca (plotly static export) | kaleido >= 1.0 | plotly 6.x (2025) | kaleido is the only supported path; Orca removed |
| `fig.show(renderer="notebook")` | `fig.show(renderer="notebook_connected")` | plotly 5+ | CDN-based: avoids 3.5 MB bundle per cell |
| `_ORBIT_PALETTE` in raw_export.py | `ORBIT_COLORS` in labels.py | Phase 44 (2026-04-16) | labels.py uses Wong 2011 colorblind-safe palette keyed by anchor orbit name |

**Deprecated/outdated:**
- `_ORBIT_PALETTE` in `raw_export.py`: Still present but keyed differently (positional index, not orbit name). Phase 45 plotly code must use `ORBIT_COLORS` from `labels.py` instead.

---

## Open Questions

1. **Whether to export plotly_3d functions from __init__.py immediately**
   - What we know: CONTEXT.md leaves this to agent discretion
   - What's unclear: Phase 46 will also add to this module; premature export may create API commitment
   - Recommendation: Export `load_orbit_library`, `orbit_figure`, `shell_figure` from `__init__.py` in Phase 45 since they are the primary deliverables

2. **Whether notebooks with `renderer="notebook_connected"` work offline**
   - What we know: `notebook_connected` loads plotly.js from CDN; requires internet
   - What's unclear: Whether tutorial users may run offline
   - Recommendation: Add a comment in the notebook cell noting CDN requirement; the HTML fallback (`preview_checked_design()`) works fully offline

---

## Sources

### Primary (HIGH confidence)

- Direct code read — `materials-discovery/src/materials_discovery/visualization/raw_export.py` — `build_view_model()`, `ZomicViewPoint`, `_infer_orbit_name` behavior
- Direct code read — `materials-discovery/src/materials_discovery/visualization/labels.py` — `ORBIT_COLORS`, `SHELL_NAMES`, `ORBIT_LABELS`, `PREFERRED_SPECIES` (Phase 44 output)
- Direct data read — `sc_zn_tsai_bridge.json` — orbit library schema, 5 orbits, 100 sites, fractional positions, `source_design_orbit` mapping
- Direct data read — `sc_zn_tsai_bridge.raw.json` — 52 labeled_points, design-orbit distribution
- Verified computation — shell radii: `tsai_zn6`=5.97A, `tsai_zn7`=6.13A, `tsai_zn5`=6.57A, `tsai_sc1`=6.73A, `tsai_zn4`=7.73A
- Verified computation — `tsai_zn6` ConvexHull: 12 triangular faces, 18 unique edges, no QhullError
- Verified — `uv run python` in project venv: plotly 6.6.0, scipy 1.17.1, matplotlib 3.10.8 installed; kaleido and nbformat NOT installed
- Verified — plotly renderers: `notebook_connected` available and is correct CDN renderer

### Secondary (MEDIUM confidence)

- `.planning/research/STACK.md` — milestone stack research (2026-04-15); confirms plotly>=6.0 and scipy>=1.13 selection rationale
- `.planning/research/ARCHITECTURE.md` — data flow documentation; confirms orbit library JSON as the primary input for both figures
- `.planning/research/PITFALLS.md` — notebook blob size (Pitfall 1) and shell hardcoding (Pitfall 4) documented

---

## Metadata

**Confidence breakdown:**
- Data schemas (raw.json, orbit library JSON): HIGH — read directly from checked files
- Standard stack (plotly, scipy, matplotlib): HIGH — verified in project venv
- Architecture patterns (orbit_figure, shell_figure): HIGH — verified with actual data and library calls
- Shell ordering: HIGH — computed from actual fractional positions
- Notebook integration: HIGH — read actual notebook cells
- ConvexHull cage rendering: HIGH — verified execution in venv

**Research date:** 2026-04-15
**Valid until:** 2026-05-15 (stable libraries; 30-day horizon)
