---
phase: 19-local-serving-runtime-and-lane-contracts
plan: 02
subsystem: llm
tags: [llm, local-serving, cli, lane-resolution, manifests, pytest]
requires:
  - phase: 19-local-serving-runtime-and-lane-contracts
    provides: additive local-serving schema, serving identity, and OpenAI-compatible readiness probing
provides:
  - shared serving-lane resolution across manual generation and campaign launch
  - additive serving identity in run manifests and resolved launch artifacts
  - operator-facing `--model-lane` support with early local-serving diagnostics
affects: [19-03, llm-generate, llm-launch, llm-replay]
tech-stack:
  added: []
  patterns: [shared lane precedence contract, compatibility-first CLI overlays, early readiness validation]
key-files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/llm/generate.py
    - materials-discovery/src/materials_discovery/llm/launch.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_llm_generate_core.py
    - materials-discovery/tests/test_llm_launch_core.py
    - materials-discovery/tests/test_llm_generate_cli.py
    - materials-discovery/tests/test_llm_launch_cli.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/Progress.md
key-decisions:
  - "Treat lane resolution as one shared contract so manual generation, campaign launch, and later replay all resolve configured/default/fallback/backend-default behavior the same way."
  - "Fail requested unavailable lanes unless an explicit fallback lane is configured; do not silently downgrade a local or specialized request to the backend tuple."
  - "Record nested serving identity additively while preserving the existing flat manifest fields so older consumers keep working."
patterns-established:
  - "CLI-requested lanes now override config defaults, which override explicit fallback, which override backend-default behavior."
  - "Local-serving readiness is checked before generation starts, so operators see lane and endpoint context before any provider call is attempted."
requirements-completed: [LLM-13, LLM-14, OPS-08]
duration: 35min
completed: 2026-04-05
---

# Phase 19 Plan 02: Lane-Aware Local Serving Integration Summary

**Manual `llm-generate` and campaign `llm-launch` now share one deterministic serving-lane contract, record richer serving identity, and fail early when local lanes are unavailable.**

## Performance

- **Duration:** 35 min
- **Completed:** 2026-04-05
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- Added shared `resolve_serving_lane(...)` semantics so manual generation and campaign launch follow the same configured/default/fallback/backend-default precedence.
- Added `llm-generate --model-lane` plus early readiness diagnostics for local-serving lanes while keeping the existing no-lane hosted and mock flow intact.
- Threaded additive `serving_identity` into run manifests and resolved launch artifacts without changing the candidate JSONL contract.
- Locked the behavior with focused generate/launch core and CLI regression coverage that remains fully offline.

## Task Commits

1. **Task 1 + Task 2 GREEN: lane-aware local serving integration** - `92a48b9c` `feat(19-02): add lane-aware local serving integration`

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_core.py tests/test_llm_launch_cli.py tests/test_cli.py -x -v`
  - Result: `40 passed in 1.13s`
- `git diff --check`
  - Result: clean before commit

## Decisions Made

- `resolve_campaign_model_lane(...)` keeps campaign intent extraction, but now delegates final lane availability and fallback semantics to the shared serving resolver.
- Manual `llm-generate` now constructs the same `LlmServingIdentity` shape that campaign launch writes, so replay and downstream auditing can compare like-for-like artifacts.
- Legacy no-lane configs continue to resolve through the backend tuple as `backend_default` instead of introducing a new implicit local-lane assumption.

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

- Phase 19 Plan 03 can now make replay decisions against explicit requested/resolved lane identity instead of inferring from flat adapter/provider/model fields alone.
- The docs and committed local example configs can now describe a real operator contract, because the lane-aware CLI and launch behavior are in place.

## Self-Check

PASSED

---
*Phase: 19-local-serving-runtime-and-lane-contracts*  
*Completed: 2026-04-05*
