from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from materials_discovery.common.io import write_json_object
from materials_discovery.llm.schema import (
    LlmServingBenchmarkSpec,
    LlmServingBenchmarkTarget,
    LlmServingBenchmarkTargetResult,
    LlmServingIdentity,
    LlmServingSmokeCheck,
)
from materials_discovery.llm.serving_benchmark import load_serving_benchmark_spec
from materials_discovery.llm.storage import (
    llm_serving_benchmark_dir,
    llm_serving_benchmark_smoke_path,
    llm_serving_benchmark_summary_path,
)


def _config_path(name: str) -> Path:
    return Path(__file__).resolve().parents[1] / "configs" / "systems" / name


def _acceptance_pack_payload(system: str) -> dict[str, object]:
    return {
        "schema_version": "llm-acceptance-pack/v1",
        "pack_id": "pack_v1",
        "created_at_utc": "2026-04-05T06:00:00Z",
        "thresholds": {
            "min_parse_success_rate": 0.8,
            "min_compile_success_rate": 0.8,
            "min_generation_success_rate": 0.3,
            "min_shortlist_pass_rate": 0.05,
            "min_validation_pass_rate": 0.02,
            "min_novelty_score_mean": 0.0,
            "min_synthesizability_mean": 0.5,
        },
        "systems": [
            {
                "system": system,
                "generate_comparison_path": "generate.json",
                "pipeline_comparison_path": "pipeline.json",
                "parse_success_rate": 0.9,
                "compile_success_rate": 0.85,
                "generation_success_rate": 0.4,
                "shortlist_pass_rate": 0.1,
                "validation_pass_rate": 0.04,
                "novelty_score_mean": 0.25,
                "synthesizability_mean": 0.6,
                "report_release_gate_ready": False,
                "failing_metrics": ["compile_success_rate"],
                "passed": False,
            }
        ],
        "overall_passed": False,
    }


def _valid_launch_target(target_id: str = "hosted_generation") -> dict[str, object]:
    return {
        "target_id": target_id,
        "label": "Hosted generation",
        "workflow_role": "campaign_launch",
        "system_config_path": str(_config_path("al_cu_fe_llm_local.yaml")),
        "campaign_spec_path": "/tmp/campaign_spec.json",
        "generation_model_lane": "general_purpose",
        "estimated_cost_usd": 0.35,
        "operator_friction_tier": "low",
    }


def _valid_evaluate_target(target_id: str = "specialized_assessment") -> dict[str, object]:
    return {
        "target_id": target_id,
        "label": "Specialized assessment",
        "workflow_role": "llm_evaluate",
        "system_config_path": str(_config_path("al_cu_fe_llm_local.yaml")),
        "batch": "top20",
        "evaluation_model_lane": "specialized_materials",
        "estimated_cost_usd": 0.05,
        "operator_friction_tier": "high",
    }


def test_benchmark_spec_requires_shared_context_and_unique_targets() -> None:
    with pytest.raises(ValueError, match="at least two"):
        LlmServingBenchmarkSpec(
            benchmark_id="bench_v1",
            acceptance_pack_path="/tmp/acceptance.json",
            targets=[LlmServingBenchmarkTarget(**_valid_launch_target())],
        )

    with pytest.raises(ValueError, match="unique target_id"):
        LlmServingBenchmarkSpec(
            benchmark_id="bench_v1",
            acceptance_pack_path="/tmp/acceptance.json",
            targets=[
                LlmServingBenchmarkTarget(**_valid_launch_target("dup")),
                LlmServingBenchmarkTarget(**_valid_evaluate_target("dup")),
            ],
        )


def test_benchmark_target_role_validation_paths() -> None:
    with pytest.raises(ValueError, match="campaign_spec_path"):
        LlmServingBenchmarkTarget(
            **{
                **_valid_launch_target(),
                "campaign_spec_path": None,
            }
        )

    with pytest.raises(ValueError, match="batch"):
        LlmServingBenchmarkTarget(
            **{
                **_valid_evaluate_target(),
                "batch": None,
            }
        )


def test_benchmark_target_defaults_and_nested_serving_identity() -> None:
    launch_target = LlmServingBenchmarkTarget(**_valid_launch_target())
    assert launch_target.allow_fallback is False

    serving_identity = LlmServingIdentity(
        requested_model_lane="general_purpose",
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        adapter="anthropic_api_v1",
        provider="anthropic",
        model="hosted-general-placeholder",
    )
    smoke = LlmServingSmokeCheck(
        target_id="hosted_generation",
        role="generation",
        status="passed",
        requested_model_lane="general_purpose",
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        serving_identity=serving_identity,
        latency_s=0.18,
    )
    result = LlmServingBenchmarkTargetResult(
        target_id="hosted_generation",
        label="Hosted generation",
        workflow_role="campaign_launch",
        estimated_cost_usd=0.35,
        operator_friction_tier="low",
        smoke_checks=[smoke],
        quality_metrics={"parse_success_rate": 0.92, "synthesizability_mean": None},
        summary_lines=["Hosted target is fastest."],
    )

    assert result.smoke_checks[0].serving_identity is not None
    assert result.quality_metrics["synthesizability_mean"] is None


def test_storage_helpers_use_llm_serving_benchmark_root(tmp_path: Path) -> None:
    assert llm_serving_benchmark_dir("bench_v1", root=tmp_path) == (
        tmp_path / "data" / "benchmarks" / "llm_serving" / "bench_v1"
    )
    assert llm_serving_benchmark_smoke_path("bench_v1", root=tmp_path) == (
        tmp_path / "data" / "benchmarks" / "llm_serving" / "bench_v1" / "smoke_checks.json"
    )
    assert llm_serving_benchmark_summary_path("bench_v1", root=tmp_path) == (
        tmp_path / "data" / "benchmarks" / "llm_serving" / "bench_v1" / "benchmark_summary.json"
    )


def test_load_serving_benchmark_spec_rejects_mixed_system_targets(tmp_path: Path) -> None:
    acceptance_pack_path = tmp_path / "acceptance_pack.json"
    write_json_object(_acceptance_pack_payload("Al-Cu-Fe"), acceptance_pack_path)
    spec_path = tmp_path / "benchmark.yaml"
    spec_path.write_text(
        yaml.safe_dump(
            {
                "benchmark_id": "bench_v1",
                "acceptance_pack_path": str(acceptance_pack_path),
                "targets": [
                    _valid_launch_target("hosted_generation"),
                    {
                        **_valid_evaluate_target("mismatched_assessment"),
                        "system_config_path": str(_config_path("sc_zn_llm_local.yaml")),
                    },
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="shared acceptance-pack context"):
        load_serving_benchmark_spec(spec_path)
