from __future__ import annotations

import json
from pathlib import Path

from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data.ingest_hypodx import ingest_fixture


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def test_ingest_dedupes_and_writes_sorted_output(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    fixture_path = workspace / "data" / "external" / "fixtures" / "hypodx_sample.json"

    config = SystemConfig.model_validate(load_yaml(config_path))
    out_path = tmp_path / "al_cu_fe_reference_phases.jsonl"

    summary = ingest_fixture(config, fixture_path, out_path)
    rows = _read_jsonl(out_path)

    assert summary.raw_count == 5
    assert summary.matched_count == 3
    assert summary.deduped_count == 2
    assert len(rows) == 2
    assert [row["phase_name"] for row in rows] == ["beta", "i-phase"]


def test_ingest_is_deterministic(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    fixture_path = workspace / "data" / "external" / "fixtures" / "hypodx_sample.json"

    config = SystemConfig.model_validate(load_yaml(config_path))

    out_a = tmp_path / "run_a.jsonl"
    out_b = tmp_path / "run_b.jsonl"

    ingest_fixture(config, fixture_path, out_a)
    ingest_fixture(config, fixture_path, out_b)

    assert out_a.read_text(encoding="utf-8") == out_b.read_text(encoding="utf-8")
