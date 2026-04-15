# Phase 41: Programmatic Visualization Artifact and Library Surface - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 41 gives the checked Sc-Zn design one repo-owned way to refresh its
visualization artifact and one stable programmatic render path that later docs
and notebook work can reuse.

This phase should deliver:

- one documented refresh path for the checked visualization artifact with no
  manual desktop-export step in the happy path
- one standalone programmatic visualization surface that Phase 42 and Phase 43
  can call directly
- a narrow, tutorial-first implementation that stays file-backed and local

This phase does not replace desktop vZome, create a general visualization
platform, or add browser/service authoring parity.

</domain>

<decisions>
## Implementation Decisions

### Official input artifact
- **D-01:** Treat the checked `*.raw.json` labeled-geometry export produced by
  `mdisc export-zomic` as the official Phase 41 visualization input.
- **D-02:** Keep richer `.vZome` and `.shapes.json` compatibility out of the
  MVP path and treat it as future expansion after the tutorial-first library is
  stable.

### Library surface
- **D-03:** Make the primary usage path Python-first so the tutorial and
  notebook can render the checked design through a direct helper call.
- **D-04:** Back that Python usage path with a small reusable JavaScript
  rendering layer instead of introducing a long-running visualization service
  as the default architecture.

### Visual fidelity
- **D-05:** Optimize for readable tutorial geometry first: points, segments,
  and orbit or label semantics are required; desktop-level vZome parity is not.
- **D-06:** Treat still-image capture or export as optional follow-on work if
  it comes cheaply from the chosen surface. Interactive rendering is the
  required MVP behavior.

### Artifact refresh and operator flow
- **D-07:** Reuse `uv run mdisc export-zomic --design ...` as the official
  artifact refresh path unless a paper-thin helper is needed solely for the
  checked tutorial ergonomics.
- **D-08:** Keep the visualization surface small enough that later tutorial and
  notebook work can consume it without turning Phase 41 into a general-purpose
  visualization project.

### the agent's Discretion
- Exact package and module naming for the Python helper and JavaScript layer
- Whether the thin JavaScript layer lives entirely under
  `materials-discovery/` or reuses small pieces from `online/`
- Styling details that improve tutorial readability without implying desktop
  parity

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` - current milestone scope and active constraints
- `.planning/REQUIREMENTS.md` - `VIS-01` and `VIS-02`, plus explicit v2
  deferrals
- `.planning/ROADMAP.md` - Phase 41 goal, success criteria, and scope
  boundaries
- `.planning/STATE.md` - current execution position and prior milestone
  decisions

### Prior tutorial and milestone decisions
- `.planning/milestones/v1.7-phases/39-guided-design-evaluation-and-visualization-tutorial/39-CONTEXT.md`
  - locked the Sc-Zn tutorial spine and the geometry authority chain
- `.planning/milestones/v1.8-phases/40-llm-narrative-enrichment-and-notebook-tutorial-conversion/40-CONTEXT.md`
  - locked the notebook as a companion artifact and kept the tutorial
  deterministic path primary

### Current docs and checked walkthrough assets
- `materials-discovery/developers-docs/guided-design-tutorial.md` - current
  tutorial section that still hands the user off to desktop vZome
- `materials-discovery/notebooks/guided_design_tutorial.ipynb` - notebook
  companion that currently mirrors the same manual visualization handoff
- `materials-discovery/developers-docs/zomic-design-workflow.md` - existing
  raw-export and orbit-library contract for Zomic-backed prototypes
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml` - checked design
  config that drives the export
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic` - editable
  geometry source
- `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json`
  - checked labeled-geometry export chosen as the MVP viewer input
- `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json` -
  checked orbit-library JSON that remains downstream of the raw export

### Existing export and viewer code
- `materials-discovery/src/materials_discovery/cli.py` - `mdisc export-zomic`
  command surface and CLI conventions
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py` -
  export bridge, default output paths, and file-backed artifact rules
- `core/src/main/java/com/vzome/core/apps/ExportZomicLabeledGeometry.java` -
  source of the checked raw labeled-geometry JSON contract
- `core/src/main/java/com/vzome/core/exporters/ShapesJsonExporter.java` -
  richer preview export path that remains future-facing for this milestone
- `online/developer-docs/architecture.md` - browser viewer supports viewing
  `.vZome` and `.shapes.json`, which constrains what can be reused directly
- `online/src/wc/vzome-viewer.js` - reusable web-component surface with
  `loadFromText`, `captureImage`, and `exportText`
- `online/src/worker/vzome-worker-static.js` - current worker-side loading and
  export behavior for `.vZome` and `.shapes.json`
- `online/src/viewer/context/viewer.jsx` - exported format list and viewer
  contracts relevant to any thin reuse

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `export_zomic_design()` and `mdisc export-zomic` already refresh both the raw
  export and the orbit-library JSON from the checked `.zomic` source.
- `ExportZomicLabeledGeometry.java` already emits the data needed for a
  tutorial-first renderer: labeled points, cartesian coordinates, and segments.
- `vzome-viewer` already offers a reusable browser component and image/export
  hooks, even though its current direct inputs are `.vZome` and `.shapes.json`
  rather than the raw labeled-geometry export.

### Established Patterns
- `materials-discovery/` is CLI-first, file-backed, and deterministic about
  output locations and JSON summaries.
- Tutorial and notebook surfaces are additive explanations over checked repo
  artifacts, not separate runtime products.
- The current milestone explicitly avoids a default long-running service and
  avoids broad product expansion while documentation is the driver.

### Integration Points
- Phase 41 should land a surface that Phase 42 can document in
  `guided-design-tutorial.md` and Phase 43 can call from
  `guided_design_tutorial.ipynb`.
- If the primary API is Python-first, it should be easy to invoke from the
  notebook and easy to wrap in a tutorial helper snippet.
- Any thin JavaScript layer should be narrow enough to live beside the
  materials-discovery workflow without creating a second visualization product
  track.

</code_context>

<specifics>
## Specific Ideas

- Render the checked Sc-Zn raw export directly instead of telling the user to
  open desktop vZome for the tutorial happy path.
- Prefer an embeddable render surface that a notebook can show inline and that
  docs can link to or launch predictably.
- Keep `.vZome` and `.shapes.json` compatibility visible as future work, not as
  hidden Phase 41 scope.

</specifics>

<deferred>
## Deferred Ideas

- Full `.vZome` and `.shapes.json` share compatibility as the primary tutorial
  path
- A long-running visualization backend or server-managed rendering flow
- Browser-side editing or broader desktop-vZome feature parity
- A generalized materials visualization platform beyond the checked Sc-Zn
  tutorial use case

</deferred>

---

*Phase: 41-programmatic-visualization-artifact-and-library-surface*
*Context gathered: 2026-04-15*
