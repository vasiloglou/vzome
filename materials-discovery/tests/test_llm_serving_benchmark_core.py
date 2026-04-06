from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from materials_discovery.llm.schema import (
    LlmCheckpointLineage,
    LlmServingBenchmarkSpec,
    LlmServingIdentity,
    LlmServingBenchmarkTarget,
    LlmServingBenchmarkTargetResult,
    LlmServingSmokeCheck,
)
from materials_discovery.llm.serving_benchmark import (
    build_serving_benchmark_summary,
    run_serving_smoke_check,
)


def _config_path(name: str) -> Path:
    return Path(__file__).resolve().parents[1] / "configs" / "systems" / name


def _launch_target(
    *,
    system_config_path: str | None = None,
    generation_model_lane: str = "general_purpose",
    allow_fallback: bool = False,
) -> LlmServingBenchmarkTarget:
    return LlmServingBenchmarkTarget(
        target_id="hosted_generation",
        label="Hosted generation",
        workflow_role="campaign_launch",
        system_config_path=system_config_path or str(_config_path("al_cu_fe_llm_local.yaml")),
        campaign_spec_path="/tmp/campaign_spec.json",
        generation_model_lane=generation_model_lane,
        estimated_cost_usd=0.35,
        operator_friction_tier="low",
        allow_fallback=allow_fallback,
    )


def _evaluate_target(
    *,
    system_config_path: str | None = None,
    evaluation_model_lane: str = "specialized_materials",
) -> LlmServingBenchmarkTarget:
    return LlmServingBenchmarkTarget(
        target_id="specialized_assessment",
        label="Specialized assessment",
        workflow_role="llm_evaluate",
        system_config_path=system_config_path or str(_config_path("al_cu_fe_llm_local.yaml")),
        batch="top20",
        evaluation_model_lane=evaluation_model_lane,
        estimated_cost_usd=0.05,
        operator_friction_tier="high",
    )


def _set_perf_counter(monkeypatch: pytest.MonkeyPatch, start: float, end: float) -> None:
    values = iter([start, end])
    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.time.perf_counter",
        lambda: next(values),
    )


def test_run_serving_smoke_check_for_launch_target_uses_generation_lane(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str | None, str | None, str]] = []

    def fake_validate(adapter, *, adapter_key, requested_lane=None, resolved_lane=None):
        calls.append((adapter_key, requested_lane, resolved_lane, adapter.model))

    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.validate_llm_adapter_ready",
        fake_validate,
    )
    _set_perf_counter(monkeypatch, 10.0, 10.25)

    smoke_checks = run_serving_smoke_check(_launch_target())

    assert len(smoke_checks) == 1
    smoke = smoke_checks[0]
    assert smoke.role == "generation"
    assert smoke.status == "passed"
    assert smoke.requested_model_lane == "general_purpose"
    assert smoke.resolved_model_lane == "general_purpose"
    assert smoke.latency_s == pytest.approx(0.25)
    assert smoke.serving_identity is not None
    assert smoke.serving_identity.model == "zomic-general-local-v1"
    assert calls == [("openai_compat_v1", "general_purpose", "general_purpose", "zomic-general-local-v1")]


def test_run_serving_smoke_check_for_evaluate_target_uses_evaluation_lane(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str | None, str | None, str]] = []

    def fake_validate(adapter, *, adapter_key, requested_lane=None, resolved_lane=None):
        calls.append((adapter_key, requested_lane, resolved_lane, adapter.model))

    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.validate_llm_adapter_ready",
        fake_validate,
    )
    _set_perf_counter(monkeypatch, 5.0, 5.4)

    smoke_checks = run_serving_smoke_check(_evaluate_target())

    assert len(smoke_checks) == 1
    smoke = smoke_checks[0]
    assert smoke.role == "evaluation"
    assert smoke.status == "passed"
    assert smoke.requested_model_lane == "specialized_materials"
    assert smoke.resolved_model_lane == "specialized_materials"
    assert smoke.serving_identity is not None
    assert smoke.serving_identity.model == "materials-al-cu-fe-specialist-v1"
    assert calls == [
        (
            "openai_compat_v1",
            "specialized_materials",
            "specialized_materials",
            "materials-al-cu-fe-specialist-v1",
        )
    ]


def test_run_serving_smoke_check_fails_on_unapproved_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_payload = yaml.safe_load(_config_path("al_cu_fe_llm_local.yaml").read_text(encoding="utf-8"))
    config_payload["llm_generate"]["model_lanes"].pop("specialized_materials")
    config_path = tmp_path / "fallback_only.yaml"
    config_path.write_text(yaml.safe_dump(config_payload, sort_keys=False), encoding="utf-8")

    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.validate_llm_adapter_ready",
        lambda *args, **kwargs: None,
    )
    _set_perf_counter(monkeypatch, 2.0, 2.1)

    smoke_checks = run_serving_smoke_check(
        _launch_target(
            system_config_path=str(config_path),
            generation_model_lane="specialized_materials",
            allow_fallback=False,
        )
    )

    smoke = smoke_checks[0]
    assert smoke.status == "failed"
    assert smoke.resolved_model_lane == "general_purpose"
    assert smoke.resolved_model_lane_source == "configured_fallback"
    assert smoke.detail is not None
    assert "allow_fallback" in smoke.detail


def test_build_serving_benchmark_summary_preserves_missing_metrics_and_recommendations() -> None:
    spec = LlmServingBenchmarkSpec(
        benchmark_id="bench_v1",
        acceptance_pack_path="/tmp/acceptance.json",
        targets=[_launch_target(), _evaluate_target()],
    )
    target_results = [
        LlmServingBenchmarkTargetResult(
            target_id="hosted_generation",
            label="Hosted generation",
            workflow_role="campaign_launch",
            estimated_cost_usd=0.35,
            operator_friction_tier="low",
            smoke_checks=[
                LlmServingSmokeCheck(
                    target_id="hosted_generation",
                    role="generation",
                    status="passed",
                    requested_model_lane="general_purpose",
                    resolved_model_lane="general_purpose",
                    resolved_model_lane_source="configured_lane",
                    latency_s=0.2,
                )
            ],
            quality_metrics={"parse_success_rate": 0.91, "synthesizability_mean": None},
            execution_latency_s=0.2,
            summary_lines=["Hosted target completed."],
        ),
        LlmServingBenchmarkTargetResult(
            target_id="specialized_assessment",
            label="Specialized assessment",
            workflow_role="llm_evaluate",
            estimated_cost_usd=0.05,
            operator_friction_tier="high",
            smoke_checks=[
                LlmServingSmokeCheck(
                    target_id="specialized_assessment",
                    role="evaluation",
                    status="passed",
                    requested_model_lane="specialized_materials",
                    resolved_model_lane="specialized_materials",
                    resolved_model_lane_source="configured_lane",
                    latency_s=0.8,
                )
            ],
            quality_metrics={"parse_success_rate": None, "synthesizability_mean": 0.84},
            execution_latency_s=0.8,
            summary_lines=["Specialized target completed."],
        ),
        LlmServingBenchmarkTargetResult(
            target_id="fallback_failure",
            label="Fallback failure",
            workflow_role="campaign_launch",
            estimated_cost_usd=0.45,
            operator_friction_tier="medium",
            smoke_checks=[
                LlmServingSmokeCheck(
                    target_id="fallback_failure",
                    role="generation",
                    status="failed",
                    requested_model_lane="specialized_materials",
                    resolved_model_lane="general_purpose",
                    resolved_model_lane_source="configured_fallback",
                    latency_s=0.3,
                    detail="resolved via configured_fallback while allow_fallback is false",
                )
            ],
            quality_metrics={"parse_success_rate": None},
            summary_lines=["Fallback failure target did not pass smoke checks."],
        ),
    ]

    summary = build_serving_benchmark_summary(spec, target_results)

    assert any("Fastest target: hosted_generation" in line for line in summary.recommendation_lines)
    assert any("Cheapest target: specialized_assessment" in line for line in summary.recommendation_lines)
    assert any("Lowest operator friction: hosted_generation" in line for line in summary.recommendation_lines)
    assert summary.failed_targets == ["fallback_failure"]
    assert summary.targets[0].quality_metrics["synthesizability_mean"] is None
    assert summary.targets[1].quality_metrics["parse_success_rate"] is None


def test_build_serving_benchmark_summary_reports_adapted_checkpoint_improvement() -> None:
    spec = LlmServingBenchmarkSpec(
        benchmark_id="bench_adapted_v1",
        acceptance_pack_path="/tmp/acceptance.json",
        targets=[
            _launch_target().model_copy(update={"target_id": "baseline_local_generation"}),
            _launch_target().model_copy(update={"target_id": "adapted_checkpoint_generation"}),
        ],
    )
    target_results = [
        LlmServingBenchmarkTargetResult(
            target_id="baseline_local_generation",
            label="Baseline local generation",
            workflow_role="campaign_launch",
            estimated_cost_usd=0.03,
            operator_friction_tier="medium",
            smoke_checks=[
                LlmServingSmokeCheck(
                    target_id="baseline_local_generation",
                    role="generation",
                    status="passed",
                    requested_model_lane="general_purpose",
                    resolved_model_lane="general_purpose",
                    resolved_model_lane_source="configured_lane",
                    serving_identity=LlmServingIdentity(
                        requested_model_lane="general_purpose",
                        resolved_model_lane="general_purpose",
                        resolved_model_lane_source="configured_lane",
                        adapter="openai_compat_v1",
                        provider="openai_compat",
                        model="zomic-general-local-v1",
                    ),
                    latency_s=0.4,
                )
            ],
            quality_metrics={
                "parse_success_rate": 0.4,
                "compile_success_rate": 0.3,
                "generation_success_rate": 0.2,
            },
            execution_latency_s=0.4,
        ),
        LlmServingBenchmarkTargetResult(
            target_id="adapted_checkpoint_generation",
            label="Adapted checkpoint generation",
            workflow_role="campaign_launch",
            estimated_cost_usd=0.04,
            operator_friction_tier="medium",
            smoke_checks=[
                LlmServingSmokeCheck(
                    target_id="adapted_checkpoint_generation",
                    role="generation",
                    status="passed",
                    requested_model_lane="general_purpose",
                    resolved_model_lane="general_purpose",
                    resolved_model_lane_source="configured_lane",
                    serving_identity=LlmServingIdentity(
                        requested_model_lane="general_purpose",
                        resolved_model_lane="general_purpose",
                        resolved_model_lane_source="configured_lane",
                        adapter="openai_compat_v1",
                        provider="openai_compat",
                        model="zomic-adapted-local-v1",
                        checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
                        checkpoint_selection_source="family_promoted_default",
                        checkpoint_lifecycle_path="data/llm_checkpoints/families/adapted-al-cu-fe/lifecycle.json",
                        checkpoint_lifecycle_revision=3,
                        checkpoint_lineage=LlmCheckpointLineage(
                            checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
                            checkpoint_family="adapted-al-cu-fe",
                            registration_path="data/llm_checkpoints/ckpt-al-cu-fe-zomic-adapted/registration.json",
                            fingerprint="fp-adapted-001",
                            base_model="zomic-general-local-v1",
                            adaptation_method="lora",
                            adaptation_artifact_path="data/llm_checkpoints/ckpt-al-cu-fe-zomic-adapted/adapter_manifest.json",
                            corpus_manifest_path="data/llm_corpus/al_cu_fe_v1/manifest.json",
                            eval_set_manifest_path="data/llm_eval_sets/al_cu_fe_v1/manifest.json",
                        ),
                    ),
                    latency_s=0.5,
                )
            ],
            quality_metrics={
                "parse_success_rate": 0.8,
                "compile_success_rate": 0.6,
                "generation_success_rate": 0.5,
            },
            execution_latency_s=0.5,
        ),
    ]

    summary = build_serving_benchmark_summary(spec, target_results)

    assert any(
        "Adapted checkpoint improvement: adapted_checkpoint_generation vs baseline_local_generation" in line
        for line in summary.recommendation_lines
    )
    assert any(
        "Rollback baseline remains available: baseline_local_generation" in line
        for line in summary.recommendation_lines
    )
    assert any(
        "Checkpoint routing: adapted_checkpoint_generation ran ckpt-al-cu-fe-zomic-adapted, via family_promoted_default, lifecycle r3"
        in line
        for line in summary.recommendation_lines
    )
