from __future__ import annotations

import hashlib
from copy import deepcopy
from statistics import mean

from materials_discovery.active_learning.train_surrogate import SurrogateModelSnapshot
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _qphi_complexity(candidate: CandidateRecord) -> float:
    coeffs: list[int] = []
    for site in candidate.sites:
        for pair in site.qphi:
            coeffs.extend(pair)
    return mean(abs(v) for v in coeffs)


def _composition_distance(candidate: CandidateRecord, centroid: dict[str, float]) -> float:
    distance = sum(
        abs(candidate.composition.get(species, 0.0) - centroid[species]) for species in centroid
    )
    return min(1.0, distance / 2.0)


def _exploration_term(candidate_id: str) -> float:
    digest = hashlib.sha256(f"{candidate_id}:active".encode()).hexdigest()
    seed = int(digest[:8], 16)
    return (seed % 101) / 100.0


def _acquisition_score(
    candidate: CandidateRecord,
    surrogate: SurrogateModelSnapshot,
) -> tuple[float, float, float]:
    similarity = 1.0 - _composition_distance(candidate, surrogate.positive_centroid)
    complexity = min(1.0, _qphi_complexity(candidate) / 3.0)

    predicted_success = 0.65 * similarity + 0.35 * complexity
    boundary_uncertainty = 1.0 - min(1.0, 2.0 * abs(predicted_success - 0.5))
    exploration = _exploration_term(candidate.candidate_id)

    acquisition = 0.6 * boundary_uncertainty + 0.3 * (1.0 - similarity) + 0.1 * exploration
    return predicted_success, boundary_uncertainty, acquisition


def select_next_candidate_batch(
    config: SystemConfig,
    candidate_pool: list[CandidateRecord],
    validated_ids: set[str],
    surrogate: SurrogateModelSnapshot,
    batch_size: int,
) -> list[CandidateRecord]:
    """Select the next deterministic candidate batch using surrogate-guided acquisition."""
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    unseen = [
        candidate for candidate in candidate_pool if candidate.candidate_id not in validated_ids
    ]
    if not unseen:
        raise ValueError("no unvalidated candidates available for selection")

    scored: list[tuple[float, CandidateRecord]] = []
    for candidate in unseen:
        predicted_success, uncertainty_proxy, acquisition = _acquisition_score(candidate, surrogate)

        copied = deepcopy(candidate)
        provenance = dict(copied.provenance)
        provenance["active_learning"] = {
            "system": config.system_name,
            "predicted_success": round(predicted_success, 6),
            "uncertainty_proxy": round(uncertainty_proxy, 6),
            "acquisition_score": round(acquisition, 6),
        }
        copied.provenance = provenance

        scored.append((acquisition, copied))

    ranked = sorted(scored, key=lambda item: (-item[0], item[1].candidate_id))
    selected = [candidate for _, candidate in ranked[:batch_size]]
    return selected
