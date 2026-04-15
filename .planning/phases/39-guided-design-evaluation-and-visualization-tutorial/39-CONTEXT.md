# Phase 39: Guided Design, Evaluation, and Visualization Tutorial - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 39 publishes one checked tutorial that teaches the current Sc-Zn
Zomic-backed operator flow from design export through generate, screen,
validate, rank, report, and geometry visualization.

This phase should deliver:

- a step-by-step tutorial document under `materials-discovery/developers-docs/`
  with runnable commands and concrete artifact paths
- interpretation notes for the current screening, validation, ranking, and
  report artifacts so readers know what signals to inspect
- explicit visualization guidance that keeps the geometry authority chain
  visible from `.zomic` source through exported prototype artifacts
- a docs index link and the required `materials-discovery/Progress.md` update

This phase does not add new discovery algorithms, new bridge code, or new
visualization exporters.

</domain>

<decisions>
## Implementation Decisions

### Tutorial scope
- **D-01:** Use the locked Sc-Zn Zomic-backed path as the only worked example.
- **D-02:** Publish the tutorial at
  `materials-discovery/developers-docs/guided-design-tutorial.md`.
- **D-03:** Link the tutorial from `materials-discovery/developers-docs/index.md`
  so it becomes part of the current docs surface.

### Workflow shape
- **D-04:** Keep the tutorial CLI-first and file-backed: every stage should show
  the command, the primary output path, and what to inspect next.
- **D-05:** Use the Phase 37 locked command chain as the canonical walkthrough:
  `export-zomic`, `generate`, `screen`, `hifi-validate`, `hifi-rank`, and
  `report`.
- **D-06:** Use the checked artifact set already present in the repo for the
  interpretation examples and call out exact snapshot values as
  `As of 2026-04-15` when they are likely to drift.

### Geometry authority and visualization
- **D-07:** Make the geometry authority chain explicit:
  `.zomic` source -> raw export JSON -> orbit-library prototype JSON ->
  generated candidate JSONL.
- **D-08:** Use the existing vZome/Zomic toolchain only. Visualization guidance
  should rely on the checked `.zomic` design, `mdisc export-zomic`, the raw
  export, and the desktop Zomic editor or other existing vZome workflow rather
  than inventing a new viewer.

### Documentation workflow
- **D-09:** Any edit under `materials-discovery/` must update
  `materials-discovery/Progress.md` in the same change set with both a
  Changelog row and a Diary entry.

### the agent's Discretion
- Exact section order inside the tutorial
- How much checked snapshot detail to include inline versus in artifact tables
- Exact wording of the visualization instructions, provided the geometry
  authority chain stays explicit

</decisions>

<specifics>
## Specific Ideas

- Start with prerequisites and the six-command walkthrough so a new operator
  can run the path in order.
- Add one artifact table that maps each command to the file it writes.
- Interpret the current checked snapshot with a few high-signal values rather
  than reproducing whole JSON payloads.
- End with the geometry authority chain so readers know what to edit when the
  design changes and what is only downstream derived state.

</specifics>

<canonical_refs>
## Canonical References

### Milestone controls
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

### Upstream phase evidence
- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md`
- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-VERIFICATION.md`
- `.planning/phases/38-narrative-refresh-and-cross-linked-deep-dive/38-01-SUMMARY.md`
- `.planning/phases/38-narrative-refresh-and-cross-linked-deep-dive/38-VERIFICATION.md`

### Current docs and artifact contracts
- `materials-discovery/developers-docs/index.md`
- `materials-discovery/RUNBOOK.md`
- `materials-discovery/developers-docs/pipeline-stages.md`
- `materials-discovery/developers-docs/zomic-design-workflow.md`
- `materials-discovery/developers-docs/vzome-geometry-tutorial.md`
- `core/docs/ZomicReference.md`
- `desktop/src/main/java/org/vorthmann/zome/ui/ZomicEditorPanel.java`

### Worked example assets
- `materials-discovery/configs/systems/sc_zn_zomic.yaml`
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml`
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic`
- `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json`
- `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json`
- `materials-discovery/data/candidates/sc_zn_candidates.jsonl`
- `materials-discovery/data/calibration/sc_zn_screen_calibration.json`
- `materials-discovery/data/hifi_validated/sc_zn_all_validated.jsonl`
- `materials-discovery/data/ranked/sc_zn_ranked.jsonl`
- `materials-discovery/data/reports/sc_zn_report.json`
- `materials-discovery/data/reports/sc_zn_xrd_patterns.jsonl`
- `materials-discovery/data/reports/sc_zn_benchmark_pack.json`

</canonical_refs>

<code_context>
## Existing Code and Docs Insights

- `zomic-design-workflow.md` already defines the export contract, runtime
  requirements, and artifact split between raw export and orbit-library JSON.
- `pipeline-stages.md` already defines the exact CLI syntax and output paths for
  every stage the tutorial needs.
- `ZomicEditorPanel.java` confirms the desktop workflow has a Zomic editor that
  can load, save, and run `.zomic` scripts directly.
- The checked Sc-Zn artifacts already provide a concrete interpretation surface:
  30 generated candidates, 20 passing screening thresholds, 4 shortlisted and
  reported candidates, and a top-ranked candidate that still ends in `hold`
  with explicit risk flags.

</code_context>

<deferred>
## Deferred Ideas

- Additional worked examples such as Al-Cu-Fe or external benchmark lanes
- New visualization exporters or reverse-import tooling
- Broader onboarding or publishing work outside the repo docs set

</deferred>

---

*Phase: 39-guided-design-evaluation-and-visualization-tutorial*
*Context gathered: 2026-04-15*
