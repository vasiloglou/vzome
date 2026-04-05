---
phase: 26
slug: zomic-adapted-local-generation-integration
status: complete
nyquist_compliant: true
created: 2026-04-05
---

# Phase 26 Validation

## Quick Commands

- `cd materials-discovery && uv run pytest tests/test_llm_generate_cli.py tests/test_llm_serving_benchmark_core.py tests/test_llm_replay_core.py tests/test_real_mode_pipeline.py -k "checkpoint or adapted or serving_benchmark_examples" -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_llm_generate_cli.py tests/test_llm_serving_benchmark_core.py tests/test_llm_replay_core.py tests/test_real_mode_pipeline.py tests/test_llm_launch_schema.py tests/test_llm_runtime.py tests/test_cli.py -x -v`
- `cd materials-discovery && uv run pytest`

## Verification Map

| Task | Requirement | Evidence |
| --- | --- | --- |
| 26-01 adapted generation lane | `LLM-20` | `tests/test_llm_generate_cli.py`, `configs/systems/al_cu_fe_llm_adapted.yaml` |
| 26-02 replay and hard drift | `LLM-20`, `LLM-21` | `tests/test_llm_replay_core.py` |
| 26-03 benchmark-compatible workflow proof | `LLM-21` | `tests/test_real_mode_pipeline.py`, `tests/test_llm_serving_benchmark_core.py` |

## Results

- Focused integration rerun: `12 passed, 28 deselected in 0.44s`
- Broad milestone rerun: `75 passed in 25.48s`
- Full suite evidence retained at milestone closeout: `421 passed, 3 skipped, 1 warning in 32.95s`
