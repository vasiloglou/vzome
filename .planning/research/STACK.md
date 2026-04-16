# Stack Research: v1.82 Illustrated Tutorial and Publication-Quality Visualization

**Domain:** Publication-quality quasicrystal visualization for Jupyter notebook tutorial
**Project:** Materials Design Program — materials-discovery subsystem
**Milestone:** v1.82
**Researched:** 2026-04-15
**Confidence:** HIGH for core plotly/matplotlib additions, MEDIUM for RDF and diffraction overlays

---

## Context: What Already Exists (DO NOT re-add)

The v1.81 milestone shipped all of these — they are already in `pyproject.toml` or the
`materials_discovery.visualization` module and must not be re-listed as additions:

- Python 3.11 runtime, `typer`, `pydantic`, `pyyaml`, `numpy`
- `materials_discovery.visualization` with `RawExportViewModel`, `ZomicViewPoint`,
  `ZomicViewSegment`, `build_view_model`, `render_raw_export_html`, `preview_raw_export`,
  `preview_zomic_design`
- HTML canvas-based point/segment viewer (2D projection with mouse rotate/zoom)
- `ExportZomicLabeledGeometry`, `ShapesJsonExporter`, `GitHubShare` export machinery
- Existing `[analysis]` optional group: `pandas>=2.2.2`, `pyarrow>=17.0.0`
- Existing `[mlip]` optional group: `ase>=3.23.0`, `pymatgen>=2024.8.9`, etc.
- Jupyter notebook at `materials-discovery/notebooks/guided_design_tutorial.ipynb`
- IPython display integration for HTML inline rendering

---

## Recommended Stack Additions

### Core Visualization Libraries

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `plotly` | `>=6.0` (current: 6.7.0 as of 2026-04-09) | Interactive 3D atomic site rendering, polyhedral cages, shell decomposition, orbit coloring | The only zero-install-overhead interactive 3D library that renders natively in Jupyter, exports self-contained HTML, and produces publication-linked PNGs via kaleido. `go.Scatter3d` + `go.Mesh3d` cover every needed 3D primitive. WebGL backend handles 10k+ points without lag. |
| `matplotlib` | `>=3.9` (current: 3.10.8) | Diffraction pattern plots, radial distribution function plots, Penrose tiling overlays, publication PDF/SVG export | The de facto standard for publication-quality 2D scientific figures. Supports LaTeX labels, vector PDF export, fine-grained control over axes/colorbars. Crystal structure tutorials in journals routinely use matplotlib for 2D panels. |
| `kaleido` | `>=1.0` (current November 2025 release) | Static PNG/SVG/PDF export from plotly figures for publication embedding | Required for `fig.write_image()`. As of plotly 6.x the old Orca engine is deprecated; kaleido 1.0+ is the only supported path. Chrome must be present — see Pitfalls. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `scipy` | `>=1.13` (current: 1.17.1) | `scipy.spatial.ConvexHull` for polyhedral cage face computation, `scipy.signal` for diffraction peak smoothing | Use when computing convex hull faces of atomic shells for `go.Mesh3d` cage rendering, or when smoothing powder-XRD curves for the diffraction plot panel. Already available in the Python 3.11 environment via transitive dependencies of `pymatgen`. |
| `nbformat` | `>=4.2.0` | Required by plotly for mime-type inline notebook rendering | Must be present when using plotly inside classic Jupyter Notebook (not only JupyterLab). Pin to `>=4.2.0` per plotly upstream requirement. |

### No New Libraries Required for These Features

| Feature | How to Implement | Source |
|---------|-----------------|--------|
| Penrose tiling overlay | Pure numpy + matplotlib `Polygon` patches — the de Bruijn multigrid dual method requires only trig and array ops | Training data + scipython.com patterns |
| Radial distribution function | numpy histogram + matplotlib bar chart, or `scipy.spatial.cKDTree` pairwise distances | scipy.spatial is already available |
| Crystal expansion / tiling | Repeat the `ZomicViewPoint` array by applying Z[phi] translation vectors — pure numpy, existing `zphi_geometry.py` math | Existing codebase |
| Orbit color legend | `matplotlib.patches.Patch` legend entries, same palette as `_ORBIT_PALETTE` in `raw_export.py` | Existing codebase |

---

## Installation

Add to `pyproject.toml` under a new `[project.optional-dependencies]` group:

```toml
[project.optional-dependencies]
# Add to existing file — new group only
viz = [
  "plotly>=6.0",
  "matplotlib>=3.9",
  "kaleido>=1.0",
  "nbformat>=4.2.0",
  "scipy>=1.13",
]
```

Install command:

```bash
cd materials-discovery
uv pip install -e ".[viz]"
```

`scipy` is already pulled in transitively by `pymatgen` in the `[mlip]` group. Include it
explicitly in `[viz]` anyway so the visualization group is self-contained for tutorial users
who do not need MLIP backends.

---

## Integration Points with Existing `materials_discovery.visualization`

The new plotly/matplotlib helpers should live in the existing module, not alongside it:

```
materials-discovery/src/materials_discovery/visualization/
    __init__.py          # already ships preview_raw_export, preview_zomic_design
    raw_export.py        # already ships RawExportViewModel, ZomicViewPoint, ZomicViewSegment
    viewer.py            # already ships HTML canvas viewer
    plotly_3d.py         # NEW: plotly scatter3d + mesh3d figures from RawExportViewModel
    matplotlib_pub.py    # NEW: diffraction pattern, RDF, Penrose overlay, shell panels
```

**Key integration contract:** Both new modules consume `RawExportViewModel` and the
`ZomicViewPoint`/`ZomicViewSegment` lists directly. They do not re-parse raw JSON — that
stays in `build_view_model()`. This keeps the geometry authority chain intact:

```
.zomic → export-zomic CLI → raw.json → build_view_model() → RawExportViewModel
                                                               ↓                  ↓
                                                         plotly_3d.py    matplotlib_pub.py
```

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| `plotly` Scatter3d + Mesh3d | `vtk` / `mayavi` | VTK requires a compiled C++ dependency and an X server — incompatible with headless CI and Jupyter-first tutorial use. Mayavi is largely unmaintained as of 2025. plotly's WebGL handles the scale we need (hundreds of atomic sites) without the setup cost. |
| `plotly` | `ipyvolume` | ipyvolume requires a separate JupyterLab extension install and has limited export path. plotly is zero-extension in modern Jupyter. |
| `matplotlib` for 2D panels | `bokeh` | bokeh is interactive-first and does not produce print-quality vector PDF/SVG as cleanly as matplotlib. Academic crystal structure papers exclusively use matplotlib. |
| `matplotlib` for 2D panels | `seaborn` | seaborn wraps matplotlib with statistical defaults; overkill and wrong semantic layer for physics plots (diffraction patterns, RDF). |
| `kaleido>=1.0` | Orca | Orca is deprecated in plotly 6.x and will be removed after September 2025. kaleido is the only supported static export path. |
| `scipy.spatial.ConvexHull` | `alphashape` | alphashape adds a separate dependency for a feature scipy already handles. Polyhedral cages in quasicrystals are convex, so `alphashape`'s concave-hull capability is not needed. |
| Custom Penrose tiling (numpy) | `PyQCstrc` | PyQCstrc is a research package (last stable 0.0.2a01, 2021) for 6D icosahedral structure modelling — far heavier than needed for an overlay illustration. The de Bruijn dual method is ~50 lines of numpy. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `vtk` / `mayavi` | Requires compiled C++ binaries, X server, and an incompatible install surface for a tutorial-first Python package. overkill for hundreds of atomic sites. | `plotly` go.Scatter3d + go.Mesh3d |
| `crystal-toolkit` (Dash app) | Requires a running Dash server — wrong model for a notebook tutorial that must run self-contained | `plotly` graph_objects figures rendered inline |
| `nglview` | JupyterLab extension required; adds widget backend dependency; molecular focus misaligns with quasicrystal geometry | `plotly` scatter3d |
| `ase` GUI / `vesta` wrappers | External binary dependency, no notebook path | matplotlib 3D axes or plotly |
| Orca (plotly static export) | Deprecated in plotly 6.x, removal announced September 2025 | `kaleido>=1.0` |
| `PyQCstrc` | Research-grade 2021 package, impractical install for a tutorial dependency, overkill for illustration | Custom numpy + matplotlib |
| `ipyvolume` | Requires extension install, limited export, less maintained than plotly | `plotly` |
| `dash` (full app) | Service-oriented, not notebook-native | `plotly` go.Figure inline display |

---

## Stack Patterns by Variant

**Interactive 3D atomic site plot (in notebook):**
- Use `plotly.graph_objects.Scatter3d` with one trace per orbit
- Color each trace using `_ORBIT_PALETTE` from `raw_export.py` so colors are identical
  between the existing HTML canvas viewer and the new plotly figure
- Set `marker.symbol='circle'`, `marker.size` proportional to atomic radius or fixed at 8
- Render with `fig.show(renderer='notebook')` for inline display

**Polyhedral cage (icosahedral shell):**
- Compute convex hull faces with `scipy.spatial.ConvexHull(shell_points).simplices`
- Pass vertex arrays and simplex i/j/k indices to `plotly.graph_objects.Mesh3d`
- Set `opacity=0.15` so interior sites remain visible through the cage face
- Overlay edge lines with a separate `go.Scatter3d` in `mode='lines'`

**Publication PNG export from plotly:**
- Call `fig.write_image("figure.png", scale=2)` after `import kaleido`
- Use `scale=2` for 2x resolution suitable for journal submission

**Diffraction pattern plot:**
- Use `matplotlib` with `ax.stem()` or `ax.vlines()` + `ax.plot()` for the envelope
- Index peaks with quasicrystal 6-index notation as x-axis tick labels
- Export with `fig.savefig("diffraction.pdf", bbox_inches='tight')`

**RDF plot:**
- Compute pairwise distances from `RawExportViewModel.points` coordinates using
  `scipy.spatial.cKDTree` or plain numpy broadcasting
- Bin with `numpy.histogram` into 0.1 Å bins
- Plot with `matplotlib` `ax.bar()` or `ax.step()`

**Penrose tiling overlay (2D projection):**
- Project 3D atomic positions onto the xy-plane
- Generate tiling background using de Bruijn dual method (numpy trig)
- Overlay with matplotlib `Polygon` patches at `alpha=0.3`
- Align tiling orientation to the 5-fold symmetry axis of the design

**Crystal expansion view:**
- Apply Z[phi] translation vectors using existing `phi_scale_coord` / `_translate_coord`
  from `zphi_geometry.py` to tile the motif outward by 1–2 shells
- Feed expanded point list into the same `go.Scatter3d` function
- Color by shell number (innermost = darkest) to show growth sequence

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `plotly>=6.0` | `kaleido>=1.0` | plotly 6.x requires kaleido 1.0+; older kaleido 0.x uses the deprecated Orca path |
| `plotly>=6.0` | `nbformat>=4.2.0` | plotly raises `ValueError` on mime-type rendering if nbformat is absent |
| `matplotlib>=3.9` | `numpy>=1.26.4` | Already required by the base project |
| `scipy>=1.13` | `numpy>=1.26.4` | Pulled in transitively via pymatgen; explicit pin ensures ConvexHull API stability |
| `kaleido>=1.0` | Chrome/Chromium | kaleido 1.0+ requires an installed Chrome binary; headless Chrome is used for rendering |

---

## Sources

- [plotly PyPI — 6.7.0 latest as of 2026-04-09](https://pypi.org/project/plotly/)
- [plotly Scatter3d API reference 6.6.0](https://plotly.github.io/plotly.py-docs/generated/plotly.graph_objects.Scatter3d.html)
- [plotly Mesh3d 3D mesh docs](https://plotly.com/python/3d-mesh/)
- [plotly static image export (kaleido 1.0)](https://plotly.com/python/static-image-export/)
- [plotly static image generation changes in 6.1](https://plotly.com/python/static-image-generation-changes/)
- [matplotlib release notes 3.10.8](https://matplotlib.org/stable/users/release_notes.html)
- [scipy 1.17.1 release notes](https://docs.scipy.org/doc/scipy/release.html)
- [scipy.spatial.ConvexHull docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.ConvexHull.html)
- [hofmann — ball-and-stick matplotlib crystal viewer with pymatgen interop](https://github.com/bjmorgan/hofmann)
- [PyQCstrc.ico — icosahedral QC modelling package (2021, research-grade)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8366420/)
- [Penrose tiling implementation (scipython.com)](https://scipython.com/blog/penrose-tiling-2/)
- [kaleido repo — Chrome requirement in v1.0](https://github.com/plotly/Kaleido)
- [plotly interactive HTML export](https://plotly.com/python/interactive-html-export/)
- [nbformat>=4.2.0 requirement (plotly issue #4512)](https://github.com/plotly/plotly.py/issues/4512)

---

*Stack research for: v1.82 illustrated tutorial and publication-quality quasicrystal visualization*
*Researched: 2026-04-15*
