from __future__ import annotations

import pytest

from materials_discovery.backends.structure_realization import (
    candidate_cartesian_positions,
    candidate_fractional_positions,
)
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    assess_translation_fidelity,
    infer_coordinate_sources,
    prepare_translated_structure,
    resolve_translation_target,
)


def _candidate(
    *,
    candidate_id: str,
    template_family: str,
    sites: list[dict[str, object]],
    provenance: dict[str, object],
) -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": candidate_id,
            "system": "Al-Cu-Fe",
            "template_family": template_family,
            "cell": {
                "a": 10.0,
                "b": 10.0,
                "c": 10.0,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            "sites": sites,
            "composition": {"Al": 0.34, "Cu": 0.33, "Fe": 0.33},
            "provenance": provenance,
        }
    )


def _mixed_origin_candidate() -> CandidateRecord:
    return _candidate(
        candidate_id="translation_core_001",
        template_family="icosahedral_approximant_1_1",
        sites=[
            {
                "label": "S1",
                "qphi": [[1, 0], [0, 1], [0, 0]],
                "species": "Al",
                "occ": 1.0,
                "fractional_position": [0.1, 0.2, 0.3],
                "cartesian_position": [1.0, 2.0, 3.0],
            },
            {
                "label": "S2",
                "qphi": [[0, 1], [1, 0], [0, 0]],
                "species": "Cu",
                "occ": 1.0,
                "cartesian_position": [4.0, 5.0, 6.0],
            },
            {
                "label": "S3",
                "qphi": [[1, 1], [0, 1], [1, 0]],
                "species": "Fe",
                "occ": 1.0,
            },
        ],
        provenance={"qc_family": ["approximant"]},
    )


def _periodic_fractional_candidate() -> CandidateRecord:
    return _candidate(
        candidate_id="translation_core_exact_001",
        template_family="icosahedral_approximant_1_1",
        sites=[
            {
                "label": "S1",
                "qphi": [[1, 0], [0, 1], [0, 0]],
                "species": "Al",
                "occ": 1.0,
                "fractional_position": [0.1, 0.2, 0.3],
            },
            {
                "label": "S2",
                "qphi": [[0, 1], [1, 0], [0, 0]],
                "species": "Cu",
                "occ": 1.0,
                "fractional_position": [0.4, 0.5, 0.6],
            },
        ],
        provenance={"qc_family": ["approximant"]},
    )


def _periodic_cartesian_candidate() -> CandidateRecord:
    return _candidate(
        candidate_id="translation_core_anchored_001",
        template_family="cubic_proxy_1_0",
        sites=[
            {
                "label": "S1",
                "qphi": [[1, 0], [0, 1], [0, 0]],
                "species": "Al",
                "occ": 1.0,
                "cartesian_position": [1.0, 2.0, 3.0],
            },
            {
                "label": "S2",
                "qphi": [[0, 1], [1, 0], [0, 0]],
                "species": "Cu",
                "occ": 1.0,
                "cartesian_position": [4.0, 5.0, 6.0],
            },
        ],
        provenance={"qc_family": ["approximant"]},
    )


def _qc_native_candidate() -> CandidateRecord:
    return _candidate(
        candidate_id="translation_core_lossy_001",
        template_family="pyqcstrc_projection",
        sites=[
            {
                "label": "Q1",
                "qphi": [[1, 0], [0, 1], [1, 1]],
                "species": "Sc",
                "occ": 1.0,
            },
            {
                "label": "Q2",
                "qphi": [[0, 1], [1, 1], [1, 0]],
                "species": "Zn",
                "occ": 1.0,
            },
        ],
        provenance={"qc_family": ["quasicrystal"]},
    )


def test_prepare_translated_structure_preserves_site_order_and_normalized_payload() -> None:
    candidate = _mixed_origin_candidate()
    artifact = prepare_translated_structure(candidate, resolve_translation_target("cif"))

    assert artifact.source.candidate_id == candidate.candidate_id
    assert artifact.target.family == "cif"
    assert artifact.cell == candidate.cell
    assert artifact.emitted_text is None
    assert [site.label for site in artifact.sites] == ["S1", "S2", "S3"]
    assert [site.species for site in artifact.sites] == ["Al", "Cu", "Fe"]
    assert [site.occupancy for site in artifact.sites] == [1.0, 1.0, 1.0]
    assert [site.fractional_position for site in artifact.sites] == candidate_fractional_positions(
        candidate
    )
    assert [site.cartesian_position for site in artifact.sites] == candidate_cartesian_positions(
        candidate
    )


def test_prepare_translated_structure_records_coordinate_sources_in_priority_order() -> None:
    candidate = _mixed_origin_candidate()

    assert infer_coordinate_sources(candidate) == (
        ("S1", "stored_fractional"),
        ("S2", "stored_cartesian"),
        ("S3", "qphi_derived"),
    )

    artifact = prepare_translated_structure(candidate, resolve_translation_target("cif"))
    assert [diagnostic.model_dump(exclude_none=True) for diagnostic in artifact.diagnostics] == [
        {
            "code": "coordinate_derivation_required",
            "severity": "warning",
            "message": "normalized coordinates required derivation for one or more sites",
            "metadata": {
                "site_coordinate_sources": [
                    {"site_label": "S1", "coordinate_source": "stored_fractional"},
                    {"site_label": "S2", "coordinate_source": "stored_cartesian"},
                    {"site_label": "S3", "coordinate_source": "qphi_derived"},
                ]
            },
        }
    ]


def test_prepare_translated_structure_is_byte_stable_for_same_candidate_and_target() -> None:
    candidate = _mixed_origin_candidate()
    target = resolve_translation_target("cif")

    first = prepare_translated_structure(candidate, target)
    second = prepare_translated_structure(candidate, target)

    assert first.model_dump_json() == second.model_dump_json()


def test_assess_translation_fidelity_distinguishes_exact_anchored_and_approximate() -> None:
    target = resolve_translation_target("cif")

    assert assess_translation_fidelity(_periodic_fractional_candidate(), target) == "exact"
    assert assess_translation_fidelity(_periodic_cartesian_candidate(), target) == "anchored"
    assert assess_translation_fidelity(_mixed_origin_candidate(), target) == "approximate"


def test_qphi_derived_or_qc_native_candidates_cannot_silently_claim_exact_periodic_export() -> None:
    target = resolve_translation_target("cif")
    artifact = prepare_translated_structure(_qc_native_candidate(), target)

    assert assess_translation_fidelity(_qc_native_candidate(), target) == "lossy"
    assert artifact.fidelity_tier == "lossy"
    assert artifact.loss_reasons == [
        "aperiodic_to_periodic_proxy",
        "coordinate_derivation_required",
        "qc_semantics_dropped",
    ]


def test_unsupported_exactness_claim_fails_clearly() -> None:
    with pytest.raises(ValueError, match="unsupported exactness claim"):
        assess_translation_fidelity(
            _qc_native_candidate(),
            resolve_translation_target("cif"),
            requested_fidelity="exact",
        )
