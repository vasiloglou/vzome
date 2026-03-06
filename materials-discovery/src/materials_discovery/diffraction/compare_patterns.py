from __future__ import annotations

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


def _pattern_gap(pattern: dict[str, Any], peers: list[dict[str, Any]]) -> float:
    if not peers:
        return 0.0

    this_first = float(pattern["peaks"][0]["two_theta"])
    peer_firsts = [float(peer["peaks"][0]["two_theta"]) for peer in peers]
    nearest = min(abs(this_first - peer_first) for peer_first in peer_firsts)
    return round(min(1.0, nearest / 5.0), 6)


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
        priority = "high" if passed_checks and distinctiveness >= 0.2 else "medium"
        if not passed_checks:
            priority = "watch"

        report_entries.append(
            {
                "candidate_id": candidate.candidate_id,
                "rank": _rank_from_provenance(candidate),
                "hifi_score": round(score, 6),
                "passed_checks": passed_checks,
                "xrd_confidence": float(candidate.digital_validation.xrd_confidence or 0.0),
                "xrd_distinctiveness": distinctiveness,
                "priority": priority,
                "top_peaks": pattern["peaks"][:4],
            }
        )

    return {
        "system": config.system_name,
        "report_version": "0.1.0",
        "ranked_count": len(ranked_candidates),
        "reported_count": len(report_entries),
        "entries": report_entries,
    }
