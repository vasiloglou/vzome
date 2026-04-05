from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.llm.schema import (
    LlmServingBenchmarkSummary,
    LlmServingBenchmarkTargetResult,
    LlmServingSmokeCheck,
)


def _summary(*, benchmark_id: str = "bench_v1") -> LlmServingBenchmarkSummary:
    return LlmServingBenchmarkSummary(
        benchmark_id=benchmark_id,
        acceptance_pack_path="/tmp/acceptance_pack.json",
        generated_at_utc="2026-04-05T07:10:00Z",
        targets=[
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
                        latency_s=0.18,
                    )
                ],
                quality_metrics={"parse_success_rate": 0.9},
                execution_latency_s=0.45,
            )
        ],
        recommendation_lines=[
            "Fastest target: hosted_generation (0.45s)",
            "Cheapest target: hosted_generation ($0.35)",
        ],
    )


def test_cli_llm_serving_benchmark_smoke_only_success(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    captured: dict[str, object] = {}

    def _fake_execute(spec_path, *, smoke_only=False, out_path=None):
        captured["spec_path"] = spec_path
        captured["smoke_only"] = smoke_only
        captured["out_path"] = out_path
        return _summary()

    monkeypatch.setattr("materials_discovery.cli.execute_serving_benchmark", _fake_execute)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    spec_path = tmp_path / "benchmark.yaml"
    result = runner.invoke(app, ["llm-serving-benchmark", "--spec", str(spec_path), "--smoke-only"])

    assert result.exit_code == 0
    assert captured == {
        "spec_path": spec_path,
        "smoke_only": True,
        "out_path": None,
    }
    assert "hosted_generation [generation] passed" in result.stdout
    assert "Smoke artifact:" in result.stdout


def test_cli_llm_serving_benchmark_returns_code_2_on_strict_smoke_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()

    monkeypatch.setattr(
        "materials_discovery.cli.execute_serving_benchmark",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("strict smoke failed for hosted_generation")
        ),
    )
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        ["llm-serving-benchmark", "--spec", str(tmp_path / "benchmark.yaml")],
    )

    assert result.exit_code == 2
    assert "llm-serving-benchmark failed: strict smoke failed for hosted_generation" in result.stderr


def test_cli_llm_serving_benchmark_prints_recommendations_and_summary_path(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()

    monkeypatch.setattr(
        "materials_discovery.cli.execute_serving_benchmark",
        lambda *args, **kwargs: _summary(),
    )
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        ["llm-serving-benchmark", "--spec", str(tmp_path / "benchmark.yaml")],
    )

    assert result.exit_code == 0
    assert "Fastest target: hosted_generation (0.45s)" in result.stdout
    assert "Cheapest target: hosted_generation ($0.35)" in result.stdout
    assert "Benchmark summary:" in result.stdout


def test_cli_llm_serving_benchmark_passes_output_override(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    captured: dict[str, object] = {}

    def _fake_execute(spec_path, *, smoke_only=False, out_path=None):
        captured["spec_path"] = spec_path
        captured["smoke_only"] = smoke_only
        captured["out_path"] = out_path
        return _summary(benchmark_id="override_bench")

    monkeypatch.setattr("materials_discovery.cli.execute_serving_benchmark", _fake_execute)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    out_path = tmp_path / "custom-summary.json"
    result = runner.invoke(
        app,
        [
            "llm-serving-benchmark",
            "--spec",
            str(tmp_path / "benchmark.yaml"),
            "--out",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert captured == {
        "spec_path": tmp_path / "benchmark.yaml",
        "smoke_only": False,
        "out_path": out_path,
    }
    assert f"Benchmark summary: {out_path}" in result.stdout
