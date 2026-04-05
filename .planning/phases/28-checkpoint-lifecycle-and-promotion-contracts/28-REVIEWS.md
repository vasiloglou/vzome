---
phase: 28
reviewers: [gemini, claude]
reviewed_at: 2026-04-05T21:14:30Z
plans_reviewed:
  - 28-01-PLAN.md
  - 28-02-PLAN.md
  - 28-03-PLAN.md
---

# Cross-AI Plan Review — Phase 28

## Gemini Review

# Implementation Plan Review: Phase 28 (Checkpoint Lifecycle and Promotion Contracts)

## 1. Summary
The plans for Phase 28 provide a robust, surgical approach to evolving the platform from a single-checkpoint registration model to a managed lifecycle fleet. By strictly separating immutable registration facts from mutable lifecycle state, the plans satisfy the auditability goals of `OPS-13` while preserving the lineage guarantees of `LLM-23`. The sequencing is strong: schema and storage first, lifecycle logic and CLI next, then examples and docs last. Deferring execution-time resolution to Phase 29 is a clear strength because it keeps this phase narrow.

## 2. Strengths
- Hybrid lifecycle model is the right architecture for immutable checkpoint facts and mutable promoted/retired state.
- Stale-write protection is a mature operational control for a file-backed registry.
- Replay integrity remains first-class because retired checkpoints stay registered and fingerprint-verifiable.
- The plans stay additive and protect `v1.3` compatibility.
- Deterministic storage under `data/llm_checkpoints/` matches the repo’s auditability pattern.

## 3. Concerns
- **MEDIUM:** The behavior when a family exists but nothing is promoted yet is still underspecified.
- **MEDIUM:** Retiring the active promoted checkpoint should fail with especially clear remediation guidance for operators.
- **LOW:** `llm-list-checkpoints` may become noisy as family size grows unless the output has a summary-first shape.

## 4. Suggestions
- Add explicit resolver behavior for the “no promoted member yet” case.
- Make retirement failures point operators toward the replacement or rollback path.
- Consider a more compact summary-first list view if many checkpoints accumulate.

## 5. Risk Assessment
**Overall Risk: LOW**

The work is additive, deliberately phased, and mostly contract-boundary work rather than runtime integration. The focused tests and backward-compatibility constraints reduce regression risk substantially.

---

## Claude Review

# Phase 28 Plan Review: Checkpoint Lifecycle and Promotion Contracts

## Overall Summary
These three plans form a well-structured, wave-ordered implementation of checkpoint lifecycle management. The bottom-up ordering is sound: schema and storage contracts, then lifecycle actions and CLI, then examples, docs, and compatibility proof. The strongest point is scope discipline around keeping promoted-default execution in Phase 29. The main remaining ambiguity is the lifecycle index concurrency and family-key contract.

## Plan 28-01: Schema and Storage Contract

### Strengths
- Clean separation between schema/config work and storage-path work.
- Backward compatibility is treated as a first-class requirement.
- Reusing the existing `data/llm_checkpoints/` root is the right move.
- The `must_haves` guardrails are concrete and useful.

### Concerns
- **MEDIUM:** `checkpoint_family` key derivation is unspecified. The plan should say whether the family is just an opaque configured string or something derived from system/template identity.
- **LOW:** Lifecycle artifacts should likely have explicit schema-version constants.
- **LOW:** If `checkpoint_family` gets added to registration models, fingerprint computation must stay unchanged so existing registrations remain idempotent.

### Suggestions
- State explicitly that `checkpoint_family` is metadata and does not affect fingerprint computation.
- Add a test proving the same checkpoint keeps the same fingerprint with and without `checkpoint_family`.
- Consider naming lifecycle schema-version constants directly in the contract.

### Risk Assessment
**LOW**

Plan 28-01 is narrow, additive, and well protected by backward-compatibility requirements.

## Plan 28-02: Lifecycle Actions and CLI

### Strengths
- Stale-write guards are required explicitly.
- Retiring the promoted checkpoint without a safe path is blocked.
- CLI is kept as a thin wrapper over `checkpoints.py`.
- The plan clearly refuses to wire promoted defaults into runtime execution yet.

### Concerns
- **MEDIUM:** The lifecycle index concurrency model is still implicit. The plan should specify whether stale-write protection is based on a monotonic revision, a hash check, or something equivalent.
- **MEDIUM:** The non-existent-family / no-index-yet case is not clearly specified. The plan should define whether the lifecycle index is created lazily or eagerly.
- **LOW:** The helper export list should include an explicit list/enumeration helper for the `llm-list-checkpoints` CLI.

### Suggestions
- Specify the stale-write mechanism directly in the plan.
- Clarify when family indexes are created.
- Add an explicit listing helper to the exported helper surface.

### Risk Assessment
**MEDIUM**

This wave carries the most ambiguity because stale-write semantics and initial index creation could drift if left open.

## Plan 28-03: Examples, Docs, and Compatibility Proof

### Strengths
- Committed example specs are the right shape for both docs and fixtures.
- Replay compatibility is tested against fingerprint identity instead of mutable lifecycle state.
- The explicit Phase 28 / Phase 29 docs boundary is strong.
- The additive-docs instruction is the right editorial constraint.

### Concerns
- **LOW:** Docs quality is only weakly covered by the automated verify command and still needs human judgment.
- **LOW:** Example evidence references may be structural rather than live paths; the plan should stay explicit about that.
- **LOW:** Replay tests should stay narrowly focused on lifecycle/replay boundary coverage, not re-test broad replay logic.

### Suggestions
- State clearly that example evidence paths are structural references if they are not expected to exist in-repo.
- Consider a manual-only validation note for docs quality.

### Risk Assessment
**LOW**

This is largely docs, examples, and compatibility proof with minimal production risk.

## Cross-Plan View

### Strengths
- Dependency ordering is correct and clean.
- Requirement coverage is sound for `LLM-23` and `OPS-13`.
- Scope discipline is strong and the Phase 29 boundary is well defended.

### Top Improvements
1. Specify the stale-write guard mechanism.
2. State explicitly that `checkpoint_family` does not affect fingerprint computation.
3. Add a listing helper to match the lifecycle CLI surface.

### Overall Risk
**LOW-MEDIUM**

The plans are solid overall. The main residual risk is the underspecified lifecycle index concurrency and creation policy.

---

## Codex Review

Skipped intentionally because the current runtime is already Codex, so it would not have been an independent external review.

---

## Consensus Summary

Phase 28 looks low risk overall and well structured. Both reviewers liked the additive hybrid-lifecycle architecture, the wave ordering, and the explicit refusal to pull promoted-default execution into this phase. The main work before execution is to tighten a few contract details so the implementation does not have to invent them ad hoc.

### Agreed Strengths
- The plan sequence is strong: schema/storage first, lifecycle actions second, examples/docs/compatibility proof last.
- The hybrid model is the right architecture: immutable checkpoint registration facts plus mutable family lifecycle state.
- Backward compatibility and replay/audit integrity are treated as first-class constraints.
- The boundary to Phase 29 is clear and keeps this phase from overreaching.

### Agreed Concerns
- The initial or empty-family state needs clearer rules: what happens when a family exists but no checkpoint is promoted yet, or when a family index does not exist yet.
- The stale-write/concurrency contract should be more explicit so lifecycle actions do not invent different protection semantics during execution.
- Operator-facing lifecycle semantics should remain sharp around promotion versus per-run pinning and around retirement of the active promoted checkpoint.

### Divergent Views
- Gemini emphasized operator ergonomics: no-promoted-member behavior, retirement remediation messaging, and list verbosity.
- Claude pushed harder on contract precision: `checkpoint_family` key shape, fingerprint invariance, lifecycle-index creation policy, and the exact stale-write mechanism.

