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


def _prepare_validated_inputs(
    config_path: Path, count: int, seed: int
) -> tuple[SystemConfig, Path]:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = SystemConfig.model_validate(load_yaml(config_path))

    candidates_path = (
        workspace / "data" / "candidates" / f"{_system_slug(config.system_name)}_candidates.jsonl"
    )
    generate_candidates(config, candidates_path, count=count, seed=seed)

    screen_result = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen_result.exit_code == 0

    validate_result = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "all"],
    )
    assert validate_result.exit_code == 0

    summary = json.loads(validate_result.stdout)
    validated_path = Path(summary["output_path"])
    return config, validated_path


def test_active_learn_command_runs_m5_pipeline() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    config, validated_path = _prepare_validated_inputs(config_path, count=80, seed=515)
    validated_rows = _read_jsonl(validated_path)

    result = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert result.exit_code == 0

    summary = json.loads(result.stdout)
    assert summary["validated_count"] == len({row["candidate_id"] for row in validated_rows})
    assert summary["selected_count"] > 0
    assert 0.0 <= summary["pass_rate"] <= 1.0

    surrogate_path = Path(summary["surrogate_path"])
    batch_path = Path(summary["batch_path"])
    assert surrogate_path.exists()
    assert batch_path.exists()

    surrogate = json.loads(surrogate_path.read_text(encoding="utf-8"))
    assert surrogate["system"] == config.system_name
    assert surrogate["training_rows"] == summary["validated_count"]

    next_batch = _read_jsonl(batch_path)
    assert len(next_batch) == summary["selected_count"]

    validated_ids = {row["candidate_id"] for row in validated_rows}
    selected_ids = {row["candidate_id"] for row in next_batch}
    assert validated_ids.isdisjoint(selected_ids)

    for row in next_batch:
        provenance = row["provenance"]
        assert isinstance(provenance, dict)
        active = provenance["active_learning"]
        assert isinstance(active, dict)
        assert active["system"] == config.system_name
        assert isinstance(active["predicted_success"], float)
        assert isinstance(active["uncertainty_proxy"], float)
        assert isinstance(active["acquisition_score"], float)


def test_active_learn_is_deterministic_for_fixed_inputs() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _, _ = _prepare_validated_inputs(config_path, count=75, seed=818)

    first = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert first.exit_code == 0
    first_summary = json.loads(first.stdout)

    batch_path = Path(first_summary["batch_path"])
    assert batch_path.exists()
    content_a = batch_path.read_text(encoding="utf-8")

    second = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert second.exit_code == 0
    assert first.stdout == second.stdout

    content_b = batch_path.read_text(encoding="utf-8")
    assert content_a == content_b
