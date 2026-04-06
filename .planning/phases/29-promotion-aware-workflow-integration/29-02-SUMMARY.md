# Phase 29 Plan 02 Summary

Kept replay, compare, and serving-benchmark flows stable after checkpoint
promotions change later.

## Delivered

- Updated replay to keep using the recorded family checkpoint identity instead
  of silently following a later promoted default, while still rejecting true
  model or fingerprint drift.
- Allowed replay-only resolution of retired historical family members so prior
  launches remain reproducible and auditable.
- Surfaced checkpoint routing details in comparison and serving-benchmark
  summary output so operators can see whether a run came from a promoted
  default, an explicit pin, or the baseline path.

## Verification

- `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py tests/test_llm_serving_benchmark_core.py -x -v`
  - Result: `23 passed in 0.29s`

## Outcome

Promotion state can keep evolving for new runs without breaking historical
replay or making comparison and benchmark artifacts ambiguous.
