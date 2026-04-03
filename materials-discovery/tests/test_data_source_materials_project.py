from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.common.io import load_jsonl
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


def _config(tmp_path: Path) -> SystemConfig:
    return SystemConfig.model_validate(
        {
            "system_name": "Li-Fe-P-O",
            "template_family": "cubic_proxy_1_0",
            "species": ["Li", "Fe", "P", "O"],
            "composition_bounds": {
                "Li": {"min": 0.05, "max": 0.4},
                "Fe": {"min": 0.05, "max": 0.4},
                "P": {"min": 0.05, "max": 0.4},
                "O": {"min": 0.2, "max": 0.8},
            },
            "coeff_bounds": {"min": -2, "max": 2},
            "seed": 29,
            "default_count": 12,
            "ingestion": {
                "source_key": "materials_project",
                "adapter_key": "direct_api_v1",
                "snapshot_id": "mp-inline-run",
                "artifact_root": str(tmp_path),
                "query": {
                    "inline_rows": [
                        {
                            "material_id": "mp-149",
                            "formula_pretty": "LiFePO4",
                            "chemsys": "Fe-Li-O-P",
                            "composition_reduced": {"Li": 1, "Fe": 1, "P": 1, "O": 4},
                            "energy_above_hull": 0.0,
                            "symmetry": {"symbol": "Pnma"},
                            "structure": {
                                "lattice": {"a": 10.33, "b": 6.01, "c": 4.69},
                                "sites": [
                                    {"label": "Li1", "species": "Li"},
                                    {"label": "Fe1", "species": "Fe"},
                                ],
                            },
                        }
                    ]
                },
            },
        }
    )


def test_materials_project_source_stages_inline_payload(tmp_path: Path) -> None:
    adapter = resolve_source_adapter("materials_project", "direct_api_v1")
    summary = stage_source_snapshot(_config(tmp_path), adapter)

    canonical_rows = load_jsonl(tmp_path / "materials_project" / "mp-inline-run" / "canonical_records.jsonl")
    record = CanonicalRawSourceRecord.model_validate(canonical_rows[0])

    assert summary.raw_count == 1
    assert summary.canonical_count == 1
    assert record.source.source_key == "materials_project"
    assert record.record_kind == "structure"
    assert record.source.source_record_id == "mp-149"
