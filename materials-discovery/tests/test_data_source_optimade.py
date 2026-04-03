from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import load_jsonl
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.adapters.optimade import OptimadeSourceAdapter
from materials_discovery.data_sources.runtime import stage_source_snapshot
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord


def _config(tmp_path: Path) -> SystemConfig:
    return SystemConfig.model_validate(
        {
            "system_name": "Fe-O",
            "template_family": "cubic_proxy_1_0",
            "species": ["Fe", "O"],
            "composition_bounds": {
                "Fe": {"min": 0.1, "max": 0.8},
                "O": {"min": 0.2, "max": 0.9},
            },
            "coeff_bounds": {"min": -2, "max": 2},
            "seed": 19,
            "default_count": 12,
            "ingestion": {
                "source_key": "optimade_demo",
                "adapter_key": "optimade_v1",
                "snapshot_id": "optimade-demo-run",
                "artifact_root": str(tmp_path),
                "query": {
                    "inline_response": {
                        "data": [
                            {
                                "id": "opt-001",
                                "type": "structures",
                                "attributes": {
                                    "chemical_system": "Fe-O",
                                    "chemical_formula_reduced": "Fe2O3",
                                    "elements": ["Fe", "O"],
                                    "elements_ratios": [0.4, 0.6],
                                    "lattice_vectors": [
                                        [5.0, 0.0, 0.0],
                                        [0.0, 5.0, 0.0],
                                        [0.0, 0.0, 13.6],
                                    ],
                                    "cartesian_site_positions": [
                                        [0.0, 0.0, 0.0],
                                        [2.5, 2.5, 2.5],
                                    ],
                                    "species_at_sites": ["Fe", "O"],
                                    "nsites": 2,
                                    "nelements": 2,
                                },
                            }
                        ]
                    }
                },
            },
        }
    )


def test_optimade_source_adapter_stages_inline_response(tmp_path: Path) -> None:
    adapter = OptimadeSourceAdapter(
        source_key="optimade_demo",
        base_url=None,
        adapter_key="optimade_v1",
        source_name="OPTIMADE Demo",
        default_snapshot="optimade_demo_snapshot_v1",
    )
    summary = stage_source_snapshot(_config(tmp_path), adapter)

    canonical_rows = load_jsonl(tmp_path / "optimade_demo" / "optimade-demo-run" / "canonical_records.jsonl")
    record = CanonicalRawSourceRecord.model_validate(canonical_rows[0])

    assert summary.raw_count == 1
    assert summary.canonical_count == 1
    assert record.source.source_key == "optimade_demo"
    assert record.record_kind == "structure"
    assert record.snapshot.snapshot_id == "optimade-demo-run"
    assert "attribute_keys" in record.source_metadata
