# Phase 30 Research

## Relevant Current State

- `LlmServingBenchmarkTarget` has workflow-role fields but no structured notion
  of lifecycle benchmark intent, so summary logic currently infers
  adapted-vs-baseline from lineage presence.
- `build_serving_benchmark_summary(...)` can already emit recommendation lines,
  which makes it the right seam for benchmark-backed promotion guidance.
- The repo now has:
  - promoted-family default config:
    `materials-discovery/configs/systems/al_cu_fe_llm_adapted.yaml`
  - explicit family pin config:
    `materials-discovery/configs/systems/al_cu_fe_llm_adapted_pinned.yaml`
  - adapted-vs-baseline benchmark spec:
    `materials-discovery/configs/llm/al_cu_fe_adapted_serving_benchmark.yaml`
- Existing real-mode coverage already stages checkpoint registration,
  promotion artifacts, and offline benchmark execution without a live server.

## Gaps To Close

1. No committed candidate-checkpoint config or benchmark spec comparing
   candidate vs promoted vs baseline.
2. No structured benchmark-target role for lifecycle recommendations.
3. Operator docs still explain adapted-vs-baseline workflow, not the full
   benchmark-backed promotion / rollback / retirement procedure.

## Implementation Direction

- Add an additive `checkpoint_benchmark_role` field to
  `LlmServingBenchmarkTarget`, limited to lifecycle-benchmark semantics for
  campaign-launch targets.
- Update benchmark summary logic to use these roles for recommendation lines.
- Commit a candidate-pinned config and lifecycle benchmark spec for Al-Cu-Fe.
- Extend real-mode and benchmark-schema/core tests to prove the new role-aware
  benchmark workflow offline.
