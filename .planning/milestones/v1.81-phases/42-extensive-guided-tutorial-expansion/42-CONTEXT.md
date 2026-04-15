# Phase 42: Extensive Guided Tutorial Expansion - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 42 expands the checked Markdown tutorial into one deeper operator
walkthrough that keeps the deterministic Sc-Zn evidence chain visible while
showing where the shipped LLM workflow families branch from that spine.

This phase should deliver:

- a substantially expanded
  `materials-discovery/developers-docs/guided-design-tutorial.md` that keeps
  the Sc-Zn deterministic path as the main worked example
- one repo-owned visualization happy path based on the Phase 41 programmatic
  preview surface instead of a mandatory desktop-vZome handoff
- one detailed same-system LLM companion branch that explains how
  `llm-generate` and `llm-evaluate` relate to the deterministic artifacts
- one explicit interoperability and external-benchmark branch that demonstrates
  `llm-translate`, `llm-translate-inspect`,
  `llm-translated-benchmark-freeze`, `llm-translated-benchmark-inspect`,
  `llm-register-external-target`, `llm-inspect-external-target`,
  `llm-smoke-external-target`, `llm-external-benchmark`, and
  `llm-inspect-external-benchmark`
- honest positioning for campaign and serving or checkpoint workflows without
  pretending they are the first-run tutorial path

This phase does not add new LLM mechanics, new benchmark features, new
visualization capabilities, notebook-only UI work, or desktop-vZome/browser
parity.

</domain>

<decisions>
## Implementation Decisions

### Tutorial structure and reader path
- **D-01:** Keep the deterministic Sc-Zn CLI walkthrough as the tutorial spine
  rather than interleaving LLM commentary into every existing section.
- **D-02:** Expand the tutorial by adding explicit branch sections that start
  from the deterministic artifact chain and explain what each LLM family
  consumes, produces, and helps an operator decide next.
- **D-03:** Keep the Markdown tutorial extensive and operator-facing, but do
  not turn it into an exhaustive replacement for the runbooks or the notebook.

### LLM branch depth and order
- **D-04:** Treat the same-system companion lane as a first-class worked branch:
  `llm-generate` and `llm-evaluate` should receive commands, artifact paths,
  and interpretation guidance rather than a short catalog entry.
- **D-05:** Treat the translation and external-benchmark family as a second
  first-class worked branch. The tutorial should explicitly demonstrate
  `llm-translate`, `llm-translate-inspect`,
  `llm-translated-benchmark-freeze`, `llm-translated-benchmark-inspect`,
  `llm-register-external-target`, `llm-inspect-external-target`,
  `llm-smoke-external-target`, `llm-external-benchmark`, and
  `llm-inspect-external-benchmark`.
- **D-06:** Keep campaign-governance commands and serving or checkpoint
  commands explicit but lighter-weight: they should be positioned as follow-on
  operator workflows with representative commands, artifact families, and links
  to deeper runbooks instead of becoming full worked examples inside this page.
- **D-07:** Reuse the same chemistry family where it is already supported by
  checked assets, but do not invent new Sc-Zn-only benchmark fixtures just to
  force every LLM branch onto one chemistry. If the translation or external
  benchmark lane relies on existing Al-Cu-Fe demo specs, say so clearly in the
  tutorial instead of hiding the context switch.

### Programmatic visualization handoff
- **D-08:** Replace the tutorial's desktop-only visualization happy path with
  the Phase 41 repo-owned preview flow:
  `.zomic` source -> `mdisc export-zomic` -> `*.raw.json` ->
  `mdisc preview-zomic` or library helper -> downstream orbit-library and
  candidate artifacts.
- **D-09:** Show the CLI preview path as the primary operator surface and also
  show the Python helper from `materials_discovery.visualization` briefly so
  readers can see the reusable library call that later notebook work should use.
- **D-10:** Keep desktop vZome positioned as optional authoring and deeper
  inspection tooling. State explicitly that `.vZome` and `.shapes.json`
  compatibility, richer browser parity, and service-backed rendering remain
  future work.

### Artifact interpretation pattern
- **D-11:** Preserve the repo's CLI-first, file-backed teaching pattern:
  command, primary output path, what to inspect, and what the signal means.
- **D-12:** Apply full artifact-interpretation treatment to the deterministic
  spine, the same-system LLM branch, and the translation/external benchmark
  branch.
- **D-13:** For campaign and serving or checkpoint flows, use concise branch
  summaries with representative commands, expected artifacts, and the decision
  point that should send an operator there next.
- **D-14:** Keep volatile counts and snapshot values dated when they may drift,
  and keep failure or hold outcomes explicit when the checked artifacts warrant
  them.

### Documentation workflow
- **D-15:** Keep the tutorial anchored to shipped surfaces only, with explicit
  future-work labels where the repo does not yet provide parity or automation.
- **D-16:** Any later edit under `materials-discovery/` for this phase must
  update `materials-discovery/Progress.md` in the same change set.

### the agent's Discretion
- Exact section titles and internal ordering
- Whether the branch summaries are presented as prose blocks, tables, or a mix
- How much of the Python helper surface to show inline versus cross-link
- Whether campaign and serving branches live in the main flow or an appendix,
  provided they stay explicit and honest

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` - current milestone scope and active constraints
- `.planning/REQUIREMENTS.md` - `DOC-06` and `DOC-07`
- `.planning/ROADMAP.md` - Phase 42 goal, success criteria, and boundaries
- `.planning/STATE.md` - current execution position and recent decisions

### Prior context that remains binding
- `.planning/milestones/v1.7-phases/39-guided-design-evaluation-and-visualization-tutorial/39-CONTEXT.md`
  - locked the deterministic Sc-Zn tutorial spine and geometry authority chain
- `.planning/milestones/v1.8-phases/40-llm-narrative-enrichment-and-notebook-tutorial-conversion/40-CONTEXT.md`
  - locked the tutorial as the shorter page and the notebook as the detailed
    companion artifact
- `.planning/phases/41-programmatic-visualization-artifact-and-library-surface/41-CONTEXT.md`
  - locked the raw-export-driven preview seam, Python-first library surface,
    and honest future-work boundary for visualization

### Primary docs and tutorial assets
- `materials-discovery/developers-docs/guided-design-tutorial.md` - main edit
  target for this phase
- `materials-discovery/developers-docs/programmatic-zomic-visualization.md` -
  shipped preview workflow, CLI entry point, and Python helper surface
- `materials-discovery/developers-docs/zomic-design-workflow.md` - geometry
  export contract and artifact chain
- `materials-discovery/developers-docs/pipeline-stages.md` - canonical command,
  output, and artifact reference for every LLM stage discussed in the tutorial
- `materials-discovery/developers-docs/llm-translation-runbook.md`
- `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md`
- `materials-discovery/developers-docs/llm-external-target-runbook.md`
- `materials-discovery/developers-docs/llm-external-benchmark-runbook.md`
- `materials-discovery/developers-docs/llm-integration.md` - existing narrative
  framing for the shipped LLM workflow families
- `materials-discovery/developers-docs/index.md` - docs hub and cross-link map
- `materials-discovery/notebooks/guided_design_tutorial.ipynb` - downstream
  notebook companion that should stay aligned conceptually with the tutorial

### Worked example and checked artifact paths
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml`
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic`
- `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json`
- `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json`
- `materials-discovery/configs/systems/sc_zn_zomic.yaml`
- `materials-discovery/configs/systems/sc_zn_llm_mock.yaml`
- `materials-discovery/configs/systems/sc_zn_llm_local.yaml`
- `materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml`
- `materials-discovery/configs/llm/al_cu_fe_external_cif_target.yaml`
- `materials-discovery/configs/llm/al_cu_fe_external_material_string_target.yaml`
- `materials-discovery/configs/llm/al_cu_fe_external_benchmark.yaml`

### Current implementation surfaces
- `materials-discovery/src/materials_discovery/visualization/raw_export.py`
- `materials-discovery/src/materials_discovery/visualization/viewer.py`
- `materials-discovery/src/materials_discovery/visualization/cli.py`
- `materials-discovery/src/materials_discovery/cli.py`

</canonical_refs>

<code_context>
## Existing Code and Docs Insights

### Reusable assets
- `guided-design-tutorial.md` already contains a checked deterministic Sc-Zn
  walkthrough with artifact inspection and a small "Where the LLM Workflows
  Fit" section that can be expanded rather than replaced wholesale.
- `programmatic-zomic-visualization.md` already documents the Phase 41 preview
  contract, including `mdisc preview-zomic` and the Python helper surface.
- The translation and external-benchmark runbooks already contain concrete
  example commands, artifact directories, and interpretation vocabulary for the
  exact command family the user wants made explicit.

### Established patterns
- `materials-discovery/` docs are CLI-first, file-backed, and honest about
  artifact lineage and future-work boundaries.
- The tutorial style is "run this, inspect this, interpret this," not a loose
  command catalog.
- The current preview seam is local and file-backed; the milestone does not
  authorize a default long-running service.

### Integration points
- The programmatic preview path should replace the old desktop-only handoff in
  the tutorial without breaking the `.zomic` -> raw export -> orbit library ->
  candidates authority chain.
- The translation/external-benchmark branch can draw on committed Al-Cu-Fe demo
  specs and fixture-backed benchmark assets, provided the tutorial calls out the
  chemistry shift explicitly instead of implying one monolithic Sc-Zn example.
- The notebook remains a downstream consumer of the same tutorial structure and
  preview helper, but this phase's primary implementation target is the
  Markdown tutorial page.

</code_context>

<specifics>
## Specific Ideas

- Rewrite the current LLM section into branch-oriented subsections that explain
  when an operator stays on the deterministic lane and when they intentionally
  branch into same-system LLM generation, interoperability translation, or
  comparative benchmarking.
- Move the visualization guidance so the programmatic preview appears as the
  normal next step after export, while desktop vZome remains an optional deeper
  inspection tool.
- Keep campaign-governance and serving/checkpoint workflows visible as "what
  comes next" surfaces rather than erasing them from the tutorial.
- Use the existing runbooks and `pipeline-stages.md` to avoid inventing new
  terminology, artifact names, or example command syntax.

</specifics>

<deferred>
## Deferred Ideas

- Rewriting the notebook in this phase
- New chemistry-specific benchmark fixtures created only for tutorial polish
- Browser-side visualization parity with desktop vZome
- A service-backed or remote-render preview workflow as the default tutorial
  path
- Turning campaign or serving/checkpoint families into fully worked end-to-end
  examples inside the Markdown page

</deferred>

---

*Phase: 42-extensive-guided-tutorial-expansion*
*Context gathered: 2026-04-15*
