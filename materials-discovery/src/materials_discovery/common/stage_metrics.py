from __future__ import annotations

from statistics import mean
from typing import Any

from materials_discovery.common.schema import CandidateRecord


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
            "passed_count": 0,
        }

    scores: list[float] = []
    for candidate in candidates:
        score_value = (candidate.provenance.get("hifi_rank") or {}).get("score", 0.0)
        if isinstance(score_value, int | float):
            scores.append(float(score_value))
        else:
            scores.append(0.0)

    passed_count = sum(
        candidate.digital_validation.passed_checks is True for candidate in candidates
    )
    return {
        "ranked_count": len(candidates),
        "score_mean": round(mean(scores), 6),
        "score_max": round(max(scores), 6),
        "score_min": round(min(scores), 6),
        "passed_count": passed_count,
    }


def report_calibration(report: dict[str, Any]) -> dict[str, float | int]:
    entries = report.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("report entries must be a list")

    high_priority = 0
    watch_priority = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        priority = entry.get("priority")
        if priority == "high":
            high_priority += 1
        if priority == "watch":
            watch_priority += 1

    return {
        "ranked_count": int(report.get("ranked_count", 0)),
        "reported_count": int(report.get("reported_count", 0)),
        "high_priority_count": high_priority,
        "watch_priority_count": watch_priority,
    }
