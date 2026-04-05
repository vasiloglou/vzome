# Phase 19: Local Serving Runtime and Lane Contracts - Research

**Date:** 2026-04-05  
**Status:** Complete  
**Requirements:** `LLM-13`, `LLM-14`, `OPS-08`

## Goal

Turn the current hosted-plus-mock LLM seam into a lane-aware runtime that can
execute against operator-managed local OpenAI-compatible servers without
breaking the shipped `llm-generate`, `llm-launch`, and `llm-replay` workflow
contracts.

Phase 19 must:

- let operators target a configured local lane through the existing
  `mdisc llm-generate` command
- keep config authoritative for available `general_purpose` and
  `specialized_materials` lanes
- fail early with clear diagnostics when local/specialized runtime inputs are
  missing or unavailable
- record deterministic lane-selection provenance instead of silently
  downgrading to the baseline backend tuple

Phase 19 must not:

- launch or manage local model processes
- add in-process `transformers` inference
- assume off-the-shelf specialized materials models already produce good Zomic
- widen the workflow beyond the existing file-backed, operator-governed seams

## Current Surface

### The repo already has one generation engine and one launch wrapper

The current LLM flow is intentionally centralized:

- `materials-discovery/src/materials_discovery/llm/generate.py`
- `materials-discovery/src/materials_discovery/llm/runtime.py`
- `materials-discovery/src/materials_discovery/llm/launch.py`
- `materials-discovery/src/materials_discovery/llm/replay.py`

`generate_llm_candidates(...)` already owns:

- prompt assembly
- seed/example-pack loading
- adapter resolution
- compile + conversion
- run-level prompt / attempt / compile artifacts
- `CandidateRecord` output and additive run-manifest writing

That means Phase 19 should extend the existing generation runtime and launch
overlay behavior rather than create a second local-serving engine.

### The config surface is close, but not yet sufficient

Current config already includes:

- `backend.llm_adapter`
- `backend.llm_provider`
- `backend.llm_model`
- `backend.llm_api_base`
- `llm_generate.model_lanes`

But Phase 19 still lacks three things:

1. a local-serving adapter that can speak to an already-running
   OpenAI-compatible server
2. an explicit lane-selection surface for manual `llm-generate`
3. enough typed serving identity to distinguish lane, endpoint, checkpoint, and
   revision information cleanly in run and launch artifacts

### Launch and replay already depend on stable lane identity

Phase 11 and Phase 12 already introduced:

- `requested_model_lanes`
- `resolved_model_lane`
- `resolved_model_lane_source`
- campaign launch and replay artifacts

That existing surface is the right foundation, but it is still tuned for the
hosted/mock world. Phase 19 needs richer serving identity without breaking
older launch artifacts that may still carry the legacy
`resolved_model_lane_source: "baseline_fallback"` value.

## Key Design Findings

### 1. OpenAI-compatible local HTTP is the right first adapter

The lowest-blast-radius local-serving move is an additive runtime adapter that
keeps the same "prompt in, text out" contract as the hosted path. The cleanest
Phase 19 seam is:

- keep `llm-generate` as the single runtime
- add one real-mode adapter such as `openai_compat_v1`
- route it through `httpx` lazily, just like the existing Anthropic adapter

This fits:

- `vLLM`
- OpenAI-compatible Ollama gateways
- TGI or similar bridges that expose OpenAI-style endpoints
- later local or proxied specialized-materials servers

It also keeps Phase 19 honest about what the milestone is doing: transport and
lane contracts, not model lifecycle management.

### 2. Transport defaults should stay in backend config, while lanes stay in `llm_generate`

The current design decision from discussion is correct and still holds after
reading the code:

- `backend` should own transport defaults and shared runtime behavior
- `llm_generate.model_lanes` should own lane selection and lane-specific
  identity

Recommended additive config fields:

In `BackendConfig`:

- `llm_request_timeout_s: float`
- `llm_probe_timeout_s: float`
- `llm_probe_path: str | None`

In `LlmModelLaneConfig`:

- existing `adapter`, `provider`, `model`, `api_base`
- additive `checkpoint_id: str | None`
- additive `model_revision: str | None`
- additive `local_model_path: str | None`

In `LlmGenerateConfig`:

- `default_model_lane: Literal["general_purpose", "specialized_materials"] | None`
- `fallback_model_lane: Literal["general_purpose", "specialized_materials"] | None`

This keeps transport policy in one place while letting each lane declare the
identity that later phases will benchmark.

### 3. Manual `llm-generate` needs an explicit lane-selection surface

Right now lane selection only exists through campaign actions and launch
resolution. That is not enough for `LLM-13`, which is explicitly about an
operator running `mdisc llm-generate` against a configured local lane.

Recommended Phase 19 CLI addition:

- `mdisc llm-generate --model-lane general_purpose`
- `mdisc llm-generate --model-lane specialized_materials`

Resolution rules should be:

- if `--model-lane` is passed, require a configured lane or fail clearly
- if `--model-lane` is omitted and `default_model_lane` is configured, use it
- if neither is set, use the existing backend tuple as the `backend_default`
  path
- only use fallback when `fallback_model_lane` is explicitly configured

That gives manual generation the same determinism that campaign launch already
expects.

### 4. Local-serving diagnostics should happen before provider execution

Phase 19 explicitly does not manage local processes, so diagnostics have to
focus on readiness, not orchestration.

Recommended runtime behavior:

- validate required fields before adapter creation:
  - nonblank model
  - `api_base` available either from lane override or backend default
- run a cheap probe before candidate-generation attempts when the selected
  adapter is `openai_compat_v1`
- surface errors that mention:
  - requested lane
  - resolved lane
  - adapter name
  - endpoint / local path
  - whether fallback was attempted or disallowed

The important UX rule is: the failure should happen before operators think the
generation run "started successfully."

### 5. Serving identity needs richer provenance than the current run manifest

Current run artifacts record:

- adapter
- provider
- model
- requested/resolved lanes

For local and specialized serving, that is not enough. The minimum additive
identity Phase 19 should write is:

- requested lane
- resolved lane
- resolved-lane source
- adapter
- provider
- model
- `api_base` or effective local endpoint
- `checkpoint_id`
- `model_revision`
- `local_model_path`

The cleanest way to do this is a typed `LlmServingIdentity` model reused across:

- `LlmRunManifest`
- `LlmCampaignResolvedLaunch`
- `LlmCampaignLaunchSummary`

The existing flat fields can stay for backward compatibility while the new
typed identity becomes the richer contract for later phases.

### 6. Lane-selection provenance needs more precise values than Phase 11 used

The current launch artifacts use:

- `configured_lane`
- `baseline_fallback`

For Phase 19, that is too coarse. The repo now needs to distinguish:

- `configured_lane`
- `default_lane`
- `configured_fallback`
- `backend_default`

Important compatibility note:

- old artifacts that say `baseline_fallback` must still deserialize cleanly
- new Phase 19 writes should use the more explicit values above

That lets replay/comparison code stay backward-compatible while making new
local-serving behavior auditable.

### 7. Replay does not need full new behavior yet, but it must stay parse-safe

`LLM-16` is a Phase 20 requirement, not Phase 19. But Phase 19 still needs to
protect the strict replay workflow from breakage.

Minimum Phase 19 replay work:

- preserve new serving-identity fields in launch/replay artifacts
- rebuild replay config using recorded `api_base` or local path information
  when the current config remains compatible
- fail clearly when the recorded local-serving identity no longer matches the
  configured lane, rather than silently replaying against a different target

That is enough to keep Phase 19 additive while saving the full
local/specialized replay compatibility story for Phase 20.

### 8. Example local configs should ship in Phase 19

Operators and tests need committed examples, even if they use placeholder local
endpoints or monkeypatched HTTP in CI.

Recommended committed examples:

- `materials-discovery/configs/systems/al_cu_fe_llm_local.yaml`
- `materials-discovery/configs/systems/sc_zn_llm_local.yaml`

These configs should:

- assume the server is already running
- declare `model_lanes`
- show `default_model_lane` / `fallback_model_lane` explicitly where used
- include endpoint and optional checkpoint identity fields
- avoid any implication that the CLI is starting local servers

## Recommended Implementation Split

### Plan 01: local-serving contract foundation

Land the contract layer first:

- additive backend and lane config fields
- typed serving identity contract
- `openai_compat_v1` runtime adapter
- readiness probe and runtime diagnostics
- focused schema/runtime tests

This gives the later plans one stable place to read transport defaults and
identity fields from.

### Plan 02: lane-aware manual generation and launch integration

Once the contract exists:

- add `--model-lane` to `mdisc llm-generate`
- reuse shared lane-resolution helpers in manual generation and campaign launch
- enforce explicit fallback rules
- record rich serving identity in run and launch artifacts
- add CLI/core regression coverage for local lanes

This is where `LLM-13` and the operational part of `LLM-14` really become
real.

### Plan 03: replay-safe identity, example configs, and operator docs

After the runtime and CLI path exist:

- make replay parse-safe with the new identity fields
- add committed local example configs
- update docs for setup assumptions, lane selection, and failure posture
- prove backward compatibility for the existing mock/hosted path

That keeps Phase 19 focused on contracts and diagnostics without prematurely
claiming full specialized-lane workflow compatibility.

## Risks and Edge Cases To Lock In Planning

### Silent fallback would destroy milestone credibility

If a requested local or specialized lane silently runs against the baseline
hosted tuple, operators will think they tested the new lane when they did not.
Phase 19 must require explicit fallback configuration and record when it was
used.

### Historical artifacts still use the old lane-source vocabulary

Archived v1.1 launch/replay artifacts may still contain
`baseline_fallback`. New validators and loaders must accept that historical
value even if Phase 19 writes the new explicit source labels.

### Readiness checks must stay offline-testable

The repo test suite cannot depend on a real local model server. Any local
runtime and CLI tests need monkeypatched `httpx` or fixture responses so the
validation surface stays deterministic.

### Specialized-materials lanes must stay honest about role

Phase 19 should not imply that every specialized lane is immediately suitable
for direct Zomic generation. The contract should support those lanes without
overselling their current task fit.

## Validation Architecture

Recommended focused verification slices:

- `cd materials-discovery && uv run pytest tests/test_llm_runtime.py tests/test_llm_launch_schema.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_core.py tests/test_llm_launch_cli.py tests/test_cli.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_runtime.py -x -v`
- `cd materials-discovery && uv run pytest`

Wave-0 expectations:

- all local-serving tests stay offline via monkeypatched HTTP responses
- any new config examples validate through `SystemConfig` without requiring a
  live server
- existing mock and hosted tests stay green after lane/source changes
- any execution touching `materials-discovery/` must update
  `materials-discovery/Progress.md` per repo policy

The important Nyquist point for Phase 19 is not raw test count. It is that the
phase proves:

1. local runtime contract correctness
2. operator-visible early failure behavior
3. no regression to the current hosted/manual path

## Recommended Planning Posture

Plan conservatively around the existing runtime seam and campaign wrapper. The
phase should make local-serving lanes first-class, but it should do that by
deepening the current contract, not by introducing a second inference stack or
operator flow.
