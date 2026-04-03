"""Tests for lake comparison engine (compare.py).

Tests are organized in TDD order: the compare module behaviors are verified
from data fixtures built inline without touching disk artifacts.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers to build fixture files
# ---------------------------------------------------------------------------

REPORT_FIXTURE_ENTRIES = [
    {
        "candidate_id": "cand_001",
        "hifi_score": 0.89,
        "stability_probability": 0.92,
        "ood_score": 0.18,
        "xrd_confidence": 0.85,
        "xrd_distinctiveness": 0.52,
        "evidence": {
            "delta_e_proxy_hull_ev_per_atom": 0.02,
            "uncertainty_ev_per_atom": 0.01,
            "md_stability_score": 0.88,
        },
    },
    {
        "candidate_id": "cand_002",
        "hifi_score": 0.75,
        "stability_probability": 0.80,
        "ood_score": 0.25,
        "xrd_confidence": 0.70,
        "xrd_distinctiveness": 0.40,
        "evidence": {
            "delta_e_proxy_hull_ev_per_atom": 0.05,
            "uncertainty_ev_per_atom": 0.03,
            "md_stability_score": 0.72,
        },
    },
]

REPORT_FIXTURE_A = {
    "system": "Al-Cu-Fe",
    "report_version": "0.2.0",
    "summary": {
        "high_priority_count": 3,
        "synthesize_count": 2,
        "xrd_confidence_mean": 0.775,
        "xrd_distinctiveness_mean": 0.46,
        "stability_probability_mean": 0.86,
        "max_ood_score": 0.25,
    },
    "release_gate": {
        "enough_synthesis_candidates": True,
        "top_xrd_confidence_gate": True,
        "top_distinctiveness_gate": True,
        "top_stability_gate": True,
        "top_ood_gate": True,
        "ready_for_experimental_pack": True,
    },
    "entries": REPORT_FIXTURE_ENTRIES,
}

REPORT_FIXTURE_B = {
    "system": "Sc-Zn",
    "report_version": "0.2.0",
    "summary": {
        "high_priority_count": 2,
        "synthesize_count": 1,
        "xrd_confidence_mean": 0.60,
        "xrd_distinctiveness_mean": 0.35,
        "stability_probability_mean": 0.70,
        "max_ood_score": 0.40,
    },
    "release_gate": {
        "enough_synthesis_candidates": True,
        "top_xrd_confidence_gate": False,
        "top_distinctiveness_gate": True,
        "top_stability_gate": False,
        "top_ood_gate": True,
        "ready_for_experimental_pack": False,
    },
    "entries": [
        {
            "candidate_id": "cand_sc_001",
            "hifi_score": 0.62,
            "stability_probability": 0.68,
            "ood_score": 0.35,
            "xrd_confidence": 0.58,
            "xrd_distinctiveness": 0.30,
            "evidence": {
                "delta_e_proxy_hull_ev_per_atom": 0.09,
                "uncertainty_ev_per_atom": 0.04,
                "md_stability_score": 0.65,
            },
        },
    ],
}


def _write_pack(
    tmp_path: Path,
    system: str,
    report_data: dict,
    override_gate: dict | None = None,
) -> Path:
    """Write a benchmark-pack JSON with an embedded report reference."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    report_path = tmp_path / f"{system.lower().replace('-', '_')}_report.json"
    report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

    gate = override_gate or report_data["release_gate"]
    summary = report_data["summary"]

    pack = {
        "schema_version": "benchmark-pack/v1",
        "system": system,
        "backend_mode": "real",
        "benchmark_context": {
            "reference_pack_id": f"{system.lower().replace('-', '_')}_pack_v1",
            "reference_pack_fingerprint": "abc123",
            "source_keys": ["hypod_x", "materials_project"],
            "benchmark_corpus": f"data/benchmarks/{system.lower().replace('-', '_')}_benchmark.json",
            "backend_mode": "real",
            "lane_id": f"{system.lower().replace('-', '_')}_pack_v1:real",
        },
        "stage_manifest_paths": {
            "ingest_manifest": "data/manifests/ingest_xxx.json",
            "report": str(report_path),
            "calibration": "data/calibration/calibration.json",
        },
        "report_metrics": {
            "release_gate": gate,
            "summary": summary,
        },
    }
    pack_path = tmp_path / f"{system.lower().replace('-', '_')}_pack.json"
    pack_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return pack_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestLaneSnapshot:
    def test_loads_from_benchmark_pack(self, tmp_path: Path) -> None:
        """Test 1: LaneSnapshot loads from benchmark-pack JSON and dereferences report."""
        pack_path = _write_pack(tmp_path, "Al-Cu-Fe", REPORT_FIXTURE_A)

        from materials_discovery.lake.compare import LaneSnapshot

        snap = LaneSnapshot.from_benchmark_pack(pack_path, workspace=tmp_path)

        assert snap.system == "Al-Cu-Fe"
        assert snap.lane_id == "al_cu_fe_pack_v1:real"
        assert snap.backend_mode == "real"
        assert "hypod_x" in snap.source_keys
        assert snap.reference_pack_id == "al_cu_fe_pack_v1"
        assert snap.report_path is not None

    def test_computes_metric_distributions(self, tmp_path: Path) -> None:
        """Test 2: LaneSnapshot computes aggregate metric distributions from report entries."""
        pack_path = _write_pack(tmp_path, "Al-Cu-Fe", REPORT_FIXTURE_A)

        from materials_discovery.lake.compare import LaneSnapshot, MetricDistribution

        snap = LaneSnapshot.from_benchmark_pack(pack_path, workspace=tmp_path)

        assert snap.metric_distributions, "Expected non-empty metric_distributions"

        # hifi_score: [0.89, 0.75] -> mean=0.82, min=0.75, max=0.89
        dist = snap.metric_distributions["hifi_score"]
        assert isinstance(dist, MetricDistribution)
        assert abs(dist.mean - statistics.mean([0.89, 0.75])) < 1e-6
        assert dist.min == 0.75
        assert dist.max == 0.89
        assert dist.count == 2

        # delta_e from evidence
        assert "delta_e_proxy_hull_ev_per_atom" in snap.metric_distributions


class TestComparisonResult:
    def test_gate_deltas(self, tmp_path: Path) -> None:
        """Test 3: compare_benchmark_packs produces gate deltas with correct status."""
        pack_a = _write_pack(tmp_path / "a", "Al-Cu-Fe", REPORT_FIXTURE_A)
        pack_b = _write_pack(tmp_path / "b", "Sc-Zn", REPORT_FIXTURE_B)

        from materials_discovery.lake.compare import compare_benchmark_packs

        result = compare_benchmark_packs(pack_a, pack_b)

        gate_map = {gd.gate_name: gd for gd in result.gate_deltas}

        # top_xrd_confidence_gate: A=True, B=False -> regression
        assert gate_map["top_xrd_confidence_gate"].status == "regression"
        assert gate_map["top_xrd_confidence_gate"].lane_a is True
        assert gate_map["top_xrd_confidence_gate"].lane_b is False

        # enough_synthesis_candidates: both True -> both_pass
        assert gate_map["enough_synthesis_candidates"].status == "both_pass"

        # top_stability_gate: A=True, B=False -> regression
        assert gate_map["top_stability_gate"].status == "regression"

    def test_metric_distribution_diffs(self, tmp_path: Path) -> None:
        """Test 4: compare_benchmark_packs produces metric distribution diffs."""
        pack_a = _write_pack(tmp_path / "a", "Al-Cu-Fe", REPORT_FIXTURE_A)
        pack_b = _write_pack(tmp_path / "b", "Sc-Zn", REPORT_FIXTURE_B)

        from materials_discovery.lake.compare import compare_benchmark_packs

        result = compare_benchmark_packs(pack_a, pack_b)

        metric_map = {md.metric_name: md for md in result.metric_deltas}
        assert "hifi_score" in metric_map

        hifi_delta = metric_map["hifi_score"]
        assert hifi_delta.lane_a is not None
        assert hifi_delta.lane_b is not None
        assert hifi_delta.delta_mean is not None
        # lane_b (Sc-Zn, single entry 0.62) < lane_a (Al-Cu-Fe, mean 0.82)
        assert hifi_delta.delta_mean < 0

    def test_format_comparison_table(self, tmp_path: Path) -> None:
        """Test 5: format_comparison_table produces readable multi-line output."""
        pack_a = _write_pack(tmp_path / "a", "Al-Cu-Fe", REPORT_FIXTURE_A)
        pack_b = _write_pack(tmp_path / "b", "Sc-Zn", REPORT_FIXTURE_B)

        from materials_discovery.lake.compare import compare_benchmark_packs, format_comparison_table

        result = compare_benchmark_packs(pack_a, pack_b)
        table = format_comparison_table(result)

        assert "Al-Cu-Fe" in table
        assert "Sc-Zn" in table
        assert "gate" in table.lower() or "Gate" in table
        assert len(table.splitlines()) > 5

    def test_comparison_result_serializes_to_json(self, tmp_path: Path) -> None:
        """Test 6: ComparisonResult serializes to JSON (D-06 dual-format requirement)."""
        pack_a = _write_pack(tmp_path / "a", "Al-Cu-Fe", REPORT_FIXTURE_A)
        pack_b = _write_pack(tmp_path / "b", "Sc-Zn", REPORT_FIXTURE_B)

        from materials_discovery.lake.compare import compare_benchmark_packs

        result = compare_benchmark_packs(pack_a, pack_b)
        data = json.loads(result.model_dump_json())

        assert data["schema_version"] == "comparison/v1"
        assert "lane_a" in data
        assert "lane_b" in data
        assert "gate_deltas" in data
        assert "metric_deltas" in data
        assert "generated_at_utc" in data

    def test_missing_report_falls_back_to_pack_metrics(self, tmp_path: Path) -> None:
        """Test 7: Comparison handles missing report paths gracefully, uses pack fallback."""
        # Build a pack where the report path points to a non-existent file
        report_data = REPORT_FIXTURE_A.copy()
        pack = {
            "schema_version": "benchmark-pack/v1",
            "system": "Al-Cu-Fe",
            "backend_mode": "real",
            "benchmark_context": {
                "reference_pack_id": "al_cu_fe_pack_v1",
                "reference_pack_fingerprint": "abc123",
                "source_keys": ["hypod_x"],
                "benchmark_corpus": "data/benchmarks/al_cu_fe_benchmark.json",
                "backend_mode": "real",
                "lane_id": "al_cu_fe_pack_v1:real",
            },
            "stage_manifest_paths": {
                "report": str(tmp_path / "nonexistent_report.json"),
            },
            "report_metrics": {
                "release_gate": report_data["release_gate"],
                "summary": report_data["summary"],
            },
        }
        pack_path = tmp_path / "pack_no_report.json"
        pack_path.write_text(json.dumps(pack), encoding="utf-8")

        from materials_discovery.lake.compare import LaneSnapshot

        # Should not raise; should fall back gracefully
        snap = LaneSnapshot.from_benchmark_pack(pack_path, workspace=tmp_path)

        assert snap.system == "Al-Cu-Fe"
        # Distributions will be empty since report was missing
        assert isinstance(snap.metric_distributions, dict)
        # Gate results come from pack's report_metrics
        assert snap.gate_results.get("enough_synthesis_candidates") is True


class TestWriteComparison:
    def test_write_comparison_creates_file(self, tmp_path: Path) -> None:
        """Test write_comparison writes JSON artifact to output_dir."""
        pack_a = _write_pack(tmp_path / "a", "Al-Cu-Fe", REPORT_FIXTURE_A)
        pack_b = _write_pack(tmp_path / "b", "Sc-Zn", REPORT_FIXTURE_B)

        from materials_discovery.lake.compare import compare_benchmark_packs, write_comparison

        result = compare_benchmark_packs(pack_a, pack_b)
        out_dir = tmp_path / "comparisons"
        out_path = write_comparison(result, output_dir=out_dir)

        assert out_path.exists()
        data = json.loads(out_path.read_text())
        assert data["schema_version"] == "comparison/v1"


class TestCLIIntegration:
    def test_cli_compare_command(self, tmp_path: Path) -> None:
        """CLI integration test: mdisc lake compare with two fixture pack paths."""
        pack_a = _write_pack(tmp_path / "a", "Al-Cu-Fe", REPORT_FIXTURE_A)
        pack_b = _write_pack(tmp_path / "b", "Sc-Zn", REPORT_FIXTURE_B)

        from typer.testing import CliRunner
        from materials_discovery.cli import app

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["lake", "compare", str(pack_a), str(pack_b), "--output-dir", str(tmp_path / "cmp_out")],
        )

        assert result.exit_code == 0, f"CLI failed with output:\n{result.output}"
        assert "Al-Cu-Fe" in result.output
        assert "Sc-Zn" in result.output

    def test_cli_compare_json_only(self, tmp_path: Path) -> None:
        """CLI: --json-only suppresses table output, still writes JSON file."""
        pack_a = _write_pack(tmp_path / "a", "Al-Cu-Fe", REPORT_FIXTURE_A)
        pack_b = _write_pack(tmp_path / "b", "Sc-Zn", REPORT_FIXTURE_B)

        from typer.testing import CliRunner
        from materials_discovery.cli import app

        runner = CliRunner()
        out_dir = tmp_path / "json_only_out"
        result = runner.invoke(
            app,
            ["lake", "compare", str(pack_a), str(pack_b), "--output-dir", str(out_dir), "--json-only"],
        )

        assert result.exit_code == 0, f"CLI failed with output:\n{result.output}"
        # JSON file should still be written
        written = list(out_dir.glob("*.json"))
        assert written, "Expected a JSON comparison file to be written"
