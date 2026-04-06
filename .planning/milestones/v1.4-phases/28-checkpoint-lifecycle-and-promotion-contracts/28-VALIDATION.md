---
phase: 28
slug: checkpoint-lifecycle-and-promotion-contracts
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
last_updated: "2026-04-06T01:00:51Z"
---

# Phase 28 — Validation Record

## Verification Runs

- `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_checkpoint_cli.py -x -v`
  - Result: `18 passed in 0.62s`
- `cd materials-discovery && uv run pytest tests/test_cli.py -x -v`
  - Result: `16 passed in 0.61s`
- `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_llm_replay_core.py tests/test_cli.py -x -v`
  - Result: `66 passed in 0.84s`
- `git diff --check`
  - Result: clean

## Covered Requirements

- `LLM-23` — checkpoint families can hold multiple members with explicit
  lifecycle state while keeping immutable registration and fingerprint
  guarantees intact
- `OPS-13` — lifecycle actions are file-backed, auditable, and fail clearly on
  stale or conflicting state

## Sign-Off

Phase 28 is validated complete and ready to hand off to promotion-aware
workflow integration.
