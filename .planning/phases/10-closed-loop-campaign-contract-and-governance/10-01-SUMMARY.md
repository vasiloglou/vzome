---
phase: 10-closed-loop-campaign-contract-and-governance
plan: 01
subsystem: api
tags: [pydantic, pytest, llm, campaign-governance, file-backed]
requires:
  - phase: 09-fine-tuned-zomic-model-and-closed-loop-design
    provides: typed acceptance packs, eval-set lineage, and dry-run llm-suggest inputs
provides:
  - typed Phase 10 campaign proposal, approval, suggestion, lineage, and campaign-spec contracts
  - deterministic acceptance-pack and campaign artifact path helpers
  - focused schema and storage regression coverage for the new governance surface
affects: [11-closed-loop-campaign-execution-bridge, 12-replay-comparison-and-operator-workflow, llm-suggest]
tech-stack:
  added: []
  patterns: [additive pydantic contracts, deterministic artifact path helpers, tdd red-green commits]
key-files:
  created:
    - materials-discovery/tests/test_llm_campaign_schema.py
    - materials-discovery/tests/test_llm_campaign_storage.py
  modified:
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/storage.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Keep the Phase 10 campaign contracts additive inside llm/schema.py instead of splitting files during this phase."
  - "Validate campaign-action payload matching with an explicit model_validator rather than a discriminated-union refactor."
  - "Keep proposals and approvals under the acceptance-pack root while campaign specs live under data/llm_campaigns/{campaign_id}."
  - "Make blank artifact identifiers fail fast in storage helpers instead of normalizing into malformed paths."
patterns-established:
  - "Campaign actions carry one family-specific optional payload field and validate the matching payload after model construction."
  - "Campaign governance artifacts stay file-backed and deterministic, with acceptance-pack lineage separated from long-lived campaign roots."
requirements-completed: [LLM-06, OPS-05]
duration: 8min
completed: 2026-04-04
---

# Phase 10 Plan 01: Governance Contract Foundation Summary

**Typed Phase 10 campaign proposal, approval, suggestion, and campaign-spec contracts with deterministic acceptance-pack and campaign artifact paths**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-04T05:28:36Z
- **Completed:** 2026-04-04T05:37:07Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- Added the additive Phase 10 governance schema family in `llm/schema.py`, including typed action payloads, system-scoped proposals, separate approvals, launch baselines, lineage, and self-contained campaign specs.
- Added deterministic storage helpers for suggestion, proposal, approval, and campaign-spec artifacts while preserving the existing acceptance-pack helpers.
- Added focused pytest coverage that locks the payload-validation rules and on-disk artifact layout for later Phase 10-12 work.

## Task Commits

Each task was committed atomically through TDD red/green commits:

1. **Task 1: Add typed campaign governance models to llm/schema.py** - `74fd039f` (test), `aac010ad` (feat)
2. **Task 2: Add deterministic storage helpers for suggestion, proposal, approval, and spec artifacts** - `0333ea1d` (test), `4de3bd3d` (feat)

Plan metadata is recorded in the final docs commit for this summary and planning-state update.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/schema.py` - Adds the Phase 10 campaign contract family and validators.
- `materials-discovery/src/materials_discovery/llm/storage.py` - Adds deterministic proposal, approval, suggestion, and campaign-spec artifact helpers.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Exports the new campaign models, constants, and storage helpers.
- `materials-discovery/tests/test_llm_campaign_schema.py` - Covers schema validation for actions, proposals, approvals, suggestions, and specs.
- `materials-discovery/tests/test_llm_campaign_storage.py` - Covers deterministic artifact roots and blank-ID rejection.
- `materials-discovery/Progress.md` - Logs the RED/GREEN work for both Task 1 and Task 2 per repo policy.

## Decisions Made

- Kept the new Phase 10 campaign types additive inside `llm/schema.py` because the plan explicitly defers any schema split.
- Used an explicit `model_validator(mode="after")` on `LlmCampaignAction` to require the payload that matches each action family and reject non-matching payloads.
- Enforced separate roots for acceptance-pack artifacts versus campaign specs so Phase 11 can materialize launches without overloading the acceptance-pack directory.
- Enforced fast failure on blank artifact identifiers in storage helpers to prevent malformed paths from propagating into later commands.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Cleared a stale git index lock before the Task 2 GREEN commit**
- **Found during:** Task 2 (Add deterministic storage helpers for suggestion, proposal, approval, and spec artifacts)
- **Issue:** A concurrent git status/commit invocation left `.git/index.lock`, blocking the required commit.
- **Fix:** Removed the stale lock and retried the commit sequentially.
- **Files modified:** None
- **Verification:** The retry succeeded and produced commit `4de3bd3d`.
- **Committed in:** `4de3bd3d`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope creep. The fix only restored the normal commit path after a transient repository lock.

## Issues Encountered

None beyond the transient git lock noted above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 10 now has durable schema and storage foundations for revising `llm-suggest` to materialize typed proposal bundles.
- Phase 11 can build approval/spec materialization and launch bridging on top of stable proposal, approval, and campaign artifact identities.

## Self-Check

PASSED

---
*Phase: 10-closed-loop-campaign-contract-and-governance*
*Completed: 2026-04-04*
