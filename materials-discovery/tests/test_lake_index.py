"""Tests for lake index rollup and CLI commands."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from materials_discovery.lake.catalog import ARTIFACT_DIRECTORIES, build_directory_catalog
from materials_discovery.lake.index import (
    LakeIndex,
    build_lake_index,
    lake_stats,
    write_lake_index,
)


# ---------------------------------------------------------------------------
# Test 1: build_lake_index scans all ARTIFACT_DIRECTORIES and returns aggregated index
# ---------------------------------------------------------------------------


def test_build_lake_index_aggregates_catalogs(tmp_path: Path) -> None:
    """build_lake_index scans all ARTIFACT_DIRECTORIES, builds catalogs, returns aggregated index."""
    # Create a few artifact directories
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "data" / "candidates").mkdir(parents=True)

    # Write a JSONL file in each
    (tmp_path / "data" / "processed" / "processed.jsonl").write_text(
        '{"candidate_id": "A"}\n{"candidate_id": "B"}\n', encoding="utf-8"
    )
    (tmp_path / "data" / "candidates" / "candidates.jsonl").write_text(
        '{"candidate_id": "C"}\n', encoding="utf-8"
    )

    index = build_lake_index(root=tmp_path)

    assert index.schema_version == "lake-index/v1"
    assert index.artifact_directories >= 2
    assert index.total_entries >= 2
    assert "data/processed" in index.catalogs or any(
        "processed" in k for k in index.catalogs
    )


# ---------------------------------------------------------------------------
# Test 2: build_lake_index skips directories that do not exist
# ---------------------------------------------------------------------------


def test_build_lake_index_skips_missing_directories(tmp_path: Path) -> None:
    """build_lake_index skips directories that do not exist (no error)."""
    # Don't create any directories — all ARTIFACT_DIRECTORIES will be absent
    index = build_lake_index(root=tmp_path)

    # Should complete without error with 0 entries
    assert index.artifact_directories == 0
    assert index.total_entries == 0
    assert index.stale_count == 0
    assert isinstance(index.catalogs, dict)


# ---------------------------------------------------------------------------
# Test 3: write_lake_index writes data/lake_index.json with correct schema_version
# ---------------------------------------------------------------------------


def test_write_lake_index_writes_json(tmp_path: Path) -> None:
    """write_lake_index writes data/lake_index.json with schema_version 'lake-index/v1'."""
    index = build_lake_index(root=tmp_path)
    output_path = write_lake_index(index, output_path=tmp_path / "data" / "lake_index.json")

    assert output_path.exists()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "lake-index/v1"
    assert "generated_at_utc" in data
    assert "total_entries" in data


# ---------------------------------------------------------------------------
# Test 4: lake_stats produces summary dict with expected keys
# ---------------------------------------------------------------------------


def test_lake_stats_produces_summary(tmp_path: Path) -> None:
    """lake_stats produces summary dict with artifact_count, stale_count, and timing info."""
    # Create a directory with one artifact
    (tmp_path / "data" / "ranked").mkdir(parents=True)
    (tmp_path / "data" / "ranked" / "ranked.jsonl").write_text(
        '{"candidate_id": "X"}\n', encoding="utf-8"
    )

    index = build_lake_index(root=tmp_path)
    stats = lake_stats(index)

    assert "artifact_directories" in stats
    assert "total_entries" in stats
    assert "stale_count" in stats
    assert isinstance(stats["artifact_directories"], int)
    assert isinstance(stats["total_entries"], int)
    assert isinstance(stats["stale_count"], int)


# ---------------------------------------------------------------------------
# Test 5: CLI integration - mdisc lake index runs without error on tmp workspace
# ---------------------------------------------------------------------------


def test_cli_lake_index_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """mdisc lake index runs without error on a tmp workspace."""
    from materials_discovery.cli import app
    import materials_discovery.common.io as io_module
    import materials_discovery.lake.index as index_module

    # Monkeypatch workspace_root to point to tmp_path for this test
    monkeypatch.setattr(io_module, "workspace_root", lambda: tmp_path)
    monkeypatch.setattr(index_module, "_workspace_root", lambda: tmp_path)

    # Create a minimal artifact directory
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "data" / "processed" / "out.jsonl").write_text(
        '{"candidate_id": "A"}\n', encoding="utf-8"
    )

    runner = CliRunner()
    result = runner.invoke(app, ["lake", "index"])

    assert result.exit_code == 0, f"Command failed:\n{result.output}\n{result.exception}"
    assert "lake_index.json" in result.output or "index" in result.output.lower()


# ---------------------------------------------------------------------------
# Test 6: LakeIndex model validates correctly
# ---------------------------------------------------------------------------


def test_lake_index_model() -> None:
    """LakeIndex model validates all required fields."""
    now = datetime.now(UTC).isoformat()
    index = LakeIndex(
        schema_version="lake-index/v1",
        generated_at_utc=now,
        workspace_root=".",
        artifact_directories=5,
        total_entries=10,
        stale_count=2,
        catalogs={},
    )
    assert index.schema_version == "lake-index/v1"
    assert index.artifact_directories == 5
    assert index.total_entries == 10
    assert index.stale_count == 2
