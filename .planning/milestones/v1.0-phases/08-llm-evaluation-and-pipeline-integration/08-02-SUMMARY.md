---
phase: 08-llm-evaluation-and-pipeline-integration
plan: 02
subsystem: llm-assessment-reporting
tags: [llm, report, ranking, calibration, additive-context]
requires:
  - phase: 08-llm-evaluation-and-pipeline-integration
    provides: llm-evaluate artifacts and candidate provenance blocks
provides:
  - report preference for all-candidate llm_evaluated artifacts
  - additive llm assessment context in report entries and evidence
  - regression proof that hifi-rank preserves but does not reweight llm assessment
affects: [phase-08, report, rank, benchmarking, calibration]
tech-stack:
  added: [llm assessment calibration metrics, enriched report evidence, ranked/report fallback logic]
  patterns: [all-candidate artifact preference, additive downstream context, explicit no-rerank guarantee]
key-files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/common/stage_metrics.py
    - materials-discovery/src/materials_discovery/diffraction/compare_patterns.py
    - materials-discovery/src/materials_discovery/hifi_digital/rank_candidates.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_report.py
    - materials-discovery/tests/test_hifi_rank.py
    - materials-discovery/Progress.md
key-decisions:
  - "Only the all-candidate llm_evaluated artifact is preferred by report; partial topN evaluation outputs do not silently shrink the report lane."
  - "LLM assessment stays additive in report entries, evidence, and calibration metrics instead of entering the ranking formula."
  - "The no-rerank policy is enforced both in code comments and in score/order invariance tests."
patterns-established:
  - "Report path preference: llm_evaluated/{system}_all_llm_evaluated.jsonl -> ranked/{system}_ranked.jsonl fallback."
  - "Phase 8 report summaries now surface llm_assessed_count, llm_anomaly_flagged_count, and llm_synthesizability_mean."
requirements-completed: [LLM-03]
duration: 16min
completed: 2026-04-03
---

# Phase 8: Plan 02 Summary

**Thread LLM assessment into report context without changing rank scores**

## Performance

- **Duration:** 16 min
- **Completed:** 2026-04-04T00:42:00Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Taught `mdisc report` to prefer the additive `*_all_llm_evaluated.jsonl` artifact when it exists, while keeping the ranked JSONL path as the normal fallback.
- Extended `compile_experiment_report()` so report entries and evidence blocks surface `llm_assessment` when present, and so report summaries capture aggregate LLM evaluation metrics.
- Extended `report_calibration()` with additive LLM-assessment counts and means for downstream comparison and benchmarking work.
- Locked the Phase 8 ranking policy in `rank_validated_candidates()`: existing `llm_assessment` provenance is preserved, but never changes rank scores.
- Added focused regressions that prove both the enriched report path and the no-rerank guarantee.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/common/stage_metrics.py` - additive LLM assessment calibration metrics
- `materials-discovery/src/materials_discovery/diffraction/compare_patterns.py` - report entry/evidence enrichment and summary aggregates
- `materials-discovery/src/materials_discovery/hifi_digital/rank_candidates.py` - explicit no-rerank contract note
- `materials-discovery/src/materials_discovery/cli.py` - report-time preference for `*_all_llm_evaluated.jsonl`
- `materials-discovery/tests/test_report.py` - report enrichment and artifact-preference coverage
- `materials-discovery/tests/test_hifi_rank.py` - score/order invariance coverage with llm assessment context
- `materials-discovery/Progress.md` - required materials-discovery progress update

## Decisions Made

- Limited report preference to the `all` evaluation artifact so the report stage never silently switches from a full ranked lane to a partial topN lane.
- Kept `llm_assessment` as visible report evidence and calibration metadata, not a latent scoring input.
- Chose explicit regression tests over implicit trust so future phases can safely build richer evaluation logic without reintroducing hidden reranking.

## Deviations from Plan

- None. The additive metrics helper, report integration, and regression proof all landed in the planned file set.

## Verification

- `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_report.py tests/test_hifi_rank.py -x -v`
- `git diff --check`

## Next Phase Readiness

Plan 03 can now benchmark deterministic vs LLM lanes through the downstream pipeline using report outputs that already expose additive LLM assessment context.

---
*Phase: 08-llm-evaluation-and-pipeline-integration*
*Completed: 2026-04-03*
