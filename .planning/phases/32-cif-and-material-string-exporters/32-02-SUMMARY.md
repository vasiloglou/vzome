---
phase: 32-cif-and-material-string-exporters
plan: 02
subsystem: api
tags: [translation, crystaltextllm, serializer, pytest, interoperability]
requires:
  - phase: 32-cif-and-material-string-exporters
    provides: shared export validation seam and deterministic CIF serialization from Plan 01
provides:
  - CrystalTextLLM-compatible material-string emitter
  - cross-target export dispatch for CIF and material strings
  - regression coverage for material-string parsing and shared artifact identity
affects: [32-03, 33]
tech-stack:
  added: []
  patterns:
    - parser-compatible material-string bodies with provenance kept on the artifact
    - cross-target copy-not-mutate export dispatch over one normalized artifact
key-files:
  created:
    - materials-discovery/tests/test_llm_translation_material_string.py
  modified:
    - materials-discovery/src/materials_discovery/llm/translation_export.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/tests/test_llm_translation_export.py
    - materials-discovery/Progress.md
key-decisions:
  - "Implemented `crystaltextllm_material_string` as a bare CrystalTextLLM-compatible body so the shipped target name remains honest about downstream parser compatibility."
  - "Kept source linkage, fidelity tier, and loss metadata on `TranslatedStructureArtifact` rather than embedding repo-only headers into the raw material string."
patterns-established:
  - "Material-string exports preserve translated site order using alternating species and fractional-coordinate lines."
  - "CIF and material-string branches now share the same validation gate, emitted-text copy semantics, and normalized artifact identity."
requirements-completed: [LLM-28, LLM-29]
duration: 2 min
completed: 2026-04-06
---

# Phase 32 Plan 02: Material-String Exporter and Cross-Target Dispatch Summary

**CrystalTextLLM-compatible material-string emission with shared cross-target export dispatch from one translated artifact identity**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-06T23:17:42-04:00
- **Completed:** 2026-04-06T23:20:28-04:00
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added the first working `material_string` exporter as a bare CrystalTextLLM-compatible body with lengths, angles, and alternating species/fractional-coordinate lines.
- Finished `emit_translated_structure(...)` so both built-in target families now emit through the shared validation seam without mutating the source artifact.
- Locked the new behavior with RED/green coverage for parser-style material-string decoding, byte-stable emission, preserved site order, and shared cross-target artifact identity.

## Task Commits

Each task was committed atomically:

1. **Task 1: Emit deterministic CrystalTextLLM-style material strings from translated artifacts** - `3c77073` (test), `464dfef` (feat)
2. **Task 2: Finish cross-target dispatch and preserve identical artifact identity across CIF and material-string export** - `af9c6e6` (test), `b50f1d4` (feat)

_Note: TDD tasks used RED then implementation commits._

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/translation_export.py` - Adds `emit_material_string_text(...)` and dispatch support for both built-in target families.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Exports the new public material-string emitter alongside the existing export helpers.
- `materials-discovery/tests/test_llm_translation_material_string.py` - Covers CrystalTextLLM-compatible body layout, parser-style decoding, lossy fixture handling, and byte-stable emission.
- `materials-discovery/tests/test_llm_translation_export.py` - Replaces the old not-implemented boundary with real cross-target dispatch and normalized-identity assertions.
- `materials-discovery/Progress.md` - Logs both RED/green task slices and the compatibility-first deviation under the required changelog and diary entries.

## Decisions Made

- Chose actual CrystalTextLLM compatibility over the literal self-describing body described in the plan, because the review surfaced that repo-only headers would make the shipped target name misleading and would break downstream parsing.
- Kept provenance, fidelity, and loss metadata on the translated artifact contract so the raw emitted material string stays parser-compatible while the repo still preserves auditable export context.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Honesty/Contract] Switched the material-string body to actual CrystalTextLLM-compatible output**
- **Found during:** Task 1 (Emit deterministic CrystalTextLLM-style material strings from translated artifacts)
- **Issue:** The literal Plan 02 body layout used repo-specific header lines and key/value records that conflicted with the research, the Phase 32 review, and the shipped target name `crystaltextllm_material_string`.
- **Fix:** Implemented a bare CrystalTextLLM-compatible body with lengths, angles, and alternating species/fractional-coordinate lines, while keeping source/fidelity/loss metadata on `TranslatedStructureArtifact`.
- **Files modified:** `materials-discovery/src/materials_discovery/llm/translation_export.py`, `materials-discovery/tests/test_llm_translation_material_string.py`, `materials-discovery/Progress.md`
- **Verification:** `uv run pytest tests/test_llm_translation_material_string.py -x -v` passed and the parser-style test fixture decoded the emitted body successfully.
- **Committed in:** `464dfef` (Task 1 implementation commit)

---

**Total deviations:** 1 auto-fixed (1 honesty/contract deviation)
**Impact on plan:** The target name and emitted text now align honestly with downstream CrystalTextLLM expectations. Provenance semantics remain preserved on the artifact contract instead of being lost.

## Issues Encountered

- The executor completion signal again did not return after the task commits landed, so the summary and phase-metadata bookkeeping were reconstructed from git history and independently re-verified locally.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Wave 2 is complete and both built-in target families now emit from the same normalized artifact contract.
- Plan 03 can freeze the exact bytes, add golden fixtures, and extend parser/failure coverage across both exporters.

---
*Phase: 32-cif-and-material-string-exporters*
*Completed: 2026-04-06*
