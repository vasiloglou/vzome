---
phase: 02-ingestion-platform-mvp
plan: 02
subsystem: materials-discovery
tags: [ingestion, hypodx, cod, cif, staging, materials-discovery]
requires: [02-01]
provides:
  - HYPOD-X source adapters for fixture-backed and pinned snapshots
  - COD local CIF conversion and staging path
  - offline tests for direct snapshot and CIF-conversion source families
affects: [02-03, DATA-03, DATA-04]
tech-stack:
  added: [offline cif fixture]
  patterns: [source adapter registration, canonical structure staging, deterministic offline provider tests]
key-files:
  created:
    - materials-discovery/src/materials_discovery/data_sources/adapters/__init__.py
    - materials-discovery/src/materials_discovery/data_sources/adapters/hypodx.py
    - materials-discovery/src/materials_discovery/data_sources/adapters/cif_conversion.py
    - materials-discovery/src/materials_discovery/data_sources/adapters/cod.py
    - materials-discovery/tests/fixtures/cod_sample.cif
    - materials-discovery/tests/test_data_source_hypodx.py
    - materials-discovery/tests/test_data_source_cod.py
    - .planning/phases/02-ingestion-platform-mvp/02-02-SUMMARY.md
  modified:
    - materials-discovery/src/materials_discovery/data_sources/__init__.py
    - materials-discovery/src/materials_discovery/data_sources/registry.py
    - materials-discovery/src/materials_discovery/data_sources/runtime.py
    - materials-discovery/Progress.md
key-decisions:
  - "Reuse the existing HYPOD-X normalization rules so the new runtime matches the current scientific ingest assumptions."
  - "Use deterministic local CIF parsing for COD fixtures instead of introducing another optional scientific dependency into the default test path."
  - "Keep built-in source adapter registration explicit so Wave 1 registry tests can still clear the registry fully."
patterns-established:
  - "HYPOD-X staging keeps raw rows intact while canonical records use stable source_record_id-derived local IDs to surface duplicate collisions in QA."
  - "CIF conversion produces structure records with CIF-backed structure_representations plus normalized cell and site summaries."
requirements-completed: []
duration: 31min
completed: 2026-04-03
---

# Phase 2 Plan 02: Implement HYPOD-X And COD Staging Summary

**First concrete provider adapters on the new source runtime: HYPOD-X as the regression anchor and COD as the CIF-conversion proof path**

## Performance

- **Duration:** 31 min
- **Started:** 2026-04-03T14:25:00Z
- **Completed:** 2026-04-03T14:56:00Z
- **Tasks:** 3
- **Task commits:** 1

## Accomplishments

- Implemented fixture-backed and pinned `HYPOD-X` adapters on the new
  `data_sources` runtime with stable canonical IDs, source manifests, QA
  reporting, and artifact staging under `data/external/sources/hypodx/`.
- Implemented a deterministic local CIF conversion path and COD adapter that
  turns a checked-in CIF fixture into canonical structure records with
  `structure_representations`.
- Added deterministic offline tests covering both HYPOD-X staging and COD CIF
  staging while preserving the legacy `mdisc ingest` path.

## Task Commits

1. **Wave 2 provider implementation and tests** - `1486e9b5` (`feat`)

## Verification

- `cd materials-discovery && uv run pytest tests/test_data_source_hypodx.py tests/test_data_source_cod.py`
- `cd materials-discovery && uv run pytest tests/test_ingest.py tests/test_ingest_real_backend.py tests/test_cli.py`
- `cd materials-discovery && uv run pytest`

All verification commands passed at the end of the wave.

## Deviations from Plan

### Intentional Consolidation

**1. Landed the three Wave 2 tasks in one commit because the registry and runtime changes were shared across both adapters**

- **Why:** `registry.py`, `runtime.py`, and the adapter package exports are shared integration points for both HYPOD-X and COD, so splitting them into separate commits would have produced awkward partial states.
- **Impact:** No behavioral ambiguity; the staged adapter surface and its tests were verified together as one coherent checkpoint.

---

**Total deviations:** 1 intentional consolidation

## Next Phase Readiness

- The runtime now supports both direct phase-row staging and CIF-derived
  structure staging, so Wave 3 can focus on direct API and OPTIMADE-family
  normalization instead of foundational file/QA concerns.
- The registry and runtime now support explicit built-in adapter registration,
  which Wave 3 can extend for `Materials Project`, `OQMD`, and `JARVIS`.

## Self-Check: PASSED

- Verified commit `1486e9b5` exists in git history.
- Verified focused Wave 2 tests, legacy ingest regression tests, and the full suite pass.
