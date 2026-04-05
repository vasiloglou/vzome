---
phase: 19-local-serving-runtime-and-lane-contracts
plan: 03
subsystem: llm
tags: [llm, local-serving, replay, configs, docs, pytest]
requires:
  - phase: 19-local-serving-runtime-and-lane-contracts
    provides: shared lane resolution, local-serving readiness checks, and additive serving identity on generation and launch artifacts
provides:
  - replay-safe local-serving identity handling with explicit hard-drift rejection
  - committed local OpenAI-compatible example configs for Al-Cu-Fe and Sc-Zn
  - additive operator docs for local serving, lane selection, and compatibility boundaries
affects: [phase-20, llm-replay, llm-generate, llm-launch, operator-docs]
tech-stack:
  added: []
  patterns: [compatibility-first replay hardening, placeholder local config fixtures, additive serving-contract docs]
key-files:
  created:
    - materials-discovery/configs/systems/al_cu_fe_llm_local.yaml
    - materials-discovery/configs/systems/sc_zn_llm_local.yaml
  modified:
    - materials-discovery/src/materials_discovery/llm/replay.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_llm_replay_core.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/developers-docs/configuration-reference.md
    - materials-discovery/developers-docs/llm-integration.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/Progress.md
key-decisions:
  - "Only artifacts with explicit serving identity trigger strict local-serving replay checks; legacy mock/hosted bundles keep the historical compatibility path."
  - "Replay treats adapter/provider/model and checkpoint as hard identity, while endpoint, revision, and local-path drift remain compatible when the lane still resolves cleanly."
  - "Committed local example configs use placeholder localhost endpoints and explicit lane blocks so operators see the intended setup boundary without implying process management."
patterns-established:
  - "Replay now preserves richer serving identity when present and normalizes legacy `baseline_fallback` bundles to the modern backend-default semantics on new writes."
  - "Local-serving docs stay additive: they clarify setup, fallback, and specialization boundaries without rewriting the shipped operator workflow."
requirements-completed: [LLM-13, LLM-14, OPS-08]
duration: 1h 05m
completed: 2026-04-05
---

# Phase 19 Plan 03: Replay-Safe Local Serving Summary

**Replay now preserves richer local-serving identity safely, ships committed local lane configs, and documents the Phase 19 serving contract without breaking legacy hosted or mock workflows.**

## Performance

- **Duration:** 1h 05m
- **Completed:** 2026-04-05
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Hardened `llm-replay` so explicit local-serving identity survives into new replay artifacts and fails clearly only on true hard drift.
- Added committed local-serving system configs for `Al-Cu-Fe` and `Sc-Zn` that validate cleanly without a live server and serve as operator-facing examples.
- Updated the developer docs to explain `openai_compat_v1`, `--model-lane`, explicit fallback rules, recorded serving identity, and the fact that specialized lanes are not assumed Zomic-native in `v1.2`.
- Re-verified the phase with both a focused replay/runtime/CLI slice and the full `materials-discovery` suite.

## Task Commits

1. **Task 1 + Task 2 GREEN: replay-safe local serving support** - `613b1496` `feat(19-03): add replay-safe local serving support`

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_runtime.py tests/test_llm_generate_cli.py tests/test_cli.py -x -v`
  - Result: `38 passed in 0.89s`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
  - Result: `388 passed, 3 skipped, 1 warning in 64.27s`
- `git diff --check`
  - Result: clean before commit

## Decisions Made

- Replay strictness is now scoped to explicit serving identity rather than retroactively tightening older mock/hosted artifacts that never carried local lane metadata.
- Hard replay identity is adapter/provider/model plus checkpoint when present; endpoint, revision, and local model-path drift remain compatible as long as the current lane still resolves to the same hard identity.
- The committed example configs use explicit `model_lanes` plus `default_model_lane` / `fallback_model_lane` so later phases can benchmark real lane behavior without inventing hidden fixture-only configs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Backward-compat CLI assertion initially attached to the wrong test**
- **Found during:** Task 2 focused compatibility verification
- **Issue:** The new `run_manifest_path` assertion was first added to legacy ingest/generate tests instead of the intended legacy `llm-generate` no-lane regression.
- **Fix:** Moved the assertion into `test_cli_llm_generate_legacy_no_lane_path_still_succeeds` so the compatibility proof matches the Phase 19 serving surface.
- **Verification:** Re-ran the focused Plan 03 slice to green.
- **Committed in:** `613b1496`

---

**Total deviations:** 1 auto-fixed (1 blocking)  
**Impact on plan:** No scope change. The correction only tightened the intended backward-compatibility proof.

## Next Phase Readiness

- Phase 20 can now integrate a real specialized lane into the broader workflow with replay-safe serving identity, committed local config references, and clearer operator guidance already in place.
- Hosted, mock, and local-serving paths are all green at the full-suite level, so Phase 20 can focus on meaningful specialized-lane behavior rather than repairing the transport contract.

## Self-Check

PASSED

---
*Phase: 19-local-serving-runtime-and-lane-contracts*  
*Completed: 2026-04-05*
