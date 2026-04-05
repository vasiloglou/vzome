# Phase 11: Closed-Loop Campaign Execution Bridge - Research

**Date:** 2026-04-04  
**Status:** Complete  
**Requirements:** `LLM-08`, `LLM-10`, `OPS-06`

## Goal

Turn the approved campaign-spec artifacts from Phase 10 into a controlled,
reproducible execution wrapper over the existing `mdisc llm-generate` path.

Phase 11 must:

- launch approved campaign specs without creating a second generation engine
- resolve typed campaign actions into concrete launch inputs deterministically
- preserve standard `CandidateRecord` and manifest outputs
- add campaign lineage that survives beyond the launch itself

Phase 11 must not:

- auto-chain the full downstream pipeline
- add resume semantics
- weaken the approval boundary from Phase 10
- hard-code the milestone to one provider or one exact model

## Current Surface

### Phase 10 already ships the governance boundary

The current campaign surface is real and typed:

- `materials-discovery/src/materials_discovery/llm/schema.py`
- `materials-discovery/src/materials_discovery/llm/campaigns.py`
- `materials-discovery/src/materials_discovery/llm/storage.py`
- `materials-discovery/src/materials_discovery/cli.py`

The repo now has:

- typed dry-run proposals
- separate approval artifacts
- self-contained `campaign_spec.json`
- deterministic `campaign_id`

What does **not** exist yet:

- a launch command
- a launch-summary artifact
- action-to-runtime resolution
- campaign-aware `llm-generate` lineage
- downstream manifest propagation for campaign lineage

### `llm-generate` is already the right runtime authority

The current generation path in
`materials-discovery/src/materials_discovery/llm/generate.py` already does the
hard work:

- resolve seed/example-pack inputs
- assemble prompts
- select an LLM adapter through `llm/runtime.py`
- compile Zomic
- convert passed outputs into `CandidateRecord`
- write run-level prompt / attempt / compile artifacts
- write an additive `LlmRunManifest`

That means Phase 11 should wrap and extend this path, not fork it.

### The current config surface cannot yet express configured model lanes

The key Phase 10 decision was:

- campaign actions choose among configured lanes such as `general_purpose` and
  `specialized_materials`

But the current config in `common/schema.py` only supports one active backend
LLM tuple:

- `backend.llm_adapter`
- `backend.llm_provider`
- `backend.llm_model`
- `backend.llm_api_base`

Phase 11 therefore needs an additive config seam for lane selection. Without
that seam, the Phase 10 dual-lane contract is only metadata, not executable
authority.

## Key Design Findings

### 1. The launch bridge needs a dedicated wrapper artifact family

Keeping standard roots primary is the right call, but the operator still needs
an auditable campaign-level wrapper for each launch. The clean additive shape is
to keep:

- standard outputs under existing roots:
  - `data/candidates/...`
  - `data/calibration/...`
  - `data/manifests/...`
  - `data/llm_runs/...`

while adding campaign wrapper artifacts under:

- `data/llm_campaigns/{campaign_id}/launches/{launch_id}/...`

Recommended wrapper files:

- `launch_summary.json`
- `resolved_launch.json`
- optional materialized seed file if one is synthesized from eval-set examples

This gives Phase 11:

- a clear failure/success envelope per launch
- stable pointers back to standard outputs
- a place to persist the resolved overlay without mutating the source YAML

### 2. Campaign actions should resolve into a runtime overlay, not a rewritten config

The Phase 11 context already locked this decision, and the code confirms it is
the lowest-blast-radius path.

Recommended structure:

- load the campaign spec
- load the referenced system config
- validate the config hash against `launch_baseline.system_config_hash`
- derive an in-memory launch overlay
- apply that overlay to a copied `SystemConfig`
- call the existing `generate_llm_candidates(...)`

This preserves:

- the baseline YAML file as authority
- the current manual `llm-generate` command
- deterministic launch inputs that can be written to disk as resolved artifacts

### 3. Prompt-conditioning actions require one additive prompt seam

Current prompting only knows:

- `prompt_template`
- optional seed Zomic
- optional conditioning examples

There is no current field for campaign-specific instruction deltas. Phase 11
therefore needs one additive seam such as:

- prompt instruction deltas passed directly into prompt assembly, or
- a copied config field consumed by `build_generation_prompt(...)`

The safer choice is to keep the config baseline unchanged and pass prompt
instruction deltas as explicit launch-time overrides. That keeps Phase 11
faithful to the "runtime overlay, not YAML mutation" decision.

### 4. Composition-window actions can already map cleanly

This is the simplest family to execute. The action can deterministically change
the copied `SystemConfig.composition_bounds` before launch.

If a proposal already carries `target_bounds`, use them directly.
If it only carries a window strategy such as
`tighten_around_validated_hits`, the launch helper should still apply a fixed,
deterministic transformation rather than consulting live heuristics.

That deterministic transformation belongs in a dedicated launch-resolution
helper, not in CLI code.

### 5. Seed/motif actions need deterministic seed resolution

The seed/motif action family is more abstract than the current
`llm-generate --seed-zomic PATH` surface. Today the spec can carry:

- `variation_strategy`
- `seed_source_hint`
- `motif_tags`

but not a concrete launch file path.

Phase 11 therefore needs a deterministic seed-resolution rule. The safest v1.1
behavior is:

1. If the launch baseline already has `seed_zomic_path`, keep or reuse it.
2. Else if the launch baseline has `example_pack_path`, choose a deterministic
   same-system example from the eval set and materialize its Zomic text as a
   launch seed artifact under the campaign launch directory.
3. Else fail clearly with a campaign-launch resolution error.

This keeps the seed family executable without inventing free-form motif search.

### 6. Campaign lineage must be recorded both in run artifacts and in downstream manifests

Current `llm-generate` lineage lives in two places:

- run-level artifacts in `data/llm_runs/...`
- candidate provenance fields like `llm_run_id`, `llm_adapter`, `prompt_path`

Current downstream stage manifests do **not** automatically carry campaign or
LLM lineage. They only receive `source_lineage` in the ingest/reference-pack
flows, and benchmark context in specific later phases.

To satisfy `OPS-06`, Phase 11 needs:

- additive campaign fields in the LLM run manifest and/or launch summary
- additive candidate provenance fields for campaign identity
- helpers that let later stage commands derive campaign lineage from the input
  candidate file or run manifest and pass it into `build_manifest(...)`
- additive pipeline-manifest support so the final umbrella artifact can also
  keep the same lineage

Without downstream propagation, Phase 11 would only satisfy "launch lineage,"
not "through downstream artifacts."

## Recommended Implementation Split

### Plan 01: launch contract and resolution foundation

Land the additive contract pieces first:

- lane-aware config seam
- launch-summary / resolved-launch artifact models
- campaign launch storage helpers
- deterministic action-resolution helpers for prompt, composition, and seed

This is the lowest-risk place to pin exact semantics before CLI wiring.

### Plan 02: execute approved campaign specs through `llm-generate`

Once the overlay semantics are stable:

- extend `generate_llm_candidates(...)` and prompt assembly with additive
  launch overrides
- create `mdisc llm-launch --campaign-spec ...`
- write campaign launch summary artifacts
- keep manual `llm-generate` behavior green

### Plan 03: propagate campaign lineage beyond launch

After launch works:

- propagate campaign lineage into downstream manifests
- keep `CandidateRecord` artifacts standard
- add campaign-aware integration tests and doc updates

That split keeps the hardest semantic work in Wave 1 and the wider regression
surface in Wave 3.

## Risks and Edge Cases To Lock In Planning

### Config drift

`campaign_spec.launch_baseline.system_config_path` points at a real file on
disk, and that file may change after approval. Phase 11 must fail fast when the
current config hash no longer matches the pinned spec hash. Silent drift would
break reproducibility.

### Lane preference versus lane availability

The Phase 10 contract allows action-level lane preferences, but a config may
not define every lane. The launch bridge should deterministically resolve the
best available lane and record both:

- what was requested
- what was actually used

If no acceptable lane exists, launch should fail before provider calls.

### Partial launch failure

The current `llm-generate` path already writes partial raw/compile artifacts
during generation. Phase 11 should preserve that behavior and wrap it with a
campaign launch summary marked failed. It should not delete partial artifacts.

### Manual downstream continuation

Phase 11 intentionally does not auto-run `screen` or later stages. That means
the propagation path must work when an operator later runs standard stage
commands against campaign-generated candidate files.

### Existing manual path regression

Phase 11 touches `generate.py`, prompting, runtime selection, CLI routing, and
manifest writing. This is a classic regression zone. The plan must explicitly
keep the existing `llm-generate` command green when no campaign spec is
involved.

## Validation Architecture

### Focused test lanes

Recommended focused Phase 11 commands:

- `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_launch_core.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_launch_cli.py tests/test_cli.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_campaign_lineage.py tests/test_report.py -x -v`

### Existing tests to keep in play

The following existing tests are especially relevant:

- `materials-discovery/tests/test_llm_campaign_spec.py`
- `materials-discovery/tests/test_llm_approve_cli.py`
- `materials-discovery/tests/test_llm_generate_core.py`
- `materials-discovery/tests/test_llm_generate_cli.py`
- `materials-discovery/tests/test_cli.py`
- `materials-discovery/tests/test_real_mode_pipeline.py`

### Wave-0 additions Phase 11 should plan for

Phase 11 likely needs these new or expanded tests:

- `materials-discovery/tests/test_llm_launch_schema.py`
- `materials-discovery/tests/test_llm_launch_core.py`
- `materials-discovery/tests/test_llm_launch_cli.py`
- `materials-discovery/tests/test_llm_campaign_lineage.py`

### Manual checks still worth keeping

- Inspect one `launch_summary.json` and confirm it records requested lane,
  resolved lane, campaign spec path, approval path, and standard output paths.
- Run one approved campaign launch, then run `screen` or `report` manually and
  confirm the later manifest still exposes the campaign lineage.

## Recommendation

Phase 11 is ready to plan as a three-wave execution phase:

1. additive launch contract and deterministic overlay semantics
2. launch CLI plus `llm-generate` bridge
3. downstream lineage propagation and compatibility proof

The critical planning detail is to treat lane selection and prompt-action
resolution as first-class contract work, not as incidental CLI glue.
