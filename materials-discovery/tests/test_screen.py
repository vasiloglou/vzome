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


def test_screen_command_runs_m3_pipeline() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    config = SystemConfig.model_validate(load_yaml(config_path))
    input_path = (
        workspace
        / "data"
        / "candidates"
        / f"{config.system_name.lower().replace('-', '_')}_candidates.jsonl"
    )
    output_path = (
        workspace
        / "data"
        / "screened"
        / f"{config.system_name.lower().replace('-', '_')}_screened.jsonl"
    )

    generate_candidates(config, input_path, count=30, seed=123)

    result = runner.invoke(app, ["screen", "--config", str(config_path)])

    assert result.exit_code == 0

    summary = json.loads(result.stdout)
    assert summary["input_count"] == 30
    assert summary["relaxed_count"] == 30
    assert summary["passed_count"] >= summary["shortlisted_count"]

    assert output_path.exists()
    shortlisted = _read_jsonl(output_path)
    assert len(shortlisted) == summary["shortlisted_count"]

    ranks = []
    for row in shortlisted:
        screen = row["screen"]
        assert isinstance(screen, dict)
        assert screen["passed_thresholds"] is True
        rank = screen["shortlist_rank"]
        assert isinstance(rank, int)
        ranks.append(rank)

    assert ranks == list(range(1, len(ranks) + 1))
