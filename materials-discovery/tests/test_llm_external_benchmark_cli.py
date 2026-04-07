from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import write_json_object
from materials_discovery.llm.schema import (
    LlmExternalBenchmarkControlDelta,
    LlmExternalBenchmarkSliceSummary,
    LlmExternalBenchmarkSummary,
    LlmExternalBenchmarkTargetSummary,
    LlmServingIdentity,
)


def _benchmark_summary() -> LlmExternalBenchmarkSummary:
    external_target = LlmExternalBenchmarkTargetSummary(
        target_id="crystallm_cif_demo",
        target_label="CrystaLLM CIF demo",
        target_kind="external_target",
        model_id="al_cu_fe_external_cif_demo",
        registration_path="data/llm_external_models/al_cu_fe_external_cif_demo/registration.json",
        environment_path="data/llm_external_models/al_cu_fe_external_cif_demo/environment.json",
        smoke_check_path="data/llm_external_models/al_cu_fe_external_cif_demo/smoke_check.json",
        run_manifest_path="data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/crystallm_cif_demo/run_manifest.json",
        eligible_count=2,
        excluded_count=1,
        overall=LlmExternalBenchmarkSliceSummary(
            eligible_count=2,
            excluded_count=1,
            response_success_rate=1.0,
            parse_success_rate=1.0,
            exact_text_match_rate=0.5,
            composition_match_rate=0.5,
            mean_latency_s=0.02,
        ),
        by_target_family={
            "cif": LlmExternalBenchmarkSliceSummary(
                eligible_count=2,
                excluded_count=1,
                response_success_rate=1.0,
                parse_success_rate=1.0,
                exact_text_match_rate=0.5,
                composition_match_rate=0.5,
                mean_latency_s=0.02,
            )
        },
        by_fidelity_tier={
            "exact": LlmExternalBenchmarkSliceSummary(
                eligible_count=1,
                excluded_count=0,
                response_success_rate=1.0,
                parse_success_rate=1.0,
                exact_text_match_rate=0.0,
                composition_match_rate=0.0,
                mean_latency_s=0.02,
            ),
            "lossy": LlmExternalBenchmarkSliceSummary(
                eligible_count=1,
                excluded_count=1,
                response_success_rate=1.0,
                parse_success_rate=1.0,
                exact_text_match_rate=1.0,
                composition_match_rate=1.0,
                mean_latency_s=0.02,
            ),
        },
        control_deltas=[
            LlmExternalBenchmarkControlDelta(
                control_target_id="promoted_internal_control",
                control_label="Promoted internal control",
                control_role="promoted_default",
                shared_eligible_count=2,
                parse_success_rate_delta=0.0,
                exact_text_match_rate_delta=0.5,
                composition_match_rate_delta=0.5,
            )
        ],
        recommendation_lines=[
            "Benchmark recommendation: crystallm_cif_demo merits targeted follow-up on the periodic-safe slice before any broader workflow expansion."
        ],
        failed=False,
    )
    internal_target = LlmExternalBenchmarkTargetSummary(
        target_id="promoted_internal_control",
        target_label="Promoted internal control",
        target_kind="internal_control",
        control_role="promoted_default",
        run_manifest_path="data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/promoted_internal_control/run_manifest.json",
        eligible_count=2,
        excluded_count=1,
        overall=LlmExternalBenchmarkSliceSummary(
            eligible_count=2,
            excluded_count=1,
            response_success_rate=1.0,
            parse_success_rate=1.0,
            exact_text_match_rate=0.0,
            composition_match_rate=0.0,
            mean_latency_s=0.01,
        ),
        by_target_family={
            "cif": LlmExternalBenchmarkSliceSummary(
                eligible_count=2,
                excluded_count=1,
                response_success_rate=1.0,
                parse_success_rate=1.0,
                exact_text_match_rate=0.0,
                composition_match_rate=0.0,
                mean_latency_s=0.01,
            )
        },
        by_fidelity_tier={
            "exact": LlmExternalBenchmarkSliceSummary(
                eligible_count=1,
                excluded_count=0,
                response_success_rate=1.0,
                parse_success_rate=1.0,
                exact_text_match_rate=1.0,
                composition_match_rate=1.0,
                mean_latency_s=0.01,
            )
        },
        serving_identity=LlmServingIdentity(
            requested_model_lane="general_purpose",
            resolved_model_lane="general_purpose",
            resolved_model_lane_source="configured_lane",
            adapter="openai_compat_v1",
            provider="local",
            model="zomic-general-local-v1",
            effective_api_base="http://localhost:8000",
        ),
    )
    return LlmExternalBenchmarkSummary(
        benchmark_id="al_cu_fe_external_benchmark_v1",
        benchmark_set_id="al_cu_fe_translated_benchmark_v1",
        benchmark_set_manifest_path="data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json",
        generated_at_utc="2026-04-07T08:20:00Z",
        targets=[external_target, internal_target],
        recommendation_lines=list(external_target.recommendation_lines),
        failed_targets=[],
        summary_path="data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/benchmark_summary.json",
    )


def test_cli_llm_external_benchmark_prints_json_summary(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    spec_path = tmp_path / "al_cu_fe_external_benchmark.yaml"
    spec_path.write_text("benchmark_id: demo\n", encoding="utf-8")
    expected_out_path = tmp_path / "custom_summary.json"
    summary = _benchmark_summary()

    def _fake_execute(spec: Path, *, root: Path | None = None, out_path: Path | None = None):
        assert spec == spec_path
        assert root == tmp_path
        assert out_path == expected_out_path
        return summary

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.cli.execute_external_benchmark", _fake_execute)

    result = runner.invoke(
        app,
        [
            "llm-external-benchmark",
            "--spec",
            str(spec_path),
            "--out",
            str(expected_out_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["benchmark_id"] == "al_cu_fe_external_benchmark_v1"
    assert payload["summary_path"].endswith("/benchmark_summary.json")
    assert len(payload["targets"]) == 2
    assert any("periodic-safe slice" in line for line in payload["recommendation_lines"])


def test_cli_llm_inspect_external_benchmark_prints_scorecard_trace(
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    summary = _benchmark_summary()
    summary_path = tmp_path / "benchmark_summary.json"
    write_json_object(summary.model_dump(mode="json"), summary_path)

    result = runner.invoke(
        app,
        [
            "llm-inspect-external-benchmark",
            "--summary",
            str(summary_path),
        ],
    )

    assert result.exit_code == 0
    assert "Benchmark: al_cu_fe_external_benchmark_v1" in result.stdout
    assert "Target: crystallm_cif_demo [external_target]" in result.stdout
    assert "Control arm: promoted_default via zomic-general-local-v1 [general_purpose]" in result.stdout
    assert "By fidelity exact: eligible 1" in result.stdout
    assert "Control delta vs promoted_internal_control [promoted_default]" in result.stdout
    assert "Recommendation: Benchmark recommendation: crystallm_cif_demo merits targeted follow-up on the periodic-safe slice" in result.stdout


def test_cli_llm_inspect_external_benchmark_can_focus_one_target(
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    summary = _benchmark_summary()
    summary_path = tmp_path / "benchmark_summary.json"
    write_json_object(summary.model_dump(mode="json"), summary_path)

    result = runner.invoke(
        app,
        [
            "llm-inspect-external-benchmark",
            "--summary",
            str(summary_path),
            "--target-id",
            "crystallm_cif_demo",
        ],
    )

    assert result.exit_code == 0
    assert "Target count: 1" in result.stdout
    assert "Target: crystallm_cif_demo [external_target]" in result.stdout
    assert "Target: promoted_internal_control [internal_control]" not in result.stdout


def test_cli_llm_external_benchmark_returns_code_2_for_missing_spec(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-external-benchmark",
            "--spec",
            str(tmp_path / "missing_external_benchmark.yaml"),
        ],
    )

    assert result.exit_code == 2
    assert "llm-external-benchmark failed:" in result.stderr


def test_cli_llm_inspect_external_benchmark_returns_code_2_for_missing_summary(
    tmp_path: Path,
) -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "llm-inspect-external-benchmark",
            "--summary",
            str(tmp_path / "missing_benchmark_summary.json"),
        ],
    )

    assert result.exit_code == 2
    assert "llm-inspect-external-benchmark failed:" in result.stderr


def test_cli_llm_inspect_external_benchmark_returns_code_2_for_invalid_summary(
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    summary_path = tmp_path / "invalid_benchmark_summary.json"
    write_json_object({"benchmark_id": "broken"}, summary_path)

    result = runner.invoke(
        app,
        [
            "llm-inspect-external-benchmark",
            "--summary",
            str(summary_path),
        ],
    )

    assert result.exit_code == 2
    assert "llm-inspect-external-benchmark failed:" in result.stderr
