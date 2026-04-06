---
one-liner: Committed the candidate-pinned config and three-way lifecycle benchmark spec, then proved the promoted-vs-candidate-vs-baseline workflow offline.
---

# Phase 30 Plan 02 Summary

Committed and proved the benchmark-backed checkpoint promotion path on one
shared acceptance-pack context.

## Delivered

- Added `configs/systems/al_cu_fe_llm_adapted_candidate.yaml` as the committed
  explicit family pin for a candidate checkpoint.
- Added `configs/llm/al_cu_fe_checkpoint_lifecycle_benchmark.yaml` with
  baseline-local, promoted-default, and candidate-checkpoint generation
  targets.
- Extended the real-mode offline proof so it stages promoted and candidate
  checkpoints inside the same family, runs the lifecycle benchmark, and checks
  for explicit promotion plus rollback guidance in the benchmark summary.

## Verification

- `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -x -v`
  - Result: `14 passed in 14.92s`

## Outcome

Operators now have a committed example benchmark that compares the family
default, a candidate member, and the baseline lane without assembling ad hoc
artifacts by hand.
