from __future__ import annotations

import hashlib
from copy import deepcopy
from statistics import mean

from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _candidate_seed(candidate: CandidateRecord) -> int:
    digest = hashlib.sha256(candidate.candidate_id.encode()).hexdigest()
    return int(digest[:8], 16)


def _qphi_complexity(candidate: CandidateRecord) -> float:
    coeffs: list[int] = []
    for site in candidate.sites:
        for pair in site.qphi:
            coeffs.extend(pair)
    return mean(abs(v) for v in coeffs)


def run_fast_relaxation(
    config: SystemConfig,
    candidates: list[CandidateRecord],
) -> list[CandidateRecord]:
    """Attach deterministic proxy-relaxation metrics to candidates."""
    relaxed: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        seed = _candidate_seed(copied)
        complexity = _qphi_complexity(copied)

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
