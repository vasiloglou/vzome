from __future__ import annotations

from copy import deepcopy
from math import exp

from materials_discovery.active_learning.train_surrogate import (
    candidate_feature_map,
    feature_distance,
    feature_names,
)
from materials_discovery.common.benchmarking import CalibrationProfile, load_calibration_profile
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


def _rank_metrics(
    candidate: CandidateRecord,
    config: SystemConfig,
    calibration: CalibrationProfile,
    names: list[str],
) -> dict[str, float]:
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
    feature_row = candidate_feature_map(config, candidate)
    stable_distance = feature_distance(feature_row, calibration.stable_feature_centroid, names)
    unstable_distance = feature_distance(feature_row, calibration.unstable_feature_centroid, names)
    benchmark_alignment = unstable_distance - stable_distance

    uncertainty_penalty = _clamp(uncertainty / calibration.uncertainty_soft_cap, 0.0, 1.0)
    hull_penalty = _clamp(delta_hull / calibration.delta_hull_soft_cap, 0.0, 1.0)
    reference_penalty = _clamp(
        reference_distance / calibration.reference_distance_soft_cap,
        0.0,
        1.0,
    )
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
        + 0.10 * _clamp(max(0.0, stable_distance - unstable_distance), 0.0, 1.0)
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
        + 2.6
        * (
            (md_score - calibration.md_stability_floor)
            / max(0.05, 1.0 - calibration.md_stability_floor)
        )
        + 2.2 * (
            (xrd_confidence - calibration.xrd_confidence_floor)
            / max(0.05, 1.0 - calibration.xrd_confidence_floor)
        )
        + 1.2 * benchmark_alignment
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
        "benchmark_alignment": round(benchmark_alignment, 6),
        "uncertainty_penalty": round(uncertainty_penalty, 6),
        "hull_penalty": round(hull_penalty, 6),
    }


def rank_validated_candidates(
    config: SystemConfig,
    candidates: list[CandidateRecord],
    benchmark_context: dict | None = None,
) -> list[CandidateRecord]:
    """Rank digitally validated candidates with calibrated success and OOD components.

    Parameters
    ----------
    config:
        The active system config.
    candidates:
        Validated candidates to rank.
    benchmark_context:
        Optional pre-assembled benchmark run context dict.  When supplied it is
        embedded in the ``hifi_rank`` provenance block of each ranked candidate
        so operators can confirm which lane produced each result without opening
        separate config or manifest files.  Callers that do not supply this
        argument still get deterministic ranking — provenance is simply absent.

    Notes
    -----
    Any existing additive provenance such as ``llm_assessment`` is preserved but
    intentionally does not alter the ranking formula in this phase.
    """
    if not candidates:
        raise ValueError("no validated candidates found for hifi ranking")

    names = feature_names(config)
    calibration = load_calibration_profile(config, feature_names=names)

    # Calibration-profile provenance that surfaces in every ranked candidate
    calibration_provenance = {
        "source": calibration.source,
        "benchmark_corpus": config.backend.benchmark_corpus,
        "backend_mode": config.backend.mode,
    }

    scored = [
        (_rank_metrics(candidate, config, calibration, names), candidate)
        for candidate in candidates
    ]
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
        hifi_rank_block: dict = {
            "rank": rank,
            "score": metrics["decision_score"],
            "decision_score": metrics["decision_score"],
            "stability_probability": metrics["stability_probability"],
            "ood_score": metrics["ood_score"],
            "novelty_score": metrics["novelty_score"],
            "reference_distance": metrics["reference_distance"],
            "benchmark_alignment": metrics["benchmark_alignment"],
            "uncertainty_penalty": metrics["uncertainty_penalty"],
            "hull_penalty": metrics["hull_penalty"],
            "calibration_provenance": calibration_provenance,
        }
        if benchmark_context is not None:
            hifi_rank_block["benchmark_context"] = benchmark_context
        provenance["hifi_rank"] = hifi_rank_block
        copied.provenance = provenance

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "ranked"
        copied.digital_validation = validation

        ranked.append(copied)

    return ranked
