from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_json_object, load_yaml
from materials_discovery.llm.pipeline_benchmark import (
    build_llm_pipeline_comparison,
    write_llm_pipeline_comparison,
)


def _repo_workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _copy_sc_zn_seed(tmp_workspace: Path) -> None:
    seed_source = _repo_workspace() / "designs" / "zomic" / "sc_zn_tsai_bridge.zomic"
    seed_target = tmp_workspace / "designs" / "zomic" / "sc_zn_tsai_bridge.zomic"
    seed_target.parent.mkdir(parents=True, exist_ok=True)
    seed_target.write_text(seed_source.read_text(encoding="utf-8"), encoding="utf-8")


def _fake_compile_factory(fixture_name: str):
    def _fake_compile(
        zomic_text: str,
        *,
        artifact_root: Path | None = None,
        **_: object,
    ) -> dict[str, object]:
        del zomic_text
        prototype_path = _repo_workspace() / "data" / "prototypes" / fixture_name
        if artifact_root is None:
            orbit_library_path = prototype_path
            raw_export_path = prototype_path.with_suffix(".raw.json")
        else:
            artifact_root.mkdir(parents=True, exist_ok=True)
            orbit_library_path = artifact_root / "compiled.json"
            orbit_library_path.write_text(
                prototype_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            raw_export_path = artifact_root / "compiled.raw.json"
            raw_export_path.write_text("{}", encoding="utf-8")
        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "error_kind": None,
            "error_message": None,
            "raw_export_path": str(raw_export_path),
            "orbit_library_path": str(orbit_library_path),
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
        }

    return _fake_compile


def _evaluation_fixture_output(system_name: str) -> str:
    payload = {
        "synthesizability_score": 0.71 if system_name == "Al-Cu-Fe" else 0.68,
        "precursor_hints": ["Al powder", "Cu powder", "Fe powder"]
        if system_name == "Al-Cu-Fe"
        else ["Sc granules", "Zn shot"],
        "anomaly_flags": [],
        "literature_context": f"Offline benchmark fixture for {system_name}.",
        "rationale": "Offline regression fixture.",
    }
    return json.dumps(payload, sort_keys=True)


def _write_config_with_llm_evaluate(
    source_config: Path,
    destination: Path,
    *,
    system_name: str,
) -> Path:
    data = load_yaml(source_config)
    data["llm_evaluate"] = {
        "prompt_template": "materials_assess_v1",
        "temperature": 0.1,
        "max_tokens": 512,
        "fixture_outputs": [_evaluation_fixture_output(system_name)],
    }
    destination.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return destination


def _stage_calibration(summary_json: str) -> dict[str, object]:
    summary = json.loads(summary_json)
    return load_json_object(Path(summary["calibration_path"]))


def _run_pipeline_lane(
    runner: CliRunner,
    *,
    config_path: Path,
    generation_command: str,
    count: int,
) -> dict[str, dict[str, object]]:
    generate_args = [generation_command, "--config", str(config_path), "--count", str(count)]
    generate_result = runner.invoke(app, generate_args)
    assert generate_result.exit_code == 0, generate_result.stdout

    screen_result = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen_result.exit_code == 0, screen_result.stdout

    validate_result = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "all"],
    )
    assert validate_result.exit_code == 0, validate_result.stdout

    rank_result = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert rank_result.exit_code == 0, rank_result.stdout

    evaluate_result = runner.invoke(
        app,
        ["llm-evaluate", "--config", str(config_path), "--batch", "all"],
    )
    assert evaluate_result.exit_code == 0, evaluate_result.stdout

    report_result = runner.invoke(app, ["report", "--config", str(config_path)])
    assert report_result.exit_code == 0, report_result.stdout

    return {
        "screen": _stage_calibration(screen_result.stdout),
        "hifi_validate": _stage_calibration(validate_result.stdout),
        "hifi_rank": _stage_calibration(rank_result.stdout),
        "report": _stage_calibration(report_result.stdout),
    }


def test_build_llm_pipeline_comparison_computes_downstream_deltas() -> None:
    comparison = build_llm_pipeline_comparison(
        "Al-Cu-Fe",
        {"pass_rate": 0.5},
        {"pass_rate": 0.2},
        {"novelty_score_mean": 0.3, "top_10_pass_rate": 0.4},
        {"synthesize_count": 1, "high_priority_count": 2, "llm_assessed_count": 5, "release_gate_ready": False},
        {"pass_rate": 0.6},
        {"pass_rate": 0.35},
        {"novelty_score_mean": 0.45, "top_10_pass_rate": 0.6},
        {"synthesize_count": 3, "high_priority_count": 4, "llm_assessed_count": 6, "release_gate_ready": True},
    )

    metrics = comparison["comparison"]
    assert metrics["screen_pass_rate_delta"] == pytest.approx(0.1)
    assert metrics["validation_pass_rate_delta"] == pytest.approx(0.15)
    assert metrics["novelty_score_mean_delta"] == pytest.approx(0.15)
    assert metrics["top_10_pass_rate_delta"] == pytest.approx(0.2)
    assert metrics["report_synthesize_count_delta"] == 2
    assert metrics["report_release_gate_ready_delta"] == 1


@pytest.mark.llm_lane
@pytest.mark.parametrize(
    ("system_name", "deterministic_config", "llm_config", "fixture_name"),
    [
        (
            "Al-Cu-Fe",
            "configs/systems/al_cu_fe.yaml",
            "configs/systems/al_cu_fe_llm_mock.yaml",
            "al_cu_fe_mackay_1_1.json",
        ),
        (
            "Sc-Zn",
            "configs/systems/sc_zn.yaml",
            "configs/systems/sc_zn_llm_mock.yaml",
            "sc_zn_tsai_sczn6.json",
        ),
    ],
)
def test_offline_llm_pipeline_benchmark_lane(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    system_name: str,
    deterministic_config: str,
    llm_config: str,
    fixture_name: str,
) -> None:
    repo_workspace = _repo_workspace()
    tmp_workspace = tmp_path / "workspace"
    tmp_workspace.mkdir(parents=True, exist_ok=True)
    _copy_sc_zn_seed(tmp_workspace)

    deterministic_config_path = _write_config_with_llm_evaluate(
        repo_workspace / deterministic_config,
        tmp_path / f"{system_name.lower().replace('-', '_')}_det.yaml",
        system_name=system_name,
    )
    llm_config_path = _write_config_with_llm_evaluate(
        repo_workspace / llm_config,
        tmp_path / f"{system_name.lower().replace('-', '_')}_llm.yaml",
        system_name=system_name,
    )

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_workspace)
    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: tmp_workspace)
    monkeypatch.setattr("materials_discovery.llm.evaluate.workspace_root", lambda: tmp_workspace)
    monkeypatch.setattr(
        "materials_discovery.llm.generate.compile_zomic_script",
        _fake_compile_factory(fixture_name),
    )

    runner = CliRunner()
    deterministic_lane = _run_pipeline_lane(
        runner,
        config_path=deterministic_config_path,
        generation_command="generate",
        count=3,
    )
    llm_lane = _run_pipeline_lane(
        runner,
        config_path=llm_config_path,
        generation_command="llm-generate",
        count=3,
    )

    comparison = build_llm_pipeline_comparison(
        system_name,
        deterministic_lane["screen"],
        deterministic_lane["hifi_validate"],
        deterministic_lane["hifi_rank"],
        deterministic_lane["report"],
        llm_lane["screen"],
        llm_lane["hifi_validate"],
        llm_lane["hifi_rank"],
        llm_lane["report"],
    )
    out_path = write_llm_pipeline_comparison(
        comparison,
        tmp_workspace
        / "data"
        / "benchmarks"
        / "llm_pipeline"
        / f"{system_name.lower().replace('-', '_')}_comparison.json",
    )

    assert out_path.exists()
    assert comparison["system"] == system_name
    assert "comparison" in comparison
    metrics = comparison["comparison"]
    assert "screen_pass_rate_delta" in metrics
    assert "validation_pass_rate_delta" in metrics
    assert "novelty_score_mean_delta" in metrics
    assert "top_10_pass_rate_delta" in metrics
    assert "report_synthesize_count_delta" in metrics
    assert "report_high_priority_count_delta" in metrics
    assert "llm_assessed_count_delta" in metrics
