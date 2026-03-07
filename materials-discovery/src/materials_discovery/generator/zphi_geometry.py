from __future__ import annotations

from materials_discovery.common.schema import QPhiCoord, QPhiPair

PHI = (1.0 + 5.0**0.5) / 2.0


_PERMUTATIONS: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2),
    (1, 2, 0),
    (2, 0, 1),
    (0, 2, 1),
    (1, 0, 2),
    (2, 1, 0),
)



def _clamp(value: int, low: int, high: int) -> int:
    return min(max(value, low), high)



def phi_scale_pair(pair: QPhiPair, steps: int) -> QPhiPair:
    a, b = pair
    if steps >= 0:
        for _ in range(steps):
            a, b = b, a + b
    else:
        for _ in range(-steps):
            a, b = b - a, a
    return (a, b)



def phi_scale_coord(coord: QPhiCoord, steps: int) -> QPhiCoord:
    return tuple(phi_scale_pair(pair, steps) for pair in coord)  # type: ignore[return-value]



def _add_pairs(first: QPhiPair, second: QPhiPair) -> QPhiPair:
    return (first[0] + second[0], first[1] + second[1])



def _translate_coord(coord: QPhiCoord, shift: QPhiCoord) -> QPhiCoord:
    return tuple(_add_pairs(pair, delta) for pair, delta in zip(coord, shift, strict=True))  # type: ignore[return-value]



def _permute_coord(coord: QPhiCoord, variant: int) -> QPhiCoord:
    order = _PERMUTATIONS[variant % len(_PERMUTATIONS)]
    permuted = tuple(coord[index] for index in order)
    if variant % 2 == 0:
        return permuted  # type: ignore[return-value]
    flipped = tuple((pair[0], -pair[1]) for pair in permuted)
    return flipped  # type: ignore[return-value]



def _bound_coord(coord: QPhiCoord, min_coeff: int, max_coeff: int) -> QPhiCoord:
    return tuple(
        (
            _clamp(pair[0], min_coeff, max_coeff),
            _clamp(pair[1], min_coeff, max_coeff),
        )
        for pair in coord
    )  # type: ignore[return-value]



def cell_scale_multiplier(
    seed: int,
    candidate_index: int,
    *,
    template_source_kind: str = "generic",
) -> float:
    if template_source_kind != "generic":
        variant = ((seed + 3 * candidate_index) % 5) - 2
        return round(1.0 + 0.015 * variant, 6)
    variant = (seed + 5 * candidate_index) % 3 - 1
    return round(PHI**variant, 6)



def construct_site_qphi(
    base_qphi: QPhiCoord,
    *,
    template_family: str,
    candidate_index: int,
    site_index: int,
    seed: int,
    min_coeff: int,
    max_coeff: int,
) -> QPhiCoord:
    family_shift = {
        "icosahedral_approximant_1_1": 2,
        "decagonal_proxy_2_1": 1,
        "cubic_proxy_1_0": 0,
    }.get(template_family, 0)
    inflation_steps = ((seed + candidate_index + site_index + family_shift) % 3) - 1
    rotated = _permute_coord(base_qphi, seed + candidate_index + site_index + family_shift)
    scaled = phi_scale_coord(rotated, inflation_steps)

    translation = (
        phi_scale_pair(((candidate_index + site_index + family_shift) % 2, 0), inflation_steps),
        phi_scale_pair((0, ((candidate_index + family_shift) % 2)), max(0, inflation_steps)),
        phi_scale_pair(
            ((site_index + family_shift) % 2, -((candidate_index + site_index) % 2)),
            0,
        ),
    )
    translated = _translate_coord(scaled, translation)
    return _bound_coord(translated, min_coeff=min_coeff, max_coeff=max_coeff)
