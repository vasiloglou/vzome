from __future__ import annotations

import json
from pathlib import Path

from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import SystemConfig
from materials_discovery.generator.candidate_factory import generate_candidates


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def _iter_qphi_pairs(candidate: dict[str, object]) -> list[list[int]]:
    pairs: list[list[int]] = []
    sites = candidate["sites"]
    assert isinstance(sites, list)
    for site in sites:
        assert isinstance(site, dict)
        qphi = site["qphi"]
        assert isinstance(qphi, list)
        for pair in qphi:
            assert isinstance(pair, list)
            pairs.append(pair)
    return pairs


def test_generate_count_unique_ids_and_bounds(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))

    out_path = tmp_path / "candidates.jsonl"
    summary = generate_candidates(config, out_path, count=25, seed=99)
    rows = _read_jsonl(out_path)

    assert summary.generated_count == 25
    assert len(rows) == 25

    ids = [row["candidate_id"] for row in rows]
    assert len(ids) == len(set(ids))
    assert ids[0] == "md_000001"
    assert ids[-1] == "md_000025"

    for row in rows:
        for pair in _iter_qphi_pairs(row):
            assert config.coeff_bounds.min <= pair[0] <= config.coeff_bounds.max
            assert config.coeff_bounds.min <= pair[1] <= config.coeff_bounds.max


def test_generate_is_deterministic_for_fixed_seed(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))

    out_a = tmp_path / "run_a.jsonl"
    out_b = tmp_path / "run_b.jsonl"

    generate_candidates(config, out_a, count=15, seed=123)
    generate_candidates(config, out_b, count=15, seed=123)

    assert out_a.read_text(encoding="utf-8") == out_b.read_text(encoding="utf-8")
