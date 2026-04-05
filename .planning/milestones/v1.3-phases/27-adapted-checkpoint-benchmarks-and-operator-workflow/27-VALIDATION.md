---
phase: 27
slug: adapted-checkpoint-benchmarks-and-operator-workflow
status: complete
nyquist_compliant: true
created: 2026-04-05
---

# Phase 27 Validation

## Quick Commands

- `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_core.py tests/test_real_mode_pipeline.py tests/test_cli.py tests/test_llm_generate_cli.py tests/test_llm_checkpoint_registry.py tests/test_llm_replay_core.py -x -v`
- `cd materials-discovery && uv run pytest`

## Verification Map

| Task | Requirement | Evidence |
| --- | --- | --- |
| 27-01 adapted-vs-baseline benchmark summary | `LLM-22` | `tests/test_llm_serving_benchmark_core.py` |
| 27-02 operator docs and rollback guidance | `OPS-12` | `RUNBOOK.md`, `configuration-reference.md`, `llm-integration.md`, `pipeline-stages.md` |
| 27-03 final workflow proof | `LLM-22`, `OPS-12` | `tests/test_real_mode_pipeline.py`, `tests/test_cli.py`, full suite |

## Results

- Broad milestone rerun: `75 passed in 25.48s`
- Full suite: `421 passed, 3 skipped, 1 warning in 32.95s`
