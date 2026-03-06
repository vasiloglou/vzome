from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from materials_discovery.common.schema import CandidateRecord, SystemConfig


@dataclass(frozen=True)
class SurrogateModelSnapshot:
    system: str
    species: list[str]
    training_rows: int
    positive_count: int
    negative_count: int
    pass_rate: float
    positive_centroid: dict[str, float]
    uncertainty_mean: float
    delta_hull_mean: float

    def model_dump(self) -> dict[str, object]:
        return {
            "system": self.system,
            "species": self.species,
            "training_rows": self.training_rows,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "pass_rate": self.pass_rate,
            "positive_centroid": self.positive_centroid,
            "uncertainty_mean": self.uncertainty_mean,
            "delta_hull_mean": self.delta_hull_mean,
        }


def _mean(values: list[float], fallback: float) -> float:
    return mean(values) if values else fallback


def _build_positive_centroid(
    config: SystemConfig,
    positives: list[CandidateRecord],
    fallback_candidates: list[CandidateRecord],
) -> dict[str, float]:
    source = positives if positives else fallback_candidates
    centroid = {
        species: _mean([candidate.composition.get(species, 0.0) for candidate in source], 0.0)
        for species in sorted(config.species)
    }
    return {species: round(value, 6) for species, value in centroid.items()}


def train_surrogate_model(
    config: SystemConfig,
    validated_candidates: list[CandidateRecord],
) -> SurrogateModelSnapshot:
    """Train a deterministic surrogate summary from high-fidelity digital labels."""
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

    training_rows = len(validated_candidates)
    positive_count = len(positives)
    negative_count = len(negatives)

    snapshot = SurrogateModelSnapshot(
        system=config.system_name,
        species=sorted(config.species),
        training_rows=training_rows,
        positive_count=positive_count,
        negative_count=negative_count,
        pass_rate=round(positive_count / training_rows, 6),
        positive_centroid=_build_positive_centroid(config, positives, validated_candidates),
        uncertainty_mean=round(_mean(uncertainty_values, fallback=0.05), 6),
        delta_hull_mean=round(_mean(delta_hull_values, fallback=0.1), 6),
    )
    return snapshot
