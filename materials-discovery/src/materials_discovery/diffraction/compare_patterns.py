from __future__ import annotations

import hashlib
import json
from typing import Any

from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _rank_from_provenance(candidate: CandidateRecord) -> int:
    raw_rank = (candidate.provenance.get("hifi_rank") or {}).get("rank")
    if isinstance(raw_rank, int):
        return raw_rank
    if isinstance(raw_rank, float) and raw_rank.is_integer():
        return int(raw_rank)
    return 10**9


def _score_from_provenance(candidate: CandidateRecord) -> float:
    raw_score = (candidate.provenance.get("hifi_rank") or {}).get("score")
    if isinstance(raw_score, int | float):
        return float(raw_score)
    return 0.0


def _rank_metric(candidate: CandidateRecord, key: str, default: float = 0.0) -> float:
    value = (candidate.provenance.get("hifi_rank") or {}).get(key, default)
    if isinstance(value, int | float):
        return float(value)
    return default


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _peak_similarity(peak: dict[str, Any], peer_peak: dict[str, Any]) -> float:
    theta_gap = min(1.0, abs(float(peak["two_theta"]) - float(peer_peak["two_theta"])) / 3.5)
    intensity_gap = min(1.0, abs(float(peak["intensity"]) - float(peer_peak["intensity"])) / 100.0)
    return max(0.0, 1.0 - 0.75 * theta_gap - 0.25 * intensity_gap)


def _pattern_similarity(pattern: dict[str, Any], peer: dict[str, Any]) -> float:
    peaks = pattern["peaks"][:6]
    peer_peaks = peer["peaks"][:6]
    if not peaks or not peer_peaks:
        return 0.0
    similarities = [
        max(_peak_similarity(peak, peer_peak) for peer_peak in peer_peaks)
        for peak in peaks
    ]
    return round(sum(similarities) / len(similarities), 6)


def _pattern_gap(pattern: dict[str, Any], peers: list[dict[str, Any]]) -> float:
    if not peers:
        return 0.0

    nearest_similarity = max(_pattern_similarity(pattern, peer) for peer in peers)
    return round(max(0.0, 1.0 - nearest_similarity), 6)


def _risk_flags(candidate: CandidateRecord, distinctiveness: float) -> list[str]:
    validation = candidate.digital_validation
    flags: list[str] = []
    if validation.passed_checks is not True:
        flags.append("failed_digital_checks")
    if float(validation.delta_e_proxy_hull_ev_per_atom or 0.0) > 0.06:
        flags.append("marginal_proxy_hull")
    if float(validation.uncertainty_ev_per_atom or 0.0) > 0.03:
        flags.append("high_uncertainty")
    if float(validation.xrd_confidence or 0.0) < 0.60:
        flags.append("weak_xrd_match")
    if _rank_metric(candidate, "ood_score") >= 0.50:
        flags.append("out_of_distribution")
    if distinctiveness < 0.12:
        flags.append("pattern_overlap")
    return flags


def _priority_and_recommendation(
    candidate: CandidateRecord,
    *,
    distinctiveness: float,
    xrd_confidence: float,
) -> tuple[str, str]:
    passed_checks = candidate.digital_validation.passed_checks is True
    stability_probability = _rank_metric(candidate, "stability_probability")
    ood_score = _rank_metric(candidate, "ood_score")
    decision_score = _score_from_provenance(candidate)

    if (
        passed_checks
        and stability_probability >= 0.65
        and ood_score <= 0.35
        and xrd_confidence >= 0.60
        and distinctiveness >= 0.12
    ):
        return "high", "synthesize"
    if (
        (passed_checks or decision_score >= 0.45)
        and ood_score <= 0.55
        and xrd_confidence >= 0.50
    ):
        return "medium", "secondary"
    return "watch", "hold"


def _report_fingerprint(report_entries: list[dict[str, Any]]) -> str:
    payload = [
        {
            "candidate_id": entry["candidate_id"],
            "rank": entry["rank"],
            "recommendation": entry["recommendation"],
            "priority": entry["priority"],
            "top_peaks": entry["top_peaks"],
        }
        for entry in report_entries
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def compile_experiment_report(
    config: SystemConfig,
    ranked_candidates: list[CandidateRecord],
    xrd_patterns: list[dict[str, Any]],
    top_n: int = 10,
) -> dict[str, Any]:
    """Build an experiment-facing report from ranked candidates and synthetic XRD patterns."""
    if not ranked_candidates:
        raise ValueError("no ranked candidates available for report generation")

    pattern_by_id = {str(pattern["candidate_id"]): pattern for pattern in xrd_patterns}

    ranked = sorted(
        ranked_candidates,
        key=lambda candidate: (_rank_from_provenance(candidate), candidate.candidate_id),
    )
    selected = ranked[: min(top_n, len(ranked))]

    report_entries: list[dict[str, Any]] = []
    for candidate in selected:
        pattern = pattern_by_id.get(candidate.candidate_id)
        if pattern is None:
            raise ValueError(f"xrd pattern missing for candidate {candidate.candidate_id}")

        peers = [
            pattern_by_id[peer.candidate_id]
            for peer in selected
            if peer.candidate_id != candidate.candidate_id and peer.candidate_id in pattern_by_id
        ]
        distinctiveness = _pattern_gap(pattern, peers)

        score = _score_from_provenance(candidate)
        passed_checks = candidate.digital_validation.passed_checks is True
        xrd_confidence = float(candidate.digital_validation.xrd_confidence or 0.0)
        priority, recommendation = _priority_and_recommendation(
            candidate,
            distinctiveness=distinctiveness,
            xrd_confidence=xrd_confidence,
        )
        risk_flags = _risk_flags(candidate, distinctiveness)
        validation = candidate.digital_validation
        report_entries.append(
            {
                "candidate_id": candidate.candidate_id,
                "rank": _rank_from_provenance(candidate),
                "hifi_score": round(score, 6),
                "passed_checks": passed_checks,
                "stability_probability": round(_rank_metric(candidate, "stability_probability"), 6),
                "ood_score": round(_rank_metric(candidate, "ood_score"), 6),
                "novelty_score": round(_rank_metric(candidate, "novelty_score"), 6),
                "xrd_confidence": xrd_confidence,
                "xrd_distinctiveness": distinctiveness,
                "priority": priority,
                "recommendation": recommendation,
                "risk_flags": risk_flags,
                "composition": candidate.composition,
                "proxy_hull_reference_phases": validation.proxy_hull_reference_phases or [],
                "evidence": {
                    "decision_score": round(score, 6),
                    "reference_distance": round(_rank_metric(candidate, "reference_distance"), 6),
                    "uncertainty_penalty": round(_rank_metric(candidate, "uncertainty_penalty"), 6),
                    "hull_penalty": round(_rank_metric(candidate, "hull_penalty"), 6),
                    "delta_e_proxy_hull_ev_per_atom": float(
                        validation.delta_e_proxy_hull_ev_per_atom or 0.0
                    ),
                    "uncertainty_ev_per_atom": float(validation.uncertainty_ev_per_atom or 0.0),
                    "md_stability_score": float(validation.md_stability_score or 0.0),
                    "committee_std_ev_per_atom": float(validation.committee_std_ev_per_atom or 0.0),
                    "xrd_confidence": xrd_confidence,
                    "passed_checks": passed_checks,
                },
                "selection_rationale": (
                    "promote_for_synthesis"
                    if recommendation == "synthesize"
                    else "retain_for_secondary_review"
                    if recommendation == "secondary"
                    else "hold_until_better_evidence"
                ),
                "top_peaks": pattern["peaks"][:4],
                "pattern_fingerprint": pattern["fingerprint"],
            }
        )

    synthesize_count = sum(entry["recommendation"] == "synthesize" for entry in report_entries)
    top_slice = report_entries[: min(3, len(report_entries))]
    top_xrd_confidence_mean = (
        round(sum(float(entry["xrd_confidence"]) for entry in top_slice) / len(top_slice), 6)
        if top_slice
        else 0.0
    )
    top_distinctiveness_mean = (
        round(sum(float(entry["xrd_distinctiveness"]) for entry in top_slice) / len(top_slice), 6)
        if top_slice
        else 0.0
    )
    top_stability_mean = (
        round(sum(float(entry["stability_probability"]) for entry in top_slice) / len(top_slice), 6)
        if top_slice
        else 0.0
    )
    top_max_ood = max((float(entry["ood_score"]) for entry in top_slice), default=0.0)
    release_gate = {
        "enough_synthesis_candidates": synthesize_count >= 1,
        "top_xrd_confidence_gate": top_xrd_confidence_mean >= 0.60,
        "top_distinctiveness_gate": top_distinctiveness_mean >= 0.12,
        "top_stability_gate": top_stability_mean >= 0.55,
        "top_ood_gate": top_max_ood <= 0.55,
    }
    release_gate["ready_for_experimental_pack"] = all(release_gate.values())

    report_fingerprint = _report_fingerprint(report_entries)
    return {
        "system": config.system_name,
        "report_version": "0.2.0",
        "ranked_count": len(ranked_candidates),
        "reported_count": len(report_entries),
        "report_fingerprint": report_fingerprint,
        "summary": {
            "top_candidate_ids": [entry["candidate_id"] for entry in report_entries[:3]],
            "high_priority_count": sum(entry["priority"] == "high" for entry in report_entries),
            "medium_priority_count": sum(entry["priority"] == "medium" for entry in report_entries),
            "watch_priority_count": sum(entry["priority"] == "watch" for entry in report_entries),
            "synthesize_count": synthesize_count,
            "secondary_count": sum(
                entry["recommendation"] == "secondary" for entry in report_entries
            ),
            "hold_count": sum(entry["recommendation"] == "hold" for entry in report_entries),
            "xrd_confidence_mean": round(
                sum(float(entry["xrd_confidence"]) for entry in report_entries)
                / len(report_entries),
                6,
            ),
            "xrd_distinctiveness_mean": round(
                sum(float(entry["xrd_distinctiveness"]) for entry in report_entries)
                / len(report_entries),
                6,
            ),
            "stability_probability_mean": round(
                sum(float(entry["stability_probability"]) for entry in report_entries)
                / len(report_entries),
                6,
            ),
            "max_ood_score": round(
                max(float(entry["ood_score"]) for entry in report_entries),
                6,
            ),
        },
        "release_gate": release_gate,
        "entries": report_entries,
    }
