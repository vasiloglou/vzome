---
phase: 25-zomic-checkpoint-artifact-and-lineage-contracts
verified: 2026-04-05T15:41:00Z
status: passed
score: 2/2 requirements verified
---

# Phase 25 Verification Report

## Requirement Coverage

| Requirement | Status | Proof |
| --- | --- | --- |
| `LLM-19` | ✓ VERIFIED | `25-01-SUMMARY.md`, `25-02-SUMMARY.md`, `25-03-SUMMARY.md`, `llm/checkpoints.py`, `cli.py`, `tests/test_llm_checkpoint_registry.py`, `tests/test_llm_checkpoint_cli.py` |
| `OPS-11` | ✓ VERIFIED | `25-02-SUMMARY.md`, `25-03-SUMMARY.md`, `schema.py`, `launch.py`, `replay.py`, `tests/test_llm_replay_core.py`, `tests/test_llm_generate_cli.py` |

## Requirement Proof

### LLM-19

Operators can register a Zomic-adapted local checkpoint with pinned base model,
adaptation artifact, corpus manifest, eval-set manifest, and optional
acceptance-pack lineage through one typed spec and one CLI command. The
registration is stored deterministically and keyed by a stable checkpoint
fingerprint.

### OPS-11

Adapted checkpoints now record auditable lineage for base model, adaptation
method, corpus/eval provenance, revision, path, and checkpoint fingerprint.
Incompatible registrations or lane mismatches fail early instead of surfacing
later as generic provider errors.

## Verification Basis

- Focused rerun:
  - `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_llm_replay_core.py -x -v`
  - Result: `16 passed in 0.35s`
- Full-suite evidence:
  - `cd materials-discovery && uv run pytest`
  - Result: `421 passed, 3 skipped, 1 warning in 32.95s`

## Verification Verdict

**Phase 25 passed.**
