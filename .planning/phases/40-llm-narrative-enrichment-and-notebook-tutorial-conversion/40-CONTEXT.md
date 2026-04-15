# Phase 40: LLM Narrative Enrichment and Notebook Tutorial Conversion - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase is a documentation follow-up to the shipped `v1.7` docs baseline.
It should make the repo's current LLM workflow surface legible inside the
hands-on docs stack and publish a notebook version of the checked guided
walkthrough.

The phase does not add new LLM mechanics, new serving/checkpoint code, new
benchmark features, or a new UI surface. It only enriches explanation and
teaching for the surfaces that already ship.

</domain>

<decisions>
## Implementation Decisions

### Tutorial framing
- Keep the deterministic Sc-Zn Zomic-backed path as the main worked example.
- Explain the LLM workflows as additive or companion lanes, not as a
  replacement for the geometry-authority spine.
- Use the same Sc-Zn family where possible so the tutorial and notebook do not
  jump to an unrelated chemistry just to mention LLM features.

### Notebook delivery
- Publish the notebook under `materials-discovery/notebooks/` to match the
  repo's existing notebook layout.
- Make the notebook useful even when not executed immediately: include setup
  notes, explicit working-directory guidance, command cells, and inspection
  cells that explain what each artifact means.
- Prefer one detailed notebook companion over fragmenting the walkthrough into
  several shorter notebooks.

### Cross-link strategy
- Update the Markdown tutorial so readers can see when to use the page versus
  the notebook.
- Update the docs hub and the deep-dive source so the notebook and LLM
  cross-links are discoverable from the existing narrative/docs stack.

### the agent's Discretion
- The exact amount of companion-lane detail is at the agent's discretion as
  long as the shipped LLM surfaces are explicit and future-work boundaries stay
  honest.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/developers-docs/guided-design-tutorial.md` already
  contains the checked deterministic Sc-Zn walkthrough and can be extended
  rather than rewritten.
- `materials-discovery/developers-docs/llm-integration.md`,
  `materials-discovery/RUNBOOK.md`, and
  `materials-discovery/developers-docs/pipeline-stages.md` already describe the
  shipped LLM commands and artifact families.
- `materials-discovery/notebooks/` already exists and contains Python 3
  notebooks, so the new notebook can follow that metadata/layout pattern.

### Established Patterns
- Docs pages in `developers-docs/` prefer one focused page per workflow plus
  index cross-links instead of huge all-in-one manuals.
- `materials-discovery/Progress.md` must be updated in the same change set as
  every `materials-discovery/` doc change.
- Existing tutorials keep exact snapshot values dated and use the checked repo
  artifacts as the source of truth.

### Integration Points
- `materials-discovery/developers-docs/index.md` is the primary docs-map entry
  point.
- `materials-discovery/developers-docs/podcast-deep-dive-source.md` is the
  long-form narrative surface that should point readers to practical docs.
- `materials-discovery/notebooks/` is the correct home for a richer executable
  tutorial artifact.

</code_context>

<specifics>
## Specific Ideas

- Add one "where the LLM workflows fit" section to the guided tutorial rather
  than trying to turn every LLM family into a full second worked example.
- Include `sc_zn_llm_mock.yaml` and `sc_zn_llm_local.yaml` in the companion
  notebook to keep the chemistry family aligned with the main walkthrough.
- Keep campaign/checkpoint/translation/external-benchmark coverage explicit via
  tables and links to the runbooks instead of bloating the checked deterministic
  walkthrough with unrelated prerequisites.

</specifics>

<deferred>
## Deferred Ideas

- A broader docs-site redesign or publishing workflow.
- Interactive notebook widgets or a notebook-driven execution UI.
- New benchmark or campaign automation features justified only by the docs work.

</deferred>
