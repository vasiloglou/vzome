# Phase 23: Phase 20 Verification Audit Closure - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning
**Source:** milestone audit gap closure

<domain>
## Phase Boundary

Phase 23 is a verification-and-traceability closure phase, not a new
specialized-lane feature phase.

Its job is to close the audit gaps left behind by Phase 20, which already
shipped specialized-lane integration and workflow compatibility. The v1.2
audit says the feature is implemented and tested, but the formal proof chain
is incomplete because Phase 20 never produced a `20-VERIFICATION.md` and the
requirement traceability remains stale.

This phase should deliver:

- a formal `20-VERIFICATION.md` proving `LLM-15`, `LLM-16`, and `OPS-09`
- any narrow refresh to `20-VALIDATION.md` needed to keep the proof chain
  current and synchronized
- refreshed requirement and traceability state for the three Phase 20
  requirements
- a clean handoff so the milestone audit can later rerun without rediscovering
  the same Phase 20 proof gap

This phase should not redesign the specialized-lane workflow or broaden the
serving surface unless the evidence refresh finds a real contradiction between
shipped behavior and claimed coverage.

</domain>

<decisions>
## Implementation Decisions

- **D-01:** Treat the v1.2 milestone audit as authoritative for Phase 23 scope.
- **D-02:** Treat existing Phase 20 code, tests, docs, validation, and
  summaries as the evidence base unless they are internally inconsistent.
- **D-03:** Create `20-VERIFICATION.md` because the audit names it explicitly
  as missing.
- **D-04:** Only touch `20-VALIDATION.md` if a narrow evidence refresh or
  retroactive note is needed; avoid churn for its own sake.
- **D-05:** `LLM-15`, `LLM-16`, and `OPS-09` should only move back to complete
  after the verification artifact exists.
- **D-06:** Phase 23 should update state so Phase 24 becomes the next active
  planning target after execution.
- **D-07:** Close the Phase 23 self-verification loop during execution so the
  milestone does not immediately create a new documentary debt phase.

</decisions>

<specifics>
## Specific Ideas

- Use the existing Phase 20 summaries as the primary execution narrative and
  turn them into a requirement-by-requirement proof matrix.
- Use one fresh focused specialized-lane rerun plus the existing Phase 20
  full-suite result as the baseline evidence surface.
- Make the end state obvious: the specialized lane should no longer be
  “operational but orphaned”; it should be “complete with explicit audit-ready
  evidence.”

</specifics>

<canonical_refs>
## Canonical References

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/v1.2-MILESTONE-AUDIT.md`
- `.planning/phases/20-specialized-lane-integration-and-workflow-compatibility/20-VALIDATION.md`
- `.planning/phases/20-specialized-lane-integration-and-workflow-compatibility/20-01-SUMMARY.md`
- `.planning/phases/20-specialized-lane-integration-and-workflow-compatibility/20-02-SUMMARY.md`
- `.planning/phases/20-specialized-lane-integration-and-workflow-compatibility/20-03-SUMMARY.md`
- `materials-discovery/src/materials_discovery/llm/evaluate.py`
- `materials-discovery/src/materials_discovery/llm/specialist.py`
- `materials-discovery/src/materials_discovery/llm/compare.py`
- `materials-discovery/src/materials_discovery/llm/replay.py`
- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/developers-docs/configuration-reference.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/pipeline-stages.md`
- `materials-discovery/tests/test_llm_evaluate_schema.py`
- `materials-discovery/tests/test_llm_evaluate_cli.py`
- `materials-discovery/tests/test_llm_compare_core.py`
- `materials-discovery/tests/test_llm_compare_cli.py`
- `materials-discovery/tests/test_llm_campaign_lineage.py`
- `materials-discovery/tests/test_llm_replay_core.py`
- `materials-discovery/tests/test_report.py`
- `materials-discovery/tests/test_real_mode_pipeline.py`

</canonical_refs>

<code_context>
## Existing Code Insights

- Phase 20 already shipped a real specialized-lane role, replay/compare
  compatibility, additive serving lineage, and honest operator docs.
- `20-VALIDATION.md` is already marked complete, so the likely work is
  verification plus evidence refresh rather than validation rescue.
- The audit gap is documentary: missing verification and stale requirement
  traceability.

</code_context>

<deferred>
## Deferred Ideas

- Closing the Phase 21 proof gap
- Rerunning the milestone audit before all three closure phases complete
- Any redesign of specialized-lane behavior that is not justified by a real
  evidence mismatch

</deferred>

---

*Phase: 23-phase-20-verification-audit-closure*  
*Context gathered: 2026-04-05*
