# Phase 44: Prose Enrichment and Zomic Annotation - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Readers can understand why the Sc-Zn Tsai bridge design was chosen, how each
Zomic block works, what the screening metrics mean, how to read the validation
report, and how the LLM lane relates to the deterministic spine — all before
running a single command. This phase also creates the shared `labels.py` orbit
label module that all later visualization phases depend on.

Deliverables: prose additions to `guided-design-tutorial.md` and
`guided_design_tutorial.ipynb`, plus the `labels.py` module inside
`materials_discovery.visualization`.

</domain>

<decisions>
## Implementation Decisions

### Narrative Structure and Placement
- Design-origin narrative goes before Section 2 "Know the Worked Example" so readers get the "why" before seeing file paths and authority chains
- Tsai cluster explanation is one paragraph explaining concentric polyhedral shells plus one figure reference — enough to understand the design without a crystallography lecture
- Markdown gets full prose; notebook gets condensed versions linking to the markdown for depth — follows the v1.81 convention
- Cite the IUCrJ 2016 Sc-Zn paper (PMC4937780) once for the shell structure and link it — grounds the tutorial in real science

### Zomic Annotation Style
- Show 3-4 annotated blocks from the checked `sc_zn_tsai_bridge.zomic` file with inline `# ← explanation` comments on key lines
- Each block annotation names the physical result ("builds the pentagonal ring", "adds frustum connectors")
- Introduce a label glossary table mapping cryptic names (pent, frustum, joint) to physical parts before the first snippet — this glossary becomes the foundation for labels.py

### Screening, Validation, and LLM Explanation Depth
- One paragraph per screening metric defining what it measures physically, then a "What the numbers mean" callout after the screening output
- Frame the "all gates False" validation result as "this is what an honest early-stage batch looks like" with a checklist explaining each gate
- One explain-then-command-then-annotate block per LLM command (llm-generate, llm-evaluate, llm-translate) — same depth as the deterministic spine
- labels.py encodes preferred_species_by_orbit from the design YAML plus a human-readable shell name per orbit

### the agent's Discretion
- Exact wording and paragraph lengths at the agent's discretion
- Ordering of explanatory blocks within each section at the agent's discretion

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials_discovery/visualization/__init__.py` exports preview_raw_export, preview_zomic_design
- `materials_discovery/visualization/raw_export.py` has `_ORBIT_PALETTE`, `ZomicViewPoint`, `ZomicViewSegment`, `build_view_model`
- `_infer_orbit_name` in `zomic_bridge.py` already maps labels to orbit names
- Existing `_ORBIT_PALETTE` defines 8 colors — must be replaced or extended with colorblind-safe palette in labels.py

### Established Patterns
- Tutorial follows: section heading → brief intro → code block → output dict → next section
- Notebook uses markdown cells for prose, code cells for execution/inspection
- Design YAML at `designs/zomic/sc_zn_tsai_bridge.yaml` has `preferred_species_by_orbit` mapping `pent: [Sc, Zn]`, `frustum: [Zn, Sc]`, `joint: [Zn]`

### Integration Points
- `guided-design-tutorial.md` sections 1-12 need enrichment
- `guided_design_tutorial.ipynb` cells need corresponding narrative additions
- New `labels.py` module sits inside `materials_discovery/visualization/` alongside `raw_export.py` and `viewer.py`
- `__init__.py` must export the new label functions

</code_context>

<specifics>
## Specific Ideas

- The Zomic file has 3 natural blocks to annotate: (1) outer frame with `size`, `symmetry`, (2) pentagonal ring via `branch`/`from`/`short`/`label`, (3) frustum connectors and joint labels
- The 5 orbits in the orbit library are `tsai_zn7`, `tsai_sc1`, `tsai_zn6`, `tsai_zn5`, `tsai_zn4` — these map to concentric Tsai cluster shells
- Use Wong (2011) colorblind-safe palette for the orbit color scheme in labels.py

</specifics>

<deferred>
## Deferred Ideas

- Interactive Zomic syntax highlighting (NARR-F01) — captured as future requirement
- Full crystallographic Wyckoff site labels — overkill for this tutorial

</deferred>
