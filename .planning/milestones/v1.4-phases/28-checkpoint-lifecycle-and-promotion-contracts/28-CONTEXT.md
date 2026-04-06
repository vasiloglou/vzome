# Phase 28: Checkpoint Lifecycle and Promotion Contracts - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 28 defines the lifecycle state, registry, and promotion artifacts needed
to manage more than one adapted checkpoint per system safely.

This phase should deliver:

- additive lifecycle models for `candidate`, `promoted`, `pinned`, and
  `retired` checkpoint states
- a file-backed lifecycle index that works with the existing per-checkpoint
  registration artifacts under `data/llm_checkpoints/`
- deterministic active-checkpoint selection rules for promoted defaults versus
  explicit pinning
- typed promotion artifacts that reference benchmark evidence without forcing
  Phase 30 scoring thresholds into the contract too early
- clear operator-facing diagnostics for conflicting promotion state, stale
  lifecycle actions, or ambiguous active-checkpoint resolution

This phase does not add benchmark threshold policy, automated training jobs, or
workflow-wide promotion orchestration. It defines the contract that later
phases will execute through generation, launch, replay, and benchmark flows.

</domain>

<decisions>
## Implementation Decisions

### Lifecycle state shape
- **D-01:** Phase 28 should use a hybrid lifecycle model.
- **D-02:** Immutable per-checkpoint registration facts should stay with each
  checkpoint artifact.
- **D-03:** A central lifecycle index should track promoted/default/pinned/
  retired state and history across the checkpoint family.

### Active selection authority
- **D-04:** Config should remain authoritative for which adapted-checkpoint
  family exists on a lane.
- **D-05:** When no explicit checkpoint pin is present, the lifecycle registry
  should resolve the promoted member of that configured family.
- **D-06:** Phase 28 should avoid a config-only default-checkpoint rule that
  turns promotion into an advisory note instead of workflow state.

### Pinning surface
- **D-07:** Operators should be able to pin a checkpoint explicitly in manual
  workflows and in governed campaign/spec workflows.
- **D-08:** Manual `llm-generate` and later campaign execution should preserve
  the same checkpoint-id pinning semantics.
- **D-09:** Phase 28 should not force checkpoint pinning to live only in one
  workflow family.

### Retirement semantics
- **D-10:** `retired` means a checkpoint can no longer be selected implicitly
  for future work.
- **D-11:** Retired checkpoints must remain replayable and auditable so prior
  results stay reproducible.
- **D-12:** Phase 28 should reject warning-only retirement semantics and should
  not block replay/history for retired checkpoints.

### Promotion evidence minimum
- **D-13:** Promotion must create a typed artifact with explicit references to
  benchmark or evaluation evidence.
- **D-14:** Phase 28 should not hard-code numeric promotion thresholds yet.
- **D-15:** Manual note-only promotion is insufficient for auditability.

### Inherited constraints
- **D-16:** Checkpoint registration remains file-backed under
  `data/llm_checkpoints/{checkpoint_id}/`.
- **D-17:** Checkpoint fingerprint remains the hard replay identity.
- **D-18:** Serving-lane configuration remains authoritative for available
  adapted lanes; lifecycle state chooses the active member, not a new runtime.
- **D-19:** Rollback to the baseline local lane remains an explicit operator
  action outside implicit promotion semantics.
- **D-20:** The workflow stays operator-governed, file-backed, and explicitly
  no-DFT.

### the agent's Discretion
- Exact schema and file names for lifecycle-index and promotion artifacts
- Exact family-key naming and how it maps from lane config into registry lookup
- Exact wording for stale/conflicting lifecycle diagnostics
- Exact additive manifest fields that preserve backward compatibility with
  existing checkpoint registration and replay artifacts

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` — `v1.4` milestone goal and the decision to prioritize
  checkpoint lifecycle/promotion before automated training-job workflows
- `.planning/ROADMAP.md` — Phase 28 scope, deliverables, success criteria, and
  milestone boundaries
- `.planning/REQUIREMENTS.md` — `LLM-23` and `OPS-13` as the governing
  requirements for this phase
- `.planning/STATE.md` — current milestone state and handoff into Phase 28

### Prior phase authority
- `.planning/milestones/v1.3-phases/25-zomic-checkpoint-artifact-and-lineage-contracts/25-CONTEXT.md`
  — registration surface, strict lineage posture, and checkpoint-identity
  constraints established in `v1.3`
- `.planning/milestones/v1.3-phases/26-zomic-adapted-local-generation-integration/26-CONTEXT.md`
  — adapted-lane integration assumptions that Phase 28 must not destabilize
- `.planning/milestones/v1.3-phases/27-adapted-checkpoint-benchmarks-and-operator-workflow/27-CONTEXT.md`
  — shared benchmark context and explicit rollback posture that promotion must
  build on rather than replace

### LLM and workflow docs
- `materials-discovery/developers-docs/llm-integration.md` — adapted-checkpoint
  architecture and current checkpoint workflow boundaries
- `materials-discovery/developers-docs/configuration-reference.md` — current
  lane/config fields that lifecycle state must extend additively
- `materials-discovery/developers-docs/pipeline-stages.md` — launch/replay/
  compare/benchmark surfaces that later phases must keep compatible
- `materials-discovery/RUNBOOK.md` — current operator workflow for adapted
  checkpoint registration, smoke testing, and rollback

### Existing contract surface
- `materials-discovery/src/materials_discovery/llm/checkpoints.py` — current
  checkpoint registration and resolution helpers
- `materials-discovery/src/materials_discovery/llm/storage.py` — file-backed
  storage helpers for checkpoint artifacts
- `materials-discovery/src/materials_discovery/common/schema.py` — current
  config and lane models that lifecycle state must extend without forking
- `materials-discovery/src/materials_discovery/llm/schema.py` — run-manifest
  and benchmark/report contracts that later phases will enrich with lifecycle
  identity
- `materials-discovery/src/materials_discovery/llm/launch.py` — explicit lane
  and checkpoint resolution path for governed launches
- `materials-discovery/src/materials_discovery/llm/replay.py` — strict replay
  identity assumptions that retirement/promotion must preserve
- `materials-discovery/src/materials_discovery/llm/serving_benchmark.py` —
  benchmark surface that promotion evidence will reference in later phases

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/src/materials_discovery/llm/checkpoints.py` already owns
  checkpoint registration and is the natural starting point for lifecycle index
  and promotion resolution logic.
- `materials-discovery/src/materials_discovery/llm/storage.py` already writes
  file-backed checkpoint artifacts under `data/llm_checkpoints/`, so lifecycle
  and promotion records should extend this surface rather than invent a new
  storage root.
- `materials-discovery/src/materials_discovery/llm/launch.py`,
  `replay.py`, and `serving_benchmark.py` already depend on stable checkpoint
  identity, which promotion/pinning/retirement must preserve.
- Existing tests already cover checkpoint registration, replay drift,
  benchmark summaries, and real-mode adapted workflow compatibility.

### Established Patterns
- Keep contract changes additive and compatible with the existing single-
  checkpoint `v1.3` workflow.
- Prefer explicit operator-facing errors over implicit fallback or ambiguous
  default selection.
- Keep lineage and replay identity strict enough that later benchmark and
  promotion claims remain auditable.
- Use shared file-backed artifacts instead of ad hoc config comments or
  out-of-band state.

### Integration Points
- `materials-discovery/src/materials_discovery/llm/checkpoints.py` for
  lifecycle index models, promotion artifacts, and active-checkpoint
  resolution rules
- `materials-discovery/src/materials_discovery/common/schema.py` for additive
  config or family-selection surface
- `materials-discovery/src/materials_discovery/llm/schema.py` for typed
  lifecycle/promotion summary contracts
- `materials-discovery/tests/test_llm_checkpoint_registry.py`,
  `test_llm_checkpoint_cli.py`, `test_llm_replay_core.py`, and
  `test_llm_serving_benchmark_core.py` as the main regression anchors

</code_context>

<specifics>
## Specific Ideas

- The safest Phase 28 cut is to separate immutable checkpoint registration
  facts from mutable lifecycle-selection state.
- Promotion should feel like an auditable workflow action, not a YAML edit or a
  hidden default buried in config.
- Retirement should protect future implicit use without breaking replay or
  auditability for already-recorded runs.
- Evidence references belong in the promotion contract now even if scoring
  thresholds wait until Phase 30.

</specifics>

<deferred>
## Deferred Ideas

- Hard numeric promotion thresholds or auto-promotion policy
- Automated training jobs or automated checkpoint production pipelines
- Large-scale checkpoint tournaments or farming infrastructure
- UI-first checkpoint lifecycle management
- Fully autonomous promotion or rollback without explicit operator action

</deferred>

---

*Phase: 28-checkpoint-lifecycle-and-promotion-contracts*
*Context gathered: 2026-04-05*
