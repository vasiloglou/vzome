---
phase: 28
reviewers: [gemini, claude]
reviewed_at: 2026-04-05T22:45:24Z
plans_reviewed:
  - 28-01-PLAN.md
  - 28-02-PLAN.md
  - 28-03-PLAN.md
---

# Cross-AI Plan Review - Phase 28

## Gemini Review

# Plan Review: Phase 28 - Checkpoint Lifecycle and Promotion Contracts

This review covers implementation plans **28-01**, **28-02**, and **28-03** for the Materials Design Program.

## Summary
The plans provide a high-quality, additive roadmap for transitioning the checkpoint management system from a single-artifact registration model to a multi-checkpoint lifecycle fleet. The strategy is well-disciplined, separating the core schema/storage primitives (Wave 1) from the mutation logic and CLI surface (Wave 2), and concluding with operational examples and documentation (Wave 3). Most importantly, the plans respect the phase boundary by explicitly deferring workflow execution integration (consumption of promoted defaults) to Phase 29, which minimizes the regression risk for existing `v1.3` workflows.

## Strengths
*   **Additive Design**: The plan preserves backward compatibility with `v1.3` artifacts and `checkpoint_id`-only lane configs, ensuring existing research results remain stable.
*   **Discretionary Guardrails**: Implementation of stale-write guards (revision tracking) and conflict detection (preventing ambiguous promotion states) directly addresses the `OPS-13` requirement for auditable governance.
*   **Explicit Phase Boundaries**: The intentional choice to define the contract first without immediately wiring it into `llm-generate` or `llm-launch` prevents "big bang" integration failures and allows for focused verification of the storage layer.
*   **Evidence-Backed Promotion**: The introduction of `LlmCheckpointPromotionSpec` with explicit evidence references ensures that promotion is a scientific decision rather than just a configuration edit.
*   **Deterministic Storage Layout**: Centralizing lifecycle state in family-keyed directories under `data/llm_checkpoints/` is consistent with the project's file-backed architecture and simplifies auditing.

## Concerns
*   **Ambiguous Active Selection during Transition** (Severity: **MEDIUM**): If a lane config provides both a legacy `checkpoint_id` and a `checkpoint_family`, the resolution precedence must be perfectly clear. Plan 01 mentions they can "coexist," but the logic in Plan 02 must ensure that an explicit legacy ID acts as a "pin" or that the system fails if they conflict.
*   **Family Key Mapping** (Severity: **LOW**): For existing registered checkpoints that lack a `checkpoint_family` field in their `registration.json`, the plan implies these will still load. However, the logic for adding these legacy checkpoints to a new family index (to promote them) should be explicitly verified in the registry tests.
*   **Stale Revision Feedback** (Severity: **LOW**): While the plan includes "clear operator-facing diagnostics," the CLI should specifically suggest how to recover from a stale-write error (e.g., "Expected revision X but found Y; please sync and retry").

## Suggestions
*   **Registry Tooling**: Ensure `llm-list-checkpoints` displays both the `checkpoint_id` and the `fingerprint` side-by-side to ensure operators are promoting the exact artifact they benchmarked.
*   **Auto-Candidate Registration**: When `llm-register-checkpoint` is called with a spec containing a `checkpoint_family`, consider automatically adding that checkpoint to the family's lifecycle index as a `candidate` to reduce the number of manual steps for operators.
*   **Dry-run Promotion**: Consider adding a `--dry-run` flag to the promotion/retirement CLI commands so operators can see the resulting index state before committing changes to disk.

## Risk Assessment
**Overall Risk: LOW**

The risk is low because the implementation is additive and the "execution wiring" is deferred to the next phase. The primary technical risk is "split-brain" state (where config says one thing and the registry says another), but the plan addresses this through deterministic resolution rules and explicit failure modes.

**Justification:**
1.  **Test Coverage**: The plans include comprehensive TDD tasks for schema, storage, and CLI layers.
2.  **Compatibility**: Replay-facing auditability is protected by maintaining the hard link to checkpoint fingerprints.
3.  **Governance**: The file-backed action artifacts (`PromotionSpec`, `RetirementSpec`) create a durable audit trail that satisfies `OPS-13`.

---

## Claude Review

# Cross-AI Review: Phase 28 - Checkpoint Lifecycle and Promotion Contracts

## Plan 28-01: Schema and Storage Contract (Wave 1)

### Summary

Plan 01 is a well-scoped foundation plan that defines types and storage paths before any behavior depends on them. By separating the schema and storage contract from the lifecycle action logic, it minimizes the regression surface and gives Plans 02 and 03 a stable base to build on. The wave-1 sequencing is correct - you need the types before you can write the helpers that emit them.

### Strengths

- **Clean separation of immutable vs. mutable state** - the plan explicitly keeps checkpoint registration immutable while lifecycle index state is mutable, which matches the D-01/D-02/D-03 decisions faithfully
- **Backward compatibility as a first-class concern** - Test 5 ("older v1.3 artifacts deserialize without lifecycle data") directly addresses the highest-risk regression path
- **Storage helpers defined before consumers** - deterministic path helpers in `storage.py` prevent ad hoc path construction from leaking into later plans
- **TDD approach with focused verify commands** - each task runs only the relevant test files, keeping feedback latency low
- **Key links section is precise** - the dependency map from schema -> storage -> checkpoints is explicit enough that a downstream agent cannot accidentally skip reading a dependency

### Concerns

- **MEDIUM: `checkpoint_family` coexistence semantics are underspecified** - The plan says `checkpoint_family` "can coexist with `checkpoint_id`" but does not define what happens when both are set. Is `checkpoint_id` an explicit pin that overrides family resolution? Is it an error if `checkpoint_family` is set but `checkpoint_id` points to a member of a different family? The executing agent will need to make this call, and the wrong choice here propagates through Plans 02 and 03. Suggest adding one explicit truth: "when both checkpoint_family and checkpoint_id are set, checkpoint_id acts as an explicit pin within that family; if it does not belong to the declared family, validation must reject the config."

- **MEDIUM: Lifecycle index revision/versioning scheme is left to agent discretion** - The plan mentions "stale or conflicting writes can rely on stable revision/index paths" but doesn't specify whether the lifecycle index carries a revision counter, a content hash, or a timestamp-based guard. Plan 02 then depends on this for stale-write protection. If Plan 01's agent picks a weak guard (e.g., last-modified timestamp), Plan 02's stale-write tests may pass in CI but fail under real concurrent operator use. Consider constraining this to an explicit monotonic revision integer.

- **LOW: No explicit test for the pin-selection contract shape** - Test 3 mentions "explicit pin-selection contract" but the action section describes pin-selection as a typed artifact "for later manual/campaign pinning in Phase 29." If the model is defined here but never exercised until Phase 29, it risks being wrong when first consumed. Consider one minimal round-trip test (serialize -> deserialize) for the pin-selection model.

- **LOW: `__init__.py` export maintenance** - The plan updates exports but doesn't specify whether the new lifecycle models should be importable from the top-level `materials_discovery.llm` namespace or only from `materials_discovery.llm.schema`. This is a minor ergonomic question but could cause import confusion if Plan 02's agent assumes a different import path.

### Suggestions

- Add one `must_haves.truths` entry: "When both `checkpoint_family` and `checkpoint_id` are present on a lane config, `checkpoint_id` acts as an explicit member pin within the declared family; a `checkpoint_id` that does not belong to the declared family is a validation error."
- Constrain the lifecycle index to carry a monotonic `revision` integer for stale-write guarding, rather than leaving the versioning scheme to agent discretion.
- Add a minimal pin-selection round-trip test to Task 1's behavior list.

### Risk Assessment

**LOW** - This is a schema-and-storage-only plan with no runtime behavior changes. The backward compatibility tests are well-placed. The two medium concerns are about underspecification rather than structural problems.

---

## Plan 28-02: Lifecycle Helpers and CLI (Wave 2)

### Summary

Plan 02 is the behavioral core of Phase 28. It turns the typed contracts from Plan 01 into real file-backed lifecycle actions (load, promote, retire) and exposes them through CLI commands. The plan correctly defers workflow integration (generation, launch, replay) to Phase 29 while still delivering a usable operator surface. The stale-write and conflict protection emphasis is appropriate given the D-10/D-12 decisions about retirement semantics.

### Strengths

- **Explicit stale-write guard requirements** - Tests 3 and 4 directly address the highest-risk failure modes (stale revision, ambiguous retirement of promoted checkpoint)
- **CLI as thin wrappers** - The key_links section correctly prescribes that CLI commands delegate to typed helpers rather than duplicating state logic, which keeps the testable surface in `checkpoints.py`
- **Retirement safety boundary** - "Retiring the currently promoted checkpoint without an explicit replacement or demotion path must fail clearly" is the right call; this prevents the most dangerous operator mistake (leaving a family with no active member)
- **Backward compatibility truth** - Existing `llm-register-checkpoint` behavior preservation is an explicit must-have
- **Test coverage distribution is appropriate** - registry tests cover the helper internals, CLI tests cover the operator-facing surface, and `test_cli.py` covers command discovery

### Concerns

- **HIGH: No specification for how `register_llm_checkpoint` interacts with the new family lifecycle** - Plan 01 adds `checkpoint_family` to the registration spec, but Plan 02 doesn't explicitly say whether `register_llm_checkpoint` should auto-create a family lifecycle index or whether family creation is a separate operator action. If registration auto-creates the family, the first registered checkpoint becomes a `candidate` member implicitly. If it doesn't, operators must manually initialize a family before any lifecycle actions work. This is a significant UX decision that's currently invisible. Suggest adding a truth: "Registering a checkpoint with a `checkpoint_family` must auto-create or extend the family lifecycle index with the new checkpoint as a `candidate` member."

- **MEDIUM: Promotion spec shape is not constrained enough for test 2** - The plan says promotion "writes a typed action artifact with evidence references" but doesn't constrain what constitutes valid evidence. D-13 says "explicit references to benchmark or evaluation evidence" and D-14 says no numeric thresholds yet. But the plan doesn't specify whether evidence references are paths, URIs, or free-text descriptions. If Plan 02's agent picks free-text, Phase 30 will need to retrofit structured evidence. Consider requiring evidence references to be file paths (consistent with the repo's file-backed architecture).

- **MEDIUM: `llm-list-checkpoints` is underspecified** - Task 2 says "operators can list checkpoints for a family through the CLI" but doesn't say what the output shape looks like. Should it show lifecycle state per member? Promoted/retired status? Fingerprints? The output shape will become a de facto contract for operators and later tooling. Suggest specifying that list output is JSON with at minimum: checkpoint_id, fingerprint, lifecycle_state, and promoted/retired timestamps.

- **LOW: No explicit test for idempotent promotion** - What happens if an operator promotes a checkpoint that is already the promoted member? Silent success? Error? The plan's stale-write tests cover the case where the *expected* promoted member doesn't match, but not the case where the *requested* promoted member is already active. Suggest adding an idempotent-promotion test case.

- **LOW: Missing `llm-demote-checkpoint` consideration** - Retirement of the promoted checkpoint fails if there's no replacement, but there's no explicit "demote without retiring" action. This may be intentional (demotion = promote a different checkpoint), but if so, the docs in Plan 03 should say so explicitly.

### Suggestions

- Add a truth about registration-to-family auto-enrollment: registering with `checkpoint_family` set should either auto-create the family lifecycle index or extend it with the new member as `candidate`.
- Constrain evidence references in promotion specs to be file paths, not free-text.
- Specify the JSON output shape for `llm-list-checkpoints`.
- Add one idempotent-promotion test case (promote an already-promoted member).
- In Plan 03's docs, explicitly state that demotion is implicit through promoting a different member, not a separate action.

### Risk Assessment

**MEDIUM** - The registration-to-family interaction gap is the highest risk. If Plan 02's agent makes the wrong call here, it creates a confusing operator workflow where checkpoints exist in registration but aren't discoverable through the family lifecycle. The stale-write and retirement safety coverage is strong, but the missing enrollment path could leave the lifecycle surface feeling disconnected from the existing registration workflow.

---

## Plan 28-03: Examples, Docs, and Compatibility (Wave 3)

### Summary

Plan 03 is a well-designed closing plan that turns the lifecycle contract into something operators can actually understand and use. Committed example specs, additive docs, and replay compatibility proof collectively ensure that Phase 28 ends with an honest, documented, and tested boundary. The explicit "Phase 29 boundary" documentation requirement is especially important - it prevents downstream agents and operators from assuming more than what's actually shipped.

### Strengths

- **Committed example specs as fixtures** - Putting real promotion and retirement YAMLs under `configs/llm/` makes the lifecycle contract testable and discoverable, not just theoretical
- **Replay compatibility as the key backward-compat proof** - Test 2 ("replay tests still protect hard checkpoint fingerprint identity") targets the most important invariant: lifecycle mutations must never weaken replay identity
- **Explicit phase boundary in docs** - The must_haves truth "The docs must be explicit that promoted-default resolution through generation, launch, and replay lands in Phase 29" prevents scope confusion
- **Additive doc strategy** - "Do not rewrite the v1.3 operator workflow into a different system; explain how lifecycle state layers onto it" is exactly right for this phase
- **Wave 3 sequencing is correct** - docs and examples depend on the schema (Plan 01) and helpers (Plan 02) being stable

### Concerns

- **MEDIUM: Example specs may be unreferenceable without real benchmark artifacts** - The promotion spec requires evidence references (per D-13), but the example spec under `configs/llm/` would need to point at something. If the evidence paths in the example reference non-existent benchmark artifacts, the spec is technically invalid under the promotion contract. The plan should specify whether the example specs use placeholder paths (and validation is relaxed for dry-run examples) or whether they reference committed fixture artifacts.

- **MEDIUM: Replay test scope may be too narrow** - Task 1 says "replay-facing tests continue to rely on checkpoint fingerprint identity rather than lifecycle mutability," which is correct. But `test_llm_replay_core.py` currently has no test that exercises replay when a checkpoint has been *retired*. The plan says retired checkpoints "remain auditable," but doesn't explicitly require a test that replays a launch made with a now-retired checkpoint. This is the most important compatibility claim in Phase 28 and should have a dedicated test.

- **LOW: No RUNBOOK.md update mentioned** - The canonical references list `materials-discovery/RUNBOOK.md` as the operator workflow document, but Plan 03 only updates `configuration-reference.md` and `llm-integration.md`. If operators are expected to use the lifecycle CLI, the RUNBOOK should at least mention the new commands. This could be deferred to Phase 29 when the commands become workflow-integrated, but the plan should say so explicitly.

- **LOW: `test_cli.py` regression test is thin** - Task 2 uses `test_cli.py` for "one focused regression that proves the shared CLI surface stays coherent." Given that Plans 01 and 02 add new commands and modify imports, a single test may not catch import-time failures or command-name collisions. Consider running the full `test_cli.py` file rather than adding just one test.

### Suggestions

- Specify whether example promotion/retirement specs use placeholder evidence paths with a note explaining they're examples, or reference committed fixture files.
- Add an explicit test to `test_llm_replay_core.py`: replay a launch bundle whose checkpoint has since been retired, and verify replay succeeds with the original fingerprint identity intact.
- Either add a minimal RUNBOOK.md update or add a truth stating that RUNBOOK updates are deferred to Phase 29 when the commands become workflow-integrated.
- Task 2's verify already runs all of `test_cli.py`, which is good - make sure the task description matches.

### Risk Assessment

**LOW** - This is a documentation and compatibility plan with minimal production code changes. The two medium concerns are about test coverage gaps rather than design problems.

---

## Codex Review

Skipped intentionally because the current runtime is already Codex, so it would not have been an independent external review.

---

## Consensus Summary

Phase 28 is well-structured and should be safe to execute once a few contract details are made explicit. Both reviewers liked the additive hybrid lifecycle architecture, the wave ordering, and the discipline of keeping promoted-default execution and workflow pin resolution out of this phase. The main risk is not overall design quality; it is leaving important operator and contract behavior implicit enough that Plan 02 has to invent policy while implementing it.

### Agreed Strengths

- The three-wave order is strong: schema and storage first, lifecycle actions and CLI second, then examples, docs, and compatibility proof.
- The hybrid architecture is right for the problem: immutable per-checkpoint registration plus mutable family lifecycle state.
- The plans preserve `v1.3` compatibility and keep replay identity anchored to checkpoint fingerprints.
- The phase boundary to Phase 29 is clear and reduces regression risk.
- File-backed action artifacts and deterministic storage align well with `OPS-13` auditability goals.

### Agreed Concerns

- The coexistence semantics for `checkpoint_family` and `checkpoint_id` need to be explicit, including whether `checkpoint_id` acts as a pin and how conflicts are rejected.
- The lifecycle stale-write contract should be pinned down, ideally with an explicit monotonic revision field rather than leaving the guard mechanism to implementation discretion.
- Registration-to-family enrollment needs a defined rule so newly registered checkpoints do not end up discoverable in registration but invisible to lifecycle management.
- Operator-facing contracts need a bit more precision around evidence-reference shape, `llm-list-checkpoints` output, and stale-write recovery guidance.
- Compatibility proof should include a dedicated retired-checkpoint replay test, and example promotion/retirement specs should make clear whether their evidence references are real fixtures or illustrative placeholders.

### Divergent Views

- Gemini focused more on operator ergonomics: CLI recovery messaging, list readability, dry-run support, and displaying `checkpoint_id` plus fingerprint together.
- Claude focused more on contract precision: auto-enrollment into lifecycle families, the exact revision scheme, pin-selection round trips, and the replay test gap for retired checkpoints.

### Recommendation

Approve with amendments. Before executing Phase 28, tighten the plan text around:

1. `checkpoint_family` plus `checkpoint_id` precedence and validation
2. the lifecycle index revision/stale-write mechanism
3. registration-to-family enrollment behavior
4. replay proof for retired checkpoints

Those are the shared risk reducers that would make execution much more mechanical and much less policy-driven.
