---
phase: 05-candidate-reference-data-lake-and-analysis-layer
plan: "01"
subsystem: materials-discovery/lake
tags: [lake, catalog, staleness, index, cli, pydantic, tdd]
dependency_graph:
  requires: []
  provides: [lake-catalog, lake-index, mdisc-lake-index, mdisc-lake-stats]
  affects: [cli.py, lake/catalog.py, lake/index.py, lake/staleness.py]
tech_stack:
  added: [pydantic-lake-models]
  patterns: [hash-based-staleness, workspace-relative-lineage, artifact-inventory-catalog]
key_files:
  created:
    - materials-discovery/src/materials_discovery/lake/__init__.py
    - materials-discovery/src/materials_discovery/lake/catalog.py
    - materials-discovery/src/materials_discovery/lake/staleness.py
    - materials-discovery/src/materials_discovery/lake/index.py
    - materials-discovery/tests/test_lake_catalog.py
    - materials-discovery/tests/test_lake_index.py
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/Progress.md
decisions:
  - "ARTIFACT_DIRECTORIES covers 17 entries (not 14) for full artifact inventory completeness"
  - "check_staleness uses hash-based detection (manifest output_hashes) as authoritative signal; mtime is a secondary hint"
  - "workspace_relative falls back to absolute path for tmp directories outside workspace root — tests use in-workspace dirs for the strict relative-path assertion"
  - "_workspace_root() indirection in index.py allows monkeypatching in tests without patching io.workspace_root"
metrics:
  duration: 25min
  completed: 2026-04-03
  tasks_completed: 2
  files_created: 6
  files_modified: 2
  tests_added: 15
  tests_total: 187
---

# Phase 05 Plan 01: Data Lake Catalog and Index Layer Summary

**One-liner:** Lake metadata layer with CatalogEntry/DirectoryCatalog Pydantic models, ARTIFACT_DIRECTORIES covering 17 subdirectories, hash-based staleness detection, lake-wide index rollup, and `mdisc lake index` / `mdisc lake stats` CLI commands.

## What Was Built

### Task 1: Catalog schema, staleness detection, per-directory catalog generator

**Files created:**
- `lake/__init__.py` — package marker
- `lake/catalog.py` — `CatalogEntry` and `DirectoryCatalog` Pydantic models; `ARTIFACT_DIRECTORIES` dict (17 entries); `build_directory_catalog()` scanning JSONL lines + JSON files with workspace-relative lineage extraction from manifests; `write_catalog()` writing `_catalog.json`
- `lake/staleness.py` — `check_staleness()` with (1) hash-based detection via manifest `output_hashes` as authoritative signal and (2) mtime comparison as secondary hint — addresses review concern #1

**Key design decisions:**
- `ARTIFACT_DIRECTORIES` maps 17 workspace-relative paths to artifact type strings, covering source_snapshot, reference_pack, external_fixtures, external_pinned, processed, candidates, screened, hifi_validated, ranked, active_learning, prototypes, calibration, benchmarks, reports, manifests, execution_cache, registry — addresses review concern #3
- All `directory_path` and `lineage` values use `workspace_relative()` from `data_sources/storage.py` — addresses review concern #5
- `content_hash` is SHA256 of `json.dumps(output_hashes, sort_keys=True)` — deterministic and manifest-driven

**Tests:** `test_lake_catalog.py` — 9 tests covering CatalogEntry validation, JSONL record count, workspace-relative paths, mtime staleness, hash staleness, freshness, artifact coverage, and write_catalog.

### Task 2: Lake index rollup and mdisc lake CLI

**Files created:**
- `lake/index.py` — `LakeIndex` Pydantic model (schema_version="lake-index/v1", workspace_root, artifact_directories, total_entries, stale_count, catalogs dict); `build_lake_index()` iterating ARTIFACT_DIRECTORIES and skipping missing dirs; `write_lake_index()` writing `data/lake_index.json`; `lake_stats()` returning summary dict
- `tests/test_lake_index.py` — 6 tests covering aggregation, missing-dir skip, JSON output schema, stats dict, CLI integration, and model validation

**Files modified:**
- `cli.py` — added `lake_app = typer.Typer(...)`, `app.add_typer(lake_app, name="lake")`, `@lake_app.command("index")`, `@lake_app.command("stats")`

**CLI commands:**
- `mdisc lake index [--root PATH]` — scans all artifact dirs, writes `_catalog.json` in each, writes `data/lake_index.json`
- `mdisc lake stats [--root PATH]` — loads or rebuilds lake_index.json, prints formatted summary table

## Test Results

All 187 tests pass (172 pre-existing + 15 new).

```
tests/test_lake_catalog.py  9 passed
tests/test_lake_index.py    6 passed
Full suite:               187 passed
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test for workspace-relative paths used tmp_path outside workspace**
- **Found during:** Task 1 (TDD GREEN)
- **Issue:** Test 3 created a `tmp_path` directory outside the workspace root. `workspace_relative()` correctly falls back to absolute paths for paths not under the workspace root — so the test assertion `not starts with /` failed.
- **Fix:** Changed test to use `workspace_root() / "data" / "_test_candidates_tmp"` (inside the workspace) and added cleanup via `shutil.rmtree`. This correctly validates the workspace-relative path contract for directories that are actually inside the workspace.
- **Files modified:** `tests/test_lake_catalog.py`
- **Commit:** d4ac4609

**2. [Rule 2 - Missing functionality] `_workspace_root()` indirection in index.py**
- **Found during:** Task 2 (CLI integration test)
- **Issue:** The CLI integration test monkeypatches workspace_root to point to `tmp_path`. Without an indirection layer, `index.py` would have captured the real workspace_root at import time.
- **Fix:** Added `_workspace_root()` wrapper function in `index.py` that calls `io.workspace_root()` lazily. Test monkeypatches `index_module._workspace_root`. This is a standard testability pattern.
- **Files modified:** `lake/index.py`

## Known Stubs

None. All functionality is fully wired:
- `build_directory_catalog` scans real files in real directories
- `check_staleness` uses real manifest hashes and real file mtimes
- `build_lake_index` iterates all ARTIFACT_DIRECTORIES
- `write_lake_index` and `write_catalog` write real JSON files
- CLI commands invoke real index/stats functions

## Self-Check: PASSED

Files verified:
- `materials-discovery/src/materials_discovery/lake/__init__.py` — FOUND
- `materials-discovery/src/materials_discovery/lake/catalog.py` — FOUND (contains CatalogEntry, DirectoryCatalog, ARTIFACT_DIRECTORIES, build_directory_catalog, workspace_relative)
- `materials-discovery/src/materials_discovery/lake/staleness.py` — FOUND (contains check_staleness, output_hashes)
- `materials-discovery/src/materials_discovery/lake/index.py` — FOUND (contains LakeIndex, build_lake_index, lake_stats)
- `materials-discovery/tests/test_lake_catalog.py` — FOUND (9 tests)
- `materials-discovery/tests/test_lake_index.py` — FOUND (6 tests)
- `materials-discovery/src/materials_discovery/cli.py` — contains lake_app, name="lake", "index", "stats"

Commits verified:
- d4ac4609 — feat(05-01): catalog schema, staleness detection, per-directory catalog builder
- a91689f1 — feat(05-01): lake index rollup, lake stats, and mdisc lake CLI commands
