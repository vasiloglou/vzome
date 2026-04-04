# Phase 9 Research

## Local primary sources reviewed

- `.planning/ROADMAP.md` Phase 9 section
- `.planning/REQUIREMENTS.md` (`LLM-05`)
- `.planning/phases/06-zomic-training-corpus-pipeline/06-CONTEXT.md`
- `.planning/phases/07-llm-inference-mvp/07-CONTEXT.md`
- `.planning/phases/08-llm-evaluation-and-pipeline-integration/08-CONTEXT.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/zomic-llm-data-plan.md`
- `materials-discovery/src/materials_discovery/llm/prompting.py`
- `materials-discovery/src/materials_discovery/llm/corpus_builder.py`
- `materials-discovery/src/materials_discovery/llm/pipeline_benchmark.py`

## Key implementation observations

- The codebase now has the full prerequisite ladder for Phase 9:
  corpus artifacts, constrained inference, additive evaluation, and a downstream
  benchmark lane.
- The missing piece is not another adapter seam; it is a formal acceptance and
  improvement loop over the artifacts already produced in Phases 6-8.
- `llm/prompting.py` is still intentionally minimal, which makes it a good
  place to add composition-conditioned examples without destabilizing the rest
  of the generation runtime.
- Phase 8 benchmarks already provide the downstream metrics needed for
  `LLM-05`; they just are not yet gathered into one explicit acceptance pack.

## Phase 9 requirement interpretation

- `LLM-05` should be satisfied by a typed, reproducible acceptance surface that
  combines validity, novelty, and downstream pass-through metrics.
- “Fine-tuned model” should be interpreted practically here as preparation for
  improvement: eval-set export, stronger prompt conditioning, and an operator
  loop that can judge whether a future model is actually better.

## Risk notes

- Avoid promising heavyweight training infrastructure if the codebase only
  needs eval/export and metrics in this milestone.
- Keep example-conditioned prompting additive and optional so the current Phase 7
  path remains valid when no eval set is present.
- Keep `llm-suggest` in dry-run/design territory for this phase; a real closed
  loop needs stronger trust and acceptance gates first.
