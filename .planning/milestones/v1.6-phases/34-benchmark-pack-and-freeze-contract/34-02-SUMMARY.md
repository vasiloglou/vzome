---
phase: 34-benchmark-pack-and-freeze-contract
plan: 02
subsystem: llm
tags: [benchmark-pack, translation, freeze, lineage, pydantic]
requires:
  - phase: 34-01-plan
    provides: translated benchmark-pack schema and deterministic llm_external_sets storage helpers
provides:
  - bundle-driven translated benchmark freeze engine with deterministic inclusion and exclusion behavior
  - persisted freeze contract, manifest, included inventory, and excluded inventory artifacts
  - public llm freeze exports plus typed manifest exclusion-reason tallies
affects: [34-03-plan, 35-external-target-registration-and-reproducible-execution, 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards]
tech-stack:
  added: []
  patterns:
    - translated benchmark packs normalize bundle manifest ordering before writing persisted contract artifacts
    - duplicate translated rows fail closed on payload-hash conflicts and otherwise demote later exact duplicates into typed exclusions
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/translated_benchmark.py
    - materials-discovery/tests/test_llm_translated_benchmark_freeze.py
  modified:
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/Progress.md
key-decisions:
  - "Freeze evaluation applies system, target-family, fidelity-tier, and loss-posture rules in a fixed order before duplicate handling so every rejected row gets one typed exclusion reason."
  - "The persisted freeze contract normalizes bundle manifest ordering so manifest, contract, and inventory bytes remain stable across repeat runs."
  - "Conflicting payload hashes for the same candidate ID fail closed instead of picking an arbitrary winning bundle."
patterns-established:
  - "Freeze artifacts always live as freeze_contract.json, manifest.json, included.jsonl, and excluded.jsonl under one benchmark-set directory."
  - "Manifest lineage carries source bundle manifest paths, source export IDs, and exclusion reason tallies as first-class typed data."
requirements-completed: [LLM-31]
duration: 10 min
completed: 2026-04-07
---

# Phase 34 Plan 02: Benchmark Pack and Freeze Contract Summary

**Bundle-driven translated benchmark freezing with typed exclusions, persisted lineage artifacts, and public `materials_discovery.llm` exports**

## Performance

- **Duration:** 10 min
- **Started:** 2026-04-07T05:50:03Z
- **Completed:** 2026-04-07T05:59:58Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added `llm/translated_benchmark.py` with spec loading, shipped bundle inventory loading, deterministic filtering, duplicate handling, and conflict failure for translated benchmark freezing.
- Materialized the full artifact family under `data/benchmarks/llm_external_sets/{benchmark_set_id}/`, including normalized `freeze_contract.json`, `manifest.json`, `included.jsonl`, and `excluded.jsonl`.
- Re-exported the freeze helpers from `materials_discovery.llm` and locked the full freeze behavior with focused pytest coverage for filtering, typed exclusions, persisted lineage, and repeat-run stability.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the bundle-driven freeze engine and explicit exclusion rules** - `412eecdf` (test, RED), `50f0f649` (feat, GREEN)
2. **Task 2: Persist the frozen contract, included inventory, excluded inventory, and manifest lineage** - `1779c04b` (test, RED), `affffdc9` (feat, GREEN)

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` - New freeze engine module for translated benchmark specs, bundle loading, exclusion evaluation, duplicate handling, and artifact writing.
- `materials-discovery/tests/test_llm_translated_benchmark_freeze.py` - Focused regression suite covering eligibility filters, typed exclusions, duplicates, persisted lineage artifacts, repeat-run stability, and public exports.
- `materials-discovery/src/materials_discovery/llm/schema.py` - Extended `TranslatedBenchmarkSetManifest` with typed `exclusion_reason_counts` for persisted manifest tallies.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Re-exported `freeze_translated_benchmark_set(...)` and `load_translated_benchmark_spec(...)` from the public `llm` surface.
- `materials-discovery/Progress.md` - Logged RED/GREEN work plus the acceptance follow-up required by repo policy.

## Decisions Made

- Normalized `bundle_manifest_paths` before writing the persisted freeze contract so artifact bytes stay stable even when the input spec lists bundles in a different order.
- Kept `target_family` as a hard row-level filter even if a bundle manifest came from a different export lane, which preserves one explicit benchmark-pack slice per family.
- Treated explicit loss posture separately from fidelity-tier filtering so `lossy_only` and `lossless_only` remain orthogonal to the selected tier list.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added typed manifest exclusion tallies**
- **Found during:** Task 2 (Persist the frozen contract, included inventory, excluded inventory, and manifest lineage)
- **Issue:** The persisted manifest needed exclusion-reason tallies for later inspect and scorecard phases, but `TranslatedBenchmarkSetManifest` had no field to store them through the typed contract.
- **Fix:** Added `exclusion_reason_counts` to the schema model, validated its counts, and wrote the tally map from the freeze engine into `manifest.json`.
- **Files modified:** `materials-discovery/src/materials_discovery/llm/schema.py`, `materials-discovery/src/materials_discovery/llm/translated_benchmark.py`
- **Verification:** `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translated_benchmark_freeze.py -x -v`
- **Committed in:** `affffdc9`

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** The deviation was required for the persisted manifest contract to carry the lineage data Plan 02 explicitly needs. No scope creep beyond the freeze artifact surface.

## Issues Encountered

- Task 2 acceptance greps required the fixed artifact filenames to appear directly in code and tests. I kept the runtime on storage helpers and added explicit filename assertions plus a short module note so the acceptance surface stayed visible without changing the path logic.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 03 can add CLI freeze and inspect commands on top of a stable file-backed freeze contract and persisted inventories.
- Later benchmark and target-registration phases can consume `source_bundle_manifest_paths`, `source_export_ids`, and `exclusion_reason_counts` directly from `manifest.json` without reconstructing lineage from raw bundles.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/34-benchmark-pack-and-freeze-contract/34-02-SUMMARY.md`
- Key files verified: `materials-discovery/src/materials_discovery/llm/translated_benchmark.py`, `materials-discovery/tests/test_llm_translated_benchmark_freeze.py`, `materials-discovery/src/materials_discovery/llm/schema.py`, `materials-discovery/src/materials_discovery/llm/__init__.py`
- Task commits verified: `412eecdf`, `50f0f649`, `1779c04b`, `affffdc9`
