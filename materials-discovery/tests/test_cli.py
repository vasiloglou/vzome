from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app


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
