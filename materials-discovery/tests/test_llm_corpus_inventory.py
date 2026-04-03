from __future__ import annotations

import json
from pathlib import Path

from materials_discovery.llm.inventory import (
    build_inventory,
    collect_candidate_inventory,
    collect_generated_export_inventory,
    collect_pyqcstrc_inventory,
    collect_repo_zomic_inventory,
    collect_source_inventory,
)
from materials_discovery.llm.schema import CorpusBuildConfig


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True))
            handle.write("\n")


def _candidate_payload(candidate_id: str, system: str) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "system": system,
        "template_family": "icosahedral_approximant_1_1",
        "cell": {
            "a": 10.0,
            "b": 10.0,
            "c": 10.0,
            "alpha": 90.0,
            "beta": 90.0,
            "gamma": 90.0,
        },
        "sites": [
            {
                "label": "shell.01",
                "qphi": [[0, 0], [1, 0], [0, 0]],
                "species": "Sc",
                "occ": 1.0,
            }
        ],
        "composition": {"Sc": 0.3, "Zn": 0.7},
        "provenance": {"prototype_key": "tsai_demo"},
    }


def _canonical_payload(local_record_id: str, system: str, source_key: str, snapshot_id: str) -> dict[str, object]:
    return {
        "schema_version": "raw-source-record/v1",
        "local_record_id": local_record_id,
        "record_kind": "material_entry",
        "source": {
            "source_key": source_key,
            "source_name": source_key.upper(),
            "source_record_id": f"{system.lower()}|001",
        },
        "access": {
            "access_level": "open",
            "auth_required": False,
            "access_surface": "fixture",
            "redistribution_posture": "allowed",
        },
        "license": {
            "license_expression": "CC-BY-4.0",
            "license_category": "open",
            "attribution_required": True,
        },
        "snapshot": {
            "snapshot_id": snapshot_id,
            "retrieved_at_utc": "2026-04-03T12:00:00Z",
            "retrieval_mode": "fixture",
            "snapshot_manifest_path": f"data/external/sources/{source_key}/{snapshot_id}/snapshot_manifest.json",
        },
        "raw_payload": {
            "payload_path": f"data/external/sources/{source_key}/{snapshot_id}/raw_rows.jsonl",
            "payload_format": "jsonl",
            "content_hash": "abc123",
        },
        "common": {
            "chemical_system": system,
            "elements": system.split("-"),
            "composition": {system.split("-")[0]: 0.5, system.split("-")[1]: 0.5}
            if len(system.split("-")) == 2
            else {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        },
        "lineage": {
            "adapter_key": f"{source_key}_fixture_v1",
            "adapter_family": "direct",
            "adapter_version": "0.1.0",
            "fetch_manifest_id": f"{source_key}_{snapshot_id}_fetch",
            "normalize_manifest_id": f"{source_key}_{snapshot_id}_normalize",
        },
    }


def _build_config(**overrides: object) -> CorpusBuildConfig:
    payload: dict[str, object] = {
        "build_id": "inventory-demo",
        "systems": ["Al-Cu-Fe", "Sc-Zn"],
        "include_repo_regression": True,
        "include_repo_parts": True,
        "include_materials_designs": True,
        "include_candidate_records": True,
        "include_generated_exports": True,
        "include_canonical_sources": True,
        "include_reference_packs": True,
        "include_pyqcstrc_projection": True,
        "gold_min_sites": 2,
        "gold_max_sites": 12,
        "silver_max_sites": 20,
        "collision_threshold_angstrom": 0.1,
        "source_keys": ["hypodx"],
        "reference_pack_ids": ["al_cu_fe_v1"],
    }
    payload.update(overrides)
    return CorpusBuildConfig.model_validate(payload)


def test_collect_repo_zomic_inventory_discovers_all_repo_families(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    regression = repo_root / "core/src/regression/files/Zomic/demo/demo.zomic"
    part = repo_root / "core/src/main/resources/com/vzome/core/parts/noTwist/redStrut.zomic"
    design = repo_root / "materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic"
    for path in (regression, part, design):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("label shell_01\n", encoding="utf-8")

    rows = collect_repo_zomic_inventory(repo_root)

    assert {row.source_family for row in rows} == {
        "repo_regression",
        "repo_parts",
        "materials_design",
    }
    design_row = next(row for row in rows if row.source_family == "materials_design")
    assert design_row.system == "Sc-Zn"
    assert design_row.loader_hint == "native_zomic"


def test_collect_candidate_inventory_discovers_jsonl_records_and_filters_systems(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    candidates_path = repo_root / "materials-discovery/data/candidates/demo_candidates.jsonl"
    _write_jsonl(
        candidates_path,
        [
            _candidate_payload("cand-001", "Sc-Zn"),
            _candidate_payload("cand-002", "Ti-Zr-Ni"),
        ],
    )

    rows = collect_candidate_inventory(repo_root, ["Sc-Zn"])

    assert len(rows) == 1
    assert rows[0].source_record_id == "cand-001"
    assert rows[0].record_locator == {
        "path": "materials-discovery/data/candidates/demo_candidates.jsonl",
        "line": 1,
    }
    assert rows[0].loader_hint == "candidate_record"


def test_collect_generated_export_inventory_reads_raw_exports(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    export_path = repo_root / "materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_text(
        json.dumps(
            {
                "zomic_file": str(
                    repo_root / "materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic"
                ),
                "parser": "antlr4",
                "symmetry": "icosahedral",
                "labeled_points": [{"label": "shell.01"}],
            }
        ),
        encoding="utf-8",
    )

    rows = collect_generated_export_inventory(repo_root)

    assert len(rows) == 1
    assert rows[0].source_record_id == "sc_zn_tsai_bridge"
    assert rows[0].loader_hint == "generated_export"
    assert rows[0].metadata["labeled_point_count"] == 1


def test_collect_source_inventory_discovers_canonical_sources_and_reference_packs(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    source_path = (
        repo_root
        / "materials-discovery/data/external/sources/hypodx/hypodx_fixture_local/canonical_records.jsonl"
    )
    pack_path = (
        repo_root
        / "materials-discovery/data/external/reference_packs/al_cu_fe/al_cu_fe_v1/canonical_records.jsonl"
    )
    _write_jsonl(
        source_path,
        [_canonical_payload("src_hypodx_1234567890abcdef", "Sc-Zn", "hypodx", "hypodx_fixture_local")],
    )
    _write_jsonl(
        pack_path,
        [_canonical_payload("src_hypodx_fedcba0987654321", "Al-Cu-Fe", "hypodx", "hypodx_fixture_local")],
    )

    rows = collect_source_inventory(repo_root, ["hypodx"], ["al_cu_fe_v1"])

    families = {row.source_family for row in rows}
    assert families == {"canonical_source", "reference_pack"}
    pack_row = next(row for row in rows if row.source_family == "reference_pack")
    assert pack_row.loader_hint == "reference_pack"
    assert pack_row.metadata["pack_id"] == "al_cu_fe_v1"
    assert pack_row.record_locator["line"] == 1


def test_collect_pyqcstrc_inventory_supports_committed_fixture_path(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    fixture_path = repo_root / "materials-discovery/tests/fixtures/pyqcstrc_projection_sample.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(
        json.dumps(
            {
                "source": "pyqcstrc",
                "model_id": "ico_demo_v1",
                "system": "Al-Cu-Fe",
                "coordinate_system": "qphi",
                "positions": [{"label": "shell.01"}],
            }
        ),
        encoding="utf-8",
    )

    rows = collect_pyqcstrc_inventory(repo_root)

    assert len(rows) == 1
    assert rows[0].source_family == "pyqcstrc_projection"
    assert rows[0].loader_hint == "pyqcstrc_projection"
    assert rows[0].source_record_id == "ico_demo_v1"


def test_build_inventory_returns_record_addressable_rows_in_deterministic_order(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    design = repo_root / "materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic"
    design.parent.mkdir(parents=True, exist_ok=True)
    design.write_text("label shell.01\n", encoding="utf-8")
    _write_jsonl(
        repo_root / "materials-discovery/data/candidates/demo_candidates.jsonl",
        [_candidate_payload("cand-001", "Sc-Zn")],
    )
    _write_jsonl(
        repo_root
        / "materials-discovery/data/external/sources/hypodx/hypodx_fixture_local/canonical_records.jsonl",
        [_canonical_payload("src_hypodx_1234567890abcdef", "Sc-Zn", "hypodx", "hypodx_fixture_local")],
    )
    pyqc_path = repo_root / "materials-discovery/tests/fixtures/pyqcstrc_projection_sample.json"
    pyqc_path.parent.mkdir(parents=True, exist_ok=True)
    pyqc_path.write_text(
        json.dumps({"source": "pyqcstrc", "model_id": "ico_demo_v1", "system": "Sc-Zn"}),
        encoding="utf-8",
    )

    rows = build_inventory(
        _build_config(
            include_repo_regression=False,
            include_repo_parts=False,
            include_generated_exports=False,
            include_reference_packs=False,
            source_keys=["hypodx"],
            systems=["Sc-Zn"],
        ),
        root=repo_root,
    )

    assert len(rows) == 4
    assert all(row.record_locator for row in rows)
    assert all(row.loader_hint for row in rows)
    assert rows == sorted(
        rows,
        key=lambda row: (
            row.source_family,
            row.system or "",
            row.source_path,
            row.source_record_id,
        ),
    )


def test_build_inventory_finds_real_repo_native_zomic_examples() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    rows = build_inventory(
        _build_config(
            include_candidate_records=False,
            include_generated_exports=False,
            include_canonical_sources=False,
            include_reference_packs=False,
            include_pyqcstrc_projection=False,
        ),
        root=repo_root,
    )

    native_rows = [row for row in rows if row.loader_hint == "native_zomic"]
    assert native_rows
    assert any(row.source_family == "repo_regression" for row in native_rows)
