from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.common.io import load_jsonl
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.registry import (
    clear_source_adapters_for_tests,
    list_source_adapters,
    register_builtin_source_adapters,
    resolve_source_adapter,
)
from materials_discovery.data_sources.runtime import stage_source_snapshot


@pytest.fixture(autouse=True)
def _builtins_registered() -> None:
    clear_source_adapters_for_tests()
    register_builtin_source_adapters()
    yield
    clear_source_adapters_for_tests()


def _config(
    tmp_path: Path,
    *,
    source_key: str,
    adapter_key: str,
    snapshot_id: str,
    inline_rows: list[dict[str, object]] | None = None,
    inline_response: dict[str, object] | None = None,
) -> SystemConfig:
    query: dict[str, object] = {}
    if inline_rows is not None:
        query["inline_rows"] = inline_rows
    if inline_response is not None:
        query["inline_response"] = inline_response
    return SystemConfig.model_validate(
        {
            "system_name": "Demo-System",
            "template_family": "cubic_proxy_1_0",
            "species": ["A", "B"],
            "composition_bounds": {
                "A": {"min": 0.1, "max": 0.9},
                "B": {"min": 0.1, "max": 0.9},
            },
            "coeff_bounds": {"min": -1, "max": 1},
            "seed": 31,
            "default_count": 4,
            "ingestion": {
                "source_key": source_key,
                "adapter_key": adapter_key,
                "snapshot_id": snapshot_id,
                "artifact_root": str(tmp_path),
                "query": query,
            },
        }
    )


def test_api_source_registry_lists_direct_and_optimade_families() -> None:
    listed = {(entry.source_key, entry.adapter_key, entry.adapter_family) for entry in list_source_adapters()}
    assert ("materials_project", "direct_api_v1", "direct") in listed
    assert ("oqmd", "direct_api_v1", "direct") in listed
    assert ("jarvis", "optimade_v1", "optimade") in listed


def test_api_source_staging_handles_direct_and_optimade_adapters(tmp_path: Path) -> None:
    oqmd_adapter = resolve_source_adapter("oqmd", "direct_api_v1")
    jarvis_adapter = resolve_source_adapter("jarvis", "optimade_v1")

    oqmd_summary = stage_source_snapshot(
        _config(
            tmp_path,
            source_key="oqmd",
            adapter_key="direct_api_v1",
            snapshot_id="oqmd-inline-run",
            inline_rows=[
                {
                    "entry_id": "oqmd-1",
                    "name": "AB2",
                    "composition_string": "A-B",
                    "composition": {"A": 1, "B": 2},
                    "delta_e": 0.012,
                }
            ],
        ),
        oqmd_adapter,
    )
    jarvis_summary = stage_source_snapshot(
        _config(
            tmp_path,
            source_key="jarvis",
            adapter_key="optimade_v1",
            snapshot_id="jarvis-inline-run",
            inline_response={
                "data": [
                    {
                        "id": "jv-1",
                        "type": "structures",
                        "attributes": {
                            "chemical_system": "A-B",
                            "chemical_formula_reduced": "AB2",
                            "elements": ["A", "B"],
                            "elements_ratios": [0.333333, 0.666667],
                            "species_at_sites": ["A", "B", "B"],
                            "nsites": 3,
                        },
                    }
                ]
            },
        ),
        jarvis_adapter,
    )

    oqmd_rows = load_jsonl(tmp_path / "oqmd" / "oqmd-inline-run" / "canonical_records.jsonl")
    jarvis_rows = load_jsonl(tmp_path / "jarvis" / "jarvis-inline-run" / "canonical_records.jsonl")

    assert oqmd_summary.canonical_count == 1
    assert jarvis_summary.canonical_count == 1
    assert oqmd_rows[0]["source"]["source_key"] == "oqmd"
    assert jarvis_rows[0]["source"]["source_key"] == "jarvis"
