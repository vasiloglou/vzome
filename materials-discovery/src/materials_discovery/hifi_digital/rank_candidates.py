from __future__ import annotations

from copy import deepcopy

from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _required_metric(value: float | None, field_name: str, candidate_id: str) -> float:
    if value is None:
        raise ValueError(
            f"{field_name} missing for candidate {candidate_id}; run 'mdisc hifi-validate'"
        )
    return float(value)


def _candidate_score(config: SystemConfig, candidate: CandidateRecord) -> float:
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

    phonon_bonus = 0.15 if validation.phonon_pass is True else 0.0
    pass_bonus = 0.20 if validation.passed_checks is True else 0.0
    system_bias = len(config.system_name) * 0.001

    score = (
        2.4
        - 12.0 * delta_hull
        - 6.0 * uncertainty
        + 1.3 * md_score
        + 1.7 * xrd_confidence
        + phonon_bonus
        + pass_bonus
        + system_bias
    )
    return round(score, 6)


def rank_validated_candidates(
    config: SystemConfig,
    candidates: list[CandidateRecord],
) -> list[CandidateRecord]:
    """Rank digitally validated candidates with a deterministic uncertainty-aware score."""
    if not candidates:
        raise ValueError("no validated candidates found for hifi ranking")

    scored = [(_candidate_score(config, candidate), candidate) for candidate in candidates]
    scored_sorted = sorted(
        scored,
        key=lambda item: (
            -item[0],
            float(item[1].digital_validation.delta_e_proxy_hull_ev_per_atom or 1.0),
            float(item[1].digital_validation.uncertainty_ev_per_atom or 1.0),
            item[1].candidate_id,
        ),
    )

    ranked: list[CandidateRecord] = []
    for rank, (score, candidate) in enumerate(scored_sorted, start=1):
        copied = deepcopy(candidate)

        provenance = dict(copied.provenance)
        provenance["hifi_rank"] = {"rank": rank, "score": score}
        copied.provenance = provenance

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "ranked"
        copied.digital_validation = validation

        ranked.append(copied)

    return ranked
