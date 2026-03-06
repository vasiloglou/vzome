from __future__ import annotations

import pytest
from pydantic import ValidationError

from materials_discovery.common.schema import CandidateRecord, SystemConfig


def valid_candidate_payload() -> dict[str, object]:
    return {
        "candidate_id": "md_000001",
        "system": "Al-Cu-Fe",
        "template_family": "icosahedral_approximant_1_1",
        "cell": {"a": 14.2, "b": 14.2, "c": 14.2, "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
        "sites": [
            {
                "label": "S1",
                "qphi": [[1, 0], [0, 1], [-1, 1]],
                "species": "Al",
                "occ": 1.0,
                "fractional_position": [0.2, 0.3, 0.4],
                "cartesian_position": [2.84, 4.26, 5.68],
            }
        ],
        "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        "screen": {"model": "MACE", "energy_per_atom_ev": -3.12},
        "digital_validation": {
            "status": "pending",
            "committee": ["MACE", "CHGNet", "MatterSim"],
            "uncertainty_ev_per_atom": None,
        },
        "provenance": {"generator_version": "0.1.0", "config_hash": "sha256:123"},
    }


def test_valid_candidate_parses() -> None:
    candidate = CandidateRecord.model_validate(valid_candidate_payload())
    assert candidate.candidate_id == "md_000001"


def test_invalid_occupancy_rejected() -> None:
    payload = valid_candidate_payload()
    payload["sites"][0]["occ"] = 1.2  # type: ignore[index]

    with pytest.raises(ValidationError):
        CandidateRecord.model_validate(payload)


def test_invalid_qphi_shape_rejected() -> None:
    payload = valid_candidate_payload()
    payload["sites"][0]["qphi"] = [[1, 0], [0, 1]]  # type: ignore[index]

    with pytest.raises(ValidationError):
        CandidateRecord.model_validate(payload)


def test_invalid_fractional_position_rejected() -> None:
    payload = valid_candidate_payload()
    payload["sites"][0]["fractional_position"] = [1.0, 0.2, 0.3]  # type: ignore[index]

    with pytest.raises(ValidationError):
        CandidateRecord.model_validate(payload)


def test_composition_sum_validation() -> None:
    payload = valid_candidate_payload()
    payload["composition"] = {"Al": 0.7, "Cu": 0.2, "Fe": 0.2}

    with pytest.raises(ValidationError):
        CandidateRecord.model_validate(payload)


def test_system_config_backend_mode_validation() -> None:
    payload = {
        "system_name": "Al-Cu-Fe",
        "template_family": "icosahedral_approximant_1_1",
        "species": ["Al", "Cu", "Fe"],
        "composition_bounds": {
            "Al": {"min": 0.6, "max": 0.8},
            "Cu": {"min": 0.1, "max": 0.25},
            "Fe": {"min": 0.05, "max": 0.2},
        },
        "coeff_bounds": {"min": -3, "max": 3},
        "seed": 17,
        "default_count": 100,
        "backend": {"mode": "invalid"},
    }

    with pytest.raises(ValidationError):
        SystemConfig.model_validate(payload)
