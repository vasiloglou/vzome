from __future__ import annotations

import json
from pathlib import Path

import yaml
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


def _prepare_ranked_inputs(config_path: Path, count: int, seed: int) -> None:
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
    assert runner.invoke(app, ["hifi-rank", "--config", str(config_path)]).exit_code == 0


def _write_source_registry_real_config(tmp_path: Path) -> Path:
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    data = load_yaml(base_config)
    data["system_name"] = "Al-Cu-Fe-SourceRegistry"
    data["backend"]["ingest_adapter"] = "source_registry_v1"
    data["ingestion"] = {
        "source_key": "hypodx",
        "adapter_key": "fixture_json_v1",
        "snapshot_id": "report_source_registry_v1",
        "use_cached_snapshot": False,
        "artifact_root": str(tmp_path / "source_cache"),
    }

    config_path = tmp_path / "al_cu_fe_report_source_registry.yaml"
    config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return config_path


def test_report_runs_pipeline() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _prepare_ranked_inputs(config_path, count=72, seed=444)

    result = runner.invoke(app, ["report", "--config", str(config_path)])
    assert result.exit_code == 0

    summary = json.loads(result.stdout)
    assert summary["ranked_count"] >= summary["reported_count"]

    report_path = Path(summary["report_path"])
    xrd_path = Path(summary["xrd_patterns_path"])
    calibration_path = Path(summary["calibration_path"])
    assert report_path.exists()
    assert xrd_path.exists()
    assert calibration_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    patterns = _read_jsonl(xrd_path)
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))

    assert report["ranked_count"] == summary["ranked_count"]
    assert report["reported_count"] == summary["reported_count"]
    assert report["report_fingerprint"] == summary["report_fingerprint"]
    assert isinstance(report["entries"], list)
    assert len(report["entries"]) == summary["reported_count"]
    assert isinstance(report["summary"], dict)
    assert isinstance(report["release_gate"], dict)

    candidate_ids = {entry["candidate_id"] for entry in report["entries"]}
    pattern_ids = {row["candidate_id"] for row in patterns}
    assert candidate_ids.issubset(pattern_ids)

    first_entry = report["entries"][0]
    assert isinstance(first_entry["hifi_score"], float)
    assert isinstance(first_entry["stability_probability"], float)
    assert isinstance(first_entry["ood_score"], float)
    assert isinstance(first_entry["novelty_score"], float)
    assert isinstance(first_entry["xrd_confidence"], float)
    assert isinstance(first_entry["xrd_distinctiveness"], float)
    assert first_entry["priority"] in {"high", "medium", "watch"}
    assert first_entry["recommendation"] in {"synthesize", "secondary", "hold"}
    assert isinstance(first_entry["risk_flags"], list)
    assert isinstance(first_entry["composition"], dict)
    assert isinstance(first_entry["evidence"], dict)
    assert isinstance(first_entry["pattern_fingerprint"], str)

    assert calibration["reported_count"] == summary["reported_count"]
    assert calibration["report_fingerprint"] == summary["report_fingerprint"]
    assert isinstance(calibration["release_gate_ready"], bool)
    assert isinstance(calibration["report_digest"], str)


def test_report_is_deterministic() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _prepare_ranked_inputs(config_path, count=68, seed=555)

    first = runner.invoke(app, ["report", "--config", str(config_path)])
    assert first.exit_code == 0
    first_summary = json.loads(first.stdout)

    report_path = Path(first_summary["report_path"])
    calibration_path = Path(first_summary["calibration_path"])
    pipeline_manifest_path = Path(first_summary["pipeline_manifest_path"])
    content_a = report_path.read_text(encoding="utf-8")
    calibration_a = calibration_path.read_text(encoding="utf-8")
    pipeline_manifest_a = json.loads(pipeline_manifest_path.read_text(encoding="utf-8"))

    second = runner.invoke(app, ["report", "--config", str(config_path)])
    assert second.exit_code == 0
    assert first.stdout == second.stdout

    content_b = report_path.read_text(encoding="utf-8")
    calibration_b = calibration_path.read_text(encoding="utf-8")
    pipeline_manifest_b = json.loads(pipeline_manifest_path.read_text(encoding="utf-8"))
    assert content_a == content_b
    assert calibration_a == calibration_b
    assert pipeline_manifest_a["output_hashes"] == pipeline_manifest_b["output_hashes"]


def test_report_runs_after_source_registry_ingest(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = _write_source_registry_real_config(tmp_path)
    fixture_path = workspace / "data" / "external" / "fixtures" / "hypodx_sample.json"

    ingest = runner.invoke(
        app,
        ["ingest", "--config", str(config_path), "--fixture", str(fixture_path)],
    )
    assert ingest.exit_code == 0

    _prepare_ranked_inputs(config_path, count=40, seed=888)

    result = runner.invoke(app, ["report", "--config", str(config_path)])
    assert result.exit_code == 0

    summary = json.loads(result.stdout)
    manifest = json.loads(Path(summary["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["stage"] == "report"
    assert "report_json" in manifest["output_hashes"]
