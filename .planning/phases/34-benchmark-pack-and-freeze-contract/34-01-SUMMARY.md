---
phase: 34-benchmark-pack-and-freeze-contract
plan: 01
subsystem: llm
tags: [benchmark-pack, translation, pydantic, storage, llm]
requires:
  - phase: 33-cli-benchmark-hooks-and-operator-docs
    provides: translation bundle manifests and inventory rows reusable as benchmark-pack lineage
provides:
  - typed translated benchmark-pack contract models
  - deterministic llm_external_sets artifact paths
  - focused schema and storage regression coverage for translated benchmark packs
affects: [34-02-plan, 34-03-plan, 35-external-target-registration-and-reproducible-execution]
tech-stack:
  added: []
  patterns:
    - translated benchmark packs reuse translation bundle enums and lineage fields instead of inventing a parallel payload schema
    - benchmark-pack artifacts live under a dedicated llm_external_sets root with deterministic contract and inventory filenames
key-files:
  created:
    - materials-discovery/tests/test_llm_translated_benchmark_schema.py
  modified:
    - materials-discovery/src/materials_discovery/llm/schema.py
    - materials-discovery/src/materials_discovery/llm/storage.py
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Benchmark-pack rows preserve source_export_id and source_bundle_manifest_path explicitly so later freeze and inspect flows can trace back to shipped translation bundles without parsing ad hoc metadata."
  - "Benchmark-pack artifacts use a dedicated data/benchmarks/llm_external_sets/{benchmark_set_id}/ root to avoid overloading translation-export or serving-benchmark directories."
patterns-established:
  - "Translated benchmark contracts mirror the translation inventory row surface and add only benchmark lineage plus exclusion semantics."
  - "Benchmark-pack storage uses freeze_contract.json, manifest.json, included.jsonl, and excluded.jsonl as the fixed artifact set."
requirements-completed: [LLM-31]
duration: 8 min
completed: 2026-04-07
---

# Phase 34 Plan 01: Benchmark Pack Contract Summary

**Typed translated benchmark-pack models and deterministic `llm_external_sets` storage paths for frozen external benchmark slices**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-07T05:32:00Z
- **Completed:** 2026-04-07T05:40:46Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added a typed translated benchmark freeze contract with explicit system, target-family, fidelity-tier, and loss-posture filters.
- Added included and excluded benchmark row models that preserve translation-bundle lineage and use typed exclusion reasons instead of stringly typed branching.
- Added deterministic benchmark-pack storage helpers under `data/benchmarks/llm_external_sets/{benchmark_set_id}/` and locked the contract/storage surface with focused pytest coverage.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define the translated benchmark freeze contract and exclusion vocabulary** - `2c6a7e0d` (test, RED), `55805326` (feat, GREEN)
2. **Task 2: Add deterministic storage helpers for the benchmark-pack artifact layout** - `78787939` (test, RED), `bb742444` (feat, GREEN)

## Files Created/Modified

- `materials-discovery/src/materials_discovery/llm/schema.py` - Added benchmark-pack contract, inclusion/exclusion row, manifest, and summary models.
- `materials-discovery/src/materials_discovery/llm/storage.py` - Added deterministic `llm_external_sets` path helpers for contract and inventory artifacts.
- `materials-discovery/src/materials_discovery/llm/__init__.py` - Re-exported the new benchmark-pack contract models.
- `materials-discovery/tests/test_llm_translated_benchmark_schema.py` - Locked schema and storage behavior for the new benchmark-pack surface.
- `materials-discovery/Progress.md` - Logged RED/GREEN progress for both TDD tasks as required by repo policy.

## Decisions Made

- Kept the benchmark-pack contract additive to translation bundles by reusing translation-family, fidelity-tier, loss-reason, and diagnostic-code types.
- Stored exclusion posture as typed literals so later CLI inspect output can branch on stable values instead of free-form text.
- Reserved a dedicated `llm_external_sets` artifact family so later freeze and comparative benchmark phases can rely on one stable filesystem contract.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02 can now freeze included and excluded rows directly against a stable benchmark-pack contract and deterministic artifact layout. The remaining Phase 34 work can build CLI freeze and inspect behavior on top of explicit lineage, typed exclusion reasons, and fixed contract/inventory paths.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/34-benchmark-pack-and-freeze-contract/34-01-SUMMARY.md`
- Key files verified: `materials-discovery/tests/test_llm_translated_benchmark_schema.py`, `materials-discovery/src/materials_discovery/llm/schema.py`, `materials-discovery/src/materials_discovery/llm/storage.py`
- Task commits verified: `2c6a7e0d`, `55805326`, `78787939`, `bb742444`
