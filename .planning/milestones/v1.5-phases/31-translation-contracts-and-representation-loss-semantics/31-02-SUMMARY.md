---
phase: 31-translation-contracts-and-representation-loss-semantics
plan: 02
subsystem: llm
tags: [translation, normalization, fidelity, pydantic, structure-realization]
requires:
  - phase: 31-01-plan
    provides: typed translated-structure artifact schema and target registry
provides:
  - deterministic candidate-to-translated-artifact normalization seam
  - explicit per-site coordinate-origin reporting reused from structure realization
  - conservative exact anchored approximate lossy translation-fidelity classification
affects: [31-03-plan, 32-cif-and-material-string-exporters]
tech-stack:
  added: []
  patterns:
    - translation normalization reuses additive structure-realization helpers instead of duplicating coordinate branching
    - translation fidelity is inferred conservatively from coordinate origin plus periodic-safe provenance hints
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/translation.py
    - materials-discovery/tests/test_llm_translation_core.py
  modified:
    - materials-discovery/src/materials_discovery/backends/structure_realization.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/tests/test_structure_realization.py
    - materials-discovery/Progress.md
key-decisions:
  - "Made coordinate origin explicit through a stable structure-realization helper rather than hiding branch logic inside the translation module."
  - "Reserved `exact` for candidates with strong periodic-safe evidence plus stored fractional coordinates; mixed-origin candidates stay conservative at `approximate`."
  - "QC-native periodic exports are marked `lossy` with explicit reasons instead of silently degrading to a weaker success state."
patterns-established:
  - "Translated artifacts keep site ordering identical to CandidateRecord site order for serializer stability."
  - "Loss semantics are recorded on the artifact while unsupported exactness requests fail fast through assess_translation_fidelity()."
requirements-completed: [LLM-27, LLM-30]
duration: 7min
completed: 2026-04-06
---

# Phase 31 Plan 02: Translation Contracts and Representation Loss Semantics Summary

**Deterministic translated-structure normalization with explicit coordinate origins and conservative exact-versus-lossy export semantics**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-06T23:47:00Z
- **Completed:** 2026-04-06T23:54:06Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added `llm/translation.py` with a deterministic normalization seam from `CandidateRecord` to `TranslatedStructureArtifact`.
- Extended structure realization with an explicit per-site coordinate-origin helper and reused it from the translation seam instead of duplicating coordinate branching.
- Implemented conservative fidelity classification so `exact`, `anchored`, `approximate`, and `lossy` remain deterministic and honest for periodic targets.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build a deterministic candidate-to-translated-artifact normalization seam** - `744871b7` (test, RED), `a5776c0f` (feat, GREEN)
2. **Task 2: Classify exact versus lossy downstream translation outcomes** - `9e9f7073` (test, RED), `16898a4e` (feat, GREEN)

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/translation.py` - New normalization and fidelity-classification core for translated artifacts.
- `materials-discovery/src/materials_discovery/backends/structure_realization.py` - Added explicit per-site fractional-position origin reporting.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Exported the translation-core API.
- `materials-discovery/tests/test_llm_translation_core.py` - Added normalization and fidelity regression coverage, including mixed-origin and QC-native cases.
- `materials-discovery/tests/test_structure_realization.py` - Locked the additive coordinate-origin helper behavior.
- `materials-discovery/Progress.md` - Logged both RED/GREEN task waves as required by repo policy.

## Decisions Made

- Used a stable helper in `structure_realization.py` for coordinate origins so later exporters can reuse the same source-of-position contract.
- Required strong periodic-safe evidence plus stored fractional coordinates for `exact`; cartesian-only periodic-safe candidates become `anchored`, mixed-origin candidates become `approximate`.
- Marked QC-native periodic targets `lossy` with explicit reasons (`aperiodic_to_periodic_proxy`, `coordinate_derivation_required`, `qc_semantics_dropped`) and rejected unsupported `exact` requests explicitly.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 03 can now freeze this contract with fixture-backed candidates and developer docs. Phase 32 has a stable normalized artifact shape, explicit coordinate-origin metadata, and deterministic fidelity semantics to serialize from.

## Self-Check

PASSED

- Summary file exists: `31-02-SUMMARY.md`
- Created files verified: `materials-discovery/src/materials_discovery/llm/translation.py`, `materials-discovery/tests/test_llm_translation_core.py`
- Task commits verified: `744871b7`, `a5776c0f`, `9e9f7073`, `16898a4e`
