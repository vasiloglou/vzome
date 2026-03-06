from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from materials_discovery.cli import app


@pytest.mark.parametrize(
    ("args", "stage", "target"),
    [
        (
            ["hifi-rank", "--config"],
            "hifi-rank",
            "materials_discovery.hifi_digital.rank_candidates.rank_validated_candidates",
        ),
        (
            ["report", "--config"],
            "report",
            "materials_discovery.diffraction.compare_patterns.compile_experiment_report",
        ),
    ],
)
def test_stub_commands_return_3(args: list[str], stage: str, target: str) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    full_args = args.copy()
    if full_args.count("--config") == 1:
        idx = full_args.index("--config")
        full_args.insert(idx + 1, str(config))

    result = runner.invoke(app, full_args)

    assert result.exit_code == 3
    assert f'"stage": "{stage}"' in result.stdout
    assert f'"target": "{target}"' in result.stdout
