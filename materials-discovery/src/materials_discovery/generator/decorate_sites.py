from __future__ import annotations

import math
import random

from materials_discovery.common.schema import CompositionBound


def assign_species(
    n_sites: int,
    composition_bounds: dict[str, CompositionBound],
    rng: random.Random,
    site_preferences: list[tuple[str, ...] | None] | None = None,
) -> tuple[list[str], dict[str, float]]:
    species = sorted(composition_bounds.keys())
    min_counts = {sp: math.ceil(composition_bounds[sp].min * n_sites) for sp in species}
    max_counts = {sp: math.floor(composition_bounds[sp].max * n_sites) for sp in species}

    if site_preferences is not None and len(site_preferences) != n_sites:
        raise ValueError("site preference count must match the number of sites")

    hard_preference_counts = {sp: 0 for sp in species}
    if site_preferences is not None:
        for preference in site_preferences:
            if preference is None or len(preference) != 1:
                continue
            preferred_species = preference[0]
            if preferred_species in hard_preference_counts:
                hard_preference_counts[preferred_species] += 1

    for sp, count in hard_preference_counts.items():
        if count > max_counts[sp]:
            raise ValueError(
                f"Hard site preferences for {sp} exceed the configured composition bounds"
            )
        min_counts[sp] = max(min_counts[sp], count)

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

    decorated: list[str | None] = [None] * n_sites
    remaining_counts = counts.copy()

    if site_preferences is not None:
        for index, preference in enumerate(site_preferences):
            if preference is None or len(preference) != 1:
                continue
            preferred_species = preference[0]
            if remaining_counts[preferred_species] <= 0:
                raise ValueError(
                    f"Could not satisfy hard site preference for species {preferred_species}"
                )
            decorated[index] = preferred_species
            remaining_counts[preferred_species] -= 1

        flexible_indices = [
            index
            for index, preference in enumerate(site_preferences)
            if decorated[index] is None and preference is not None
        ]
        rng.shuffle(flexible_indices)
        for index in flexible_indices:
            preference = site_preferences[index]
            if preference is None:
                continue
            chosen_species = next(
                (sp for sp in preference if remaining_counts.get(sp, 0) > 0),
                None,
            )
            if chosen_species is None:
                continue
            decorated[index] = chosen_species
            remaining_counts[chosen_species] -= 1

    unassigned_indices = [index for index, value in enumerate(decorated) if value is None]
    tail: list[str] = []
    for sp in species:
        tail.extend([sp] * remaining_counts[sp])
    rng.shuffle(tail)
    for index, chosen in zip(unassigned_indices, tail, strict=True):
        decorated[index] = chosen

    if any(value is None for value in decorated):
        raise ValueError("Could not assign species to all sites")

    composition = {sp: counts[sp] / n_sites for sp in species}
    return [value for value in decorated if value is not None], composition
