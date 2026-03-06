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


def _prepare_validated_inputs(config_path: Path, count: int, seed: int) -> Path:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = SystemConfig.model_validate(load_yaml(config_path))

    candidates_path = (
        workspace / "data" / "candidates" / f"{_system_slug(config.system_name)}_candidates.jsonl"
    )
    generate_candidates(config, candidates_path, count=count, seed=seed)

    assert runner.invoke(app, ["screen", "--config", str(config_path)]).exit_code == 0
    assert (
        runner.invoke(
            app,
            ["hifi-validate", "--config", str(config_path), "--batch", "all"],
        ).exit_code
        == 0
    )

    return candidates_path


def test_hifi_rank_runs_pipeline() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _ = _prepare_validated_inputs(config_path, count=70, seed=222)

    result = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert result.exit_code == 0

    summary = json.loads(result.stdout)
    assert summary["ranked_count"] == summary["input_count"]

    output_path = Path(summary["output_path"])
    assert output_path.exists()

    ranked_rows = _read_jsonl(output_path)
    assert len(ranked_rows) == summary["ranked_count"]

    ranks: list[int] = []
    scores: list[float] = []
    passed_count = 0

    for row in ranked_rows:
        provenance = row["provenance"]
        assert isinstance(provenance, dict)
        hifi_rank = provenance["hifi_rank"]
        assert isinstance(hifi_rank, dict)

        rank = hifi_rank["rank"]
        score = hifi_rank["score"]
        assert isinstance(rank, int)
        assert isinstance(score, float)

        ranks.append(rank)
        scores.append(score)

        validation = row["digital_validation"]
        assert isinstance(validation, dict)
        assert validation["status"] == "ranked"
        if validation["passed_checks"]:
            passed_count += 1

    assert ranks == list(range(1, len(ranks) + 1))
    assert scores == sorted(scores, reverse=True)
    assert passed_count == summary["passed_count"]


def test_hifi_rank_is_deterministic() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _ = _prepare_validated_inputs(config_path, count=65, seed=333)

    first = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert first.exit_code == 0
    first_summary = json.loads(first.stdout)

    output_path = Path(first_summary["output_path"])
    content_a = output_path.read_text(encoding="utf-8")

    second = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert second.exit_code == 0
    assert first.stdout == second.stdout

    content_b = output_path.read_text(encoding="utf-8")
    assert content_a == content_b
