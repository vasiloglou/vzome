---
phase: 10-closed-loop-campaign-contract-and-governance
plan: 03
subsystem: cli
tags: [llm, governance, typer, pydantic, pytest, docs]
requires:
  - phase: 10-closed-loop-campaign-contract-and-governance
    provides: typed proposals, approvals, storage helpers, and dry-run llm-suggest bundles
provides:
  - deterministic approval and campaign-spec materialization helpers
  - non-launching `mdisc llm-approve` CLI command with explicit governance boundary
  - additive docs and regression coverage for approval/spec artifact flow
affects: [11-closed-loop-campaign-execution-bridge, 12-replay-comparison-and-operator-workflow, llm-suggest]
tech-stack:
  added: []
  patterns: [deterministic artifact ids, file-backed governance boundary, tdd red-green verification]
key-files:
  created:
    - materials-discovery/tests/test_llm_campaign_spec.py
    - materials-discovery/tests/test_llm_approve_cli.py
  modified:
    - materials-discovery/src/materials_discovery/llm/campaigns.py
    - materials-discovery/src/materials_discovery/llm/storage.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/developers-docs/llm-integration.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/tests/test_cli.py
    - materials-discovery/Progress.md
key-decisions:
  - "Derive campaign IDs deterministically from proposal plus approval identity so re-approval preserves prior specs instead of overwriting them."
  - "Keep `llm-approve` as a pure artifact-materialization command; it may pin launch baselines but must not call `llm-generate` or `llm-evaluate`."
  - "Resolve the campaign artifact root from the acceptance-pack path so approvals stay under the pack root while campaign specs remain under `data/llm_campaigns/`."
patterns-established:
  - "Closed-loop governance is now a two-step file-backed boundary: dry-run proposals first, explicit approval/spec materialization second."
  - "Approved proposals require a config-backed launch baseline snapshot; rejected proposals stop at the approval artifact."
requirements-completed: [LLM-06, OPS-05]
duration: 3min
completed: 2026-04-04
---

# Phase 10 Plan 03: Approval and Spec Governance Summary

**The Phase 10 governance boundary now materializes separate approval artifacts and self-contained campaign specs without launching downstream LLM execution.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-04T14:56:00Z
- **Completed:** 2026-04-04T14:59:00Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Added `create_campaign_approval()` and `materialize_campaign_spec()` so typed dry-run proposals can become explicit approvals and self-contained campaign specs with pinned config lineage.
- Added `mdisc llm-approve` to materialize those artifacts from the CLI while explicitly stopping before any `llm-generate`, `llm-evaluate`, or candidate-writing work.
- Refreshed the LLM developer docs and added focused plus shared CLI regression coverage, then re-verified the whole `materials-discovery` suite.

## Task Commits

1. **Plan 03 implementation:** `3d29bc45` `feat(10-03): add llm approval governance boundary`

Plan metadata and execution-state updates are recorded in the final docs commit for this summary.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/campaigns.py` - Adds deterministic approval and campaign-spec materialization helpers.
- `materials-discovery/src/materials_discovery/llm/storage.py` - Adds acceptance-pack-root artifact-root derivation for approval/spec placement.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Exports the new governance helper surface.
- `materials-discovery/src/materials_discovery/cli.py` - Adds the non-launching `mdisc llm-approve` command and JSON summary output.
- `materials-discovery/tests/test_llm_campaign_spec.py` - Covers approved, rejected, deterministic, and re-approval spec flows.
- `materials-discovery/tests/test_llm_approve_cli.py` - Covers CLI success, validation failures, and non-launch behavior.
- `materials-discovery/tests/test_cli.py` - Adds a shared smoke case for `llm-approve`.
- `materials-discovery/developers-docs/llm-integration.md` - Documents the new dry-run vs approval/spec governance boundary.
- `materials-discovery/developers-docs/pipeline-stages.md` - Documents `mdisc llm-approve` and updates `llm-suggest` artifact semantics.
- `materials-discovery/Progress.md` - Logs the Phase 10 Plan 03 RED/GREEN work and the final full-suite verification result.

## Verification

Focused checks:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_campaign_spec.py -x -v`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_approve_cli.py tests/test_cli.py -x -v`

Full regression sweep:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
  - Result: `332 passed, 3 skipped, 1 warning`

## Decisions Made

- Approval IDs are deterministic from proposal, decision, operator, timestamp, and notes; approved campaign IDs are deterministic from proposal and approval identity.
- `llm-approve` requires `--config` only for approved decisions so the resulting campaign spec can pin a launch baseline snapshot and config hash.
- Artifact placement is rooted in the acceptance-pack path to keep approvals near the proposal bundle while still placing campaign specs under `data/llm_campaigns/{campaign_id}/`.

## Deviations from Plan

None.

## Issues Encountered

The original Wave 3 executor agent stalled without producing files or commits, so Plan 03 was completed locally after confirming there was no agent-produced work to preserve.

## User Setup Required

None. `llm-approve` is file-backed and uses existing system configs; no new provider secrets or services are required in Phase 10.

## Next Phase Readiness

- Phase 11 can now treat campaign specs as the single source of truth for launching closed-loop runs.
- Replay and comparison work in Phase 12 can key directly off approval IDs and campaign IDs without rereading the original suggestion heuristics.

## Self-Check

PASSED

---
*Phase: 10-closed-loop-campaign-contract-and-governance*
*Completed: 2026-04-04*
