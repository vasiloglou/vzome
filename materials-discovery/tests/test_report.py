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


def test_report_emits_benchmark_context_when_ranked_candidates_carry_it() -> None:
    """compile_experiment_report must surface benchmark_context when candidates carry it."""
    from materials_discovery.common.benchmarking import build_benchmark_run_context
    from materials_discovery.common.io import load_yaml
    from materials_discovery.common.schema import CandidateRecord, SystemConfig
    from materials_discovery.diffraction.compare_patterns import compile_experiment_report
    from materials_discovery.diffraction.simulate_powder_xrd import simulate_powder_xrd_patterns
    from materials_discovery.hifi_digital.rank_candidates import rank_validated_candidates

    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))

    # Build a minimal validated candidate list
    raw = {
        "candidate_id": "rpt_ctx_1",
        "system": "Al-Cu-Fe",
        "template_family": "icosahedral_approximant_1_1",
        "cell": {"a": 14.2, "b": 14.2, "c": 14.2, "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
        "sites": [{"label": "S1", "qphi": [[1, 0], [0, 1], [-1, 1]], "species": "Al", "occ": 1.0}],
        "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        "screen": {"energy_proxy_ev_per_atom": -2.9},
        "digital_validation": {
            "status": "passed",
            "committee": ["MACE", "CHGNet", "MatterSim"],
            "uncertainty_ev_per_atom": 0.006,
            "committee_energy_ev_per_atom": {"MACE": -2.91, "CHGNet": -2.90, "MatterSim": -2.89},
            "committee_std_ev_per_atom": 0.006,
            "delta_e_proxy_hull_ev_per_atom": 0.012,
            "proxy_hull_reference_distance": 0.0,
            "proxy_hull_reference_phases": ["i-phase"],
            "phonon_imaginary_modes": 0,
            "phonon_pass": True,
            "md_stability_score": 0.90,
            "md_pass": True,
            "xrd_confidence": 0.91,
            "xrd_pass": True,
            "passed_checks": True,
        },
        "provenance": {"generator_version": "0.1.0"},
    }
    candidate = CandidateRecord.model_validate(raw)

    bm_ctx = build_benchmark_run_context(config).as_dict()
    ranked = rank_validated_candidates(config, [candidate], benchmark_context=bm_ctx)
    xrd_patterns = simulate_powder_xrd_patterns(ranked)
    report = compile_experiment_report(config, ranked, xrd_patterns)

    # Report must carry benchmark_context at top level
    assert "benchmark_context" in report, "report is missing benchmark_context"
    rpt_ctx = report["benchmark_context"]
    assert isinstance(rpt_ctx, dict)
    assert "backend_mode" in rpt_ctx
    assert "source_keys" in rpt_ctx
    assert "lane_id" in rpt_ctx

    # Each entry's evidence block should carry calibration_provenance
    first_entry = report["entries"][0]
    ev = first_entry["evidence"]
    assert "calibration_provenance" in ev
    cal_prov = ev["calibration_provenance"]
    assert isinstance(cal_prov, dict)
    assert "source" in cal_prov
    assert "backend_mode" in cal_prov


def test_benchmark_pack_written_by_report_command() -> None:
    """The report CLI command must write a benchmark_pack.json artifact."""
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _prepare_ranked_inputs(config_path, count=45, seed=999)

    result = runner.invoke(app, ["report", "--config", str(config_path)])
    assert result.exit_code == 0

    config = SystemConfig.model_validate(load_yaml(config_path))
    system_slug = config.system_name.lower().replace("-", "_")
    benchmark_pack_path = workspace / "data" / "reports" / f"{system_slug}_benchmark_pack.json"
    assert benchmark_pack_path.exists(), f"benchmark_pack.json not written: {benchmark_pack_path}"

    bp = json.loads(benchmark_pack_path.read_text(encoding="utf-8"))
    assert bp["schema_version"] == "benchmark-pack/v1"
    assert bp["system"] == config.system_name
    assert "benchmark_context" in bp
    assert "stage_manifest_paths" in bp
    assert "report_metrics" in bp
    report_metrics = bp["report_metrics"]
    assert "report_fingerprint" in report_metrics
    assert "release_gate" in report_metrics


def test_cross_lane_benchmark_context_keys_match() -> None:
    """Al-Cu-Fe baseline vs. real lane: benchmark_context dicts must have identical keys.

    We reuse artifacts already produced by previous pipeline tests where possible
    to avoid running two full fresh pipelines.  This test verifies the *structure*
    of comparable outputs across two lanes for the same system.
    """
    from materials_discovery.common.benchmarking import build_benchmark_run_context
    from materials_discovery.common.io import load_yaml
    from materials_discovery.common.schema import SystemConfig

    workspace = Path(__file__).resolve().parents[1]
    baseline_config = SystemConfig.model_validate(
        load_yaml(workspace / "configs" / "systems" / "al_cu_fe.yaml")
    )
    real_config = SystemConfig.model_validate(
        load_yaml(workspace / "configs" / "systems" / "al_cu_fe_real.yaml")
    )

    baseline_ctx = build_benchmark_run_context(baseline_config).as_dict()
    real_ctx = build_benchmark_run_context(real_config).as_dict()

    # Both lanes must expose the same context keys
    assert set(baseline_ctx.keys()) == set(real_ctx.keys()), (
        f"Cross-lane context key mismatch: baseline={sorted(baseline_ctx)}, "
        f"real={sorted(real_ctx)}"
    )
    # Lane IDs must differ (different backend modes)
    assert baseline_ctx["lane_id"] != real_ctx["lane_id"] or baseline_ctx["backend_mode"] != real_ctx["backend_mode"]


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
