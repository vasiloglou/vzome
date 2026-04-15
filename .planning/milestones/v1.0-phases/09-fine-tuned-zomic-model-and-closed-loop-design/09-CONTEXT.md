# Phase 9: Fine-Tuned Zomic Model and Closed-Loop Design - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning
**Mode:** Autonomous defaults from roadmap + completed Phases 6-8

<domain>
## Phase Boundary

Phase 9 should turn the now-stable LLM corpus, inference path, evaluation path,
and downstream benchmark lane into a sharper model-improvement surface. The
phase should deliver:

- formal acceptance metrics for the LLM workstream, grounded in the already
  implemented downstream benchmark lane
- an evaluation-set or acceptance-pack surface built from the existing corpus
  and benchmark artifacts
- a stronger, more composition-conditioned `llm-generate` prompt path that can
  use curated examples without changing the underlying Zomic compile authority
- an initial `llm-suggest` contract/design surface for future closed-loop work

This phase should avoid pretending to land full-scale training infrastructure,
distributed fine-tuning, or live closed-loop autonomy in one jump. The v1 goal
is to make model improvement measurable, reproducible, and ready for the next
training iteration.

</domain>

<decisions>
## Default Decisions

### Metrics and acceptance posture
- **D-01:** Phase 9 should satisfy `LLM-05` first by defining a formal
  acceptance-pack artifact over parse success, compile success, uniqueness,
  shortlist pass-through, validation pass rate, and report acceptance.
- **D-02:** Acceptance metrics must be computed from the implemented Phase 7/8
  artifact family rather than from ad hoc notebook logic.

### Fine-tuning/eval-set posture
- **D-03:** The practical Phase 9 deliverable is a reproducible eval-set/export
  layer and training metadata surface, not heavyweight trainer orchestration.
- **D-04:** The eval set should be derived from the existing Phase 6 corpus plus
  the Phase 8 benchmark lane so training and evaluation use the same Zomic-first
  contracts.

### Stronger inference posture
- **D-05:** Strengthen `llm-generate` through composition-conditioned prompting
  and curated example retrieval, not by changing the compile/validation
  authority or creating a second candidate schema.
- **D-06:** Example conditioning must remain file-backed and reproducible so the
  same prompt context can be rebuilt later for training or debugging.

### Closed-loop posture
- **D-07:** `llm-suggest` in Phase 9 should be a design/contract surface plus a
  lightweight operator-facing scaffold, not a fully autonomous optimizer.
- **D-08:** Any suggestion output should align with existing `active-learn`
  concepts: composition regions, candidate triage, and next-batch rationale.

### Inherited constraints
- **D-09:** Zomic remains the native generation representation.
- **D-10:** The no-DFT boundary stays explicit.
- **D-11:** Mock/offline proof remains the default test posture.
- **D-12:** New artifacts must stay additive to the current CLI/schema/manifests.

</decisions>

<specifics>
## Specific Ideas

- Add a typed `acceptance_pack.json` artifact that summarizes both deterministic
  and LLM lanes for the required systems.
- Export a compact eval set from Phase 6 gold/silver corpus examples so Phase 9
  can support both benchmarked prompting and later fine-tuning without
  duplicating conversion logic.
- Extend `llm-generate` with optional example retrieval keyed by system,
  composition, or eval-set tags to make prompting more composition-conditioned.
- Add a first `llm-suggest` design artifact or dry-run CLI that emits structured
  suggestions without executing a new search loop yet.

</specifics>

<canonical_refs>
## Canonical References

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/06-zomic-training-corpus-pipeline/06-CONTEXT.md`
- `.planning/phases/07-llm-inference-mvp/07-CONTEXT.md`
- `.planning/phases/08-llm-evaluation-and-pipeline-integration/08-CONTEXT.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/zomic-llm-data-plan.md`
- `materials-discovery/developers-docs/pipeline-stages.md`

</canonical_refs>

<code_context>
## Existing Code Insights

- `materials_discovery/llm/schema.py` already carries the evolving LLM contract
  surface and is the natural home for acceptance/eval-set models.
- `materials_discovery/llm/corpus_builder.py` and `llm/storage.py` already
  produce deterministic corpus artifacts that can seed a Phase 9 eval set.
- `materials_discovery/llm/prompting.py` is intentionally simple today, which
  makes it a good insertion point for composition-conditioned examples.
- `materials_discovery/llm/pipeline_benchmark.py` now provides the downstream
  lane-comparison surface needed to compute formal acceptance metrics.
- `cli.py` already exposes `llm-corpus`, `llm-generate`, and `llm-evaluate`,
  so Phase 9 can extend the existing operator surface rather than inventing a
  new entrypoint family.

</code_context>

<deferred>
## Deferred Ideas

- Full trainer orchestration for LoRA/QLoRA or distributed fine-tuning
- Local serving stacks beyond the already deferred provider seam
- Autonomous `llm-suggest` execution that directly mutates active-learning runs

</deferred>

---

*Phase: 09-fine-tuned-zomic-model-and-closed-loop-design*
*Context gathered: 2026-04-03*
