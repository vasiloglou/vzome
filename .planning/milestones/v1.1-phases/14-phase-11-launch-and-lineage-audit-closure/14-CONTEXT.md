# Phase 14: Phase 11 Launch and Lineage Audit Closure - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning
**Source:** milestone audit gap closure

<domain>
## Phase Boundary

Phase 14 is a verification-and-traceability closure phase for the shipped
Phase 11 launch bridge.

Its job is to close the audit gaps left behind after Phase 11, which already
delivered:

- typed launch contracts
- `llm-launch` as the approved-spec execution bridge
- additive campaign metadata through the existing `llm-generate` path
- downstream lineage propagation through manifests and the pipeline manifest

The milestone audit says that behavior is implemented and tested, but the
formal proof chain is incomplete because:

- Phase 11 has no `11-VERIFICATION.md`
- `11-VALIDATION.md` is still draft
- the current v1.1 traceability still leaves `LLM-08`, `LLM-10`, and `OPS-06`
  pending until this closure phase finishes

This phase should deliver:

- a formal `11-VERIFICATION.md` proving `LLM-08`, `LLM-10`, and `OPS-06`
- a finalized `11-VALIDATION.md` with current evidence and Nyquist state
- refreshed requirement/traceability state for the three Phase 11-owned
  requirements
- a clean handoff so the next gap-closure phase can focus on Phase 12 only

This phase should not redesign Phase 11, broaden `llm-launch`, or rerun the
full milestone audit early unless the evidence pass finds a real mismatch.

</domain>

<decisions>
## Implementation Decisions

### Evidence posture
- **D-01:** Treat the v1.1 milestone audit as the scope authority for this
  closure phase.
- **D-02:** Treat shipped Phase 11 code, docs, tests, and summaries as the
  primary evidence base unless they prove inconsistent.
- **D-03:** Prefer formalizing already-shipped evidence over reopening
  implementation work.

### Proof chain requirements
- **D-04:** Phase 14 must create `11-VERIFICATION.md`, because the audit names
  that specific artifact as missing.
- **D-05:** Phase 14 must update `11-VALIDATION.md` from draft to an
  audit-ready validation record with explicit command/results status.
- **D-06:** Phase 14 must make the proof path readable from requirement to code
  to tests to summaries without forcing a later audit to reconstruct it manually.

### Requirement scope
- **D-07:** `LLM-08`, `LLM-10`, and `OPS-06` are the only requirements in scope
  for this phase.
- **D-08:** Requirement checkboxes and traceability rows should only move back
  to complete once the verification artifact exists.
- **D-09:** Phase 14 should leave milestone state pointing to Phase 15 after
  execution, not back to the audit gate.

### Change discipline
- **D-10:** This phase should stay planning/docs-first and avoid unnecessary
  changes under `materials-discovery/`.
- **D-11:** If execution unexpectedly needs a `materials-discovery/` change to
  fix a real proof mismatch, that work must update `materials-discovery/Progress.md`
  per `AGENTS.md`.
- **D-12:** Do not rerun the milestone audit in this phase; that waits until
  Phase 15 also closes its proof gap.

### the agent's Discretion
- Exact structure of the launch/lineage evidence matrix in `11-VERIFICATION.md`
- Exact grouping of fresh focused reruns for launch, lineage, and downstream
  compatibility evidence
- Whether to add a small Phase 14 wrapper note if the audit tooling later needs
  an explicit closure pointer in addition to `11-VERIFICATION.md`

</decisions>

<specifics>
## Specific Ideas

- Use the existing Phase 11 summaries as the execution narrative, then tighten
  them into a requirement proof matrix for launch, standard-artifact continuity,
  and lineage.
- Rerun the narrow launch and lineage slices that matter for the audit rather
  than the whole repository unless evidence refresh requires it.
- Make the end state obvious:
  `LLM-08`, `LLM-10`, and `OPS-06` should no longer be “implemented but
  partial”; they should be “complete with explicit audit-ready proof.”

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone control
- `.planning/PROJECT.md` - v1.1 milestone scope and Project 3 objective
- `.planning/ROADMAP.md` - Phase 14 goal, deliverables, and success criteria
- `.planning/REQUIREMENTS.md` - current traceability target for `LLM-08`,
  `LLM-10`, and `OPS-06`
- `.planning/STATE.md` - current milestone handoff and active phase
- `.planning/v1.1-MILESTONE-AUDIT.md` - authoritative list of the gaps this
  phase exists to close

### Original Phase 11 authority
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-CONTEXT.md`
  - locked Phase 11 design decisions
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-RESEARCH.md`
  - Phase 11 planning research
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-VALIDATION.md`
  - current stale validation artifact that must be finalized
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-01-SUMMARY.md`
  - launch contract and resolution proof
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-02-SUMMARY.md`
  - `llm-launch` execution-bridge proof
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-03-SUMMARY.md`
  - downstream lineage and manual continuation proof

### Runtime and documentation evidence
- `materials-discovery/src/materials_discovery/common/schema.py` - lane-aware
  config seam used by Phase 11
- `materials-discovery/src/materials_discovery/llm/schema.py` - launch summary
  and resolved-launch contracts
- `materials-discovery/src/materials_discovery/llm/launch.py` - launch overlay
  resolution logic
- `materials-discovery/src/materials_discovery/llm/generate.py` - additive
  campaign-aware generate path
- `materials-discovery/src/materials_discovery/common/pipeline_manifest.py` -
  pipeline-manifest lineage support
- `materials-discovery/src/materials_discovery/cli.py` - shipped `llm-launch`
  surface plus downstream lineage threading
- `materials-discovery/developers-docs/llm-integration.md` - launch and lineage
  documentation
- `materials-discovery/developers-docs/pipeline-stages.md` - Phase 11 CLI and
  continuation docs

### Test evidence
- `materials-discovery/tests/test_llm_launch_schema.py`
- `materials-discovery/tests/test_llm_launch_core.py`
- `materials-discovery/tests/test_llm_generate_core.py`
- `materials-discovery/tests/test_llm_generate_cli.py`
- `materials-discovery/tests/test_llm_launch_cli.py`
- `materials-discovery/tests/test_llm_campaign_lineage.py`
- `materials-discovery/tests/test_report.py`
- `materials-discovery/tests/test_real_mode_pipeline.py`
- `materials-discovery/tests/test_cli.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The milestone audit already marks the cross-phase flow
  approved spec -> `llm-launch` -> downstream manifests/pipeline as verified.
- Phase 11 produced three summary artifacts that together cover launch setup,
  execution bridging, and downstream lineage propagation.
- The focused pytest surfaces already line up with the audit seam: launch
  schema/core, launch CLI/manual path compatibility, lineage/report propagation,
  and `llm-launch -> screen` compatibility.

### Established Patterns
- Gap-closure phases finalize a stale `VALIDATION.md` before writing the
  retroactive `VERIFICATION.md`.
- Requirements remain incomplete until the proof chain is explicit in planning
  artifacts, even when the code is already shipped.
- GSD milestone audits prefer one readable requirement matrix over forcing the
  auditor to mentally join multiple summary files.

### Integration Points
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-VALIDATION.md`
  must become audit-ready
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-VERIFICATION.md`
  must be created
- `.planning/REQUIREMENTS.md` and `.planning/STATE.md` must reflect the closure
  when the phase completes

</code_context>

<deferred>
## Deferred Ideas

- Closing the remaining Phase 12 proof gap
- Rerunning the milestone audit before all three closure phases complete
- Any redesign of `llm-launch`, downstream lineage, or Phase 11 operator flow
  that is not justified by a real evidence mismatch

</deferred>

---

*Phase: 14-phase-11-launch-and-lineage-audit-closure*
*Context gathered: 2026-04-04*
