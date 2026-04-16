# Phase 45: Interactive 3D Visualization with Plotly - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

The notebook renders interactive publication-quality 3D figures showing
orbit-colored atomic sites and shell-decomposed Tsai cluster layers, backed
by an installable [viz] optional dependency group. New modules `plotly_3d.py`
and a stub `matplotlib_pub.py` live inside `materials_discovery.visualization`.

</domain>

<decisions>
## Implementation Decisions

### Plotly 3D Figure Design
- Import ORBIT_COLORS from labels.py (Phase 44 output) — one Scatter3d trace per anchor-library orbit name
- Hover text shows: site label + orbit name + species + shell name (e.g. "pent.top.center (tsai_zn7) - Zn/Sc - Pentagonal ring")
- Labels OFF by default, show on hover — prevents overcrowding of 52 points
- Uniform marker size=8 for all sites — clean, readable

### Shell Decomposition and Cage Rendering
- Assign orbits to shells by computing mean radial distance of each orbit's sites from motif_center (from design YAML), sorted ascending
- Render polyhedral cages with scipy.spatial.ConvexHull for each shell → Mesh3d with opacity=0.15 + edge lines overlay
- Shells toggleable via plotly updatemenus or separate traces with legendgroup
- Two separate plotly figures: orbit-colored scatter (all 52 points) and shell-decomposed figure (layers + cages)

### Module Structure and Dependencies
- New modules inside materials_discovery/visualization/: plotly_3d.py (functional), matplotlib_pub.py (empty stub for Phase 46)
- try/except ImportError at module top with clear "install materials-discovery[viz]" error message
- New [viz] optional-dependencies group in pyproject.toml: plotly>=6.0, matplotlib>=3.9, kaleido>=1.0, scipy>=1.13, nbformat>=4.2.0
- Replace current EMBED_PREVIEW HTML block in notebook with plotly figure cells, keeping EMBED_PREVIEW as fallback when plotly is not installed

### the agent's Discretion
- Exact plotly layout parameters (camera angle, axis labels, title text) at the agent's discretion
- Whether to add plotly_3d helper functions to __init__.py or keep them as direct imports from plotly_3d
- Number of helper functions vs monolithic orbit_figure() / shell_figure() at agent's discretion

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `labels.py` (Phase 44 output): ORBIT_LABELS, SHELL_NAMES, ORBIT_COLORS, PREFERRED_SPECIES, DEFAULT_ORBIT_COLOR
- `raw_export.py`: ZomicViewPoint, ZomicViewSegment, RawExportViewModel, build_view_model, load_raw_export
- `viewer.py`: preview_raw_export, preview_zomic_design (HTML renderer — keeps working as fallback)
- `sc_zn_tsai_bridge.yaml`: motif_center=[0.5, 0.5, 0.5], base_cell a=b=c=13.7923
- `sc_zn_tsai_bridge.raw.json`: 52 labeled_points, 52 segments
- `sc_zn_tsai_bridge.json` (orbit library): 5 orbits with site data

### Established Patterns
- RawExportViewModel is the standard data source for all visualization
- build_view_model() parses raw.json → typed objects
- _infer_orbit_name() in zomic_bridge.py maps labels to orbit names

### Integration Points
- Notebook Section 4 "Programmatic Preview" is where plotly figures replace/augment the HTML viewer
- __init__.py needs updated exports for new plotly_3d functions
- pyproject.toml needs [viz] extra group

</code_context>

<specifics>
## Specific Ideas

- The orbit_figure function should accept a RawExportViewModel and return a plotly Figure
- The shell_figure function should accept a RawExportViewModel plus the orbit library data and return a plotly Figure with toggleable shell layers
- Use `fig.show(renderer="notebook_connected")` for CDN-based plotly.js loading to avoid notebook bloat

</specifics>

<deferred>
## Deferred Ideas

- matplotlib 2D panels (Phase 46)
- Crystal expansion view (Phase 46)
- Static PNG/SVG export via kaleido (future)

</deferred>
