from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from materials_discovery.cli import app


@pytest.mark.integration
def test_real_mode_end_to_end_pipeline_artifacts() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"

    ingest = runner.invoke(app, ["ingest", "--config", str(config_path)])
    assert ingest.exit_code == 0
    ingest_summary = json.loads(ingest.stdout)
    ingest_manifest = Path(ingest_summary["manifest_path"])
    assert ingest_manifest.exists()

    generate = runner.invoke(
        app,
        ["generate", "--config", str(config_path), "--count", "45", "--seed", "1001"],
    )
    assert generate.exit_code == 0
    generate_summary = json.loads(generate.stdout)
    assert Path(generate_summary["manifest_path"]).exists()
    assert Path(generate_summary["calibration_path"]).exists()

    screen = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen.exit_code == 0
    screen_summary = json.loads(screen.stdout)
    assert Path(screen_summary["manifest_path"]).exists()
    assert Path(screen_summary["calibration_path"]).exists()

    validate = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "all"],
    )
    assert validate.exit_code == 0
    validate_summary = json.loads(validate.stdout)
    assert Path(validate_summary["manifest_path"]).exists()
    assert Path(validate_summary["calibration_path"]).exists()

    rank = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert rank.exit_code == 0
    rank_summary = json.loads(rank.stdout)
    assert Path(rank_summary["manifest_path"]).exists()
    assert Path(rank_summary["calibration_path"]).exists()

    active = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert active.exit_code == 0
    active_summary = json.loads(active.stdout)
    assert Path(active_summary["manifest_path"]).exists()
    assert Path(active_summary["feature_store_path"]).exists()
    model_registry_path = Path(active_summary["model_registry_path"])
    assert model_registry_path.exists()

    with model_registry_path.open("r", encoding="utf-8") as handle:
        registry_rows = [json.loads(line) for line in handle if line.strip()]
    assert any(row.get("model_id") == active_summary["model_id"] for row in registry_rows)

    report = runner.invoke(app, ["report", "--config", str(config_path)])
    assert report.exit_code == 0
    report_summary = json.loads(report.stdout)
    assert Path(report_summary["manifest_path"]).exists()

    pipeline_manifest_path = Path(report_summary["pipeline_manifest_path"])
    assert pipeline_manifest_path.exists()
    pipeline_manifest = json.loads(pipeline_manifest_path.read_text(encoding="utf-8"))
    assert pipeline_manifest["stage"] == "pipeline"
    assert "report_json" in pipeline_manifest["output_hashes"]
