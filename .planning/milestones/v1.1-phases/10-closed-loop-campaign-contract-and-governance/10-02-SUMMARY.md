---
phase: 10-closed-loop-campaign-contract-and-governance
plan: 02
subsystem: api
tags: [python, typer, pytest, llm, campaign-governance, dry-run]
requires:
  - phase: 10-closed-loop-campaign-contract-and-governance
    provides: typed Phase 10 campaign schema and deterministic acceptance-pack artifact helpers from Plan 01
provides:
  - acceptance-pack to typed campaign-proposal mapping with deterministic proposal and action IDs
  - llm-suggest bundle writing plus per-system proposal artifacts rooted at the acceptance-pack directory
  - focused core and CLI regression coverage for the typed llm-suggest contract
affects: [11-closed-loop-campaign-execution-bridge, llm-suggest, campaign-approval, replay]
tech-stack:
  added: []
  patterns: [tdd red-green commits, thin CLI orchestration, deterministic dry-run campaign artifacts]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/campaigns.py
    - materials-discovery/tests/test_llm_suggest_core.py
    - materials-discovery/tests/test_llm_suggest_cli.py
  modified:
    - materials-discovery/src/materials_discovery/llm/suggest.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_llm_acceptance_benchmarks.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/Progress.md
key-decisions:
  - "Move acceptance-pack to proposal mapping into llm/campaigns.py while keeping suggest.py responsible for directory creation and JSON writing."
  - "Proposal artifacts always live under the acceptance-pack sibling proposals/ directory, even when the suggestion bundle uses a custom --out path."
  - "CLI prints the persisted typed bundle JSON so stdout matches the on-disk contract exactly."
patterns-established:
  - "Each acceptance-pack system maps to one dry-run proposal with deterministic proposal_id and per-proposal action_id values."
  - "Dry-run CLI commands delegate artifact writing to llm helpers instead of creating proposal files inline in cli.py."
requirements-completed: [LLM-06, OPS-05]
duration: 7min
completed: 2026-04-04
---

# Phase 10 Plan 02: Typed llm-suggest Bundle Summary

**Typed acceptance-pack campaign bundles with deterministic per-system proposal artifacts and a dry-run llm-suggest CLI contract**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-04T01:44:14-04:00
- **Completed:** 2026-04-04T01:50:54-04:00
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- Added `llm/campaigns.py` to map typed acceptance-pack evidence into one system-scoped `LlmCampaignProposal` per system, including deterministic proposal IDs, deterministic action IDs, and action-family routing across parse/compile, pass-through, synthesizability, release-gate, and healthy-system cases.
- Migrated `llm/suggest.py` from the legacy `LlmSuggestion` surface to the typed `LlmCampaignSuggestion` bundle and made it responsible for writing both `suggestions.json` and sibling `proposals/{proposal_id}.json` artifacts.
- Updated the `mdisc llm-suggest` CLI and shared callers/tests so the command stays dry-run, prints the typed bundle JSON, writes proposal artifacts under the acceptance-pack root, and preserves exit-2 behavior for invalid acceptance-pack input.

## Task Commits

Each task was committed atomically through TDD red/green commits:

1. **Task 1: Map acceptance-pack evidence into typed system-scoped proposals** - `c2068555` (test), `f6590524` (feat)
2. **Task 2: Update the llm-suggest CLI to emit dry-run proposal artifacts** - `f72f76d2` (test), `ab3a029d` (feat)

Plan metadata is recorded in the final docs commit for this summary and planning-state update.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/campaigns.py` - New acceptance-pack to proposal mapper and proposal-summary builder.
- `materials-discovery/src/materials_discovery/llm/suggest.py` - Typed bundle orchestration and proposal-artifact writing rooted at the acceptance-pack directory.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Public exports for the new campaign helper surface.
- `materials-discovery/src/materials_discovery/cli.py` - Updated `mdisc llm-suggest` to write typed bundle/proposal artifacts and print the persisted bundle JSON.
- `materials-discovery/tests/test_llm_suggest_core.py` - Focused core coverage for proposal mapping, deterministic IDs, specialized-materials routing, and summary paths.
- `materials-discovery/tests/test_llm_suggest_cli.py` - Focused CLI coverage for typed stdout, default artifact writing, and invalid-input handling.
- `materials-discovery/tests/test_llm_acceptance_benchmarks.py` - In-repo caller migration away from the legacy `LlmSuggestion` contract.
- `materials-discovery/tests/test_cli.py` - Shared CLI regression updated to the typed bundle output contract.
- `materials-discovery/Progress.md` - Required changelog and diary entries for both Task 1 and Task 2 RED/GREEN steps.

## Decisions Made

- Kept the proposal-building heuristics in a dedicated `llm/campaigns.py` module so the Phase 10 core mapping logic is reusable by future approval/spec work without bloating `cli.py`.
- Kept `suggest.py` as the write-owner for the bundle and per-proposal artifacts so the CLI remains a thin load/validate/emit layer.
- Printed the persisted suggestion bundle from disk in the CLI so stdout and written JSON stay aligned even when the writer controls timestamps.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 11 can now consume typed per-system proposal artifacts instead of plain-language suggestions when adding approval and launch bridging.
- The dry-run/operator-governed boundary remains intact: `llm-suggest` writes only bundle/proposal artifacts and does not touch configs, generation inputs, or active-learning outputs.

## Self-Check

PASSED
