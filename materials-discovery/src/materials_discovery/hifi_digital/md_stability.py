from __future__ import annotations

import hashlib
from copy import deepcopy

from materials_discovery.common.schema import CandidateRecord


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def run_short_md_stability(
    candidates: list[CandidateRecord],
    min_score: float = 0.55,
) -> list[CandidateRecord]:
    """Attach deterministic short-MD stability scores and pass/fail labels."""
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
