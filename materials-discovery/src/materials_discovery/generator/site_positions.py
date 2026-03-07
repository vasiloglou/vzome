from __future__ import annotations

from math import sqrt

from materials_discovery.common.coordinates import (
    CartesianCoord,
    FractionalCoord,
    cartesian_positions_from_fractional,
    cell_matrix_from_cell,
    qphi_coord_to_float,
)
from materials_discovery.common.schema import QPhiCoord
from materials_discovery.generator.approximant_templates import ApproximantTemplate

_FALLBACK_AXES: tuple[FractionalCoord, ...] = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)
_COLLISION_OFFSETS: tuple[tuple[int, int], ...] = (
    (0, 0),
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, 1),
    (-1, 1),
    (1, -1),
    (-1, -1),
    (2, 0),
    (0, 2),
    (-2, 0),
    (0, -2),
)


def _dot(first: FractionalCoord, second: FractionalCoord) -> float:
    return sum(a * b for a, b in zip(first, second, strict=True))


def _cross(first: FractionalCoord, second: FractionalCoord) -> FractionalCoord:
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def _normalize(vector: FractionalCoord) -> FractionalCoord:
    norm = sqrt(sum(component * component for component in vector))
    if norm <= 1e-12:
        return (0.0, 0.0, 0.0)
    return tuple(component / norm for component in vector)  # type: ignore[return-value]


def _difference(first: FractionalCoord, second: FractionalCoord) -> FractionalCoord:
    return tuple(a - b for a, b in zip(first, second, strict=True))  # type: ignore[return-value]


def _wrap(position: FractionalCoord) -> FractionalCoord:
    return tuple(round(value % 1.0, 6) for value in position)  # type: ignore[return-value]


def _periodic_axis_delta(first: float, second: float) -> float:
    delta = abs(first - second)
    return min(delta, 1.0 - delta)


def _fractional_distance(first: FractionalCoord, second: FractionalCoord) -> float:
    dx = _periodic_axis_delta(first[0], second[0])
    dy = _periodic_axis_delta(first[1], second[1])
    dz = _periodic_axis_delta(first[2], second[2])
    return float(sqrt(dx * dx + dy * dy + dz * dz))


def _reduced_qphi_components(coord: QPhiCoord, divisor: float) -> FractionalCoord:
    values = qphi_coord_to_float(coord)
    return tuple((((value / divisor) + 0.5) % 1.0) - 0.5 for value in values)  # type: ignore[return-value]


def _select_reference_axis(
    radial_direction: FractionalCoord,
    template: ApproximantTemplate,
    site_index: int,
) -> FractionalCoord:
    template_axes = template.reference_axes
    for offset in range(len(template_axes)):
        candidate = template_axes[(site_index + offset) % len(template_axes)]
        if abs(_dot(radial_direction, candidate)) < 0.92:
            return candidate
    for candidate in _FALLBACK_AXES:
        if abs(_dot(radial_direction, candidate)) < 0.92:
            return candidate
    return (1.0, 0.0, 0.0)


def _local_frame(
    base_fractional_position: FractionalCoord,
    template: ApproximantTemplate,
    site_index: int,
) -> tuple[FractionalCoord, FractionalCoord, FractionalCoord]:
    radial_direction = _normalize(
        _difference(base_fractional_position, template.motif_center)
    )
    if radial_direction == (0.0, 0.0, 0.0):
        radial_direction = template.reference_axes[site_index % len(template.reference_axes)]

    reference_axis = _select_reference_axis(radial_direction, template, site_index)
    tangential_a = _normalize(_cross(radial_direction, reference_axis))
    if tangential_a == (0.0, 0.0, 0.0):
        for axis in _FALLBACK_AXES:
            tangential_a = _normalize(_cross(radial_direction, axis))
            if tangential_a != (0.0, 0.0, 0.0):
                break

    tangential_b = _normalize(_cross(radial_direction, tangential_a))
    if tangential_b == (0.0, 0.0, 0.0):
        tangential_b = template.reference_axes[(site_index + 1) % len(template.reference_axes)]
    return radial_direction, tangential_a, tangential_b


def _displaced_position(
    base_fractional_position: FractionalCoord,
    qphi_coord: QPhiCoord,
    template: ApproximantTemplate,
    site_index: int,
) -> tuple[FractionalCoord, FractionalCoord, FractionalCoord]:
    reduced = _reduced_qphi_components(qphi_coord, template.translation_divisor)
    radial_direction, tangential_a, tangential_b = _local_frame(
        base_fractional_position,
        template,
        site_index,
    )
    displacement = (
        template.radial_scale * reduced[0] * radial_direction[0]
        + template.tangential_scale * reduced[1] * tangential_a[0]
        + template.tangential_scale * reduced[2] * tangential_b[0],
        template.radial_scale * reduced[0] * radial_direction[1]
        + template.tangential_scale * reduced[1] * tangential_a[1]
        + template.tangential_scale * reduced[2] * tangential_b[1],
        template.radial_scale * reduced[0] * radial_direction[2]
        + template.tangential_scale * reduced[1] * tangential_a[2]
        + template.tangential_scale * reduced[2] * tangential_b[2],
    )
    position = _wrap(
        (
            base_fractional_position[0] + displacement[0],
            base_fractional_position[1] + displacement[1],
            base_fractional_position[2] + displacement[2],
        )
    )
    return position, tangential_a, tangential_b


def _resolve_collision(
    position: FractionalCoord,
    tangent_a: FractionalCoord,
    tangent_b: FractionalCoord,
    existing_positions: list[FractionalCoord],
    minimum_site_separation: float,
) -> FractionalCoord:
    step = minimum_site_separation * 0.48
    for offset_a, offset_b in _COLLISION_OFFSETS:
        candidate = _wrap(
            (
                position[0] + step * offset_a * tangent_a[0] + step * offset_b * tangent_b[0],
                position[1] + step * offset_a * tangent_a[1] + step * offset_b * tangent_b[1],
                position[2] + step * offset_a * tangent_a[2] + step * offset_b * tangent_b[2],
            )
        )
        if all(
            _fractional_distance(candidate, existing) >= minimum_site_separation
            for existing in existing_positions
        ):
            return candidate
    return position


def site_positions_from_template(
    template: ApproximantTemplate,
    qphi_coords: list[QPhiCoord],
    cell: dict[str, float],
) -> tuple[list[FractionalCoord], list[CartesianCoord]]:
    if len(qphi_coords) != len(template.sites):
        raise ValueError("qphi site count does not match approximant template")

    fractional_positions: list[FractionalCoord] = []
    for site_index, (template_site, qphi_coord) in enumerate(
        zip(template.sites, qphi_coords, strict=True)
    ):
        position, tangent_a, tangent_b = _displaced_position(
            template_site.base_fractional_position,
            qphi_coord,
            template,
            site_index,
        )
        resolved = _resolve_collision(
            position,
            tangent_a,
            tangent_b,
            fractional_positions,
            template.minimum_site_separation,
        )
        fractional_positions.append(resolved)

    cell_matrix = cell_matrix_from_cell(cell)
    cartesian_positions = cartesian_positions_from_fractional(
        fractional_positions,
        cell_matrix,
    )
    return fractional_positions, cartesian_positions
