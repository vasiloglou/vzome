from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml


def test_cli_ingest_success(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    fixture = workspace / "data" / "external" / "fixtures" / "hypodx_sample.json"
    out_file = tmp_path / "ingest.jsonl"

    result = runner.invoke(
        app,
        [
            "ingest",
            "--config",
            str(config),
            "--fixture",
            str(fixture),
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()


def test_cli_generate_success(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    out_file = tmp_path / "generated.jsonl"

    result = runner.invoke(
        app,
        [
            "generate",
            "--config",
            str(config),
            "--count",
            "12",
            "--seed",
            "7",
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()


def test_cli_invalid_config_returns_2() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "ingest",
            "--config",
            "does/not/exist.yaml",
        ],
    )

    assert result.exit_code == 2


def test_cli_invalid_backend_mode_returns_2(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    data = load_yaml(base_config)
    data["backend"] = {"mode": "unknown"}
    bad_backend_config = tmp_path / "bad_backend.yaml"
    bad_backend_config.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "ingest",
            "--config",
            str(bad_backend_config),
        ],
    )

    assert result.exit_code == 2
