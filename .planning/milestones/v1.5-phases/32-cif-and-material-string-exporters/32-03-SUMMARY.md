---
phase: 32-cif-and-material-string-exporters
plan: 03
subsystem: testing
tags: [translation, cif, crystaltextllm, pytest, regression]
requires:
  - phase: 32-cif-and-material-string-exporters
    provides: deterministic CIF and CrystalTextLLM-compatible material-string exporters from Plans 01 and 02
provides:
  - checked-in golden outputs for exact and lossy exporter boundary cases
  - parser compatibility coverage for periodic and lossy CIF payloads
  - explicit malformed-artifact regression coverage on the shared export seam
affects: [33, translation-cli, interoperability]
tech-stack:
  added: []
  patterns:
    - golden-file regression anchors for shipped exporter bytes
    - explicit separation between lossy artifact metadata and bare material-string bodies
key-files:
  created:
    - materials-discovery/tests/test_llm_translation_export_fixtures.py
    - materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_expected.cif
    - materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_expected.material_string.txt
    - materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_expected.cif
    - materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_expected.material_string.txt
  modified:
    - materials-discovery/tests/test_llm_translation_cif.py
    - materials-discovery/tests/test_llm_translation_export.py
    - materials-discovery/Progress.md
key-decisions:
  - "Frozen the actual shipped contract: CIF goldens include the fidelity/loss comment preamble, while material-string goldens stay bare CrystalTextLLM-compatible bodies."
  - "Kept lossy material-string provenance assertions on TranslatedStructureArtifact instead of reintroducing repo-only metadata headers into the raw text."
  - "Used repo-local parse_cif coverage against both the checked-in periodic golden and the stripped lossy payload so parser compatibility is explicit and stable."
patterns-established:
  - "Exporter stability is anchored on checked-in golden files instead of inline string fragments."
  - "Malformed periodic artifacts fail through the shared export dispatcher, while legitimate lossy exports remain serializable."
requirements-completed: [LLM-28, LLM-29]
duration: 3 min
completed: 2026-04-06
---

# Phase 32 Plan 03: Golden Exporter Regressions Summary

**Golden CIF and CrystalTextLLM-compatible material-string fixtures with parser-backed CIF regressions and explicit malformed-artifact export failures**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-06T23:25:31-04:00
- **Completed:** 2026-04-06T23:28:50-04:00
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Added four checked-in golden outputs that freeze the exact Al-Cu-Fe and lossy Sc-Zn exporter bytes across both built-in target families.
- Added `test_llm_translation_export_fixtures.py` so exporter regressions now compare emitted bytes directly against repo-backed goldens instead of ad hoc inline fragments.
- Extended CIF and export tests to prove repo-local CIF parsing remains compatible and malformed periodic artifacts fail cleanly without blocking legitimate lossy exports.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add golden-output fixtures and regression coverage for exact and lossy exporter paths** - `334fc1c1` (test), `4ea83589` (test)
2. **Task 2: Add parser compatibility and malformed-artifact failure coverage** - `95ff9355` (test)

## Files Created/Modified

- `materials-discovery/tests/test_llm_translation_export_fixtures.py` - Adds the golden-output regression suite for both candidate fixtures and both target families.
- `materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_expected.cif` - Freezes the exact periodic-safe CIF output.
- `materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_expected.material_string.txt` - Freezes the exact bare CrystalTextLLM-compatible material-string body.
- `materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_expected.cif` - Freezes the lossy QC-native CIF output with explicit fidelity/loss metadata.
- `materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_expected.material_string.txt` - Freezes the lossy bare CrystalTextLLM-compatible material-string body.
- `materials-discovery/tests/test_llm_translation_cif.py` - Adds parser coverage for the checked-in periodic golden and the stripped lossy QC payload.
- `materials-discovery/tests/test_llm_translation_export.py` - Adds malformed-artifact export failures and positive lossy-export assertions through the shared dispatcher.
- `materials-discovery/Progress.md` - Logs the Task 1 and Task 2 regression work per repo rules.

## Decisions Made

- Froze the compatibility-first Phase 32 contract exactly as shipped instead of reviving the superseded header-based material-string concept.
- Treated raw material-string goldens as parser-facing bodies and the translated artifact as the home for provenance, fidelity tier, and loss reasons.
- Added parser coverage at the repo-local `parse_cif()` boundary so later CLI/file workflow work in Phase 33 inherits a stable CIF compatibility proof.

## Deviations from Plan

None - plan executed exactly as written, using the already-approved Phase 32 compatibility-first material-string contract.

## Issues Encountered

None - the existing exporter implementation already satisfied the new parser and malformed-artifact guard rails once the regression coverage was added.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 32 now ends with frozen exporter bytes, parser-compatible CIF coverage, and explicit malformed-artifact failures.
- Phase 33 can build the CLI/file-backed workflow on top of stable goldens instead of reinterpreting exporter behavior.

## Self-Check: PASSED

- Verified all created golden fixtures, the new regression test file, and this summary exist on disk.
- Verified task commits `334fc1c1`, `4ea83589`, and `95ff9355` exist in git history.
- Scanned the created and modified plan files for placeholder/stub markers and found none.

---
*Phase: 32-cif-and-material-string-exporters*
*Completed: 2026-04-06*
