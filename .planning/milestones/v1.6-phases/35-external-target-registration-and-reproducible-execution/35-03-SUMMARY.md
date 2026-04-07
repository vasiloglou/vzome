---
phase: 35-external-target-registration-and-reproducible-execution
plan: 03
subsystem: llm
tags: [external-targets, cli, docs, runbook, llm]
requires:
  - phase: 35-external-target-registration-and-reproducible-execution
    provides: persisted external-target registration, environment, and smoke artifacts
provides:
  - operator CLI commands for external target register, inspect, and smoke workflows
  - committed example CIF and material-string target specs for the Phase 35 contract
  - operator-facing docs that explain artifact layout and the Phase 36 boundary
affects: [35-phase-verification, 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards]
tech-stack:
  added: []
  patterns:
    - external-target CLI commands reuse the repo's standard JSON-or-human-readable output split and exit-code-2 failure posture
    - external target example specs are standalone YAML contracts rather than new SystemConfig fields
key-files:
  created:
    - materials-discovery/tests/test_llm_external_target_cli.py
    - materials-discovery/configs/llm/al_cu_fe_external_cif_target.yaml
    - materials-discovery/configs/llm/al_cu_fe_external_material_string_target.yaml
    - materials-discovery/developers-docs/llm-external-target-runbook.md
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/developers-docs/configuration-reference.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/developers-docs/index.md
    - materials-discovery/Progress.md
key-decisions:
  - "Inspect stays human-readable while register and smoke return typed JSON so operators can both script and quickly eyeball target readiness."
  - "Example external-target specs are templates with explicit placeholder snapshot paths instead of pretending the repo already ships runnable third-party weights."
patterns-established:
  - "Phase 35 CLI commands stop at registration and smoke persistence; comparative benchmark execution remains explicitly deferred to Phase 36."
  - "Docs now present external target registration beside translated-benchmark freeze and checkpoint lifecycle workflows as one adjacent operator path."
requirements-completed: [OPS-17]
duration: 12 min
completed: 2026-04-07
---

# Phase 35 Plan 03: External Target Operator Workflow Summary

**Operator CLI, example specs, and runbook coverage for registering, inspecting, and smoke-testing external benchmark targets**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-07T07:12:00Z
- **Completed:** 2026-04-07T07:23:36Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Added `mdisc llm-register-external-target`, `mdisc llm-inspect-external-target`, and `mdisc llm-smoke-external-target` so operators can exercise the Phase 35 registry surface without writing custom Python.
- Added committed CIF and material-string example target specs plus a dedicated runbook that explains required snapshot inputs, artifact layout, and the immutable-versus-mutable target boundary.
- Refreshed the docs map, configuration reference, and pipeline command reference so the new workflow is discoverable next to translated benchmark packs and checkpoint lifecycle guidance.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add CLI register, inspect, and smoke commands for external targets** - `45b7f222` (feat)
2. **Task 2: Add example target specs and operator documentation for the Phase 35 workflow** - `486c3254` (docs)

## Files Created/Modified

- `materials-discovery/src/materials_discovery/cli.py` - Added the external-target register, inspect, and smoke commands.
- `materials-discovery/tests/test_llm_external_target_cli.py` - Added focused CLI coverage for real registration, inspect, smoke, and failure paths.
- `materials-discovery/tests/test_cli.py` - Locked root-help discoverability for the new commands.
- `materials-discovery/configs/llm/al_cu_fe_external_cif_target.yaml` - Added a CIF-oriented example external-target spec template.
- `materials-discovery/configs/llm/al_cu_fe_external_material_string_target.yaml` - Added a material-string-oriented example external-target spec template.
- `materials-discovery/developers-docs/llm-external-target-runbook.md` - Documented the Phase 35 operator workflow and artifact layout.
- `materials-discovery/developers-docs/configuration-reference.md` - Added the standalone external-target spec contract and scope notes.
- `materials-discovery/developers-docs/pipeline-stages.md` - Added command reference entries for the new CLI surface and updated the side-branch flow narrative.
- `materials-discovery/developers-docs/index.md` - Added the new commands to the stage table and linked the runbook from the docs map.
- `materials-discovery/Progress.md` - Logged both Plan 35 Plan 03 task slices per repo policy.

## Decisions Made

- Kept the inspect command human-readable so operators can quickly trace immutable identity and readiness artifacts without parsing JSON.
- Used example specs with explicit placeholder snapshot paths rather than shipping fake repo-backed model weights or implying a download flow that does not exist yet.
- Threaded the Phase 36 boundary through the runbook and reference docs so registration and smoke do not blur into comparative benchmark execution prematurely.

## Deviations from Plan

None.

## Issues Encountered

None.

## User Setup Required

Replace the placeholder snapshot paths and revisions in the example YAML files with a real downloaded model snapshot before running the new CLI commands against those examples.

## Next Phase Readiness

Phase 35 is now operator-usable end to end: a user can register one external target, inspect immutable identity plus readiness artifacts, and run the smoke path from the CLI. Phase verification can now confirm the full external-target handoff surface before Phase 36 begins comparative execution and scorecard work.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/35-external-target-registration-and-reproducible-execution/35-03-SUMMARY.md`
- Key files verified: `materials-discovery/src/materials_discovery/cli.py`, `materials-discovery/tests/test_llm_external_target_cli.py`, `materials-discovery/developers-docs/llm-external-target-runbook.md`
- Verification passed: `uv run pytest tests/test_llm_external_target_cli.py tests/test_cli.py -x -v`
- Task commits verified: `45b7f222`, `486c3254`
