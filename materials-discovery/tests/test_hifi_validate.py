from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import SystemConfig
from materials_discovery.generator.candidate_factory import generate_candidates


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _prepare_screened_batch(config_path: Path, count: int, seed: int) -> tuple[SystemConfig, Path]:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = SystemConfig.model_validate(load_yaml(config_path))

    candidates_path = (
        workspace / "data" / "candidates" / f"{_system_slug(config.system_name)}_candidates.jsonl"
    )
    screened_path = (
        workspace / "data" / "screened" / f"{_system_slug(config.system_name)}_screened.jsonl"
    )

    generate_candidates(config, candidates_path, count=count, seed=seed)
    screen_result = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen_result.exit_code == 0

    return config, screened_path


def test_hifi_validate_runs_m4_pipeline() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    config, screened_path = _prepare_screened_batch(config_path, count=60, seed=404)
    screened_rows = _read_jsonl(screened_path)

    result = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "all"],
    )

    assert result.exit_code == 0

    summary = json.loads(result.stdout)
    assert summary["batch"] == "all"
    assert summary["input_count"] == len(screened_rows)
    assert summary["validated_count"] == len(screened_rows)

    output_path = Path(summary["output_path"])
    assert output_path.exists()

    validated_rows = _read_jsonl(output_path)
    assert len(validated_rows) == summary["validated_count"]

    passed_count = 0
    for row in validated_rows:
        validation = row["digital_validation"]
        assert isinstance(validation, dict)
        assert validation["batch"] == "all"

        committee = validation["committee_energy_ev_per_atom"]
        assert isinstance(committee, dict)
        assert set(committee.keys()) == {"MACE", "CHGNet", "MatterSim"}

        assert isinstance(validation["uncertainty_ev_per_atom"], float)
        assert isinstance(validation["committee_std_ev_per_atom"], float)
        assert isinstance(validation["delta_e_proxy_hull_ev_per_atom"], float)
        assert isinstance(validation["phonon_imaginary_modes"], int)
        assert isinstance(validation["phonon_pass"], bool)
        assert isinstance(validation["md_stability_score"], float)
        assert isinstance(validation["md_pass"], bool)
        assert isinstance(validation["xrd_confidence"], float)
        assert isinstance(validation["xrd_pass"], bool)
        assert isinstance(validation["passed_checks"], bool)
        assert validation["status"] in {"passed", "failed"}

        if validation["passed_checks"]:
            passed_count += 1

    assert passed_count == summary["passed_count"]
    assert output_path.name == f"{_system_slug(config.system_name)}_all_validated.jsonl"


def test_hifi_validate_is_deterministic_for_fixed_inputs() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _, _ = _prepare_screened_batch(config_path, count=55, seed=909)

    first = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "top3"],
    )
    assert first.exit_code == 0
    first_summary = json.loads(first.stdout)
    output_path = Path(first_summary["output_path"])
    assert output_path.exists()
    content_a = output_path.read_text(encoding="utf-8")

    second = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "top3"],
    )

    assert second.exit_code == 0
    assert first.stdout == second.stdout

    content_b = output_path.read_text(encoding="utf-8")
    assert content_a == content_b
