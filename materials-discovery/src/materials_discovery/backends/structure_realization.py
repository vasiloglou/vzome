from __future__ import annotations

import importlib
from math import cos, pi, sin, sqrt
from typing import Any

from materials_discovery.common.schema import CandidateRecord, QPhiCoord, QPhiPair

PHI = (1.0 + 5.0**0.5) / 2.0
_OFFSET_VECTORS: tuple[tuple[float, float, float], ...] = (
    (0.0, 0.0, 0.0),
    (0.131, 0.173, 0.197),
    (0.223, 0.089, 0.157),
    (0.307, 0.271, 0.113),
    (0.419, 0.347, 0.263),
    (0.541, 0.433, 0.359),
)
_MIN_FRACTIONAL_SEPARATION = 0.085


def qphi_pair_to_float(pair: QPhiPair) -> float:
    return float(pair[0]) + float(pair[1]) * PHI


def qphi_coord_to_float(coord: QPhiCoord) -> tuple[float, float, float]:
    return tuple(qphi_pair_to_float(pair) for pair in coord)  # type: ignore[return-value]


def _normalized_axis(values: list[float]) -> list[float]:
    if not values:
        return []
    low = min(values)
    high = max(values)
    span = high - low
    if span < 1e-9:
        count = len(values)
        return [round((index + 1) / (count + 1), 6) for index in range(count)]
    return [round(0.12 + 0.76 * ((value - low) / span), 6) for value in values]


def _periodic_axis_delta(first: float, second: float) -> float:
    delta = abs(first - second)
    return min(delta, 1.0 - delta)


def _fractional_distance(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> float:
    dx = _periodic_axis_delta(first[0], second[0])
    dy = _periodic_axis_delta(first[1], second[1])
    dz = _periodic_axis_delta(first[2], second[2])
    return float(sqrt(dx * dx + dy * dy + dz * dz))


def candidate_fractional_positions(candidate: CandidateRecord) -> list[tuple[float, float, float]]:
    raw_positions = [qphi_coord_to_float(site.qphi) for site in candidate.sites]
    x_axis = _normalized_axis([position[0] for position in raw_positions])
    y_axis = _normalized_axis([position[1] for position in raw_positions])
    z_axis = _normalized_axis([position[2] for position in raw_positions])

    positions: list[tuple[float, float, float]] = []
    for index, (base_x, base_y, base_z) in enumerate(zip(x_axis, y_axis, z_axis, strict=True)):
        seed = index + 1
        fractional = (
            (base_x + 0.023 * ((seed * PHI) % 1.0)) % 1.0,
            (base_y + 0.019 * (((seed + 1) * PHI) % 1.0)) % 1.0,
            (base_z + 0.017 * (((seed + 2) * PHI) % 1.0)) % 1.0,
        )
        for offset_x, offset_y, offset_z in _OFFSET_VECTORS:
            shifted = (
                round((fractional[0] + offset_x) % 1.0, 6),
                round((fractional[1] + offset_y) % 1.0, 6),
                round((fractional[2] + offset_z) % 1.0, 6),
            )
            if all(
                _fractional_distance(shifted, existing) >= _MIN_FRACTIONAL_SEPARATION
                for existing in positions
            ):
                positions.append(shifted)
                break
        else:
            positions.append(
                (
                    round(fractional[0], 6),
                    round(fractional[1], 6),
                    round(fractional[2], 6),
                )
            )
    return positions


def candidate_cell_matrix(candidate: CandidateRecord) -> list[list[float]]:
    a = float(candidate.cell["a"])
    b = float(candidate.cell["b"])
    c = float(candidate.cell["c"])
    alpha = float(candidate.cell["alpha"]) * pi / 180.0
    beta = float(candidate.cell["beta"]) * pi / 180.0
    gamma = float(candidate.cell["gamma"]) * pi / 180.0

    if abs(sin(gamma)) < 1e-9:
        raise ValueError("invalid gamma angle for cell construction")

    vector_a = [a, 0.0, 0.0]
    vector_b = [b * cos(gamma), b * sin(gamma), 0.0]
    cx = c * cos(beta)
    cy = c * (cos(alpha) - cos(beta) * cos(gamma)) / sin(gamma)
    cz_sq = max(0.0, c * c - cx * cx - cy * cy)
    vector_c = [cx, cy, sqrt(cz_sq)]
    return [vector_a, vector_b, vector_c]


def _import_dependency(module_name: str, dependency_name: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        raise RuntimeError(
            f"optional dependency '{dependency_name}' is required; install with "
            "`uv sync --extra dev --extra mlip`"
        ) from exc


def build_ase_atoms(candidate: CandidateRecord) -> Any:
    ase_module = _import_dependency("ase", "ase")
    return ase_module.Atoms(
        symbols=[site.species for site in candidate.sites],
        scaled_positions=candidate_fractional_positions(candidate),
        cell=candidate_cell_matrix(candidate),
        pbc=True,
    )


def build_pymatgen_structure(candidate: CandidateRecord) -> Any:
    core_module = _import_dependency("pymatgen.core", "pymatgen")
    lattice = core_module.Lattice(candidate_cell_matrix(candidate))
    return core_module.Structure(
        lattice,
        [site.species for site in candidate.sites],
        candidate_fractional_positions(candidate),
        coords_are_cartesian=False,
    )
