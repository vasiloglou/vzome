from __future__ import annotations

import json
from pathlib import Path

import pytest

from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    emit_translated_structure,
    prepare_translated_structure,
    resolve_translation_target,
    validate_translated_structure_for_export,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_translation"


def _load_candidate_fixture(name: str) -> CandidateRecord:
    fixture_path = FIXTURE_DIR / name
    return CandidateRecord.model_validate(json.loads(fixture_path.read_text()))


def _periodic_artifact(target_family: str = "cif"):
    candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    return prepare_translated_structure(candidate, resolve_translation_target(target_family))


def test_emit_translated_structure_is_byte_stable_for_same_artifact() -> None:
    artifact = _periodic_artifact()

    first = emit_translated_structure(artifact)
    second = emit_translated_structure(artifact)

    assert artifact.emitted_text is None
    assert first.emitted_text == second.emitted_text
    assert first.model_dump_json() == second.model_dump_json()


def test_validate_translated_structure_for_export_rejects_missing_periodic_cell() -> None:
    artifact = _periodic_artifact().model_copy(update={"cell": None})

    with pytest.raises(ValueError, match="cell"):
        validate_translated_structure_for_export(artifact)


def test_validate_translated_structure_for_export_rejects_empty_sites() -> None:
    artifact = _periodic_artifact().model_copy(update={"sites": []})

    with pytest.raises(ValueError, match="at least one site"):
        validate_translated_structure_for_export(artifact)


def test_validate_translated_structure_for_export_rejects_missing_fractional_coordinates() -> None:
    artifact = _periodic_artifact()
    invalid_site = artifact.sites[0].model_copy(update={"fractional_position": None})
    invalid_artifact = artifact.model_copy(update={"sites": [invalid_site, *artifact.sites[1:]]})

    with pytest.raises(ValueError, match="fractional_position"):
        validate_translated_structure_for_export(invalid_artifact)


def test_emit_translated_structure_returns_copy_with_emitted_text_without_mutating_input() -> None:
    artifact = _periodic_artifact()

    emitted = emit_translated_structure(artifact)

    assert emitted is not artifact
    assert emitted.emitted_text
    assert artifact.emitted_text is None
    assert emitted.source == artifact.source
    assert emitted.sites == artifact.sites


def test_emit_translated_structure_rejects_material_string_until_serializer_lands() -> None:
    artifact = _periodic_artifact("material_string")

    with pytest.raises(
        NotImplementedError,
        match="material_string export not implemented yet",
    ):
        emit_translated_structure(artifact)
