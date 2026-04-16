# Requirements: Materials Design Program

**Defined:** 2026-04-15
**Core Value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.

## v1.82 Requirements

Requirements for the Illustrated Tutorial and Publication-Quality Visualization
milestone. Each maps to roadmap phases.

### Narrative

- [x] **NARR-01**: Tutorial explains what a Tsai-type icosahedral cluster is and why the Sc-Zn bridge design was chosen, with plain-language conceptual framing before any commands
- [x] **NARR-02**: Tutorial shows annotated Zomic file snippets with per-block explanations of geometry commands (size, symmetry, branch, from, label, short, color directions)
- [x] **NARR-03**: Tutorial explains what the screening stage does: what energy_proxy_ev_per_atom and min_distance_proxy measure, how the shortlist threshold works, and what passed_count vs shortlisted_count means
- [x] **NARR-04**: Tutorial explains each validation signal (geometry_prefilter, phonon_imaginary_modes, md_stability_score, xrd_confidence), the release gate logic, and how to read the recommendation field
- [x] **NARR-05**: Tutorial explains the same-system LLM lane and the translation/external benchmark branch with the same explanatory depth as the deterministic spine

### Visualization

- [x] **VIZ-01**: Notebook renders an interactive plotly 3D scatter with one trace per orbit, distinct colorblind-safe colors, hover labels showing site name and orbit
- [x] **VIZ-02**: Notebook renders a shell-decomposed Tsai cluster figure showing each concentric polyhedral shell as separate labeled layers with polyhedral cage wireframes
- [x] **VIZ-03**: Notebook renders a 2D matplotlib scatter of energy_proxy vs min_distance_proxy with shortlisted candidates highlighted and threshold boundaries
- [x] **VIZ-04**: Notebook renders a radial distribution function plot with shell-peak annotations derived from raw.json labeled point distances
- [x] **VIZ-05**: Notebook renders a simulated powder XRD diffraction pattern using existing pipeline infrastructure

### Enrichment

- [x] **ENRICH-01**: Orbit labels are mapped from cryptic names to intuitive human-readable names with a shared colorblind-safe palette used across all figures
- [ ] **ENRICH-02**: Notebook shows a crystal expansion view demonstrating how the Sc-Zn motif tiles into a larger periodic approximant structure
- [x] **ENRICH-03**: New visualization modules (plotly_3d.py, matplotlib_pub.py, labels.py, expansion.py) live inside materials_discovery.visualization and are installable via a [viz] optional dependency group

## Future Requirements

### Deferred from v1.82

- **VIZ-F01**: Publication-quality static SVG/PDF figure export via kaleido for journal submission
- **VIZ-F02**: Animated rotation GIF/video of 3D structure
- **NARR-F01**: Interactive Zomic syntax highlighting in notebook cells

## Out of Scope

| Feature | Reason |
|---------|--------|
| 2D Penrose tiling overlay on 3D structure | The Sc-Zn Tsai bridge is a 3D periodic approximant, not a 2D Penrose tiling — overlay would misrepresent the structure |
| VESTA-style realistic atom sphere rendering | Requires heavy rendering dependencies (VTK/PyOpenGL) incompatible with notebook-first constraint |
| Voronoi cell rendering | Quasiperiodic Voronoi cells are geometrically complex; standard pymatgen approach incorrect for Zomic-native geometry |
| Live DFT or phonon calculation figure | Contradicts the project's explicit no-DFT constraint |
| Standalone visualization microservice | Contradicts the repo's constraint against mandatory new services |
| New chemistry scope or training automation | This is a tutorial enrichment milestone, not a product expansion |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| NARR-01 | Phase 44 | Complete |
| NARR-02 | Phase 44 | Complete |
| NARR-03 | Phase 44 | Complete |
| NARR-04 | Phase 44 | Complete |
| NARR-05 | Phase 44 | Complete |
| ENRICH-01 | Phase 44 | Complete |
| VIZ-01 | Phase 45 | Complete |
| VIZ-02 | Phase 45 | Complete |
| ENRICH-03 | Phase 45 | Complete |
| VIZ-03 | Phase 46 | Complete |
| VIZ-04 | Phase 46 | Complete |
| VIZ-05 | Phase 46 | Complete |
| ENRICH-02 | Phase 46 | Pending |

**Coverage:**
- v1.82 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0

---
*Requirements defined: 2026-04-15*
*Last updated: 2026-04-15 after roadmap creation — all 13 requirements mapped to phases 44-46*
