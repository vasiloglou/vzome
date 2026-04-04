# Feature Research: v1.1 Closed-Loop LLM Campaign MVP

## Table stakes

- Turn a dry-run `llm-suggest` result into a structured campaign proposal.
- Keep proposal scope aligned to existing workflow concepts:
  - composition regions
  - motif edits
  - conditioning example choices
  - prompt and sampling changes
- Require explicit operator approval before any campaign launch.
- Materialize an approved proposal into a reproducible campaign spec.
- Launch approved campaigns through existing `llm-generate` contracts instead of
  inventing a second candidate format.
- Record lineage from acceptance pack and eval set through downstream results.
- Support replay and comparison of campaign outcomes.

## Differentiators

- Suggestions stay grounded in acceptance-pack metrics rather than vague advice.
- Campaigns are auditable and replayable from file-backed specs.
- Downstream comparison is native to the existing benchmark and report surfaces.
- The loop remains no-DFT and compatible with current rank/report workflows.

## Anti-features for this milestone

- Fully autonomous self-improving search loop.
- Local or fine-tuned model serving.
- New chemistry expansion as the milestone headline.
- UI-first orchestration.

## Feature grouping for requirements

### Closed-loop suggestions

Focus on turning acceptance-pack analysis into executable proposals and campaign
specs.

### Workflow integration

Focus on launching approved campaigns through `llm-generate` and measuring
their downstream performance using existing artifacts.

### Operations and governance

Focus on approval gates, replayability, provenance, and operator runbooks.
