from __future__ import annotations

import hashlib
from copy import deepcopy

from materials_discovery.backends.registry import resolve_phonon_adapter
from materials_discovery.common.chemistry import qphi_complexity
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _run_mlip_phonon_checks_mock(
    candidates: list[CandidateRecord],
    max_imaginary_modes: int,
) -> list[CandidateRecord]:
    """Legacy deterministic phonon check for mock mode."""
    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        if copied.digital_validation.geometry_prefilter_pass is False:
            scored.append(copied)
            continue
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
    config: SystemConfig,
) -> list[CandidateRecord]:
    """Fixture-backed phonon stability adapter for no-DFT real mode."""
    adapter = None
    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        if copied.digital_validation.geometry_prefilter_pass is False:
            scored.append(copied)
            continue
        if adapter is None:
            adapter = resolve_phonon_adapter(config.backend.mode, config.backend.phonon_adapter)
        imaginary_modes = adapter.evaluate_candidate(config, copied).imaginary_modes

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
        return _run_mlip_phonon_checks_real(
            candidates,
            max_imaginary_modes=max_imaginary_modes,
            config=config,
        )
    return _run_mlip_phonon_checks_mock(candidates, max_imaginary_modes=max_imaginary_modes)
