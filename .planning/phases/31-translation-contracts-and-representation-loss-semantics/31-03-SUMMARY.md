---
phase: 31-translation-contracts-and-representation-loss-semantics
plan: 03
subsystem: llm
tags: [fixtures, translation, docs, cif, crystaltextllm]
requires:
  - phase: 31-01-plan
    provides: typed translated-structure artifact schema and target registry
  - phase: 31-02-plan
    provides: deterministic normalization seam and fidelity classification
provides:
  - repo-backed periodic-safe and QC-native translation fixtures for later serializer work
  - fixture regression coverage that freezes exact versus lossy export boundaries
  - implementation-facing translation contract note for Phase 32 exporters
affects: [32-cif-and-material-string-exporters, 33-cli-benchmark-hooks-and-operator-docs]
tech-stack:
  added: []
  patterns:
    - repo-backed translation fixtures encode the periodic-safe versus QC-native distinction in data shape, not only in prose
    - exporter handoff docs stay implementation-facing and defer operator workflow guidance to Phase 33
key-files:
  created:
    - materials-discovery/tests/test_llm_translation_fixtures.py
    - materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_candidate.json
    - materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_candidate.json
    - materials-discovery/developers-docs/llm-translation-contract.md
  modified:
    - materials-discovery/Progress.md
key-decisions:
  - "Made the periodic-safe versus QC-native fixture boundary explicit in the fixture data shape by using stored fractional coordinates for Al-Cu-Fe and qphi-only sites for Sc-Zn."
  - "Kept `approximate` covered in translation-core tests rather than adding a third fixture because Plan 03 needed to freeze the two exporter-facing boundary cases first."
  - "Kept the new translation contract note implementation-facing and deferred operator workflow and CLI guidance to Phase 33."
patterns-established:
  - "Phase 32 serializers should build from `prepare_translated_structure(...)` plus a resolved target descriptor instead of reading raw candidate dicts."
  - "Phase-level fixture regressions should load repo files directly so contract tests cannot drift into synthetic inline-only examples."
requirements-completed: [LLM-27, LLM-30]
duration: 5min
completed: 2026-04-06
---

# Phase 31 Plan 03: Translation Contracts and Representation Loss Semantics Summary

**Repo-backed periodic-safe and QC-native translation fixtures plus an implementation-facing exporter contract for Phase 32**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-06T23:58:13Z
- **Completed:** 2026-04-07T00:03:17Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added repo-backed translation fixtures that freeze the contract on a periodic-safe Al-Cu-Fe candidate and a QC-native/lossy Sc-Zn candidate.
- Added fixture regression coverage across both built-in translation targets so Phase 32 cannot silently blur the exact-versus-lossy boundary.
- Wrote a developer translation contract note that defines the source-of-truth boundary, target registry, fidelity semantics, and Phase 32 serializer handoff.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add fixture-backed regression coverage for periodic-safe and QC-native/lossy translation paths** - `a8bbd64b` (test, RED), `2547392e` (feat, GREEN)
2. **Task 2: Write the developer translation contract note for exporter implementers** - `013d636c` (chore)

_Note: Task 1 used TDD and therefore has separate RED and GREEN commits._

## Files Created/Modified

- `materials-discovery/tests/test_llm_translation_fixtures.py` - Regression tests that load repo fixtures, assert exact versus lossy behavior, and prove deterministic translation output.
- `materials-discovery/tests/fixtures/llm_translation/al_cu_fe_periodic_candidate.json` - Periodic-safe Al-Cu-Fe candidate fixture with stored fractional coordinates on every site.
- `materials-discovery/tests/fixtures/llm_translation/sc_zn_qc_candidate.json` - QC-native Sc-Zn candidate fixture with qphi-only site geometry that stays explicitly lossy for periodic targets.
- `materials-discovery/developers-docs/llm-translation-contract.md` - Implementation-facing contract note for Phase 32 serializer authors.
- `materials-discovery/Progress.md` - Required changelog and diary updates for the RED, GREEN, and documentation work.

## Decisions Made

- Encoded the periodic-safe versus QC-native fixture distinction directly in the fixture payloads instead of depending on descriptive comments alone.
- Documented that the `approximate` tier remains anchored in `test_llm_translation_core.py` because this wave needed to freeze the exporter-facing boundary cases first.
- Kept the new doc focused on implementer semantics and explicitly deferred operator-facing CLI/runbook guidance to Phase 33.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 32 now has stable repo fixtures, a deterministic regression suite, and a written serializer contract for both built-in target families. No blockers remain from Phase 31; the only intentional gap is that `approximate` stays covered in translation-core tests rather than a dedicated fixture.

## Self-Check

PASSED

- Summary file exists: `31-03-SUMMARY.md`
- Task commits verified: `a8bbd64b`, `2547392e`, `013d636c`
