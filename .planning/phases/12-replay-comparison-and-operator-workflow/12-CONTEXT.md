# Phase 12: Replay, Comparison, and Operator Workflow - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 12 should make the new closed-loop campaign workflow reproducible,
comparable, and usable by operators on a regular basis.

This phase should deliver:

- strict replay helpers for saved campaign launches
- comparison helpers and summaries against originating acceptance packs and
  prior campaign outcomes
- operator-friendly output artifacts for both machine use and human review
- a real runbook for suggest, approve, launch, replay, compare, and result
  interpretation

This phase should not reopen launch mechanics, add resume semantics, or make
the loop autonomous. Those are beyond the current milestone boundary.

</domain>

<decisions>
## Implementation Decisions

### Replay authority
- **D-01:** Replay should use the recorded launch artifact as the primary
  execution authority.
- **D-02:** `campaign_spec.json` should remain provenance context for replay,
  but replay should not recompute behavior from approval-time intent when a
  concrete launch record already exists.
- **D-03:** Phase 12 replay should be strict by default and should not support
  behavioral overrides such as prompt, lane, or action changes.

### Comparison baselines
- **D-04:** Comparison should always consider the originating acceptance pack as
  a baseline.
- **D-05:** Comparison should also use the most recent prior launch for the
  same campaign or system when one exists.
- **D-06:** Comparison should therefore provide both absolute context
  (acceptance-pack and benchmark context) and relative context (recent prior
  launch).

### CLI surface
- **D-07:** Phase 12 should introduce separate commands for replay and
  comparison, e.g. `mdisc llm-replay` and `mdisc llm-compare`.
- **D-08:** Replay and compare should not be folded back into `llm-launch` as
  overloaded flags.

### Comparison outputs
- **D-09:** Phase 12 should emit typed JSON artifacts for replay and comparison
  so later tooling can consume the results programmatically.
- **D-10:** Phase 12 should also print concise human-readable summaries so
  operators can interpret results directly from the CLI.

### Operator workflow
- **D-11:** Phase 12 should ship a real end-to-end runbook rather than only
  scattered command snippets.
- **D-12:** The runbook should cover the full operator path: dry-run suggest,
  approval, launch, replay, compare, and interpretation of outcomes.
- **D-13:** Safe defaults remain part of the design; replay and compare should
  not introduce surprising mutations or implicit execution beyond their stated
  scope.

### Inherited constraints
- **D-14:** `llm-suggest` remains dry-run and governance-only surfaces stay
  separate from execution surfaces.
- **D-15:** `llm-launch` remains the sole campaign execution bridge over the
  existing `llm-generate` runtime.
- **D-16:** Existing artifact roots stay primary, with additive campaign-aware
  lineage rather than a second incompatible storage tree.
- **D-17:** Zomic remains the native generation format.
- **D-18:** The no-DFT boundary remains explicit.

### the agent's Discretion
- Exact replay/comparison artifact filenames and directory organization
- Exact metric field names and console-summary formatting
- Exact helper/module boundaries for replay and comparison logic
- Exact definition of "most recent prior launch" so long as it is deterministic
  and documented

</decisions>

<specifics>
## Specific Ideas

- Treat replay as "rerun what actually launched" rather than "reinterpret the
  approved campaign spec."
- Make comparison outputs easy to inspect from both JSON artifacts and terminal
  summaries so operators do not need notebooks for first-pass interpretation.
- Keep the full workflow linear and auditable: suggest -> approve -> launch ->
  replay -> compare.
- Use the comparison surface to expose whether a campaign improved, regressed,
  or stayed flat relative to both acceptance-pack expectations and prior
  campaign behavior.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` - v1.1 milestone goal and closed-loop workflow target
- `.planning/ROADMAP.md` - Phase 12 scope, deliverables, and success criteria
- `.planning/REQUIREMENTS.md` - `LLM-09`, `LLM-11`, and `OPS-07`
- `.planning/STATE.md` - current milestone handoff and prior phase status

### Prior phase authority
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-CONTEXT.md`
  - proposal, approval, and campaign-spec governance boundary
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-CONTEXT.md`
  - launch behavior, lineage rules, and failure posture
- `.planning/phases/11-closed-loop-campaign-execution-bridge/11-03-SUMMARY.md`
  - what Phase 11 actually shipped

### LLM and operator docs
- `materials-discovery/developers-docs/llm-integration.md` - current LLM
  architecture and campaign workflow
- `materials-discovery/developers-docs/pipeline-stages.md` - CLI stage
  boundaries and downstream continuation expectations

### Existing contract surface
- `materials-discovery/src/materials_discovery/cli.py` - `llm-suggest`,
  `llm-approve`, and `llm-launch` surfaces
- `materials-discovery/src/materials_discovery/llm/campaigns.py` - campaign
  governance storage helpers and launch artifacts
- `materials-discovery/src/materials_discovery/llm/schema.py` - campaign, launch,
  and lineage contracts
- `materials-discovery/src/materials_discovery/llm/generate.py` - execution
  runtime and manifest-writing behavior
- `materials-discovery/src/materials_discovery/common/pipeline_manifest.py` -
  downstream campaign-lineage propagation

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials_discovery/llm/campaigns.py` already owns campaign storage and is
  the natural home for replay/comparison artifact lookup helpers.
- `materials_discovery/llm/generate.py` already writes the launch-side data that
  replay should treat as authoritative.
- `materials_discovery/common/pipeline_manifest.py` already carries additive
  campaign lineage into downstream stages and should stay the comparison anchor.
- `materials_discovery/cli.py` already separates governance and execution
  commands, which fits the new replay/compare command split.

### Established Patterns
- Durable contracts live in typed models and JSON artifacts.
- CLI commands stay thin and call helper modules for the real behavior.
- Operator-safe workflow decisions favor reproducibility and explicitness over
  convenience or hidden automation.
- Additive lineage is preferred over breaking existing artifact contracts.

### Integration Points
- `materials-discovery/src/materials_discovery/cli.py` for new replay and
  compare commands
- `materials-discovery/src/materials_discovery/llm/` for replay/comparison
  helpers and summary generation
- `materials-discovery/developers-docs/` and `materials-discovery/RUNBOOK.md`
  for operator workflow documentation
- existing launch artifacts under `data/llm_campaigns/{campaign_id}/` plus
  standard stage/manifests for baseline comparison

</code_context>

<deferred>
## Deferred Ideas

- Replay-time behavioral overrides
- Resume or continuation semantics for partially failed launches
- Automatic downstream chaining beyond the existing manual/operator path
- Autonomous campaign execution
- Local or fine-tuned serving infrastructure

</deferred>

---

*Phase: 12-replay-comparison-and-operator-workflow*
*Context gathered: 2026-04-04*
