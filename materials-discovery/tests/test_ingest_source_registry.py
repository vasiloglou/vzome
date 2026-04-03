from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def _materials_project_rows() -> list[dict[str, object]]:
    return [
        {
            "material_id": "mp-i-phase",
            "formula_pretty": "Al7Cu2Fe",
            "chemsys": "Al-Cu-Fe",
            "composition_reduced": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            "symmetry": {"symbol": "Pm-3"},
            "structure": {"site_count": 36},
        },
        {
            "material_id": "mp-beta",
            "formula_pretty": "Al16Cu3Fe1",
            "chemsys": "Al-Cu-Fe",
            "composition_reduced": {"Al": 0.8, "Cu": 0.15, "Fe": 0.05},
            "symmetry": {"symbol": "Im-3"},
            "structure": {"site_count": 24},
        },
        {
            "material_id": "mp-other",
            "formula_pretty": "ScZn2",
            "chemsys": "Sc-Zn",
            "composition_reduced": {"Sc": 0.3333333, "Zn": 0.6666667},
            "symmetry": {"symbol": "Im-3"},
            "structure": {"site_count": 12},
        },
    ]


def _write_source_registry_config(tmp_path: Path, *, include_ingestion: bool = True) -> Path:
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    data = load_yaml(base_config)
    data["backend"] = {
        "mode": "real",
        "ingest_adapter": "source_registry_v1",
    }
    if include_ingestion:
        data["ingestion"] = {
            "source_key": "materials_project",
            "adapter_key": "direct_api_v1",
            "snapshot_id": "mp_fixture_snapshot_v1",
            "use_cached_snapshot": True,
            "artifact_root": str(tmp_path / "source_cache"),
            "query": {"inline_rows": _materials_project_rows()},
        }

    config_path = tmp_path / "source_registry.yaml"
    config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return config_path


def test_source_registry_ingest_success_writes_processed_output_and_manifest_lineage(
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    config_path = _write_source_registry_config(tmp_path)
    out_path = tmp_path / "source_registry_reference_phases.jsonl"

    result = runner.invoke(
        app,
        ["ingest", "--config", str(config_path), "--out", str(out_path)],
    )

    assert result.exit_code == 0
    assert out_path.exists()

    summary = json.loads(result.stdout)
    assert summary["backend_adapter"] == "source_registry_v1"
    assert summary["raw_count"] == 3
    assert summary["matched_count"] == 2
    assert summary["deduped_count"] == 2

    rows = _read_jsonl(out_path)
    assert len(rows) == 2
    assert rows[0]["metadata"]["source_key"] == "materials_project"
    assert rows[0]["metadata"]["record_kind"] in {"material_entry", "structure"}

    manifest_path = Path(summary["manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["stage"] == "ingest"
    assert manifest["backend_mode"] == "real"
    assert manifest["source_lineage"]["source_key"] == "materials_project"
    assert manifest["source_lineage"]["snapshot_id"] == "mp_fixture_snapshot_v1"
    assert "canonical_records_path" in manifest["source_lineage"]
    assert manifest["source_lineage"]["projection_summary"]["deduped_count"] == 2


def test_source_registry_ingest_reuses_cached_snapshot_when_enabled(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    config_path = _write_source_registry_config(tmp_path)
    first_out = tmp_path / "first.jsonl"
    second_out = tmp_path / "second.jsonl"

    first = runner.invoke(app, ["ingest", "--config", str(config_path), "--out", str(first_out)])
    assert first.exit_code == 0

    def _unexpected_stage(*args, **kwargs):
        raise AssertionError("cache reuse should avoid restaging source snapshots")

    monkeypatch.setattr("materials_discovery.cli.stage_registered_source_snapshot", _unexpected_stage)
    second = runner.invoke(
        app,
        ["ingest", "--config", str(config_path), "--out", str(second_out)],
    )

    assert second.exit_code == 0
    assert second_out.exists()
    second_summary = json.loads(second.stdout)
    assert second_summary["deduped_count"] == 2


def test_source_registry_ingest_requires_ingestion_block(tmp_path: Path) -> None:
    runner = CliRunner()
    config_path = _write_source_registry_config(tmp_path, include_ingestion=False)

    result = runner.invoke(app, ["ingest", "--config", str(config_path)])

    assert result.exit_code == 2
    assert "source_registry_v1 ingest requires an ingestion block" in result.stderr
