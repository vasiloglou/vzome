from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from materials_discovery.common.io import load_json_object, load_yaml, workspace_root
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.launch import build_serving_identity, resolve_serving_lane
from materials_discovery.llm.runtime import resolve_llm_adapter, validate_llm_adapter_ready
from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmServingBenchmarkSpec,
    LlmServingBenchmarkSummary,
    LlmServingBenchmarkTarget,
    LlmServingBenchmarkTargetResult,
    LlmServingSmokeCheck,
)


def _resolve_spec_relative_path(spec_path: Path, candidate: str) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path
    return (spec_path.parent / path).resolve()


def load_serving_benchmark_spec(spec_path: Path) -> LlmServingBenchmarkSpec:
    raw_spec = load_yaml(spec_path)
    spec = LlmServingBenchmarkSpec.model_validate(raw_spec)

    acceptance_pack_file = _resolve_spec_relative_path(spec_path, spec.acceptance_pack_path)
    acceptance_pack = LlmAcceptancePack.model_validate(load_json_object(acceptance_pack_file))
    acceptance_systems = {system_metrics.system for system_metrics in acceptance_pack.systems}
    if not acceptance_systems:
        raise ValueError("shared acceptance-pack context must include at least one system")

    for target in spec.targets:
        system_config_file = _resolve_spec_relative_path(spec_path, target.system_config_path)
        system_config = SystemConfig.model_validate(load_yaml(system_config_file))
        if system_config.system_name not in acceptance_systems:
            raise ValueError(
                "benchmark targets must stay within the shared acceptance-pack context"
            )

    return spec.model_copy(
        update={
            "acceptance_pack_path": str(acceptance_pack_file),
            "targets": [
                target.model_copy(
                    update={
                        "system_config_path": str(
                            _resolve_spec_relative_path(spec_path, target.system_config_path)
                        ),
                        "campaign_spec_path": (
                            str(_resolve_spec_relative_path(spec_path, target.campaign_spec_path))
                            if target.campaign_spec_path is not None
                            else None
                        ),
                    }
                )
                for target in spec.targets
            ],
        }
    )


def _resolve_runtime_path(path_str: str, *, root: Path | None = None) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    base_root = workspace_root() if root is None else root
    return (base_root / path).resolve()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _role_for_target(target: LlmServingBenchmarkTarget) -> str:
    return "generation" if target.workflow_role == "campaign_launch" else "evaluation"


def _requested_lane_for_target(target: LlmServingBenchmarkTarget) -> str | None:
    if target.workflow_role == "campaign_launch":
        return target.generation_model_lane
    return target.evaluation_model_lane


def run_serving_smoke_check(
    target: LlmServingBenchmarkTarget,
    *,
    root: Path | None = None,
) -> list[LlmServingSmokeCheck]:
    start = time.perf_counter()
    role = _role_for_target(target)
    requested_lane = _requested_lane_for_target(target)
    resolved_lane: str | None = None
    resolved_source = None
    serving_identity = None

    try:
        config_path = _resolve_runtime_path(target.system_config_path, root=root)
        config = SystemConfig.model_validate(load_yaml(config_path))
        if requested_lane is None:
            raise ValueError(
                f"{target.workflow_role} targets require a requested model lane for smoke checks"
            )

        resolved_lane, lane_config, resolved_source = resolve_serving_lane(
            requested_lane,
            config.llm_generate,
            config.backend,
        )
        effective_backend = config.backend.model_copy(deep=True)
        if lane_config is not None:
            effective_backend.llm_adapter = lane_config.adapter
            effective_backend.llm_provider = lane_config.provider
            effective_backend.llm_model = lane_config.model
            effective_backend.llm_api_base = lane_config.api_base

        adapter = resolve_llm_adapter(
            effective_backend.mode,
            backend=effective_backend,
            llm_generate=config.llm_generate,
        )
        adapter_key = effective_backend.llm_adapter or "llm_fixture_v1"
        serving_identity = build_serving_identity(
            requested_lane=requested_lane,
            resolved_lane=resolved_lane,
            lane_source=resolved_source,
            backend=config.backend,
            lane_config=lane_config,
        )
        validate_llm_adapter_ready(
            adapter,
            adapter_key=adapter_key,
            requested_lane=requested_lane,
            resolved_lane=resolved_lane,
        )

        status = "passed"
        detail = None
        if requested_lane != resolved_lane and not target.allow_fallback:
            status = "failed"
            detail = (
                f"resolved via {resolved_source} to '{resolved_lane}' while allow_fallback is false"
            )
    except Exception as exc:
        status = "failed"
        detail = str(exc)

    latency_s = max(time.perf_counter() - start, 0.0)
    return [
        LlmServingSmokeCheck(
            target_id=target.target_id,
            role=role,
            status=status,
            requested_model_lane=requested_lane,
            resolved_model_lane=resolved_lane,
            resolved_model_lane_source=resolved_source,
            serving_identity=serving_identity,
            latency_s=latency_s,
            detail=detail,
        )
    ]


def build_serving_benchmark_summary(
    spec: LlmServingBenchmarkSpec,
    target_results: list[LlmServingBenchmarkTargetResult],
) -> LlmServingBenchmarkSummary:
    recommendation_lines: list[str] = []

    with_latency = [result for result in target_results if result.execution_latency_s is not None]
    if with_latency:
        fastest = min(with_latency, key=lambda result: float(result.execution_latency_s or 0.0))
        recommendation_lines.append(
            f"Fastest target: {fastest.target_id} ({fastest.execution_latency_s:.2f}s)"
        )

    if target_results:
        cheapest = min(target_results, key=lambda result: result.estimated_cost_usd)
        recommendation_lines.append(
            f"Cheapest target: {cheapest.target_id} (${cheapest.estimated_cost_usd:.2f})"
        )

    friction_order = {"low": 0, "medium": 1, "high": 2}
    if target_results:
        lowest_friction = min(
            target_results,
            key=lambda result: (
                friction_order[result.operator_friction_tier],
                result.target_id,
            ),
        )
        recommendation_lines.append(
            "Lowest operator friction: "
            f"{lowest_friction.target_id} ({lowest_friction.operator_friction_tier})"
        )

    failed_targets: list[str] = []
    for result in target_results:
        if any(smoke.status == "failed" for smoke in result.smoke_checks):
            failed_targets.append(result.target_id)

    return LlmServingBenchmarkSummary(
        benchmark_id=spec.benchmark_id,
        acceptance_pack_path=spec.acceptance_pack_path,
        generated_at_utc=_utc_now(),
        targets=target_results,
        recommendation_lines=recommendation_lines,
        failed_targets=failed_targets,
    )
