# Phase 29: Promotion-Aware Workflow Integration - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 29 must turn the Phase 28 lifecycle contract into real runtime behavior
for the shipped workflow surfaces.

This phase should deliver:

- promoted-default checkpoint resolution for `mdisc llm-generate`
- campaign launch and replay behavior that can distinguish between the
  promoted member of a checkpoint family and an explicit checkpoint pin
- compare, replay, and benchmark artifacts that keep enough lifecycle identity
  to explain which checkpoint actually ran after promotions change
- explicit rollback posture that keeps the baseline local lane as a first-class
  operator path

This phase does not yet add the shared promoted-vs-candidate benchmark and
operator promotion/retirement procedure for the whole lifecycle workflow.
Those workflow-level comparisons and operator runbooks belong to Phase 30.

</domain>

<decisions>
## Implementation Decisions

### Runtime resolution
- **D-01:** `checkpoint_family` without `checkpoint_id` should mean
  "use the currently promoted member of this family" for new execution.
- **D-02:** `checkpoint_family` plus `checkpoint_id` should remain an explicit
  pin inside that family for new execution.
- **D-03:** legacy `checkpoint_id`-only lanes must keep working for older
  single-checkpoint configs.

### Replay semantics
- **D-04:** Replay must preserve the recorded checkpoint identity even if the
  current promoted member changes later.
- **D-05:** A retired checkpoint may still replay when the recorded launch
  bundle pins that checkpoint by immutable registration and fingerprint.
- **D-06:** Replay should reject true model/fingerprint drift, not lifecycle
  drift caused by later promotion changes.

### Lifecycle selection boundaries
- **D-07:** Retired checkpoints must never be selected implicitly for new
  execution.
- **D-08:** Explicit future work should only pin active family members; replay
  is the only path that may continue to use a retired checkpoint safely.
- **D-09:** The runtime should fail clearly when a lane asks for a family that
  has no promoted member yet.

### Identity and auditability
- **D-10:** Launch, replay, compare, and benchmark artifacts must record not
  just the final checkpoint id, but also how that checkpoint was chosen.
- **D-11:** The serving identity should expose whether a run used a promoted
  family default, an explicit family pin, or a legacy checkpoint-only lane.
- **D-12:** The family lifecycle revision used for default selection should be
  recorded when available so later promotion changes stay explainable.

### Workflow posture
- **D-13:** The baseline local lane remains the rollback surface; promotion
  should not replace it or hide it.
- **D-14:** Phase 29 may update committed configs and docs to make
  promoted-default versus explicit-pin behavior concrete for operators.
- **D-15:** Phase 29 should not invent a separate checkpoint-only runtime or
  a UI-first promotion surface.

### the agent's Discretion
- Exact naming for lifecycle selection metadata on serving identities
- Exact failure messages for "no promoted member", "retired explicit pin", and
  replay-after-promotion-drift cases
- Whether the committed promoted-default proof uses one updated config, one
  pinned example config, or both

</decisions>

<canonical_refs>
## Canonical References

### Milestone controls
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`

### Prior phase authority
- `.planning/phases/28-checkpoint-lifecycle-and-promotion-contracts/28-CONTEXT.md`
- `.planning/phases/28-checkpoint-lifecycle-and-promotion-contracts/28-RESEARCH.md`
- `.planning/phases/28-checkpoint-lifecycle-and-promotion-contracts/28-REVIEWS.md`

### Existing runtime surfaces
- `materials-discovery/src/materials_discovery/llm/checkpoints.py`
- `materials-discovery/src/materials_discovery/llm/launch.py`
- `materials-discovery/src/materials_discovery/llm/replay.py`
- `materials-discovery/src/materials_discovery/llm/compare.py`
- `materials-discovery/src/materials_discovery/llm/serving_benchmark.py`
- `materials-discovery/src/materials_discovery/llm/evaluate.py`
- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/src/materials_discovery/llm/schema.py`

### Current operator/docs surface
- `materials-discovery/configs/systems/al_cu_fe_llm_adapted.yaml`
- `materials-discovery/configs/systems/al_cu_fe_llm_local.yaml`
- `materials-discovery/configs/llm/al_cu_fe_adapted_serving_benchmark.yaml`
- `materials-discovery/RUNBOOK.md`
- `materials-discovery/developers-docs/configuration-reference.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/pipeline-stages.md`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `resolve_checkpoint_lane(...)` already owns the strict adapter/provider/model
  validation for checkpoint-backed lanes, so promoted-family resolution should
  extend that surface rather than bypass it.
- `build_serving_identity(...)` is already shared by `llm-launch`,
  `llm-evaluate`, and serving benchmark code paths, making it the best seam for
  lifecycle selection metadata.
- `build_replay_serving_identity(...)` already enforces hard replay identity,
  so replay-after-promotion-drift belongs there rather than in CLI glue.
- `LlmServingIdentity`, `LlmCampaignLaunchSummary`, and
  `LlmCampaignOutcomeSnapshot` already thread serving identity through launch,
  replay, compare, and benchmark artifacts.

### Established Patterns
- Keep runtime changes additive to the v1.3 and v1.4 contracts.
- Prefer explicit errors over silent fallback when lifecycle state is missing
  or incompatible.
- Preserve replay safety by relying on registration + fingerprint identity.
- Update committed configs/docs only when the underlying runtime contract is
  actually implemented and regression-tested.

### Integration Points
- `materials-discovery/tests/test_llm_checkpoint_registry.py`
- `materials-discovery/tests/test_llm_launch_core.py`
- `materials-discovery/tests/test_llm_generate_cli.py`
- `materials-discovery/tests/test_llm_replay_core.py`
- `materials-discovery/tests/test_llm_compare_core.py`
- `materials-discovery/tests/test_llm_serving_benchmark_core.py`
- `materials-discovery/tests/test_real_mode_pipeline.py`

</code_context>

<specifics>
## Specific Ideas

- The main adapted Al-Cu-Fe config should likely stop hard-pinning one
  checkpoint in YAML and instead consume the promoted family member.
- A committed pinned example still helps prove the "explicit checkpoint choice"
  story without forcing operators to hand-edit configs.
- Compare output will be much more useful if it prints checkpoint-family
  selection details alongside the generation lane line.

</specifics>

<deferred>
## Deferred Ideas

- Multi-target promoted-vs-candidate benchmark orchestration on one shared
  context
- Benchmark-derived promotion recommendation artifacts or automation
- Full operator promotion/rollback/retirement runbook flow
- Target-level checkpoint pin overrides inside benchmark specs

</deferred>

---

*Phase: 29-promotion-aware-workflow-integration*
*Context gathered: 2026-04-05*
