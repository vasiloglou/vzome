# Phase 15: Phase 12 Replay and Operator Workflow Audit Closure - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning
**Source:** milestone audit gap closure

<domain>
## Phase Boundary

Phase 15 is a verification-and-traceability closure phase for the shipped
Phase 12 replay, comparison, and operator workflow.

Its job is to close the audit gaps left behind after Phase 12, which already
delivered:

- `llm-replay` as a strict replay surface driven by recorded launch artifacts
- `llm-compare` as a comparison surface against acceptance-pack and prior-launch
  baselines
- typed replay and comparison artifacts
- an operator workflow documented end to end for
  suggest -> approve -> launch -> replay -> compare

The milestone audit says that behavior is implemented and tested, but the
formal proof chain is incomplete because:

- Phase 12 has no `12-VERIFICATION.md`
- Phase 12 only has a `12-03-SUMMARY.md`; the earlier summary chain expected by
  the audit is missing
- `LLM-09`, `LLM-11`, and `OPS-07` remain pending until this closure phase
  restores explicit proof and traceability

This phase should deliver:

- a formal `12-VERIFICATION.md` proving `LLM-09`, `LLM-11`, and `OPS-07`
- the missing `12-01-SUMMARY.md` and `12-02-SUMMARY.md` artifacts, or an
  equivalent explicit summary chain if the evidence says they are required
- refreshed requirement/traceability state for the three Phase 12-owned
  requirements
- a clean handoff so the v1.1 milestone audit can rerun without rediscovering
  the same Phase 12 proof gap

This phase should not redesign Phase 12, broaden replay/compare behavior, or
rerun the milestone audit early unless the evidence pass finds a real mismatch.

</domain>

<decisions>
## Implementation Decisions

### Evidence posture
- **D-01:** Treat the v1.1 milestone audit as the scope authority for this
  closure phase.
- **D-02:** Treat shipped Phase 12 code, docs, tests, and `12-03-SUMMARY.md` as
  the primary evidence base unless they prove inconsistent.
- **D-03:** Prefer formalizing already-shipped evidence over reopening
  implementation work.

### Proof chain requirements
- **D-04:** Phase 15 must create `12-VERIFICATION.md`, because the audit names
  that specific artifact as missing.
- **D-05:** Phase 15 must close the summary-chain gap by creating
  `12-01-SUMMARY.md` and `12-02-SUMMARY.md` from real evidence.
- **D-06:** Phase 15 should reuse the already-green `12-VALIDATION.md` as the
  validation authority unless the new summary chain reveals a contradiction that
  requires a narrow evidence refresh note.
- **D-07:** Phase 15 must make the proof path readable from requirement to code
  to tests to summaries to runbook coverage without forcing a later audit to
  reconstruct it manually.

### Requirement scope
- **D-08:** `LLM-09`, `LLM-11`, and `OPS-07` are the only requirements in scope
  for this phase.
- **D-09:** Requirement checkboxes and traceability rows should only move back
  to complete once the verification artifact exists.
- **D-10:** Phase 15 should leave milestone state pointing to a milestone-audit
  rerun rather than to a new implementation phase.

### Change discipline
- **D-11:** This phase should stay planning/docs-first and avoid unnecessary
  changes under `materials-discovery/`.
- **D-12:** If execution unexpectedly needs a `materials-discovery/` change to
  fix a real proof mismatch, that work must update
  `materials-discovery/Progress.md` per `AGENTS.md`.
- **D-13:** Do not mark the milestone archived or complete in this phase; it
  should only become ready for `gsd-audit-milestone`.

### the agent's Discretion
- Exact structure of the replay/comparison/operator evidence matrix in
  `12-VERIFICATION.md`
- Exact split of evidence between `12-01-SUMMARY.md` and `12-02-SUMMARY.md`
- Whether `12-VALIDATION.md` needs only cross-link updates or no edits at all
  once the new summary chain exists

</decisions>

<specifics>
## Specific Ideas

- Use the Phase 12 plan split as the natural summary split:
  replay/compare core foundation for `12-01-SUMMARY.md`, CLI workflow bridge
  for `12-02-SUMMARY.md`, and operator runbook plus end-to-end proof from the
  existing `12-03-SUMMARY.md`.
- Rerun the narrow replay/compare core and CLI slices for proof freshness
  instead of the whole repository unless evidence refresh requires it.
- Make the end state obvious:
  `LLM-09`, `LLM-11`, and `OPS-07` should no longer be “implemented but
  partial”; they should be “complete with explicit audit-ready proof.”

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone control
- `.planning/PROJECT.md` - v1.1 milestone scope and Project 3 objective
- `.planning/ROADMAP.md` - Phase 15 goal, deliverables, and success criteria
- `.planning/REQUIREMENTS.md` - current traceability target for `LLM-09`,
  `LLM-11`, and `OPS-07`
- `.planning/STATE.md` - current milestone handoff and active phase
- `.planning/v1.1-MILESTONE-AUDIT.md` - authoritative list of the gaps this
  phase exists to close

### Original Phase 12 authority
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-CONTEXT.md`
  - locked Phase 12 design decisions
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-RESEARCH.md`
  - Phase 12 planning research
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-VALIDATION.md`
  - current validation authority for replay/compare/operator workflow
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-01-PLAN.md`
  - replay/comparison contract foundation
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-02-PLAN.md`
  - CLI workflow and comparison output plan
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-03-PLAN.md`
  - runbook and end-to-end workflow proof plan
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-03-SUMMARY.md`
  - shipped operator-workflow and full-suite evidence

### Runtime and documentation evidence
- `materials-discovery/src/materials_discovery/llm/schema.py` - replay and
  comparison contracts
- `materials-discovery/src/materials_discovery/llm/storage.py` - saved replay
  and comparison artifact paths
- `materials-discovery/src/materials_discovery/llm/replay.py` - replay logic
- `materials-discovery/src/materials_discovery/llm/compare.py` - comparison
  logic and output summaries
- `materials-discovery/src/materials_discovery/cli.py` - shipped `llm-replay`
  and `llm-compare` operator surface
- `materials-discovery/RUNBOOK.md` - operator workflow documentation
- `materials-discovery/developers-docs/llm-integration.md` - replay/compare
  design and CLI docs
- `materials-discovery/developers-docs/pipeline-stages.md` - operator-facing
  Phase 12 stage documentation

### Test evidence
- `materials-discovery/tests/test_llm_replay_core.py`
- `materials-discovery/tests/test_llm_compare_core.py`
- `materials-discovery/tests/test_llm_replay_cli.py`
- `materials-discovery/tests/test_llm_compare_cli.py`
- `materials-discovery/tests/test_llm_campaign_lineage.py`
- `materials-discovery/tests/test_real_mode_pipeline.py`
- `materials-discovery/tests/test_cli.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The milestone audit already says the
  `llm-launch -> llm-replay -> llm-compare` flow is verified locally.
- Phase 12 already has a strong final summary artifact and a green validation
  file, so the missing proof is documentary rather than architectural.
- The focused pytest surfaces line up directly with the missing summary chain:
  core replay/compare behavior, CLI/operator surface, and end-to-end offline
  workflow proof.

### Established Patterns
- Gap-closure phases use a final `VALIDATION.md` plus a retroactive
  `VERIFICATION.md` and then restore requirement traceability.
- Requirements remain incomplete until the proof chain is explicit in planning
  artifacts, even when the code is already shipped.
- GSD milestone audits prefer summary evidence for each shipped plan rather than
  forcing the auditor to infer missing summaries from later artifacts.

### Integration Points
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-01-SUMMARY.md`
  must be created
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-02-SUMMARY.md`
  must be created
- `.planning/phases/12-replay-comparison-and-operator-workflow/12-VERIFICATION.md`
  must be created
- `.planning/REQUIREMENTS.md` and `.planning/STATE.md` must reflect the closure
  when the phase completes

</code_context>

<deferred>
## Deferred Ideas

- Rerunning the milestone audit before Phase 15 closes
- Any redesign of replay, compare, or operator workflow behavior that is not
  justified by a real evidence mismatch
- Milestone archival or v1.1 completion decisions before the audit reruns

</deferred>

---

*Phase: 15-phase-12-replay-and-operator-workflow-audit-closure*
*Context gathered: 2026-04-04*
