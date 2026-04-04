# Phase 11: Closed-Loop Campaign Execution Bridge - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 11 should turn the approved, self-contained campaign specs from Phase 10
into a controlled execution bridge over the existing `llm-generate` runtime.

This phase should deliver:

- a dedicated launch surface for approved campaign specs
- deterministic mapping from approved campaign actions into `llm-generate`
  launch inputs
- additive lineage and campaign-aware pointers over the existing artifact roots
- an operator-safe failure posture that preserves auditability without adding
  resume complexity yet

This phase should not create a second incompatible generation system, auto-run
the full downstream discovery pipeline, or absorb replay/comparison work. Those
belong to later phases.

</domain>

<decisions>
## Implementation Decisions

### Launch CLI shape
- **D-01:** Phase 11 should introduce a dedicated launch command rooted in the
  approved campaign spec, e.g. `mdisc llm-launch --campaign-spec PATH`.
- **D-02:** `llm-approve` must remain governance-only. Approval and launch
  should stay as separate operator actions.

### Action-to-runtime mapping
- **D-03:** Approved campaign actions should resolve into a derived runtime
  overlay at launch time rather than mutating the base YAML config on disk.
- **D-04:** Prompt and conditioning actions should map into prompt/example
  selection or equivalent prompt-assembly inputs.
- **D-05:** Composition-window actions should narrow or reshape the active
  composition bounds passed into `llm-generate`.
- **D-06:** Seed and motif variation actions should resolve seed or motif launch
  inputs without inventing a parallel candidate schema.

### Execution scope
- **D-07:** Phase 11 should launch `llm-generate` only.
- **D-08:** Downstream stages such as `screen`, `hifi-validate`, and `report`
  should continue through the existing manual/operator flow after launch, using
  preserved lineage rather than automatic chaining.

### Lineage and output layout
- **D-09:** Existing standard artifact roots remain primary. Phase 11 should not
  replace them with a separate incompatible campaign tree.
- **D-10:** Campaign-aware pointers and lineage fields should be added so
  generated runs and outputs can be traced back to campaign specs, approvals,
  acceptance packs, and eval sets.
- **D-11:** Campaign-specific storage may exist for wrapper artifacts, but the
  core `llm-generate` outputs should remain compatible with the current
  pipeline's standard locations and contracts.

### Model-lane authority
- **D-12:** Config remains authoritative for which model lanes, providers, and
  models are available.
- **D-13:** Campaign actions and campaign specs should choose among configured
  lanes such as `general_purpose` or `specialized_materials`, rather than
  directly hard-overriding provider/model identity by default.
- **D-14:** Specialized materials-model lanes remain first-class and should be
  executable through the same Phase 11 bridge when configured.

### Failure handling
- **D-15:** Partial artifacts should be preserved on failure for auditability.
- **D-16:** Failed launches must be marked clearly in manifests or launch
  summaries so operators can distinguish partial failure from success.
- **D-17:** Phase 11 should not introduce resume support. Operators should use
  an explicit fresh relaunch instead of an implicit continuation flow.

### Inherited constraints
- **D-18:** Zomic remains the native generation representation.
- **D-19:** The no-DFT boundary remains explicit.
- **D-20:** The existing manual `llm-generate` path must stay valid and should
  not regress because of the new campaign-launch wrapper.

### the agent's Discretion
- Exact internal overlay structure and helper/module boundaries
- Exact artifact filenames for launch summaries and campaign pointers
- Exact optional CLI flags beyond the locked campaign-spec-based launch identity
- Exact manifest field names, provided they stay additive and consistent with
  current artifact conventions

</decisions>

<specifics>
## Specific Ideas

- Treat `llm-launch` as a controlled wrapper around the existing
  `llm-generate` path rather than a second generation framework.
- Make the runtime overlay ephemeral and reproducible so operators can tell
  exactly how an approved campaign spec altered the baseline launch inputs.
- Preserve the current stage-oriented artifact layout while making campaign
  lineage easy to follow from launch spec to generated candidates.
- Keep specialized materials-model lanes explicitly supported in the contract,
  but route them through the same launch machinery as general-purpose lanes.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` - v1.1 milestone goal and Project 3 focus
- `.planning/ROADMAP.md` - Phase 11 scope, success criteria, and boundary to
  Phase 12
- `.planning/REQUIREMENTS.md` - `LLM-08`, `LLM-10`, and `OPS-06`
- `.planning/STATE.md` - current milestone handoff and prior phase status

### Prior phase authority
- `.planning/phases/07-llm-inference-mvp/07-CONTEXT.md` - locked
  `llm-generate` runtime posture and additive config/manifest expectations
- `.planning/phases/09-fine-tuned-zomic-model-and-closed-loop-design/09-CONTEXT.md`
  - acceptance-pack and `llm-suggest` posture
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-CONTEXT.md`
  - approved proposal, approval, and campaign-spec authority
- `.planning/phases/10-closed-loop-campaign-contract-and-governance/10-03-SUMMARY.md`
  - what Phase 10 actually shipped at the governance boundary

### LLM and pipeline docs
- `materials-discovery/developers-docs/llm-integration.md` - current LLM
  architecture, runtime seam, and campaign-governance design
- `materials-discovery/developers-docs/pipeline-stages.md` - current CLI stage
  boundaries and how generated artifacts feed the rest of the pipeline

### Existing contract surface
- `materials-discovery/src/materials_discovery/cli.py` - `llm-generate`,
  `llm-suggest`, and `llm-approve` orchestration patterns
- `materials-discovery/src/materials_discovery/llm/generate.py` - current
  generate runtime, manifest writing, and candidate emission path
- `materials-discovery/src/materials_discovery/llm/campaigns.py` - current
  campaign-governance storage and spec materialization helpers
- `materials-discovery/src/materials_discovery/llm/schema.py` - campaign spec
  and LLM runtime contracts
- `materials-discovery/src/materials_discovery/llm/runtime.py` - model-lane and
  provider execution seam
- `materials-discovery/src/materials_discovery/llm/prompting.py` - prompt and
  conditioning assembly surface
- `materials-discovery/src/materials_discovery/common/schema.py` - additive
  generation config patterns and candidate contracts

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials_discovery/llm/generate.py`: existing `llm-generate` execution path
  should stay the single runtime authority for LLM candidate generation.
- `materials_discovery/llm/campaigns.py`: already holds campaign approval/spec
  storage patterns and is the natural bridge point for launch lookup helpers.
- `materials_discovery/llm/schema.py`: already defines the campaign contracts
  that Phase 11 needs to consume.
- `materials_discovery/llm/runtime.py`: already separates provider/model lanes
  behind a config-driven execution seam.
- `materials_discovery/llm/prompting.py`: natural place to apply
  prompt/conditioning campaign overlays without inventing a second prompt stack.

### Established Patterns
- CLI commands stay thin while Pydantic models and module helpers define the
  durable contract.
- Artifact lineage is additive and file-backed.
- Existing stage roots under `materials-discovery/data/` are already consumed by
  later pipeline stages and should remain compatible.
- Real-provider support stays narrow and explicit, while the contract preserves
  a broader lane/provider abstraction.

### Integration Points
- `materials-discovery/src/materials_discovery/cli.py` for the new
  `llm-launch` command
- `materials-discovery/src/materials_discovery/llm/` for launch orchestration,
  overlay construction, and campaign-aware manifest helpers
- `materials-discovery/data/llm_campaigns/{campaign_id}/` for campaign wrapper
  artifacts and launch pointers
- existing `llm-generate` manifests and candidate outputs, which downstream
  stages should continue to consume without format breaks

</code_context>

<deferred>
## Deferred Ideas

- Automatic downstream chaining beyond `llm-generate`
- Replay and comparison workflows for campaign outcomes
- Resume or continuation support for partial campaign launches
- Hard provider/model overrides directly from campaign specs as the default path
- Local or fine-tuned serving infrastructure in this milestone

</deferred>

---

*Phase: 11-closed-loop-campaign-execution-bridge*
*Context gathered: 2026-04-04*
