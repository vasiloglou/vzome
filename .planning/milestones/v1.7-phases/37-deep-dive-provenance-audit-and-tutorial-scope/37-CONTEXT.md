# Phase 37: Deep-Dive Provenance Audit and Tutorial Scope - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 37 establishes the evidence base and scope lock for the `v1.7`
documentation milestone.

This phase should deliver:

- git-backed provenance for
  `materials-discovery/developers-docs/podcast-deep-dive-source.md`,
  including when it was created, where it moved, and what major shipped
  workflow surfaces landed after the first draft
- an explicit list of stale or missing capability claims that Phase 38 must
  correct in the refreshed narrative
- one tutorial anchor path that later phases can build around without drifting
  across too many systems, modes, or example documents

This phase does not rewrite the deep-dive source itself and does not yet author
the tutorial content. It fixes the scope, evidence posture, and example path so
later work stays honest and bounded.

</domain>

<decisions>
## Implementation Decisions

### Narrative boundary
- **D-01:** The refreshed deep-dive source should remain a high-level external
  narrative, not become a standalone exhaustive operator manual.
- **D-02:** The narrative should cross-link the current runbooks and reference
  docs instead of duplicating their full procedural detail.
- **D-03:** The refresh must explicitly cover the shipped workflow surface
  through `v1.6`, not stop at the earlier seven-stage core pipeline.

### Evidence and freshness policy
- **D-04:** Capability claims in the refreshed deep-dive source should be
  backed by shipped planning artifacts, current docs, or git history.
- **D-05:** Planned or future capabilities must be labeled explicitly as future
  work rather than blended into current-state prose.
- **D-06:** Quantitative claims that drift quickly, such as commit counts or
  module counts, should either be refreshed from the repo or softened so the
  document does not go stale immediately again.

### Tutorial anchor example
- **D-07:** The tutorial should center one reproducible Sc-Zn Zomic-backed
  example because it connects design authoring, pipeline execution, and
  vZome/Zomic visualization in one path.
- **D-08:** The default tutorial path should optimize for reproducibility and
  operator learning first, using the checked example config and design assets
  before any optional real/native follow-on notes.
- **D-09:** Broader chemistry coverage should be deferred rather than packing
  multiple worked examples into the first tutorial.

### Tutorial walkthrough shape
- **D-10:** The tutorial should be a step-by-step operator walkthrough with
  concrete commands, expected artifact locations, and interpretation checkpoints
  after each major stage.
- **D-11:** The tutorial must explain how to read screening, validation,
  ranking, and report artifacts, not just how to run commands.
- **D-12:** The visualization section should point to the exact Zomic design and
  export artifacts that remain the geometry authority for the worked example.

### the agent's Discretion
- Exact document naming and where the tutorial lives within
  `materials-discovery/developers-docs/`
- Whether tables, diagrams, or screenshots are worth adding if they clarify the
  shipped workflow without requiring new product work
- Exact balance of prose, callouts, and command blocks in the tutorial

</decisions>

<specifics>
## Specific Ideas

- The user explicitly wants to refresh
  `materials-discovery/developers-docs/podcast-deep-dive-source.md` because it
  may be stale relative to what has shipped since it was written.
- The user explicitly wants one nice tutorial with examples and step-by-step
  instructions for using the current tool to design new materials, evaluate
  their properties, and visualize them with the vZome/Zomic toolchain.
- The tutorial should feel like one coherent workflow rather than disconnected
  command reference fragments.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` — `v1.7` milestone framing, active goals, and current
  boundaries for documentation-first work
- `.planning/REQUIREMENTS.md` — `DOC-01`, `DOC-02`, `DOC-03`, `OPS-19`,
  `OPS-20`, and `OPS-21` as the governing requirements for this milestone
- `.planning/ROADMAP.md` — Phase 37-39 scope, dependencies, and success
  criteria
- `.planning/STATE.md` — current milestone state and handoff into Phase 37

### Current narrative and operator docs
- `materials-discovery/developers-docs/podcast-deep-dive-source.md` — existing
  long-form narrative source to audit and refresh
- `materials-discovery/developers-docs/index.md` — current command surface and
  docs map for what is actually shipped
- `materials-discovery/RUNBOOK.md` — source-of-truth operator workflow,
  artifact locations, and current command examples
- `materials-discovery/developers-docs/pipeline-stages.md` — per-command
  current behavior and stage contract details

### Zomic and visualization path
- `materials-discovery/developers-docs/zomic-design-workflow.md` — current
  Zomic-authored design path, export flow, and bridge boundary
- `materials-discovery/developers-docs/vzome-geometry-tutorial.md` — vZome
  geometry context and visualization-facing tutorial material

### Worked example inputs
- `materials-discovery/configs/systems/sc_zn_zomic.yaml` — checked Zomic-backed
  system config for the tutorial anchor example
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml` — current design
  input for export and geometry walkthrough

### CLI and implementation surface
- `materials-discovery/src/materials_discovery/cli.py` — current command
  registry and emitted summary contract for shipped workflow surfaces
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py` —
  narrow bridge between Zomic design inputs and generated orbit-library assets

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/developers-docs/index.md` already provides a compact,
  current command table and documentation hub that the refreshed narrative can
  cite instead of re-listing every command.
- `materials-discovery/RUNBOOK.md` already uses the command-plus-artifact-path
  style that should anchor the tutorial's operational sections.
- `materials-discovery/developers-docs/zomic-design-workflow.md` already
  explains the Zomic authoring bridge and can supply design-specific detail
  without forcing the tutorial to re-explain the whole bridge.
- `materials-discovery/developers-docs/pipeline-stages.md` already contains
  the current per-command contracts that can validate tutorial correctness.
- `materials-discovery/developers-docs/vzome-geometry-tutorial.md` already
  provides the deeper vZome context for the visualization portion.

### Established Patterns
- The docs surface is CLI-first, file-backed, and artifact-oriented.
- Examples are strongest when they use checked configs and explicit paths under
  `materials-discovery/data/`.
- Runtime prerequisites such as Java for the Zomic export path should be called
  out explicitly rather than buried in prose.
- Narrative docs can stay broad, but operator guidance should point back to the
  source-of-truth runbooks and config references.

### Integration Points
- `materials-discovery/developers-docs/podcast-deep-dive-source.md` for the
  narrative refresh
- `materials-discovery/developers-docs/` as the natural home for the guided
  tutorial and its cross-links
- `materials-discovery/Progress.md`, which must be updated once Phase 38 or 39
  edits files under `materials-discovery/`
- `materials-discovery/configs/systems/sc_zn_zomic.yaml` and
  `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml` as the worked
  example assets

</code_context>

<deferred>
## Deferred Ideas

- Additional worked tutorials for Al-Cu-Fe reference-aware flow or the external
  benchmark surface
- Broader podcast or website packaging beyond the repo documentation set
- Multi-example chemistry coverage in the first tutorial

</deferred>

---

*Phase: 37-deep-dive-provenance-audit-and-tutorial-scope*
*Context gathered: 2026-04-14*
