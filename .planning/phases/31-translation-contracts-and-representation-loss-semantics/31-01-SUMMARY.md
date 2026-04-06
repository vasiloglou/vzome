---
phase: 31-translation-contracts-and-representation-loss-semantics
plan: 01
subsystem: llm
tags: [pydantic, translation, cif, crystaltextllm, schema]
requires: []
provides:
  - typed translated-structure artifact schema for external-format interoperability
  - export-facing fidelity tiers with explicit lossy reasons
  - built-in target registry and resolution helpers for CIF and material-string exporters
affects: [31-02-plan, 31-03-plan, 32-cif-and-material-string-exporters]
tech-stack:
  added: []
  patterns:
    - additive pydantic schema extension in materials_discovery.llm.schema
    - typed target discovery through list_translation_targets and resolve_translation_target
key-files:
  created: [materials-discovery/tests/test_llm_translation_schema.py]
  modified:
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Kept translation fidelity separate from corpus FidelityTier so lossy export semantics do not alter shipped LLM corpus workflows."
  - "Standardized translation loss-reason names and added requires_periodic_cell metadata so later exporters can classify representational loss explicitly."
  - "Exposed list_translation_targets() and resolve_translation_target() as the stable registry API for later translation phases."
patterns-established:
  - "Translation artifacts carry typed source linkage back to CandidateRecord provenance."
  - "Target selection is registry-backed and never inferred from ad hoc target-family strings."
requirements-completed: [LLM-27, LLM-30]
duration: 6min
completed: 2026-04-06
---

# Phase 31 Plan 01: Translation Contracts and Representation Loss Semantics Summary

**Translated-structure schema with explicit lossy export semantics and a built-in CIF/material-string target registry**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-06T23:35:00Z
- **Completed:** 2026-04-06T23:40:50Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added an additive translated-structure artifact contract with typed source linkage, typed target descriptors, diagnostics, and export-facing fidelity tiers.
- Preserved existing corpus fidelity behavior while introducing explicit `lossy` semantics and standardized loss-reason names for downstream export phases.
- Shipped a built-in CIF/material-string registry with stable list and resolve helpers so later phases can depend on explicit target semantics.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add a typed translated-structure artifact contract with export fidelity and source linkage** - `b818f5bc` (test, RED), `3ec8790d` (feat, GREEN)
2. **Task 2: Register supported target families for CIF and material-string workflows** - `9f57eefd` (test, RED), `915f3224` (feat, GREEN)

## Files Created/Modified

- `materials-discovery/tests/test_llm_translation_schema.py` - Focused schema and registry coverage for translation artifacts, additive fidelity separation, and target resolution failures.
- `materials-discovery/src/materials_discovery/llm/schema.py` - New translation contract models, standardized loss reasons, and the built-in target registry plus resolution helpers.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Public exports for the translation artifact contract and target registry API.
- `materials-discovery/Progress.md` - Required changelog and diary updates for every materials-discovery change made during the plan.

## Decisions Made

- Kept translation fidelity separate from the older corpus `FidelityTier` so export loss semantics stay additive and do not alter Phase 6-9 behavior.
- Added the missing-source-linkage rejection test and implemented typed source references instead of allowing loosely structured provenance.
- Standardized loss-reason naming and exposed `requires_periodic_cell` directly on target descriptors so later phases can classify periodic-proxy requirements without guesswork.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02 can now normalize `CandidateRecord` inputs into `TranslatedStructureArtifact` instances against a stable contract and use `resolve_translation_target()` for deterministic target semantics. No blockers remain from Plan 01.

## Self-Check

PASSED

- Summary file exists: `31-01-SUMMARY.md`
- Task commits verified: `b818f5bc`, `3ec8790d`, `9f57eefd`, `915f3224`
