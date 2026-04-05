# Phase 20: Specialized Lane Integration and Workflow Compatibility - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-05
**Phase:** 20-specialized-lane-integration-and-workflow-compatibility
**Areas discussed:** Specialized lane role, Proof target, Serving source, Workflow touchpoint, Compatibility boundary

---

## Specialized lane role

| Option | Description | Selected |
|--------|-------------|----------|
| Synthesis-aware evaluation first | Make the first specialized lane earn its place through synthesizability or materials-plausibility work rather than direct Zomic generation | ✓ |
| Generation-adjacent conditioning first | Use the specialized lane mainly to influence prompts, composition windows, or seed choices | |
| Direct generation first | Make the specialized lane generate Zomic candidates directly in Phase 20 | |

**User's choice:** Synthesis-aware evaluation first
**Notes:** Chosen because it is the most honest role for currently available specialized materials models, given that off-the-shelf models are not assumed to understand Zomic natively.

---

## Proof target

| Option | Description | Selected |
|--------|-------------|----------|
| One real system plus one thin fixture lane | Prove the specialized lane deeply on one system and show lighter compatibility on a second path | ✓ |
| Both Al-Cu-Fe and Sc-Zn fully | Run the full specialized-lane proof on both systems | |
| One real system only | Prove the lane on only one system | |

**User's choice:** One real system plus one thin fixture lane
**Notes:** Chosen to balance honest proof with Phase 20 scope while leaving broader serving comparison for Phase 21.

---

## Serving source

| Option | Description | Selected |
|--------|-------------|----------|
| Any runnable specialized OpenAI-compatible endpoint, with local preferred but not mandatory | Use a real executable specialized endpoint that fits the existing serving contract | ✓ |
| Must be locally served | Require the first specialized lane to run locally | |
| Contract only for now | Stop at config and contract support without a real specialized runtime | |

**User's choice:** Any runnable specialized OpenAI-compatible endpoint, with local preferred but not mandatory
**Notes:** Chosen because the priority is proving a real specialized lane inside the workflow, not blocking the phase on local packaging details.

---

## Workflow touchpoint

| Option | Description | Selected |
|--------|-------------|----------|
| Evaluation-primary, generation-compatible | The specialized lane primarily contributes through evaluation-style behavior while generation/launch/replay/compare remain compatible | ✓ |
| Generation-primary | Make the specialized lane primarily a generator | |
| Equal dual role | Ask the specialized lane to play equal generation and evaluation roles in the same phase | |

**User's choice:** Evaluation-primary, generation-compatible
**Notes:** Chosen because evaluation is the clearest fit for current specialized materials models and best aligns with the existing `llm-evaluate` surface.

---

## Compatibility boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Keep core artifact shapes stable, add richer lineage and explicit lane-aware compare/report fields | Preserve the shipped workflow while making lane differences auditable and visible | ✓ |
| Stable artifact shapes only | Keep artifact shapes stable without surfacing richer lane-aware compare/report fields | |
| New specialized-only artifact path | Create a separate artifact family for specialized-lane runs | |

**User's choice:** Keep core artifact shapes stable, add richer lineage and explicit lane-aware compare/report fields
**Notes:** Chosen so operators can see lane differences clearly without fracturing the workflow into parallel specialized-only paths.

---

## the agent's Discretion

- Exact specialized model or endpoint choice
- Exact system chosen for the deeper proof versus the thinner compatibility proof
- Exact additive lineage field names
- Exact compare/report wording for lane-aware operator summaries

## Deferred Ideas

- Direct specialized-lane Zomic generation as the primary goal
- Requiring the first specialized lane to be fully local-only
- Full two-system benchmark parity in this phase
- Specialized-only artifact families or workflow branches
- Zomic-native fine-tuned local generation in this milestone
