---
phase: 11-closed-loop-campaign-execution-bridge
plan: 02
subsystem: llm
tags: [llm, campaign, cli, launch, pytest]
requires:
  - phase: 11-closed-loop-campaign-execution-bridge
    provides: typed launch contracts and additive launch-resolution overlays
provides:
  - additive campaign metadata threading through the existing llm-generate runtime
  - operator-facing llm-launch command for approved campaign specs
  - failed-launch audit artifacts that preserve partial outputs instead of deleting them
affects: [11-03, llm-launch, llm-generate]
tech-stack:
  added: []
  patterns: [tdd red-green execution, wrapper-cli execution bridge, additive provenance]
key-files:
  created:
    - materials-discovery/tests/test_llm_launch_cli.py
  modified:
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/prompting.py
    - materials-discovery/src/materials_discovery/llm/generate.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_llm_generate_core.py
    - materials-discovery/tests/test_llm_generate_cli.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/Progress.md
key-decisions:
  - "Keep Phase 11 launches on the existing generate runtime by passing only additive prompt/campaign metadata into generate_llm_candidates()."
  - "Write resolved_launch.json before provider execution so config-drift or runtime failures still leave an auditable launch wrapper."
  - "Record the effective candidates path and whether --out was used on the resolved launch contract for operator traceability."
patterns-established:
  - "Campaign execution remains wrapper-based: llm-launch resolves a typed overlay, writes launch artifacts, then delegates to llm-generate."
  - "Launched candidates retain standard CandidateRecord outputs plus an additive llm_campaign provenance block."
requirements-completed: [LLM-08, LLM-10, OPS-06]
duration: 6min
completed: 2026-04-04
---

# Phase 11 Plan 02: Campaign Execution Bridge Summary

**Phase 11 can now execute approved campaign specs through `mdisc llm-launch` without creating a second generation path or breaking manual `llm-generate`.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-04T16:42:00Z
- **Completed:** 2026-04-04T16:47:52Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Extended the existing `llm-generate` runtime with additive prompt instruction deltas, launch-aware run-manifest fields, and additive `llm_campaign` provenance on generated candidates.
- Added `mdisc llm-launch --campaign-spec ...` as the operator-facing bridge from approved specs into the existing generation runtime.
- Locked the launch behavior with focused CLI regression coverage for success, missing-spec handling, and config-hash drift failures before moving on to downstream lineage propagation.

## Task Commits

1. **Task 1 RED: campaign-aware llm-generate tests** - `8d8fe234` `test(11-02): add failing test for campaign-aware llm-generate`
2. **Task 1 GREEN: additive generate metadata** - `7cec5572` `feat(11-02): add campaign-aware llm-generate metadata`
3. **Task 2 RED: llm-launch CLI tests** - `766d0789` `test(11-02): add failing test for llm-launch cli`
4. **Task 2 GREEN: llm-launch execution bridge** - `c6ae7024` `feat(11-02): add llm-launch execution bridge`

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/schema.py` - Adds additive launch result fields on `LlmCampaignResolvedLaunch` plus campaign-aware generation/run-manifest metadata.
- `materials-discovery/src/materials_discovery/llm/prompting.py` - Threads deterministic instruction deltas into prompt assembly.
- `materials-discovery/src/materials_discovery/llm/generate.py` - Accepts additive campaign metadata, records `llm_campaign` provenance, and avoids run-hash collisions across different launch overlays.
- `materials-discovery/src/materials_discovery/cli.py` - Adds `mdisc llm-launch`, config-hash drift validation, launch artifact writing, and failed-launch summary emission.
- `materials-discovery/tests/test_llm_generate_core.py` - Covers additive launch metadata on the existing generation path.
- `materials-discovery/tests/test_llm_generate_cli.py` - Keeps the manual generate CLI path green while covering the additive request surface.
- `materials-discovery/tests/test_llm_launch_cli.py` - Covers successful launch, artifact writing, and config-drift failure behavior.
- `materials-discovery/tests/test_cli.py` - Adds shared CLI regression coverage for missing campaign specs.
- `materials-discovery/Progress.md` - Logs the RED/GREEN execution trail for Phase 11 Plan 02.

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py -x -v`
  - Result: `14 passed`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_launch_cli.py tests/test_cli.py -x -v`
  - Result: `13 passed`

## Decisions Made

- `llm-launch` remains a thin wrapper: it validates config drift, resolves a deterministic launch overlay, writes launch artifacts, and delegates actual generation to `generate_llm_candidates()`.
- Config-drift failures surface pinned/current hash detail and re-approval guidance before any runtime adapter is touched.
- Launch wrapper artifacts record both the resolved lane source and the effective candidate output path so later lineage work can trace exact launch conditions.

## Deviations from Plan

None.

## Issues Encountered

None beyond the expected RED-to-GREEN test failures during TDD.

## User Setup Required

None. The new launch path stays offline-compatible with the mock LLM provider and the committed system configs.

## Next Phase Readiness

- Phase 11 Plan 03 can now propagate campaign lineage from launch wrappers and launched candidate provenance into downstream stage manifests.
- The new `llm-launch` CLI provides a stable bridge for the end-to-end mock regression and docs updates in Wave 3.

## Self-Check

PASSED

---
*Phase: 11-closed-loop-campaign-execution-bridge*
*Completed: 2026-04-04*
