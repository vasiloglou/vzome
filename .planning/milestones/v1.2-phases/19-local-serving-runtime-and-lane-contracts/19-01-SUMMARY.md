---
phase: 19-local-serving-runtime-and-lane-contracts
plan: 01
subsystem: llm
tags: [llm, local-serving, runtime, schema, pydantic, pytest]
requires:
  - phase: 11-closed-loop-campaign-execution-bridge
    provides: typed launch and replay lineage contracts for llm artifacts
provides:
  - additive local-serving backend and lane config fields
  - typed serving identity for run and launch artifacts
  - openai-compatible local runtime adapter plus readiness diagnostics
affects: [19-02, 19-03, llm-generate, llm-launch, llm-replay]
tech-stack:
  added: []
  patterns: [additive schema evolution, offline runtime probing, compatibility-first artifact contracts]
key-files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/common/schema.py
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/runtime.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/tests/test_llm_launch_schema.py
    - materials-discovery/tests/test_llm_runtime.py
    - materials-discovery/Progress.md
key-decisions:
  - "Treat serving identity as additive and optional so older launch and replay bundles still deserialize cleanly."
  - "Default local readiness probing to `/v1/models` and keep the local-serving seam fully offline-testable with monkeypatched HTTP."
  - "Normalize API base values early so later lane resolution and replay comparisons are comparing stable identities rather than slash variants."
patterns-established:
  - "Local-serving support now extends the existing llm runtime seam instead of introducing a second generation engine."
  - "Run and launch artifacts can now carry nested serving identity while preserving the existing flat adapter/provider/model fields for compatibility."
requirements-completed: [LLM-13, LLM-14]
duration: 28min
completed: 2026-04-05
---

# Phase 19 Plan 01: Local Serving Schema and Runtime Foundation Summary

**Phase 19 now has the additive schema and runtime contract needed to support a local OpenAI-compatible serving lane without breaking the shipped hosted and mock paths.**

## Performance

- **Duration:** 28 min
- **Completed:** 2026-04-05
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Added additive local-serving transport controls and lane-identity fields to the shared config surface in `common/schema.py`.
- Introduced typed `LlmServingIdentity` support for run and launch artifacts while preserving compatibility with older artifacts that do not carry nested serving identity.
- Added `openai_compat_v1` plus `validate_llm_adapter_ready()` so later manual and campaign flows can validate an already-running local server before generation attempts start.
- Locked the new behavior with focused schema and runtime coverage that stays fully offline.

## Task Commits

1. **Task 1 + Task 2 GREEN: local-serving schema and runtime foundation** - `33d3f247` `feat(19-01): add local serving runtime contracts`

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_runtime.py -x -v`
  - Result: `20 passed in 0.51s`
- `git diff --check`
  - Result: clean before commit

## Decisions Made

- `BackendConfig` now owns local transport timeouts and optional probe path, while lane-specific identity stays in `LlmModelLaneConfig`.
- `resolved_model_lane_source` now accepts the Phase 19 explicit values while still reading legacy `baseline_fallback`.
- OpenAI-compatible response parsing prefers `choices[0].message.content` and only falls back to `choices[0].text` as a compatibility path.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] First commit attempt hit a transient `.git/index.lock`**
- **Found during:** Plan 01 commit
- **Issue:** The initial `git add && git commit` attempt reported `.git/index.lock` contention even though no active git process remained.
- **Fix:** Confirmed the lock file had already disappeared, re-staged the Plan 01 files, and retried the commit successfully.
- **Verification:** `ls -l .git/index.lock`, `ps -ef | rg "git (commit|add|status|diff|update-index|write-tree)"`, then retry commit
- **Committed in:** `33d3f247`

---

**Total deviations:** 1 auto-fixed (1 blocking)  
**Impact on plan:** No scope change. The retry preserved the intended Plan 01 surface and verification result.

## Next Phase Readiness

- Phase 19 Plan 02 can now resolve lanes against a richer, normalized serving identity and a real local adapter key.
- Phase 19 Plan 03 can now make replay decisions against explicit local-serving metadata instead of inferring from flat adapter/provider/model fields alone.

## Self-Check

PASSED

---
*Phase: 19-local-serving-runtime-and-lane-contracts*  
*Completed: 2026-04-05*
