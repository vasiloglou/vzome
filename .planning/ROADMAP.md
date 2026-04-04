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

## Phase 13: Phase 10 Verification and Governance Audit Closure

**Goal:** close the audit gaps left after Phase 10 by producing the missing
verification chain, finalizing validation status, and restoring requirement
traceability for the closed-loop governance boundary.

**Deliverables**

- `10-VERIFICATION.md` with requirement-level proof for campaign proposal,
  approval, and governance behavior
- finalized `10-VALIDATION.md` with explicit Nyquist/verification status
- refreshed traceability and requirement state for `LLM-06` and `OPS-05`
- audit-ready evidence map back to Phase 10 summaries and tests

**Primary requirements**

- `LLM-06`, `OPS-05`

**Success criteria**

1. Phase 10 has a formal verification artifact that closes the missing-proof gap
   identified in the v1.1 audit.
2. Requirement traceability no longer claims Phase 10 is complete without
   verification evidence.
3. The dry-run versus approval governance boundary is proven in an audit-ready
   form.
4. The audit can consume the Phase 10 evidence without relying on manual
   interpretation of summaries alone.

**Notes**

- This is a gap-closure phase created directly from the v1.1 milestone audit.

## Phase 14: Phase 11 Launch and Lineage Audit Closure

**Goal:** close the audit gaps left after Phase 11 by formalizing launch,
lineage, and downstream-continuation verification for approved campaign specs.

**Deliverables**

- `11-VERIFICATION.md` with requirement-level proof for launch, lineage, and
  downstream artifact continuity
- finalized `11-VALIDATION.md` with explicit Nyquist/verification status
- refreshed traceability and requirement state for `LLM-08`, `LLM-10`, and
  `OPS-06`
- audit-ready evidence map back to Phase 11 summaries and launch-lineage tests

**Primary requirements**

- `LLM-08`, `LLM-10`, `OPS-06`

**Success criteria**

1. Phase 11 has a formal verification artifact that proves approved campaign
   specs launch reproducibly.
2. Lineage from acceptance pack through downstream manifests is documented in an
   audit-ready form.
3. Requirement traceability reflects the audit-closure work instead of stale
   pending or partially proven status.
4. The audit can verify Phase 11 without re-deriving evidence from multiple
   summaries by hand.

**Notes**

- This is a gap-closure phase created directly from the v1.1 milestone audit.

## Phase 15: Phase 12 Replay and Operator Workflow Audit Closure

**Goal:** close the audit gaps left after Phase 12 by formalizing replay,
comparison, and operator-workflow verification, including any missing
supporting summary artifacts the audit expects.

**Deliverables**

- `12-VERIFICATION.md` with requirement-level proof for replay, comparison, and
  operator workflow safety
- any missing summary or validation artifacts required to make Phase 12
  audit-ready
- refreshed traceability and requirement state for `LLM-09`, `LLM-11`, and
  `OPS-07`
- audit-ready evidence map back to replay/compare tests and runbook coverage

**Primary requirements**

- `LLM-09`, `LLM-11`, `OPS-07`

**Success criteria**

1. Phase 12 has a formal verification artifact that proves replay and
   comparison behavior in an audit-ready form.
2. The operator workflow is supported by explicit evidence, not only docs and a
   late summary.
3. Requirement traceability reflects the closure work and removes the current
   partial-proof state.
4. The milestone can be rerun through audit without the current Phase 12
   verification gap.

**Notes**

- This is a gap-closure phase created directly from the v1.1 milestone audit.

## Workstream View

### Project C: Material Design Based on LLM Training and Inference

Owns Phases 10-15 in `v1.1`.

Success condition:

- the shipped dry-run suggestion surface becomes an operator-governed,
  reproducible, replayable campaign workflow that can drive new LLM generation
  runs and measure whether they improve downstream discovery outcomes
- the full v1.1 closed-loop workflow is also formally audit-ready, with phase
  verification and requirement traceability aligned to the delivered behavior

## Archive References

- Previous milestone roadmap: `.planning/milestones/v1.0-ROADMAP.md`
- Previous milestone requirements: `.planning/milestones/v1.0-REQUIREMENTS.md`
- Previous milestone audit: `.planning/milestones/v1.0-MILESTONE-AUDIT.md`

## Recommended Immediate Start

1. **Phase 13**
   Close the missing Phase 10 verification and governance-proof gap.
2. **Phase 14**
   Close the missing Phase 11 launch and lineage verification gap.
3. **Phase 15**
   Close the missing Phase 12 replay and operator-workflow verification gap.
