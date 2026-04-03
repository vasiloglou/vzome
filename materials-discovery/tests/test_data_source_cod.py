from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.common.io import load_json_object, load_jsonl
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.registry import (
    clear_source_adapters_for_tests,
    list_source_adapters,
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


def _config(tmp_path: Path) -> SystemConfig:
    return SystemConfig.model_validate(
        {
            "system_name": "Sc-Zn",
            "template_family": "cubic_proxy_1_0",
            "species": ["Sc", "Zn"],
            "composition_bounds": {
                "Sc": {"min": 0.1, "max": 0.8},
                "Zn": {"min": 0.2, "max": 0.9},
            },
            "coeff_bounds": {"min": -2, "max": 2},
            "seed": 11,
            "default_count": 10,
            "ingestion": {
                "source_key": "cod",
                "adapter_key": "cif_archive_v1",
                "snapshot_id": "cod-sample-run",
                "artifact_root": str(tmp_path),
            },
        }
    )


def test_cod_source_registry_registers_cif_conversion_adapter() -> None:
    adapters = {(entry.source_key, entry.adapter_key, entry.adapter_family) for entry in list_source_adapters()}
    assert ("cod", "cif_archive_v1", "cif_conversion") in adapters


def test_cod_source_staging_converts_cif_fixture_into_structure_record(tmp_path: Path) -> None:
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "cod_sample.cif"
    adapter = resolve_source_adapter("cod", "cif_archive_v1")
    summary = stage_source_snapshot(_config(tmp_path), adapter, snapshot_path=fixture_path)

    output_dir = tmp_path / "cod" / "cod-sample-run"
    qa_report = load_json_object(output_dir / "qa_report.json")
    canonical_rows = load_jsonl(output_dir / "canonical_records.jsonl")
    record = CanonicalRawSourceRecord.model_validate(canonical_rows[0])

    assert summary.raw_count == 1
    assert summary.canonical_count == 1
    assert qa_report["malformed_structure_count"] == 0
    assert qa_report["passed"] is True
    assert record.record_kind == "structure"
    assert record.source.source_key == "cod"
    assert record.common.structure_representations
    assert record.common.structure_representations[0].payload_format == "cif"
