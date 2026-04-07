from __future__ import annotations

import json
from pathlib import Path

import pytest

from materials_discovery.common.io import load_json_object, load_jsonl, write_jsonl
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    TranslationBundleManifest,
    TranslationInventoryRow,
    export_translation_bundle,
    llm_translate_stage_manifest_path,
    llm_translation_export_dir,
    llm_translation_inventory_path,
    llm_translation_manifest_path,
    llm_translation_payload_dir,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_translation"


def _load_candidate_fixture(name: str) -> CandidateRecord:
    fixture_path = FIXTURE_DIR / name
    return CandidateRecord.model_validate(json.loads(fixture_path.read_text()))


def _write_candidate_jsonl(path: Path, candidates: list[CandidateRecord]) -> None:
    write_jsonl([candidate.model_dump(mode="json") for candidate in candidates], path)


def test_translation_bundle_storage_helpers_use_dedicated_export_root(tmp_path: Path) -> None:
    root = tmp_path / "workspace"
    export_id = "demo_export_v1"

    export_dir = llm_translation_export_dir(export_id, root=root)

    assert export_dir == root / "data" / "llm_translation_exports" / export_id
    assert llm_translation_manifest_path(export_id, root=root) == export_dir / "manifest.json"
    assert llm_translation_inventory_path(export_id, root=root) == export_dir / "inventory.jsonl"
    assert llm_translation_payload_dir(export_id, root=root) == export_dir / "payloads"
    assert llm_translate_stage_manifest_path("al_cu_fe", export_id, root=root) == (
        root / "data" / "manifests" / "al_cu_fe_demo_export_v1_llm_translate_manifest.json"
    )


def test_translation_bundle_models_reject_blank_required_strings() -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        TranslationBundleManifest(
            export_id=" ",
            created_at_utc="2026-04-06T23:56:00Z",
            input_path="data/ranked/al_cu_fe_ranked.jsonl",
            target_family="cif",
            target_format="cif_text",
            inventory_path="data/llm_translation_exports/demo/inventory.jsonl",
            payload_dir="data/llm_translation_exports/demo/payloads",
            candidate_count=1,
            exported_count=1,
            lossy_count=0,
        )

    with pytest.raises(ValueError, match="must not be blank"):
        TranslationInventoryRow(
            export_id="demo_export_v1",
            candidate_id="candidate_001",
            system="Al-Cu-Fe",
            template_family="ico",
            target_family="cif",
            target_format="cif_text",
            fidelity_tier="exact",
            composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            payload_path=" ",
            payload_hash="deadbeef",
            emitted_text="data_demo\n",
        )


def test_translation_inventory_row_preserves_target_fidelity_and_emitted_text() -> None:
    row = TranslationInventoryRow(
        export_id="demo_export_v1",
        candidate_id="candidate_001",
        system="Al-Cu-Fe",
        template_family="ico",
        target_family="material_string",
        target_format="crystaltextllm_material_string",
        fidelity_tier="lossy",
        loss_reasons=[
            "aperiodic_to_periodic_proxy",
            "coordinate_derivation_required",
            "qc_semantics_dropped",
        ],
        diagnostic_codes=[
            "coordinate_derivation_required",
            "periodic_proxy_required",
            "qc_semantics_dropped",
        ],
        composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        payload_path="data/llm_translation_exports/demo/payloads/candidate_001.material_string.txt",
        payload_hash="deadbeef",
        emitted_text="1.0 1.0 1.0\n90.0 90.0 90.0\nAl\n0.0 0.0 0.0\n",
    )

    assert row.target_family == "material_string"
    assert row.fidelity_tier == "lossy"
    assert row.loss_reasons == [
        "aperiodic_to_periodic_proxy",
        "coordinate_derivation_required",
        "qc_semantics_dropped",
    ]
    assert row.emitted_text.startswith("1.0 1.0 1.0")


def test_export_translation_bundle_writes_payloads_inventory_and_manifest_for_periodic_fixture(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    input_path = workspace / "data" / "ranked" / "al_cu_fe_ranked.jsonl"
    candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    _write_candidate_jsonl(input_path, [candidate])

    summary = export_translation_bundle(
        candidates=[candidate],
        input_path=input_path,
        target_family="cif",
        export_id="al_cu_fe_cif_v1",
        root=workspace,
    )

    assert Path(summary.manifest_path).exists()
    assert Path(summary.inventory_path).exists()
    assert Path(summary.payload_dir).is_dir()
    assert summary.exported_count == 1

    manifest = TranslationBundleManifest.model_validate(load_json_object(Path(summary.manifest_path)))
    rows = [TranslationInventoryRow.model_validate(row) for row in load_jsonl(Path(summary.inventory_path))]

    assert manifest.target_family == "cif"
    assert manifest.candidate_count == 1
    assert manifest.exported_count == 1
    assert rows[0].candidate_id == candidate.candidate_id
    assert rows[0].payload_path.endswith(".cif")
    assert Path(workspace / rows[0].payload_path).read_text(encoding="utf-8") == rows[0].emitted_text
    assert rows[0].emitted_text.startswith("# source_candidate_id=")


def test_export_translation_bundle_preserves_lossy_semantics_without_breaking_raw_material_string_body(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    input_path = workspace / "data" / "ranked" / "sc_zn_ranked.jsonl"
    candidate = _load_candidate_fixture("sc_zn_qc_candidate.json")
    _write_candidate_jsonl(input_path, [candidate])

    summary = export_translation_bundle(
        candidates=[candidate],
        input_path=input_path,
        target_family="material_string",
        export_id="sc_zn_material_v1",
        root=workspace,
    )

    rows = [TranslationInventoryRow.model_validate(row) for row in load_jsonl(Path(summary.inventory_path))]

    assert summary.lossy_count == 1
    assert rows[0].fidelity_tier == "lossy"
    assert rows[0].loss_reasons == [
        "aperiodic_to_periodic_proxy",
        "coordinate_derivation_required",
        "qc_semantics_dropped",
    ]
    assert rows[0].payload_path.endswith(".material_string.txt")
    assert not rows[0].emitted_text.startswith("#")
    assert Path(workspace / rows[0].payload_path).read_text(encoding="utf-8") == rows[0].emitted_text


def test_export_translation_bundle_is_byte_stable_for_same_fixture_and_export_id(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    input_path = workspace / "data" / "ranked" / "al_cu_fe_ranked.jsonl"
    candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    _write_candidate_jsonl(input_path, [candidate])

    first = export_translation_bundle(
        candidates=[candidate],
        input_path=input_path,
        target_family="cif",
        export_id="al_cu_fe_cif_v1",
        root=workspace,
    )
    second = export_translation_bundle(
        candidates=[candidate],
        input_path=input_path,
        target_family="cif",
        export_id="al_cu_fe_cif_v1",
        root=workspace,
    )

    assert Path(first.manifest_path).read_text(encoding="utf-8") == Path(second.manifest_path).read_text(
        encoding="utf-8"
    )
    assert Path(first.inventory_path).read_text(encoding="utf-8") == Path(second.inventory_path).read_text(
        encoding="utf-8"
    )
