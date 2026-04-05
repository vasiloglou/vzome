from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from pathlib import Path

from materials_discovery.common.io import (
    load_json_object,
    load_jsonl,
    load_yaml,
    workspace_root,
    write_json_object,
)
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.compare import (
    build_campaign_comparison,
    build_campaign_outcome_snapshot,
)
from materials_discovery.llm.evaluate import evaluate_llm_candidates
from materials_discovery.llm.generate import generate_llm_candidates
from materials_discovery.llm.launch import (
    build_serving_identity,
    resolve_campaign_launch,
    resolve_serving_lane,
)
from materials_discovery.llm.replay import load_campaign_launch_bundle
from materials_discovery.llm.runtime import resolve_llm_adapter, validate_llm_adapter_ready
from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmCampaignLaunchSummary,
    LlmCampaignSpec,
    LlmServingBenchmarkSpec,
    LlmServingBenchmarkSummary,
    LlmServingBenchmarkTarget,
    LlmServingBenchmarkTargetResult,
    LlmServingSmokeCheck,
)
from materials_discovery.llm.storage import (
    llm_campaign_comparison_path,
    llm_campaign_launch_summary_path,
    llm_campaign_resolved_launch_path,
    llm_serving_benchmark_smoke_path,
    llm_serving_benchmark_summary_path,
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


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _new_benchmark_launch_id(target_id: str) -> str:
    normalized_target = re.sub(r"[^a-z0-9]+", "_", target_id.strip().lower()).strip("_")
    return (
        f"launch_{normalized_target}_"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    )


def _target_quality_metrics_from_launch(snapshot) -> dict[str, float | bool | None]:
    quality_metrics: dict[str, float | bool | None] = {
        "parse_success_rate": snapshot.parse_success_rate,
        "compile_success_rate": snapshot.compile_success_rate,
        "generation_success_rate": snapshot.generation_success_rate,
    }
    if snapshot.synthesizability_mean is not None:
        quality_metrics["synthesizability_mean"] = snapshot.synthesizability_mean
    if snapshot.report_release_gate_ready is not None:
        quality_metrics["report_release_gate_ready"] = snapshot.report_release_gate_ready
    return quality_metrics


def _evaluation_batch_is_aligned(batch: str) -> bool:
    normalized = batch.strip().lower()
    return normalized == "all" or bool(re.fullmatch(r"top\d+", normalized))


def _evaluate_quality_metrics(output_path: Path) -> dict[str, float | bool | None]:
    rows = load_jsonl(output_path)
    synth_scores: list[float] = []
    for row in rows:
        provenance = row.get("provenance")
        if not isinstance(provenance, dict):
            continue
        assessment = provenance.get("llm_assessment")
        if not isinstance(assessment, dict):
            continue
        score = assessment.get("synthesizability_score")
        if isinstance(score, int | float):
            synth_scores.append(float(score))
    if not synth_scores:
        return {}
    return {
        "synthesizability_mean": round(sum(synth_scores) / len(synth_scores), 6)
    }


def _execute_launch_target(
    spec: LlmServingBenchmarkSpec,
    target: LlmServingBenchmarkTarget,
    *,
    artifact_root: Path,
    smoke_checks: list[LlmServingSmokeCheck],
) -> LlmServingBenchmarkTargetResult:
    start = time.perf_counter()
    config_path = Path(target.system_config_path)
    config = SystemConfig.model_validate(load_yaml(config_path))
    campaign_spec_path = Path(target.campaign_spec_path or "")
    campaign_spec = LlmCampaignSpec.model_validate(load_json_object(campaign_spec_path))
    launch_id = _new_benchmark_launch_id(target.target_id)

    resolved_config, resolved_launch = resolve_campaign_launch(
        campaign_spec,
        config,
        campaign_spec_path=campaign_spec_path,
        launch_id=launch_id,
        artifact_root=artifact_root,
        requested_model_lane_override=target.generation_model_lane,
    )
    system_slug = _system_slug(resolved_config.system_name)
    candidates_path = (
        artifact_root / "data" / "candidates" / f"{system_slug}_{target.target_id}_{launch_id}.jsonl"
    )
    resolved_launch.effective_candidates_path = str(candidates_path)
    resolved_launch.output_override_used = False

    resolved_launch_path = llm_campaign_resolved_launch_path(
        campaign_spec.campaign_id,
        launch_id,
        root=artifact_root,
    )
    write_json_object(resolved_launch.model_dump(mode="json"), resolved_launch_path)

    launch_summary_path = llm_campaign_launch_summary_path(
        campaign_spec.campaign_id,
        launch_id,
        root=artifact_root,
    )
    campaign_metadata = {
        "campaign_id": campaign_spec.campaign_id,
        "launch_id": launch_id,
        "campaign_spec_path": str(campaign_spec_path),
        "proposal_id": campaign_spec.proposal_id,
        "approval_id": campaign_spec.approval_id,
        "requested_model_lanes": list(resolved_launch.requested_model_lanes),
        "resolved_model_lane": resolved_launch.resolved_model_lane,
        "resolved_model_lane_source": resolved_launch.resolved_model_lane_source,
        "launch_summary_path": str(launch_summary_path),
    }
    summary = generate_llm_candidates(
        resolved_config,
        candidates_path,
        count=campaign_spec.launch_baseline.default_count,
        config_path=config_path,
        prompt_instruction_deltas=resolved_launch.prompt_instruction_deltas,
        campaign_metadata=campaign_metadata,
        serving_identity=resolved_launch.serving_identity,
    )

    launch_summary = LlmCampaignLaunchSummary(
        launch_id=launch_id,
        campaign_id=campaign_spec.campaign_id,
        campaign_spec_path=str(campaign_spec_path),
        proposal_id=campaign_spec.proposal_id,
        approval_id=campaign_spec.approval_id,
        system=campaign_spec.system,
        status="succeeded",
        created_at_utc=_utc_now(),
        requested_count=campaign_spec.launch_baseline.default_count,
        requested_model_lanes=list(resolved_launch.requested_model_lanes),
        resolved_model_lane=resolved_launch.resolved_model_lane,
        resolved_model_lane_source=resolved_launch.resolved_model_lane_source,
        serving_identity=resolved_launch.serving_identity,
        resolved_launch_path=str(resolved_launch_path),
        run_manifest_path=summary.run_manifest_path,
        candidates_path=str(candidates_path),
    )
    write_json_object(launch_summary.model_dump(mode="json"), launch_summary_path)

    bundle = load_campaign_launch_bundle(launch_summary_path, root=artifact_root)
    current_outcome = build_campaign_outcome_snapshot(bundle, root=artifact_root)
    comparison = build_campaign_comparison(
        bundle,
        current_outcome=current_outcome,
        root=artifact_root,
    )
    execution_latency_s = round(max(time.perf_counter() - start, 0.0), 6)
    comparison_path = llm_campaign_comparison_path(
        comparison.campaign_id,
        comparison.comparison_id,
        root=artifact_root,
    )
    return LlmServingBenchmarkTargetResult(
        target_id=target.target_id,
        label=target.label,
        workflow_role=target.workflow_role,
        estimated_cost_usd=target.estimated_cost_usd,
        operator_friction_tier=target.operator_friction_tier,
        smoke_checks=smoke_checks,
        quality_metrics=_target_quality_metrics_from_launch(current_outcome),
        execution_latency_s=execution_latency_s,
        launch_summary_path=str(launch_summary_path),
        comparison_path=str(comparison_path),
        summary_lines=list(comparison.summary_lines),
    )


def _execute_evaluate_target(
    spec: LlmServingBenchmarkSpec,
    target: LlmServingBenchmarkTarget,
    *,
    artifact_root: Path,
    smoke_checks: list[LlmServingSmokeCheck],
) -> LlmServingBenchmarkTargetResult:
    del spec
    if target.batch is None or not _evaluation_batch_is_aligned(target.batch):
        raise ValueError(
            "benchmark evaluation batch must stay aligned with the shared acceptance-pack context"
        )

    start = time.perf_counter()
    config_path = Path(target.system_config_path)
    config = SystemConfig.model_validate(load_yaml(config_path))
    system_slug = _system_slug(config.system_name)
    evaluate_output_path = (
        artifact_root
        / "data"
        / "llm_evaluated"
        / f"{system_slug}_{target.target_id}_{target.batch}.jsonl"
    )
    evaluate_summary = evaluate_llm_candidates(
        config,
        evaluate_output_path,
        batch=target.batch,
        requested_model_lane=target.evaluation_model_lane,
    )
    evaluate_summary_path = evaluate_output_path.with_name(
        f"{evaluate_output_path.stem}_summary.json"
    )
    write_json_object(evaluate_summary.model_dump(mode="json"), evaluate_summary_path)
    execution_latency_s = round(max(time.perf_counter() - start, 0.0), 6)
    return LlmServingBenchmarkTargetResult(
        target_id=target.target_id,
        label=target.label,
        workflow_role=target.workflow_role,
        estimated_cost_usd=target.estimated_cost_usd,
        operator_friction_tier=target.operator_friction_tier,
        smoke_checks=smoke_checks,
        quality_metrics=_evaluate_quality_metrics(evaluate_output_path),
        execution_latency_s=execution_latency_s,
        evaluate_summary_path=str(evaluate_summary_path),
    )


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

    generation_targets = [
        result for result in target_results if result.workflow_role == "campaign_launch"
    ]
    adapted_generation_targets = [
        result
        for result in generation_targets
        if any(
            smoke.serving_identity is not None
            and smoke.serving_identity.checkpoint_lineage is not None
            for smoke in result.smoke_checks
        )
    ]
    baseline_generation_targets = [
        result
        for result in generation_targets
        if all(
            smoke.serving_identity is None
            or smoke.serving_identity.checkpoint_lineage is None
            for smoke in result.smoke_checks
        )
    ]
    if adapted_generation_targets and baseline_generation_targets:
        adapted_target = adapted_generation_targets[0]
        baseline_target = baseline_generation_targets[0]
        delta_bits: list[str] = []
        for metric_name in (
            "parse_success_rate",
            "compile_success_rate",
            "generation_success_rate",
        ):
            adapted_metric = adapted_target.quality_metrics.get(metric_name)
            baseline_metric = baseline_target.quality_metrics.get(metric_name)
            if not isinstance(adapted_metric, (int, float)) or not isinstance(
                baseline_metric, (int, float)
            ):
                continue
            delta = float(adapted_metric) - float(baseline_metric)
            if delta > 0:
                delta_bits.append(f"{metric_name} +{delta:.2f}")
        if delta_bits:
            recommendation_lines.append(
                "Adapted checkpoint improvement: "
                f"{adapted_target.target_id} vs {baseline_target.target_id} "
                f"({', '.join(delta_bits)})"
            )
        else:
            recommendation_lines.append(
                "Adapted checkpoint comparison: "
                f"{adapted_target.target_id} did not beat {baseline_target.target_id} "
                "on the tracked generation metrics."
            )

    return LlmServingBenchmarkSummary(
        benchmark_id=spec.benchmark_id,
        acceptance_pack_path=spec.acceptance_pack_path,
        generated_at_utc=_utc_now(),
        targets=target_results,
        recommendation_lines=recommendation_lines,
        failed_targets=failed_targets,
    )


def execute_serving_benchmark(
    spec_path: Path,
    *,
    smoke_only: bool = False,
    out_path: Path | None = None,
) -> LlmServingBenchmarkSummary:
    spec = load_serving_benchmark_spec(spec_path)
    artifact_root = workspace_root()

    target_results: list[LlmServingBenchmarkTargetResult] = []
    all_smoke_checks: list[LlmServingSmokeCheck] = []
    for target in spec.targets:
        smoke_checks = run_serving_smoke_check(target, root=artifact_root)
        all_smoke_checks.extend(smoke_checks)
        execution_latency = None if not smoke_checks else smoke_checks[-1].latency_s
        target_results.append(
            LlmServingBenchmarkTargetResult(
                target_id=target.target_id,
                label=target.label,
                workflow_role=target.workflow_role,
                estimated_cost_usd=target.estimated_cost_usd,
                operator_friction_tier=target.operator_friction_tier,
                smoke_checks=smoke_checks,
                quality_metrics={},
                execution_latency_s=execution_latency,
            )
        )

    smoke_path = llm_serving_benchmark_smoke_path(spec.benchmark_id, root=artifact_root)
    write_json_object(
        {
            "benchmark_id": spec.benchmark_id,
            "generated_at_utc": _utc_now(),
            "smoke_checks": [item.model_dump(mode="json") for item in all_smoke_checks],
        },
        smoke_path,
    )

    summary = build_serving_benchmark_summary(spec, target_results)
    if smoke_only:
        return summary

    if summary.failed_targets:
        failed = ", ".join(summary.failed_targets)
        raise RuntimeError(
            f"strict smoke failed for {failed}; see {smoke_path}"
        )

    for target in spec.targets:
        if target.workflow_role == "llm_evaluate":
            if target.batch is None or not _evaluation_batch_is_aligned(target.batch):
                raise ValueError(
                    "benchmark evaluation batch must stay aligned with the shared acceptance-pack context"
                )

    target_results = []
    for target in spec.targets:
        smoke_for_target = [item for item in all_smoke_checks if item.target_id == target.target_id]
        if target.workflow_role == "campaign_launch":
            result = _execute_launch_target(
                spec,
                target,
                artifact_root=artifact_root,
                smoke_checks=smoke_for_target,
            )
        else:
            result = _execute_evaluate_target(
                spec,
                target,
                artifact_root=artifact_root,
                smoke_checks=smoke_for_target,
            )
        target_results.append(result)

    summary = build_serving_benchmark_summary(spec, target_results)
    summary_path = out_path or llm_serving_benchmark_summary_path(
        spec.benchmark_id,
        root=artifact_root,
    )
    write_json_object(summary.model_dump(mode="json"), summary_path)
    return summary
