from __future__ import annotations

from copy import deepcopy
from statistics import pstdev

from materials_discovery.common.schema import CandidateRecord


def compute_committee_uncertainty(
    candidates: list[CandidateRecord],
    uncertainty_floor: float = 0.002,
) -> list[CandidateRecord]:
    """Compute deterministic uncertainty from committee energy disagreement."""
    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        committee_energies = copied.digital_validation.committee_energy_ev_per_atom
        if not committee_energies:
            raise ValueError(
                "committee energies missing; run committee relaxation before uncertainty scoring"
            )

        values = [float(v) for _, v in sorted(committee_energies.items())]
        uncertainty = round(max(uncertainty_floor, pstdev(values)), 6)

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "uncertainty_scored"
        validation.committee_std_ev_per_atom = uncertainty
        validation.uncertainty_ev_per_atom = uncertainty
        copied.digital_validation = validation
        scored.append(copied)
    return scored
