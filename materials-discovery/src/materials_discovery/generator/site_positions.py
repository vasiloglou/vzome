from __future__ import annotations

from materials_discovery.common.coordinates import (
    cartesian_positions_from_fractional,
    cell_matrix_from_cell,
    fractional_positions_from_qphi_coords,
)
from materials_discovery.common.schema import QPhiCoord


def site_positions_from_qphi(
    qphi_coords: list[QPhiCoord],
    cell: dict[str, float],
) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]]]:
    fractional_positions = fractional_positions_from_qphi_coords(qphi_coords)
    cartesian_positions = cartesian_positions_from_fractional(
        fractional_positions,
        cell_matrix_from_cell(cell),
    )
    return fractional_positions, cartesian_positions
