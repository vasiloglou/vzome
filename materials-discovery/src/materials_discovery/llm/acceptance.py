from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from materials_discovery.common.io import load_json_object, write_json_object
from materials_discovery.llm.schema import (
    LlmAcceptanceBenchmarkInput,
    LlmAcceptancePack,
    LlmAcceptanceSystemMetrics,
    LlmAcceptanceThresholds,
)


def _as_float(payload: dict[str, object], key: str, default: float = 0.0) -> float:
    value = payload.get(key, default)
    if isinstance(value, int | float):
        return float(value)
    return default


def load_acceptance_benchmark_input(
    *,
    system: str,
    generate_comparison_path: Path,
    pipeline_comparison_path: Path,
) -> LlmAcceptanceBenchmarkInput:
    return LlmAcceptanceBenchmarkInput(
        system=system,
        generate_comparison_path=str(generate_comparison_path),
        pipeline_comparison_path=str(pipeline_comparison_path),
        generate_comparison=load_json_object(generate_comparison_path),
        pipeline_comparison=load_json_object(pipeline_comparison_path),
    )


def _system_metrics(
    benchmark: LlmAcceptanceBenchmarkInput,
    thresholds: LlmAcceptanceThresholds,
) -> LlmAcceptanceSystemMetrics:
    generation = benchmark.generate_comparison.get("llm_generation", {})
    pipeline_llm = benchmark.pipeline_comparison.get("llm", {})
    screen = pipeline_llm.get("screen", {})
    validation = pipeline_llm.get("hifi_validate", {})
    ranking = pipeline_llm.get("hifi_rank", {})
    report = pipeline_llm.get("report", {})

    metrics = {
        "parse_success_rate": _as_float(generation, "parse_pass_rate"),
        "compile_success_rate": _as_float(generation, "compile_pass_rate"),
        "generation_success_rate": _as_float(generation, "generation_success_rate"),
        "shortlist_pass_rate": _as_float(screen, "pass_rate"),
        "validation_pass_rate": _as_float(validation, "pass_rate"),
        "novelty_score_mean": _as_float(ranking, "novelty_score_mean"),
        "synthesizability_mean": _as_float(report, "llm_synthesizability_mean"),
    }

    failing_metrics: list[str] = []
    if metrics["parse_success_rate"] < thresholds.min_parse_success_rate:
        failing_metrics.append("parse_success_rate")
    if metrics["compile_success_rate"] < thresholds.min_compile_success_rate:
        failing_metrics.append("compile_success_rate")
    if metrics["generation_success_rate"] < thresholds.min_generation_success_rate:
        failing_metrics.append("generation_success_rate")
    if metrics["shortlist_pass_rate"] < thresholds.min_shortlist_pass_rate:
        failing_metrics.append("shortlist_pass_rate")
    if metrics["validation_pass_rate"] < thresholds.min_validation_pass_rate:
        failing_metrics.append("validation_pass_rate")
    if metrics["novelty_score_mean"] < thresholds.min_novelty_score_mean:
        failing_metrics.append("novelty_score_mean")
    if metrics["synthesizability_mean"] < thresholds.min_synthesizability_mean:
        failing_metrics.append("synthesizability_mean")

    return LlmAcceptanceSystemMetrics(
        system=benchmark.system,
        generate_comparison_path=benchmark.generate_comparison_path,
        pipeline_comparison_path=benchmark.pipeline_comparison_path,
        parse_success_rate=metrics["parse_success_rate"],
        compile_success_rate=metrics["compile_success_rate"],
        generation_success_rate=metrics["generation_success_rate"],
        shortlist_pass_rate=metrics["shortlist_pass_rate"],
        validation_pass_rate=metrics["validation_pass_rate"],
        novelty_score_mean=metrics["novelty_score_mean"],
        synthesizability_mean=metrics["synthesizability_mean"],
        report_release_gate_ready=bool(report.get("release_gate_ready", False)),
        failing_metrics=failing_metrics,
        passed=not failing_metrics,
    )


def build_llm_acceptance_pack(
    *,
    pack_id: str,
    benchmark_inputs: list[LlmAcceptanceBenchmarkInput],
    thresholds: LlmAcceptanceThresholds | None = None,
    eval_set_manifest_path: str | None = None,
) -> LlmAcceptancePack:
    effective_thresholds = thresholds or LlmAcceptanceThresholds()
    systems = [_system_metrics(benchmark, effective_thresholds) for benchmark in benchmark_inputs]
    return LlmAcceptancePack(
        pack_id=pack_id,
        created_at_utc=datetime.now(UTC).isoformat(),
        eval_set_manifest_path=eval_set_manifest_path,
        thresholds=effective_thresholds,
        systems=systems,
        overall_passed=all(system.passed for system in systems),
    )


def write_llm_acceptance_pack(pack: LlmAcceptancePack, path: Path) -> Path:
    write_json_object(pack.model_dump(mode="json"), path)
    return path
