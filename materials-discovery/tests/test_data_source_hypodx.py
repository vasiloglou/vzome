from __future__ import annotations

import json
from pathlib import Path

import pytest

from materials_discovery.common.io import load_json_object, load_jsonl
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.registry import (
    clear_source_adapters_for_tests,
    register_builtin_source_adapters,
    resolve_source_adapter,
)
from materials_discovery.data_sources.runtime import stage_source_snapshot
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord


@pytest.fixture(autouse=True)
def _builtins_registered() -> None:
    clear_source_adapters_for_tests()
    register_builtin_source_adapters()
    yield
    clear_source_adapters_for_tests()


def _config(tmp_path: Path, *, adapter_key: str, snapshot_id: str) -> SystemConfig:
    return SystemConfig.model_validate(
        {
            "system_name": "Al-Cu-Fe",
            "template_family": "icosahedral_approximant_1_1",
            "species": ["Al", "Cu", "Fe"],
            "composition_bounds": {
                "Al": {"min": 0.1, "max": 0.8},
                "Cu": {"min": 0.1, "max": 0.8},
                "Fe": {"min": 0.1, "max": 0.8},
            },
            "coeff_bounds": {"min": -3, "max": 3},
            "seed": 17,
            "default_count": 100,
            "ingestion": {
                "source_key": "hypodx",
                "adapter_key": adapter_key,
                "snapshot_id": snapshot_id,
                "artifact_root": str(tmp_path),
            },
        }
    )


def test_hypodx_source_fixture_staging_writes_expected_artifacts(tmp_path: Path) -> None:
    adapter = resolve_source_adapter("hypodx", "fixture_json_v1")
    summary = stage_source_snapshot(
        _config(tmp_path, adapter_key="fixture_json_v1", snapshot_id="fixture-run"),
        adapter,
    )

    output_dir = tmp_path / "hypodx" / "fixture-run"
    assert summary.raw_count == 8
    assert summary.canonical_count == 8
    assert (output_dir / "raw_rows.jsonl").exists()
    assert (output_dir / "canonical_records.jsonl").exists()
    assert (output_dir / "qa_report.json").exists()
    assert (output_dir / "snapshot_manifest.json").exists()

    qa_report = load_json_object(output_dir / "qa_report.json")
    assert qa_report["duplicate_collision_count"] == 2
    assert qa_report["canonical_count"] == 8
    assert qa_report["passed"] is False

    canonical_rows = load_jsonl(output_dir / "canonical_records.jsonl")
    first = CanonicalRawSourceRecord.model_validate(canonical_rows[0])
    assert first.source.source_key == "hypodx"
    assert first.snapshot.snapshot_id == "fixture-run"
    assert first.local_record_id.startswith("src_hypodx_")


def test_hypodx_source_pinned_snapshot_staging_filters_invalid_rows(tmp_path: Path) -> None:
    adapter = resolve_source_adapter("hypodx", "pinned_snapshot_v2026_03_09")
    summary = stage_source_snapshot(
        _config(
            tmp_path,
            adapter_key="pinned_snapshot_v2026_03_09",
            snapshot_id="pinned-run",
        ),
        adapter,
    )

    output_dir = tmp_path / "hypodx" / "pinned-run"
    qa_report = load_json_object(output_dir / "qa_report.json")
    manifest = json.loads((output_dir / "snapshot_manifest.json").read_text(encoding="utf-8"))
    canonical_rows = load_jsonl(output_dir / "canonical_records.jsonl")

    assert summary.raw_count == 6
    assert summary.canonical_count == 5
    assert qa_report["canonical_count"] == 5
    assert qa_report["duplicate_collision_count"] == 2
    assert manifest["adapter_key"] == "pinned_snapshot_v2026_03_09"
    assert {row["source"]["source_key"] for row in canonical_rows} == {"hypodx"}
