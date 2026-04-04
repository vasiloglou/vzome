---
phase: 11-closed-loop-campaign-execution-bridge
plan: 03
subsystem: llm
tags: [llm, campaign, lineage, manifests, docs, pytest]
requires:
  - phase: 11-closed-loop-campaign-execution-bridge
    provides: approved-spec launch bridge and campaign-aware llm-generate execution
provides:
  - additive llm_campaign lineage on launched llm-generate manifests and downstream stage manifests
  - pipeline-manifest support for campaign lineage
  - offline llm-launch to screen compatibility proof and operator-facing docs for manual continuation
affects: [phase-12, report, screen, hifi-validate, hifi-rank, active-learn]
tech-stack:
  added: []
  patterns: [normalized source lineage, additive manifest propagation, offline end-to-end regression]
key-files:
  created:
    - materials-discovery/tests/test_llm_campaign_lineage.py
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/src/materials_discovery/common/pipeline_manifest.py
    - materials-discovery/tests/test_report.py
    - materials-discovery/tests/test_real_mode_pipeline.py
    - materials-discovery/developers-docs/llm-integration.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/Progress.md
key-decisions:
  - "Normalize campaign lineage once as source_lineage.llm_campaign and reuse that shape across launch, downstream stage manifests, and the pipeline manifest."
  - "Prefer launched candidate provenance for identity, then enrich it from the llm-generate manifest so launch-wrapper paths survive into later stages."
  - "Keep Phase 11 manual after launch: llm-launch writes standard artifacts, and operators continue with the normal stage commands."
patterns-established:
  - "Launched candidates and downstream manifests now share one additive lineage contract instead of each stage inventing its own campaign payload."
  - "Operator docs now describe the file-backed launch wrapper and Lineage Audit path rather than relying on code discovery."
requirements-completed: [LLM-10, OPS-06]
duration: 11min
completed: 2026-04-04
---

# Phase 11 Plan 03: Downstream Lineage and Operator Flow Summary

**Phase 11 now preserves campaign lineage beyond launch and documents how operators continue launched runs through the existing pipeline.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-04-04T16:47:00Z
- **Completed:** 2026-04-04T16:58:13Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- Added one normalized `llm_campaign` lineage shape and threaded it through launched `llm_generate` manifests, downstream stage manifests, and the final pipeline manifest.
- Added focused regressions for lineage normalization plus an offline mock proof that `llm-launch` candidates continue cleanly into `screen`.
- Documented `llm-launch`, its wrapper artifacts, the manual downstream continuation flow, failure posture, and the on-disk Lineage Audit path in the developer docs.

## Task Commits

1. **Task 1 + Task 2 GREEN: downstream lineage propagation, E2E proof, and docs** - `f1e2432a` `feat(11-03): propagate campaign lineage downstream`

## Files Created/Modified

- `materials-discovery/src/materials_discovery/cli.py` - Adds campaign-lineage normalization/merge helpers, writes launch lineage into the launched `llm_generate` manifest, and threads lineage into `screen`, `hifi-validate`, `hifi-rank`, `active-learn`, `report`, and the pipeline manifest.
- `materials-discovery/src/materials_discovery/common/pipeline_manifest.py` - Adds additive `source_lineage` support for the pipeline manifest.
- `materials-discovery/tests/test_llm_campaign_lineage.py` - Covers lineage normalization, manifest enrichment, and screen-manifest propagation.
- `materials-discovery/tests/test_report.py` - Proves report and pipeline manifests preserve campaign lineage.
- `materials-discovery/tests/test_real_mode_pipeline.py` - Adds the offline `llm-launch -> screen` compatibility regression using the committed mock config.
- `materials-discovery/developers-docs/llm-integration.md` - Documents `llm-launch`, manual continuation, failure posture, and the Lineage Audit chain.
- `materials-discovery/developers-docs/pipeline-stages.md` - Adds the full `mdisc llm-launch` command reference and downstream continuation guidance.
- `materials-discovery/Progress.md` - Logs the RED/GREEN work and verification results for Phase 11 Plan 03.

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_campaign_lineage.py tests/test_report.py -x -v`
  - Result: `16 passed`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "campaign or llm_launch" -x -v`
  - Result: `1 passed, 6 deselected`
- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
  - Result: `357 passed, 3 skipped, 1 warning`
- `git diff --check`
  - Result: clean

## Decisions Made

- `source_lineage.llm_campaign` is the only normalized downstream lineage shape for launched campaigns.
- Candidate provenance remains the preferred identity source, while the launched `llm_generate` manifest enriches that lineage with wrapper paths such as `launch_summary_path` and `resolved_launch_path`.
- Phase 11 stops at launch plus manual continuation documentation; resume, replay, and richer operator workflow remain Phase 12 work.

## Deviations from Plan

None.

## Issues Encountered

While adding the new Phase 11 tests, `test_real_mode_pipeline.py` was accidentally overwritten with a placeholder during patching. The file was restored immediately from `HEAD`, the new launch regression was appended correctly, and the full suite was rerun to confirm no unrelated tests were lost.

## User Setup Required

None. The documented Phase 11 path stays offline-compatible with the committed mock LLM config and does not require live provider access.

## Next Phase Readiness

- Phase 12 can now build replay and comparison helpers on top of a stable `campaign_spec -> llm-launch -> downstream manifests` artifact chain.
- The new operator docs provide the baseline Lineage Audit path that Phase 12 can expand into a fuller runbook.

## Self-Check

PASSED

---
*Phase: 11-closed-loop-campaign-execution-bridge*
*Completed: 2026-04-04*
