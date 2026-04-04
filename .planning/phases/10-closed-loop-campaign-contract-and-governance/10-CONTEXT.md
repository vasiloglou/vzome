# Phase 10: Closed-Loop Campaign Contract and Governance - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 10 defines the typed contract that turns the shipped dry-run
`mdisc llm-suggest` surface into materializable campaign intent.

This phase should deliver:

- typed proposal, approval, and campaign-spec contracts
- executable proposal actions that stay grounded in acceptance-pack analysis
- an explicit governance boundary between dry-run suggestions and approved
  launch intent
- file-backed lineage rooted in acceptance packs and eval-set references

This phase does not launch campaigns through `llm-generate`, replay campaigns,
or compare outcomes. Those belong to Phases 11 and 12.

</domain>

<decisions>
## Implementation Decisions

### Proposal unit
- **D-01:** Proposals should be system-scoped. One proposal belongs to one
  system from the acceptance pack and may bundle a small set of related
  execution actions for that system.
- **D-02:** Phase 10 should avoid both pack-wide multi-system proposals and
  single-action-only proposals as the primary contract shape.

### Action vocabulary
- **D-03:** The Phase 10 contract should support three typed action families
  from day one:
  - prompt and conditioning changes
  - composition-window changes
  - seed and motif variation changes
- **D-04:** Provider or runtime experimentation should not be a core action
  family in Phase 10. It can appear as metadata or a preferred execution lane,
  but not as the main campaign-action surface yet.

### Approval shape
- **D-05:** Approval must be represented by a separate typed approval artifact.
  Suggestion and proposal artifacts stay immutable after creation.
- **D-06:** Phase 10 should not use in-place approval flags or "spec creation
  implies approval" shortcuts.

### Campaign spec authority
- **D-07:** An approved proposal must materialize into a self-contained campaign
  spec that pins the resolved actions and launch inputs needed for later replay.
- **D-08:** The campaign spec may still reference source artifacts for context,
  but it must not depend on a thin pointer-only design.

### Model reliance posture
- **D-09:** Phase 10 should support a dual-lane model contract. Campaign
  proposals and campaign specs may target either:
  - general-purpose models
  - specialized materials models
- **D-10:** Specialized materials models mentioned in the research are
  first-class in the contract surface, not a later afterthought. This includes:
  - generation-side specialized models such as `CrystaLLM`,
    `CrystalTextLLM`, or similar Zomic-adapted descendants
  - evaluation-side specialized models such as `CSLLM`-style
    synthesizability and precursor-assessment models
- **D-11:** Phase 10 should not hard-code the milestone to one vendor or one
  currently implemented hosted adapter. Provider/model choice may be recorded as
  a preferred execution lane, but the contract itself must stay portable.

### Governance and phase inheritance
- **D-12:** Dry-run `llm-suggest` behavior must remain available as a safe mode
  even after the new proposal and approval contracts exist.
- **D-13:** Zomic remains the native generation representation.
- **D-14:** The no-DFT boundary remains explicit and must not be weakened by the
  new campaign contract surface.
- **D-15:** The workflow remains file-backed and operator-governed. No
  suggestion may mutate generation inputs, campaign state, or active-learning
  artifacts without an explicit approval step.

### the agent's Discretion
- Exact schema field names and version strings for proposal, approval, and
  campaign-spec models
- Exact artifact filenames and storage-path helpers, as long as they follow the
  existing file-backed artifact conventions
- Exact enum names and subfields for the three action families
- Exact approval metadata fields such as operator notes or rejection reasons
- Exact summary JSON printed by the CLI for dry-run versus approved artifacts

</decisions>

<specifics>
## Specific Ideas

- Keep the current `LlmSuggestionItem` spirit, but evolve it from plain text
  advice into typed, executable proposal actions per system.
- Make specialized materials models an explicit part of the campaign contract so
  later phases can choose between general-purpose and domain-specialized LLM
  lanes without redesigning the schema.
- Treat campaign specs as the launch authority for later phases, not just a
  convenience wrapper around the acceptance pack.
- Preserve a very clear split between:
  - suggestion artifacts
  - approval artifacts
  - campaign specs

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` - v1.1 milestone goal, Project 3 focus, and the
  decision to prioritize closed-loop campaign execution before local serving
- `.planning/ROADMAP.md` - Phase 10 goal, deliverables, success criteria, and
  the Phase 10 to 12 boundary
- `.planning/REQUIREMENTS.md` - `LLM-06`, `LLM-08`, `LLM-09`, `LLM-10`,
  `LLM-11`, `OPS-05`, `OPS-06`, and `OPS-07`
- `.planning/STATE.md` - current milestone state and active phase handoff

### Prior phase authority
- `.planning/phases/06-zomic-training-corpus-pipeline/06-CONTEXT.md` - locked
  corpus, fidelity, and eval-set lineage posture
- `.planning/phases/07-llm-inference-mvp/07-CONTEXT.md` - locked
  `llm-generate` runtime posture, artifact lineage, and provider-neutral seam
- `.planning/phases/08-llm-evaluation-and-pipeline-integration/08-CONTEXT.md`
  - additive evaluation/report integration and benchmark posture
- `.planning/phases/09-fine-tuned-zomic-model-and-closed-loop-design/09-CONTEXT.md`
  - acceptance-pack contract, conditioned prompting posture, and the dry-run
  `llm-suggest` boundary

### LLM design docs
- `materials-discovery/developers-docs/llm-integration.md` - current LLM
  architecture, dry-run `llm-suggest` description, provider seam, and
  specialized model research summary
- `materials-discovery/developers-docs/llm-integration.md` Section 3.1 -
  current `mdisc llm-suggest` design as a dry-run acceptance workflow
- `materials-discovery/developers-docs/llm-integration.md` Section 4.1 -
  fine-tuning and model-selection research including `LLaMA-3 8B`
- `materials-discovery/developers-docs/llm-quasicrystal-landscape.md` -
  specialized materials-model landscape including `CrystaLLM`,
  `CrystalTextLLM`, `MatLLMSearch`, and `CSLLM`
- `materials-discovery/developers-docs/pipeline-stages.md` Section 11 -
  current `mdisc llm-suggest` CLI contract and artifact paths

### Existing contract surface
- `materials-discovery/src/materials_discovery/cli.py` - current `llm-suggest`
  command and CLI orchestration pattern
- `materials-discovery/src/materials_discovery/llm/suggest.py` - current dry-run
  suggestion builder
- `materials-discovery/src/materials_discovery/llm/schema.py` - existing
  `LlmAcceptancePack`, `LlmSuggestion`, and related typed LLM contracts
- `materials-discovery/src/materials_discovery/llm/storage.py` - current
  acceptance-pack path helpers and file-backed artifact conventions
- `materials-discovery/src/materials_discovery/common/schema.py` -
  `LlmGenerateConfig` and additive config conventions
- `materials-discovery/src/materials_discovery/llm/runtime.py` - current
  provider seam (`mock` plus `anthropic_api_v1`) that the new contract must not
  overfit

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/src/materials_discovery/llm/suggest.py`: current
  acceptance-pack to suggestion mapping and per-system suggestion shape
- `materials-discovery/src/materials_discovery/llm/schema.py`: existing
  acceptance and suggestion models that can be extended into proposal and
  approval contracts
- `materials-discovery/src/materials_discovery/llm/storage.py`: current
  file-backed artifact-root helpers for acceptance-pack outputs
- `materials-discovery/src/materials_discovery/common/schema.py`:
  `LlmGenerateConfig` and additive config-extension pattern
- `materials-discovery/src/materials_discovery/llm/runtime.py`: provider/model
  seam that already separates adapter, provider, and model identity
- `materials-discovery/src/materials_discovery/active_learning/select_next_batch.py`:
  existing feedback-loop provenance style and deterministic selection posture

### Established Patterns
- File-backed JSON and JSONL artifacts under `materials-discovery/data/`
- Pydantic contracts define the durable interface, while CLI commands stay thin
- New LLM surfaces are additive and do not replace existing pipeline artifacts
- Current real-provider support is intentionally narrow, while docs preserve a
  broader provider and model seam

### Integration Points
- `materials-discovery/src/materials_discovery/cli.py` for future proposal and
  approval commands or modes
- `materials-discovery/src/materials_discovery/llm/` as the implementation home
  for proposal, approval, and campaign-spec contracts
- `materials-discovery/data/benchmarks/llm_acceptance/{pack_id}/` as the
  natural starting point for Phase 10 artifact lineage
- Existing `llm-generate` config and run-manifest contracts, which Phase 11 will
  eventually consume from the new campaign spec

</code_context>

<deferred>
## Deferred Ideas

- Actual campaign launch through `llm-generate` - Phase 11
- Replay and comparison of saved campaign outcomes - Phase 12
- Local or fine-tuned model serving infrastructure - later milestone
- Fully autonomous mutation of the active-learning loop - later milestone
- Broader provider bakeoffs or vendor-specific optimization as a primary action
  family - later phase once the governance contract is stable

</deferred>

---

*Phase: 10-closed-loop-campaign-contract-and-governance*
*Context gathered: 2026-04-04*
