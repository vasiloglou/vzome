from __future__ import annotations

import json
from pathlib import Path

import pytest

from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    assess_translation_fidelity,
    prepare_translated_structure,
    resolve_translation_target,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_translation"


def _load_candidate_fixture(name: str) -> CandidateRecord:
    fixture_path = FIXTURE_DIR / name
    return CandidateRecord.model_validate(json.loads(fixture_path.read_text()))


@pytest.mark.parametrize("target_family", ["cif", "material_string"])
def test_periodic_fixture_round_trips_with_stable_exact_expectations(target_family: str) -> None:
    candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    target = resolve_translation_target(target_family)

    first = prepare_translated_structure(candidate, target)
    second = prepare_translated_structure(candidate, target)

    assert candidate.provenance["structure_class"] == "periodic_approximant"
    assert all(site.fractional_position is not None for site in candidate.sites)
    assert all(site.cartesian_position is None for site in candidate.sites)
    assert first.source.candidate_id == "al_cu_fe_fixture_periodic_001"
    assert first.target.family == target_family
    assert first.fidelity_tier == "exact"
    assert first.loss_reasons == []
    assert first.diagnostics == []
    assert first.model_dump_json() == second.model_dump_json()
    assert assess_translation_fidelity(candidate, target) == "exact"


@pytest.mark.parametrize("target_family", ["cif", "material_string"])
def test_qc_native_fixture_is_lossy_with_explicit_periodic_proxy_diagnostics(
    target_family: str,
) -> None:
    candidate = _load_candidate_fixture("sc_zn_qc_candidate.json")
    target = resolve_translation_target(target_family)

    artifact = prepare_translated_structure(candidate, target)

    assert candidate.provenance["structure_class"] == "qc_native_projection"
    assert all(site.fractional_position is None for site in candidate.sites)
    assert all(site.cartesian_position is None for site in candidate.sites)
    assert assess_translation_fidelity(candidate, target) == "lossy"
    assert artifact.fidelity_tier == "lossy"
    assert artifact.loss_reasons == [
        "aperiodic_to_periodic_proxy",
        "coordinate_derivation_required",
        "qc_semantics_dropped",
    ]
    assert [diagnostic.code for diagnostic in artifact.diagnostics] == [
        "coordinate_derivation_required",
        "periodic_proxy_required",
        "qc_semantics_dropped",
    ]


def test_fixture_suite_is_rooted_in_repo_files_not_inline_dicts() -> None:
    periodic_path = FIXTURE_DIR / "al_cu_fe_periodic_candidate.json"
    qc_path = FIXTURE_DIR / "sc_zn_qc_candidate.json"

    assert periodic_path.is_file()
    assert qc_path.is_file()
    assert periodic_path.parent == qc_path.parent == FIXTURE_DIR
