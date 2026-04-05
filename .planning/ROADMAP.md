# Roadmap: Materials Design Program

**Milestone:** `v1.3`
**Focus:** Project 3 expansion - Zomic-Native Local Checkpoint MVP
**Numbering mode:** continue after `v1.2` (`Phase 25+`)

## Milestone Summary

This milestone extends the shipped `v1.2` local and specialized serving
workflow.

`v1.2` proved that the platform can:
- run hosted, local, and specialized lanes inside one governed workflow
- preserve launch, replay, compare, and benchmark compatibility across lanes
- benchmark those lanes honestly with smoke-first operator workflow

`v1.3` turns that serving surface into the first real Zomic-adapted local
checkpoint workflow:
- adapted checkpoints become first-class local serving lanes
- checkpoint lineage and registration become auditable and reproducible
- operators can compare adapted checkpoints against baseline local lanes before
  any broader training-automation milestone

## Phase Roadmap

## Phase 25: Zomic Checkpoint Artifact and Lineage Contracts

**Goal:** define the checkpoint artifact, registration, and lineage contract
needed to treat a Zomic-adapted local checkpoint as a first-class serving lane.

**Deliverables**

- additive checkpoint metadata and registration contract under
  `materials_discovery/llm/`
- config/schema support for adapted checkpoint identity, base model, revision,
  and lineage inputs
- deterministic loading and validation for adapted local checkpoint lanes
- clear operator-facing errors for incomplete, incompatible, or unresolvable
  checkpoint registrations

**Primary requirements**

- `LLM-19`, `OPS-11`

**Success criteria**

1. An operator can register an adapted checkpoint artifact without inventing a
   side-channel outside the existing config and manifest surface.
2. Checkpoint lineage captures base model, adaptation artifact, corpus/eval
   provenance, and serving identity cleanly.
3. Invalid or incompatible checkpoint registrations fail early with clear
   diagnostics.
4. Existing hosted, local baseline, and specialized lanes remain
   backward-compatible.

**Notes**

- This phase should define the adapted-checkpoint contract, not require full
  automated training orchestration.

## Phase 26: Zomic-Adapted Local Generation Integration

**Goal:** run at least one adapted local checkpoint through the shipped
generation and campaign workflow without breaking the standard artifact family.

**Deliverables**

- one adapted checkpoint lane wired through `llm-generate`
- campaign launch and replay compatibility for adapted checkpoint runs
- compare and benchmark compatibility for adapted-vs-baseline evaluation
- additive serving/checkpoint lineage preserved across standard artifacts

**Primary requirements**

- `LLM-20`, `LLM-21`

**Success criteria**

1. At least one adapted checkpoint can execute through `llm-generate` and
   approved campaign launches.
2. Adapted checkpoint runs remain compatible with launch, replay, compare, and
   benchmark helpers rather than forking a new workflow.
3. Standard `CandidateRecord` and manifest contracts remain intact.
4. Operators can still fall back to baseline local lanes cleanly.

**Notes**

- The checkpoint may come from an external or manual adaptation step; this
  milestone focuses on operational integration, not full automated training.

## Phase 27: Adapted Checkpoint Benchmarks and Operator Workflow

**Goal:** make adapted checkpoints measurable and operator-usable through
adapted-vs-baseline benchmarks, smoke tests, rollback guidance, and final
workflow docs.

**Deliverables**

- benchmark workflow comparing an adapted checkpoint against an unadapted local
  baseline on one shared context
- operator-facing smoke-test and rollback procedure for adapted checkpoints
- runbook updates for registration, checkpoint selection, failure diagnosis,
  and comparison interpretation
- regression coverage protecting the adapted-checkpoint workflow boundary

**Primary requirements**

- `LLM-22`, `OPS-12`

**Success criteria**

1. Operators can compare adapted and baseline local checkpoints against the
   same benchmark context without hand-assembling artifacts.
2. At least one adapted checkpoint shows a measurable improvement on the
   defined Zomic validity or compile/conversion acceptance surface.
3. The runbook explains registration, smoke testing, rollback, and when to
   prefer the adapted checkpoint.
4. The milestone ends with an operator-usable adapted-checkpoint workflow, not
   just a one-off experiment.

**Notes**

- Fully autonomous campaign execution and large-scale checkpoint orchestration
  remain out of scope until this adapted-checkpoint workflow proves reliable.

## Scope Boundaries

- This milestone does **not** add fully autonomous campaign execution.
- This milestone does **not** introduce broad checkpoint farming or automated
  checkpoint promotion pipelines.
- This milestone does **not** require foundation-model training from scratch.
- This milestone does **not** make chemistry breadth the headline.
- This milestone does **not** replace the current CLI/file-backed workflow with
  a UI-first orchestration layer.

## Previous Milestones

- `v1.2` archive: `.planning/milestones/v1.2-ROADMAP.md`
- `v1.1` archive: `.planning/milestones/v1.1-ROADMAP.md`
- `v1.0` archive: `.planning/milestones/v1.0-ROADMAP.md`
