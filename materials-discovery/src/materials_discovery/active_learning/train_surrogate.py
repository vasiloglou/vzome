from __future__ import annotations

from dataclasses import dataclass
from math import exp
from statistics import mean

from materials_discovery.common.chemistry import composition_l1_distance, describe_candidate
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-value))


def _mean(values: list[float], fallback: float) -> float:
    return mean(values) if values else fallback


def _composition_centroid(
    config: SystemConfig,
    candidates: list[CandidateRecord],
) -> dict[str, float]:
    if not candidates:
        return {species: 0.0 for species in sorted(config.species)}
    centroid = {
        species: _mean([candidate.composition.get(species, 0.0) for candidate in candidates], 0.0)
        for species in sorted(config.species)
    }
    return {species: round(value, 6) for species, value in centroid.items()}


def feature_names(config: SystemConfig) -> list[str]:
    return [f"frac_{species}" for species in sorted(config.species)] + [
        "qphi_complexity_norm",
        "radius_mismatch_norm",
        "en_spread_norm",
        "pair_mixing_preference",
        "energy_preference",
        "packing_preference",
        "shortlist_signal",
    ]


def candidate_feature_map(
    config: SystemConfig,
    candidate: CandidateRecord,
) -> dict[str, float]:
    descriptor = describe_candidate(candidate, strict_pairs=config.backend.mode == "real")
    screen = candidate.screen or {}

    energy_proxy = float(screen.get("energy_proxy_ev_per_atom", -2.4))
    min_distance = float(screen.get("min_distance_proxy", 0.55))
    shortlist_rank = screen.get("shortlist_rank")
    shortlist_signal = 0.0
    if isinstance(shortlist_rank, int) and shortlist_rank > 0:
        shortlist_signal = 1.0 / min(50.0, float(shortlist_rank))
    elif isinstance(shortlist_rank, float) and shortlist_rank > 0.0:
        shortlist_signal = 1.0 / min(50.0, float(shortlist_rank))

    features: dict[str, float] = {}
    for species in sorted(config.species):
        features[f"frac_{species}"] = round(float(candidate.composition.get(species, 0.0)), 6)

    features["qphi_complexity_norm"] = round(_clamp(descriptor.qphi_complexity / 3.5, 0.0, 1.0), 6)
    features["radius_mismatch_norm"] = round(
        _clamp(descriptor.radius_mismatch / 0.15, 0.0, 1.0),
        6,
    )
    features["en_spread_norm"] = round(
        _clamp(descriptor.electronegativity_spread / 0.20, 0.0, 1.0),
        6,
    )
    features["pair_mixing_preference"] = round(
        _clamp((-descriptor.pair_mixing_enthalpy_ev_per_atom) / 0.30, 0.0, 1.0),
        6,
    )
    features["energy_preference"] = round(
        _clamp(((-energy_proxy) - 2.55) / 0.75, 0.0, 1.0),
        6,
    )
    features["packing_preference"] = round(
        _clamp((min_distance - 0.50) / 0.60, 0.0, 1.0),
        6,
    )
    features["shortlist_signal"] = round(_clamp(shortlist_signal, 0.0, 1.0), 6)
    return features


def feature_centroid(
    rows: list[dict[str, float]],
    names: list[str],
) -> dict[str, float]:
    if not rows:
        return {name: 0.0 for name in names}
    return {
        name: round(_mean([row[name] for row in rows], 0.0), 6)
        for name in names
    }


def feature_distance(
    feature_row: dict[str, float],
    centroid: dict[str, float],
    names: list[str],
) -> float:
    return sum(abs(feature_row[name] - centroid[name]) for name in names) / len(names)


def predict_success_from_features(
    feature_row: dict[str, float],
    *,
    positive_feature_centroid: dict[str, float],
    negative_feature_centroid: dict[str, float],
    names: list[str],
    pass_rate: float,
) -> float:
    pos_dist = feature_distance(feature_row, positive_feature_centroid, names)
    neg_dist = feature_distance(feature_row, negative_feature_centroid, names)
    separation = neg_dist - pos_dist

    logit = (
        2.8 * separation
        + 0.90 * feature_row["energy_preference"]
        + 0.55 * feature_row["packing_preference"]
        + 0.35 * feature_row["pair_mixing_preference"]
        + 0.20 * feature_row["shortlist_signal"]
        + 1.40 * (pass_rate - 0.25)
    )
    return round(_clamp(_sigmoid(logit), 0.0, 1.0), 6)


@dataclass(frozen=True)
class SurrogateModelSnapshot:
    system: str
    species: list[str]
    training_rows: int
    positive_count: int
    negative_count: int
    pass_rate: float
    positive_centroid: dict[str, float]
    negative_centroid: dict[str, float]
    feature_names: list[str]
    positive_feature_centroid: dict[str, float]
    negative_feature_centroid: dict[str, float]
    uncertainty_mean: float
    delta_hull_mean: float
    decision_threshold: float
    separation_margin: float
    training_radius: float
    top_k_precision: float
    mean_predicted_success: float

    def model_dump(self) -> dict[str, object]:
        return {
            "system": self.system,
            "species": self.species,
            "training_rows": self.training_rows,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "pass_rate": self.pass_rate,
            "positive_centroid": self.positive_centroid,
            "negative_centroid": self.negative_centroid,
            "feature_names": self.feature_names,
            "positive_feature_centroid": self.positive_feature_centroid,
            "negative_feature_centroid": self.negative_feature_centroid,
            "uncertainty_mean": self.uncertainty_mean,
            "delta_hull_mean": self.delta_hull_mean,
            "decision_threshold": self.decision_threshold,
            "separation_margin": self.separation_margin,
            "training_radius": self.training_radius,
            "top_k_precision": self.top_k_precision,
            "mean_predicted_success": self.mean_predicted_success,
        }


def train_surrogate_model(
    config: SystemConfig,
    validated_candidates: list[CandidateRecord],
) -> SurrogateModelSnapshot:
    """Train a deterministic surrogate over pre-hifi descriptors and screening features."""
    if not validated_candidates:
        raise ValueError("no validated candidates available for active learning")

    positives = [
        candidate
        for candidate in validated_candidates
        if candidate.digital_validation.passed_checks is True
    ]
    negatives = [
        candidate
        for candidate in validated_candidates
        if candidate.digital_validation.passed_checks is not True
    ]

    uncertainty_values = [
        float(candidate.digital_validation.uncertainty_ev_per_atom)
        for candidate in validated_candidates
        if candidate.digital_validation.uncertainty_ev_per_atom is not None
    ]
    delta_hull_values = [
        float(candidate.digital_validation.delta_e_proxy_hull_ev_per_atom)
        for candidate in validated_candidates
        if candidate.digital_validation.delta_e_proxy_hull_ev_per_atom is not None
    ]

    names = feature_names(config)
    feature_rows = {
        candidate.candidate_id: candidate_feature_map(config, candidate)
        for candidate in validated_candidates
    }
    positive_rows = [feature_rows[candidate.candidate_id] for candidate in positives]
    negative_rows = [feature_rows[candidate.candidate_id] for candidate in negatives]

    if not positive_rows:
        positive_rows = list(feature_rows.values())
    if not negative_rows:
        negative_rows = list(feature_rows.values())

    positive_feature_centroid = feature_centroid(positive_rows, names)
    negative_feature_centroid = feature_centroid(negative_rows, names)

    predictions = [
        predict_success_from_features(
            feature_rows[candidate.candidate_id],
            positive_feature_centroid=positive_feature_centroid,
            negative_feature_centroid=negative_feature_centroid,
            names=names,
            pass_rate=len(positives) / len(validated_candidates),
        )
        for candidate in validated_candidates
    ]
    positive_predictions = [
        predictions[index]
        for index, candidate in enumerate(validated_candidates)
        if candidate.digital_validation.passed_checks is True
    ]
    negative_predictions = [
        predictions[index]
        for index, candidate in enumerate(validated_candidates)
        if candidate.digital_validation.passed_checks is not True
    ]
    positive_prediction_mean = _mean(positive_predictions, fallback=0.65)
    negative_prediction_mean = _mean(negative_predictions, fallback=0.35)
    decision_threshold = round(
        _clamp((positive_prediction_mean + negative_prediction_mean) / 2.0, 0.35, 0.75),
        6,
    )

    training_distances = [
        min(
            feature_distance(
                feature_rows[candidate.candidate_id],
                positive_feature_centroid,
                names,
            ),
            feature_distance(
                feature_rows[candidate.candidate_id],
                negative_feature_centroid,
                names,
            ),
        )
        for candidate in validated_candidates
    ]
    training_radius = round(_mean(training_distances, fallback=0.15), 6)

    predicted_with_ids = list(zip(predictions, validated_candidates, strict=True))
    predicted_with_ids.sort(key=lambda item: (-item[0], item[1].candidate_id))
    top_k = min(max(1, len(positives)), 5, len(predicted_with_ids))
    top_k_precision = round(
        sum(item[1].digital_validation.passed_checks is True for item in predicted_with_ids[:top_k])
        / top_k,
        6,
    )

    return SurrogateModelSnapshot(
        system=config.system_name,
        species=sorted(config.species),
        training_rows=len(validated_candidates),
        positive_count=len(positives),
        negative_count=len(negatives),
        pass_rate=round(len(positives) / len(validated_candidates), 6),
        positive_centroid=_composition_centroid(config, positives or validated_candidates),
        negative_centroid=_composition_centroid(config, negatives or validated_candidates),
        feature_names=names,
        positive_feature_centroid=positive_feature_centroid,
        negative_feature_centroid=negative_feature_centroid,
        uncertainty_mean=round(_mean(uncertainty_values, fallback=0.05), 6),
        delta_hull_mean=round(_mean(delta_hull_values, fallback=0.1), 6),
        decision_threshold=decision_threshold,
        separation_margin=round(positive_prediction_mean - negative_prediction_mean, 6),
        training_radius=training_radius,
        top_k_precision=top_k_precision,
        mean_predicted_success=round(_mean(predictions, fallback=0.5), 6),
    )


def composition_distance_to_centroid(
    candidate: CandidateRecord,
    centroid: dict[str, float],
) -> float:
    return min(1.0, composition_l1_distance(candidate.composition, centroid) / 2.0)
