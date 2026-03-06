from __future__ import annotations

import numpy as np

from materials_discovery.backends.structure_realization import (
    candidate_cell_matrix,
    candidate_fractional_positions,
)
from materials_discovery.common.schema import CandidateRecord


def _candidate() -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": "md_realize_001",
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
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def test_fractional_positions_are_in_unit_cell_and_separated() -> None:
    positions = candidate_fractional_positions(_candidate())

    assert len(positions) == 3
    for position in positions:
        assert all(0.0 <= value < 1.0 for value in position)
    assert len(set(positions)) == len(positions)


def test_cell_matrix_has_positive_volume() -> None:
    matrix = np.asarray(candidate_cell_matrix(_candidate()), dtype=float)
    assert matrix.shape == (3, 3)
    assert float(np.linalg.det(matrix)) > 0.0
