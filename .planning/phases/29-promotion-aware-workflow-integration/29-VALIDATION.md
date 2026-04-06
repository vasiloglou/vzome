---
phase: 29
slug: promotion-aware-workflow-integration
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
last_updated: "2026-04-06T00:37:35Z"
---

# Phase 29 — Validation Record

## Verification Runs

- `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py tests/test_llm_launch_core.py tests/test_llm_generate_cli.py -x -v`
  - Result: `34 passed in 0.40s`
- `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py tests/test_llm_serving_benchmark_core.py -x -v`
  - Result: `23 passed in 0.29s`
- `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -x -v`
  - Result: `13 passed in 22.07s`
- `cd materials-discovery && uv run pytest tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py -x -v`
  - Result: `12 passed in 0.32s`

## Covered Requirements

- `LLM-24` — promoted and pinned checkpoints resolve cleanly through generate,
  launch, replay, compare, and benchmark workflows
- `LLM-26` — baseline rollback remains explicit and historical launches keep
  enough lifecycle identity to explain what actually ran

## Sign-Off

Phase 29 is verified complete and ready to hand off to Phase 30.
