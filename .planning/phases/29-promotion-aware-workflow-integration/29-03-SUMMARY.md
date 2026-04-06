# Phase 29 Plan 03 Summary

Closed the promotion-aware workflow with committed configs, offline proof, and
operator docs.

## Delivered

- Switched `configs/systems/al_cu_fe_llm_adapted.yaml` to promoted-family
  default resolution and added
  `configs/systems/al_cu_fe_llm_adapted_pinned.yaml` as the explicit-pin
  companion config.
- Proved the promoted-default benchmark path offline by registering and
  promoting the adapted checkpoint before the benchmark run and verifying the
  resulting serving identity metadata.
- Updated the runbook and developer docs to explain promoted defaults, explicit
  family pins, replay-safe historical launches, and the baseline local rollback
  path while keeping the Phase 30 benchmark/promotion workflow boundary
  explicit.

## Verification

- `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -x -v`
  - Result: `13 passed in 22.07s`
- `cd materials-discovery && uv run pytest tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py -x -v`
  - Result: `12 passed in 0.32s`

## Outcome

Phase 29 now ships one coherent operator workflow for promoted defaults,
explicit pins, replay-safe history, and rollback-to-baseline behavior.
