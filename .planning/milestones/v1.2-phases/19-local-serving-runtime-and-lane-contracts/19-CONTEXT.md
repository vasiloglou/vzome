# Phase 19: Local Serving Runtime and Lane Contracts - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 19 adds the runtime contracts, config surface, and diagnostics needed to
execute `llm-generate` and campaign launches through local and lane-aware model
serving without breaking the current hosted/manual workflow.

This phase should deliver:

- an additive local-serving runtime contract under `materials_discovery/llm/`
- config/schema support for local endpoints or local model/checkpoint identity
- deterministic lane resolution for `general_purpose` and
  `specialized_materials`
- clear operator-facing diagnostics for missing dependencies, unavailable lanes,
  invalid endpoints, and unresolvable local-serving config

This phase does not add autonomous execution, process management for local
servers, or Zomic-native fine-tuning. It makes the runtime ready for local and
specialized serving under the existing governed workflow.

</domain>

<decisions>
## Implementation Decisions

### Local execution form
- **D-01:** Phase 19 should target an OpenAI-compatible local server contract
  first, not in-process `transformers` inference.
- **D-02:** The first local-serving seam should be broad enough to support local
  HTTP servers such as `vLLM`, `TGI`, `Ollama`-style gateways, or similar
  OpenAI-compatible local endpoints.
- **D-03:** Phase 19 should not try to support both external local servers and
  in-process local inference from day one.

### Serving config shape
- **D-04:** Transport defaults belong in backend/runtime config, while lane
  choice stays in `llm_generate.model_lanes`.
- **D-05:** Lane records should remain the source of concrete lane selection
  (`general_purpose` vs `specialized_materials`) and should carry the runtime
  identity chosen by that lane.
- **D-06:** Phase 19 should avoid a backend-only config shape that weakens
  multi-lane local/specialized setups.

### Operator setup posture
- **D-07:** Phase 19 should assume the local server is already running and
  reachable.
- **D-08:** The CLI should validate configuration and connectivity, but it
  should not launch or manage local inference processes in this phase.
- **D-09:** Config-only support without runtime validation is not sufficient for
  Phase 19.

### Diagnostics and fallback
- **D-10:** Requested local or specialized lanes should fail hard with clear
  diagnostics unless fallback is explicitly configured.
- **D-11:** Phase 19 should not silently downgrade a requested local or
  specialized run back to the baseline hosted lane.
- **D-12:** Campaign launch and replay should preserve the same explicitness:
  if the requested lane is unavailable, operators should see a clear failure and
  reroute intentionally.

### Recorded serving identity
- **D-13:** Phase 19 should record a full auditable serving identity for local
  and specialized runs.
- **D-14:** The minimum recorded identity should include requested lane,
  resolved lane, adapter, provider, model, endpoint or local path, and
  checkpoint/revision/hash when available.
- **D-15:** Lineage must preserve this identity across manual generation,
  campaign launch, and replay so Phase 20 and Phase 21 can compare lanes
  honestly.

### Inherited constraints
- **D-16:** `llm-generate` remains the single generation engine.
- **D-17:** `llm-launch` and `llm-replay` remain wrappers over the existing
  generation runtime rather than separate inference systems.
- **D-18:** Config remains authoritative for which lanes exist and what runtime
  identity they point to.
- **D-19:** The workflow stays operator-governed, file-backed, and explicitly
  no-DFT.
- **D-20:** Off-the-shelf specialized materials models are not assumed to be
  Zomic-native in this phase; the local-serving runtime must support them as
  honest workflow lanes without pretending they can already generate high-grade
  Zomic directly.

### the agent's Discretion
- Exact config field names for transport defaults, explicit fallback controls,
  and local-serving identity details
- Exact adapter names and internal module boundaries for the new local-serving
  runtime seam
- Exact connectivity-check mechanics and error phrasing, provided they stay
  operator-facing and deterministic
- Exact manifest and lineage field names, provided they stay additive and
  compatible with current launch/replay paths

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` — `v1.2` milestone goal, scope note on specialized
  models not being assumed Zomic-native, and later-milestone direction for
  Zomic-native local generation adaptation
- `.planning/ROADMAP.md` — Phase 19 scope, deliverables, success criteria, and
  the boundaries to Phases 20 and 21
- `.planning/REQUIREMENTS.md` — `LLM-13`, `LLM-14`, and `OPS-08` as the Phase
  19 requirements
- `.planning/STATE.md` — current milestone state and handoff into Phase 19

### Prior phase authority
- `.planning/phases/07-llm-inference-mvp/07-CONTEXT.md` — provider-neutral
  runtime seam, config-driven generation, and the explicit deferral of local
  serving in the original `llm-generate` MVP
- `.planning/milestones/v1.1-phases/10-closed-loop-campaign-contract-and-governance/10-CONTEXT.md`
  — dual-lane campaign posture and the requirement to keep contracts portable
  across general-purpose and specialized materials lanes
- `.planning/milestones/v1.1-phases/11-closed-loop-campaign-execution-bridge/11-CONTEXT.md`
  — config-authoritative model-lane selection, launch wrapper constraints, and
  additive lineage expectations
- `.planning/milestones/v1.1-phases/12-replay-comparison-and-operator-workflow/12-CONTEXT.md`
  — strict replay authority and comparison posture that Phase 19 must not
  destabilize

### LLM and serving docs
- `materials-discovery/developers-docs/llm-integration.md` — planned local
  adapter concept, current LLM architecture, and longer-term fine-tuning design
- `materials-discovery/developers-docs/llm-quasicrystal-landscape.md` — why
  specialized materials models are valuable but not assumed to be Zomic-native
- `materials-discovery/developers-docs/pipeline-stages.md` Section 13-15 —
  launch and replay behavior that local/specialized serving must preserve
- `materials-discovery/developers-docs/configuration-reference.md` — current
  backend adapter/provider fields and `SystemConfig` conventions

### Existing contract surface
- `materials-discovery/src/materials_discovery/common/schema.py` —
  `BackendConfig`, `LlmGenerateConfig`, and `LlmModelLaneConfig`
- `materials-discovery/src/materials_discovery/llm/runtime.py` — current
  adapter resolution seam (`mock` plus `anthropic_api_v1`)
- `materials-discovery/src/materials_discovery/llm/generate.py` — single
  generation runtime that local serving must extend
- `materials-discovery/src/materials_discovery/llm/launch.py` — lane resolution
  and launch overlay behavior
- `materials-discovery/src/materials_discovery/llm/replay.py` — replay
  assumptions that depend on stable lane/runtime identity
- `materials-discovery/src/materials_discovery/llm/schema.py` — run-manifest,
  launch-summary, and campaign-lineage contracts

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/src/materials_discovery/llm/runtime.py`: already owns the
  runtime adapter seam and is the natural place for a local HTTP-serving
  adapter.
- `materials-discovery/src/materials_discovery/common/schema.py`: already
  defines `LlmModelLaneConfig` and `model_lanes`, so Phase 19 can extend the
  config without inventing a second lane system.
- `materials-discovery/src/materials_discovery/llm/launch.py`: already resolves
  configured lanes and distinguishes configured-lane resolution from baseline
  fallback.
- `materials-discovery/src/materials_discovery/llm/replay.py`: already rebuilds
  replay config from recorded lane/runtime identity, so new local fields must be
  replay-safe.
- `materials-discovery/src/materials_discovery/llm/generate.py`: already
  records request, adapter, provider, model, and run-manifest artifacts.

### Established Patterns
- Keep generation runtime changes additive and centered on `llm-generate`.
- Keep config authoritative and route campaign launch/replay through resolved
  overlays instead of mutating YAML on disk.
- Prefer explicit operator-facing errors over silent runtime fallback.
- Preserve file-backed lineage so later benchmark and replay flows stay honest.

### Integration Points
- `materials-discovery/src/materials_discovery/llm/runtime.py` for local
  adapter resolution and connectivity validation
- `materials-discovery/src/materials_discovery/common/schema.py` for transport
  defaults and richer lane/runtime identity fields
- `materials-discovery/src/materials_discovery/llm/generate.py` for additive
  run-manifest and request identity recording
- `materials-discovery/src/materials_discovery/llm/launch.py` and
  `materials-discovery/src/materials_discovery/llm/replay.py` for consistent
  lane-resolution and replay compatibility

</code_context>

<specifics>
## Specific Ideas

- The safest Phase 19 cut is a local HTTP-serving seam that looks like the
  current hosted runtime from the generator's point of view.
- Phase 19 should make it impossible to think a specialized lane ran when the
  runtime actually fell back to hosted baseline behavior.
- Local-serving identity should be rich enough that later benchmark comparisons
  can distinguish model family, checkpoint, endpoint, and explicit lane
  resolution source without post-hoc guesswork.

</specifics>

<deferred>
## Deferred Ideas

- In-process `transformers` inference inside the Python runtime
- CLI-managed local-server lifecycle or process orchestration
- Autonomous execution or automatic launch fallback across lanes
- Zomic-native local generation adaptation or fine-tuned checkpoint training
- Broader chemistry expansion or UI-first orchestration

</deferred>

---

*Phase: 19-local-serving-runtime-and-lane-contracts*
*Context gathered: 2026-04-05*
