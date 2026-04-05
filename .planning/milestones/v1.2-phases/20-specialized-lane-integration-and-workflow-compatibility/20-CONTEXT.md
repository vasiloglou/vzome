# Phase 20: Specialized Lane Integration and Workflow Compatibility - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 20 integrates at least one real `specialized_materials` lane into the
shipped operator-governed LLM workflow so `llm-generate`, `llm-launch`,
`llm-replay`, and `llm-compare` remain compatible when local or specialized
serving is involved.

This phase should deliver:

- one specialized-materials lane with a real workflow role beyond generic
  hosted prompting
- additive lineage that preserves specialized lane identity across launch,
  replay, and comparison
- workflow compatibility for local or specialized lane runs without creating a
  parallel pipeline path
- an honest specialized-lane role that respects the fact that off-the-shelf
  materials models are not assumed to be Zomic-native

This phase does not benchmark all serving lanes comprehensively, require direct
specialized-lane Zomic generation, or introduce autonomous campaign behavior.
It makes the first specialized lane operationally meaningful inside the
existing governed workflow.

</domain>

<decisions>
## Implementation Decisions

### Specialized lane role
- **D-01:** The first real `specialized_materials` lane should be
  evaluation-primary rather than direct-generation-first.
- **D-02:** The specialized lane should prove its value through
  synthesizability, materials plausibility, precursor guidance, anomaly
  detection, or similarly honest evaluation-style behavior.
- **D-03:** Phase 20 should not force the first specialized lane to pretend it
  can already generate strong Zomic directly if the available model does not
  support that honestly.

### Proof target
- **D-04:** Phase 20 should prove the specialized lane on one real system plus
  one thin compatibility fixture or lighter second-system proof.
- **D-05:** The main proof should show the specialized lane doing real workflow
  work on one concrete system instead of spreading effort thinly across two
  full benchmark lanes.
- **D-06:** The second proof path should be enough to show compatibility across
  launch, replay, and compare without turning Phase 20 into the full benchmark
  milestone.

### Serving source
- **D-07:** The specialized lane may use any runnable OpenAI-compatible
  specialized endpoint; local serving is preferred but not mandatory for the
  first operational proof.
- **D-08:** What matters in Phase 20 is that the specialized lane is real and
  executable inside the workflow, not that every specialized checkpoint is
  packaged for purely local operation from day one.
- **D-09:** Phase 20 should not stop at a contract-only specialized lane. A
  real runnable endpoint is required.

### Workflow touchpoint
- **D-10:** The specialized lane should be evaluation-primary and
  generation-compatible.
- **D-11:** The clearest Phase 20 value is to route the specialized lane
  through `llm-evaluate` or equivalent assessment-style outputs while keeping
  `llm-generate`, `llm-launch`, `llm-replay`, and `llm-compare` compatible with
  that lane as the originating lane.
- **D-12:** Generation compatibility still matters, but it is secondary to
  getting one honest specialized-lane workflow role working end to end.

### Compatibility boundary
- **D-13:** Core artifact shapes should remain stable.
- **D-14:** Phase 20 should add richer lineage plus explicit lane-aware
  compare/report fields so operators can tell which outcomes came from a
  specialized lane and what exact serving identity was involved.
- **D-15:** Phase 20 should not create a specialized-only artifact path or a
  parallel workflow family.

### Inherited constraints
- **D-16:** Config remains authoritative for available lanes and their serving
  identities.
- **D-17:** `llm-generate` remains the single generation engine; `llm-launch`
  and `llm-replay` remain wrappers.
- **D-18:** Explicit fallback and replay identity rules from Phase 19 remain in
  force for specialized lanes.
- **D-19:** The workflow stays operator-governed, file-backed, and explicitly
  no-DFT.
- **D-20:** Off-the-shelf specialized materials models are not assumed to
  understand Zomic natively; Phase 20 should choose the highest-value supported
  role rather than forcing direct Zomic symmetry.

### the agent's Discretion
- The exact specialized model or endpoint selected, provided it is genuinely
  materials-specific and executable behind the Phase 19 serving contract
- The exact system chosen for the “real” proof versus the thinner compatibility
  proof
- The exact additive lineage field names and compare/report output wording,
  provided the core artifact contracts stay stable
- The exact place where the specialized lane is surfaced most prominently in
  operator docs, provided the role stays evaluation-primary

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` — `v1.2` milestone goal, current scope, and the note
  that specialized materials models are not assumed Zomic-native
- `.planning/ROADMAP.md` — Phase 20 goal, deliverables, success criteria, and
  the boundary to Phase 21 benchmarks
- `.planning/REQUIREMENTS.md` — `LLM-15`, `LLM-16`, and `OPS-09` as the Phase
  20 requirements
- `.planning/STATE.md` — current milestone handoff after Phase 19 completion

### Prior phase authority
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-CONTEXT.md`
  — Phase 19 local-serving contract, lane authority, fallback posture, and
  full serving-identity requirements
- `.planning/milestones/v1.1-phases/11-closed-loop-campaign-execution-bridge/11-CONTEXT.md`
  — launch wrapper constraints, config-authoritative lane posture, and additive
  lineage expectations
- `.planning/milestones/v1.1-phases/12-replay-comparison-and-operator-workflow/12-CONTEXT.md`
  — replay authority, comparison baseline expectations, and strict replay
  posture that Phase 20 must preserve

### LLM and workflow docs
- `materials-discovery/developers-docs/llm-integration.md` — current LLM
  architecture, specialized-lane scope note, and phase-by-phase workflow
  expectations
- `materials-discovery/developers-docs/llm-quasicrystal-landscape.md` — why
  specialized materials models are valuable for quasicrystal workflows while
  still not being assumed Zomic-native
- `materials-discovery/developers-docs/pipeline-stages.md` — `llm-generate`,
  `llm-evaluate`, `llm-launch`, `llm-replay`, and `llm-compare` workflow
  contracts
- `materials-discovery/developers-docs/configuration-reference.md` — lane and
  local-serving config semantics introduced in Phase 19

### Existing contract surface
- `materials-discovery/src/materials_discovery/common/schema.py` —
  `SystemConfig`, `LlmGenerateConfig`, `LlmEvaluateConfig`, and model-lane
  schema surfaces
- `materials-discovery/src/materials_discovery/llm/schema.py` — run manifest,
  assessment, launch, replay, and comparison artifact contracts
- `materials-discovery/src/materials_discovery/llm/runtime.py` — adapter
  resolution seam and the current `openai_compat_v1` serving contract
- `materials-discovery/src/materials_discovery/llm/evaluate.py` — existing
  evaluation entrypoint and provenance shape for synthesizability-style outputs
- `materials-discovery/src/materials_discovery/llm/launch.py` — lane-aware
  launch overlay behavior
- `materials-discovery/src/materials_discovery/llm/replay.py` — replay serving
  identity enforcement and compatibility rules
- `materials-discovery/src/materials_discovery/llm/compare.py` — outcome
  snapshot and comparison surfaces that must remain compatible

### Phase 19 examples
- `materials-discovery/configs/systems/al_cu_fe_llm_local.yaml` — current local
  lane config example with `general_purpose` and `specialized_materials`
- `materials-discovery/configs/systems/sc_zn_llm_local.yaml` — second local
  lane config example and seeded local workflow reference

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/src/materials_discovery/llm/evaluate.py`: already
  provides an additive LLM assessment path with synthesizability, precursor
  hints, anomaly flags, and rationale fields that fit an evaluation-primary
  specialized lane.
- `materials-discovery/src/materials_discovery/llm/launch.py`: already resolves
  serving lanes and records serving identity, so Phase 20 can extend the same
  launch contract rather than inventing a second execution path.
- `materials-discovery/src/materials_discovery/llm/replay.py`: already enforces
  hard serving identity versus transport drift; specialized-lane replay can
  build on this directly.
- `materials-discovery/src/materials_discovery/llm/compare.py`: already builds
  outcome snapshots and comparisons from launch/replay artifacts, making it the
  natural place to surface richer lane-aware comparison outputs.
- `materials-discovery/configs/systems/al_cu_fe_llm_local.yaml` and
  `materials-discovery/configs/systems/sc_zn_llm_local.yaml`: already show the
  lane structure that a real specialized endpoint can inhabit.

### Established Patterns
- Keep serving behavior additive and preserve the existing CLI/file-backed
  artifact flow.
- Preserve stable artifact shapes and extend lineage rather than forking new
  specialized-only artifacts.
- Use one real runtime seam (`llm-generate` / `llm-launch` / `llm-replay`) with
  explicit lane identity rather than per-lane bespoke code paths.
- Prefer honest capability boundaries over “paper support” for direct Zomic
  generation.

### Integration Points
- `materials-discovery/src/materials_discovery/llm/evaluate.py` for making a
  specialized lane operationally meaningful in the shipped workflow
- `materials-discovery/src/materials_discovery/cli.py` for lane-aware command
  wiring and additive operator-facing summaries
- `materials-discovery/src/materials_discovery/llm/launch.py`,
  `materials-discovery/src/materials_discovery/llm/replay.py`, and
  `materials-discovery/src/materials_discovery/llm/compare.py` for preserving
  compatibility across the closed-loop workflow
- `materials-discovery/developers-docs/llm-integration.md` and
  `materials-discovery/developers-docs/pipeline-stages.md` for documenting the
  first honest specialized-lane role

</code_context>

<specifics>
## Specific Ideas

- The first specialized lane should earn its place through evaluation-style
  strengths such as synthesizability or precursor realism rather than weak
  direct Zomic generation.
- Phase 20 should prove one real specialized lane on one real system and use a
  thinner second proof to demonstrate that launch, replay, and compare stay
  compatible.
- A runnable OpenAI-compatible specialized endpoint is enough for the first
  proof even if the model is not packaged as a purely local checkpoint yet.

</specifics>

<deferred>
## Deferred Ideas

- Forcing direct specialized-lane Zomic generation as the primary Phase 20 goal
- Requiring every specialized lane to be locally served before it can enter the
  workflow
- Full two-system benchmark parity as part of Phase 20 instead of Phase 21
- Creating a specialized-only artifact path or specialized-only workflow
- Zomic-native local generation adaptation or fine-tuned checkpoint training

</deferred>

---

*Phase: 20-specialized-lane-integration-and-workflow-compatibility*
*Context gathered: 2026-04-05*
