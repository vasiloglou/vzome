# Phase 43: Notebook Visualization and LLM Walkthrough Integration - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 43 makes `materials-discovery/notebooks/guided_design_tutorial.ipynb`
the most detailed executable companion for the checked Sc-Zn walkthrough.

This phase should deliver:

- a notebook that uses the Phase 41 programmatic preview helper directly,
  including a documented preview-vs-refresh path that stays inside repo-owned
  code for the normal checked geometry inspection flow
- a richer notebook treatment of the shipped LLM surfaces than the Markdown
  tutorial alone, while preserving the deterministic Sc-Zn spine as the main
  authority chain
- explicit notebook coverage of the same-system Sc-Zn lane and the
  translation/external benchmark branch, including the full inspect/freeze/
  register/smoke/benchmark command family the user requested
- docs-hub and cross-link updates that explain when to use the Markdown
  tutorial, the notebook, and the standalone programmatic visualization
  reference

This phase does not add new LLM mechanics, new visualization backends,
desktop-vZome/browser parity, new chemistry fixtures, or a notebook-specific UI
product.

</domain>

<decisions>
## Implementation Decisions

### Notebook role and structure
- **D-01:** Keep the deterministic Sc-Zn walkthrough as the notebook spine, not
  as a side note beneath the additive LLM branches.
- **D-02:** Make the notebook the richest runnable companion surface while
  preserving the Markdown tutorial as the shortest checked operator story.
- **D-03:** Reuse the branch structure introduced in Phase 42 so the notebook
  deepens the same narrative instead of teaching a second taxonomy.

### Programmatic preview behavior
- **D-04:** Integrate the Phase 41 helper from
  `materials_discovery.visualization` directly inside the notebook.
- **D-05:** Default the notebook to safe preview behavior over checked artifacts
  and document an explicit refresh/execute switch for users who want to rerun
  the export path.
- **D-06:** Keep desktop vZome positioned as optional authoring and deeper
  inspection tooling, not as the notebook happy path.

### LLM branch depth
- **D-07:** Expand the same-system Sc-Zn lane into explicit command, artifact,
  and interpretation cells rather than leaving it as one short code preview.
- **D-08:** Expand the translation/external benchmark branch into a structured
  walkthrough that includes `llm-translate`, `llm-translate-inspect`,
  `llm-translated-benchmark-freeze`, `llm-translated-benchmark-inspect`,
  `llm-register-external-target`, `llm-inspect-external-target`,
  `llm-smoke-external-target`, `llm-external-benchmark`, and
  `llm-inspect-external-benchmark`.
- **D-09:** Preserve the explicit Sc-Zn -> Al-Cu-Fe context switch language for
  the interoperability branch so the notebook does not imply a new geometry
  authority chain.

### Documentation alignment
- **D-10:** Update the docs index and visualization reference so readers can
  tell when to open the Markdown tutorial, the notebook, or the standalone
  visualization doc.
- **D-11:** Any `materials-discovery/` edits in this phase must update
  `materials-discovery/Progress.md` in the same change set.

### the agent's Discretion
- Exact notebook cell ordering and helper ergonomics
- Whether path/existence checks or committed example artifacts carry more of the
  external-branch teaching burden when real runtimes are absent
- How much repeated prose should stay in Markdown cells versus compact code-cell
  comments

</decisions>

<canonical_refs>
## Canonical References

### Milestone controls
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` - `OPS-25`, `OPS-26`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

### Prior phase context that remains binding
- `.planning/milestones/v1.8-phases/40-llm-narrative-enrichment-and-notebook-tutorial-conversion/40-CONTEXT.md`
- `.planning/phases/41-programmatic-visualization-artifact-and-library-surface/41-CONTEXT.md`
- `.planning/phases/42-extensive-guided-tutorial-expansion/42-CONTEXT.md`

### Primary implementation targets
- `materials-discovery/notebooks/guided_design_tutorial.ipynb`
- `materials-discovery/developers-docs/guided-design-tutorial.md`
- `materials-discovery/developers-docs/programmatic-zomic-visualization.md`
- `materials-discovery/developers-docs/index.md`
- `materials-discovery/Progress.md`

### Supporting docs and configs
- `materials-discovery/RUNBOOK.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/pipeline-stages.md`
- `materials-discovery/developers-docs/llm-translation-runbook.md`
- `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md`
- `materials-discovery/developers-docs/llm-external-target-runbook.md`
- `materials-discovery/developers-docs/llm-external-benchmark-runbook.md`
- `materials-discovery/configs/systems/sc_zn_zomic.yaml`
- `materials-discovery/configs/systems/sc_zn_llm_mock.yaml`
- `materials-discovery/configs/systems/sc_zn_llm_local.yaml`
- `materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml`
- `materials-discovery/configs/llm/al_cu_fe_external_cif_target.yaml`
- `materials-discovery/configs/llm/al_cu_fe_external_material_string_target.yaml`
- `materials-discovery/configs/llm/al_cu_fe_external_benchmark.yaml`

### Implementation surfaces
- `materials-discovery/src/materials_discovery/visualization/__init__.py`
- `materials-discovery/src/materials_discovery/visualization/viewer.py`
- `materials-discovery/src/materials_discovery/common/schema.py`

</canonical_refs>

<code_context>
## Existing Code and Docs Insights

### Reusable assets
- The current notebook already has working-directory guards, safe preview-mode
  command helpers, and checked artifact readers.
- The Phase 41 visualization helper already exposes `preview_raw_export(...)`
  and `preview_zomic_design(...)`, which are exactly the programmatic notebook
  surfaces this phase needs.
- The Markdown tutorial now contains the branch map, preview handoff, and
  LLM-branch structure the notebook should deepen rather than contradict.

### Established patterns
- `materials-discovery/` tutorials stay CLI-first, file-backed, and honest
  about future-work boundaries.
- Notebook code cells should be safe to read without running everything
  immediately.
- Translation and external benchmark docs already rely on fixture-backed
  Al-Cu-Fe example specs rather than pretending a full external runtime is
  bundled in the repo.

### Integration points
- The notebook should link back to the Markdown tutorial and the standalone
  visualization reference rather than absorbing both roles into one artifact.
- The docs index should gain an explicit path to the standalone visualization
  doc so the tutorial/notebook/library split is legible.
- The visualization reference should stop treating notebook embedding as purely
  future work once this phase lands.

</code_context>

<specifics>
## Specific Ideas

- Add notebook flags that separate safe preview, deterministic reruns, and the
  heavier or optional LLM branches so users can execute selectively.
- Render the checked Sc-Zn preview inline from repo-owned helpers, ideally into
  a temporary HTML path so read-only notebook execution does not dirty the repo.
- Use committed translation-bundle artifacts where available, and graceful
  path/spec inspection when external target outputs are not present yet.
- Add notebook sections for the Al-Cu-Fe context switch, follow-on workflow
  families, and the preview-vs-desktop-vZome boundary so the notebook is
  richer than the Markdown page, not merely duplicated.

</specifics>

<deferred>
## Deferred Ideas

- New chemistry fixtures created only to make the notebook prettier
- Full external-target runtime snapshots checked into the repo
- Richer browser-side `.vZome` / `.shapes.json` parity
- Notebook widgets or a notebook-driven UI layer

</deferred>

---

*Phase: 43-notebook-visualization-and-llm-walkthrough-integration*
*Context gathered: 2026-04-15*
