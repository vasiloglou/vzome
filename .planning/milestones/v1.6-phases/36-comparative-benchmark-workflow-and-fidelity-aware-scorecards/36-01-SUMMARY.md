---
phase: 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards
plan: 01
subsystem: llm
tags: [external-benchmark, schema, storage, pydantic, llm]
requires:
  - phase: 34-benchmark-pack-and-freeze-contract
    provides: frozen translated benchmark-set manifest and included-row lineage
  - phase: 35-external-target-registration-and-reproducible-execution
    provides: immutable external-target registrations and reproducibility artifacts
provides:
  - typed Phase 36 benchmark spec, target, case-result, run-manifest, delta, and summary contracts
  - deterministic llm_external benchmark artifact paths
  - focused schema and storage regression coverage for the new benchmark artifact family
affects: [36-02-plan, 36-03-plan, 36-phase-verification]
tech-stack:
  added: []
  patterns:
    - external-vs-internal translated benchmarks use typed target variants instead of one ambiguous target blob
    - benchmark artifacts live under a dedicated llm_external benchmark root with deterministic per-target files
key-files:
  created:
    - materials-discovery/tests/test_llm_external_benchmark_schema.py
  modified:
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/storage.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Phase 36 benchmark specs require both external targets and internal controls so scorecards always have an explicit control arm."
  - "Benchmark summaries and case-result rows preserve target-family and fidelity-tier slices directly in the contract instead of reconstructing them later."
patterns-established:
  - "The llm_external benchmark artifact family uses benchmark_summary.json, scorecard_by_case.jsonl, and per-target run_manifest.json / case_results.jsonl / raw_responses.jsonl paths."
  - "Internal control identity is part of the benchmark contract through a dedicated control-role field rather than being hidden in free-form notes."
requirements-progressed: [LLM-32, LLM-33]
duration: 7 min
completed: 2026-04-07
---

# Phase 36 Plan 01: Comparative Benchmark Contract Summary

**Typed comparative benchmark contracts and deterministic `llm_external` storage paths for Phase 36**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-07T07:51:00Z
- **Completed:** 2026-04-07T07:58:18Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added typed Phase 36 benchmark models for explicit external targets, internal
  controls, per-case results, per-target run manifests, slice summaries,
  control deltas, and benchmark summaries.
- Added deterministic `data/benchmarks/llm_external/{benchmark_id}/` storage
  helpers for benchmark-level and per-target artifacts.
- Added focused schema and storage regression coverage that locks the new
  benchmark artifact family before benchmark execution logic is implemented.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/schema.py` - Added Phase 36
  benchmark-spec, case-result, run-manifest, slice-summary, control-delta, and
  summary models.
- `materials-discovery/src/materials_discovery/llm/storage.py` - Added
  deterministic `llm_external` benchmark path helpers for benchmark-level and
  per-target artifacts.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Re-exported
  the new benchmark contract models, constants, and storage helpers.
- `materials-discovery/tests/test_llm_external_benchmark_schema.py` - Locked
  validator and storage behavior for the new Phase 36 contract.
- `materials-discovery/Progress.md` - Logged the Plan 36-01 contract and
  storage changes per repo policy.

## Validation

- Focused verification command:
  `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_schema.py -x -v`
- Result: `7 passed in 0.28s`

## Decisions Made

- Required both external targets and internal controls in the benchmark spec so
  later scorecards always have an explicit control arm.
- Preserved `target_family`, `fidelity_tier`, `loss_reasons`, and
  `diagnostic_codes` directly in the case-result contract so the summary layer
  cannot silently collapse fidelity boundaries.
- Reserved a dedicated `llm_external` benchmark artifact family instead of
  overloading Phase 34 benchmark-set directories or Phase 35 external-target
  roots.

## Deviations from Plan

None.

## Issues Encountered

- One temporary export-name mismatch in `materials_discovery.llm` surfaced
  while wiring the new run-manifest class; it was corrected before the focused
  schema suite ran.

## User Setup Required

None for Plan 01. This slice is contract and storage only.

## Next Phase Readiness

Plan 02 can now implement benchmark execution and scorecard aggregation
directly against a stable schema and deterministic artifact layout. The next
slice can focus on loading frozen benchmark manifests, resolving registered
targets and internal controls, and writing per-target results without further
contract churn.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/36-comparative-benchmark-workflow-and-fidelity-aware-scorecards/36-01-SUMMARY.md`
- Key files verified: `materials-discovery/tests/test_llm_external_benchmark_schema.py`, `materials-discovery/src/materials_discovery/llm/schema.py`, `materials-discovery/src/materials_discovery/llm/storage.py`
- Focused validation is green: `7 passed in 0.28s`
