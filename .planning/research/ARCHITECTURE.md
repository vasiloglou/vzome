# Architecture Research: v1.82 Illustrated Tutorial and Publication-Quality Visualization

**Milestone:** `v1.82`
**Researched:** 2026-04-15
**Confidence:** HIGH for plotly/matplotlib integration, MEDIUM for crystal
expansion rendering approach.

## Executive Position

v1.82 adds two linked layers to the existing tutorial infrastructure:

1. **Prose enrichment** — design narrative, annotated Zomic walkthrough,
   plain-language screening/validation/LLM explanations
2. **Publication-quality visualization** — plotly 3D interactive figures,
   matplotlib 2D publication panels, intuitive labels, crystal expansion views

The architecture reuses the existing `materials_discovery.visualization` module
as the integration point and the checked raw export + orbit library as the data
sources. New visualization functions consume the same artifacts the current
HTML viewer already reads.

## Integration Points

### Existing artifacts consumed by new visualization

| Artifact | Path | New consumers |
|----------|------|---------------|
| Raw labeled geometry | `data/prototypes/generated/sc_zn_tsai_bridge.raw.json` | plotly 3D orbit figure, label redesign, expansion view |
| Orbit-library JSON | `data/prototypes/generated/sc_zn_tsai_bridge.json` | plotly orbit coloring, shell decomposition, polyhedral cages |
| Screened JSONL | `data/screened/sc_zn_screened.jsonl` | matplotlib screening scatter plot |
| Screen calibration | `data/calibration/sc_zn_screen_calibration.json` | screening explanation annotations |
| Validated JSONL | `data/hifi_validated/sc_zn_all_validated.jsonl` | matplotlib validation dashboard |
| Report JSON | `data/reports/sc_zn_report.json` | release gate visualization |
| Zomic source | `designs/zomic/sc_zn_tsai_bridge.zomic` | annotated code walkthrough (prose only) |
| Design YAML | `designs/zomic/sc_zn_tsai_bridge.yaml` | design parameter explanation (prose only) |

### Existing code modified

| Component | Modification |
|-----------|-------------|
| `materials_discovery/visualization/__init__.py` | Add exports for new plotly/matplotlib functions |
| `guided-design-tutorial.md` | Add narrative sections, Zomic annotations, figure references |
| `guided_design_tutorial.ipynb` | Add visualization cells, prose cells, expansion cells |

## New Components

### New modules inside `materials_discovery.visualization`

| Module | Purpose | Input | Output |
|--------|---------|-------|--------|
| `plotly_3d.py` | Interactive 3D atomic site and polyhedral cage rendering | `raw.json`, orbit-library `.json` | plotly `Figure` objects |
| `matplotlib_pub.py` | Publication-quality 2D panels (RDF, screening scatter, validation dashboard, diffraction) | screened/validated JSONL, raw.json | matplotlib `Figure` objects |
| `labels.py` | Intuitive label mapping from cryptic orbit labels to human-readable names | orbit-library `.json`, design YAML | label lookup dict |
| `expansion.py` | Crystal motif expansion/tiling into larger structure | raw.json, orbit-library `.json`, design YAML | expanded site coordinates for plotly rendering |

### Data flow

```text
raw.json ──────────────┬──> plotly_3d.orbit_figure()        -> interactive 3D orbit view
                       ├──> plotly_3d.shell_figure()         -> shell decomposition view
orbit-library.json ────┤──> plotly_3d.cage_figure()          -> polyhedral cage view
                       ├──> expansion.expand_motif()         -> expanded coordinates
                       │      └──> plotly_3d.expansion_figure()
                       └──> labels.intuitive_labels()        -> human-readable label map

screened.jsonl ────────┬──> matplotlib_pub.screening_scatter() -> energy vs distance scatter
screen_calibration ────┘

validated.jsonl ───────┬──> matplotlib_pub.validation_dashboard() -> multi-panel validation view
report.json ───────────┘──> matplotlib_pub.release_gate_panel()   -> gate status visualization

raw.json ──────────────┬──> matplotlib_pub.rdf_plot()        -> radial distribution function
                       └──> matplotlib_pub.diffraction_plot() -> simulated diffraction pattern
```

## Suggested Build Order

### Phase 1: Prose enrichment and Zomic annotation

**Dependencies:** None — works on existing artifacts
**Delivers:**
- Design-origin narrative (how the Sc-Zn Tsai bridge was conceived, why this design)
- Annotated Zomic file walkthrough (each block explained)
- Plain-language screening and validation explanations
- LLM section enrichment
- Intuitive label mapping (the `labels.py` module, needed before figures)

**Rationale:** The Features research found the tutorial gap is structural —
figures become uninterpretable without explanatory prose. This phase is low
complexity and unblocks everything else.

### Phase 2: Interactive 3D visualization with plotly

**Dependencies:** Phase 1 (labels module, narrative context)
**Delivers:**
- `plotly_3d.py` with orbit-colored Scatter3d, shell decomposition, polyhedral cage Mesh3d
- Notebook cells with inline plotly figures
- Markdown tutorial figure references
- `[viz]` optional dependency group in pyproject.toml

**Rationale:** The orbit-colored 3D figure is the single highest-impact visual
upgrade. Plotly renders inline in notebooks without extensions.

### Phase 3: Publication 2D panels, crystal expansion, and polish

**Dependencies:** Phase 2 (visualization module structure)
**Delivers:**
- `matplotlib_pub.py` with screening scatter, validation dashboard, RDF, diffraction
- `expansion.py` with motif tiling logic
- Crystal expansion plotly figure
- Static figure export for markdown tutorial
- Final label and color scheme polish

**Rationale:** The 2D panels and expansion view are the publication-quality
differentiators. They depend on the module structure from Phase 2 and the
narrative context from Phase 1.

## Architectural Seams

### 1. Keep plotly and matplotlib optional

Add them under a `[viz]` extra in pyproject.toml. The core pipeline must not
break if visualization dependencies are not installed. Guard imports with
try/except in the notebook.

### 2. Keep visualization read-only on checked artifacts

The new visualization functions must only read existing artifacts. They must not
re-run pipeline stages, mutate data files, or require live pipeline execution
to produce figures.

### 3. One orbit color scheme shared across all figures

Define the orbit-to-color mapping once in `labels.py` and reuse it in both
plotly and matplotlib figures. Use a colorblind-safe palette (e.g., Wong 2011
or Tol's qualitative scheme).

### 4. Shell assignment from radial distance

The 5 orbits in the orbit library map to concentric Tsai cluster shells. The
shell assignment should be computed from mean radial distance of each orbit's
sites relative to motif center, not hardcoded. This keeps it correct if the
design changes.

### 5. Expansion uses existing geometry math

Crystal expansion replicates the motif at lattice translation vectors using the
base_cell parameters from the design YAML. The `zphi_geometry.py` module
already has relevant icosahedral math. Keep expansion modest (2x2x2 or 3x3x3)
to avoid performance issues.
