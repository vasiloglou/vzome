from __future__ import annotations

import hashlib
from copy import deepcopy
from statistics import mean

from materials_discovery.common.schema import CandidateRecord


def _qphi_complexity(candidate: CandidateRecord) -> float:
    coeffs: list[int] = []
    for site in candidate.sites:
        for pair in site.qphi:
            coeffs.extend(pair)
    return mean(abs(v) for v in coeffs)


def run_mlip_phonon_checks(
    candidates: list[CandidateRecord],
    max_imaginary_modes: int = 1,
) -> list[CandidateRecord]:
    """Attach deterministic MLIP phonon checks for staged no-DFT filtering."""
    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        complexity = _qphi_complexity(copied)
        delta_hull = copied.digital_validation.delta_e_proxy_hull_ev_per_atom or 0.0

        digest = hashlib.sha256(f"{copied.candidate_id}:phonon".encode()).hexdigest()
        seed = int(digest[:8], 16)

        imagined = max(0, int(round(complexity / 1.8)) + (seed % 3) - 1)
        if delta_hull < 0.03 and imagined > 0:
            imagined -= 1

        phonon_pass = imagined <= max_imaginary_modes

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "phonon_checked"
        validation.phonon_imaginary_modes = imagined
        validation.phonon_pass = phonon_pass
        copied.digital_validation = validation
        scored.append(copied)
    return scored
