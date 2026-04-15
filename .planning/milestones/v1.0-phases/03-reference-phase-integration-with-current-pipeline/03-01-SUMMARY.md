---
phase: 03-reference-phase-integration-with-current-pipeline
plan: 01
subsystem: materials-discovery
tags: [ingestion, projection, source-registry, reference-phases, testing, materials-discovery]
requires: [02-ingestion-platform-mvp]
provides:
  - canonical source projection module from staged records to processed IngestRecord rows
  - deterministic system matching, phase-name fallback, and dedupe rules
  - reusable ProjectionSummary lineage handoff plus focused projection tests
affects: [03-02, 03-03, DATA-05, OPS-03]
tech-stack:
  added: [projection module]
  patterns: [canonical-to-processed projection, additive provenance metadata, deterministic projection fingerprints]
key-files:
  created:
    - materials-discovery/src/materials_discovery/data_sources/projection.py
    - materials-discovery/tests/test_data_source_projection.py
    - .planning/phases/03-reference-phase-integration-with-current-pipeline/03-01-SUMMARY.md
  modified:
    - materials-discovery/src/materials_discovery/data_sources/__init__.py
    - materials-discovery/src/materials_discovery/data_sources/schema.py
    - materials-discovery/Progress.md
key-decisions:
  - "Keep projection in materials_discovery.data_sources.projection instead of widening the legacy HYPOD-X normalization seam."
  - "Normalize source-system matching from canonical element hints rather than raw provider string equality."
  - "Use additive processed metadata for lineage, structure tags, and QC cues so downstream consumers stay backward-compatible."
patterns-established:
  - "Projection returns both projected IngestRecord rows and a ProjectionSummary for later manifest lineage."
  - "Phase names fall back in the locked order reported_properties.phase_name -> source.record_title -> common.formula_reduced -> source.source_record_id."
requirements-completed: [DATA-05, OPS-03]
duration: 19min
completed: 2026-04-03
---

# Phase 3 Plan 01: Build The Reference-Phase Projection Core Summary

**Canonical source projection from staged records into processed reference-phase rows with deterministic matching, labeling, and provenance**

## Performance

- **Duration:** 19 min
- **Started:** 2026-04-03T09:39:00-04:00
- **Completed:** 2026-04-03T09:58:00-04:00
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added `materials_discovery.data_sources.projection` as the dedicated seam from
  staged canonical source records into processed `IngestRecord` rows.
- Locked deterministic rules for system matching, phase-name derivation,
  projection fingerprints, and dedupe winner selection.
- Added `ProjectionSummary` so the later ingest manifest can carry projection
  counts without re-reading processed rows.
- Added focused projection tests, including a direct downstream compatibility
  proof with `hull_proxy`.

## Task Commits

1. **Task 1: Implement canonical-source projection into processed reference-phase records** - `74fb2e67` (`feat`)
2. **Task 2: Lock projection behavior with deterministic focused tests** - `74fb2e67` (`feat`)

## Verification

- `cd materials-discovery && uv run pytest tests/test_data_source_projection.py`
- `cd materials-discovery && uv run pytest tests/test_hull_proxy.py`

Both verification commands passed.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- The repo now has a stable projection seam that Wave 2 can call from the
  existing `mdisc ingest` command.
- Projection counts are available for ingest-manifest lineage without changing
  downstream consumers.

## Self-Check: PASSED

- Verified commit `74fb2e67` exists in git history.
- Verified focused projection and downstream compatibility tests pass.
