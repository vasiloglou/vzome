from __future__ import annotations

from copy import deepcopy

from materials_discovery.active_learning.train_surrogate import (
    SurrogateModelSnapshot,
    candidate_feature_map,
    composition_distance_to_centroid,
    feature_distance,
    predict_success_from_features,
)
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _energy_desirability(feature_row: dict[str, float]) -> float:
    return round(
        0.65 * feature_row["energy_preference"] + 0.35 * feature_row["packing_preference"],
        6,
    )


def _boundary_uncertainty(predicted_success: float, decision_threshold: float) -> float:
    scale = max(decision_threshold, 1.0 - decision_threshold, 0.15)
    return round(1.0 - min(1.0, abs(predicted_success - decision_threshold) / scale), 6)


def _ood_score(
    feature_row: dict[str, float],
    surrogate: SurrogateModelSnapshot,
) -> float:
    nearest_distance = min(
        feature_distance(
            feature_row,
            surrogate.positive_feature_centroid,
            surrogate.feature_names,
        ),
        feature_distance(
            feature_row,
            surrogate.negative_feature_centroid,
            surrogate.feature_names,
        ),
    )
    score = (nearest_distance - surrogate.training_radius) / max(
        0.10,
        1.0 - surrogate.training_radius,
    )
    return round(_clamp(score, 0.0, 1.0), 6)


def _novelty_score(
    candidate: CandidateRecord,
    feature_row: dict[str, float],
    surrogate: SurrogateModelSnapshot,
    ood_score: float,
) -> float:
    composition_novelty = composition_distance_to_centroid(candidate, surrogate.positive_centroid)
    structural_novelty = abs(
        feature_row["qphi_complexity_norm"]
        - surrogate.positive_feature_centroid["qphi_complexity_norm"]
    )
    score = 0.55 * composition_novelty + 0.45 * structural_novelty - 0.25 * ood_score
    return round(_clamp(score, 0.0, 1.0), 6)


def _acquisition_metrics(
    config: SystemConfig,
    candidate: CandidateRecord,
    surrogate: SurrogateModelSnapshot,
) -> tuple[float, float, float, float, float, float]:
    feature_row = candidate_feature_map(config, candidate)
    predicted_success = predict_success_from_features(
        feature_row,
        positive_feature_centroid=surrogate.positive_feature_centroid,
        negative_feature_centroid=surrogate.negative_feature_centroid,
        names=surrogate.feature_names,
        pass_rate=surrogate.pass_rate,
    )
    uncertainty_proxy = _boundary_uncertainty(predicted_success, surrogate.decision_threshold)
    ood_score = _ood_score(feature_row, surrogate)
    novelty_score = _novelty_score(candidate, feature_row, surrogate, ood_score)
    energy_desirability = _energy_desirability(feature_row)

    acquisition = (
        0.32 * predicted_success
        + 0.30 * uncertainty_proxy
        + 0.20 * energy_desirability
        + 0.12 * novelty_score
        - 0.22 * ood_score
    )
    return (
        round(predicted_success, 6),
        round(uncertainty_proxy, 6),
        round(novelty_score, 6),
        round(ood_score, 6),
        round(energy_desirability, 6),
        round(acquisition, 6),
    )


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

    scored: list[tuple[tuple[float, float, float, float], CandidateRecord]] = []
    for candidate in unseen:
        (
            predicted_success,
            uncertainty_proxy,
            novelty_score,
            ood_score,
            energy_desirability,
            acquisition,
        ) = _acquisition_metrics(config, candidate, surrogate)

        copied = deepcopy(candidate)
        provenance = dict(copied.provenance)
        provenance["active_learning"] = {
            "system": config.system_name,
            "predicted_success": predicted_success,
            "uncertainty_proxy": uncertainty_proxy,
            "novelty_score": novelty_score,
            "ood_score": ood_score,
            "energy_desirability": energy_desirability,
            "acquisition_score": acquisition,
        }
        copied.provenance = provenance

        scored.append(
            (
                (
                    acquisition,
                    predicted_success,
                    energy_desirability,
                    -ood_score,
                ),
                copied,
            )
        )

    ranked = sorted(
        scored,
        key=lambda item: (
            -item[0][0],
            -item[0][1],
            -item[0][2],
            item[1].candidate_id,
        ),
    )
    selected = [candidate for _, candidate in ranked[:batch_size]]
    return selected
