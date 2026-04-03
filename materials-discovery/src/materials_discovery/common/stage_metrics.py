from __future__ import annotations

import hashlib
import json
from statistics import mean
from typing import Any

from materials_discovery.common.schema import CandidateRecord


def _rank_metric(candidate: CandidateRecord, key: str, default: float = 0.0) -> float:
    value = (candidate.provenance.get("hifi_rank") or {}).get(key, default)
    if isinstance(value, int | float):
        return float(value)
    return default


def generation_metrics(
    requested_count: int,
    generated_count: int,
    invalid_filtered_count: int,
    unique_count: int,
) -> dict[str, float | int | bool]:
    duplicate_rate = 0.0 if generated_count == 0 else 1.0 - (unique_count / generated_count)
    invalid_rate = 0.0 if requested_count == 0 else invalid_filtered_count / requested_count
    return {
        "requested_count": requested_count,
        "generated_count": generated_count,
        "unique_count": unique_count,
        "invalid_filtered_count": invalid_filtered_count,
        "duplicate_rate": round(duplicate_rate, 6),
        "invalid_rate": round(invalid_rate, 6),
        "passed": duplicate_rate <= 0.05,
    }


def llm_generation_metrics(
    requested_count: int,
    generated_count: int,
    attempt_count: int,
    parse_pass_count: int,
    compile_pass_count: int,
) -> dict[str, float | int | bool]:
    parse_pass_rate = 0.0 if attempt_count == 0 else parse_pass_count / attempt_count
    compile_pass_rate = 0.0 if attempt_count == 0 else compile_pass_count / attempt_count
    generation_success_rate = 0.0 if requested_count == 0 else generated_count / requested_count
    return {
        "requested_count": requested_count,
        "generated_count": generated_count,
        "attempt_count": attempt_count,
        "parse_pass_count": parse_pass_count,
        "compile_pass_count": compile_pass_count,
        "parse_pass_rate": round(parse_pass_rate, 6),
        "compile_pass_rate": round(compile_pass_rate, 6),
        "generation_success_rate": round(generation_success_rate, 6),
        "passed": generated_count > 0,
    }


def screening_calibration(
    input_count: int,
    relaxed_count: int,
    passed_count: int,
    shortlisted_count: int,
    min_distance_proxy: float,
    max_energy_proxy: float,
) -> dict[str, float | int]:
    pass_rate = 0.0 if relaxed_count == 0 else passed_count / relaxed_count
    shortlist_fraction = 0.0 if input_count == 0 else shortlisted_count / input_count
    return {
        "input_count": input_count,
        "relaxed_count": relaxed_count,
        "passed_count": passed_count,
        "shortlisted_count": shortlisted_count,
        "pass_rate": round(pass_rate, 6),
        "shortlist_fraction": round(shortlist_fraction, 6),
        "min_distance_threshold": min_distance_proxy,
        "max_energy_threshold": max_energy_proxy,
    }


def validation_calibration(candidates: list[CandidateRecord]) -> dict[str, float | int]:
    if not candidates:
        return {
            "validated_count": 0,
            "passed_count": 0,
            "pass_rate": 0.0,
            "uncertainty_mean": 0.0,
            "delta_hull_mean": 0.0,
            "proxy_hull_reference_distance_mean": 0.0,
            "proxy_hull_exact_match_rate": 0.0,
        }

    passed_count = sum(
        candidate.digital_validation.passed_checks is True for candidate in candidates
    )
    uncertainties = [
        float(candidate.digital_validation.uncertainty_ev_per_atom)
        for candidate in candidates
        if candidate.digital_validation.uncertainty_ev_per_atom is not None
    ]
    hulls = [
        float(candidate.digital_validation.delta_e_proxy_hull_ev_per_atom)
        for candidate in candidates
        if candidate.digital_validation.delta_e_proxy_hull_ev_per_atom is not None
    ]
    reference_distances = [
        float(candidate.digital_validation.proxy_hull_reference_distance)
        for candidate in candidates
        if candidate.digital_validation.proxy_hull_reference_distance is not None
    ]

    return {
        "validated_count": len(candidates),
        "passed_count": passed_count,
        "pass_rate": round(passed_count / len(candidates), 6),
        "uncertainty_mean": round(mean(uncertainties), 6) if uncertainties else 0.0,
        "delta_hull_mean": round(mean(hulls), 6) if hulls else 0.0,
        "proxy_hull_reference_distance_mean": (
            round(mean(reference_distances), 6) if reference_distances else 0.0
        ),
        "proxy_hull_exact_match_rate": (
            round(
                sum(distance <= 1e-6 for distance in reference_distances)
                / len(reference_distances),
                6,
            )
            if reference_distances
            else 0.0
        ),
    }


def ranking_calibration(candidates: list[CandidateRecord]) -> dict[str, float | int]:
    if not candidates:
        return {
            "ranked_count": 0,
            "score_mean": 0.0,
            "score_max": 0.0,
            "score_min": 0.0,
            "score_range": 0.0,
            "passed_count": 0,
            "passed_score_mean": 0.0,
            "failed_score_mean": 0.0,
            "stability_probability_mean": 0.0,
            "ood_score_mean": 0.0,
            "novelty_score_mean": 0.0,
            "top_10_pass_rate": 0.0,
            "top_25_pass_rate": 0.0,
            "ood_fraction": 0.0,
        }

    scores = [_rank_metric(candidate, "score") for candidate in candidates]
    stability_probabilities = [
        _rank_metric(candidate, "stability_probability") for candidate in candidates
    ]
    ood_scores = [_rank_metric(candidate, "ood_score") for candidate in candidates]
    novelty_scores = [_rank_metric(candidate, "novelty_score") for candidate in candidates]

    passed_count = sum(
        candidate.digital_validation.passed_checks is True for candidate in candidates
    )
    passed_scores = [
        _rank_metric(candidate, "score")
        for candidate in candidates
        if candidate.digital_validation.passed_checks is True
    ]
    failed_scores = [
        _rank_metric(candidate, "score")
        for candidate in candidates
        if candidate.digital_validation.passed_checks is not True
    ]
    top_10 = candidates[: min(10, len(candidates))]
    top_25 = candidates[: min(25, len(candidates))]
    return {
        "ranked_count": len(candidates),
        "score_mean": round(mean(scores), 6),
        "score_max": round(max(scores), 6),
        "score_min": round(min(scores), 6),
        "score_range": round(max(scores) - min(scores), 6),
        "passed_count": passed_count,
        "passed_score_mean": round(mean(passed_scores), 6) if passed_scores else 0.0,
        "failed_score_mean": round(mean(failed_scores), 6) if failed_scores else 0.0,
        "stability_probability_mean": round(mean(stability_probabilities), 6),
        "ood_score_mean": round(mean(ood_scores), 6),
        "novelty_score_mean": round(mean(novelty_scores), 6),
        "top_10_pass_rate": round(
            sum(candidate.digital_validation.passed_checks is True for candidate in top_10)
            / len(top_10),
            6,
        ),
        "top_25_pass_rate": round(
            sum(candidate.digital_validation.passed_checks is True for candidate in top_25)
            / len(top_25),
            6,
        ),
        "ood_fraction": round(sum(score >= 0.5 for score in ood_scores) / len(ood_scores), 6),
    }


def report_calibration(report: dict[str, Any]) -> dict[str, Any]:
    entries = report.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("report entries must be a list")

    high_priority = 0
    medium_priority = 0
    watch_priority = 0
    synthesize_count = 0
    secondary_count = 0
    hold_count = 0
    xrd_confidences: list[float] = []
    distinctiveness_values: list[float] = []
    stability_probabilities: list[float] = []
    ood_scores: list[float] = []
    top_three_passes = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        priority = entry.get("priority")
        if priority == "high":
            high_priority += 1
        if priority == "medium":
            medium_priority += 1
        if priority == "watch":
            watch_priority += 1
        recommendation = entry.get("recommendation")
        if recommendation == "synthesize":
            synthesize_count += 1
        if recommendation == "secondary":
            secondary_count += 1
        if recommendation == "hold":
            hold_count += 1
        xrd_confidences.append(float(entry.get("xrd_confidence", 0.0)))
        distinctiveness_values.append(float(entry.get("xrd_distinctiveness", 0.0)))
        stability_probabilities.append(float(entry.get("stability_probability", 0.0)))
        ood_scores.append(float(entry.get("ood_score", 0.0)))

    top_three = [entry for entry in entries[:3] if isinstance(entry, dict)]
    if top_three:
        top_three_passes = sum(bool(entry.get("passed_checks")) for entry in top_three)

    release_gate = report.get("release_gate", {})
    if not isinstance(release_gate, dict):
        release_gate = {}
    release_gate_pass_count = sum(bool(value) for value in release_gate.values())
    payload = json.dumps(report, sort_keys=True).encode()
    report_digest = hashlib.sha256(payload).hexdigest()[:16]

    return {
        "ranked_count": int(report.get("ranked_count", 0)),
        "reported_count": int(report.get("reported_count", 0)),
        "high_priority_count": high_priority,
        "medium_priority_count": medium_priority,
        "watch_priority_count": watch_priority,
        "synthesize_count": synthesize_count,
        "secondary_count": secondary_count,
        "hold_count": hold_count,
        "xrd_confidence_mean": round(mean(xrd_confidences), 6) if xrd_confidences else 0.0,
        "xrd_distinctiveness_mean": (
            round(mean(distinctiveness_values), 6) if distinctiveness_values else 0.0
        ),
        "xrd_distinctiveness_min": min(distinctiveness_values) if distinctiveness_values else 0.0,
        "stability_probability_mean": (
            round(mean(stability_probabilities), 6) if stability_probabilities else 0.0
        ),
        "max_ood_score": max(ood_scores) if ood_scores else 0.0,
        "top_3_pass_rate": round(top_three_passes / len(top_three), 6) if top_three else 0.0,
        "release_gate_ready": bool(release_gate.get("ready_for_experimental_pack", False)),
        "release_gate_pass_count": release_gate_pass_count,
        "report_fingerprint": str(report.get("report_fingerprint", "")),
        "report_digest": report_digest,
    }
