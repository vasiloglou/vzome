# Phase 28 Plan 02 Summary

Turned the checkpoint lifecycle contract into real file-backed registry actions
and operator CLI commands.

## Delivered

- Added checkpoint-family lifecycle loading, candidate auto-enrollment during
  registration, idempotent promotion, safe retirement, and revision-based
  stale-write protection in `llm/checkpoints.py`.
- Preserved the v1.3 registration contract while validating explicit
  `checkpoint_family` plus `checkpoint_id` pins and keeping retired checkpoints
  replay-safe through immutable registration artifacts.
- Added `llm-list-checkpoints`, `llm-promote-checkpoint`, and
  `llm-retire-checkpoint` as thin CLI wrappers with structured JSON output and
  clear retry guidance for stale or unsafe operations.

## Task Commits

- Task 1: `90684a6a` — `feat: add checkpoint lifecycle registry actions`
- Task 2: `d2cf61ff` — `feat: add checkpoint lifecycle cli commands`

## Verification

- `uv run pytest tests/test_llm_checkpoint_registry.py -x -v`
  - Result: `16 passed in 0.32s`
- `uv run pytest tests/test_llm_checkpoint_cli.py -x -v`
  - Result: `6 passed in 0.37s`
- `uv run pytest tests/test_cli.py -x -v`
  - Result: `16 passed in 0.41s`
- `uv run pytest tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_cli.py -x -v`
  - Result: `38 passed in 0.70s`

## Outcome

Operators can now register, inspect, promote, and retire checkpoint-family
state audibly and deterministically, while promoted-default execution wiring
remains correctly deferred to Phase 29.
