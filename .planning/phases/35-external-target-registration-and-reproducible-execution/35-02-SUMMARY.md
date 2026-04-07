---
phase: 35-external-target-registration-and-reproducible-execution
plan: 02
subsystem: llm
tags: [external-targets, registration, smoke, reproducibility, llm]
requires:
  - phase: 35-external-target-registration-and-reproducible-execution
    provides: typed external-target contracts and deterministic llm_external_models storage
provides:
  - immutable external-target registration with conflict-detecting fingerprints
  - persisted environment lineage and typed smoke artifacts for registered benchmark targets
  - focused regression coverage for registration reload, environment capture, and smoke persistence
affects: [35-03-plan, 35-phase-verification, 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards]
tech-stack:
  added: []
  patterns:
    - external-target registration normalizes spec-relative paths into stable repo-relative artifact references before persistence
    - smoke readiness for external targets is expressed as typed persisted artifacts rather than transient CLI output
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/external_targets.py
    - materials-discovery/tests/test_llm_external_target_registry.py
  modified:
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Registration fingerprints are derived from immutable target facts only so operators can re-run registration idempotently without silent drift."
  - "Environment capture and smoke checks fail closed on missing snapshot lineage, but still persist a typed smoke artifact for later inspection."
patterns-established:
  - "External target runtime lineage is stored alongside the registration contract under one deterministic llm_external_models artifact root."
  - "Heavy runtime dependencies stay isolated behind smoke helpers so registry tests remain fast and monkeypatchable."
requirements-completed: [OPS-17]
duration: 12 min
completed: 2026-04-07
---

# Phase 35 Plan 02: External Target Registry Summary

**Immutable external-target registration, reproducibility lineage capture, and typed smoke persistence for curated benchmark models**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-07T06:59:00Z
- **Completed:** 2026-04-07T07:11:25Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added a dedicated `llm/external_targets.py` module that loads typed specs, normalizes snapshot paths, fingerprints immutable target facts, persists `registration.json`, and rejects conflicting reuse of a `model_id`.
- Added reproducibility lineage capture that writes `environment.json` with Python, platform, optional CUDA visibility, package versions, and snapshot-linked registration metadata.
- Added typed smoke persistence that writes `smoke_check.json` for both passing and fail-closed cases, then locked the entire registration surface with focused tmp-path pytest coverage.

## Task Commits

Implementation was completed in one atomic feature commit because Task 2 extends the same registry module introduced in Task 1:

1. **Tasks 1-2: External-target registration core plus environment and smoke persistence** - `88690ed8` (feat)

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/external_targets.py` - Added spec loading, immutable registration, reproducibility capture, and smoke persistence helpers for external benchmark targets.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Re-exported the new registration, environment, and smoke helpers from the public `materials_discovery.llm` API.
- `materials-discovery/tests/test_llm_external_target_registry.py` - Added focused regression coverage for registration normalization, fingerprint conflicts, environment capture, reload, and smoke pass/fail persistence.
- `materials-discovery/Progress.md` - Logged both Plan 35-02 implementation slices as required by repo policy.

## Decisions Made

- Kept registration additive to the checkpoint machinery by persisting immutable benchmark-target facts without introducing promotion or lifecycle state.
- Normalized snapshot and manifest paths relative to the repo root when possible so later CLI and benchmark consumers resolve one stable artifact contract.
- Captured environment and smoke results as typed files even on failures so later inspection surfaces can distinguish registry drift from runtime readiness problems.

## Deviations from Plan

None.

## Issues Encountered

None.

## User Setup Required

None for Plan 02. This slice is registry, reproducibility, and smoke persistence only.

## Next Phase Readiness

Plan 03 can now build CLI registration and inspection flows directly on top of stable `registration.json`, `environment.json`, and `smoke_check.json` artifacts. Phase verification can also assert immutable target identity and fail-closed smoke posture without depending on raw dicts or ad hoc filesystem assumptions.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/35-external-target-registration-and-reproducible-execution/35-02-SUMMARY.md`
- Key files verified: `materials-discovery/src/materials_discovery/llm/external_targets.py`, `materials-discovery/tests/test_llm_external_target_registry.py`
- Verification passed: `uv run pytest tests/test_llm_external_target_schema.py tests/test_llm_external_target_registry.py -x -v`
- Implementation commit verified: `88690ed8`
