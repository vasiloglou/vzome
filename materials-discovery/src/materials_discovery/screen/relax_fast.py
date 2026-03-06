from __future__ import annotations

import hashlib
from copy import deepcopy
from statistics import mean

from materials_discovery.common.chemistry import describe_candidate, validate_supported_species
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _candidate_seed(candidate: CandidateRecord) -> int:
    digest = hashlib.sha256(candidate.candidate_id.encode()).hexdigest()
    return int(digest[:8], 16)


def _qphi_complexity_mock(candidate: CandidateRecord) -> float:
    coeffs: list[int] = []
    for site in candidate.sites:
        for pair in site.qphi:
            coeffs.extend(pair)
    return mean(abs(v) for v in coeffs)


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _run_fast_relaxation_mock(
    config: SystemConfig,
    candidates: list[CandidateRecord],
) -> list[CandidateRecord]:
    """Legacy deterministic proxy logic for mock mode and CI reproducibility."""
    relaxed: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        seed = _candidate_seed(copied)
        complexity = _qphi_complexity_mock(copied)

        base_energy = -3.2 + (seed % 150) / 300.0
        template_shift = len(config.template_family) * 0.001
        energy_proxy = round(base_energy + 0.02 * complexity + template_shift, 6)

        min_distance_proxy = round(
            max(0.35, 1.15 - 0.05 * complexity + ((seed // 10) % 15) / 200.0),
            6,
        )

        copied.screen = {
            **(copied.screen or {}),
            "stage": "screen_relaxed",
            "model": "MACE-proxy",
            "energy_proxy_ev_per_atom": energy_proxy,
            "min_distance_proxy": min_distance_proxy,
            "complexity_proxy": round(complexity, 6),
        }
        relaxed.append(copied)
    return relaxed


def _run_fast_relaxation_real(
    config: SystemConfig,
    candidates: list[CandidateRecord],
) -> list[CandidateRecord]:
    """No-DFT descriptor-based screening model for real mode."""
    validate_supported_species(config.species, strict_pairs=True)

    relaxed: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        descriptor = describe_candidate(copied, strict_pairs=True)

        vec_penalty = abs(descriptor.vec - 6.0)
        energy_proxy = (
            -2.82
            + 0.50 * descriptor.pair_mixing_enthalpy_ev_per_atom
            + 0.22 * descriptor.radius_mismatch
            + 0.11 * descriptor.electronegativity_spread
            + 0.018 * descriptor.qphi_complexity
            + 0.012 * vec_penalty
        )
        energy_proxy = round(energy_proxy, 6)

        min_distance_proxy = (
            0.76
            - 0.23 * descriptor.radius_mismatch
            - 0.035 * descriptor.qphi_complexity
            + 0.06 * (1.0 - descriptor.electronegativity_spread)
        )
        min_distance_proxy = round(_clamp(min_distance_proxy, 0.35, 1.15), 6)

        copied.screen = {
            **(copied.screen or {}),
            "stage": "screen_relaxed",
            "model": "descriptor_screen_v2",
            "energy_proxy_ev_per_atom": energy_proxy,
            "min_distance_proxy": min_distance_proxy,
            "complexity_proxy": descriptor.qphi_complexity,
            "descriptor_vec": descriptor.vec,
            "descriptor_radius_mismatch": descriptor.radius_mismatch,
            "descriptor_en_spread": descriptor.electronegativity_spread,
            "descriptor_pair_mixing_ev_per_atom": descriptor.pair_mixing_enthalpy_ev_per_atom,
        }
        relaxed.append(copied)

    return relaxed


def run_fast_relaxation(
    config: SystemConfig,
    candidates: list[CandidateRecord],
) -> list[CandidateRecord]:
    """Attach proxy-relaxation metrics to candidates."""
    if config.backend.mode == "real":
        return _run_fast_relaxation_real(config, candidates)
    return _run_fast_relaxation_mock(config, candidates)
