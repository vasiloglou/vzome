---
phase: 35-external-target-registration-and-reproducible-execution
plan: 01
subsystem: llm
tags: [external-targets, registration, pydantic, storage, llm]
requires:
  - phase: 34-benchmark-pack-and-freeze-contract
    provides: frozen translated benchmark-pack contract and artifact-boundary precedent
provides:
  - typed external-target registration, environment, and smoke contracts
  - deterministic llm_external_models artifact paths
  - focused schema and storage regression coverage for external benchmark targets
affects: [35-02-plan, 35-03-plan, 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards]
tech-stack:
  added: []
  patterns:
    - external target registration mirrors checkpoint-registration discipline without adding lifecycle state
    - external-target artifacts live under a dedicated llm_external_models root with deterministic registration, environment, and smoke filenames
key-files:
  created:
    - materials-discovery/tests/test_llm_external_target_schema.py
  modified:
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/storage.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "External benchmark targets keep immutable registration facts separate from later mutable smoke or environment observations."
  - "External target artifacts use a dedicated data/llm_external_models/{model_id}/ root to avoid overloading checkpoint or benchmark directories."
patterns-established:
  - "External target contracts reuse translation target-family enums and repo-style path normalization instead of inventing a second compatibility vocabulary."
  - "External target storage uses registration.json, environment.json, and smoke_check.json as the fixed Phase 35 artifact set."
requirements-completed: [OPS-17]
duration: 5 min
completed: 2026-04-07
---

# Phase 35 Plan 01: External Target Contract Summary

**Typed external-target registration models and deterministic `llm_external_models` storage paths for immutable benchmark targets**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-07T07:00:00Z
- **Completed:** 2026-04-07T07:04:29Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added a typed external-target registration contract with explicit model identity, supported translation families, runner choice, prompt or parser hooks, and immutable fingerprint metadata.
- Added typed environment-manifest and smoke-check models so reproducibility and readiness can be persisted as first-class files instead of CLI-only text.
- Added deterministic external-target storage helpers under `data/llm_external_models/{model_id}/` and locked the contract or storage surface with focused pytest coverage.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define the immutable external-target registration and reproducibility contract** - `1ce62e48` (feat)
2. **Task 2: Add deterministic storage helpers for external-target artifacts** - `4078d074` (feat)

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/schema.py` - Added external-target spec, registration, environment, smoke, and summary models.
- `materials-discovery/src/materials_discovery/llm/storage.py` - Added deterministic `llm_external_models` path helpers for registration and reproducibility artifacts.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Re-exported the new external-target contract models and storage helpers.
- `materials-discovery/tests/test_llm_external_target_schema.py` - Locked schema and storage behavior for the new external-target surface.
- `materials-discovery/Progress.md` - Logged both Phase 35 Plan 01 implementation slices as required by repo policy.

## Decisions Made

- Kept the Phase 35 contract additive to checkpoint registration by mirroring immutable registration facts without introducing lifecycle promotion state.
- Stored environment and smoke artifacts as separate typed files so later CLI inspect flows can distinguish immutable target identity from mutable runtime observations.
- Reserved a dedicated `llm_external_models` artifact family so later registration, smoke, and comparative benchmark phases can rely on one stable filesystem contract.

## Deviations from Plan

None.

## Issues Encountered

None.

## User Setup Required

None for Plan 01. This slice is schema and storage only.

## Next Phase Readiness

Plan 02 can now implement the registration core, environment capture, and smoke persistence directly against a stable contract and deterministic artifact layout. The remaining Phase 35 work can build CLI and docs behavior on top of explicit target identity, typed reproducibility artifacts, and fixed storage paths.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/35-external-target-registration-and-reproducible-execution/35-01-SUMMARY.md`
- Key files verified: `materials-discovery/tests/test_llm_external_target_schema.py`, `materials-discovery/src/materials_discovery/llm/schema.py`, `materials-discovery/src/materials_discovery/llm/storage.py`
- Task commits verified: `1ce62e48`, `4078d074`
