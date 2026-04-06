---
one-liner: Closed the operator lifecycle workflow with committed docs and help coverage for registration, benchmarking, promotion, rollback, and retirement.
requirements-completed:
  - LLM-25
  - OPS-14
---

# Phase 30 Plan 03 Summary

Closed the benchmark-backed lifecycle workflow with operator docs and CLI
discoverability coverage.

## Delivered

- Updated `RUNBOOK.md` with the full register -> benchmark -> promote-or-keep
  -> rollback -> retire flow using the committed lifecycle benchmark spec and
  family commands.
- Updated the developer docs so configuration, LLM workflow, and pipeline-stage
  references all describe checkpoint lifecycle benchmarks in terms of explicit
  benchmark roles and committed example configs.
- Added help-surface regression coverage so the lifecycle workflow commands stay
  visible together at the CLI layer.

## Verification

- `cd materials-discovery && uv run pytest tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py tests/test_llm_checkpoint_cli.py tests/test_cli.py -x -v`
  - Result: `36 passed in 0.71s`

## Outcome

The milestone now ends with a documented, benchmark-backed checkpoint lifecycle
workflow that operators can follow without inventing an ad hoc process.
