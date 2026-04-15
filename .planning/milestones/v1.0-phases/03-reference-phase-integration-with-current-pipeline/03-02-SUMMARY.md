---
phase: 03-reference-phase-integration-with-current-pipeline
plan: 02
subsystem: materials-discovery
tags: [ingest, source-registry, cli, manifests, lineage, materials-discovery]
requires: [03-01]
provides:
  - real source_registry_v1 branch inside mdisc ingest
  - additive ingest-manifest source_lineage references
  - offline bridge tests for source-backed, legacy, and non-ingest manifest paths
affects: [03-03, PIPE-01, DATA-05, OPS-03]
tech-stack:
  added: [source lineage manifest field]
  patterns: [source-registry CLI branching, cached snapshot reuse, additive manifest evolution]
key-files:
  created:
    - materials-discovery/tests/test_ingest_source_registry.py
    - .planning/phases/03-reference-phase-integration-with-current-pipeline/03-02-SUMMARY.md
  modified:
    - materials-discovery/src/materials_discovery/backends/registry.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/src/materials_discovery/common/manifest.py
    - materials-discovery/src/materials_discovery/common/schema.py
    - materials-discovery/src/materials_discovery/data_sources/runtime.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/tests/test_generate.py
    - materials-discovery/Progress.md
key-decisions:
  - "Branch on source_registry_v1 in cli.py instead of trying to force SourceAdapter through the legacy IngestBackend protocol."
  - "Treat incomplete cached snapshots as a hard ingest error, while missing caches stage fresh artifacts."
  - "Attach source_lineage directly to the standard ingest manifest instead of inventing a second operator-facing manifest."
patterns-established:
  - "Source-backed ingest reuses cached canonical snapshot artifacts when the cache is complete and use_cached_snapshot is enabled."
  - "Non-ingest manifests remain valid with source_lineage unset, preserving additive schema evolution."
requirements-completed: [DATA-05, PIPE-01, OPS-03]
duration: 17min
completed: 2026-04-03
---

# Phase 3 Plan 02: Wire The Source-Registry Bridge Into `mdisc ingest` Summary

**Source-backed ingest inside the existing CLI with cached snapshot reuse and additive ingest-manifest lineage**

## Performance

- **Duration:** 17 min
- **Started:** 2026-04-03T09:58:00-04:00
- **Completed:** 2026-04-03T10:15:00-04:00
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Turned `source_registry_v1` into a real `mdisc ingest` path that stages or
  reuses canonical source snapshots, projects them into processed reference
  phases, and keeps the legacy path intact.
- Added additive `source_lineage` support on the standard ingest manifest,
  including snapshot references and projection counts.
- Added deterministic bridge tests for source-backed ingest success, cached
  snapshot reuse, missing-ingestion failure, legacy CLI compatibility, and
  non-ingest manifest serialization.

## Task Commits

1. **Task 1: Bridge the reserved source-runtime adapter into `mdisc ingest`** - `63c21d07` (`feat`)
2. **Task 2: Extend the standard ingest manifest with source lineage** - `63c21d07` (`feat`)
3. **Task 3: Add bridge integration tests for source-backed and legacy ingest** - `63c21d07` (`feat`)

## Verification

- `cd materials-discovery && uv run pytest tests/test_ingest_source_registry.py tests/test_cli.py tests/test_ingest.py tests/test_ingest_real_backend.py tests/test_generate.py`

The full Wave 2 verification command passed.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- The stable `mdisc ingest` operator command now supports both legacy and
  source-backed reference-phase ingestion.
- Wave 3 can focus entirely on downstream pipeline compatibility and no-DFT
  guardrails rather than bridge mechanics.

## Self-Check: PASSED

- Verified commit `63c21d07` exists in git history.
- Verified bridge, legacy CLI, legacy ingest, and non-ingest manifest tests pass.
