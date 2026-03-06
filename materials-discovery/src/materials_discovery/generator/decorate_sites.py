from __future__ import annotations

import math
import random

from materials_discovery.common.schema import CompositionBound


def assign_species(
    n_sites: int,
    composition_bounds: dict[str, CompositionBound],
    rng: random.Random,
) -> tuple[list[str], dict[str, float]]:
    species = sorted(composition_bounds.keys())
    min_counts = {sp: math.ceil(composition_bounds[sp].min * n_sites) for sp in species}
    max_counts = {sp: math.floor(composition_bounds[sp].max * n_sites) for sp in species}

    total_min = sum(min_counts.values())
    total_max = sum(max_counts.values())

    if total_min > n_sites or total_max < n_sites:
        raise ValueError("No feasible species assignment for the configured composition bounds")

    counts = min_counts.copy()
    remaining = n_sites - total_min

    while remaining > 0:
        candidates = [sp for sp in species if counts[sp] < max_counts[sp]]
        if not candidates:
            raise ValueError("Could not allocate remaining species counts within bounds")
        chosen = rng.choice(candidates)
        counts[chosen] += 1
        remaining -= 1

    decorated: list[str] = []
    for sp in species:
        decorated.extend([sp] * counts[sp])

    rng.shuffle(decorated)

    composition = {sp: counts[sp] / n_sites for sp in species}
    return decorated, composition
