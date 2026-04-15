---
phase: 07-llm-inference-mvp
plan: 01
subsystem: llm-runtime
tags: [pydantic, runtime, mock, anthropic, config]
requires:
  - phase: 06-zomic-training-corpus-pipeline
    provides: llm package surface, validation taxonomy, file-backed artifact conventions
provides:
  - additive llm-generate config contracts
  - typed generation request/attempt/result/run-manifest models
  - deterministic llm fixture adapter seam
  - first hosted provider adapter seam
affects: [phase-07, llm, cli-foundation, config]
tech-stack:
  added: [pydantic models, runtime adapter layer]
  patterns: [lazy optional imports, mock-first provider defaults, versioned llm schemas]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/runtime.py
    - materials-discovery/tests/test_llm_generate_schema.py
    - materials-discovery/tests/test_llm_runtime.py
  modified:
    - materials-discovery/src/materials_discovery/common/schema.py
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/developers-docs/configuration-reference.md
    - materials-discovery/Progress.md
key-decisions:
  - "Keep llm_generate optional on SystemConfig so legacy configs remain valid and llm execution can fail explicitly instead of forcing config churn."
  - "Reuse CompositionBound and ValidationStatus in Phase 7 to avoid taxonomy drift between the corpus and inference lanes."
  - "Use lazy httpx import plus raw REST for anthropic_api_v1 so the mock-only install path stays light."
patterns-established:
  - "Phase 7 runtime pattern: provider selection stays in BackendConfig while generation behavior lives in LlmGenerateConfig."
  - "Versioned llm runtime artifacts mirror the Phase 6 schema-version convention instead of using untyped dict payloads."
requirements-completed: [LLM-02]
duration: 25min
completed: 2026-04-03
---

# Phase 7: Plan 01 Summary

**Additive llm-generate contracts, versioned runtime models, and the first mock/hosted adapter seam**

## Performance

- **Duration:** 25 min
- **Completed:** 2026-04-03T22:55:00Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Extended `SystemConfig` and `BackendConfig` with the additive Phase 7 LLM surface without breaking existing configs.
- Added typed `LlmGenerationRequest`, `LlmGenerationAttempt`, `LlmGenerationResult`, and `LlmRunManifest` models with versioned schemas.
- Added `llm_fixture_v1` and `anthropic_api_v1` runtime adapters with lazy `httpx` loading and clearer hosted-provider failure detail.
- Added focused schema/runtime pytest coverage and documented the new `llm_generate:` config block.

## Task Commits

This plan was checkpointed as one combined commit for the schema/runtime batch.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/common/schema.py` - additive Phase 7 config and summary contracts
- `materials-discovery/src/materials_discovery/llm/schema.py` - typed request/attempt/result/run-manifest models
- `materials-discovery/src/materials_discovery/llm/runtime.py` - provider-neutral runtime seam with mock and Anthropic adapters
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Phase 7 exports
- `materials-discovery/developers-docs/configuration-reference.md` - `llm_generate` and backend `llm_*` docs
- `materials-discovery/tests/test_llm_generate_schema.py` - schema/config coverage
- `materials-discovery/tests/test_llm_runtime.py` - runtime adapter coverage
- `materials-discovery/Progress.md` - required materials-discovery progress log update

## Decisions Made

- Kept `llm_generate` optional and explicit, so `mdisc llm-generate` can reject unconfigured runs instead of silently inventing defaults in real mode.
- Reused the existing `ValidationStatus` and `CompositionBound` models to keep Phase 7 aligned with Phase 6 and the broader config contract.
- Delayed API-key validation until adapter `generate(...)` time, which makes adapter resolution deterministic for tests and clearer for CLI error handling later.

## Deviations from Plan

- No task-level commit split was used for Plan 01; the schema and runtime work were kept together because the runtime tests depend on the newly added typed models.

## Issues Encountered

- None. Both focused verification lanes passed on the first run.

## User Setup Required

- None for mock mode. Real-provider execution will require `ANTHROPIC_API_KEY` later in Phase 7, but this plan only adds the runtime seam and tests.

## Next Phase Readiness

Plan 02 can now build prompt assembly, attempt persistence, CLI wiring, and candidate conversion against a stable typed runtime surface.

---
*Phase: 07-llm-inference-mvp*
*Completed: 2026-04-03*
