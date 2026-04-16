# Roadmap: Materials Design Program

## Overview

`v1.81` is shipped and archived. The active milestone is v1.82 — Illustrated
Tutorial and Publication-Quality Visualization. This milestone enriches the
tutorial and notebook from a command-reference walkthrough into a richly
illustrated, self-explanatory educational resource with publication-quality
graphics. Phases 44-46 continue the continuous numbering from v1.81's Phase 43.

## Milestones

- ✅ **v1.6 Translator-Backed External Materials-LLM Benchmark MVP** - Phases
  34-36 (shipped 2026-04-07)
- ✅ **v1.7 Documentation Refresh and Guided Design Tutorial MVP** - Phases
  37-39 (shipped 2026-04-15; archive: `milestones/v1.7-ROADMAP.md`)
- ✅ **v1.8 LLM Narrative Enrichment and Notebook Tutorial MVP** - Phase 40
  (shipped 2026-04-15; archive: `milestones/v1.8-ROADMAP.md`)
- ✅ **v1.81 Extensive LLM Tutorial and Programmatic vZome Visualization
  MVP** - Phases 41-43 (shipped 2026-04-15; archive:
  `milestones/v1.81-ROADMAP.md`)
- 🚧 **v1.82 Illustrated Tutorial and Publication-Quality Visualization** -
  Phases 44-46 (in progress)

## Phases

<details>
<summary>✅ v1.0 through v1.81 (Phases 1-43) - SHIPPED</summary>

See archive pointers below for details on phases 1-43.

</details>

### 🚧 v1.82 Illustrated Tutorial and Publication-Quality Visualization (In Progress)

**Milestone Goal:** Transform the guided design tutorial (notebook + markdown)
from a command-reference walkthrough into a richly illustrated, self-explanatory
educational resource with publication-quality graphics.

- [x] **Phase 44: Prose Enrichment and Zomic Annotation** - Conceptual framing, annotated Zomic walkthrough, plain-language screening and validation explanations, and the shared orbit label module (completed 2026-04-16)
- [x] **Phase 45: Interactive 3D Visualization with Plotly** - Orbit-colored 3D scatter, shell-decomposed Tsai cluster figure, and the [viz] optional dependency group (completed 2026-04-16)
- [ ] **Phase 46: Publication 2D Panels, Crystal Expansion, and Polish** - Screening proxy scatter, RDF plot, simulated diffraction pattern, and crystal expansion tiling view

## Phase Details

### Phase 44: Prose Enrichment and Zomic Annotation
**Goal**: Readers can understand why the Sc-Zn Tsai bridge design was chosen, how each Zomic block works, what the screening metrics mean, how to read the validation report, and how the LLM lane relates to the deterministic spine — all before running a single command
**Depends on**: Phase 43 (v1.81 shipped preview surface and notebook)
**Requirements**: NARR-01, NARR-02, NARR-03, NARR-04, NARR-05, ENRICH-01
**Success Criteria** (what must be TRUE):
  1. A reader opening the tutorial encounters a plain-language explanation of what a Tsai-type icosahedral cluster is and why the Sc-Zn design was chosen before any command appears
  2. Each Zomic file block in the tutorial has an inline annotation that names the command (size, symmetry, branch, from, label, short, color) and describes what it contributes to the structure
  3. The screening section explains what energy_proxy_ev_per_atom and min_distance_proxy measure, how the shortlist threshold selects candidates, and what passed_count vs shortlisted_count means
  4. The validation section explains each signal (geometry_prefilter, phonon_imaginary_modes, md_stability_score, xrd_confidence), the release gate logic, and how to read the recommendation field
  5. The LLM lane and translation/external benchmark branch sections carry the same explain-then-command-then-annotate depth as the deterministic spine, and a shared colorblind-safe orbit palette is defined in labels.py
**Plans**: 3 plans
Plans:
- [x] 44-01-PLAN.md — Shared orbit label module (labels.py) with colorblind-safe palette and unit tests
- [x] 44-02-PLAN.md — Design-origin narrative and annotated Zomic walkthrough in tutorial
- [x] 44-03-PLAN.md — Screening, validation, and LLM prose enrichment in tutorial
**UI hint**: no

### Phase 45: Interactive 3D Visualization with Plotly
**Goal**: The notebook renders interactive publication-quality 3D figures showing orbit-colored atomic sites and shell-decomposed Tsai cluster layers, backed by an installable [viz] optional dependency group
**Depends on**: Phase 44
**Requirements**: VIZ-01, VIZ-02, ENRICH-03
**Success Criteria** (what must be TRUE):
  1. Running the notebook produces an interactive plotly 3D scatter where each orbit has a distinct colorblind-safe color and hovering a site shows its name and orbit
  2. Running the notebook produces a shell-decomposed Tsai cluster figure where each concentric polyhedral shell appears as a separate labeled layer with polyhedral cage wireframes
  3. The visualization modules (plotly_3d.py, matplotlib_pub.py, labels.py, expansion.py) live inside materials_discovery.visualization and are importable after pip install "materials-discovery[viz]"
  4. The core pipeline never imports plotly or matplotlib — the [viz] group remains strictly optional
**Plans**: 2 plans
Plans:
- [x] 45-01-PLAN.md — plotly_3d.py module with orbit_figure/shell_figure, matplotlib_pub.py stub, [viz] extra group, and unit tests
- [x] 45-02-PLAN.md — Notebook integration with plotly figure cells in Section 4 and visual verification
**UI hint**: yes

### Phase 46: Publication 2D Panels, Crystal Expansion, and Polish
**Goal**: The notebook renders a complete set of 2D publication-quality panels (screening scatter, RDF, diffraction) and a crystal expansion view, and the full tutorial reads as a coherent illustrated educational resource
**Depends on**: Phase 45
**Requirements**: VIZ-03, VIZ-04, VIZ-05, ENRICH-02
**Success Criteria** (what must be TRUE):
  1. Running the notebook produces a 2D matplotlib scatter of energy_proxy vs min_distance_proxy with shortlisted candidates highlighted and threshold boundary lines visible
  2. Running the notebook produces a radial distribution function plot with annotated shell-peak markers derived from raw.json labeled point distances
  3. Running the notebook produces a simulated powder XRD diffraction pattern using existing pipeline infrastructure
  4. Running the notebook produces a crystal expansion view showing how the Sc-Zn motif tiles into a larger periodic approximant structure (2x2x2 default)
**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 44 → 45 → 46

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 44. Prose Enrichment and Zomic Annotation | v1.82 | 3/3 | Complete    | 2026-04-16 |
| 45. Interactive 3D Visualization with Plotly | v1.82 | 2/2 | Complete   | 2026-04-16 |
| 46. Publication 2D Panels, Crystal Expansion, and Polish | v1.82 | 0/TBD | Not started | - |

## Archive Pointers

- `.planning/milestones/v1.81-ROADMAP.md`
- `.planning/milestones/v1.81-REQUIREMENTS.md`
- `.planning/milestones/v1.81-phases/`
- `.planning/v1.81-MILESTONE-AUDIT.md`
