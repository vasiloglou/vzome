---
phase: 02-ingestion-platform-mvp
plan: 01
subsystem: materials-discovery
tags: [ingestion, data-sources, schema, qa, testing, materials-discovery]
requires: [01-program-charter-and-canonical-data-model]
provides:
  - canonical source staging runtime modules under materials_discovery.data_sources
  - additive SystemConfig.ingestion seam with reserved source bridge key
  - focused schema, registry, and QA tests for the new runtime contract
affects: [02-02, 02-03, DATA-03, DATA-04, OPS-04]
tech-stack:
  added: [httpx, pymatgen]
  patterns: [file-backed source staging, additive config seam, canonical raw-source contracts]
key-files:
  created:
    - materials-discovery/src/materials_discovery/data_sources/__init__.py
    - materials-discovery/src/materials_discovery/data_sources/schema.py
    - materials-discovery/src/materials_discovery/data_sources/types.py
    - materials-discovery/src/materials_discovery/data_sources/registry.py
    - materials-discovery/src/materials_discovery/data_sources/storage.py
    - materials-discovery/src/materials_discovery/data_sources/manifests.py
    - materials-discovery/src/materials_discovery/data_sources/qa.py
    - materials-discovery/tests/test_data_source_schema.py
    - materials-discovery/tests/test_data_source_registry.py
    - materials-discovery/tests/test_data_source_qa.py
    - .planning/phases/02-ingestion-platform-mvp/02-01-SUMMARY.md
  modified:
    - materials-discovery/pyproject.toml
    - materials-discovery/uv.lock
    - materials-discovery/src/materials_discovery/common/schema.py
    - materials-discovery/src/materials_discovery/backends/registry.py
    - materials-discovery/src/materials_discovery/data_sources/runtime.py
    - materials-discovery/tests/test_native_providers.py
    - materials-discovery/Progress.md
key-decisions:
  - "Keep provider ingestion logic in materials_discovery.data_sources instead of widening the legacy ingest backend contract."
  - "Introduce SystemConfig.ingestion additively so current YAML configs stay valid with no source-runtime wiring yet."
  - "Treat schema, registry, and QA behavior as Wave 1 contract tests before any provider-specific adapters are added."
patterns-established:
  - "Canonical raw-source staging writes raw rows, canonical records, QA reports, and snapshot manifests under data/external/sources/{source_key}/{snapshot_id}/."
  - "Registry-driven adapters are keyed by source_key plus adapter_key, with a reserved source_registry_v1 bridge for later CLI integration."
  - "Wave-level verification uses both focused tests and the full materials-discovery pytest suite."
requirements-completed: []
duration: 59min
completed: 2026-04-03
---

# Phase 2 Plan 01: Build The Ingestion Runtime Foundation Summary

**Source staging foundation, additive config seam, and contract tests for the new ingestion runtime**

## Performance

- **Duration:** 59 min
- **Started:** 2026-04-03T13:25:00Z
- **Completed:** 2026-04-03T14:24:00Z
- **Tasks:** 3
- **Task commits:** 4

## Accomplishments

- Built the `materials_discovery.data_sources` runtime package with schema,
  registry, storage, manifest, QA, and staging orchestration modules.
- Added the additive `SystemConfig.ingestion` block and reserved the
  `source_registry_v1` bridge adapter key without changing the existing
  `mdisc ingest` operator path.
- Added focused pytest coverage for canonical raw-source schema behavior,
  adapter registry behavior, and QA aggregation edge cases.
- Refreshed the lockfile for the new `ingestion` extra and hardened one
  native-provider test so the full suite reflects the optional-dependency
  contract accurately.

## Task Commits

1. **Task 1: Implement the canonical source runtime modules** - `a61cceca` (`feat`)
2. **Task 2: Add additive config support and reserve the source-runtime bridge** - `7e57443c` (`feat`)
3. **Task 3: Add foundational schema, registry, and QA tests** - `4cfdb95e` (`test`)
4. **Support: Refresh ingestion lockfile** - `8b8a6503` (`chore`)

## Verification

- `cd materials-discovery && python3 -m compileall src/materials_discovery/data_sources`
- `cd materials-discovery && python3 -m compileall src/materials_discovery/common/schema.py src/materials_discovery/backends/registry.py src/materials_discovery/data_sources/runtime.py`
- `cd materials-discovery && uv run pytest tests/test_data_source_schema.py tests/test_data_source_registry.py tests/test_data_source_qa.py`
- `cd materials-discovery && uv run pytest tests/test_cli.py tests/test_ingest.py tests/test_ingest_real_backend.py`
- `cd materials-discovery && uv run pytest`

All verification commands passed at the end of the wave.

## Deviations from Plan

### Auto-fixed Issues

**1. Full-suite optional dependency test assumed `ase` was present in the base test environment**

- **Found during:** Wave-level `uv run pytest`
- **Issue:** `tests/test_native_providers.py` expected the MD provider to fail only at the missing-calculator branch, but the base environment can fail earlier when `ase` itself is absent because it remains behind the `mlip` extra.
- **Fix:** Relaxed the assertion to accept either a missing ASE-compatible calculator or the clean optional-dependency message for `ase`.
- **Files modified:** `materials-discovery/tests/test_native_providers.py`
- **Verification:** `cd materials-discovery && uv run pytest`
- **Committed in:** `4cfdb95e`

---

**Total deviations:** 1 auto-fixed
**Impact on plan:** The change kept the wave verification aligned with the repo’s optional-dependency contract and did not alter production behavior.

## Next Phase Readiness

- Wave 2 can now implement `HYPOD-X` and `COD` adapters against a tested raw-source runtime instead of adding provider logic on top of placeholders.
- Wave 3 can build direct and OPTIMADE-family API adapters on top of the same schema, registry, and QA contract.
- The legacy ingest path remains green, so Phase 3 can bridge the new runtime later without undoing operator-facing behavior now.

## Self-Check: PASSED

- Verified task commits `a61cceca`, `7e57443c`, `4cfdb95e`, and `8b8a6503` exist in git history.
- Verified focused Wave 1 tests and the full materials-discovery suite pass after the test hardening fix.
