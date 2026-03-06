from __future__ import annotations

import json
from pathlib import Path

import pytest
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


@pytest.mark.integration
def test_ingest_real_backend_with_pinned_snapshot(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]

    base_config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    snapshot_path = workspace / "data" / "external" / "pinned" / "hypodx_pinned_2026_03_09.json"
    out_path = tmp_path / "al_cu_fe_real_reference_phases.jsonl"

    config_data = load_yaml(base_config_path)
    config_data["backend"] = {
        "mode": "real",
        "ingest_adapter": "hypodx_pinned_v2026_03_09",
        "pinned_snapshot": str(snapshot_path),
        "versions": {"hypodx_snapshot": "2026-03-09"},
    }

    config_path = tmp_path / "al_cu_fe_real.yaml"
    config_path.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")

    result = runner.invoke(
        app,
        ["ingest", "--config", str(config_path), "--out", str(out_path)],
    )

    assert result.exit_code == 0
    assert out_path.exists()

    summary = json.loads(result.stdout)
    assert summary["backend_mode"] == "real"
    assert summary["backend_adapter"] == "hypodx_pinned_v2026_03_09"
    assert summary["invalid_count"] == 1
    assert summary["deduped_count"] == 3

    qa_metrics = summary["qa_metrics"]
    assert isinstance(qa_metrics, dict)
    assert qa_metrics["passed"] is True

    manifest_path = Path(summary["manifest_path"])
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["stage"] == "ingest"
    assert manifest["backend_mode"] == "real"
    assert "processed_jsonl" in manifest["output_hashes"]

    rows = _read_jsonl(out_path)
    assert len(rows) == summary["deduped_count"]
