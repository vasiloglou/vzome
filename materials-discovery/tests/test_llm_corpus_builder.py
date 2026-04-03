from __future__ import annotations

import json
from pathlib import Path

from materials_discovery.common.io import load_json_object, load_jsonl
from materials_discovery.llm.corpus_builder import build_llm_corpus
from materials_discovery.llm.schema import CorpusBuildConfig


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True))
            handle.write("\n")


def _candidate_payload() -> dict[str, object]:
    return {
        "candidate_id": "sc_zn_candidate_001",
        "system": "Sc-Zn",
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
            },
            {
                "label": "shell.02",
                "qphi": [[0, 0], [0, 1], [0, 0]],
                "species": "Zn",
                "occ": 1.0,
            },
        ],
        "composition": {"Sc": 0.3, "Zn": 0.7},
        "provenance": {"prototype_key": "sc_zn_tsai_bridge"},
    }


def _canonical_payload() -> dict[str, object]:
    return {
        "schema_version": "raw-source-record/v1",
        "local_record_id": "src_cod_1234567890abcdef",
        "record_kind": "structure",
        "source": {
            "source_key": "cod",
            "source_name": "Crystallography Open Database",
            "source_record_id": "cod-001",
        },
        "access": {
            "access_level": "open",
            "auth_required": False,
            "access_surface": "fixture",
            "redistribution_posture": "allowed",
        },
        "license": {
            "license_expression": "CC0-1.0",
            "license_category": "open",
            "attribution_required": False,
        },
        "snapshot": {
            "snapshot_id": "cod_fixture_v1",
            "retrieved_at_utc": "2026-04-03T00:00:00Z",
            "retrieval_mode": "fixture",
            "snapshot_manifest_path": "data/external/sources/cod/cod_fixture_v1/snapshot_manifest.json",
        },
        "raw_payload": {
            "payload_path": "data/external/sources/cod/cod_fixture_v1/raw_rows.jsonl",
            "payload_format": "jsonl",
            "content_hash": "abc123",
        },
        "common": {
            "chemical_system": "Sc-Zn",
            "elements": ["Sc", "Zn"],
            "composition": {"Sc": 0.3333333333, "Zn": 0.6666666667},
            "structure_representations": [
                {
                    "representation_kind": "cif",
                    "payload_path": "tests/fixtures/cod_sample.cif",
                    "payload_format": "cif",
                    "content_hash": "def456",
                    "structure_summary": {},
                }
            ],
        },
        "lineage": {
            "adapter_key": "cif_archive_v1",
            "adapter_family": "cif_conversion",
            "adapter_version": "0.1.0",
            "fetch_manifest_id": "fetch-001",
            "normalize_manifest_id": "normalize-001",
        },
    }


def _config() -> CorpusBuildConfig:
    return CorpusBuildConfig.model_validate(
        {
            "build_id": "builder_demo",
            "systems": ["Sc-Zn"],
            "include_repo_regression": False,
            "include_repo_parts": False,
            "include_materials_designs": True,
            "include_candidate_records": True,
            "include_generated_exports": False,
            "include_canonical_sources": True,
            "include_reference_packs": False,
            "include_pyqcstrc_projection": True,
            "gold_min_sites": 1,
            "gold_max_sites": 20,
            "silver_max_sites": 40,
            "collision_threshold_angstrom": 0.1,
            "source_keys": ["cod"],
            "reference_pack_ids": [],
        }
    )


def _setup_repo_fixture(repo_root: Path) -> None:
    design_path = repo_root / "materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic"
    design_path.parent.mkdir(parents=True, exist_ok=True)
    design_path.write_text("label shell.01\nlabel shell.02\n", encoding="utf-8")

    _write_jsonl(
        repo_root / "materials-discovery/data/candidates/sc_zn_candidates.jsonl",
        [_candidate_payload()],
    )
    _write_jsonl(
        repo_root / "materials-discovery/data/external/sources/cod/cod_fixture_v1/canonical_records.jsonl",
        [_canonical_payload()],
    )

    fixture_dir = repo_root / "materials-discovery/tests/fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    source_cif = Path(__file__).resolve().parent / "fixtures" / "cod_sample.cif"
    (fixture_dir / "cod_sample.cif").write_text(source_cif.read_text(encoding="utf-8"), encoding="utf-8")
    (fixture_dir / "pyqcstrc_projection_sample.json").write_text(
        json.dumps(
            {
                "source": "pyqcstrc",
                "model_id": "sc_zn_projection_001",
                "system": "Sc-Zn",
                "coordinate_system": "qphi",
                "composition": {"Sc": 0.3, "Zn": 0.7},
                "positions": [
                    {"label": "shell.01", "qphi": [[0, 0], [1, 0], [0, 0]], "species": "Sc"},
                    {"label": "shell.02", "qphi": [[0, 0], [0, 1], [0, 0]], "species": "Zn"},
                ],
            }
        ),
        encoding="utf-8",
    )


def test_build_llm_corpus_emits_syntax_and_materials_corpora(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    _setup_repo_fixture(repo_root)
    monkeypatch.setattr(
        "materials_discovery.llm.corpus_builder.compile_zomic_script",
        lambda *args, **kwargs: {
            "parse_status": "passed",
            "compile_status": "passed",
            "raw_export_path": None,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        },
    )

    summary = build_llm_corpus(_config(), root=repo_root)

    assert Path(summary.syntax_corpus_path).exists()
    assert Path(summary.materials_corpus_path).exists()


def test_build_llm_corpus_writes_rejects_inventory_qa_and_manifest(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    _setup_repo_fixture(repo_root)
    monkeypatch.setattr(
        "materials_discovery.llm.corpus_builder.compile_zomic_script",
        lambda *args, **kwargs: {
            "parse_status": "passed",
            "compile_status": "passed",
            "raw_export_path": None,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        },
    )

    summary = build_llm_corpus(_config(), root=repo_root)

    assert Path(summary.rejects_path).exists()
    assert Path(summary.inventory_path).exists()
    assert Path(summary.qa_path).exists()
    assert Path(summary.manifest_path).exists()


def test_syntax_corpus_includes_repo_native_zomic_examples(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    _setup_repo_fixture(repo_root)
    monkeypatch.setattr(
        "materials_discovery.llm.corpus_builder.compile_zomic_script",
        lambda *args, **kwargs: {
            "parse_status": "passed",
            "compile_status": "passed",
            "raw_export_path": None,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        },
    )

    summary = build_llm_corpus(_config(), root=repo_root)
    syntax_rows = load_jsonl(Path(summary.syntax_corpus_path))

    assert any(row["provenance"]["source_family"] == "materials_design" for row in syntax_rows)


def test_materials_corpus_includes_candidate_cif_and_pyqc_examples(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    _setup_repo_fixture(repo_root)
    monkeypatch.setattr(
        "materials_discovery.llm.corpus_builder.compile_zomic_script",
        lambda *args, **kwargs: {
            "parse_status": "passed",
            "compile_status": "passed",
            "raw_export_path": None,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        },
    )

    summary = build_llm_corpus(_config(), root=repo_root)
    materials_rows = load_jsonl(Path(summary.materials_corpus_path))
    families = {row["provenance"]["source_family"] for row in materials_rows}

    assert {"candidate_record", "canonical_source", "pyqcstrc_projection"}.issubset(families)


def test_qa_summary_counts_match_corpus_contents_after_dedupe_and_tiering(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    _setup_repo_fixture(repo_root)
    monkeypatch.setattr(
        "materials_discovery.llm.corpus_builder.compile_zomic_script",
        lambda *args, **kwargs: {
            "parse_status": "passed",
            "compile_status": "passed",
            "raw_export_path": None,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        },
    )

    summary = build_llm_corpus(_config(), root=repo_root)
    qa_summary = load_json_object(Path(summary.qa_path))

    assert qa_summary["gold_count"] + qa_summary["silver_count"] + qa_summary["reject_count"] == summary.syntax_count + summary.reject_count
