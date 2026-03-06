from __future__ import annotations

from copy import deepcopy
from math import exp

from materials_discovery.common.chemistry import describe_candidate
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _required_metric(value: float | None, field_name: str, candidate_id: str) -> float:
    if value is None:
        raise ValueError(
            f"{field_name} missing for candidate {candidate_id}; run 'mdisc hifi-validate'"
        )
    return float(value)


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-value))


def _rank_metrics(candidate: CandidateRecord, config: SystemConfig) -> dict[str, float]:
    validation = candidate.digital_validation
    uncertainty = _required_metric(
        validation.uncertainty_ev_per_atom,
        "digital_validation.uncertainty_ev_per_atom",
        candidate.candidate_id,
    )
    delta_hull = _required_metric(
        validation.delta_e_proxy_hull_ev_per_atom,
        "digital_validation.delta_e_proxy_hull_ev_per_atom",
        candidate.candidate_id,
    )
    md_score = _required_metric(
        validation.md_stability_score,
        "digital_validation.md_stability_score",
        candidate.candidate_id,
    )
    xrd_confidence = _required_metric(
        validation.xrd_confidence,
        "digital_validation.xrd_confidence",
        candidate.candidate_id,
    )

    descriptor = describe_candidate(
        candidate,
        strict_pairs=config.backend.mode == "real",
    )
    reference_distance = float(validation.proxy_hull_reference_distance or 0.0)

    uncertainty_penalty = _clamp(uncertainty / 0.05, 0.0, 1.0)
    hull_penalty = _clamp(delta_hull / 0.10, 0.0, 1.0)
    reference_penalty = _clamp(reference_distance / 0.18, 0.0, 1.0)
    radius_penalty = _clamp(descriptor.radius_mismatch / 0.12, 0.0, 1.0)
    en_penalty = _clamp(descriptor.electronegativity_spread / 0.18, 0.0, 1.0)
    vec_penalty = _clamp(abs(descriptor.vec - 6.0) / 4.0, 0.0, 1.0)
    complexity_penalty = _clamp(max(0.0, descriptor.qphi_complexity - 1.5) / 2.5, 0.0, 1.0)

    ood_score = (
        0.45 * reference_penalty
        + 0.20 * radius_penalty
        + 0.15 * en_penalty
        + 0.10 * vec_penalty
        + 0.10 * complexity_penalty
    )
    ood_score = round(_clamp(ood_score, 0.0, 1.0), 6)

    complexity_novelty = _clamp((descriptor.qphi_complexity - 0.5) / 3.0, 0.0, 1.0)
    composition_novelty = _clamp(reference_distance / 0.12, 0.0, 1.0)
    novelty_score = (
        0.60 * complexity_novelty + 0.40 * composition_novelty - 0.35 * ood_score
    )
    novelty_score = round(_clamp(novelty_score, 0.0, 1.0), 6)

    logit = (
        2.8
        - 3.4 * hull_penalty
        - 2.4 * uncertainty_penalty
        - 1.8 * ood_score
        + 2.6 * (md_score - 0.5)
        + 2.2 * (xrd_confidence - 0.5)
    )
    if validation.phonon_pass is True:
        logit += 0.35
    if validation.md_pass is True:
        logit += 0.25
    if validation.xrd_pass is True:
        logit += 0.20

    stability_probability = round(_clamp(_sigmoid(logit), 0.0, 1.0), 6)

    decision_score = (
        0.72 * stability_probability
        + 0.10 * novelty_score
        - 0.18 * ood_score
        - 0.08 * uncertainty_penalty
        - 0.08 * hull_penalty
    )
    if validation.passed_checks is True:
        decision_score += 0.03
    decision_score = round(decision_score, 6)

    return {
        "decision_score": decision_score,
        "stability_probability": stability_probability,
        "ood_score": ood_score,
        "novelty_score": novelty_score,
        "reference_distance": round(reference_distance, 6),
        "uncertainty_penalty": round(uncertainty_penalty, 6),
        "hull_penalty": round(hull_penalty, 6),
    }


def rank_validated_candidates(
    config: SystemConfig,
    candidates: list[CandidateRecord],
) -> list[CandidateRecord]:
    """Rank digitally validated candidates with calibrated success and OOD components."""
    if not candidates:
        raise ValueError("no validated candidates found for hifi ranking")

    scored = [(_rank_metrics(candidate, config), candidate) for candidate in candidates]
    scored_sorted = sorted(
        scored,
        key=lambda item: (
            -item[0]["decision_score"],
            -item[0]["stability_probability"],
            item[0]["ood_score"],
            float(item[1].digital_validation.delta_e_proxy_hull_ev_per_atom or 1.0),
            float(item[1].digital_validation.uncertainty_ev_per_atom or 1.0),
            item[1].candidate_id,
        ),
    )

    ranked: list[CandidateRecord] = []
    for rank, (metrics, candidate) in enumerate(scored_sorted, start=1):
        copied = deepcopy(candidate)

        provenance = dict(copied.provenance)
        provenance["hifi_rank"] = {
            "rank": rank,
            "score": metrics["decision_score"],
            "decision_score": metrics["decision_score"],
            "stability_probability": metrics["stability_probability"],
            "ood_score": metrics["ood_score"],
            "novelty_score": metrics["novelty_score"],
            "reference_distance": metrics["reference_distance"],
            "uncertainty_penalty": metrics["uncertainty_penalty"],
            "hull_penalty": metrics["hull_penalty"],
        }
        copied.provenance = provenance

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "ranked"
        copied.digital_validation = validation

        ranked.append(copied)

    return ranked
