# Phase 22: Phase 19 Verification and Validation Audit Closure - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning
**Source:** milestone audit gap closure

<domain>
## Phase Boundary

Phase 22 is a verification-and-traceability closure phase, not a new serving
feature phase.

Its job is to close the audit gaps left behind by Phase 19, which already
shipped the local-serving runtime and lane contracts. The v1.2 audit says the
feature is implemented and tested, but the formal proof chain is incomplete
because Phase 19 never produced a `19-VERIFICATION.md`, its validation file is
still draft, and requirement ownership was reset into the new gap-closure
phases.

This phase should deliver:

- a formal `19-VERIFICATION.md` proving `LLM-13`, `LLM-14`, and `OPS-08`
- a finalized `19-VALIDATION.md` with real status, evidence, and Nyquist state
- refreshed requirement and traceability state for the three Phase 19
  requirements
- a clean handoff so the milestone audit can later rerun without rediscovering
  the same Phase 19 proof gap

This phase should not redesign the local-serving runtime, broaden the serving
surface, or reopen unrelated `materials-discovery/` work unless the evidence
refresh finds a real contradiction between shipped behavior and claimed
coverage.

</domain>

<decisions>
## Implementation Decisions

### Evidence posture
- **D-01:** Treat the v1.2 milestone audit as authoritative for Phase 22 scope.
- **D-02:** Treat existing Phase 19 code, tests, docs, and summaries as the
  evidence base unless they are internally inconsistent.
- **D-03:** Prefer formalizing already-shipped evidence over inventing new
  implementation work.

### Proof chain requirements
- **D-04:** Phase 22 must create `19-VERIFICATION.md` because the audit names
  it explicitly as missing.
- **D-05:** Phase 22 must update `19-VALIDATION.md` from draft to an
  audit-ready validation record with explicit command/results status.
- **D-06:** Phase 22 must leave a clear path from requirements to summaries to
  validation to verification without making auditors reconstruct the proof
  manually.

### Traceability expectations
- **D-07:** `LLM-13`, `LLM-14`, and `OPS-08` remain the only requirements in
  scope for this phase.
- **D-08:** Requirement checkboxes and traceability rows should only move back
  to complete once the verification artifact exists.
- **D-09:** Phase 22 should update milestone state so Phase 23 becomes the next
  active planning target after execution.

### Change discipline
- **D-10:** This phase should stay planning/docs-first and avoid unnecessary
  changes under `materials-discovery/`.
- **D-11:** If execution unexpectedly needs a `materials-discovery/` edit to
  fix a real proof mismatch, that work must also update
  `materials-discovery/Progress.md` per `AGENTS.md`.
- **D-12:** Do not rerun the full milestone audit inside this phase; that
  should wait until Phases 23 and 24 also close their gaps.

### the agent's Discretion
- Exact structure of the evidence matrix inside `19-VERIFICATION.md`
- Exact wording of validation sign-off and Nyquist-compliance notes
- Whether the final Phase 22 closeout should add a thin self-verification note
  so this closure phase does not create fresh documentary debt

</decisions>

<specifics>
## Specific Ideas

- Use the existing Phase 19 summaries as the primary execution narrative and
  turn them into a requirement-by-requirement proof matrix.
- Use one fresh focused local-serving rerun plus the existing Phase 19
  full-suite result as the baseline evidence surface.
- Make the end state obvious: `LLM-13`, `LLM-14`, and `OPS-08` should no longer
  be “implemented but orphaned”; they should be “complete with explicit
  audit-ready evidence.”

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone control
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/v1.2-MILESTONE-AUDIT.md`

### Original Phase 19 authority
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-CONTEXT.md`
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-RESEARCH.md`
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-VALIDATION.md`
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-01-SUMMARY.md`
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-02-SUMMARY.md`
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-03-SUMMARY.md`

### Runtime and documentation evidence
- `materials-discovery/src/materials_discovery/common/schema.py`
- `materials-discovery/src/materials_discovery/llm/schema.py`
- `materials-discovery/src/materials_discovery/llm/runtime.py`
- `materials-discovery/src/materials_discovery/llm/generate.py`
- `materials-discovery/src/materials_discovery/llm/launch.py`
- `materials-discovery/src/materials_discovery/llm/replay.py`
- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/developers-docs/configuration-reference.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/pipeline-stages.md`

### Test evidence
- `materials-discovery/tests/test_llm_launch_schema.py`
- `materials-discovery/tests/test_llm_runtime.py`
- `materials-discovery/tests/test_llm_generate_core.py`
- `materials-discovery/tests/test_llm_generate_cli.py`
- `materials-discovery/tests/test_llm_launch_core.py`
- `materials-discovery/tests/test_llm_launch_cli.py`
- `materials-discovery/tests/test_llm_replay_core.py`
- `materials-discovery/tests/test_cli.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Phase 19 already shipped deterministic local-serving lane resolution, serving
  identity recording, replay-safe drift handling, and committed local configs.
- The existing focused pytest files align closely with the serving seams the
  audit wants formally proven.
- The audit already says the implementation looks healthy; the gap is proof
  chain completeness.

### Established Patterns
- Prior proof-closure phases use one refreshed `VALIDATION.md` for the evidence
  contract and one `VERIFICATION.md` for explicit requirement proof.
- Requirements remain pending until the proof artifact exists, even when the
  code already shipped.
- Milestone audits prefer a clear requirement matrix plus summary evidence
  rather than summary-only inference.

### Integration Points
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-VALIDATION.md`
  must become audit-ready
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-VERIFICATION.md`
  must be created
- `.planning/REQUIREMENTS.md` and `.planning/STATE.md` must reflect the closure
  when the phase completes

</code_context>

<deferred>
## Deferred Ideas

- Closing the Phase 20 and Phase 21 proof gaps
- Rerunning the milestone audit before all three closure phases complete
- Any redesign of local-serving behavior that is not justified by a real
  evidence mismatch

</deferred>

---

*Phase: 22-phase-19-verification-and-validation-audit-closure*  
*Context gathered: 2026-04-05*
