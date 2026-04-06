---
one-liner: Added explicit lifecycle benchmark roles so serving-benchmark summaries can recommend promote, keep, and rollback behavior from structured target intent.
---

# Phase 30 Plan 01 Summary

Gave checkpoint lifecycle benchmarks explicit target roles and role-aware
recommendation lines.

## Delivered

- Added `checkpoint_benchmark_role` to serving-benchmark launch targets with
  typed values for the rollback baseline, the promoted default, and the
  candidate checkpoint.
- Reused those roles in `serving_benchmark.py` so benchmark summaries can
  recommend promotion or retention without relying on target-name heuristics.
- Kept the prior adapted-vs-baseline summary path intact while extending
  schema/core coverage to the new lifecycle-benchmark semantics.

## Verification

- `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py -x -v`
  - Result: `12 passed in 0.48s`

## Outcome

Serving benchmarks can now describe lifecycle intent directly, which gives the
operator workflow a reliable promote-or-keep decision seam.
