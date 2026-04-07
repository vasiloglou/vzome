---
phase: 32-cif-and-material-string-exporters
plan: 01
subsystem: api
tags: [translation, cif, serializer, pydantic, pytest]
requires:
  - phase: 31-translation-contracts-and-representation-loss-semantics
    provides: typed translated structure artifacts, target registry, and fidelity/loss semantics
provides:
  - shared translation export validation and dispatch seam
  - deterministic CIF serializer for translated artifacts
  - focused export and CIF regression coverage
affects: [32-02, 32-03, 33]
tech-stack:
  added: []
  patterns:
    - artifact-first export dispatch over TranslatedStructureArtifact
    - deterministic pure-text CIF emission with explicit fidelity metadata
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/translation_export.py
    - materials-discovery/tests/test_llm_translation_export.py
    - materials-discovery/tests/test_llm_translation_cif.py
  modified:
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Kept export validation centralized in translation_export.py so later target families reuse one readiness gate and one copy-not-mutate dispatch path."
  - "Emitted CIF as a narrow deterministic text serializer with a metadata comment preamble so lossy periodic-proxy exports stay visibly labeled."
patterns-established:
  - "Validate translated artifacts before target-family dispatch so CIF and later material-string exports share the same export-readiness contract."
  - "Preserve translated site ordering exactly in emitted payloads and test parser compatibility against repo-local CIF tooling."
requirements-completed: [LLM-28, LLM-29]
duration: 6 min
completed: 2026-04-06
---

# Phase 32 Plan 01: Shared Export Seam and CIF Serializer Summary

**Shared translated-structure export seam with deterministic CIF emission, parser-compatible atom loops, and explicit lossy periodic-proxy metadata**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-06T23:02:17-04:00
- **Completed:** 2026-04-06T23:08:50-04:00
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added `translation_export.py` with export-readiness validation, deterministic float formatting, copy-not-mutate dispatch, and the Phase 32 public export seam.
- Implemented deterministic CIF serialization with a fixed metadata preamble, fixed cell-field order, fixed atom-site headers, preserved site ordering, and repo-local parser compatibility.
- Locked the new behavior with focused RED/green coverage for export validation, CIF layout, parser recovery after comment stripping, and explicit lossy QC-native metadata.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add shared export validation and deterministic formatting helpers** - `4016e05` (test), `5bc2a5d` (feat)
2. **Task 2: Emit deterministic CIF text from translated artifacts** - `1a6021c` (test), `1437d8b` (feat)

_Note: TDD tasks used RED then implementation commits._

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/translation_export.py` - Defines export validation, shared dispatch, float formatting, CIF emission, and supporting helpers.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Re-exports the new Phase 32 export helpers from the public `materials_discovery.llm` surface.
- `materials-discovery/tests/test_llm_translation_export.py` - Covers deterministic export behavior, validation failures, copy-not-mutate semantics, and the temporary material-string `NotImplementedError` boundary.
- `materials-discovery/tests/test_llm_translation_cif.py` - Covers CIF preamble, fixed scalar and atom-loop order, parser compatibility, preserved site order, and explicit lossy metadata.
- `materials-discovery/Progress.md` - Logs both RED/green task slices and diary notes per the repository instructions.

## Decisions Made

- Centralized export readiness checks in `validate_translated_structure_for_export(...)` so later target-family serializers inherit the same periodic-cell and fractional-coordinate contract.
- Preserved a narrow pure-text CIF path for Phase 32 rather than introducing a writer dependency, while keeping the emitted layout explicit and parser-checked against repo-local tooling.
- Kept source candidate ID, system, fidelity tier, and loss reasons visible in CIF comment lines so lossy periodic-proxy exports cannot masquerade as exact periodic structures.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Corrected the CIF site-order assertion after the first green run**
- **Found during:** Task 2 (Emit deterministic CIF text from translated artifacts)
- **Issue:** The initial test counted the CIF `loop_` control line as a data row, which made the site-order assertion fail even though the serializer preserved the correct site order.
- **Fix:** Tightened the new site-order test to ignore the `loop_` control line and only compare actual atom rows.
- **Files modified:** `materials-discovery/tests/test_llm_translation_cif.py`, `materials-discovery/Progress.md`
- **Verification:** `uv run pytest tests/test_llm_translation_cif.py -x -v` passed after the assertion fix.
- **Committed in:** `1437d8b` (part of Task 2 implementation commit)

---

**Total deviations:** 1 auto-fixed (1 blocking test assertion issue)
**Impact on plan:** No scope creep. The adjustment kept the planned coverage intact and clarified the intended CIF row parsing.

## Issues Encountered

- The executor completion signal did not return even though all four task commits landed cleanly. The plan work itself was recovered from git history and independently re-verified.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Wave 1 is complete and the shared export seam is ready for the material-string work in Plan 02.
- Plan 02 can build on the existing validation/dispatch path without reopening translation normalization.

---
*Phase: 32-cif-and-material-string-exporters*
*Completed: 2026-04-06*
