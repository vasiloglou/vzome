# Roadmap: Materials Design Program

**Milestone:** `v1.4`
**Focus:** Project 3 expansion - Adapted Checkpoint Lifecycle and Promotion MVP
**Numbering mode:** continue after `v1.3` (`Phase 28+`)

## Milestone Summary

This milestone extends the shipped `v1.3` adapted-checkpoint workflow.

`v1.3` proved that the platform can:
- register one adapted checkpoint with auditable lineage
- run one adapted checkpoint through the shipped generation workflow
- replay and benchmark that checkpoint safely against a baseline local lane
- guide operators through registration, smoke testing, and rollback

`v1.4` turns that one-checkpoint proof into a real lifecycle surface:
- multiple checkpoints can coexist per system
- promotion, pinning, rollback, and retirement become file-backed workflow
  actions
- operators can compare candidate checkpoints against the promoted default
  without hand-wiring a second workflow family

## Phase Roadmap

## Phase 28: Checkpoint Lifecycle and Promotion Contracts

**Goal:** define the lifecycle state, registry, and promotion artifacts needed
to manage more than one adapted checkpoint per system safely.

**Deliverables**

- additive lifecycle models for candidate, promoted, pinned, and retired
  checkpoint states
- file-backed registry and promotion artifacts under the existing
  `data/llm_checkpoints/` surface
- deterministic validation for conflicting promotion or stale lifecycle state
- operator-facing diagnostics for incompatible or ambiguous active-checkpoint
  selection

**Primary requirements**

- `LLM-23`, `OPS-13`

**Success criteria**

1. Operators can manage more than one adapted checkpoint per system without
   losing the strict lineage guarantees from `v1.3`.
2. Promotion and retirement are explicit file-backed actions, not config
   comment conventions.
3. Ambiguous or conflicting active-checkpoint state fails early with clear
   diagnostics.
4. The new lifecycle artifacts remain additive to the existing checkpoint
   registration contract.

## Phase 29: Promotion-Aware Workflow Integration

**Goal:** make promoted and explicitly pinned checkpoints resolve cleanly
through the shipped generation, campaign, and replay workflow.

**Deliverables**

- promotion-aware checkpoint resolution for `llm-generate`
- campaign launch and replay support for promoted-vs-pinned checkpoint choice
- compatibility for compare, replay, and benchmark artifacts when the active
  checkpoint changes
- explicit rollback-to-prior-checkpoint and baseline-lane semantics

**Primary requirements**

- `LLM-24`, `LLM-26`

**Success criteria**

1. Operators can run with the promoted default checkpoint or pin a specific
   checkpoint deliberately.
2. Promotion and rollback do not fork the workflow into a checkpoint-only path.
3. Replay and compare preserve enough lifecycle identity to explain which
   checkpoint actually ran.
4. The baseline local lane remains an explicit rollback path.

## Phase 30: Promotion Benchmarks and Operator Lifecycle Workflow

**Goal:** make checkpoint promotion and retirement benchmark-backed and usable
for operators.

**Deliverables**

- benchmark workflow comparing candidate checkpoints, the promoted checkpoint,
  and the baseline local lane on one shared context
- operator-facing promotion, rollback, and retirement procedure
- runbook and developer-doc updates for checkpoint lifecycle management
- regression coverage protecting the new lifecycle workflow boundary

**Primary requirements**

- `LLM-25`, `OPS-14`

**Success criteria**

1. Operators can compare candidate and promoted checkpoints on one shared
   benchmark context without assembling ad hoc artifacts.
2. Promotion recommendations are grounded in benchmark evidence rather than
   manual file editing.
3. The docs explain promotion, pinning, rollback, and retirement clearly.
4. The milestone ends with a small but real checkpoint-lifecycle workflow, not
   just another schema layer.

## Scope Boundaries

- This milestone does **not** automate model training jobs end to end.
- This milestone does **not** add large-scale checkpoint farming or tournament
  infrastructure.
- This milestone does **not** introduce fully autonomous campaign execution.
- This milestone does **not** replace the current CLI/file-backed workflow with
  a UI-first checkpoint-management layer.

## Previous Milestones

- `v1.3` archive: `.planning/milestones/v1.3-ROADMAP.md`
- `v1.2` archive: `.planning/milestones/v1.2-ROADMAP.md`
- `v1.1` archive: `.planning/milestones/v1.1-ROADMAP.md`
- `v1.0` archive: `.planning/milestones/v1.0-ROADMAP.md`
