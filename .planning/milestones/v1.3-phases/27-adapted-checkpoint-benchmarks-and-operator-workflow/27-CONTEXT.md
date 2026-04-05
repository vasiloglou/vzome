# Phase 27: Adapted Checkpoint Benchmarks and Operator Workflow

**Gathered:** 2026-04-05  
**Mode:** Autonomous defaults from the v1.3 roadmap

## Phase Boundary

Turn the adapted checkpoint from a code-only capability into an operator-usable
workflow with explicit benchmark interpretation and rollback guidance.

## Locked Decisions

- Adapted-vs-baseline comparison uses one shared acceptance-pack context.
- Benchmark summaries must surface adapted-checkpoint improvement explicitly
  instead of forcing operators to infer it manually.
- Rollback remains the baseline local lane, not a hidden fallback.
- The runbook must cover registration, smoke testing, benchmark execution, and
  rollback.
