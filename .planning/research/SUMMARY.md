# Research Summary: v1.82 Illustrated Tutorial and Publication-Quality Visualization

**Synthesized:** 2026-04-15
**Sources:** STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md

## Executive Summary

v1.82 is an educational enrichment milestone. The core pipeline works; the
problem is pedagogical — the tutorial shows commands and outputs but never
explains what outputs mean, why commands exist, or what the geometry looks like.
Academic quasicrystal tutorials follow: explain concept, show command, show
output, annotate output. The current tutorial does steps 2 and 3 but omits 1
and 4 almost entirely.

## Stack Additions

New `[viz]` optional dependency group (does not touch core pipeline):

| Library | Version | Purpose |
|---------|---------|---------|
| `plotly` | `>=6.0` | Interactive 3D orbit figures, polyhedral cages |
| `matplotlib` | `>=3.9` | 2D publication panels (RDF, diffraction, scatter) |
| `kaleido` | `>=1.0` | Static PNG/SVG/PDF export from plotly |
| `scipy` | `>=1.13` | ConvexHull for cages, cKDTree for RDF |
| `nbformat` | `>=4.2.0` | Required by plotly for notebook mime-type rendering |

Ruled out: vtk/mayavi, nglview, ipyvolume, crystal-toolkit/Dash, PyQCstrc.

## Feature Table Stakes (P1)

- Design-origin narrative (prose, LOW complexity)
- Annotated Zomic file walkthrough (prose + snippets, MEDIUM)
- Plain-language screening explanation (prose, LOW)
- Plain-language validation report explanation (prose, LOW)
- LLM section explanatory depth (prose, MEDIUM)
- Annotated screening proxy scatter (matplotlib, LOW)
- Orbit-colored 3D scatter in notebook (plotly, MEDIUM)

## Feature Differentiators (P2)

- Shell-decomposed Tsai cluster figure (plotly/matplotlib, HIGH)
- RDF plot with annotated shell peaks (matplotlib, MEDIUM)
- Simulated diffraction pattern (matplotlib, MEDIUM)

## Deferred (P3 / v1.83+)

- Crystal expansion / tiling view (HIGH complexity, needs generator output)
- Publication SVG/PDF export (stable figures first)
- 2D Penrose overlay (actively incorrect for this 3D periodic approximant)

## Architecture

Four new modules inside existing `materials_discovery.visualization`:

1. `plotly_3d.py` — orbit-colored Scatter3d, shell decomposition, Mesh3d cages
2. `matplotlib_pub.py` — screening scatter, validation dashboard, RDF, diffraction
3. `labels.py` — orbit-to-human-readable names, shared colorblind-safe palette
4. `expansion.py` — crystal motif tiling (2x2x2 default)

Key rules:
- plotly/matplotlib stay optional; core pipeline never imports them
- All visualization functions read-only on checked artifacts
- One orbit color scheme in `labels.py`, shared by all figures
- Shell assignment computed from mean radial distance, not hardcoded

## Top Pitfalls

1. **Plotly notebook bloat** — use `notebook_connected` renderer, limit 3-4 inline 3D figures
2. **Misleading approximant as QC** — label as "periodic approximant tiling," no Penrose overlay
3. **Label overcrowding** — labels off by default, show on hover, one representative per orbit
4. **Narrative drift** — derive claims programmatically from checked files
5. **Hardcoded shell assignment** — compute from radial distances, not IUCrJ paper copy

## Suggested Phase Structure (3 phases)

**Phase 1: Prose Enrichment and Zomic Annotation**
- Design narrative, Zomic walkthrough, screening/validation/LLM explanations
- `labels.py` module (only code)
- No dependencies, unblocks everything

**Phase 2: Interactive 3D Visualization with Plotly**
- `plotly_3d.py`, `[viz]` dependency group, notebook plotly cells
- Depends on Phase 1 (labels module)

**Phase 3: Publication 2D Panels and Polish**
- `matplotlib_pub.py`, `expansion.py`, static figure export
- Depends on Phase 2 (module structure)

## Watch Out For

- kaleido Chrome dependency in CI environments
- `simulate_powder_xrd.py` notebook API needs verification before Phase 3
- Crystal expansion tiling vectors need `approximant_templates.py` read
- Orbit-library JSON schema needs direct read before `plotly_3d.py`
