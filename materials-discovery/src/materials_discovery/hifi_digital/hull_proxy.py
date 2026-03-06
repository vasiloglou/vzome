from __future__ import annotations

from copy import deepcopy
from statistics import mean

from materials_discovery.common.schema import CandidateRecord


def _committee_mean_energy(candidate: CandidateRecord) -> float:
    committee_energies = candidate.digital_validation.committee_energy_ev_per_atom
    if not committee_energies:
        raise ValueError("committee energies missing for proxy-hull calculation")
    return mean(float(v) for v in committee_energies.values())


def _composition_imbalance(composition: dict[str, float]) -> float:
    target = 1.0 / len(composition)
    return sum(abs(frac - target) for frac in composition.values()) / 2.0


def compute_proxy_hull(candidates: list[CandidateRecord]) -> list[CandidateRecord]:
    """Compute deterministic proxy hull deltas from committee energies and composition balance."""
    if not candidates:
        return []

    mean_energies = {c.candidate_id: _committee_mean_energy(c) for c in candidates}
    best_energy = min(mean_energies.values())

    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        energy_term = mean_energies[copied.candidate_id] - best_energy
        balance_term = 0.04 * _composition_imbalance(copied.composition)
        delta_hull = round(max(0.0, energy_term + balance_term), 6)

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "hull_scored"
        validation.delta_e_proxy_hull_ev_per_atom = delta_hull
        copied.digital_validation = validation
        scored.append(copied)
    return scored
