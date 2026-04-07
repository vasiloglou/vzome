from __future__ import annotations

import json
from pathlib import Path

import pytest

from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    emit_translated_structure,
    prepare_translated_structure,
    resolve_translation_target,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_translation"


def _load_candidate_fixture(name: str) -> CandidateRecord:
    fixture_path = FIXTURE_DIR / name
    return CandidateRecord.model_validate(json.loads(fixture_path.read_text()))


def _expected_output(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("candidate_fixture", "target_family", "expected_fixture"),
    [
        (
            "al_cu_fe_periodic_candidate.json",
            "cif",
            "al_cu_fe_periodic_expected.cif",
        ),
        (
            "al_cu_fe_periodic_candidate.json",
            "material_string",
            "al_cu_fe_periodic_expected.material_string.txt",
        ),
        (
            "sc_zn_qc_candidate.json",
            "cif",
            "sc_zn_qc_expected.cif",
        ),
        (
            "sc_zn_qc_candidate.json",
            "material_string",
            "sc_zn_qc_expected.material_string.txt",
        ),
    ],
)
def test_emit_translated_structure_matches_checked_in_golden_outputs(
    candidate_fixture: str,
    target_family: str,
    expected_fixture: str,
) -> None:
    candidate = _load_candidate_fixture(candidate_fixture)
    artifact = prepare_translated_structure(candidate, resolve_translation_target(target_family))

    emitted = emit_translated_structure(artifact)

    assert emitted.emitted_text == _expected_output(expected_fixture)


def test_all_phase_32_golden_output_files_exist() -> None:
    assert (FIXTURE_DIR / "al_cu_fe_periodic_expected.cif").is_file()
    assert (FIXTURE_DIR / "al_cu_fe_periodic_expected.material_string.txt").is_file()
    assert (FIXTURE_DIR / "sc_zn_qc_expected.cif").is_file()
    assert (FIXTURE_DIR / "sc_zn_qc_expected.material_string.txt").is_file()


def test_lossy_qc_golden_contract_keeps_periodic_proxy_metadata_explicit() -> None:
    candidate = _load_candidate_fixture("sc_zn_qc_candidate.json")
    cif_artifact = emit_translated_structure(
        prepare_translated_structure(candidate, resolve_translation_target("cif"))
    )
    material_artifact = emit_translated_structure(
        prepare_translated_structure(candidate, resolve_translation_target("material_string"))
    )

    assert cif_artifact.fidelity_tier == "lossy"
    assert material_artifact.fidelity_tier == "lossy"
    assert cif_artifact.loss_reasons == material_artifact.loss_reasons == [
        "aperiodic_to_periodic_proxy",
        "coordinate_derivation_required",
        "qc_semantics_dropped",
    ]
    assert "# fidelity_tier=lossy" in cif_artifact.emitted_text
    assert "# loss_reasons=aperiodic_to_periodic_proxy,coordinate_derivation_required,qc_semantics_dropped" in cif_artifact.emitted_text
    assert material_artifact.emitted_text == _expected_output(
        "sc_zn_qc_expected.material_string.txt"
    )
    assert not material_artifact.emitted_text.startswith("#")
