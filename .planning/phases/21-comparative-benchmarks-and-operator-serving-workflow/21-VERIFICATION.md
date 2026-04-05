---
phase: 21-comparative-benchmarks-and-operator-serving-workflow
verified: 2026-04-05T08:00:07Z
status: passed
score: 2/2 requirements verified
---

# Phase 21 Verification Report

**Phase Goal:** make the new serving lanes usable and measurable for operators
through comparative benchmarks, smoke tests, and a stable runbook.  
**Verified:** 2026-04-05T08:00:07Z  
**Status:** passed

## Requirement Coverage

| Requirement | Status | Proof |
| --- | --- | --- |
| `LLM-17` | ✓ VERIFIED | Hosted, local, and specialized lanes can be benchmarked against one shared context through the shipped benchmark contract, CLI, example configs, and real-mode proof coverage across `21-01-SUMMARY.md`, `21-02-SUMMARY.md`, `21-03-SUMMARY.md`, `serving_benchmark.py`, `cli.py`, and the refreshed Phase 24 rerun (`40 passed`). |
| `OPS-10` | ✓ VERIFIED | The runbook and operator workflow document smoke-first setup, explicit fallback rules, reproducible benchmark comparison, and operator tradeoff interpretation across `21-03-SUMMARY.md`, `RUNBOOK.md`, the developer docs, and the refreshed Phase 24 rerun. |

**Score:** 2/2 requirements verified

## Requirement Proof

### LLM-17

**Claim:** The platform can benchmark hosted, local, and specialized lanes
against the same acceptance-pack or benchmark context so operators can judge
quality, cost, and workflow tradeoffs.

**Implementation surface**
- `materials-discovery/src/materials_discovery/llm/serving_benchmark.py`
- `materials-discovery/src/materials_discovery/llm/schema.py`
- `materials-discovery/src/materials_discovery/llm/storage.py`
- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/configs/llm/al_cu_fe_serving_benchmark.yaml`
- `materials-discovery/configs/llm/sc_zn_serving_benchmark.yaml`

**Summary evidence**
- [21-01-SUMMARY.md](/Users/nikolaosvasiloglou/github-repos/vzome/.planning/phases/21-comparative-benchmarks-and-operator-serving-workflow/21-01-SUMMARY.md)
- [21-02-SUMMARY.md](/Users/nikolaosvasiloglou/github-repos/vzome/.planning/phases/21-comparative-benchmarks-and-operator-serving-workflow/21-02-SUMMARY.md)
- [21-03-SUMMARY.md](/Users/nikolaosvasiloglou/github-repos/vzome/.planning/phases/21-comparative-benchmarks-and-operator-serving-workflow/21-03-SUMMARY.md)

**Focused test evidence**
- `tests/test_llm_serving_benchmark_schema.py`
- `tests/test_llm_serving_benchmark_core.py`
- `tests/test_llm_serving_benchmark_cli.py`
- `tests/test_real_mode_pipeline.py`
- Phase 24 rerun result: `40 passed in 26.84s`

**Verdict:** The benchmark surface is shared-context, smoke-first, explicit
about missing metrics, and operator-usable across hosted, local, and
specialized targets.

### OPS-10

**Claim:** The workflow ships with an operator runbook for setup, smoke tests,
lane fallback, and reproducible benchmark comparison across hosted and
local/specialized serving paths.

**Implementation surface**
- `materials-discovery/RUNBOOK.md`
- `materials-discovery/developers-docs/configuration-reference.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/pipeline-stages.md`
- `materials-discovery/src/materials_discovery/cli.py`

**Summary evidence**
- [21-02-SUMMARY.md](/Users/nikolaosvasiloglou/github-repos/vzome/.planning/phases/21-comparative-benchmarks-and-operator-serving-workflow/21-02-SUMMARY.md)
- [21-03-SUMMARY.md](/Users/nikolaosvasiloglou/github-repos/vzome/.planning/phases/21-comparative-benchmarks-and-operator-serving-workflow/21-03-SUMMARY.md)

**Focused test evidence**
- `tests/test_llm_serving_benchmark_cli.py`
- `tests/test_cli.py`
- `tests/test_real_mode_pipeline.py`
- Phase 24 rerun result: `40 passed in 26.84s`

**Verdict:** The operator workflow is documented, regression-backed, and
explicit about smoke-only execution, no-silent-fallback rules, and benchmark
artifact expectations.

## Residual Caveats

- The specialized lane in v1.2 remains evaluation-primary in the benchmark
  examples; the milestone does not claim mature direct Zomic-native specialized
  generation.
- `mdisc` still expects model servers to be provisioned externally rather than
  launching them itself.

## Verification Basis

- Fresh focused rerun:
  - `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v`
  - Result: `40 passed in 26.84s`
- Shipped full-suite evidence from Phase 21:
  - `410 passed, 3 skipped, 1 warning in 37.07s`
- Validation source:
  - [21-VALIDATION.md](/Users/nikolaosvasiloglou/github-repos/vzome/.planning/phases/21-comparative-benchmarks-and-operator-serving-workflow/21-VALIDATION.md)

## Verification Verdict

**Gap closed.**

Phase 21 now has an explicit proof chain from requirements to summaries,
tests, docs, validation, and a formal verification report.

---
_Verified: 2026-04-05T08:00:07Z_  
_Verifier: Codex (Phase 24 audit closure)_
