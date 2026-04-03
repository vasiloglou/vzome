"""Tests for lake catalog generation, staleness detection, and index rollup."""
from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from materials_discovery.lake.catalog import (
    ARTIFACT_DIRECTORIES,
    CatalogEntry,
    DirectoryCatalog,
    build_directory_catalog,
    write_catalog,
)
from materials_discovery.lake.staleness import check_staleness


# ---------------------------------------------------------------------------
# Test 1: CatalogEntry model validates all required fields
# ---------------------------------------------------------------------------


def test_catalog_entry_required_fields() -> None:
    """CatalogEntry model validates all required fields."""
    now = datetime.now(UTC).isoformat()
    entry = CatalogEntry(
        artifact_type="processed",
        directory_path="data/processed",
        schema_version="v1",
        record_count=42,
        last_modified_utc=now,
        lineage={},
        size_bytes=1024,
        is_stale=False,
        content_hash=None,
    )
    assert entry.artifact_type == "processed"
    assert entry.directory_path == "data/processed"
    assert entry.schema_version == "v1"
    assert entry.record_count == 42
    assert entry.last_modified_utc == now
    assert entry.lineage == {}
    assert entry.size_bytes == 1024
    assert entry.is_stale is False
    assert entry.content_hash is None


def test_directory_catalog_model() -> None:
    """DirectoryCatalog model validates correctly."""
    now = datetime.now(UTC).isoformat()
    entry = CatalogEntry(
        artifact_type="candidates",
        directory_path="data/candidates",
        schema_version="unknown",
        record_count=0,
        last_modified_utc=now,
        lineage={},
        size_bytes=0,
        is_stale=True,
        content_hash=None,
    )
    catalog = DirectoryCatalog(
        schema_version="catalog/v1",
        generated_at_utc=now,
        entries=[entry],
    )
    assert catalog.schema_version == "catalog/v1"
    assert len(catalog.entries) == 1


# ---------------------------------------------------------------------------
# Test 2: build_directory_catalog scans JSONL files and counts records correctly
# ---------------------------------------------------------------------------


def test_build_directory_catalog_jsonl_record_count(tmp_path: Path) -> None:
    """build_directory_catalog produces correct record_count and size_bytes for JSONL files."""
    artifact_dir = tmp_path / "processed"
    artifact_dir.mkdir()

    # Write a JSONL file with 3 records
    jsonl_file = artifact_dir / "output.jsonl"
    lines = [
        '{"candidate_id": "A", "schema_version": "candidate/v1"}\n',
        '{"candidate_id": "B", "schema_version": "candidate/v1"}\n',
        '{"candidate_id": "C", "schema_version": "candidate/v1"}\n',
    ]
    jsonl_file.write_text("".join(lines), encoding="utf-8")

    catalog = build_directory_catalog(artifact_dir, "processed")
    assert len(catalog.entries) == 1
    entry = catalog.entries[0]
    assert entry.record_count == 3
    assert entry.size_bytes == jsonl_file.stat().st_size
    assert entry.artifact_type == "processed"


# ---------------------------------------------------------------------------
# Test 3: build_directory_catalog generates workspace-relative lineage paths
# ---------------------------------------------------------------------------


def test_build_directory_catalog_workspace_relative_paths() -> None:
    """build_directory_catalog generates workspace-relative lineage paths for workspace dirs."""
    import tempfile
    from materials_discovery.common.io import workspace_root

    # Use a real subdirectory INSIDE the workspace so workspace_relative works
    ws = workspace_root()
    artifact_dir = ws / "data" / "_test_candidates_tmp"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    try:
        manifest_data = {
            "run_id": "test_run_001",
            "stage": "generate",
            "system": "Al-Cu-Fe",
            "config_hash": "abc123",
            "backend_mode": "mock",
            "backend_versions": {},
            "output_hashes": {"candidates": "deadbeef"},
            "created_at_utc": datetime.now(UTC).isoformat(),
            "source_lineage": None,
            "benchmark_context": None,
        }
        manifest_file = artifact_dir / "manifest.json"
        manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

        jsonl_file = artifact_dir / "candidates.jsonl"
        jsonl_file.write_text('{"candidate_id": "X"}\n', encoding="utf-8")

        catalog = build_directory_catalog(artifact_dir, "candidates")
        entry = catalog.entries[0]
        # directory_path must be workspace-relative (not absolute)
        assert not entry.directory_path.startswith("/"), (
            f"Expected workspace-relative path, got: {entry.directory_path}"
        )
        assert entry.directory_path == "data/_test_candidates_tmp", (
            f"Unexpected path: {entry.directory_path}"
        )
        # All lineage values must be workspace-relative too
        for key, value in entry.lineage.items():
            assert not str(value).startswith("/"), (
                f"Lineage value for '{key}' is absolute: {value}"
            )
    finally:
        import shutil
        shutil.rmtree(artifact_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Test 4: check_staleness returns True when directory mtime is newer than catalog
# ---------------------------------------------------------------------------


def test_check_staleness_mtime_newer_than_catalog(tmp_path: Path) -> None:
    """check_staleness returns True when directory mtime is newer than catalog mtime."""
    artifact_dir = tmp_path / "screened"
    artifact_dir.mkdir()
    catalog_path = tmp_path / "_catalog.json"

    # Write a catalog file first (older mtime)
    catalog_path.write_text("{}", encoding="utf-8")
    old_mtime = catalog_path.stat().st_mtime

    # Touch a file inside the directory with a newer mtime
    new_file = artifact_dir / "new_output.jsonl"
    new_file.write_text('{"record": 1}\n', encoding="utf-8")

    # Force directory's newest mtime to be clearly after the catalog
    import os
    future_time = old_mtime + 10
    os.utime(new_file, (future_time, future_time))

    assert check_staleness(artifact_dir, catalog_path) is True


# ---------------------------------------------------------------------------
# Test 5: check_staleness returns True when manifest output_hash differs
# ---------------------------------------------------------------------------


def test_check_staleness_hash_changed(tmp_path: Path) -> None:
    """check_staleness returns True when a manifest output_hash differs from catalog content_hash."""
    artifact_dir = tmp_path / "ranked"
    artifact_dir.mkdir()

    # Write a manifest
    manifest_data = {
        "run_id": "run_002",
        "stage": "rank",
        "system": "Al-Cu-Fe",
        "config_hash": "cfg123",
        "backend_mode": "mock",
        "backend_versions": {},
        "output_hashes": {"ranked": "newhash"},
        "created_at_utc": datetime.now(UTC).isoformat(),
        "source_lineage": None,
        "benchmark_context": None,
    }
    manifest_file = artifact_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest_data), encoding="utf-8")

    # Write a catalog that records a DIFFERENT content_hash
    old_content_hash = "oldhash_different"
    catalog_data = {
        "schema_version": "catalog/v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "entries": [
            {
                "artifact_type": "ranked",
                "directory_path": "data/ranked",
                "schema_version": "unknown",
                "record_count": 0,
                "last_modified_utc": datetime.now(UTC).isoformat(),
                "lineage": {},
                "size_bytes": 0,
                "is_stale": False,
                "content_hash": old_content_hash,
            }
        ],
    }
    catalog_path = artifact_dir / "_catalog.json"
    catalog_path.write_text(json.dumps(catalog_data), encoding="utf-8")

    assert check_staleness(artifact_dir, catalog_path) is True


# ---------------------------------------------------------------------------
# Test 6: check_staleness returns False when nothing has changed
# ---------------------------------------------------------------------------


def test_check_staleness_no_change(tmp_path: Path) -> None:
    """check_staleness returns False when nothing has changed."""
    artifact_dir = tmp_path / "hifi_validated"
    artifact_dir.mkdir()

    # Write a JSONL file
    jsonl_file = artifact_dir / "hifi.jsonl"
    jsonl_file.write_text('{"record": 1}\n', encoding="utf-8")

    # Write a catalog file with a newer mtime (simulate fresh catalog)
    catalog_path = artifact_dir / "_catalog.json"
    # Create catalog data (no manifest, so no hash check)
    catalog_data = {
        "schema_version": "catalog/v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "entries": [],
    }
    catalog_path.write_text(json.dumps(catalog_data), encoding="utf-8")

    # Set catalog mtime to be NEWER than the files in the dir
    import os
    future_time = jsonl_file.stat().st_mtime + 100
    os.utime(catalog_path, (future_time, future_time))

    assert check_staleness(artifact_dir, catalog_path) is False


# ---------------------------------------------------------------------------
# Test 7: ARTIFACT_DIRECTORIES covers all artifact classes
# ---------------------------------------------------------------------------


def test_artifact_directories_coverage() -> None:
    """Catalog covers all artifact classes — not just the D-01 subset."""
    expected_types = {
        "source_snapshot",
        "reference_pack",
        "processed",
        "candidates",
        "screened",
        "hifi_validated",
        "ranked",
        "active_learning",
        "prototypes",
        "calibration",
        "benchmarks",
        "reports",
        "manifests",
        "execution_cache",
    }
    artifact_types = set(ARTIFACT_DIRECTORIES.values())
    missing = expected_types - artifact_types
    assert not missing, f"ARTIFACT_DIRECTORIES missing types: {missing}"
    # Must have at least 14 entries
    assert len(ARTIFACT_DIRECTORIES) >= 14, (
        f"Expected >= 14 artifact directories, got {len(ARTIFACT_DIRECTORIES)}"
    )


# ---------------------------------------------------------------------------
# Test 8: write_catalog writes _catalog.json into the directory
# ---------------------------------------------------------------------------


def test_write_catalog(tmp_path: Path) -> None:
    """write_catalog writes _catalog.json and returns the path."""
    artifact_dir = tmp_path / "reports"
    artifact_dir.mkdir()

    # Write a dummy JSONL
    (artifact_dir / "report.jsonl").write_text('{"data": 1}\n', encoding="utf-8")

    catalog = build_directory_catalog(artifact_dir, "reports")
    catalog_path = write_catalog(catalog, artifact_dir)

    assert catalog_path.exists()
    assert catalog_path.name == "_catalog.json"
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "catalog/v1"
    assert len(data["entries"]) == 1
