# Phase 13: Phase 10 Verification and Governance Audit Closure - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning
**Source:** milestone audit gap closure

<domain>
## Phase Boundary

Phase 13 is a verification-and-traceability closure phase, not a new feature
phase.

Its job is to close the audit gaps left behind by Phase 10, which already
shipped the closed-loop governance boundary. The audit says the feature is
implemented and tested, but the formal proof chain is incomplete because
Phase 10 never produced a `10-VERIFICATION.md`, its validation file is still
draft, and the current v1.1 traceability was reset into the new gap-closure
phases.

This phase should deliver:

- a formal `10-VERIFICATION.md` proving `LLM-06` and `OPS-05`
- a finalized `10-VALIDATION.md` with real status, evidence, and Nyquist state
- refreshed requirement/traceability state for `LLM-06` and `OPS-05`
- a clean handoff so the milestone audit can later rerun without rediscovering
  the same Phase 10 proof gap

This phase should not redesign Phase 10, broaden the governance feature set, or
reopen unrelated Project 3 work unless the evidence pass finds a real mismatch
between shipped behavior and the claimed requirement coverage.

</domain>

<decisions>
## Implementation Decisions

### Evidence posture
- **D-01:** Treat the v1.1 milestone audit as authoritative for the closure
  scope.
- **D-02:** Treat existing Phase 10 code, tests, docs, and summaries as the
  evidence base unless they are internally inconsistent.
- **D-03:** Prefer formalizing already-shipped evidence over inventing new
  implementation work.

### Proof chain requirements
- **D-04:** Phase 13 must create `10-VERIFICATION.md` as the retroactive proof
  artifact the milestone audit explicitly says is missing.
- **D-05:** Phase 13 must update `10-VALIDATION.md` from draft to an
  audit-ready validation record with explicit command/results status.
- **D-06:** Phase 13 must leave a traceable path from requirements to summaries
  to verification without making auditors reconstruct the proof manually.

### Traceability expectations
- **D-07:** `LLM-06` and `OPS-05` remain the only requirements in scope for
  this phase.
- **D-08:** Requirement checkboxes and traceability rows should only move back
  to complete once the verification artifact exists.
- **D-09:** Phase 13 should update milestone state so the next gap-closure phase
  becomes the active planning target after execution.

### Change discipline
- **D-10:** This phase should stay planning/docs-first and avoid unnecessary
  changes under `materials-discovery/`.
- **D-11:** If execution unexpectedly needs a `materials-discovery/` edit to fix
  a real proof mismatch, that work must also update
  `materials-discovery/Progress.md` per `AGENTS.md`.
- **D-12:** Do not rerun the full milestone audit inside this phase; that should
  wait until Phases 14 and 15 also close their gaps.

### the agent's Discretion
- Exact structure of the evidence matrix inside `10-VERIFICATION.md`
- Exact wording of validation sign-off and Nyquist-compliance notes
- Whether to add a thin Phase 13 wrapper note if the current audit tooling
  needs a phase-local verification pointer in addition to `10-VERIFICATION.md`

</decisions>

<specifics>
## Specific Ideas

- Use the existing Phase 10 summaries as the primary execution narrative and
  turn them into a tighter requirement-by-requirement proof matrix.
- Use the already committed focused pytest commands from `10-VALIDATION.md` and
  `10-03-SUMMARY.md` as the baseline verification surface, with one fresh rerun
  to make the proof current.
- Make the end state obvious:
  `LLM-06` and `OPS-05` should no longer be "implemented but partial"; they
  should be "complete with explicit audit-ready evidence."

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone control
- `.planning/PROJECT.md` - v1.1 milestone scope and Project 3 objective
- `.planning/ROADMAP.md` - Phase 13 goal, deliverables, and success criteria
- `.planning/REQUIREMENTS.md` - current traceability target for `LLM-06` and
  `OPS-05`
- `.planning/STATE.md` - current milestone handoff and active phase
- `.planning/v1.1-MILESTONE-AUDIT.md` - authoritative list of the gaps this
  phase exists to close

### Original Phase 10 authority
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-CONTEXT.md`
  - locked governance-phase decisions
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-RESEARCH.md`
  - Phase 10 planning research
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-VALIDATION.md`
  - current stale validation artifact that must be finalized
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-01-SUMMARY.md`
  - schema/storage proof for typed governance artifacts
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-02-SUMMARY.md`
  - typed `llm-suggest` proposal bundle proof
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-03-SUMMARY.md`
  - approval/spec governance proof and Phase 10 full-suite result

### Runtime and documentation evidence
- `materials-discovery/src/materials_discovery/llm/schema.py` - shipped
  governance contracts
- `materials-discovery/src/materials_discovery/llm/storage.py` - shipped
  deterministic governance artifact paths
- `materials-discovery/src/materials_discovery/llm/campaigns.py` - shipped
  proposal/approval/spec helpers
- `materials-discovery/src/materials_discovery/cli.py` - shipped `llm-suggest`
  and `llm-approve` operator surface
- `materials-discovery/developers-docs/llm-integration.md` - governance-boundary
  documentation
- `materials-discovery/developers-docs/pipeline-stages.md` - operator-facing
  Phase 10 CLI stage documentation

### Test evidence
- `materials-discovery/tests/test_llm_campaign_schema.py`
- `materials-discovery/tests/test_llm_campaign_storage.py`
- `materials-discovery/tests/test_llm_suggest_core.py`
- `materials-discovery/tests/test_llm_suggest_cli.py`
- `materials-discovery/tests/test_llm_campaign_spec.py`
- `materials-discovery/tests/test_llm_approve_cli.py`
- `materials-discovery/tests/test_cli.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The audit already says the Acceptance Pack -> `llm-suggest` -> `llm-approve`
  flow is verified by tests and summaries.
- Phase 10 produced deterministic on-disk governance artifacts, so proof should
  focus on evidence mapping rather than implementation discovery.
- The existing focused pytest files align almost one-to-one with the requirement
  seam the audit wants formally proven.

### Established Patterns
- Prior phases use one `VALIDATION.md` to describe the test contract and one
  `VERIFICATION.md` to turn execution evidence into explicit requirement proof.
- Requirements are treated as incomplete until the proof chain is explicit in
  planning artifacts, not merely because the code exists.
- GSD milestone audits prefer requirement matrix + summary evidence +
  verification artifact, all with clear file-backed linkage.

### Integration Points
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-VALIDATION.md`
  must become audit-ready
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-VERIFICATION.md`
  must be created
- `.planning/REQUIREMENTS.md` and `.planning/STATE.md` must reflect the closure
  when the phase completes

</code_context>

<deferred>
## Deferred Ideas

- Closing Phase 11 and Phase 12 audit gaps
- Rerunning the milestone audit before all three closure phases complete
- Any redesign of Phase 10 behavior that is not justified by a real evidence
  mismatch

</deferred>

---

*Phase: 13-phase-10-verification-and-governance-audit-closure*
*Context gathered: 2026-04-04*
