from __future__ import annotations

from copy import deepcopy

from materials_discovery.common.schema import CandidateRecord

DEFAULT_MIN_DISTANCE_PROXY = 0.55
DEFAULT_MAX_ENERGY_PROXY = -2.65


def apply_screen_thresholds(
    candidates: list[CandidateRecord],
    min_distance_proxy: float = DEFAULT_MIN_DISTANCE_PROXY,
    max_energy_proxy: float = DEFAULT_MAX_ENERGY_PROXY,
) -> tuple[list[CandidateRecord], int]:
    """Filter candidates by proxy thresholds and mark pass/fail status."""
    passing: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        screen = dict(copied.screen or {})
        min_distance = float(screen["min_distance_proxy"])
        energy = float(screen["energy_proxy_ev_per_atom"])
        passed = min_distance >= min_distance_proxy and energy <= max_energy_proxy
        screen["passed_thresholds"] = passed
        copied.screen = screen
        if passed:
            passing.append(copied)

    rejected_count = len(candidates) - len(passing)
    return passing, rejected_count
