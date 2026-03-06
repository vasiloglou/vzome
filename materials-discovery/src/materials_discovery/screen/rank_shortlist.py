from __future__ import annotations

import math
from copy import deepcopy

from materials_discovery.common.schema import CandidateRecord


def rank_screen_shortlist(
    candidates: list[CandidateRecord],
    keep_fraction: float = 0.2,
    max_keep: int = 200,
) -> list[CandidateRecord]:
    """Rank and keep top shortlist candidates from threshold-passing inputs."""
    if not candidates:
        return []

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (
            float((c.screen or {})["energy_proxy_ev_per_atom"]),
            -float((c.screen or {})["min_distance_proxy"]),
            c.candidate_id,
        ),
    )

    computed_keep = max(1, math.ceil(len(sorted_candidates) * keep_fraction))
    keep_count = min(max_keep, computed_keep, len(sorted_candidates))

    shortlisted: list[CandidateRecord] = []
    for idx, candidate in enumerate(sorted_candidates[:keep_count], start=1):
        copied = deepcopy(candidate)
        screen = dict(copied.screen or {})
        screen["shortlist_rank"] = idx
        copied.screen = screen
        shortlisted.append(copied)
    return shortlisted
