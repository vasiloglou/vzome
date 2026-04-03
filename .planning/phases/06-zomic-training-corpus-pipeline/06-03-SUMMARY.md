---
phase: 06-zomic-training-corpus-pipeline
plan: 03
subsystem: materials-discovery
tags: [llm, zomic, converters, compiler, projection, materials-discovery]
requires: [06-01, 06-02]
provides:
  - deterministic CandidateRecord -> Zomic conversion with trace metadata
  - shared qphi axis-walk decomposition and geometry-equivalence helper
  - bridge-backed compile-validation helper and PyQCstrc projection conversion
affects: [06-04, LLM-01]
tech-stack:
  added: []
  patterns: [comment-preamble serializer, bounded axis-walk search, temp design wrapper around zomic bridge, fixture-backed projection conversion]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/converters/__init__.py
    - materials-discovery/src/materials_discovery/llm/converters/axis_walk.py
    - materials-discovery/src/materials_discovery/llm/converters/record2zomic.py
    - materials-discovery/src/materials_discovery/llm/compiler.py
    - materials-discovery/src/materials_discovery/llm/converters/projection2zomic.py
    - materials-discovery/tests/test_llm_record2zomic.py
    - materials-discovery/tests/test_llm_projection2zomic.py
    - .planning/phases/06-zomic-training-corpus-pipeline/06-03-SUMMARY.md
  modified:
    - materials-discovery/tests/fixtures/pyqcstrc_projection_sample.json
    - materials-discovery/Progress.md
key-decisions:
  - "Reserve exact fidelity for native or exact-source paths; CandidateRecord conversion defaults to anchored unless a later equivalence check proves otherwise."
  - "Wrap compile validation in a temporary design-YAML seam so the phase reuses the existing zomic bridge instead of inventing a second compiler."
  - "Keep PyQCstrc support fixture-backed and offline by converting the committed payload through the same record2zomic serializer backbone."
patterns-established:
  - "Conversion traces carry strategy, step count, unresolved axes, and a stable source signature."
  - "Compile-validation is testable offline via monkeypatched bridge calls because the temp design wrapper is isolated and deterministic."
requirements-completed: []
duration: 36min
completed: 2026-04-03
---

# Phase 6 Plan 03: Converter Backbone Summary

**Deterministic record conversion, temporary compile validation, and offline PyQCstrc projection coverage**

## Performance

- **Duration:** 36 min
- **Completed:** 2026-04-03
- **Tasks:** 2
- **Task commits:** 2

## Accomplishments

- Added `axis_walk.py` and `record2zomic.py` so CandidateRecord inputs can be
  serialized into deterministic Zomic text with orbit grouping, comment
  preambles, source-label preservation, and explicit fidelity traces.
- Added `compiler.py` and `projection2zomic.py` so Phase 6 can validate Zomic
  text through the existing bridge seam and convert committed PyQCstrc payloads
  without a live external dependency.
- Added focused tests covering deterministic ordering, duplicate-label
  disambiguation, compile-success/failure reporting, and scale-sensitive temp
  design generation.

## Task Commits

1. **Task 1: Implement deterministic record2zomic conversion with trace metadata** - `876018ab` (`feat`)
2. **Task 2: Add compile-validation helper and projection2zomic for PyQCstrc payloads** - `a6133fb2` (`feat`)

## Verification

- `cd materials-discovery && uv run pytest tests/test_llm_record2zomic.py tests/test_llm_projection2zomic.py -x -v`

The combined converter/compiler verification passed after the orbit-name expectation was corrected.

## Deviations from Plan

### Auto-fixed Issues

**1. Orbit-name expectation in the first record2zomic test used the raw label instead of the shared orbit-name rule**

- **Found during:** `tests/test_llm_record2zomic.py`
- **Issue:** The initial expectation assumed `joint.top.right` would remain the orbit name, but the existing `_infer_orbit_name()` contract reduces that label to `joint`.
- **Fix:** Updated the test to follow the shared orbit-name contract rather than special-casing the converter output.
- **Files modified:** `materials-discovery/tests/test_llm_record2zomic.py`
- **Verification:** `cd materials-discovery && uv run pytest tests/test_llm_record2zomic.py tests/test_llm_projection2zomic.py -x -v`

---

**Total deviations:** 1 auto-fixed
**Impact on plan:** The fix clarified the intended contract and did not require converter redesign.

## Next Phase Readiness

- The final builder can now consume CandidateRecord, PyQCstrc, and later
  exact-source loaders through a consistent `CorpusExample` contract.
- Phase 6 now has the compile-validation seam needed to promote generated
  examples out of `pending` during assembly.

## Self-Check: PASSED

- Verified commits `876018ab` and `a6133fb2` exist in git history.
- Verified the combined converter/compiler test slice passes.
