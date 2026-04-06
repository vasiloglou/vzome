# Phase 28 Plan 03 Summary

Closed the lifecycle contract with committed example specs, replay-safe
retirement proof, and additive operator docs that keep the Phase 29 boundary
explicit.

## Delivered

- Added committed promotion and retirement action examples for the
  `adapted-al-cu-fe` checkpoint family under `configs/llm/`.
- Proved that a checkpoint can be retired in lifecycle state without breaking
  replay when a historical launch bundle still pins that checkpoint by
  registration and fingerprint.
- Documented `checkpoint_family`, lifecycle storage, lifecycle CLI JSON shape,
  demotion-by-promotion semantics, placeholder evidence-path intent, and the
  explicit deferral of promoted-default execution wiring to Phase 29.

## Task Commits

- Task 1: `6623ad2c` — `feat: add checkpoint lifecycle example specs`
- Task 2: `402ce739` — `docs: explain checkpoint lifecycle contracts`

## Verification

- `uv run pytest tests/test_llm_replay_core.py tests/test_llm_checkpoint_cli.py -x -v`
  - Result: `18 passed in 0.62s`
- `uv run pytest tests/test_cli.py -x -v`
  - Result: `16 passed in 0.61s`
- `uv run pytest tests/test_llm_launch_schema.py tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_llm_replay_core.py tests/test_cli.py -x -v`
  - Result: `66 passed in 0.84s`
- `git diff --check`
  - Result: clean

## Outcome

Phase 28 now ships a real checkpoint lifecycle contract that operators can read
and exercise safely, while the workflow-aware promoted-default execution work
remains clearly queued for Phase 29.
