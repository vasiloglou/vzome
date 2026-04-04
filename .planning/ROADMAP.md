# Roadmap: Materials Design Program

**Milestone:** `v1.1`
**Focus:** Project 3 expansion - Closed-Loop LLM Campaign MVP
**Numbering mode:** continue after `v1.0` (`Phase 10+`)

## Milestone Summary

This milestone extends the shipped Project 3 baseline from `v1.0`.

`v1.0` proved the Zomic-centered LLM ladder through:
- corpus building
- constrained `llm-generate`
- additive `llm-evaluate`
- typed acceptance packs
- dry-run `llm-suggest`

`v1.1` turns that advisory surface into an operator-governed closed-loop
campaign workflow that can propose, approve, launch, replay, and compare LLM
campaigns without bypassing the existing no-DFT pipeline.

## Phase Roadmap

## Phase 10: Closed-Loop Campaign Contract and Governance

**Goal:** define the typed campaign proposal, approval, and spec contracts that
turn `llm-suggest` from dry-run advice into materializable campaign intent.

**Deliverables**

- typed proposal, approval, campaign-spec, and launch-lineage models
- a revised `llm-suggest` output contract with executable proposal actions
- explicit dry-run versus approved-launch boundary
- file-backed campaign manifest layout rooted in acceptance packs and eval sets

**Primary requirements**

- `LLM-06`, `OPS-05`

**Success criteria**

1. An acceptance pack can produce typed proposal actions that are specific
   enough to save as a campaign spec.
2. No campaign can be launched without an explicit approval artifact.
3. Proposal and approval artifacts record acceptance-pack and eval-set lineage.
4. The existing dry-run suggestion behavior remains available as a safe mode.

**Notes**

- This phase should lock the governance boundary before anything starts
  launching new LLM runs automatically.

## Phase 11: Closed-Loop Campaign Execution Bridge

**Goal:** launch approved campaign specs through the existing LLM generation
and downstream discovery pipeline without breaking current contracts.

**Deliverables**

- CLI flow to approve and launch a campaign spec
- bridge from campaign specs into standard `llm-generate` inputs
- campaign-aware run manifests and output directories
- downstream integration that keeps `CandidateRecord` and existing stage
  artifacts intact

**Primary requirements**

- `LLM-08`, `LLM-10`, `OPS-06`

**Success criteria**

1. An approved campaign spec can launch `llm-generate` reproducibly.
2. Generated candidates remain standard artifacts that flow into the existing
   downstream pipeline.
3. Run outputs preserve lineage from acceptance pack and approval decision
   through downstream stage artifacts.
4. Existing manual `llm-generate` usage remains green and unchanged.

**Notes**

- This phase should add a controlled wrapper over `llm-generate`, not a second
  incompatible generation path.

## Phase 12: Replay, Comparison, and Operator Workflow

**Goal:** make the new closed-loop surface measurable, replayable, and safe for
regular operator use.

**Deliverables**

- replay and comparison helpers for saved campaign specs
- comparison summaries against originating acceptance packs and prior benchmark
  lanes
- operator runbook for dry-run, approval, launch, replay, and interpretation
- regression coverage for the new campaign workflow boundaries

**Primary requirements**

- `LLM-09`, `LLM-11`, `OPS-07`

**Success criteria**

1. An operator can replay a saved campaign and recover the same references and
   launch settings.
2. The workflow can compare campaign outcomes against the originating
   acceptance-pack and benchmark context.
3. The runbook explains the full closed-loop flow end to end.
4. Regression coverage protects dry-run, approval, launch, and replay
   boundaries.

**Notes**

- Local or fine-tuned inference serving stays out of scope until this workflow
  is stable and useful.

## Workstream View

### Project C: Material Design Based on LLM Training and Inference

Owns Phases 10-12 in `v1.1`.

Success condition:

- the shipped dry-run suggestion surface becomes an operator-governed,
  reproducible, replayable campaign workflow that can drive new LLM generation
  runs and measure whether they improve downstream discovery outcomes.

## Archive References

- Previous milestone roadmap: `.planning/milestones/v1.0-ROADMAP.md`
- Previous milestone requirements: `.planning/milestones/v1.0-REQUIREMENTS.md`
- Previous milestone audit: `.planning/milestones/v1.0-MILESTONE-AUDIT.md`

## Recommended Immediate Start

1. **Phase 10**
   Lock campaign proposal contracts, approval states, and manifest boundaries.
2. **Phase 11**
   Wire approved campaign specs into `llm-generate` without changing the
   existing manual path.
3. **Phase 12**
   Make the loop replayable and comparable before considering more autonomy.
