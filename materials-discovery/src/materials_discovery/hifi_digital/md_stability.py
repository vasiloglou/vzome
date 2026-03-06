from __future__ import annotations

import hashlib
from copy import deepcopy

from materials_discovery.common.chemistry import describe_candidate
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _run_short_md_stability_mock(
    candidates: list[CandidateRecord],
    min_score: float,
) -> list[CandidateRecord]:
    """Legacy deterministic short-MD stability proxy for mock mode."""
    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        uncertainty = copied.digital_validation.uncertainty_ev_per_atom or 0.05
        delta_hull = copied.digital_validation.delta_e_proxy_hull_ev_per_atom or 0.1

        digest = hashlib.sha256(f"{copied.candidate_id}:md".encode()).hexdigest()
        seed = int(digest[:8], 16)
        jitter = ((seed % 31) - 15) / 100.0

        stability_score = _clamp(0.86 - 2.2 * uncertainty - 1.4 * delta_hull + jitter, 0.0, 1.0)
        stability_score = round(stability_score, 6)

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "md_checked"
        validation.md_stability_score = stability_score
        validation.md_pass = stability_score >= min_score
        copied.digital_validation = validation
        scored.append(copied)
    return scored


def _run_short_md_stability_real(
    candidates: list[CandidateRecord],
    min_score: float,
) -> list[CandidateRecord]:
    """Descriptor-driven short-MD stability proxy for no-DFT real mode."""
    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        descriptor = describe_candidate(copied, strict_pairs=True)

        uncertainty = copied.digital_validation.uncertainty_ev_per_atom or 0.05
        delta_hull = copied.digital_validation.delta_e_proxy_hull_ev_per_atom or 0.1
        imaginary_modes = copied.digital_validation.phonon_imaginary_modes or 0
        min_distance = float((copied.screen or {}).get("min_distance_proxy", 0.6))

        packing_bonus = max(0.0, min(0.16, (min_distance - 0.55) * 0.45))
        vec_penalty = abs(descriptor.vec - 6.0) / 6.0

        stability_score = (
            0.95
            - 2.4 * uncertainty
            - 1.8 * delta_hull
            - 0.05 * max(0, imaginary_modes - 1)
            - 0.30 * descriptor.radius_mismatch
            - 0.22 * descriptor.electronegativity_spread
            - 0.08 * vec_penalty
            + packing_bonus
        )
        stability_score = round(_clamp(stability_score, 0.0, 1.0), 6)

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "md_checked"
        validation.md_stability_score = stability_score
        validation.md_pass = stability_score >= min_score
        copied.digital_validation = validation
        scored.append(copied)

    return scored


def run_short_md_stability(
    candidates: list[CandidateRecord],
    min_score: float = 0.55,
    config: SystemConfig | None = None,
) -> list[CandidateRecord]:
    """Attach short-MD stability scores and pass/fail labels."""
    if config is not None and config.backend.mode == "real":
        return _run_short_md_stability_real(candidates, min_score=min_score)
    return _run_short_md_stability_mock(candidates, min_score=min_score)
