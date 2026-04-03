---
phase: 04-reference-aware-no-dft-materials-discovery-v1
plan: "01"
subsystem: materials-discovery
tags:
  - reference-packs
  - benchmarking
  - multi-source
  - schema
  - config
dependency_graph:
  requires:
    - phase-03-reference-phase-integration-with-current-pipeline
  provides:
    - reference-pack-assembly-layer
    - al_cu_fe_reference_aware_config
    - sc_zn_reference_aware_config
  affects:
    - materials_discovery.common.schema
    - materials_discovery.data_sources
    - materials_discovery.cli
tech_stack:
  added:
    - reference_packs.py module (data_sources)
    - ReferencePackConfig, ReferencePackMemberConfig (common/schema.py)
    - ReferencePackManifest, ReferencePackMemberResult (data_sources/schema.py)
  patterns:
    - multi-source canonical-record assembly with deterministic deduplication
    - explicit source-priority ordering (QC-specific sources > generic periodic sources)
    - cached-pack reuse with optional bypass
    - pack manifest with deterministic SHA-256 fingerprint
key_files:
  created:
    - materials-discovery/src/materials_discovery/data_sources/reference_packs.py
    - materials-discovery/tests/test_reference_packs.py
    - materials-discovery/configs/systems/al_cu_fe_reference_aware.yaml
    - materials-discovery/configs/systems/sc_zn_reference_aware.yaml
    - materials-discovery/data/external/sources/materials_project/mp_fixture_v1/canonical_records.jsonl
    - materials-discovery/data/external/sources/cod/cod_fixture_v1/canonical_records.jsonl
    - materials-discovery/data/external/sources/hypodx/hypodx_pinned_2026_03_09/canonical_records.jsonl
    - materials-discovery/data/external/sources/hypodx/hypodx_fixture_local/canonical_records.jsonl
  modified:
    - materials-discovery/src/materials_discovery/common/schema.py
    - materials-discovery/src/materials_discovery/data_sources/schema.py
    - materials-discovery/src/materials_discovery/data_sources/storage.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_benchmarking.py
    - materials-discovery/Progress.md
    - materials-discovery/.gitignore
decisions:
  - "ReferencePackConfig and ReferencePackMemberConfig live in common/schema.py (config layer) to avoid circular imports with data_sources/schema.py"
  - "ReferencePackManifest and ReferencePackMemberResult live in data_sources/schema.py (disk-artifact layer)"
  - "pack_root override parameter added to storage helpers so tests write into tmp_path without polluting workspace"
  - "CLI detects ingestion.reference_pack and routes source_registry_v1 through _ingest_via_reference_pack instead of _ingest_via_source_registry"
  - "Second source for Al-Cu-Fe: materials_project (MP fixture v1); for Sc-Zn: cod (COD fixture v1)"
metrics:
  duration_minutes: 12
  completed_date: "2026-04-03"
  tasks_completed: 2
  tasks_total: 2
  files_created: 8
  files_modified: 7
  tests_added: 46
  tests_passing: 151
---

# Phase 4 Plan 01: Assemble Two-System Reference Packs And Benchmark Configs Summary

**One-liner:** Explicit multi-source reference-pack assembly layer with deterministic deduplication and priority ordering, plus committed Phase 4 benchmark configs for Al-Cu-Fe (HYPOD-X + Materials Project) and Sc-Zn (HYPOD-X + COD) with thin second-source fixtures and 46 new deterministic tests.

## What Was Built

### Task 1: Explicit reference-pack assembly and reuse layer

A new `materials_discovery.data_sources.reference_packs` module implements:

- **`assemble_reference_pack(pack_config, system_slug, artifact_root, pack_root)`** — loads staged canonical source snapshots per member, deduplicates across sources using explicit priority ordering (lower priority rank wins), writes `canonical_records.jsonl` + `pack_manifest.json` under `data/external/reference_packs/{slug}/{pack_id}/`, and reuses complete cached packs when `reuse_cached_pack=True`.
- **`assemble_reference_pack_from_config(config, system_slug, pack_root)`** — convenience wrapper that extracts the `ingestion.reference_pack` block from a `SystemConfig`.
- **`load_cached_pack_manifest(system_slug, pack_id, pack_root)`** — returns a cached `ReferencePackManifest` if a complete pack already exists.

**Schema additions (`common/schema.py`):**
- `ReferencePackMemberConfig` — single source-snapshot member (source_key, snapshot_id, optional staged path overrides).
- `ReferencePackConfig` — additive `ingestion.reference_pack` contract: `pack_id`, `members[]`, `reuse_cached_pack`, `priority_order`. This is the Phase 4 schema contract that Plan 02 can consume directly.
- `IngestionConfig.source_key` made optional (defaults to `""`) when `reference_pack` is provided.

**Schema additions (`data_sources/schema.py`):**
- `ReferencePackMemberResult` — per-member assembly outcome recorded in `pack_manifest.json`.
- `ReferencePackManifest` — the full pack manifest: `pack_id`, `system_slug`, `created_at_utc`, `pack_fingerprint` (SHA-256, 32 hex chars), `members`, `priority_order`, `total_canonical_records`, `duplicate_dropped_count`, `overlap_count`, `canonical_records_path`.

**Storage helpers (`data_sources/storage.py`):**
- `reference_pack_dir(system_slug, pack_id, pack_root=None)`
- `reference_pack_canonical_records_path(system_slug, pack_id, pack_root=None)`
- `reference_pack_manifest_path(system_slug, pack_id, pack_root=None)`

The `pack_root` parameter defaults to `data/external/reference_packs/` under the workspace root; tests use `tmp_path / "packs"` to avoid writing into the workspace during test runs.

### Task 2: Benchmark-ready reference-aware configs and CLI routing

**New committed configs:**
- `al_cu_fe_reference_aware.yaml` — `source_registry_v1`, real mode, `ingestion.reference_pack` with pack_id `al_cu_fe_v1`, two members (HYPOD-X pinned 2026-03-09 + Materials Project mp_fixture_v1), priority order `[hypodx, materials_project]`, benchmark corpus and validation snapshot wired.
- `sc_zn_reference_aware.yaml` — same structure for Sc-Zn, `zomic_design` preserved, two members (HYPOD-X fixture_local + COD cod_fixture_v1), priority order `[hypodx, cod]`.

**Thin second-source canonical fixtures committed:**
- `data/external/sources/materials_project/mp_fixture_v1/canonical_records.jsonl` — 2 MP records for Al-Cu-Fe.
- `data/external/sources/cod/cod_fixture_v1/canonical_records.jsonl` — 1 COD record for Sc-Zn.
- `data/external/sources/hypodx/hypodx_pinned_2026_03_09/canonical_records.jsonl` — 5 canonical records staged from the pinned HYPOD-X snapshot.
- `data/external/sources/hypodx/hypodx_fixture_local/canonical_records.jsonl` — 1 Sc-Zn record from the local HYPOD-X fixture.

**CLI extension (`cli.py`):**
- New `_ingest_via_reference_pack(config, out_path)` — assembles pack, projects canonical records into processed IngestRecords, writes output JSONL, returns `IngestSummary` and `source_lineage` dict with pack provenance.
- Ingest command detects `ingestion.reference_pack` is set and routes through `_ingest_via_reference_pack` before the existing single-source `_ingest_via_source_registry` path.

## Tests Added

| File | Tests Added | Coverage |
|------|-------------|----------|
| `tests/test_reference_packs.py` | 15 | Config validation, single/multi-source assembly, deduplication, manifest fields, member lineage, cache reuse/bypass, missing-source error, fingerprint determinism, explicit priority ordering |
| `tests/test_benchmarking.py` | 31 | Both configs validate as SystemConfig; pack IDs, member source keys, snapshot IDs, priority ordering, benchmark corpus, validation snapshots, Zomic design path (Sc-Zn), second-source fixture existence |

**Total tests in suite: 151 (all passing)**

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] Added `pack_root` override to storage helpers**
- **Found during:** Task 1 test implementation
- **Issue:** `reference_pack_dir` used `workspace_root()` unconditionally, causing tests to write into the repo's `data/external/reference_packs/` directory instead of `tmp_path`.
- **Fix:** Added optional `pack_root` parameter to all three reference-pack storage functions; updated `assemble_reference_pack` and `load_cached_pack_manifest` to thread `pack_root` through; updated all tests to use `pack_root=str(tmp_path / "packs")`.
- **Files modified:** `data_sources/storage.py`, `data_sources/reference_packs.py`, `tests/test_reference_packs.py`
- **Commit:** 0ab3bfce (inlined in Task 1 before commit)

**2. [Rule 2 - Missing critical functionality] CLI reference-pack routing**
- **Found during:** Task 2 config implementation
- **Issue:** The existing `_ingest_via_source_registry` function calls `resolve_source_adapter(ingestion.source_key, ...)` which fails when `source_key=""` (the reference-pack case). Without this fix, the new configs would not be end-to-end runnable.
- **Fix:** Added `_ingest_via_reference_pack` function and added reference-pack detection logic in the ingest command.
- **Files modified:** `cli.py`
- **Commit:** 2ed5e377 (inlined in Task 2 before commit)

**3. [Rule 2 - Missing critical functionality] Removed duplicate schema models from data_sources/schema.py**
- **Found during:** Task 1 cleanup
- **Issue:** `ReferencePackMember` and `ReferencePackConfig` were added to `data_sources/schema.py` and then superseded by `ReferencePackMemberConfig` and `ReferencePackConfig` in `common/schema.py`. Having both would cause confusion and potential import cycles.
- **Fix:** Removed the duplicate config-layer models from `data_sources/schema.py`; kept only the disk-artifact models (`ReferencePackMemberResult`, `ReferencePackManifest`) there.
- **Files modified:** `data_sources/schema.py`
- **Commit:** 0ab3bfce (inlined in Task 1 before commit)

## Known Stubs

None. Both benchmark configs reference real fixture paths committed to the repository. The `reuse_cached_pack: true` default means production runs will write packs to `data/external/reference_packs/` on first run and reuse them thereafter.

## Self-Check: PASSED
