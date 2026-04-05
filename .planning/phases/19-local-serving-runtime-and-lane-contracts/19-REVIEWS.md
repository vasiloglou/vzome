---
phase: 19
reviewers: [gemini, claude]
reviewed_at: 2026-04-05T03:01:27.497Z
plans_reviewed:
  - 19-01-PLAN.md
  - 19-02-PLAN.md
  - 19-03-PLAN.md
---

# Cross-AI Plan Review — Phase 19

## Gemini Review

The following review assesses the three-track implementation plan for **Phase 19: Local Serving Runtime and Lane Contracts**.

### 1. Summary
The plan is a high-quality, architecturally sound extension of the existing LLM subsystem. It successfully pivots from a hardcoded "hosted-vs-mock" model to a flexible "lane-aware" system while maintaining strict backward compatibility. By prioritizing the OpenAI-compatible HTTP contract and a "fail-fast" diagnostic posture, the plan addresses the operational risks of local serving without introducing the complexity of process management or in-process inference. The transition from a single `baseline_fallback` to a more granular set of resolution sources (`configured_lane`, `default_lane`, `configured_fallback`, `backend_default`) is a particularly strong design choice that ensures transparency in the generation lineage.

### 2. Strengths
- **Deterministic Lane Resolution**: The introduction of `resolve_serving_lane` as a shared utility for both manual and campaign generation ensures that the logic remains consistent across the entire workflow.
- **Fail-Fast Diagnostics**: The inclusion of `validate_llm_adapter_ready` in Plan 01/02 addresses `OPS-08` directly by checking connectivity before expensive or multi-attempt generation loops begin.
- **Rich Serving Identity**: The `LlmServingIdentity` model correctly identifies that model name alone is insufficient for local serving; tracking `api_base`, `checkpoint_id`, and `model_revision` is critical for the comparative benchmarking goals of Phase 21.
- **Preservation of Governance**: The plan respects the "Operator-in-the-loop" mandate by requiring explicit fallback configuration rather than defaulting to silent hosted downgrades.
- **Backward Compatibility**: The specific task to handle legacy `baseline_fallback` values in schema deserialization (Plan 01, Task 1) prevents breaking existing campaign archives.

### 3. Concerns
- **Replay Drift Logic (Plan 03, Task 1)**:
  - **Risk**: MEDIUM.
  - **Detail**: Local endpoints (URLs) are more transient than hosted model names. If an operator restarts a local server on a different port, a strict identity match might block a valid replay.
  - **Suggestion**: Ensure the error message specifically distinguishes between a "Model/Checkpoint Mismatch" (fatal) and a "Transport/Endpoint Mismatch" (which might be resolvable via config update).
- **Dependency on `httpx`**:
  - **Risk**: LOW.
  - **Detail**: Plan 01 mentions lazy loading `httpx`.
  - **Suggestion**: Ensure `httpx` is added to the project's optional dependencies (e.g., in `pyproject.toml`) if it wasn't already a core requirement, or verify that the "local serving" requirement implies its presence.
- **Manual Generation Parameterization (Plan 02, Task 2)**:
  - **Risk**: LOW.
  - **Detail**: The CLI addition of `--model-lane` is good, but does not explicitly mention if it overrides or respects the `default_model_lane` in the config.
  - **Suggestion**: The implementation should follow the hierarchy: `CLI Flag > Config Default > Backend Baseline`.

### 4. Suggestions
- **Normalization of `api_base`**: In Plan 01, Task 1, ensure that trailing slashes are consistently stripped or handled in the `BackendConfig` validator to prevent malformed URLs in the `httpx` calls later.
- **Diagnostic Verbosity**: When `validate_llm_adapter_ready` fails, include a suggestion in the error message (e.g., "Check if vLLM/Ollama is running at [endpoint]").
- **Test Fixtures**: For Plan 02, ensure that the `materials-discovery/tests/` suite includes a "Local Mock" system config that specifically exercises the `openai_compat_v1` adapter with a monkeypatched response to prove the lane-resolution logic works end-to-end in CI.

### 5. Risk Assessment
**Overall Risk: LOW**

The plan is inherently low-risk because it is **additive**. By not attempting to manage local processes (D-08) or support complex `transformers` pipelines (D-03), it keeps the blast radius confined to the runtime/adapter layer. The strongest protection against risk is the decision to record the "resolved lane source," which makes it impossible to mistake a hosted fallback for a successful local run.

| Risk Category | Level | Justification |
|--- |--- |--- |
| **Architectural** | Low | Extends existing `LlmAdapter` and `SystemConfig` patterns. |
| **Operational** | Low | Assume server is running; focuses on clear error reporting. |
| **Data Integrity** | Low | Richer lineage fields improve auditability without breaking old data. |
| **Schedule** | Low | Clear task split; dependencies are logical. |

**Verdict**: Approved for execution. Proceed with Plan 01.

---

## Claude Review

# Phase 19 Plan Review: Local Serving Runtime and Lane Contracts

## Overall Assessment

These three plans form a well-structured, low-risk implementation of local OpenAI-compatible serving into an already mature LLM pipeline. The wave-based decomposition (contract first, then integration, then replay/docs) is the right ordering. The plans demonstrate strong awareness of the existing codebase contracts and backward-compatibility constraints. My concerns are minor and mostly about execution-time edge cases rather than architectural flaws.

---

## Plan 19-01: Local-Serving Contract Foundation

### Summary

Solid foundation plan. Lands schema extensions, a typed `LlmServingIdentity` model, the `openai_compat_v1` adapter, and readiness diagnostics before anything else touches the CLI or launch path. This is exactly the right first cut — it gives Plans 02 and 03 a stable contract to build on.

### Strengths

- **Clean separation of transport vs lane config.** Keeping timeouts in `BackendConfig` and lane identity in `LlmModelLaneConfig` avoids a config-shape mess that would haunt Phase 20+.
- **Backward-compatible lane-source expansion.** The explicit plan to accept legacy `baseline_fallback` while writing more precise values (`configured_lane`, `default_lane`, `configured_fallback`, `backend_default`) is exactly right for a system with archived v1.1 artifacts.
- **Lazy httpx import.** Matching the existing Anthropic adapter pattern keeps the dependency footprint clean for mock-mode users.
- **Readiness probe as a separate helper.** `validate_llm_adapter_ready(...)` being callable before generation means the CLI can fail fast without coupling diagnostics to the adapter's `generate()` method.

### Concerns

| # | Concern | Severity |
|---|---------|----------|
| 1 | **`LlmServingIdentity` threading into existing models may break serialization.** Adding an optional nested model to `LlmRunManifest`, `LlmCampaignResolvedLaunch`, and `LlmCampaignLaunchSummary` is additive, but if any downstream code does `model_dump(exclude_none=True)` and then re-validates, the missing nested object could cause Pydantic surprises. The plan should explicitly state whether `serving_identity` is `LlmServingIdentity \| None = None` or always populated. | MEDIUM |
| 2 | **Probe path default is unspecified.** The plan says `llm_probe_path: str \| None = None` but doesn't specify what the adapter does when `probe_path` is None. Does it skip probing? Use a sensible default like `/v1/models`? The readiness helper's behavior with no configured probe path should be explicit. | MEDIUM |
| 3 | **No mention of response-format validation for OpenAI-compat.** Different local servers (vLLM, Ollama, TGI) have subtle response-shape differences (e.g., `choices[0].message.content` vs `choices[0].text`). The plan should note which response shape the adapter expects and how it handles deviations. | LOW |
| 4 | **`llm_request_timeout_s` default of 30s may be too short for local LLM inference.** Local 7B models on CPU can take 60-120s for 2048 tokens. The default should be documented as tunable, or set higher (e.g., 120s). | LOW |

### Suggestions

1. Make `serving_identity` explicitly optional (`None`) on artifact models so old artifacts deserialize cleanly. New writes should always populate it.
2. Define the no-probe-path behavior: either skip the probe (just validate config fields) or default to `GET /v1/models` which is the most universal OpenAI-compat health check.
3. Add a brief comment in the adapter about which OpenAI response shape is expected (`choices[0].message.content`), since this is the contract local servers must honor.

---

## Plan 19-02: Lane-Aware Manual Generation and Launch Integration

### Summary

This is the operational core of Phase 19 — where `LLM-13` and `LLM-14` become real. The plan correctly identifies that a single shared `resolve_serving_lane(...)` helper should serve both manual generation and campaign launch, avoiding the duplication trap that the existing `resolve_campaign_model_lane()` already risks.

### Strengths

- **Single resolution path.** Having one `resolve_serving_lane(...)` used by both manual `llm-generate` and `llm-launch` is the most important architectural decision in this phase. It prevents lane-selection drift between manual and campaign paths.
- **Explicit fallback-only-when-configured semantics.** This directly addresses the "silent fallback destroys milestone credibility" risk from the research doc.
- **`backend_default` as the no-config path.** Preserving the existing backend tuple when nothing is configured keeps all current tests green without special-casing.
- **Readiness check before generation.** The CLI wiring validates local-lane readiness before `generate_llm_candidates()` starts, so operators don't see a half-started run directory before the error.

### Concerns

| # | Concern | Severity |
|---|---------|----------|
| 1 | **`resolve_serving_lane(...)` signature is underspecified.** The plan describes semantics well but doesn't clarify inputs. It needs at minimum: `requested_lane`, `config.llm_generate` (for `model_lanes`, `default_model_lane`, `fallback_model_lane`), and `config.backend` (for the baseline tuple). Making this explicit prevents the implementer from accidentally coupling it to campaign-specific state. | MEDIUM |
| 2 | **`generate_llm_candidates()` signature change needs care.** The plan says it "accepts additive lane-selection input" but the current signature already has 8 positional/keyword args plus `campaign_metadata`. Adding more kwargs risks a cluttered interface. Consider whether lane-selection should be bundled into a small dataclass or passed via `campaign_metadata` for both manual and campaign paths. | MEDIUM |
| 3 | **Interaction between `resolve_serving_lane` and existing `resolve_campaign_model_lane`.** The plan says launch should "reuse the same helper" but the existing `resolve_campaign_model_lane()` in `launch.py` has campaign-specific logic (action priority ordering, preferred lanes from actions). The plan should clarify whether `resolve_campaign_model_lane` is refactored to call `resolve_serving_lane` internally, or replaced entirely. Replacing it risks breaking campaign-action priority semantics. | MEDIUM |
| 4 | **Run manifest backward compatibility.** The plan adds `LlmServingIdentity` to run manifests but doesn't specify whether the existing flat fields (`adapter_key`, `provider`, `model`) are kept alongside or replaced. They should be kept (duplication is fine for backward compat) with the new identity as an additive nested field. | LOW |

### Suggestions

1. Define `resolve_serving_lane` as accepting a simple input struct: `(requested_lane: str | None, llm_generate_config: LlmGenerateConfig, backend_config: BackendConfig)` returning `(resolved_lane: str | None, lane_config: LlmModelLaneConfig | None, lane_source: str)`.
2. Have `resolve_campaign_model_lane` call `resolve_serving_lane` after it extracts the campaign's preferred lane from actions, rather than replacing the campaign-specific logic.
3. Keep the existing flat manifest fields and add `serving_identity` as a parallel nested field.

---

## Plan 19-03: Replay Safety, Example Configs, and Docs

### Summary

Good closing plan. It correctly scopes replay work to "parse-safe, not full parity" (which is Phase 20's job), ships committed example configs as both operator references and test fixtures, and updates docs to reflect the real Phase 19 boundary. The plan is appropriately conservative about what replay promises in this phase.

### Strengths

- **Replay scope is exactly right.** Only making the new identity fields non-breaking in replay, without promising full local-lane replay, avoids over-promising while keeping Phase 20 clean.
- **Committed configs double as test fixtures.** Having `al_cu_fe_llm_local.yaml` and `sc_zn_llm_local.yaml` in the repo means schema validation tests can load them without synthetic config construction.
- **Docs explicitly call out what Phase 19 does NOT do.** Saying "the local server must already be running" and "specialized lanes are not assumed Zomic-native" prevents operator confusion.
- **Backward-compat regression as an explicit test.** The focused test proving old configs without lanes still work is the cheapest insurance against a regression that would block all existing users.

### Concerns

| # | Concern | Severity |
|---|---------|----------|
| 1 | **Example configs reference placeholder endpoints.** The plan says configs should "assume the server is already running" but doesn't specify what placeholder endpoint to use. Using `http://localhost:8000` is fine for examples, but the tests should monkeypatch rather than attempt connection. This is likely handled, but should be explicit. | LOW |
| 2 | **Replay drift detection granularity.** The plan says "fail clearly when the recorded local-serving identity no longer matches the configured local lane." The definition of "match" matters: does endpoint URL change count? What about checkpoint_id changing? Model revision? The plan should specify which identity fields are match-critical for replay and which are informational. | MEDIUM |
| 3 | **Doc update scope.** Three docs are updated (`configuration-reference.md`, `llm-integration.md`, `pipeline-stages.md`). The plan should confirm these are additive sections only, not rewrites, to keep the diff reviewable. (The must_haves imply this but don't enforce it explicitly in the action.) | LOW |
| 4 | **Missing: `read_first` references `al_cu_fe_llm_mock.yaml` and `sc_zn_llm_mock.yaml`.** These files may not exist yet (they aren't in the current config listing). If they don't exist, the implementer needs guidance on what to base the local configs on — probably the base `al_cu_fe.yaml` and `sc_zn.yaml`. | LOW |

### Suggestions

1. Specify replay match semantics: adapter + provider + model must match (hard fail); endpoint/checkpoint/revision are informational warnings logged but not blocking in Phase 19 (Phase 20 can tighten this).
2. Confirm example config base: if `*_llm_mock.yaml` doesn't exist, derive local configs from the base mock configs plus `llm_generate` + `model_lanes` blocks.

---

## Cross-Plan Concerns

| # | Concern | Severity |
|---|---------|----------|
| 1 | **No plan explicitly covers `llm/__init__.py` exports in detail.** All three plans list it in `files_modified` but none specify which new symbols to export. This is trivial but could cause import errors if the executor forgets. | LOW |
| 2 | **Test file explosion.** Plans 01-03 touch 8+ test files. The test structure is already well-established, but the plans should note that new test functions should follow existing naming conventions in each file to keep the suite navigable. | LOW |
| 3 | **No explicit full-suite green gate between waves.** The validation strategy says "full suite must be green before verify-work" but doesn't mandate a full-suite run between Plan 01 and Plan 02. Given that Plan 01 changes schemas that Plan 02 depends on, a full-suite gate after Plan 01 would catch unexpected breakage early. | MEDIUM |

---

## Risk Assessment

**Overall Risk: LOW**

Justification:
- The phase is genuinely additive — no existing behavior is removed or replaced.
- The implementation split follows the natural dependency order (contract -> integration -> cleanup).
- The codebase already has the right seams (`runtime.py`, `launch.py`, `schema.py`) for these changes.
- The backward-compatibility story is well-thought-out (legacy `baseline_fallback` acceptance, flat fields alongside new identity).
- Test coverage is planned per-task with focused verification commands.

The main execution risk is not architectural but operational: the `resolve_serving_lane` helper needs a clean interface that both manual generation and campaign launch can call without leaking campaign-specific concerns into the shared path. If that boundary is drawn well, the rest follows naturally.

---

## Consensus Summary

Both reviewers rate Phase 19 as low risk overall and agree that the plan set is
well ordered: contract first, integration second, replay/docs last. The shared
view is that the milestone is being approached in the right additive way, with
strong backward-compatibility instincts and the right fail-fast operator
posture.

### Agreed Strengths

- The wave split is strong and matches the actual dependency order of the codebase.
- A shared lane-resolution helper is the right architectural center for manual generation and campaign launch.
- Explicit fallback-only-when-configured behavior is a strong safeguard against misleading operators.
- Richer serving identity is necessary and appropriately recognized as a first-class requirement rather than an afterthought.
- Backward compatibility for legacy `baseline_fallback` artifacts is correctly treated as mandatory.

### Agreed Concerns

- **Shared lane-resolution contract needs to be tighter.**
  Both reviews want the interface and ownership boundary around
  `resolve_serving_lane(...)` to be more explicit, especially how it relates to
  the existing `resolve_campaign_model_lane(...)` logic.
- **Replay identity matching needs more precise semantics.**
  Both reviews flagged that "identity drift" is too broad as written. The plan
  should say which fields are hard-fail replay requirements and which are more
  transport-level or informational drift.
- **The local readiness-probe contract is underspecified.**
  Both reviews want the plan to say what happens when no explicit probe path is
  configured and to be clear about the expected OpenAI-compatible response
  shape.

### Divergent Views

- Gemini leans toward distinguishing transport drift from model/checkpoint drift
  so operators can resolve benign endpoint changes without confusion.
- Claude pushes harder on serialization and function-shape clarity, especially
  whether `serving_identity` is optional and whether `generate_llm_candidates()`
  should take more kwargs or a more structured input.
- Claude also uniquely flagged the value of a full-suite gate between early and
  later waves; Gemini was more comfortable with the focused verification slices.

### Notes

- `codex` was intentionally skipped as a reviewer because the current runtime is
  already Codex and the goal here is independent external feedback.
- `claude` initially rejected `--no-input`, so the review was retried with plain
  `claude -p`.
- `gemini` logged quota-retry messages to stderr but still returned a usable
  review body.
