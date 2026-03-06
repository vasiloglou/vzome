from __future__ import annotations

import hashlib
from copy import deepcopy

from materials_discovery.common.chemistry import describe_candidate, qphi_complexity
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _run_mlip_phonon_checks_mock(
    candidates: list[CandidateRecord],
    max_imaginary_modes: int,
) -> list[CandidateRecord]:
    """Legacy deterministic phonon check for mock mode."""
    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        complexity = qphi_complexity(copied)
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


def _run_mlip_phonon_checks_real(
    candidates: list[CandidateRecord],
    max_imaginary_modes: int,
) -> list[CandidateRecord]:
    """Descriptor-driven phonon stability proxy for no-DFT real mode."""
    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        descriptor = describe_candidate(copied, strict_pairs=True)

        delta_hull = copied.digital_validation.delta_e_proxy_hull_ev_per_atom or 0.0
        uncertainty = copied.digital_validation.uncertainty_ev_per_atom or 0.05

        instability_index = (
            2.7 * descriptor.radius_mismatch
            + 1.8 * descriptor.electronegativity_spread
            + 0.30 * min(1.0, descriptor.qphi_complexity / 3.0)
            + 4.0 * delta_hull
            + 3.0 * uncertainty
        )
        imaginary_modes = max(0, int(round(instability_index * 2.0)))

        if descriptor.pair_mixing_enthalpy_ev_per_atom <= -0.12 and imaginary_modes > 0:
            imaginary_modes -= 1

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "phonon_checked"
        validation.phonon_imaginary_modes = imaginary_modes
        validation.phonon_pass = imaginary_modes <= max_imaginary_modes
        copied.digital_validation = validation
        scored.append(copied)
    return scored


def run_mlip_phonon_checks(
    candidates: list[CandidateRecord],
    max_imaginary_modes: int = 1,
    config: SystemConfig | None = None,
) -> list[CandidateRecord]:
    """Attach MLIP phonon checks for staged no-DFT filtering."""
    if config is not None and config.backend.mode == "real":
        return _run_mlip_phonon_checks_real(candidates, max_imaginary_modes=max_imaginary_modes)
    return _run_mlip_phonon_checks_mock(candidates, max_imaginary_modes=max_imaginary_modes)
