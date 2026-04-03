---
phase: 02-ingestion-platform-mvp
plan: 03
subsystem: materials-discovery
tags: [ingestion, optimade, materials-project, oqmd, jarvis, api, materials-discovery]
requires: [02-01, 02-02]
provides:
  - shared OPTIMADE normalization foundation with lazy httpx integration
  - direct API adapters for Materials Project and OQMD
  - JARVIS adapter and mixed adapter-family compatibility tests
affects: [OPS-04, DATA-03, DATA-04, phase-02-completion]
tech-stack:
  added: [OPTIMADE JSON normalization]
  patterns: [lazy optional HTTP deps, offline inline API fixtures, mixed direct-and-optimade registry coverage]
key-files:
  created:
    - materials-discovery/src/materials_discovery/data_sources/adapters/optimade.py
    - materials-discovery/src/materials_discovery/data_sources/adapters/materials_project.py
    - materials-discovery/src/materials_discovery/data_sources/adapters/oqmd.py
    - materials-discovery/src/materials_discovery/data_sources/adapters/jarvis.py
    - materials-discovery/tests/test_data_source_optimade.py
    - materials-discovery/tests/test_data_source_materials_project.py
    - materials-discovery/tests/test_data_source_api_adapters.py
    - .planning/phases/02-ingestion-platform-mvp/02-03-SUMMARY.md
  modified:
    - materials-discovery/src/materials_discovery/data_sources/adapters/__init__.py
    - materials-discovery/src/materials_discovery/data_sources/registry.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/Progress.md
key-decisions:
  - "Keep httpx imports lazy so the default uv test flow stays green without explicitly installing the ingestion extra."
  - "Use inline response fixtures in tests for OPTIMADE and direct API adapters instead of recorded network cassettes."
  - "Keep JARVIS as a dedicated adapter file even though it reuses the generic OPTIMADE base, so the file layout matches the roadmap contract."
patterns-established:
  - "Shared OPTIMADE adapters normalize provider IDs, attributes, and structure payloads into the canonical raw-source contract."
  - "Direct API adapters accept inline rows or snapshot files for offline testing, with network paths reserved for future live runs."
  - "CLI compatibility is protected by explicit tests that legacy configs still succeed without an ingestion block."
requirements-completed: []
duration: 32min
completed: 2026-04-03
---

# Phase 2 Plan 03: Implement Direct API And OPTIMADE Adapters Summary

**Shared OPTIMADE foundation plus offline-capable Materials Project, OQMD, and JARVIS adapters**

## Performance

- **Duration:** 32 min
- **Started:** 2026-04-03T14:57:00Z
- **Completed:** 2026-04-03T15:29:00Z
- **Tasks:** 3
- **Task commits:** 1

## Accomplishments

- Added a reusable `OptimadeSourceAdapter` base that imports `httpx` lazily,
  normalizes OPTIMADE records into canonical raw-source records, and supports
  offline inline responses for tests.
- Added direct source adapters for `Materials Project` and `OQMD` plus a
  dedicated `jarvis.py` adapter that reuses the shared OPTIMADE foundation.
- Added deterministic tests for the OPTIMADE base, the Materials Project
  adapter, mixed direct-and-OPTIMADE registry behavior, and legacy CLI
  compatibility without an `ingestion` block.

## Task Commits

1. **Wave 3 API and OPTIMADE adapter implementation** - `720650ff` (`feat`)

## Verification

- `cd materials-discovery && uv run pytest tests/test_data_source_optimade.py tests/test_data_source_materials_project.py tests/test_data_source_api_adapters.py tests/test_cli.py`
- `cd materials-discovery && uv run pytest tests/test_ingest.py tests/test_ingest_real_backend.py tests/test_cli.py`
- `cd materials-discovery && uv run pytest`

All verification commands passed at the end of the wave.

## Deviations from Plan

### Auto-fixed Issues

**1. Added a dedicated `jarvis.py` wrapper after the first implementation placed the JARVIS builder only in `optimade.py`**

- **Found during:** Acceptance-criteria review before focused Wave 3 tests
- **Issue:** The plan explicitly called for a `materials_discovery/data_sources/adapters/jarvis.py` file.
- **Fix:** Added `jarvis.py` as the explicit JARVIS adapter entrypoint while keeping the shared normalization logic in `optimade.py`.
- **Files modified:** `materials-discovery/src/materials_discovery/data_sources/adapters/jarvis.py`, `materials-discovery/src/materials_discovery/data_sources/adapters/__init__.py`
- **Verification:** `cd materials-discovery && uv run pytest tests/test_data_source_optimade.py tests/test_data_source_materials_project.py tests/test_data_source_api_adapters.py tests/test_cli.py`
- **Committed in:** `720650ff`

---

**Total deviations:** 1 auto-fixed

## Next Phase Readiness

- Phase 2 now proves the runtime across direct snapshot, CIF-conversion, direct
  API, and OPTIMADE-family adapters, which is enough to start Phase 3’s bridge
  back into the current `mdisc ingest` path.
- The CLI compatibility test coverage gives Phase 3 a safety net while it wires
  the `source_registry_v1` seam into the existing operator workflow.

## Self-Check: PASSED

- Verified commit `720650ff` exists in git history.
- Verified focused Wave 3 tests, legacy CLI/ingest regression tests, and the full suite pass.
