---
phase: 12-replay-comparison-and-operator-workflow
plan: 01
subsystem: llm
tags: [llm, replay, compare, schema, storage, pytest]
requires:
  - phase: 11-closed-loop-campaign-execution-bridge
    provides: launch summaries, resolved launches, campaign specs, and run manifests
provides:
  - typed replay/comparison contracts and deterministic campaign storage helpers
  - strict launch-bundle loading and replay-config reconstruction
  - deterministic outcome snapshots and prior-launch baseline selection
affects: [milestone-v1.1-closeout, llm-launch, llm-replay, llm-compare]
tech-stack:
  added: []
  patterns:
    [
      typed JSON audit artifacts,
      strict replay bundle authority,
      deterministic prior-launch comparison baselines,
    ]
key-files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/storage.py
    - materials-discovery/src/materials_discovery/llm/replay.py
    - materials-discovery/src/materials_discovery/llm/compare.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/tests/test_llm_replay_core.py
    - materials-discovery/tests/test_llm_compare_core.py
    - materials-discovery/Progress.md
key-decisions:
  - "Replay is bundle-driven: launch_summary.json is the entrypoint, but strict replay requires resolved_launch.json, campaign_spec.json, run_manifest.json, and prompt.json to agree."
  - "Outcome snapshots preserve missing downstream metrics explicitly instead of coercing absent stage evidence to zero."
  - "Prior-launch comparison is deterministic: it orders by created_at_utc and then launch_id for ties."
patterns-established:
  - "Replay and compare both rely on typed JSON artifacts instead of ad hoc dicts so later CLI and audit layers can reuse the same proof surface."
  - "Phase 12 proof is cumulative: this summary establishes the replay/compare foundations that [12-02-SUMMARY.md](./12-02-SUMMARY.md) and [12-03-SUMMARY.md](./12-03-SUMMARY.md) build on."
requirements-completed: [LLM-09, LLM-11]
duration: 5min
completed: 2026-04-04
---

# Phase 12 Plan 01: Replay and Comparison Foundations Summary

**Phase 12 started by freezing replay and comparison around durable launch-bundle truth, typed storage contracts, and deterministic baseline selection.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-04T17:25:00Z
- **Completed:** 2026-04-04T17:30:02Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Added additive replay-lineage fields plus typed `LlmCampaignOutcomeSnapshot` and `LlmCampaignComparisonResult` contracts so replay and comparison artifacts have stable JSON schemas.
- Added deterministic campaign storage helpers for launch-local `outcome_snapshot.json` and campaign-level comparison artifacts under `data/llm_campaigns/{campaign_id}/comparisons/`.
- Implemented strict launch-bundle loading and replay-config reconstruction in `replay.py`, including recorded runtime preservation and mismatch rejection for system or template drift.
- Implemented outcome snapshot collection and prior-launch selection in `compare.py`, including explicit `missing_metrics` tracking and acceptance-pack baseline reuse.

## Task Commits

1. **Plan 01 implementation:** `5ac1a3f1` `feat(12-01): add replay and comparison foundations`

Plan metadata and the retroactive audit-chain restoration are recorded separately in Phase 15 closure commits.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/schema.py` - Adds replay-lineage fields plus the typed outcome-snapshot and comparison-result models.
- `materials-discovery/src/materials_discovery/llm/storage.py` - Adds deterministic snapshot and comparison artifact paths under the existing campaign storage tree.
- `materials-discovery/src/materials_discovery/llm/replay.py` - Loads strict launch bundles and rebuilds replay configs from recorded launch-time inputs.
- `materials-discovery/src/materials_discovery/llm/compare.py` - Builds outcome snapshots, finds deterministic prior launches, and computes deltas versus acceptance-pack and prior-launch baselines.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Re-exports the new replay/comparison contracts and helpers.
- `materials-discovery/tests/test_llm_replay_core.py` - Covers additive replay fields, storage helpers, strict bundle loading, preserved runtime inputs, and mismatch rejection.
- `materials-discovery/tests/test_llm_compare_core.py` - Covers snapshot persistence, explicit missing metrics, deterministic prior-launch resolution, and comparison deltas.
- `materials-discovery/Progress.md` - Logged the original Plan 01 implementation and verification when Phase 12 shipped.

## Verification

Original focused verification during Phase 12 execution:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py -x -v`
  - Result at ship time: green

Retroactive audit refresh during Phase 15:

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py -x -v`
  - Result: `10 passed in 0.19s`

## Decisions Made

- Launch artifacts, not approval-time intent, are the replay authority.
- Comparison is allowed to be incomplete, but incompleteness must be explicit through `missing_metrics`.
- Prior-launch selection is deterministic so replay/compare audits do not depend on filesystem ordering accidents.

## Deviations from Plan

None.

## Issues Encountered

None. The focused replay/compare foundation tests still pass cleanly under the Phase 15 audit refresh.

## User Setup Required

None. The replay/comparison foundation remains offline and mock-friendly.

## Next Phase Readiness

- [12-02-SUMMARY.md](./12-02-SUMMARY.md) closes the CLI/operator proof on top of these foundations.
- [12-03-SUMMARY.md](./12-03-SUMMARY.md) closes the end-to-end operator workflow, docs, and full-suite evidence.

Together, [12-01-SUMMARY.md](./12-01-SUMMARY.md), [12-02-SUMMARY.md](./12-02-SUMMARY.md), and [12-03-SUMMARY.md](./12-03-SUMMARY.md) form the full Phase 12 audit chain.

## Self-Check

PASSED

---
*Phase: 12-replay-comparison-and-operator-workflow*
*Completed: 2026-04-04*
