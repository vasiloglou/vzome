# Phase 10: Closed-Loop Campaign Contract and Governance - Research

**Date:** 2026-04-04  
**Status:** Complete  
**Requirements:** `LLM-06`, `OPS-05`

## Goal

Turn the shipped Phase 9 dry-run `mdisc llm-suggest` surface into a typed,
file-backed campaign-governance layer without launching anything yet.

Phase 10 must define:

- typed proposal artifacts
- separate typed approval artifacts
- self-contained campaign specs for later launch/replay work
- a clear dry-run versus approved-launch boundary

Phase 10 must not:

- launch `llm-generate`
- mutate active-learning outputs
- introduce a second candidate schema
- overfit the contract to one current provider adapter

## Current Surface

### Acceptance-pack input is already typed and stable

The current `materials-discovery` LLM ladder already has a durable analysis
surface:

- `materials-discovery/src/materials_discovery/llm/acceptance.py`
- `materials-discovery/src/materials_discovery/llm/schema.py`
- `materials-discovery/src/materials_discovery/llm/storage.py`

`LlmAcceptancePack` is already the right input seam for campaign governance.
Each system record carries:

- the system name
- benchmark comparison paths
- per-system failing metrics
- release-gate posture
- the optional eval-set manifest lineage

That means Phase 10 does not need a new benchmark-analysis layer. It needs a
better contract over the results of that analysis.

### `llm-suggest` is currently heuristic, readable, and too thin

The current implementation:

- loads an acceptance pack
- maps failing metrics to plain-language `LlmSuggestionItem`s
- writes one dry-run `suggestions.json`

That is a good operator-facing scaffold, but it is not yet materializable
campaign intent because it lacks:

- typed action families
- proposal identity
- approval state
- spec lineage
- pinned baseline config references

### Provider/model implementation is intentionally narrower than the future seam

The runtime in `materials-discovery/src/materials_discovery/llm/runtime.py`
currently supports:

- deterministic mock
- one hosted real adapter: `anthropic_api_v1`

The docs and research intentionally describe a broader lane:

- general-purpose hosted LLMs for prompt-driven generation/evaluation
- specialized materials models such as `CrystaLLM`, `CrystalTextLLM`,
  `MatLLMSearch`, and `CSLLM`

Phase 10 should preserve that portability. Provider/model choice belongs in the
proposal/spec metadata, not in the core action vocabulary.

## Key Design Constraints

### 1. Proposals must stay system-scoped

This matches:

- the current acceptance-pack structure
- the benchmark lane organization
- the eventual need to approve or reject campaigns per chemistry/system

Pack-wide proposals would blur approval and replay boundaries. Single-action
proposals would create too much operator overhead.

### 2. The action vocabulary should stay small and typed

The locked action families are:

- `prompt_conditioning`
- `composition_window`
- `seed_motif_variation`

This is enough to express the next real closed-loop moves without smuggling in
future execution concerns like vendor bakeoffs or runtime tuning as first-class
campaign actions.

### 3. Approval needs a separate artifact

Phase 10 is the governance phase. A separate approval artifact gives us:

- immutable dry-run proposal outputs
- an auditable decision record
- a clean pre-launch boundary for later phases

This also makes rejection a first-class outcome instead of a silent absence of
execution.

### 4. Campaign specs need a pinned baseline config

An acceptance pack alone is not enough to reconstruct later launch intent.
Important launch inputs currently live in the system config:

- `template_family`
- `composition_bounds`
- `default_count`
- `llm_generate` prompt/example/seed settings

That means a self-contained campaign spec should pin:

- the source system config path
- a stable hash of the source system config
- a baseline snapshot of the launch-relevant config subset
- the typed proposal actions that should later be applied to that baseline

This is the cleanest compromise between:

- Phase 10 not launching anything yet
- Phase 11 needing enough information to deterministically materialize a real
  `llm-generate` run

### 5. Specialized models must be first-class metadata, not a hard dependency

The user explicitly wants specialized materials LLMs in-scope. The right Phase
10 move is to support a dual-lane contract:

- `general_purpose`
- `specialized_materials`

Each proposal action or proposal summary can record:

- preferred model lane
- optional preferred provider
- optional preferred model
- optional specialized model family label

That keeps the contract portable while making research-backed specialized lanes
visible to operators and later execution code.

## Recommended Artifact Layout

### Acceptance-pack rooted proposal/approval artifacts

Keep dry-run and approval outputs attached to the acceptance-pack directory:

- `data/benchmarks/llm_acceptance/{pack_id}/suggestions.json`
- `data/benchmarks/llm_acceptance/{pack_id}/proposals/{proposal_id}.json`
- `data/benchmarks/llm_acceptance/{pack_id}/approvals/{approval_id}.json`

Why this works:

- it keeps dry-run artifacts near the benchmark analysis that produced them
- it preserves the current operator mental model
- it keeps replay lineage obvious

### Dedicated campaign-spec root

Approved campaign specs should live under a durable campaign directory:

- `data/llm_campaigns/{campaign_id}/campaign_spec.json`

This gives Phases 11 and 12 a stable root for:

- launch outputs
- replay metadata
- comparison outputs

without overloading the acceptance-pack directory as a long-lived run home.

## Recommended Contract Split

### Suggestion bundle

The top-level `llm-suggest` output should stay dry-run and human-readable, but
it should now point at typed system-scoped proposals instead of only carrying
plain-language advice.

Recommended shape:

- acceptance-pack metadata
- overall status
- one summary row per system proposal
- explicit proposal file path per summary row

### Proposal artifact

Each system proposal should be a durable typed object with:

- proposal identity
- source acceptance-pack lineage
- system name
- benchmark evidence and failing metrics
- priority
- a bounded list of typed actions
- optional preferred model lane/provider/model metadata

### Approval artifact

The approval artifact should record:

- approval identity
- proposal identity/path
- decision (`approved` or `rejected`)
- operator identity
- timestamp
- optional notes/reason
- campaign id when approved

Rejected approvals should still be written to disk.

### Campaign spec

The campaign spec should be self-contained for later execution and replay:

- campaign id
- approved proposal identity
- source config path and config hash
- launch baseline snapshot
- typed actions to apply
- proposal/approval/acceptance-pack/eval-set lineage

Phase 10 does not need to resolve the final launched `llm-generate` request
body. It only needs to pin the baseline and the actions so Phase 11 can do that
deterministically.

## Risks and Edge Cases To Lock In Planning

### Acceptance packs can have no failing metrics

The current dry-run path emits a "promote to broader comparisons" style
suggestion. In Phase 10 that should still produce a typed proposal, but the
proposal should remain clearly dry-run and non-executing. The action family can
still be `prompt_conditioning` with a low-priority exploratory intent, or the
proposal can explicitly carry zero executable actions and remain unapprovable.

Recommendation: keep at least one low-priority typed action so the proposal
surface stays uniform.

### Proposal generation must not silently mutate files beyond its own artifacts

`llm-suggest` remains dry-run only. No config files, eval sets, candidate JSONL,
or active-learning artifacts should change.

### Approval should not imply launch

Approval materializes a spec and stops there. Phase 11 owns any actual execution
bridge into `llm-generate`.

### Proposal generation may benefit from optional config context

An acceptance pack is enough to generate typed actions, but an optional system
config input can enrich:

- current prompt template lineage
- current composition bounds for action hints
- seed/example-pack references

Recommendation: design the proposal contract so it works without the config, but
allow CLI enrichment with config when available.

## Recommended Phase Split

### Plan 01: Contract foundation

Define:

- typed proposal/approval/spec/lineage models
- campaign storage helpers
- schema/storage tests

### Plan 02: Typed dry-run proposal generation

Extend `llm-suggest` so it:

- reads acceptance packs
- writes a suggestion bundle plus per-system proposal files
- maps failing metrics into the three typed action families
- keeps dry-run semantics intact

### Plan 03: Approval and spec governance

Add approval/spec helpers and operator CLI so an approved proposal can become a
self-contained campaign spec without launching anything.

## Validation Architecture

Phase 10 is contract-heavy and should rely on focused pytest coverage:

- schema tests for typed campaign models
- storage-path tests for artifact layout
- core tests for proposal mapping logic
- CLI tests for dry-run suggestion output
- CLI/core tests for approval/spec materialization

The phase should end with:

- targeted Phase 10 pytest commands per wave
- full `materials-discovery` pytest
- `git diff --check`

Because this phase changes `materials-discovery/`, execution plans must remind
the implementer to update `materials-discovery/Progress.md` on every code/docs
change under that directory.

## Planning Outcome

Phase 10 should be planned as three waves:

1. contract and storage foundation
2. typed dry-run proposal generation
3. approval/spec governance and docs

That order minimizes blast radius and keeps the launch boundary locked before
Phase 11 starts execution work.
