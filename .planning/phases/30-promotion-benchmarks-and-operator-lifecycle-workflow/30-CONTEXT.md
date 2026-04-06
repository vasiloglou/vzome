# Phase 30: Promotion Benchmarks and Operator Lifecycle Workflow - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning
**Mode:** Autonomous follow-on from completed Phase 29

<domain>
## Phase Boundary

Phase 29 made checkpoint-family runtime resolution real for generate, launch,
replay, compare, and serving benchmarks. Phase 30 needs to turn that runtime
surface into an operator-usable lifecycle workflow:

- benchmark a promoted checkpoint, a candidate checkpoint, and the baseline
  local lane on one shared acceptance-pack context
- make benchmark summaries recommend promotion, retention, or rollback from
  structured target intent rather than target-name guessing
- document the concrete promotion, rollback, and retirement procedure around
  the existing `llm-list-checkpoints`, `llm-promote-checkpoint`, and
  `llm-retire-checkpoint` commands

</domain>

<decisions>
## Implementation Decisions

### Benchmark intent should be explicit

Use typed benchmark-target roles for lifecycle benchmarking instead of relying
on target IDs or free-form notes to infer which target is the promoted default,
which one is the candidate checkpoint, and which one is the rollback baseline.

### Keep the workflow CLI-first

Do not add a new high-level lifecycle command in this phase. Reuse the shipped
serving-benchmark runner plus the existing checkpoint lifecycle CLI commands and
close the gap with better benchmark summaries, committed benchmark specs, and
operator docs.

### Preserve baseline rollback visibility

The baseline local lane must stay visible in both benchmark output and docs so
operators always have a rollback path even when candidate/promoted benchmark
results are inconclusive.

</decisions>

<code_context>
## Existing Code Insights

- `llm/serving_benchmark.py` already supports multi-target shared-context
  benchmarks and writes recommendation lines, but the adapted-checkpoint logic
  is still heuristic and only distinguishes adapted-vs-baseline.
- `configs/systems/al_cu_fe_llm_adapted.yaml` now resolves the promoted family
  default, and `al_cu_fe_llm_adapted_pinned.yaml` already demonstrates explicit
  pinning inside the same family.
- Phase 28 lifecycle commands (`llm-list-checkpoints`, `llm-promote-checkpoint`,
  `llm-retire-checkpoint`) are already operator-usable and only need a clearer
  end-to-end procedure around benchmark evidence.
- `test_real_mode_pipeline.py` already proves offline adapted-vs-baseline
  serving-benchmark execution, so it is the right seam for a new promoted vs
  candidate vs baseline proof.

</code_context>

<specifics>
## Specific Ideas

- Add a committed candidate config for `Al-Cu-Fe` that explicitly pins one
  non-promoted family member.
- Add a committed lifecycle benchmark spec with three generation targets:
  baseline local, promoted family default, and candidate explicit pin.
- Teach benchmark summaries to emit clear recommendation lines such as
  "promote candidate", "keep promoted", or "rollback baseline remains
  available" from typed benchmark-role metadata.

</specifics>

<deferred>
## Deferred Ideas

- No automated training-job orchestration
- No multi-candidate tournaments or bracketed promotion systems
- No UI for checkpoint lifecycle management

</deferred>
