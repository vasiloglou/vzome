from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from math import sqrt

from materials_discovery.backends.structure_realization import (
    candidate_cell_matrix,
    candidate_fractional_positions,
)
from materials_discovery.common.schema import CandidateRecord, SystemConfig


@dataclass(frozen=True)
class GeometryMetrics:
    minimum_cartesian_distance_angstrom: float
    close_contact_pairs: int
    volume_per_atom_ang3: float


def _cross(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def _dot(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> float:
    return first[0] * second[0] + first[1] * second[1] + first[2] * second[2]


def _fractional_delta(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        ((first[0] - second[0] + 0.5) % 1.0) - 0.5,
        ((first[1] - second[1] + 0.5) % 1.0) - 0.5,
        ((first[2] - second[2] + 0.5) % 1.0) - 0.5,
    )


def _fractional_to_cartesian(
    fractional: tuple[float, float, float],
    cell_matrix: list[list[float]],
) -> tuple[float, float, float]:
    return (
        fractional[0] * cell_matrix[0][0]
        + fractional[1] * cell_matrix[1][0]
        + fractional[2] * cell_matrix[2][0],
        fractional[0] * cell_matrix[0][1]
        + fractional[1] * cell_matrix[1][1]
        + fractional[2] * cell_matrix[2][1],
        fractional[0] * cell_matrix[0][2]
        + fractional[1] * cell_matrix[1][2]
        + fractional[2] * cell_matrix[2][2],
    )


def describe_geometry(
    candidate: CandidateRecord,
    *,
    close_contact_cutoff_angstrom: float,
) -> GeometryMetrics:
    fractional_positions = candidate_fractional_positions(candidate)
    cell_matrix = candidate_cell_matrix(candidate)
    vector_a = (cell_matrix[0][0], cell_matrix[0][1], cell_matrix[0][2])
    vector_b = (cell_matrix[1][0], cell_matrix[1][1], cell_matrix[1][2])
    vector_c = (cell_matrix[2][0], cell_matrix[2][1], cell_matrix[2][2])
    cell_volume = abs(_dot(vector_a, _cross(vector_b, vector_c)))
    if cell_volume <= 0.0:
        raise ValueError(f"candidate {candidate.candidate_id} has non-positive cell volume")

    minimum_distance = float("inf")
    close_contact_pairs = 0
    for index, first in enumerate(fractional_positions):
        for second in fractional_positions[index + 1 :]:
            delta = _fractional_delta(first, second)
            cartesian_delta = _fractional_to_cartesian(delta, cell_matrix)
            distance = sqrt(
                cartesian_delta[0] * cartesian_delta[0]
                + cartesian_delta[1] * cartesian_delta[1]
                + cartesian_delta[2] * cartesian_delta[2]
            )
            minimum_distance = min(minimum_distance, distance)
            if distance < close_contact_cutoff_angstrom:
                close_contact_pairs += 1

    if minimum_distance == float("inf"):
        minimum_distance = 0.0

    return GeometryMetrics(
        minimum_cartesian_distance_angstrom=round(minimum_distance, 6),
        close_contact_pairs=close_contact_pairs,
        volume_per_atom_ang3=round(cell_volume / max(1, len(candidate.sites)), 6),
    )


def run_geometry_prefilter(
    candidates: list[CandidateRecord],
    *,
    config: SystemConfig,
    min_distance_angstrom: float = 1.45,
    close_contact_cutoff_angstrom: float = 1.50,
    max_close_contact_fraction: float = 0.04,
    min_volume_per_atom_ang3: float = 12.0,
    max_volume_per_atom_ang3: float = 45.0,
) -> list[CandidateRecord]:
    """Apply a cheap geometry sanity gate before expensive real-mode phonon checks."""
    if config.backend.mode != "real":
        return candidates

    filtered: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        metrics = describe_geometry(
            copied,
            close_contact_cutoff_angstrom=close_contact_cutoff_angstrom,
        )
        validation = copied.digital_validation.model_copy(deep=True)
        validation.minimum_cartesian_distance_angstrom = (
            metrics.minimum_cartesian_distance_angstrom
        )
        validation.close_contact_pairs = metrics.close_contact_pairs
        validation.volume_per_atom_ang3 = metrics.volume_per_atom_ang3

        max_close_contacts = max(2, int(len(copied.sites) * max_close_contact_fraction))
        reason: str | None = None
        if metrics.minimum_cartesian_distance_angstrom < min_distance_angstrom:
            reason = "min_distance"
        elif metrics.close_contact_pairs > max_close_contacts:
            reason = "close_contacts"
        elif metrics.volume_per_atom_ang3 < min_volume_per_atom_ang3:
            reason = "volume_too_low"
        elif metrics.volume_per_atom_ang3 > max_volume_per_atom_ang3:
            reason = "volume_too_high"

        validation.geometry_prefilter_pass = reason is None
        validation.geometry_prefilter_reason = reason
        if reason is not None:
            validation.status = "geometry_prefilter_failed"
            validation.phonon_imaginary_modes = 99
            validation.phonon_pass = False
            validation.md_stability_score = 0.0
            validation.md_pass = False
            validation.xrd_confidence = 0.0
            validation.xrd_pass = False

        copied.digital_validation = validation
        filtered.append(copied)
    return filtered
