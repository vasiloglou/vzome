# Feature Research

**Domain:** Illustrated tutorial and publication-quality visualization for quasicrystal materials discovery (v1.82)
**Researched:** 2026-04-15
**Confidence:** HIGH (pipeline internals), MEDIUM (academic visualization conventions)

---

## Context: What Is Already Shipped

This research targets additive features for v1.82. The following are **already complete** and must not be rebuilt:

- Guided design tutorial markdown (`guided-design-tutorial.md`) with full operator command walkthrough
- Notebook companion (`guided_design_tutorial.ipynb`) with RUN_* flags, `preview_checked_design()`, artifact inspection cells
- Repo-owned HTML point/segment viewer (`viewer.py`, `preview-zomic` CLI command) rendered via Canvas 2D
- Zomic file syntax and export pipeline (`export-zomic`, `zomic_bridge.py`)
- Screening, validation, ranking, and report pipeline stages
- Same-system LLM companion lane documentation
- Translation and external benchmark branch documentation

The v1.82 gap: the tutorial reads as a command reference with minimal explanation of *why* commands exist or *what* the outputs mean physically. Visualizations are primitive (monochrome Canvas 2D wire-frame) compared to what the geometry data can support.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features without which the tutorial remains a command reference rather than an educational resource. "Users" here means: a researcher new to the Sc-Zn Tsai pipeline who opens the notebook or markdown page and needs to understand the design, not just reproduce commands.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Design-origin narrative for Sc-Zn Tsai bridge | Readers cannot understand *why* this design was chosen without a plain-language account of what Tsai-type clusters are, what the "bridge" motif does, and how the algorithm selected it. Academic tutorials (e.g., matgenb, JChemEd 2020 Penrose tiling paper) always open with conceptual framing before commands. | LOW | Markdown prose addition to section 2 of the guided tutorial. No new code. Depends on nothing new. |
| Annotated Zomic file walkthrough | The Zomic DSL is not documented anywhere accessible to newcomers. Academic DSL tutorials universally show annotated snippets with per-line or per-block callouts explaining what each construct does. Without this, the `sc_zn_tsai_bridge.zomic` file is opaque. | MEDIUM | Requires extracting representative Zomic snippet blocks from the checked file and adding sidebar annotations or HTML callout boxes in the notebook. Depends on existing `.zomic` file. |
| Plain-language screening explanation | `energy_proxy_ev_per_atom`, `min_distance_proxy`, `shortlist_rank`, and `passed_count` are printed as JSON but never explained. Readers cannot understand what the screening stage is doing or why proxy metrics matter. | LOW | Prose addition to section 5 of the tutorial and a corresponding notebook markdown cell. No new code. |
| Plain-language validation report explanation | The checked artifact shows `geometry_prefilter_pass: False`, `phonon_imaginary_modes: 99`, `md_stability_score: 0.0`, `xrd_confidence: 0.0`, and all release gates `False`. Without explanation, a newcomer reads this as "broken pipeline" rather than "honest batch with no promoted candidates." | LOW | Prose addition to section 6 and notebook section 7. The notebook already has a partial "How to Read the Current Evidence" cell — this deepens it. |
| Color-coded orbit visualization | Academic crystal structure figures (VESTA standard; IUCrJ 2016 Sc-Zn paper, PMC4937780) always assign distinct colors to inequivalent atomic sites or orbits. The current viewer renders all points identically without orbit-based color coding. The raw export already has orbit labels; the viewer discards them. | MEDIUM | Requires extending `build_view_model()` to pass orbit identity through to the renderer and mapping orbits to a color palette. Alternatively, implement in plotly/matplotlib as a new figure type. The 5 orbits (`tsai_zn7`, `tsai_sc1`, `tsai_zn6`, `tsai_zn5`, `tsai_zn4`) are already present in `sc_zn_tsai_bridge.json`. |
| Labeled axis and legend in figures | Publication-quality figures always have explicit axis labels, units, a title or caption, and a legend. The current Canvas viewer has no axes, no units, no color legend. Journal guidelines (IUCr Notes for Authors; Journal of Crystal Growth style guide) specify minimum 1.5-3 mm lettering height after reduction. | LOW | Achievable in matplotlib/plotly with standard `xlabel`, `ylabel`, `title`, `legend` calls. For the HTML Canvas viewer, a static legend overlay is sufficient. |
| LLM section with same explanatory depth | The same-system LLM lane and translation branch sections (notebook sections 8-10) contain commands and artifact-status dictionaries but almost no explanation of what the LLM evaluates, what `llm-evaluate` signals mean, or what the translation pipeline is doing. The markdown tutorial has the same gap. | MEDIUM | Prose additions only. No new code. Must stay within the scope of shipped commands without implying broader automation. |

### Differentiators (Competitive Advantage)

Features that would distinguish this tutorial from a standard command reference and from generic materials science Jupyter notebooks.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Shell-decomposed Tsai cluster figure | The defining visual of a Tsai-type icosahedral quasicrystal is a series of concentric polyhedral shells (tetrahedron, dodecahedron, icosahedron, icosidodecahedron, triacontahedron). The IUCrJ 2016 Sc-Zn paper (PMC4937780) uses this as Figure 1. No other tutorial in this repo shows the Sc-Zn Tsai bridge shell structure. This is the single figure that would make the tutorial recognizable to a quasicrystal specialist. | HIGH | Requires computing shell radii from `raw.json` labeled point coordinates and rendering each shell as a distinct plotly trace or matplotlib scatter. Depends on `build_view_model()` output and orbit labels. Must correctly attribute the 52 labeled points to their shells from the 5 known orbits. |
| Crystal expansion / tiling view | Quasicrystal tutorials (Wikipedia QC article, Euler CMU tutorial) always show the motif expanding outward — either as a 2D Penrose tiling or as a 3D cluster aggregate. This repo has no such figure. Showing how the Sc-Zn Tsai bridge motif tiles into a larger approximant structure would make the tutorial pedagogically unique. | HIGH | Requires using the generator's `site_positions.py` and approximant template logic to produce a tiled structure and plotting it. Depends on `CandidateRecord` output from `generate`. Not trivially derivable from the raw export alone. |
| Simulated diffraction pattern (2D projection) | Academic quasicrystal tutorials and papers (IUCrJ Sc-Zn paper Fig. 4; CMU Euler tutorial) always include a diffraction pattern showing fivefold symmetry. The repo already has `diffraction/simulate_powder_xrd.py` and `diffraction/compare_patterns.py`. An in-notebook simulated diffraction pattern using these would be unique and immediately recognizable to materials science readers. | MEDIUM | Depends on `hifi_digital/xrd_validate.py` and `diffraction/simulate_powder_xrd.py` being callable in notebook mode with `CandidateRecord` input. The repo already has infrastructure for this; needs a notebook-facing wrapper and matplotlib rendering. |
| Radial distribution function plot with annotated shell peaks | The RDF g(r) is a standard structural fingerprint in materials science papers. For a quasicrystalline approximant, shell peaks in the RDF directly correspond to the concentric cluster shells. A labeled g(r) plot with peak annotations (e.g., "inner shell ~2.8 Å", "icosahedron shell ~4.2 Å") would make the screening proxy metrics physically legible. | MEDIUM | Can be computed directly from the `raw.json` labeled point positions using numpy distance histograms. Does not require running the full pipeline. |
| Annotated screening proxy scatter plot | A 2D scatter of `energy_proxy_ev_per_atom` vs `min_distance_proxy` with shortlisted candidates highlighted and threshold boundaries drawn would make the screening stage visually comprehensible. This type of figure is standard in materials informatics papers. | LOW | Reads the checked `sc_zn_screened.jsonl` artifact. Simple matplotlib scatter with threshold lines. No new pipeline dependencies. |
| Interactive orbit-colored 3D scatter in notebook | Using `plotly.graph_objects.Scatter3d` with one trace per orbit, distinct colors, and hover text showing site label and orbit name would replace the current monochrome Canvas viewer for the notebook context. This aligns with standard practice in interactive materials science notebooks (matgenb style) and is directly achievable from the `raw.json` data. | MEDIUM | Depends on plotly being available (already in the dev environment given existing notebook usage). One implementation replaces the `EMBED_PREVIEW` HTML block in notebook section 4 with a plotly figure. Must be clearly scoped as a notebook visualization, not a replacement for the HTML viewer. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Realistic 3D polyhedral cage rendering with VESTA-style atom spheres | Looks impressive; VESTA is the publication standard for crystal structures | Requires either a heavy rendering dependency (PyOpenGL, VTK, or `ase.visualize.plot`) or a new always-on service. Contradicts the repo's constraint against mandatory desktop steps. VESTA itself is a closed GUI tool. | Use plotly `Scatter3d` with marker sizes and per-orbit colors for an approximation that works in-notebook without new heavy dependencies. |
| Animated GIF or video of rotating structure | Pedagogically appealing for showing 3D structure | Creates large binary assets, hard to version-control, requires imagemagick or ffmpeg as a runtime dependency. The existing HTML Canvas viewer already supports interactive rotation. | Keep the interactive HTML viewer. Add a note in the notebook that users can drag to rotate. |
| Full CIF-based Voronoi cell rendering | Common in periodic crystal tutorials | Voronoi cells for a quasicrystalline approximant are geometrically complex and aperiodic; the standard pymatgen `Structure.get_voronoi_neighbors` approach is incorrect for Zomic-native geometry. Would require implementing quasiperiodic Voronoi logic from scratch. | Show the polyhedral shell decomposition (concentric polyhedra) instead, which is the correct QC analog and is already partially supported by the orbit structure. |
| Live DFT or phonon calculation figure | Adds scientific credibility | Contradicts the project's explicit no-DFT constraint. Would imply the pipeline is DFT-backed when it is intentionally not. | Use the mock phonon validation output (`phonon_imaginary_modes: 99` from the checked artifact) with a clear annotation that these are proxy validation signals, not DFT results. |
| Penrose tiling 2D overlay on the geometry figure | Visually connects to QC theory | The Sc-Zn Tsai bridge is a 3D approximant, not a 2D Penrose tiling. Overlaying a 2D Penrose tiling would misrepresent the structural relationship and mislead readers about the geometry. | Explain in prose how 2D Penrose tilings and 3D icosahedral quasicrystals relate, cite the 3D Ammann rhombohedra, but do not overlay. Show the 3D cluster shell structure instead. |
| Standalone visualization microservice | Removes the notebook viewer dependency | Adds infrastructure the repo's constraint prohibits (no new always-on service). Duplicates the already-shipped HTML Canvas viewer. | Keep the existing `preview-zomic` CLI and HTML viewer as the non-notebook inspection path. Use plotly for the in-notebook figure. |

---

## Feature Dependencies

```
[Design-origin narrative]
    └── no dependencies (prose only, depends on existing docs)

[Plain-language screening explanation]
    └── no dependencies (prose only, reads checked screened.jsonl)

[Plain-language validation explanation]
    └── no dependencies (prose only, reads checked validated.jsonl)

[LLM section explanation depth]
    └── no dependencies (prose only, reads existing tutorial structure)

[Labeled axis/legend in figures]
    └── requires──> [Orbit-colored 3D scatter] OR [Shell-decomposed figure]

[Orbit-colored 3D scatter (plotly)]
    └── requires──> raw.json export with orbit labels (already exists)
    └── requires──> plotly (already available in dev environment)

[Annotated Zomic walkthrough]
    └── requires──> sc_zn_tsai_bridge.zomic (checked, already exists)

[Annotated screening proxy scatter]
    └── requires──> sc_zn_screened.jsonl (checked, already exists)
    └── requires──> matplotlib (already available)

[RDF plot with shell annotations]
    └── requires──> sc_zn_tsai_bridge.raw.json labeled point coordinates
    └── requires──> numpy for distance histogram (already available)

[Shell-decomposed Tsai cluster figure]
    └── requires──> orbit labels from raw.json or orbit-library JSON
    └── requires──> manual or computed shell-radius assignment per orbit
    └── enhances──> [Orbit-colored 3D scatter]

[Simulated diffraction pattern]
    └── requires──> diffraction/simulate_powder_xrd.py (already in repo)
    └── requires──> CandidateRecord from checked generate output
    └── requires──> matplotlib (already available)

[Crystal expansion / tiling view]
    └── requires──> generator/site_positions.py output
    └── requires──> at least one generated CandidateRecord with full site list
    └── requires──> matplotlib or plotly 3D (already available)
    └── enhances──> [Design-origin narrative]

[Design-origin narrative] ──enhances──> [Shell-decomposed Tsai cluster figure]
    (figure becomes legible only after prose establishes what shells are)

[Plain-language screening explanation] ──enhances──> [Annotated screening proxy scatter]
    (scatter becomes interpretable only after proxy metrics are explained in prose)
```

### Dependency Notes

- **Orbit-colored 3D scatter requires orbit labels from raw.json:** The checked `sc_zn_tsai_bridge.raw.json` already contains 52 labeled points; labels encode orbit names (e.g., `tsai_zn7`, `tsai_sc1`). The `build_view_model()` function already reads these but discards orbit identity before rendering. Extending it requires only a small change to pass orbit name through the view model.
- **Shell-decomposed figure requires shell-radius assignment:** The five orbits (`tsai_zn7`, `tsai_sc1`, `tsai_zn6`, `tsai_zn5`, `tsai_zn4`) correspond to distinct radial bands but the mapping from orbit name to physical shell (dodecahedron, icosahedron, icosidodecahedron, etc.) is not yet encoded in the repo. This mapping must be derived from radial distances in the `raw.json` output or documented manually from the IUCrJ 2016 Sc-Zn paper.
- **Crystal expansion view requires generate output:** The checked `sc_zn_candidates.jsonl` already contains generated candidate records with full site lists. The expansion view is derivable from these without rerunning the pipeline. However, interpreting the tiling geometry requires understanding the `approximant_templates.py` logic.
- **Simulated diffraction pattern requires pipeline output but can use checked artifacts:** `simulate_powder_xrd.py` needs a `CandidateRecord` or ASE Atoms input. The checked validated artifact contains this. The figure can be generated from the checked artifact without rerunning the pipeline.

---

## MVP Definition

### Launch With (v1.82 core)

Minimum set to transform the tutorial from a command reference into an educational resource. All of these either require no new code or extend trivially from existing infrastructure.

- [ ] Design-origin narrative for the Sc-Zn Tsai bridge — explains what the motif is, what Tsai-type clusters are, and why this design was selected. Prose only.
- [ ] Annotated Zomic file walkthrough — shows 3-6 representative Zomic syntax blocks with per-block callouts. Requires choosing representative excerpts; no new code.
- [ ] Plain-language screening explanation — explains what the proxy metrics mean, how the shortlist threshold works, and how to interpret `passed_count` vs `shortlisted_count`. Prose only.
- [ ] Plain-language validation report explanation — explains each gate in `release_gate`, why `phonon_imaginary_modes: 99` is a warning and not an error in the mock backend, and how to read `recommendation`. Prose only.
- [ ] LLM section explanatory depth — adds "what this signal means" prose to sections 8-10 of the notebook and the equivalent sections in the markdown tutorial. No new code.
- [ ] Annotated screening proxy scatter plot — 2D matplotlib scatter of `energy_proxy_ev_per_atom` vs `min_distance_proxy` with shortlisted candidates highlighted. Reads checked `screened.jsonl`. Low implementation cost.
- [ ] Orbit-colored 3D scatter in notebook — plotly `Scatter3d` with one trace per orbit, distinct colors, hover labels. Replaces the current monochrome HTML Canvas viewer in the notebook context. Reads `raw.json`.

### Add After Core Is Working (v1.82 enrichment)

Features to add once the core explanatory pass is complete and the orbit-colored figure is validated.

- [ ] Shell-decomposed Tsai cluster figure — labeled matplotlib figure showing each orbit at its radial shell, with orbit name annotations. Requires shell-radius assignment from `raw.json` distances.
- [ ] RDF plot with annotated shell peaks — g(r) derived from `raw.json` labeled point distances, with shell peak labels. Requires numpy distance histogram; approximately 20 lines of code.
- [ ] Simulated diffraction pattern — calls `simulate_powder_xrd.py` on the checked `CandidateRecord` and renders with matplotlib. Visualizes fivefold-symmetry signal.

### Future Consideration (v1.83+)

- [ ] Crystal expansion / tiling view — shows motif repeating into a larger approximant structure. Requires more pipeline integration; deferred until core explanatory pass is proven.
- [ ] Publication-quality static SVG/PDF figure export — uses matplotlib `savefig` with `pdf.fonttype=42` for journal submission. Useful once the figures are stable; not needed for the tutorial itself.

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Design-origin narrative | HIGH | LOW | P1 |
| Plain-language screening explanation | HIGH | LOW | P1 |
| Plain-language validation explanation | HIGH | LOW | P1 |
| LLM section explanatory depth | HIGH | LOW | P1 |
| Annotated Zomic file walkthrough | HIGH | MEDIUM | P1 |
| Annotated screening proxy scatter | HIGH | LOW | P1 |
| Orbit-colored 3D scatter (plotly) | HIGH | MEDIUM | P1 |
| Shell-decomposed Tsai cluster figure | HIGH | HIGH | P2 |
| RDF plot with shell peak annotations | MEDIUM | MEDIUM | P2 |
| Simulated diffraction pattern | MEDIUM | MEDIUM | P2 |
| Crystal expansion / tiling view | HIGH | HIGH | P3 |
| Publication-quality SVG/PDF export | LOW | LOW | P3 |

**Priority key:**
- P1: Must have for v1.82 launch — transforms command reference into educational resource
- P2: Should have — adds scientific depth and makes figures publication-grade
- P3: Nice to have — deferred until P1/P2 are proven stable

---

## Academic Visualization Standards (Research Findings)

These findings inform which features are "expected" by a materials science audience.

### What Academic Quasicrystal Papers Show

Based on the IUCrJ 2016 Sc-Zn paper (PMC4937780) and the research literature on Tsai-type clusters:

1. **Figure 1 in nearly every Tsai-cluster paper:** Successive concentric polyhedral shells drawn as wireframe or solid polyhedra with distinct colors per shell — tetrahedron (innermost), dodecahedron, icosahedron, icosidodecahedron, triacontahedron (outermost). This is the canonical "what is a Tsai cluster" figure. For Sc-Zn specifically: central Zn4 tetrahedron, Zn20 dodecahedron, Sc12 icosahedron, Zn30 icosidodecahedron, decorated outer shell.

2. **Figure 2 type:** 2D projection of the quasiperiodic tiling showing cluster linkage types (b-linkage, c-linkage). Hard to generate without tiling data; lower priority.

3. **Diffraction figures:** Cross-sections perpendicular to two-, three-, and fivefold axes showing Bragg peak positions. The repo has XRD simulation infrastructure but not oriented diffraction patterns.

4. **RDF plots:** Sharp peaks labeled with approximate distances and shell identities. Standard in structural analysis sections.

5. **Atomic projection slabs:** An N x M x P angstrom slab perpendicular to a symmetry axis with cluster shells outlined. Requires tiling data; lower priority.

### What Publication-Quality Means in This Context

From research on matplotlib best practices and the matgenb notebook collection:

- **Font:** Arial or similar sans-serif, minimum 10 pt after reduction to one-column width (8.8 cm in most journals per IUCr author guidelines)
- **DPI:** 300 dpi minimum for raster; prefer vector (SVG/PDF) for line art
- **Colors:** Colorblind-safe palette (e.g., IBM Carbon, Wong 2011 palette); no more than 5-6 distinct colors per figure; matplotlib rcParams for consistency
- **Axes:** Always labeled with units in parentheses ("Distance (A)", "Energy (eV/atom)")
- **Legend:** Inside or outside the axes frame; never overlapping data; per-orbit legends for crystal structure figures
- **Spines:** Remove top and right spines (`ax.spines['right'].set_visible(False)`) for cleaner appearance
- **Annotations:** Use `ax.annotate()` with arrowprops for peak labels; use `ax.text()` for region labels
- **Font type for export:** Set `mpl.rcParams['pdf.fonttype'] = 42` and `mpl.rcParams['ps.fonttype'] = 42` for Adobe Illustrator compatibility
- **Caption vs title:** In journals, figures have captions not titles; in notebooks, a short descriptive title above the figure is standard

### What Makes a Tutorial Publication-Quality vs Command Reference

From analysis of matgenb notebooks, Journal of Chemical Education quasicrystal tutorial (ACS 2019), and the "Notebooks Now!" Wiley publication:

| Command Reference | Publication-Quality Tutorial |
|-------------------|------------------------------|
| Shows the command | Explains why the command exists before showing it |
| Prints raw JSON output | Extracts the 2-3 meaningful fields and explains each |
| No figures | Has figures at every conceptual transition point |
| No narrative | Has a "Before you continue" or "What this means" section after each major result |
| Skips failures | Explains what an "expected failure" means and why it is informative |
| Assumes physics background | Defines domain terms on first use with a one-sentence definition |

The key structural pattern: **Explain the concept -> show the command -> show the output -> annotate the output.** The current tutorial does steps 2 and 3 but skips 1 and 4 almost entirely.

---

## Sources

- [Atomic structure and phason modes of the Sc-Zn icosahedral quasicrystal, IUCrJ 2016 (PMC4937780)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4937780/) — definitive Sc-Zn structural paper; source for shell decomposition conventions and figure types expected by specialists
- [Quasicrystals as cluster aggregates, Nature Materials 2004](https://www.nature.com/articles/nmat1244) — establishes cluster aggregate visualization as standard; Tsai-type shell nomenclature
- [Icosahedral cluster successive shells (ResearchGate figure)](https://www.researchgate.net/figure/Icosahedral-cluster-consisting-of-five-successive-shells-from-the-center-tetrahedron_fig1_236327440) — representative published Figure 1 format for Tsai clusters
- [Tsai-type icosahedral cluster concentric polyhedral shells (ResearchGate)](https://www.researchgate.net/figure/The-Tsai-type-icosahedral-cluster-composed-of-a-series-of-concentric-polyhedral-shells_fig1_257205730) — published figure format for the Tsai cluster type directly relevant to Sc-Zn
- [Tutorial on Describing, Classifying, and Visualizing Crystal Structures, ACS NanoSci Au 2024 (PMC11487663)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11487663/) — annotation and labeling conventions for crystal structure tutorials
- [Quasiperiodic Crystals: Teaching Aperiodicity with 3D-Printed Penrose Tiles, JChemEd 2020](https://pubs.acs.org/doi/10.1021/acs.jchemed.9b00702) — pedagogical structure for QC tutorials; conceptual-framing-before-commands pattern
- [matgenb: Materials Science Jupyter Notebooks (Materials Virtual Lab)](https://matgenb.materialsvirtuallab.org/) — standard for materials science notebook pedagogy; "newcomer should follow without difficulty" design principle
- [Making publication-quality figures in Python, Towards Data Science](https://towardsdatascience.com/making-publication-quality-figures-in-python-part-i-fig-and-axes-d86c3903ad9b/) — matplotlib conventions for publication figures; fonttype, DPI, spine removal
- [VESTA 3, J. Appl. Cryst. 2011 (Momma and Izumi)](https://onlinelibrary.wiley.com/doi/abs/10.1107/S0021889811038970) — dominant visualization tool in materials science; sets the color-per-site convention this milestone approximates
- [Plotly Python 3D Scatter documentation](https://plotly.com/python/3d-scatter-plots/) — implementation reference for orbit-colored 3D scatter
- [Penrose tiling Python package (xnx/penrose, GitHub)](https://github.com/xnx/penrose) — informs the anti-feature decision against 2D Penrose overlay on a 3D cluster
- [Notes for Authors of IUCrData, IUCr](https://iucrdata.iucr.org/x/services/notesforauthors.html) — journal figure sizing and lettering standards
- Internal: `materials-discovery/src/materials_discovery/visualization/viewer.py` — existing Canvas 2D renderer showing current orbit-color gap
- Internal: `materials-discovery/src/materials_discovery/diffraction/simulate_powder_xrd.py` — XRD simulation infrastructure for the simulated diffraction pattern figure
- Internal: `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json` — 52 labeled points and 52 segments; primary data source for all new figures

---

*Feature research for: v1.82 Illustrated Tutorial and Publication-Quality Visualization*
*Researched: 2026-04-15*
