from __future__ import annotations

import pytest

from materials_discovery.backends.native_providers import (
    evaluate_committee_provider,
    evaluate_md_provider,
    evaluate_phonon_provider,
    evaluate_xrd_provider,
)
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _candidate() -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": "md_native_001",
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
                },
                {
                    "label": "S2",
                    "qphi": [[0, 1], [1, 0], [1, 1]],
                    "species": "Cu",
                    "occ": 1.0,
                },
                {
                    "label": "S3",
                    "qphi": [[-1, 1], [1, 0], [0, 1]],
                    "species": "Fe",
                    "occ": 1.0,
                },
            ],
            "composition": {"Al": 0.333333, "Cu": 0.333333, "Fe": 0.333334},
            "digital_validation": {
                "uncertainty_ev_per_atom": 0.01,
                "phonon_imaginary_modes": 0,
                "md_stability_score": 0.7,
            },
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def _config() -> SystemConfig:
    return SystemConfig.model_validate(
        {
            "system_name": "Al-Cu-Fe",
            "template_family": "icosahedral_approximant_1_1",
            "species": ["Al", "Cu", "Fe"],
            "composition_bounds": {
                "Al": {"min": 0.10, "max": 0.80},
                "Cu": {"min": 0.10, "max": 0.80},
                "Fe": {"min": 0.10, "max": 0.80},
            },
            "coeff_bounds": {"min": -3, "max": 3},
            "seed": 17,
            "default_count": 100,
            "backend": {
                "mode": "real",
                "committee_provider": "ase_committee_v1",
                "phonon_provider": "mace_hessian_v1",
                "md_provider": "ase_langevin_v1",
                "xrd_provider": "pymatgen_xrd_v1",
            },
        }
    )


def test_native_committee_provider_fails_cleanly_without_optional_deps() -> None:
    with pytest.raises(RuntimeError, match="uv sync --extra dev --extra mlip"):
        evaluate_committee_provider(_config(), _candidate())


def test_native_phonon_provider_fails_cleanly_without_optional_deps() -> None:
    with pytest.raises(RuntimeError, match="uv sync --extra dev --extra mlip"):
        evaluate_phonon_provider(_config(), _candidate())


def test_native_md_provider_fails_cleanly_without_optional_deps() -> None:
    with pytest.raises(RuntimeError, match="uv sync --extra dev --extra mlip"):
        evaluate_md_provider(_config(), _candidate())


def test_native_xrd_provider_fails_cleanly_without_optional_deps() -> None:
    with pytest.raises(RuntimeError, match="uv sync --extra dev --extra mlip"):
        evaluate_xrd_provider(_config(), _candidate())
