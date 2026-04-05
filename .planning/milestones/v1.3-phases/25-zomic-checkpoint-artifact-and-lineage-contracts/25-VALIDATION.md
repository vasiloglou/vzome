---
phase: 25
slug: zomic-checkpoint-artifact-and-lineage-contracts
status: complete
nyquist_compliant: true
created: 2026-04-05
---

# Phase 25 Validation

## Quick Commands

- `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_llm_replay_core.py -x -v`
- `cd materials-discovery && uv run pytest`

## Verification Map

| Task | Requirement | Evidence |
| --- | --- | --- |
| 25-01 schema and storage contracts | `LLM-19`, `OPS-11` | `tests/test_llm_checkpoint_registry.py` |
| 25-02 registration CLI and resolver | `LLM-19`, `OPS-11` | `tests/test_llm_checkpoint_cli.py`, `tests/test_llm_checkpoint_registry.py` |
| 25-03 serving identity threading | `LLM-19`, `OPS-11` | `tests/test_llm_replay_core.py`, `tests/test_llm_generate_cli.py` |

## Results

- Focused rerun: `16 passed in 0.35s`
- Full suite evidence retained at milestone closeout: `421 passed, 3 skipped, 1 warning in 32.95s`
