# Architecture Research: v1.6 Translator-Backed External Materials-LLM Benchmark MVP

**Milestone:** `v1.6`  
**Researched:** 2026-04-07  
**Confidence:** High for repo-fit and storage shape; medium for the exact external prompt/result schema because the benchmark task contract is not frozen yet.

## Executive Position

`v1.6` should be a new sibling benchmark workflow, not a mutation of the
shipped `llm-generate` or `llm-evaluate` paths and not a broad expansion of
`SystemConfig`.

The architecture already has the right primitives:

- translation bundles under `data/llm_translation_exports/{export_id}/`
- immutable checkpoint registrations and mutable internal-control lifecycle
- benchmark summaries under `data/benchmarks/...`
- run manifests, stage manifests, `benchmark_context`, and `serving_identity`

The safest extension is:

1. freeze a translated benchmark set from translation-bundle inventory rows
2. register downloaded external models as immutable repo artifacts
3. execute benchmark targets through a dedicated external-benchmark runtime seam
4. normalize both external targets and internal controls into one scorecard

That preserves the repo's current posture: file-backed, schema-driven,
CLI-first, replayable, and honest about fidelity loss.

## Integration Points

- `materials-discovery/src/materials_discovery/llm/schema.py`
- `materials-discovery/src/materials_discovery/llm/storage.py`
- `materials-discovery/src/materials_discovery/llm/runtime.py`
- `materials-discovery/src/materials_discovery/common/manifest.py`
- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/src/materials_discovery/llm/translation_bundle.py`
- `materials-discovery/src/materials_discovery/llm/checkpoints.py`
- `materials-discovery/src/materials_discovery/llm/serving_benchmark.py`
- `materials-discovery/configs/llm/`
- `materials-discovery/data/llm_translation_exports/`
- `materials-discovery/data/llm_checkpoints/`
- `materials-discovery/data/benchmarks/`

## Recommended Architecture

```text
CandidateRecord JSONL
  -> llm-translate
  -> data/llm_translation_exports/{export_id}/
      manifest.json
      inventory.jsonl
      payloads/

Translation bundle(s)
  -> freeze translated benchmark set
  -> data/benchmarks/llm_external_sets/{set_id}/
      manifest.json
      cases.jsonl

External model registration spec
  -> llm-register-external-model
  -> data/llm_external_models/{model_id}/registration.json

Benchmark spec
  -> llm-external-benchmark --spec ...
  -> data/benchmarks/llm_external/{benchmark_id}/
      smoke_checks.json
      benchmark_summary.json
      targets/{target_id}/run_manifest.json
      targets/{target_id}/environment.json
      targets/{target_id}/case_results.jsonl
      targets/{target_id}/raw_responses.jsonl

Internal controls
  -> existing campaign/checkpoint/serving artifacts
  -> referenced into the same benchmark summary
```

## New vs Modified Components

### New Components

| Component | Why it should exist | Responsibility |
|-----------|---------------------|----------------|
| `TranslatedBenchmarkSet` artifact family | Translation bundles are reusable exports, not curated benchmark inputs | Freeze a reproducible subset of translation rows plus fidelity boundaries and inclusion rules |
| `ExternalModelRegistration` artifact family | Downloaded external models need immutable identity just like adapted checkpoints do | Record model family, local path or endpoint contract, supported translation families, version/revision, prompt contract, and static provenance |
| `external_runtime` seam | Existing `llm/runtime.py` is generation-oriented and assumes current LLM request shape | Execute external targets through either an OpenAI-compatible server or an exec-wrapped local runner without polluting the core generation path |
| `ExternalBenchmark` orchestrator | Current serving benchmark assumes launch/evaluate roles on internal flows | Run smoke checks, execute per-case translated prompts, normalize outputs, and build scorecards |
| `ExternalBenchmarkScorecard` schema | Current `recommendation_lines` are too thin by themselves for fidelity-aware translated cases | Aggregate overall metrics plus `target_family`, `fidelity_tier`, and control deltas |

### Modified Components

| Component | Modification | Why |
|-----------|-------------|-----|
| `llm/schema.py` | Add typed models for translated benchmark sets, external model registrations, external benchmark specs, smoke checks, per-target run manifests, case results, and summary/scorecard artifacts | Keep the new workflow schema-driven like the rest of the repo |
| `llm/storage.py` | Add helpers for `data/llm_external_models/`, `data/benchmarks/llm_external_sets/`, and `data/benchmarks/llm_external/` | Avoid ad hoc paths in the CLI or runtime |
| `cli.py` | Add benchmark-set freeze, external-model registration, and benchmark execution commands | Keep the milestone CLI-first and operator-governed |
| `common/manifest.py` usage | Reuse standard stage-manifest writing for benchmark-set freeze and benchmark execution | Keep provenance visible to existing tooling |
| `llm/runtime.py` | Reuse only the generic readiness/request helpers where it helps; do not merge external benchmark logic into ordinary `llm-generate` | Preserve the current Zomic-native generation path |
| `translation_bundle.py` | No contract rewrite required; at most add helper utilities for inventory-row selection or bundle fingerprinting | v1.5 already established the correct upstream artifact family |

## Architectural Seams for Downloaded External Model Lanes

### 1. Keep external-model execution out of `SystemConfig`

Do not add a large new `external_models:` subtree to `SystemConfig`.

Reason:

- `SystemConfig` currently describes one system pipeline and its normal
  generation/evaluation lanes.
- downloaded external models in `v1.6` are benchmark targets, not first-class
  replacements for the main `llm-generate` workflow
- mixing them into `SystemConfig` would blur the boundary between the normal
  Zomic workflow and a benchmark-only experiment surface

Recommendation:

- keep internal controls on their current `configs/systems/*.yaml` contracts
- define external targets in a dedicated benchmark spec under
  `configs/llm/*.yaml`
- reference immutable model registrations from that spec

### 2. Add an immutable external-model registration contract

This should mirror the checkpoint-registration pattern, but without lifecycle
state in the MVP.

Recommended fields:

- `model_id`
- `model_family`
- `system_scope` or `supported_systems`
- `translation_target_families`
- `adapter`
- `provider`
- `model`
- `local_model_path` or `api_base`
- `model_revision`
- `download_source`
- `license/posture`
- `prompt_contract`
- `response_parser_key`
- `notes`
- `fingerprint`

Why:

- internal controls already rely on immutable checkpoint facts plus separate
  runtime selection
- external models need the same identity discipline before any benchmark
  results should influence roadmap decisions

### 3. Add a dedicated external runtime seam with two lane types

The runtime seam should support exactly two MVP execution surfaces:

- `openai_compat_v1`
  - for already-running local or remote OpenAI-compatible model servers
  - reuse the current readiness-probe behavior
- `exec_prompt_runner_v1`
  - for downloaded models launched through a repo-owned wrapper command
  - reuse the validation subsystem's subprocess JSON I/O pattern, but keep it
    in an LLM-specific module instead of overloading validation adapters

This should be benchmark-only runtime infrastructure. The CLI still should not
start or supervise long-lived model servers.

### 4. Normalize target execution into one case-result contract

Every target, external or internal, should produce one typed case-result row
per translated benchmark case.

That row should include:

- `benchmark_id`
- `target_id`
- `case_id`
- `model_id` or internal control identity
- `translation_target_family`
- `fidelity_tier`
- `loss_reasons`
- `payload_hash`
- `request_fingerprint`
- `response_status`
- `parsed_output`
- `task metrics`
- `lineage pointers`

This is the key seam that lets the scorecard layer stay simple.

### 5. Treat internal controls as referenced targets, not reimplemented targets

The new benchmark should not duplicate internal campaign/checkpoint logic.

Instead:

- benchmark specs should point at the current promoted or explicit-pin internal
  control configs
- execution should reuse existing serving/campaign lineage where possible
- the external benchmark summary should carry pointers to the existing internal
  artifacts such as run manifests, launch summaries, comparison outputs, and
  `serving_identity`

That keeps `v1.6` additive.

## Where Each Artifact Should Live

### Translated benchmark-set definitions

**Config templates**

- `materials-discovery/configs/llm/{system_slug}_translated_benchmark_set.yaml`

**Materialized artifacts**

- `materials-discovery/data/benchmarks/llm_external_sets/{set_id}/manifest.json`
- `materials-discovery/data/benchmarks/llm_external_sets/{set_id}/cases.jsonl`

**Why here**

- this is benchmark input, not a general translation export
- it follows the existing `data/benchmarks/...` convention
- it keeps `llm_eval_sets/` reserved for Zomic-text eval examples

### External model metadata

**Config templates**

- `materials-discovery/configs/llm/{model_id}_external_model.yaml`

**Materialized artifacts**

- `materials-discovery/data/llm_external_models/{model_id}/registration.json`

**Why here**

- this mirrors `data/llm_checkpoints/{checkpoint_id}/registration.json`
- the registration can be immutable even if later benchmark participation
  changes

### Execution lineage

**Per benchmark run**

- `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/smoke_checks.json`
- `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/targets/{target_id}/run_manifest.json`
- `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/targets/{target_id}/environment.json`
- `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/targets/{target_id}/case_results.jsonl`
- `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/targets/{target_id}/raw_responses.jsonl`

**Standard stage manifests**

- `materials-discovery/data/manifests/{system_slug}_{set_id}_llm_external_benchmark_set_manifest.json`
- `materials-discovery/data/manifests/{system_slug}_{benchmark_id}_llm_external_benchmark_manifest.json`

**Why here**

- the benchmark run itself needs its own artifact family because there is no
  existing campaign directory for external targets
- stage manifests keep the new workflow visible to current provenance tooling

### Scorecards

**Primary summary**

- `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/benchmark_summary.json`

**Optional detailed sidecars**

- `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/scorecard_by_target.json`
- `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/scorecard_by_case.jsonl`

**Why here**

- this follows the current `llm_serving` benchmark pattern
- the scorecard should be a typed benchmark summary first, not a new loose
  reporting concept

## Data Flow

### 1. Freeze the translated benchmark set

Input:

- one or more translation bundle manifests under
  `data/llm_translation_exports/{export_id}/manifest.json`

Process:

- load bundle manifests and `TranslationInventoryRow`s
- apply explicit inclusion rules:
  - systems
  - target families
  - allowed fidelity tiers
  - explicit lossy-case policy
  - per-system caps
- snapshot the selected rows into `cases.jsonl`

Important detail:

- do not rely on live bundle paths alone
- each frozen case should carry `emitted_text`, `payload_hash`,
  `source_bundle_manifest_path`, `candidate_id`, `target_family`,
  `fidelity_tier`, and `loss_reasons`

This makes the benchmark set reproducible even if operators later regenerate a
bundle with the same `export_id`.

### 2. Resolve target registrations and smoke-check execution surfaces

For external targets:

- resolve `registration.json`
- validate translation-target compatibility
- capture static model metadata
- run smoke checks on the declared execution surface

For internal controls:

- resolve the current promoted or explicit-pin lane through existing config and
  checkpoint-lifecycle logic
- capture current `serving_identity`

### 3. Execute one target against the frozen cases

Each target should write:

- one request/response trace per case
- parsed case results
- aggregate metrics
- runtime/environment capture
- one run manifest tying together:
  - benchmark set manifest
  - model registration or internal control identity
  - output file paths
  - timing
  - adapter/provider/model details
  - current hashes/fingerprints

### 4. Build a fidelity-aware scorecard

The summary layer should aggregate:

- overall metrics
- metrics by `translation_target_family`
- metrics by `fidelity_tier`
- explicit `lossy` slice
- deltas versus the selected internal control arm

This is the right place to answer the milestone question:

- does any downloaded external model outperform or complement the current
  promoted/pinned internal controls
- only on exact/anchored translations, or also on lossy ones
- at what runtime and operator cost

## Recommended Scorecard Shape

The benchmark summary should not stop at one flat recommendation list.

Recommended summary sections:

- `overall`
  - success rate
  - task metric means
  - latency
  - cost estimate
  - operator friction
- `by_fidelity_tier`
  - `exact`
  - `anchored`
  - `approximate`
  - `lossy`
- `by_target_family`
  - `cif`
  - `material_string`
- `control_deltas`
  - promoted internal vs external
  - explicit pinned internal vs external
- `recommendation_lines`
  - roadmap-facing plain-language guidance

Why this shape:

- `v1.5` made fidelity explicit, so `v1.6` must not collapse it away in the
  benchmark summary
- roadmap decisions should be based on where external models help, not only on
  a single blended aggregate

## Anti-Patterns to Avoid

### Do not overload `LlmEvalSetExample`

`llm_eval_sets/` exist for Zomic-text examples. CIF or material-string payloads
should stay in a separate translated benchmark-set family.

### Do not treat external models like checkpoint families

The internal checkpoint lifecycle exists because those models are part of the
core generation workflow. Downloaded external models in `v1.6` are benchmark
subjects. Registration is enough; promotion/retirement is unnecessary scope.

### Do not benchmark directly off live translation bundles

Bundles are reusable exports. A benchmark needs a frozen subset artifact with a
stable manifest and case inventory.

### Do not bypass existing internal lineage

Internal controls already have run manifests, checkpoint lineage, and serving
identity. Reference those artifacts instead of rebuilding them inside the new
benchmark code.

### Do not let lossy cases disappear into the overall aggregate

Lossy translation is a first-class architectural fact after `v1.5`. The
scorecard must preserve it.

## Suggested Phase Order

### Phase 1: Freeze translated benchmark-set contracts

Build first:

- translated benchmark-set schema
- storage helpers
- freeze command/spec
- stage-manifest writing

Why first:

- it locks the benchmark input shape before runtime work begins
- it forces the inclusion and fidelity policy to become explicit early

### Phase 2: Register external models and add smoke-only runtime support

Build second:

- external model registration schema and storage
- runtime seam for `openai_compat_v1` and `exec_prompt_runner_v1`
- smoke checks and environment capture

Why second:

- it proves the repo can identify and reach each downloaded model before
  mixing in benchmark scoring

### Phase 3: Execute one external target against one internal control

Build third:

- external benchmark spec
- per-target run manifests
- case-result normalization
- internal-control reference wiring

Why third:

- it validates the core data flow with the smallest possible comparison surface
- it reuses existing promoted/pinned control patterns without committing to a
  large matrix too early

### Phase 4: Add scorecards and roadmap-facing recommendations

Build fourth:

- fidelity-aware aggregation
- control deltas
- benchmark summary artifact
- operator docs

Why fourth:

- recommendation logic is trustworthy only after per-case lineage and target
  normalization are stable

## Why This Build Order Reduces Risk

- It freezes the translated-case contract before runtime variability enters the
  picture.
- It keeps external runtime work benchmark-scoped instead of turning into a
  premature general serving framework.
- It preserves the current internal control arm instead of refactoring it.
- It follows the repo's existing pattern of immutable inputs first, execution
  second, operator summary last.

## Concise Recommended Architecture Shape for v1.6

`v1.6` should be a dedicated `llm_external_benchmark` workflow layered on top
of the shipped translation bundle surface:

- translation bundles remain the reusable upstream export layer
- a new frozen translated benchmark-set artifact snapshots curated cases
- downloaded external models get immutable registrations, not lifecycle state
- a benchmark-only external runtime executes those targets with smoke checks and
  environment capture
- internal controls stay on the current promoted/pinned checkpoint and campaign
  lineage
- one typed scorecard summarizes external-vs-internal results by target family
  and fidelity tier

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/ARCHITECTURE.md`
