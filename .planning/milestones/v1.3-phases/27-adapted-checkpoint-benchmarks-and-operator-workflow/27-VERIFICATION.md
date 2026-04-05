---
phase: 27-adapted-checkpoint-benchmarks-and-operator-workflow
verified: 2026-04-05T15:41:00Z
status: passed
score: 2/2 requirements verified
---

# Phase 27 Verification Report

## Requirement Coverage

| Requirement | Status | Proof |
| --- | --- | --- |
| `LLM-22` | ✓ VERIFIED | `27-01-SUMMARY.md`, `27-03-SUMMARY.md`, `serving_benchmark.py`, `tests/test_llm_serving_benchmark_core.py`, `tests/test_real_mode_pipeline.py` |
| `OPS-12` | ✓ VERIFIED | `27-02-SUMMARY.md`, `RUNBOOK.md`, `configuration-reference.md`, `llm-integration.md`, `pipeline-stages.md`, `tests/test_cli.py` |

## Requirement Proof

### LLM-22

The adapted checkpoint now has a dedicated benchmark path against the baseline
local lane on one shared acceptance-pack context. The benchmark summary keeps
adapted-vs-baseline metrics explicit and emits a dedicated improvement line
when the adapted checkpoint outperforms the baseline on parse, compile, or
generation success.

### OPS-12

The workflow now ships explicit operator guidance for:

- checkpoint registration
- adapted-lane generation
- smoke testing and full adapted-vs-baseline benchmarking
- rollback to the baseline local lane

## Residual Caveat

The repository still does not ship checkpoint weights. The operational proof is
therefore file-backed and benchmark-driven, with real checkpoint bytes supplied
by the operator.

## Verification Basis

- Broad milestone rerun:
  - `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_llm_generate_cli.py tests/test_llm_serving_benchmark_core.py tests/test_llm_replay_core.py tests/test_real_mode_pipeline.py tests/test_llm_launch_schema.py tests/test_llm_runtime.py tests/test_cli.py -x -v`
  - Result: `75 passed in 25.48s`
- Full-suite evidence:
  - `cd materials-discovery && uv run pytest`
  - Result: `421 passed, 3 skipped, 1 warning in 32.95s`

## Verification Verdict

**Phase 27 passed.**
