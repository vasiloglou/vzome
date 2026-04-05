---
phase: 20-specialized-lane-integration-and-workflow-compatibility
plan: 03
subsystem: llm
tags: [llm, specialized-lane, docs, real-mode, replay, compare, pytest]
requires:
  - phase: 20-specialized-lane-integration-and-workflow-compatibility
    provides: lane-aware evaluation contract, additive evaluation lineage, and the deep Al-Cu-Fe specialized proof
provides:
  - thin Sc-Zn specialized evaluation compatibility proof
  - additive operator docs for evaluation-primary specialized lanes
  - full-suite-stable specialized workflow closeout
affects: [phase-21, llm-launch, llm-replay, llm-compare, llm-evaluate, operator-docs]
tech-stack:
  added: []
  patterns: [thin compatibility proof, additive workflow docs, full-suite cleanup]
key-files:
  created: []
  modified:
    - materials-discovery/configs/systems/sc_zn_llm_local.yaml
    - materials-discovery/developers-docs/configuration-reference.md
    - materials-discovery/developers-docs/llm-integration.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/src/materials_discovery/llm/converters/projection2zomic.py
    - materials-discovery/tests/test_real_mode_pipeline.py
    - materials-discovery/Progress.md
key-decisions:
  - "Sc-Zn stays a thin compatibility proof: it proves launch, replay, compare, and specialized evaluation lineage can coexist on a second system without duplicating the deeper Al-Cu-Fe proof."
  - "Phase 20 docs now describe the specialized lane honestly as evaluation-primary and generation-compatible, while keeping direct Zomic-native specialized generation for a later milestone."
  - "Inherited full-suite float noise is fixed at the projection conversion boundary instead of loosening the regression or hiding the mismatch in tests."
patterns-established:
  - "Generation and evaluation lane identity can now differ intentionally while compare and report keep both lineages visible inside the existing artifact families."
  - "Specialized endpoint guidance stays operational and additive: the docs show an OpenAI-compatible recipe without implying `mdisc` manages the serving process."
requirements-completed: [LLM-15, LLM-16, OPS-09]
duration: 47min
completed: 2026-04-05
---

# Phase 20 Plan 03: Sc-Zn Compatibility and Docs Summary

**Phase 20 now closes with one deep specialized proof, one thinner compatibility proof, honest operator docs, and a full-suite-green handoff to the benchmark milestone.**

## Performance

- **Duration:** 47 min
- **Completed:** 2026-04-05
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Added `llm_evaluate.model_lane: specialized_materials` to `sc_zn_llm_local.yaml` without disturbing its seeded cubic generation path.
- Added an offline `Sc-Zn` end-to-end regression that launches, replays, injects specialized evaluation lineage, and compares successfully while keeping generation on `general_purpose`.
- Updated the configuration, integration, and pipeline docs so Phase 20 now states the specialized lane boundary explicitly: evaluation-primary, generation-compatible, one deep proof plus one thin proof, and a concrete OpenAI-compatible endpoint recipe.
- Fixed inherited projection metadata float noise in `projection2zomic` so the expanded full-suite run stays exact-value stable.

## Task Commits

1. **Task 1 + Task 2 GREEN: Sc-Zn compatibility proof and docs closeout** - `d976fd8b` `feat(20-03): add sc-zn specialized workflow compatibility`

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run python -m pytest tests/test_real_mode_pipeline.py tests/test_cli.py tests/test_llm_compare_cli.py -x -v`
  - Result: `25 passed in 25.29s`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run python -m pytest tests/test_llm_projection2zomic.py -x -v`
  - Result: `6 passed in 0.46s`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run python -m pytest`
  - Result: `393 passed, 3 skipped, 1 warning in 29.32s`
- `git diff --check`
  - Result: clean before commit

## Decisions Made

- `Sc-Zn` is intentionally not a second deep specialist workflow; it is the lighter proof that the specialized evaluation lane does not fracture launch/replay/compare when applied to another system.
- Phase 20 documentation now treats `llm_evaluate.model_lane` as a first-class operator control and makes it explicit that evaluation may use `specialized_materials` while generation stays on `general_purpose`.
- The full-suite cleanup happened in code, not in tests: projection metadata is normalized deterministically where it is produced.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Full-suite regression exposed inherited float noise in `projection2zomic` composition metadata**
- **Found during:** Final full-suite verification
- **Issue:** `tests/test_llm_projection2zomic.py` compared exact composition values and surfaced `0.7000000000000001`-style float noise after the wider Phase 20 verification pass.
- **Fix:** Normalized the returned `CorpusExample.composition` in `projection2zomic.py` after `candidate_to_zomic(...)` so the conversion remains deterministic and exact-value stable.
- **Verification:** Re-ran `tests/test_llm_projection2zomic.py` to `6 passed`, then re-ran the full suite to `393 passed, 3 skipped, 1 warning`.
- **Committed in:** `d976fd8b`

---

**Total deviations:** 1 auto-fixed (1 blocking)  
**Impact on plan:** No scope change. The fix only restored full-suite stability while finishing the planned Phase 20 closeout work.

## Next Phase Readiness

- Phase 21 can now focus on comparative benchmarks and operator serving workflow instead of contract repair.
- Hosted, local, and specialized lanes now share stable generation/evaluation lineage semantics, committed configs, and additive operator docs.

## Self-Check

PASSED

---
*Phase: 20-specialized-lane-integration-and-workflow-compatibility*  
*Completed: 2026-04-05*
