---
phase: 20-specialized-lane-integration-and-workflow-compatibility
plan: 01
subsystem: llm
tags: [llm, evaluation, specialized-lane, schema, provenance, pytest]
requires:
  - phase: 19-local-serving-runtime-and-lane-contracts
    provides: shared serving-lane resolution, readiness probing, and additive serving identity
provides:
  - additive evaluation-lane config selection
  - typed serving identity on evaluation artifacts and summaries
  - a thin specialist payload seam for evaluation-primary specialized lanes
affects: [20-02, 20-03, llm-evaluate, llm-compare, llm-replay]
tech-stack:
  added: []
  patterns: [additive schema evolution, shared lane resolution reuse, compatibility-first provenance enrichment]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/specialist.py
  modified:
    - materials-discovery/src/materials_discovery/common/schema.py
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/evaluate.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/tests/test_llm_evaluate_schema.py
    - materials-discovery/Progress.md
key-decisions:
  - "Evaluation lane selection reuses Phase 19's shared serving resolver instead of introducing a second model-lane registry under `llm_evaluate`."
  - "Specialized evaluation remains additive: the candidate JSONL contract is unchanged and richer lane identity only appears in provenance, run manifests, and summaries."
  - "The first specialized seam is prompt-and-payload level only; it adds structure-aware context without pretending off-the-shelf materials models are Zomic-native generators."
patterns-established:
  - "Evaluation summaries, assessments, and run manifests now carry the same requested/resolved lane and serving-identity shape already used by generation and launch artifacts."
  - "Legacy evaluation artifacts remain readable because all new lane and serving fields are optional on deserialize."
requirements-completed: [LLM-15, OPS-09]
duration: 35min
completed: 2026-04-05
---

# Phase 20 Plan 01: Specialized Evaluation Foundation Summary

**`llm-evaluate` can now resolve and record a specialized materials lane honestly, while staying backward-compatible with the existing evaluation artifact family.**

## Performance

- **Duration:** 35 min
- **Completed:** 2026-04-05
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Added additive `llm_evaluate.model_lane` support plus richer `LlmEvaluateSummary` fields for requested/resolved lane identity and typed `serving_identity`.
- Extended `LlmAssessment` and `LlmEvaluationRunManifest` with additive lane identity while keeping older manifests readable.
- Added `llm/specialist.py` and routed specialized evaluation through a structure-aware payload seam instead of making the specialized lane differ only by endpoint choice.
- Taught `evaluate_llm_candidates(...)` to reuse `resolve_serving_lane(...)`, `build_serving_identity(...)`, and `validate_llm_adapter_ready(...)` from the shipped Phase 19 serving contract.

## Task Commits

1. **Task 1 + Task 2 GREEN: specialized evaluation lane foundation** - `3222cb9a` `feat(20-01): add specialized evaluation lane foundation`

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run python -m pytest tests/test_llm_evaluate_schema.py -x -v`
  - Result: `5 passed in 0.41s`
- `git diff --check`
  - Result: pending before commit

## Decisions Made

- Evaluation lane precedence is now: explicit request, then `llm_evaluate.model_lane`, then the Phase 19 shared default/fallback/backend-default semantics.
- Specialized evaluation provenance records both the requested lane and the resolved lane so explicit fallback can stay auditable later in CLI and compare surfaces.
- `LlmEvaluateSummary` remains in `common/schema.py`, but its nested `serving_identity` typing is rebuilt from `llm/schema.py` so CLI JSON output can stay typed without creating a new common-vs-llm split.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Local test environment was missing the Phase 20 dev dependencies**
- **Found during:** First Wave 1 pytest attempt
- **Issue:** `uv run pytest` could not spawn `pytest`, and the system Python lacked `pydantic`, so the planned regression command could not run as written in the unsynced environment.
- **Fix:** Synced the repo with `uv sync --extra dev --extra ingestion` and ran the equivalent verification via `uv run python -m pytest ...`, which exercises the same environment and test surface.
- **Verification:** Focused `tests/test_llm_evaluate_schema.py` slice passed green afterward.
- **Committed in:** `3222cb9a`

---

**Total deviations:** 1 auto-fixed (1 blocking)  
**Impact on plan:** No scope change. The fix only restored the intended verification path in the local workspace.

## Next Phase Readiness

- Phase 20 Plan 02 can now expose a real specialized evaluation lane through CLI and config because the core evaluation engine already resolves, validates, and records lane identity.
- Compare, report, and replay can now add evaluation-lane visibility without inventing a second evaluation artifact contract.

## Self-Check

PASSED

---
*Phase: 20-specialized-lane-integration-and-workflow-compatibility*  
*Completed: 2026-04-05*
