from __future__ import annotations

from pathlib import Path
from typing import Any

from materials_discovery.common.io import write_json_object


def _as_float(payload: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = payload.get(key, default)
    if isinstance(value, int | float):
        return float(value)
    return default


def _as_bool(payload: dict[str, Any], key: str) -> bool:
    return bool(payload.get(key, False))


def build_llm_pipeline_comparison(
    system: str,
    deterministic_screen: dict[str, Any],
    deterministic_validate: dict[str, Any],
    deterministic_rank: dict[str, Any],
    deterministic_report: dict[str, Any],
    llm_screen: dict[str, Any],
    llm_validate: dict[str, Any],
    llm_rank: dict[str, Any],
    llm_report: dict[str, Any],
) -> dict[str, Any]:
    comparison = {
        "screen_pass_rate_delta": round(
            _as_float(llm_screen, "pass_rate") - _as_float(deterministic_screen, "pass_rate"),
            6,
        ),
        "validation_pass_rate_delta": round(
            _as_float(llm_validate, "pass_rate") - _as_float(deterministic_validate, "pass_rate"),
            6,
        ),
        "novelty_score_mean_delta": round(
            _as_float(llm_rank, "novelty_score_mean")
            - _as_float(deterministic_rank, "novelty_score_mean"),
            6,
        ),
        "top_10_pass_rate_delta": round(
            _as_float(llm_rank, "top_10_pass_rate")
            - _as_float(deterministic_rank, "top_10_pass_rate"),
            6,
        ),
        "report_synthesize_count_delta": int(
            _as_float(llm_report, "synthesize_count")
            - _as_float(deterministic_report, "synthesize_count")
        ),
        "report_high_priority_count_delta": int(
            _as_float(llm_report, "high_priority_count")
            - _as_float(deterministic_report, "high_priority_count")
        ),
        "llm_assessed_count_delta": int(
            _as_float(llm_report, "llm_assessed_count")
            - _as_float(deterministic_report, "llm_assessed_count")
        ),
        "report_release_gate_ready_delta": int(
            _as_bool(llm_report, "release_gate_ready")
        )
        - int(_as_bool(deterministic_report, "release_gate_ready")),
    }

    return {
        "system": system,
        "deterministic": {
            "screen": deterministic_screen,
            "hifi_validate": deterministic_validate,
            "hifi_rank": deterministic_rank,
            "report": deterministic_report,
        },
        "llm": {
            "screen": llm_screen,
            "hifi_validate": llm_validate,
            "hifi_rank": llm_rank,
            "report": llm_report,
        },
        "comparison": comparison,
    }


def write_llm_pipeline_comparison(payload: dict[str, Any], path: Path) -> Path:
    write_json_object(payload, path)
    return path
