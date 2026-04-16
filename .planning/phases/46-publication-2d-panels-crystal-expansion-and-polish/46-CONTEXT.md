# Phase 46: Publication 2D Panels, Crystal Expansion, and Polish - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

The notebook renders a complete set of 2D publication-quality panels (screening
scatter, RDF, diffraction) and a crystal expansion view. The full tutorial reads
as a coherent illustrated educational resource. Implements matplotlib_pub.py and
expansion.py (replacing Phase 45 stubs).

</domain>

<decisions>
## Implementation Decisions

### Matplotlib Figure Style
- Shared style dict in matplotlib_pub.py: sans-serif font, 300 DPI, removed top/right spines, pdf.fonttype=42
- Default figure size 6x4 inches for single panels, 10x4 for side-by-side
- Use ORBIT_COLORS from labels.py for shortlisted points, gray for non-shortlisted
- Inline rendering in notebook via fig.show(), save static PNG alongside for markdown tutorial reference

### Specific Figure Implementations
- RDF: compute from raw.json labeled_points pairwise distances using numpy broadcasting, bin at 0.1 Angstrom
- Diffraction: call existing simulate_powder_xrd.py on checked CandidateRecord from sc_zn_candidates.jsonl
- Screening scatter: read checked sc_zn_screened.jsonl directly (20 data points)
- Annotate RDF peaks with orbit shell names from SHELL_NAMES using vertical lines at computed mean radial distances

### Crystal Expansion View
- Replicate orbit-library sites at lattice vectors [a,0,0], [0,a,0], [0,0,a] using base_cell from design YAML
- Default 2x2x2 expansion (800 sites from 100 motif × 8 cells)
- Plotly Scatter3d with markers only (no bonds/cages), central cell highlighted with higher opacity
- Label as "periodic approximant tiling" with a note explaining the relationship to true QC

### the agent's Discretion
- Exact axis label wording and annotation placement at the agent's discretion
- Whether to combine RDF + diffraction into one side-by-side panel or keep separate
- How to handle the simulate_powder_xrd.py API integration if the call signature differs from expectations

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `labels.py`: ORBIT_COLORS, SHELL_NAMES, PREFERRED_SPECIES (Phase 44)
- `plotly_3d.py`: load_orbit_library(), orbit_figure(), shell_figure() (Phase 45)
- `expansion.py`: empty stub ready to implement (Phase 45)
- `matplotlib_pub.py`: empty stub ready to implement (Phase 45)
- `raw_export.py`: build_view_model, load_raw_export
- `sc_zn_screened.jsonl`: checked screening output (20 passed, 4 shortlisted)
- `sc_zn_all_validated.jsonl`: checked validation output
- `sc_zn_report.json`: checked report with release_gate
- `sc_zn_tsai_bridge.raw.json`: 52 labeled points for RDF
- `sc_zn_tsai_bridge.json`: orbit library for expansion
- `sc_zn_tsai_bridge.yaml`: base_cell a=13.7923 for expansion lattice vectors
- `diffraction/simulate_powder_xrd.py`: existing XRD simulation infrastructure

### Integration Points
- expansion.py replaces its stub; matplotlib_pub.py replaces its stub
- __init__.py may need updated exports for new functions
- Notebook sections 5, 6, and after section 10 need new figure cells
- Progress.md needs changelog entries

</code_context>

<specifics>
## Specific Ideas

- screening_scatter() should highlight the 4 shortlisted candidates with filled markers and the 16 non-shortlisted with hollow gray markers, with threshold lines for energy and distance proxies
- rdf_plot() should compute g(r) from the 52 raw.json labeled points and annotate the 5 shell peaks
- expansion_figure() should use plotly_3d-style orbit coloring for the central cell and desaturated versions for surrounding cells

</specifics>

<deferred>
## Deferred Ideas

- Publication SVG/PDF export via kaleido (VIZ-F01 — future)
- Animated rotation (VIZ-F02 — future)

</deferred>
