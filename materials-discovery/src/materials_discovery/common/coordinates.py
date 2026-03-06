from __future__ import annotations

from math import cos, pi, sin, sqrt

from materials_discovery.common.schema import QPhiCoord, QPhiPair

PHI = (1.0 + 5.0**0.5) / 2.0
FractionalCoord = tuple[float, float, float]
CartesianCoord = tuple[float, float, float]

_OFFSET_VECTORS: tuple[FractionalCoord, ...] = (
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


def qphi_coord_to_float(coord: QPhiCoord) -> CartesianCoord:
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


def _fractional_distance(first: FractionalCoord, second: FractionalCoord) -> float:
    dx = _periodic_axis_delta(first[0], second[0])
    dy = _periodic_axis_delta(first[1], second[1])
    dz = _periodic_axis_delta(first[2], second[2])
    return float(sqrt(dx * dx + dy * dy + dz * dz))


def fractional_positions_from_qphi_coords(qphi_coords: list[QPhiCoord]) -> list[FractionalCoord]:
    raw_positions = [qphi_coord_to_float(coord) for coord in qphi_coords]
    x_axis = _normalized_axis([position[0] for position in raw_positions])
    y_axis = _normalized_axis([position[1] for position in raw_positions])
    z_axis = _normalized_axis([position[2] for position in raw_positions])

    positions: list[FractionalCoord] = []
    for index, (base_x, base_y, base_z) in enumerate(zip(x_axis, y_axis, z_axis, strict=True)):
        seed = index + 1
        fractional = (
            (base_x + 0.023 * ((seed * PHI) % 1.0)) % 1.0,
            (base_y + 0.019 * (((seed + 1) * PHI) % 1.0)) % 1.0,
            (base_z + 0.017 * (((seed + 2) * PHI) % 1.0)) % 1.0,
        )
        for offset_x, offset_y, offset_z in _OFFSET_VECTORS:
            shifted: FractionalCoord = (
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


def cell_matrix_from_cell(cell: dict[str, float]) -> list[list[float]]:
    a = float(cell["a"])
    b = float(cell["b"])
    c = float(cell["c"])
    alpha = float(cell["alpha"]) * pi / 180.0
    beta = float(cell["beta"]) * pi / 180.0
    gamma = float(cell["gamma"]) * pi / 180.0

    if abs(sin(gamma)) < 1e-9:
        raise ValueError("invalid gamma angle for cell construction")

    vector_a = [a, 0.0, 0.0]
    vector_b = [b * cos(gamma), b * sin(gamma), 0.0]
    cx = c * cos(beta)
    cy = c * (cos(alpha) - cos(beta) * cos(gamma)) / sin(gamma)
    cz_sq = max(0.0, c * c - cx * cx - cy * cy)
    vector_c = [cx, cy, sqrt(cz_sq)]
    return [vector_a, vector_b, vector_c]


def fractional_to_cartesian(
    fractional: FractionalCoord,
    cell_matrix: list[list[float]],
) -> CartesianCoord:
    return (
        round(
            fractional[0] * cell_matrix[0][0]
            + fractional[1] * cell_matrix[1][0]
            + fractional[2] * cell_matrix[2][0],
            6,
        ),
        round(
            fractional[0] * cell_matrix[0][1]
            + fractional[1] * cell_matrix[1][1]
            + fractional[2] * cell_matrix[2][1],
            6,
        ),
        round(
            fractional[0] * cell_matrix[0][2]
            + fractional[1] * cell_matrix[1][2]
            + fractional[2] * cell_matrix[2][2],
            6,
        ),
    )


def cartesian_to_fractional(
    cartesian: CartesianCoord,
    cell_matrix: list[list[float]],
) -> FractionalCoord:
    matrix = [
        [float(cell_matrix[row][col]) for col in range(3)]
        for row in range(3)
    ]
    determinant = (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )
    if abs(determinant) < 1e-12:
        raise ValueError("cell matrix is singular and cannot be inverted")

    inverse = _invert_3x3(matrix, determinant)
    fractional = (
        inverse[0][0] * cartesian[0] + inverse[0][1] * cartesian[1] + inverse[0][2] * cartesian[2],
        inverse[1][0] * cartesian[0] + inverse[1][1] * cartesian[1] + inverse[1][2] * cartesian[2],
        inverse[2][0] * cartesian[0] + inverse[2][1] * cartesian[1] + inverse[2][2] * cartesian[2],
    )
    return tuple(round(value % 1.0, 6) for value in fractional)  # type: ignore[return-value]


def _invert_3x3(matrix: list[list[float]], determinant: float) -> list[list[float]]:
    return [
        [
            (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) / determinant,
            (matrix[0][2] * matrix[2][1] - matrix[0][1] * matrix[2][2]) / determinant,
            (matrix[0][1] * matrix[1][2] - matrix[0][2] * matrix[1][1]) / determinant,
        ],
        [
            (matrix[1][2] * matrix[2][0] - matrix[1][0] * matrix[2][2]) / determinant,
            (matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]) / determinant,
            (matrix[0][2] * matrix[1][0] - matrix[0][0] * matrix[1][2]) / determinant,
        ],
        [
            (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]) / determinant,
            (matrix[0][1] * matrix[2][0] - matrix[0][0] * matrix[2][1]) / determinant,
            (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) / determinant,
        ],
    ]


def cartesian_positions_from_fractional(
    fractional_positions: list[FractionalCoord],
    cell_matrix: list[list[float]],
) -> list[CartesianCoord]:
    return [
        fractional_to_cartesian(fractional, cell_matrix)
        for fractional in fractional_positions
    ]
