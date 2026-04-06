---
phase: 30
slug: promotion-benchmarks-and-operator-lifecycle-workflow
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
last_updated: "2026-04-06T01:00:51Z"
---

# Phase 30 — Validation Record

## Verification Runs

- `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py -x -v`
  - Result: `12 passed in 0.48s`
- `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -x -v`
  - Result: `14 passed in 14.92s`
- `cd materials-discovery && uv run pytest tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py tests/test_llm_checkpoint_cli.py tests/test_cli.py -x -v`
  - Result: `36 passed in 0.71s`
- `git diff --check`
  - Result: clean

## Covered Requirements

- `LLM-25` — operators can compare the promoted default, a candidate checkpoint,
  and the baseline local lane on one shared benchmark context with explicit
  benchmark-backed recommendations
- `OPS-14` — the workflow now ships concrete operator guidance for listing,
  pinning, benchmarking, promoting, rolling back, and retiring checkpoints

## Sign-Off

Phase 30 is validated complete and ready for milestone audit and archive.
