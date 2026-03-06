from __future__ import annotations

import pytest

from materials_discovery.common.chemistry import (
    composition_l1_distance,
    describe_candidate,
    describe_composition,
    validate_supported_species,
)
from materials_discovery.common.schema import CandidateRecord


def _candidate() -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": "md_000001",
            "system": "Al-Cu-Fe",
            "template_family": "icosahedral_approximant_1_1",
            "cell": {
                "a": 14.2,
                "b": 14.2,
                "c": 14.2,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            "sites": [
                {
                    "label": "S1",
                    "qphi": [[1, 0], [0, 1], [-1, 1]],
                    "species": "Al",
                    "occ": 1.0,
                }
            ],
            "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            "screen": {},
            "digital_validation": {"status": "pending"},
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def test_describe_candidate_returns_physical_descriptors() -> None:
    descriptor = describe_candidate(_candidate(), strict_pairs=True)
    assert descriptor.qphi_complexity > 0.0
    assert descriptor.pair_mixing_enthalpy_ev_per_atom < 0.0
    assert 0.0 <= descriptor.radius_mismatch <= 1.0
    assert 0.0 <= descriptor.electronegativity_spread <= 1.0
    assert 1.0 <= descriptor.vec <= 12.0


def test_describe_composition_returns_structure_free_descriptors() -> None:
    descriptor = describe_composition({"Al": 0.7, "Cu": 0.2, "Fe": 0.1}, strict_pairs=True)
    assert descriptor.pair_mixing_enthalpy_ev_per_atom < 0.0
    assert descriptor.dominant_fraction == 0.7


def test_validate_supported_species_requires_pair_priors_in_strict_mode() -> None:
    with pytest.raises(ValueError, match="pair-mixing priors"):
        validate_supported_species(["Al", "Cu", "Zn"], strict_pairs=True)


def test_composition_l1_distance_is_symmetric() -> None:
    a = {"Al": 0.7, "Cu": 0.2, "Fe": 0.1}
    b = {"Al": 0.6, "Cu": 0.1, "Fe": 0.3}
    assert composition_l1_distance(a, b) == composition_l1_distance(b, a)
