---
phase: 10
reviewers: [gemini, claude]
reviewed_at: 2026-04-04T05:21:42Z
plans_reviewed:
  - 10-01-PLAN.md
  - 10-02-PLAN.md
  - 10-03-PLAN.md
---

# Cross-AI Plan Review — Phase 10

`codex` was intentionally skipped as a reviewer because the current runtime is
already Codex and the GSD review workflow prefers independent external
feedback.

## Gemini Review

# Plan Review: Phase 10 — Closed-Loop Campaign Contract and Governance

This review covers the three-wave execution plan for establishing the governance layer that turns dry-run suggestions into materializable campaign intent.

## 1. Summary
The plan is a high-quality, comprehensive roadmap for implementing Phase 10. It successfully translates the advisory `llm-suggest` surface into a rigorous, file-backed governance workflow. By separating **Proposals**, **Approvals**, and **Campaign Specs**, the plan creates a robust audit trail and a clear "governance boundary" that prevents accidental execution while ensuring all necessary launch context (like configuration baselines and lineage) is captured. The dual-lane model contract (General vs. Specialized) is well-integrated as first-class metadata.

## 2. Strengths
*   **Immutability and Separation of Concerns:** The design strictly follows decision **D-05/D-06** by keeping proposals immutable and requiring a separate approval artifact. This ensures that a rejected proposal is as auditable as an approved one.
*   **Self-Contained Campaign Specs:** Wave 03’s focus on pinning the `SystemConfig` baseline and hash is critical for reproducibility. It solves the "floating reference" problem where a system config might change between approval and execution.
*   **Metric-to-Action Mapping:** Wave 02 provides a concrete logic for mapping existing acceptance metrics (parse/compile failures, etc.) into the three locked action families. This moves the system from "text advice" to "executable intent."
*   **Lineage Integrity:** The `LlmCampaignLineage` model captures the full chain from acceptance pack through eval-set to the final approval, fulfilling requirement **OPS-06**.
*   **Deterministic Storage:** The use of deterministic path helpers in `storage.py` ensures that the new artifacts stay organized within the existing `data/benchmarks/` and `data/llm_campaigns/` hierarchies.

## 3. Concerns
*   **Breaking Change for `llm-suggest` Output:** (MEDIUM) Wave 02 modifies `mdisc llm-suggest` to return an `LlmCampaignSuggestion` instead of the legacy `LlmSuggestion`. While the goal is a "revised contract," this will break any existing scripts or notebooks parsing the Phase 9 JSON structure.
*   **Payload Validation Complexity:** (LOW) The `LlmCampaignAction` model uses optional fields for different action data. Without a strict discriminated union or complex validator, it's possible to create an action where the `family` doesn't match the populated payload.
*   **Operator Identity Spoofing:** (LOW) The CLI allows any string for `--operator`. While appropriate for a CLI tool, the documentation should clarify that this is for audit purposes rather than security/authentication.

## 4. Suggestions
*   **Discriminated Union for Actions:** In `LlmCampaignAction`, consider using a Pydantic `Union` with a `Discriminator` on the `family` field. This provides cleaner validation and better IDE/Type hint support than multiple optional fields.
*   **Legacy Compatibility Layer:** If `llm-suggest` is intended to remain a "safe mode" (D-12), consider having the CLI output *both* the new typed bundle and a simplified text summary to stdout to avoid breaking human-readable logs or simple parsers.
*   **Auto-generated Action IDs:** In `campaigns.py`, ensure `action_id` is generated deterministically (e.g., `action-01`, `action-02`) within a proposal so that they are easy to reference in operator notes.
*   **Config Hash Verification:** In Wave 03, add a check to ensure that if a proposal was generated against `Config A`, the operator isn't accidentally approving it against `Config B` (unless that's an intentional override).

## 5. Risk Assessment
**Risk Level: LOW**

The plan is inherently low-risk because Phase 10 is explicitly **non-executing**. It creates data structures and files but does not mutate the active-learning loop or launch LLM runs. The technical dependencies are well-managed, and the TDD approach with focused schema/storage tests provides a high degree of confidence in the contract's stability before Phase 11 begins.

**Justification:**
*   Strict adherence to "Dry-run only" boundary.
*   Strong focus on file-backed reproducibility.
*   Incremental wave-based roll-out minimizes the blast radius of schema changes.

---
**Verdict:** Ready for implementation. The transition from text-based advice to typed campaign intent is well-engineered.

---

## Claude Review

# Phase 10 Plan Review: Closed-Loop Campaign Contract and Governance

## Overall Assessment

Phase 10 is a contract-definition phase with no runtime execution side effects. The three plans follow a clean wave structure: types first, proposal generation second, approval/spec governance third. The plans are thorough, well-sequenced, and tightly scoped to the phase boundary. The main risks are minor and relate to schema complexity, backward compatibility of the `llm-suggest` command, and a few underspecified edge cases.

---

## Plan 10-01: Contract Foundation

### Summary

Defines ~12 new Pydantic models plus storage helpers. This is the right first move — landing durable types before any behavioral code ensures Plans 02 and 03 build on stable contracts. The schema design is detailed enough to implement without ambiguity while leaving field-level naming to the executor's discretion.

### Strengths

- Clean separation: types and storage in one wave, behavior in later waves
- Action-family payload validation (only the matching payload populated) catches a real class of bugs early
- `CampaignModelLane` as a typed literal rather than a free-form string prevents contract drift toward vendor lock-in
- Storage helpers follow the established `_artifact_root()` pattern — no new conventions to learn
- Test behaviors are specific enough to verify without being over-prescriptive on implementation details

### Concerns

- **MEDIUM — Schema file growth.** `llm/schema.py` is already ~930 lines. Adding ~12 more models will push it past 1200. Not a blocker, but future phases may want to split into `llm/campaign_schema.py`. The plan should at least note this as a known trade-off and explicitly decide to keep everything in one file for now.

- **MEDIUM — `LlmCampaignAction` payload validation complexity.** The "only the payload matching `family` is populated" validator needs a `model_validator(mode='after')` that checks three optional fields against one enum. This is straightforward but easy to get subtly wrong (e.g., should a `None` payload for the matching family be valid, or must it be populated?). The plan doesn't specify whether the matching payload is *required* or just *permitted*. Recommendation: require the matching payload and reject non-matching payloads.

- **LOW — `LlmCampaignLaunchBaseline.default_count` sign.** The plan specifies `default_count: int` but doesn't mention a validator. Given the existing pattern (`default_count` in `SystemConfig` has no explicit validator either), this is consistent but worth noting: a negative `default_count` in a campaign spec would be nonsensical.

- **LOW — No versioning migration story.** The plan defines `llm-campaign-proposal/v1` etc., but doesn't say what happens if v2 is needed. This is fine for Phase 10 — version bumps are a future concern — but worth flagging so the team doesn't assume v1 schemas are immutable forever.

### Suggestions

- Explicitly state that the matching action-family payload is **required** (not just permitted) when `family` is set. This removes ambiguity for the executor.
- Add a one-line note acknowledging schema.py growth and deferring a split to a later phase.
- Consider adding `default_count` >= 1 validation to `LlmCampaignLaunchBaseline` for consistency with how it's used downstream.

### Risk Assessment: **LOW**

Pure additive type definitions with no behavioral side effects. The worst case is a schema field that needs renaming before Plan 02 consumes it, which is a trivial fix.

---

## Plan 10-02: Typed Dry-Run Proposal Generation

### Summary

This is the behavioral core of Phase 10: mapping acceptance-pack analysis into typed proposals and updating the CLI. The plan correctly identifies all five heuristic branches from the current `suggest.py` and maps each to typed action families. The decision to create `campaigns.py` as a new module rather than overloading `suggest.py` is clean.

### Strengths

- Preserves backward compatibility: `llm-suggest` command name stays, acceptance-pack input stays mandatory
- Heuristic-to-action mapping is explicit and covers all current branches (parse/compile, shortlist/validation, synthesizability, release-gate, healthy)
- Deterministic `proposal_id` from `pack_id + system_slug` is a good design — it makes replay and comparison stable
- Creating `campaigns.py` as a separate module keeps `suggest.py` thin and avoids circular imports
- Test behaviors cover the interesting branches, not just happy paths

### Concerns

- **HIGH — Backward compatibility of `build_llm_suggestions` signature.** The plan says `build_llm_suggestions(...)` should now build a `LlmCampaignSuggestion` instead of `LlmSuggestion`. But `build_llm_suggestions` is already exported from `llm/__init__.py` and may be called by existing test code or the CLI. The plan should explicitly address whether the old `LlmSuggestion` return type is dropped, deprecated, or kept alongside the new one. If existing tests in `test_cli.py` call `build_llm_suggestions` and expect `LlmSuggestion`, they will break. **Mitigation:** The plan mentions updating `test_cli.py` only "if shared CLI behavior changes enough to justify it" — this needs to be stronger. The executor should check and update `test_cli.py` as part of this plan, not defer it.

- **MEDIUM — `suggest.py` now writes multiple files.** The current `write_llm_suggestions` writes a single JSON file. Plan 02 wants it to write a bundle *plus* per-system proposal files. This means `suggest.py` needs to create directories (`proposals/`) and write N+1 files. The plan should clarify whether `suggest.py` owns the directory creation or whether the CLI does it. Recommendation: let `suggest.py` own writing (it already has `write_json_object`), and have the CLI just call one function.

- **MEDIUM — `acceptance_pack_path` parameter threading.** `build_campaign_proposals` needs `acceptance_pack_path` as a parameter, but the current CLI resolves the pack path from `--acceptance-pack`. The plan should ensure the CLI passes the resolved path through to the proposal builder rather than having the builder try to reconstruct it. This is likely obvious to the executor but worth calling out.

- **LOW — Optional `--config` enrichment scope.** The plan says config enrichment is optional, which is correct. But it doesn't specify *what* enrichment means concretely for proposals in Plan 02 (vs. Plan 03 where config is needed for the launch baseline). If Plan 02's config enrichment only adds hints to action payloads (e.g., current composition bounds), that's fine. If it's meant to pre-populate launch baseline fields, that belongs in Plan 03. Recommendation: defer `--config` to Plan 03 entirely rather than introducing a half-useful version here.

### Suggestions

- Make the `build_llm_suggestions` return-type change explicit: document that it now returns `LlmCampaignSuggestion` and update or replace the old `LlmSuggestion`-based path.
- Add a task step to verify `test_cli.py` still passes after the signature change — don't defer this.
- Defer `--config` enrichment entirely to Plan 03 where it's actually needed for baseline pinning. Plan 02 can record the acceptance-pack path and system config path as `None` in proposal metadata.
- Clarify that `suggest.py` (not the CLI) owns the proposal directory creation and per-system file writing.

### Risk Assessment: **MEDIUM**

The backward-compatibility concern around `build_llm_suggestions` is real. If the executor doesn't check existing callers, tests will break in a way that looks like Plan 02's fault but is actually a signature migration issue. With the mitigation above, risk drops to LOW.

---

## Plan 10-03: Approval and Spec Governance

### Summary

Closes the governance loop: approval artifacts, campaign-spec materialization, a new CLI command, and doc updates. This is where `OPS-05` gets its teeth — no campaign can launch without an explicit approval file. The plan correctly requires system config input only for approvals (not rejections) and stops at spec materialization without any execution bridge.

### Strengths

- Approval as a separate artifact with explicit `approved`/`rejected` decision is exactly right for auditability
- Requiring `--config` only for approved proposals (not rejections) avoids unnecessary operator burden
- `config_sha256` reuse from `common/manifest.py` is clean — no new hashing logic
- The plan explicitly lists what the CLI must *not* do (no `generate_llm_candidates`, no candidate JSONL, no active-learning mutation)
- Doc updates are included in the same plan rather than deferred — this is good practice for a governance phase

### Concerns

- **MEDIUM — `campaign_id` generation strategy.** The plan says approved proposals create a "stable `campaign_id`" but doesn't specify the generation strategy. Is it deterministic from proposal + approval inputs (enabling idempotent re-approval)? Or is it UUID-based (simpler but non-deterministic)? For replay purposes (Phase 12), a deterministic ID would be better. Recommendation: derive `campaign_id` from `proposal_id + approval_id` hash, making re-creation stable.

- **MEDIUM — Re-approval of the same proposal.** What happens if an operator approves the same proposal twice? The plan doesn't address this. Options: (a) overwrite the previous approval/spec, (b) reject with an error, (c) create a second approval with a new ID. For governance auditability, option (c) is probably best — each approval is a unique decision event — but the spec directory would need to handle multiple campaign IDs for the same proposal. The plan should state the expected behavior.

- **LOW — `llm-approve` command name.** The plan suggests `mdisc llm-approve` which is a new top-level command. This is fine, but the project already has a pattern of subcommands under `mdisc llm-*`. Verify that `typer` command registration is consistent with `llm-suggest`, `llm-generate`, `llm-evaluate`.

- **LOW — Doc update scope.** The plan asks for updates to both `llm-integration.md` and `pipeline-stages.md`. These are already long documents. The update should be additive (new sections) rather than restructuring existing content, to minimize diff size and review burden.

### Suggestions

- Specify that `campaign_id` is deterministic from `proposal_id + operator + timestamp` or similar — document the strategy so Phase 11/12 can rely on it.
- Add a test case for re-approval of the same proposal (even if the behavior is "each approval is independent").
- Ensure `llm-approve` error handling follows the existing pattern: `FileNotFoundError`, `ValidationError`, `ValueError` caught and exiting with code 2.
- Keep doc updates additive — new sections for `llm-approve` and the campaign-spec artifact layout, rather than reorganizing existing content.

### Risk Assessment: **LOW**

The approval/spec path is straightforward. The edge cases (re-approval, campaign ID stability) are real but not blocking — they can be resolved during execution without changing the plan structure.

---

## Cross-Plan Concerns

### 1. Existing test regression (MEDIUM)

Plans 02 and 03 modify `cli.py` and `suggest.py`, which are already covered by `test_cli.py` and potentially other test files. The validation strategy mentions running `test_cli.py` but only in Plan 03. Plan 02 should also verify `test_cli.py` passes after changing the `build_llm_suggestions` return type.

### 2. `__init__.py` export accumulation (LOW)

All three plans add exports to `llm/__init__.py`, which is already 188 lines. This is manageable but the file will grow to ~220+ lines. Consider whether a wildcard or grouped re-export pattern would help, though the current explicit style is safer.

### 3. Progress.md update enforcement (LOW)

All three plans correctly note the Progress.md requirement. The executor should batch these updates per plan, not per task, to avoid noisy diffs.

### 4. No integration test across all three plans (LOW)

Each plan has its own focused tests, but there's no end-to-end test that exercises the full flow: acceptance pack → suggestions → proposals → approval → campaign spec. This is acceptable for Phase 10 (which is contract-focused), but Phase 11 should add an integration test before wiring the spec into `llm-generate`.

---

## Final Verdict

| Plan | Risk | Recommendation |
|------|------|---------------|
| 10-01 | LOW | Execute as-is with minor suggestions |
| 10-02 | MEDIUM | Clarify `build_llm_suggestions` backward compatibility before execution |
| 10-03 | LOW | Specify campaign_id generation strategy; otherwise execute as-is |

**Overall Phase 10 Risk: LOW-MEDIUM.** The plans are well-structured and appropriately scoped. The main risk is the `build_llm_suggestions` signature change in Plan 02 breaking existing tests. With the mitigations noted, this phase should land cleanly in three waves.

---

## Consensus Summary

Both reviewers see Phase 10 as a strong, low-blast-radius governance phase with
the right wave ordering: contracts first, typed proposal generation second, and
approval/spec materialization third. The main shared risk is not the overall
scope, but a few contract edges that should be tightened before execution so the
Phase 10 surface is easier to evolve and less likely to break the existing
`llm-suggest` callers.

### Agreed Strengths

- The phase boundary is disciplined: dry-run proposals, separate approvals, and
  self-contained campaign specs are clearly split.
- The proposal/approval/spec workflow creates a strong audit trail and preserves
  the explicit approval boundary required by `OPS-05`.
- Pinning source config lineage and baseline launch context inside the campaign
  spec is the right reproducibility posture for later execution and replay.
- The metric-to-action mapping approach is concrete enough to move from text
  advice to typed campaign intent.
- The deterministic artifact layout under acceptance-pack roots and
  `data/llm_campaigns/` fits the repo’s existing file-backed conventions.

### Agreed Concerns

- The biggest shared concern is Phase 10 Plan 02’s migration of
  `build_llm_suggestions` / `llm-suggest` from the legacy `LlmSuggestion`
  surface to the new typed campaign bundle. Both reviewers think the plan should
  be more explicit about backward compatibility and test coverage for existing
  callers, especially `test_cli.py`.
- Both reviewers flagged the `LlmCampaignAction` payload model as a place where
  validation can get subtle. The plan should make it explicit that the payload
  matching the action family is required, and non-matching payloads are rejected.
- Both reviews surfaced a need to tighten a few governance details before
  execution: deterministic IDs and path ownership, especially around proposal
  files and campaign/spec identity.

### Divergent Views

- Gemini rates the overall phase as low risk and focuses more on operator
  readability and artifact ergonomics.
- Claude rates the phase as low-medium risk because of concrete migration edges:
  `llm-suggest` backward compatibility, `campaign_id` generation, re-approval
  behavior, and the exact ownership of proposal file writing.
- Gemini suggests a more explicit human-readable compatibility layer for
  `llm-suggest`, while Claude is more focused on keeping the new typed contract
  clean and making any migration impacts explicit in tests and plan wording.
