# Phase 10: Closed-Loop Campaign Contract and Governance - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 10-closed-loop-campaign-contract-and-governance
**Areas discussed:** Proposal unit, Action vocabulary, Approval shape, Campaign spec authority, Model reliance posture

---

## Proposal unit

| Option | Description | Selected |
|--------|-------------|----------|
| System-scoped proposal | One proposal per system, bundling a small set of concrete actions | ✓ |
| Pack-wide proposal | One proposal can span multiple systems | |
| Single-action proposal | One proposal per action only | |

**User's choice:** System-scoped proposal
**Notes:** User agreed with the recommended default.

---

## Action vocabulary

| Option | Description | Selected |
|--------|-------------|----------|
| Three typed families | Prompt/conditioning changes, composition-window changes, and seed/motif variation changes | ✓ |
| Prompt-only first | Only prompt and conditioning actions in Phase 10 | |
| Broader action set | Include provider/runtime/sampling changes too | |

**User's choice:** Three typed action families
**Notes:** User agreed with the recommended default and did not want to narrow the contract to prompt-only work.

---

## Approval shape

| Option | Description | Selected |
|--------|-------------|----------|
| Separate approval artifact | Suggestion/proposal stays immutable; approval is its own typed file | ✓ |
| Embedded approval status | Mutate the proposal file with approved/rejected state | |
| Spec creation implies approval | No separate approval record | |

**User's choice:** Separate approval artifact
**Notes:** User agreed with the recommended governance boundary.

---

## Campaign spec authority

| Option | Description | Selected |
|--------|-------------|----------|
| Self-contained spec | Approved spec pins resolved actions and launch inputs for replay | ✓ |
| Thin pointer spec | Spec mostly points back to acceptance pack and current config | |
| Hybrid spec | Pin critical execution inputs but still reference source artifacts for context | |

**User's choice:** Self-contained campaign spec
**Notes:** User agreed with the recommended reproducibility posture.

---

## Model reliance posture

| Option | Description | Selected |
|--------|-------------|----------|
| Dual-lane contract | Campaigns may target general-purpose or specialized materials models | ✓ |
| Specialized-first contract | Specialized materials models are the default, general-purpose is fallback | |
| General-purpose first | Keep specialized models out of the Phase 10 contract | |

**User's choice:** Dual-lane contract with explicit specialized-model support
**Notes:** User explicitly asked that specialized LLMs from the research remain in scope for the contract surface.

## the agent's Discretion

- Exact schema field names and version strings
- Exact artifact filenames and storage helper names
- Exact enum names for proposal and approval state
- Exact optional metadata fields for operator notes and reasons

## Deferred Ideas

- Actual execution bridge into `llm-generate` - Phase 11
- Replay/comparison workflow - Phase 12
- Local or fine-tuned serving infrastructure
- Fully autonomous campaign execution
