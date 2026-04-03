from __future__ import annotations

from pathlib import Path
from typing import Any

from materials_discovery.common.io import write_json_object


def _as_float(payload: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = payload.get(key, default)
    if isinstance(value, int | float):
        return float(value)
    return default


def _rate(numerator: float, denominator: float) -> float:
    if denominator <= 0.0:
        return 0.0
    return numerator / denominator


def build_llm_generate_comparison(
    system: str,
    deterministic_generation: dict[str, Any],
    deterministic_screen: dict[str, Any],
    llm_generation: dict[str, Any],
    llm_screen: dict[str, Any],
) -> dict[str, Any]:
    deterministic_requested = _as_float(deterministic_generation, "requested_count")
    deterministic_generated = _as_float(deterministic_generation, "generated_count")
    llm_attempt_count = _as_float(llm_generation, "attempt_count")
    llm_generated = _as_float(llm_generation, "generated_count")

    deterministic_parse_rate = 0.0 if deterministic_requested == 0.0 else 1.0
    deterministic_compile_rate = 0.0 if deterministic_requested == 0.0 else 1.0
    llm_parse_rate = _as_float(llm_generation, "parse_pass_rate")
    llm_compile_rate = _as_float(llm_generation, "compile_pass_rate")

    deterministic_conversion_rate = _rate(deterministic_generated, deterministic_requested)
    llm_conversion_rate = _rate(llm_generated, llm_attempt_count)
    deterministic_screen_pass_rate = _as_float(deterministic_screen, "pass_rate")
    llm_screen_pass_rate = _as_float(llm_screen, "pass_rate")

    comparison = {
        "parse_pass_rate_delta": round(llm_parse_rate - deterministic_parse_rate, 6),
        "compile_pass_rate_delta": round(llm_compile_rate - deterministic_compile_rate, 6),
        "conversion_rate_delta": round(
            llm_conversion_rate - deterministic_conversion_rate,
            6,
        ),
        "screen_pass_rate_delta": round(
            llm_screen_pass_rate - deterministic_screen_pass_rate,
            6,
        ),
    }
    return {
        "system": system,
        "deterministic_generation": deterministic_generation,
        "deterministic_screen": deterministic_screen,
        "llm_generation": llm_generation,
        "llm_screen": llm_screen,
        "comparison": comparison,
    }


def write_llm_generate_comparison(payload: dict[str, Any], path: Path) -> Path:
    write_json_object(payload, path)
    return path
