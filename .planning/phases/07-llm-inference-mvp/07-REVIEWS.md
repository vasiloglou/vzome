---
phase: 7
requested_reviewers: [gemini, claude, codex]
completed_reviewers: [gemini, claude]
skipped_reviewers: [codex]
reviewed_at: 2026-04-03T22:20:19Z
plans_reviewed:
  - 07-01-PLAN.md
  - 07-02-PLAN.md
  - 07-03-PLAN.md
---

# Cross-AI Plan Review — Phase 7

`codex` was intentionally skipped for this review because the current runtime is
already Codex, and the review workflow prefers independent external feedback.

## Gemini Review

The proposed implementation plans for **Phase 7: LLM Inference MVP** are exceptionally well-structured, adhering strictly to the architectural constraints and research findings established in previous phases. The strategy of separating the provider-neutral runtime (07-01), the generation engine (07-02), and the benchmark harness (07-03) provides a low-risk, additive path for integrating LLM capabilities without compromising the stability of the existing no-DFT discovery pipeline.

### Strengths

*   **Dependency Discipline:** The plans avoid forcing vendor SDKs (like `anthropic` or `openai`) onto the base project by using lazy `httpx` imports and raw REST calls. This preserves the "mock-first" and "offline-capable" posture of the repository.
*   **Auditability & Provenance:** The decision to separate heavy run-level audit trails (prompts, raw completions, retries) from lightweight `CandidateRecord` provenance is an excellent architectural choice that prevents artifact bloat while ensuring every model decision is traceable.
*   **Code Reuse:** Refactoring `candidate_factory.py` to extract a shared candidate-building helper ensures that LLM-generated candidates are structurally identical to deterministic ones, making downstream comparison (`screen`, `validate`) seamless and reliable.
*   **Metric Granularity:** Extending the compiler seam to distinguish between parse failures and compile failures provides high-signal metrics (parse rate vs. compile rate) which are critical for evaluating LLM performance in a structured language like Zomic.
*   **Bounded Retry Logic:** The implementation of a simple, bounded retry loop without a complex (and potentially unstable) self-healing repair loop is appropriate for an MVP and aligns with the "config-driven" mandate.

### Concerns

*   **Anthropic Adapter Error Detail (LOW):** While the plan specifies raising a `RuntimeError` on non-2xx statuses, it should explicitly require capturing the response body or specific error code in the log/manifest to aid debugging of rate limits or safety filters.
*   **Benchmark Count Default (LOW):** The `run_llm_generate_benchmarks.sh` script should have a safe, low default count (e.g., 5 or 10) for mock-mode tests to ensure the "slower lane" tests remain reasonably fast in CI environments.
*   **SystemConfig Pollution (LOW):** Adding `llm_generate` to the top-level `SystemConfig` is necessary for the CLI, but care should be taken in `07-01` to ensure it remains optional (`| None = None`) so existing configs for other systems (like `Ti-Zr-Ni`) don't require updates.

### Suggestions

*   **Capture Model Usage:** In `AnthropicApiLlmAdapter`, consider extracting token usage headers (if available in the response) and recording them in the `LlmGenerationAttempt` model. This will be invaluable for cost-tracking and efficiency analysis in Phase 8.
*   **Seed-Zomic Validation:** In `Task 07-02-01`, ensure that if a `seed_zomic` path is provided but the file is unparseable, the engine fails early with a clear error before making any LLM calls.
*   **Schema versioning:** Explicitly version the new `LlmRunManifest` and `LlmGenerationAttempt` schemas in `llm/schema.py` to match the versioning pattern used in Phase 6 (`llm-corpus-example/v1`).

### Risk Assessment: LOW

The plans are low risk because they are strictly additive and rely on the same validation stack (`screen`) that has been hardened in Phases 1–5. By anchoring the benchmark to `Al-Cu-Fe` and `Sc-Zn` with mock fixtures, the implementation proves the architectural "plumbing" is correct before any dependency on live AI providers or expensive training is introduced. The clear separation of concerns ensures that a failure in the LLM runtime cannot "poison" the deterministic generation path.

---

## Claude Review

# Phase 7 Plan Review: LLM Inference MVP

## 07-01-PLAN: Runtime Contracts, Config Extensions, and Provider Seam

### Summary

A well-scoped foundation plan that lands typed contracts before any CLI wiring. The config split (provider selection in `BackendConfig`, generation behavior in `LlmGenerateConfig`) follows the established pattern cleanly. The decision to use raw `httpx` instead of the Anthropic SDK is the right call for dependency hygiene. The plan is low-risk and sets up everything the next two plans need.

### Strengths

- Clean separation of concerns: provider selection in `BackendConfig` vs generation behavior in `LlmGenerateConfig`
- Mock-mode auto-defaulting mirrors the existing ingest adapter pattern exactly — consistent with `BackendConfig.default_adapter`
- Explicit decision NOT to auto-default real-mode LLM fields prevents silent misconfiguration
- Lazy `httpx` import preserves the mock-only install path
- Run-level provenance models (`LlmGenerationAttempt`, `LlmRunManifest`) are typed upfront instead of being added retroactively
- The `fixture_outputs` field on `LlmGenerateConfig` gives mock adapters deterministic content without requiring filesystem fixtures

### Concerns

- **MEDIUM**: The `AnthropicApiLlmAdapter` reads `ANTHROPIC_API_KEY` from the environment but the plan doesn't specify whether this happens at adapter construction or at `generate()` call time. If at construction, a misconfigured real-mode config will fail at adapter resolution rather than at generation — which might be desirable but should be explicit.
- **MEDIUM**: `LlmGenerationAttempt.parse_status` and `compile_status` are typed as bare `str` rather than reusing the existing `ValidationStatus` literal from `llm/schema.py`. This creates a taxonomic drift risk where the corpus pipeline uses `"pending"/"passed"/"failed"` but the generation pipeline could use arbitrary strings.
- **LOW**: The plan adds `llm_generate: LlmGenerateConfig | None = None` to `SystemConfig` but doesn't specify what happens when `mdisc llm-generate` is called with a config that has `llm_generate: null`. Plan 02 presumably handles this, but the contract boundary should be documented in Plan 01.
- **LOW**: `LlmGenerationRequest.composition_bounds` uses `dict[str, dict[str, float]]` instead of reusing the existing `CompositionBound` model. This means the request model silently accepts invalid bounds (e.g., `min > max`) that `SystemConfig` would reject.

### Suggestions

- Reuse `ValidationStatus` literal for `parse_status`/`compile_status` on attempt and result models, or define a new `LlmValidationStatus` literal that includes the needed values
- Add a note that `LlmGenerateConfig` being `None` means the system isn't configured for LLM generation, and Plan 02 should raise a clear error in that case
- Consider making `LlmGenerationRequest.composition_bounds` use `dict[str, CompositionBound]` for consistency

### Risk Assessment: **LOW**

This is a contract-only plan with no CLI surface, no I/O, and focused tests. The worst outcome is a schema that needs minor adjustment in Plan 02. The dependency graph is clean.

---

## 07-02-PLAN: Core `llm-generate` Engine and CLI

### Summary

The most complex plan in the phase. It correctly identifies that candidate conversion should reuse the existing `candidate_factory.py` path rather than forking the schema. The retry loop design (no model-repair, preserve all attempts) matches the context decisions. The main risk is the `build_candidate_from_prototype_library` refactor — extracting a helper from `candidate_factory.py` touches a critical existing path and needs careful test coverage to avoid regressions.

### Strengths

- Reusing the existing candidate factory instead of inventing a parallel candidate schema is exactly right — this is the single most important design decision in the phase
- Run artifact layout (`prompt.json`, `attempts.jsonl`, `compile_results.jsonl`, `run_manifest.json`) is well-defined and separates heavy lineage from candidate output
- The `request_hash` for run directory naming prevents collisions while staying deterministic for the same inputs
- Bounded retry without model-repair is appropriately scoped for an MVP
- Example mock configs committed to the repo mean the path is exercisable without any external setup
- `RuntimeError` is explicitly caught alongside the standard error trio — needed because the compile bridge can throw it

### Concerns

- **HIGH**: The `build_candidate_from_prototype_library` refactor in `candidate_factory.py` is a load-bearing extraction from `_make_candidate`. The plan says "reuses the existing site/species assignment path" but `_make_candidate` currently does Z[phi] coordinate construction (`construct_site_qphi`), cell scaling (`cell_scale_multiplier`), and site position computation — none of which apply to an orbit-library-backed candidate. The extracted helper needs to load the template from the orbit library path and skip the Z[phi] geometry entirely, using only `site_positions_from_template`. This is a non-trivial divergence that the plan underspecifies.
- **MEDIUM**: The compiler extension ("distinguish `parse_status`, `compile_status`, `error_kind`") is vague. The current compiler treats all bridge failures as both parse and compile failures. The plan doesn't specify how to distinguish them without adding a Python-side parser, which it explicitly forbids. In practice, with the Java bridge as the only authority, all failures will still be `parse_status="failed", compile_status="failed"` unless the bridge's error messages are parsed for classification. This should be addressed or acknowledged.
- **MEDIUM**: The `fixture_outputs` in the mock configs need to be valid enough to pass through the compile bridge. But the compile bridge requires a Java runtime (`./gradlew :core:zomicExport`). If the tests monkeypatch the compiler, they won't catch real Zomic syntax issues. If they don't, they require Java — breaking the offline/deterministic test contract. The plan should specify the monkeypatching strategy explicitly.
- **LOW**: The plan says calibration goes to `data/calibration/{slug}_llm_generation_metrics.json` but doesn't specify whether the `llm_generation_metrics` helper or the CLI command is responsible for writing it. Convention from other stages is that the CLI writes it after calling the metrics helper.

### Suggestions

- Specify the exact contract for `build_candidate_from_prototype_library`: it should accept a `template_override_path` (the orbit library JSON), load it via `template_from_path`, and then follow the existing `_make_candidate` path from the template-loaded point onward. Make this explicit so the executor doesn't accidentally try to run Z[phi] geometry on LLM outputs.
- For the compiler taxonomy: acknowledge that the Java bridge is the only classifier, and that Phase 7 will classify based on error message patterns (e.g., "parse error" vs "compile error" substrings) or fall back to `error_kind="bridge_failure"` when the message is ambiguous. This sets honest expectations for the benchmark metrics.
- Specify that tests monkeypatch `compile_zomic_script` to return controlled pass/fail dicts, and that the mock adapter's fixture outputs are raw Zomic text strings (not files), since the adapter returns strings per the Plan 01 contract.

### Risk Assessment: **MEDIUM**

The candidate factory refactor and compiler taxonomy extension are the two riskiest items. Both touch existing code that other stages depend on. The refactor needs regression coverage beyond what the plan specifies (the existing `test_cli.py` generate tests should still pass after extraction). The compiler taxonomy needs honest scoping to avoid over-promising on parse-vs-compile differentiation.

---

## 07-03-PLAN: Offline Benchmark and Docs

### Summary

A well-bounded closure plan. The comparison helper is thin and metric-focused. The benchmark runner script reuses existing `mdisc` commands rather than inventing orchestration. The docs updates are appropriately scoped. The main risk is that the benchmark tests need to exercise the full `generate → screen` path for both lanes, which means they depend on every preceding plan working correctly — making them more integration-heavy than the plan's "offline fixture-backed" framing suggests.

### Strengths

- The comparison payload structure (`deterministic_generation`, `llm_generation`, `comparison` with deltas) is clean and immediately useful for operator judgment
- Reusing `mdisc` commands in the benchmark script instead of building orchestration follows the project convention from `run_reference_aware_benchmarks.sh`
- Dedicated `llm_lane` pytest marker keeps slower tests separable
- Docs updates hit all the right files: README, index, llm-integration, pipeline-stages
- The comparison includes screen pass-through, which is the most meaningful MVP metric (not just "did it parse")

### Concerns

- **MEDIUM**: The benchmark tests claim to "avoid live network access by using mock configs and monkeypatched runtime calls" but running `mdisc screen` on generated candidates requires the screening stage to work end-to-end. If the mock LLM generates fixture Zomic that compiles into orbit libraries with valid geometry, the screening stage should work. But if the mock fixtures produce degenerate geometry (all sites at the same position), screening will behave differently than real data. The plan should specify that mock fixture Zomic must produce at least minimally valid geometry for screening to be meaningful.
- **MEDIUM**: `conversion_rate_delta` is listed as a comparison metric but isn't defined in the `llm_generation_metrics` helper from Plan 02. The conversion rate would be `generated_count / attempt_count` for the LLM lane and `generated_count / requested_count` for the deterministic lane. These aren't directly comparable since the deterministic generator doesn't have "attempts." The plan should define this delta precisely.
- **LOW**: The benchmark runner script accepts `--systems` and `--count` but doesn't specify error handling if a system's config file is missing or if a stage fails mid-run. The existing `run_reference_aware_benchmarks.sh` pattern should guide this.
- **LOW**: The plan updates `pipeline-stages.md` to reflect the implemented `llm-generate` stage, but the current doc already has a "(Planned)" section for it. The update should replace "(Planned)" with the actual implemented contract rather than adding a second section.

### Suggestions

- Define `conversion_rate_delta` explicitly: for the LLM lane it's `compile_pass_count / attempt_count`; for the deterministic lane use `1.0` (since every requested candidate is generated). The delta is `llm_rate - deterministic_rate`.
- Specify that the mock fixture Zomic in the configs must produce orbit libraries with at least 2 distinct sites to make screening non-trivial.
- Add `set -euo pipefail` to the benchmark runner script (consistent with the existing `run_reference_aware_benchmarks.sh` pattern).

### Risk Assessment: **LOW-MEDIUM**

The plan is well-scoped but the benchmark tests are closer to integration tests than unit tests. If Plans 01 and 02 land cleanly, Plan 03 should be straightforward. The main risk is the mock fixture quality affecting benchmark meaningfulness.

---

## Cross-Plan Assessment

### Overall Phase Risk: **MEDIUM**

The three-plan decomposition is sound. The dependency chain (01 → 02 → 03) is correct and each plan has a clear deliverable boundary. The two highest risks are:

1. **Candidate factory refactor** (Plan 02): Extracting `build_candidate_from_prototype_library` from `_make_candidate` touches a critical shared path. The extraction needs to be clean and well-tested to avoid regressions in the existing `generate` command.

2. **Parse vs compile taxonomy** (Plan 02): The current Java bridge doesn't distinguish parse from compile failures. The plan promises separate metrics but doesn't specify how to achieve them. This needs honest scoping — either classify by error message pattern or acknowledge that both will be reported as the same failure type in the MVP.

### What's Missing

- **No explicit regression gate**: None of the plans specify running the full existing test suite (`uv run pytest`) as a gate before moving to the next plan. The validation strategy mentions it for "before final phase sign-off" but not between plans. Given that Plan 02 refactors `candidate_factory.py`, a full suite run after Plan 02 would catch regressions early.
- **No `__init__.py` update plan for Plan 02 modules**: Plan 01 explicitly updates `llm/__init__.py` for runtime exports, but Plan 02 adds `prompting.py`, `generate.py`, and `benchmark.py` (Plan 03) without specifying `__init__.py` updates. These modules need to be importable.
- **Progress.md updates**: All three plans list this as a must-have truth but none of the task actions explicitly include the update step. The executor needs to remember this.

### Verdict

The plans are ready for execution. The two medium-risk items (factory refactor, compiler taxonomy) should be addressed by the executor during implementation rather than requiring a planning revision. The phase scope is appropriate — it stays clearly within inference-only territory without leaking into Phase 8's evaluation work.

---

## Consensus Summary

Both reviewers see the phase as well-structured and appropriately additive, with
the main execution risk concentrated in Plan 02 rather than in the phase shape
itself. The shared message is that the runtime/config foundation looks sound,
but the candidate-conversion bridge, compile-failure taxonomy, and benchmark
fixture contracts should be made more explicit before or during execution.

### Agreed Strengths

- The phase decomposition is strong: runtime/contracts first, generation engine
  second, benchmark/docs last.
- Dependency hygiene is good: lazy `httpx`, no forced vendor SDK, and mock-first
  coverage preserve the repo’s offline-friendly posture.
- Provenance design is strong: heavy run-level lineage is kept separate from
  lightweight `CandidateRecord` outputs.
- Reusing the existing candidate pipeline is the right architectural direction,
  because it keeps downstream `screen` compatibility and avoids schema forks.

### Agreed Concerns

- Plan 02 is the highest-risk part of the phase, especially the
  `candidate_factory.py` extraction needed to turn validated Zomic outputs into
  standard candidates without regressing the existing deterministic generator.
- The phase should tighten contract details around LLM config optionality and
  related schema reuse so `llm-generate` fails clearly when the config is absent
  or malformed rather than drifting into ambiguous runtime behavior.
- The compile/parsing taxonomy needs more honest scoping. The Java bridge is the
  only validation authority today, so separate parse-vs-compile metrics need a
  clearly documented classification rule instead of an implied precise parser.
- The benchmark lane needs more explicit fixture and metric definitions so the
  mock-based comparison remains meaningful and stable in CI.

### Divergent Views

- Gemini rates the phase as overall low risk and focuses on polish items such as
  error detail, default benchmark counts, seed validation, and schema versioning.
- Claude rates the phase medium risk because the Plan 02 refactor touches
  load-bearing generation code and the parse/compile distinction is still
  underspecified.
- Gemini is comfortable treating the current plans as nearly execution-ready,
  while Claude argues for making the candidate-conversion contract and benchmark
  assumptions more explicit before implementation starts.
