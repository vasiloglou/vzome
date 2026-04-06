from __future__ import annotations

from materials_discovery.backends.structure_realization import (
    candidate_cartesian_positions,
    candidate_fractional_positions,
)
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    infer_coordinate_sources,
    prepare_translated_structure,
    resolve_translation_target,
)


def _mixed_origin_candidate() -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": "translation_core_001",
            "system": "Al-Cu-Fe",
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
            "composition": {"Al": 0.34, "Cu": 0.33, "Fe": 0.33},
            "provenance": {"qc_family": ["approximant"]},
        }
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
