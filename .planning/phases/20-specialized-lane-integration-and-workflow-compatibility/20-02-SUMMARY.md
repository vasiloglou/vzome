---
phase: 20-specialized-lane-integration-and-workflow-compatibility
plan: 02
subsystem: llm
tags: [llm, evaluation, compare, report, replay, cli, pytest]
requires:
  - phase: 20-specialized-lane-integration-and-workflow-compatibility
    provides: lane-aware evaluation core, typed evaluation serving identity, and specialist payload routing
provides:
  - operator-facing `llm-evaluate --model-lane`
  - a real `Al-Cu-Fe` specialized evaluation proof config
  - additive compare/report visibility for distinct evaluation-lane lineage
affects: [20-03, llm-evaluate, llm-compare, report, replay]
tech-stack:
  added: []
  patterns: [operator-addressable lane selection, additive lineage comparison, compatibility-first reporting]
key-files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/compare.py
    - materials-discovery/configs/systems/al_cu_fe_llm_local.yaml
    - materials-discovery/tests/test_llm_evaluate_cli.py
    - materials-discovery/tests/test_llm_compare_core.py
    - materials-discovery/tests/test_llm_compare_cli.py
    - materials-discovery/tests/test_report.py
    - materials-discovery/Progress.md
key-decisions:
  - "The first specialized lane is operationally real through evaluation-first behavior on `Al-Cu-Fe`, not by pretending the specialist endpoint is a mature Zomic generator."
  - "Compare keeps generation-lane lineage and evaluation-lane lineage as separate additive fields so operators can see what generated candidates versus what assessed them."
  - "Evaluation-lane comparison data is sourced from the additive `llm_assessment` provenance already carried into report entries, rather than inventing a second evaluation-manifest lookup contract."
patterns-established:
  - "`llm-evaluate` now follows the same explicit request -> config -> fallback -> backend-default precedence already established for generation and launch."
  - "Compare CLI summaries now surface both generation and evaluation lane identity when specialized assessment lineage is present, while report artifacts continue to use the same standard roots."
requirements-completed: [LLM-15, LLM-16, OPS-09]
duration: 32min
completed: 2026-04-05
---

# Phase 20 Plan 02: Specialized Evaluation Compatibility Summary

**Operators can now point `llm-evaluate` at a specialized lane explicitly, prove it on `Al-Cu-Fe`, and still compare, replay, and report on that workflow without fracturing the artifact contract.**

## Performance

- **Duration:** 32 min
- **Completed:** 2026-04-05
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- Added `mdisc llm-evaluate --model-lane ...` and proved CLI precedence, explicit fallback recording, and early unavailable-lane failure entirely offline.
- Turned `configs/systems/al_cu_fe_llm_local.yaml` into the real Phase 20 proof config by declaring `llm_evaluate.model_lane: specialized_materials` while leaving generation on the normal lane contract.
- Extended campaign outcome snapshots so they now carry additive evaluation lane identity and serving identity alongside the existing generation lane fields.
- Updated compare/report tests so specialized evaluation lineage stays visible through comparison summaries and report evidence without changing artifact roots or replay hard-drift rules.

## Task Commits

1. **Task 1 + Task 2 GREEN: specialized evaluation workflow compatibility** - `98495037` `feat(20-02): add specialized evaluation workflow compatibility`

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run python -m pytest tests/test_llm_evaluate_cli.py -x -v`
  - Result: `4 passed in 0.47s`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run python -m pytest tests/test_llm_compare_core.py tests/test_llm_compare_cli.py tests/test_llm_campaign_lineage.py tests/test_llm_replay_core.py tests/test_report.py -x -v`
  - Result: `32 passed in 2.13s`
- `git diff --check`
  - Result: pending before commit

## Decisions Made

- `llm-evaluate` now records fallback honestly: if a requested specialized lane resolves through `fallback_model_lane`, the summary keeps the specialized request while the resolved lane/source show the downgrade explicitly.
- Compare outcome snapshots distinguish generation-lane lineage from evaluation-lane lineage instead of flattening them into one generic model field.
- Replay compatibility remains generation-serving-authoritative; specialized evaluation lineage is additive context and does not participate in replay hard-drift checks.

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

- Phase 20 Plan 03 can now add the thinner `Sc-Zn` proof and docs on top of a real specialized workflow surface instead of a contract-only seam.
- Phase 21 can benchmark hosted, local, and specialized lanes with explicit generation-vs-evaluation provenance already preserved in compare/report outputs.

## Self-Check

PASSED

---
*Phase: 20-specialized-lane-integration-and-workflow-compatibility*  
*Completed: 2026-04-05*
