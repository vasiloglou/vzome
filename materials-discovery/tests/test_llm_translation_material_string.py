from __future__ import annotations

import json
from pathlib import Path

from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    emit_material_string_text,
    emit_translated_structure,
    prepare_translated_structure,
    resolve_translation_target,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_translation"


def _load_candidate_fixture(name: str) -> CandidateRecord:
    fixture_path = FIXTURE_DIR / name
    return CandidateRecord.model_validate(json.loads(fixture_path.read_text()))


def _artifact(name: str):
    candidate = _load_candidate_fixture(name)
    return prepare_translated_structure(candidate, resolve_translation_target("material_string"))


def _parse_material_string(text: str) -> tuple[list[float], list[float], list[tuple[str, list[float]]]]:
    lines = text.splitlines()
    assert len(lines) >= 4
    assert len(lines[2:]) % 2 == 0

    lengths = [float(token) for token in lines[0].split()]
    angles = [float(token) for token in lines[1].split()]
    site_rows = [
        (
            lines[index],
            [float(token) for token in lines[index + 1].split()],
        )
        for index in range(2, len(lines), 2)
    ]
    return lengths, angles, site_rows


def test_emit_material_string_text_uses_crystaltextllm_compatible_body_layout() -> None:
    artifact = _artifact("al_cu_fe_periodic_candidate.json")

    emitted = emit_material_string_text(artifact)
    lengths, angles, site_rows = _parse_material_string(emitted)

    assert emitted.splitlines()[0] != "source_candidate_id"
    assert len(lengths) == 3
    assert lengths == [artifact.cell["a"], artifact.cell["b"], artifact.cell["c"]]
    assert angles == [artifact.cell["alpha"], artifact.cell["beta"], artifact.cell["gamma"]]
    assert [species for species, _ in site_rows] == [site.species for site in artifact.sites]
    assert [coords for _, coords in site_rows] == [
        list(site.fractional_position) for site in artifact.sites
    ]


def test_lossy_qc_native_material_string_body_stays_parseable_without_metadata_preamble() -> None:
    artifact = _artifact("sc_zn_qc_candidate.json")

    emitted = emit_material_string_text(artifact)
    lengths, angles, site_rows = _parse_material_string(emitted)

    assert artifact.fidelity_tier == "lossy"
    assert artifact.loss_reasons == [
        "aperiodic_to_periodic_proxy",
        "coordinate_derivation_required",
        "qc_semantics_dropped",
    ]
    assert len(lengths) == 3
    assert len(angles) == 3
    assert len(site_rows) == len(artifact.sites)
    assert not emitted.startswith("source_candidate_id ")


def test_emit_material_string_text_is_byte_stable_for_same_artifact() -> None:
    artifact = _artifact("al_cu_fe_periodic_candidate.json")

    first = emit_material_string_text(artifact)
    second = emit_material_string_text(artifact)

    assert first == second


def test_emit_translated_structure_uses_material_string_body_formatter() -> None:
    artifact = _artifact("al_cu_fe_periodic_candidate.json")

    emitted_artifact = emit_translated_structure(artifact)

    assert artifact.emitted_text is None
    assert emitted_artifact.emitted_text == emit_material_string_text(artifact)
    _, _, site_rows = _parse_material_string(emitted_artifact.emitted_text)
    assert [species for species, _ in site_rows] == [site.species for site in artifact.sites]
