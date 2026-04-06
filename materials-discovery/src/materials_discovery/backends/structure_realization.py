from __future__ import annotations

import importlib
from typing import Any, Literal

from materials_discovery.common.coordinates import (
    cartesian_positions_from_fractional,
    cartesian_to_fractional,
    cell_matrix_from_cell,
    fractional_positions_from_qphi_coords,
)
from materials_discovery.common.schema import CandidateRecord

CoordinateSource = Literal["stored_fractional", "stored_cartesian", "qphi_derived"]


def candidate_fractional_positions_with_sources(
    candidate: CandidateRecord,
) -> list[tuple[tuple[float, float, float], CoordinateSource]]:
    fallback_positions = fractional_positions_from_qphi_coords(
        [site.qphi for site in candidate.sites]
    )
    cell_matrix = cell_matrix_from_cell(candidate.cell)

    positions: list[tuple[tuple[float, float, float], CoordinateSource]] = []
    for index, site in enumerate(candidate.sites):
        if site.fractional_position is not None:
            positions.append((site.fractional_position, "stored_fractional"))
        elif site.cartesian_position is not None:
            positions.append(
                (cartesian_to_fractional(site.cartesian_position, cell_matrix), "stored_cartesian")
            )
        else:
            positions.append((fallback_positions[index], "qphi_derived"))
    return positions


def candidate_fractional_positions(candidate: CandidateRecord) -> list[tuple[float, float, float]]:
    return [position for position, _ in candidate_fractional_positions_with_sources(candidate)]


def candidate_cartesian_positions(candidate: CandidateRecord) -> list[tuple[float, float, float]]:
    cell_matrix = cell_matrix_from_cell(candidate.cell)
    if all(site.cartesian_position is not None for site in candidate.sites):
        return [
            site.cartesian_position
            for site in candidate.sites
            if site.cartesian_position is not None
        ]
    return cartesian_positions_from_fractional(
        candidate_fractional_positions(candidate),
        cell_matrix,
    )


def candidate_cell_matrix(candidate: CandidateRecord) -> list[list[float]]:
    return cell_matrix_from_cell(candidate.cell)


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
