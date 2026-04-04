from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import SystemConfig


@pytest.mark.integration
@pytest.mark.parametrize(
    ("config_name", "expect_exec_cache"),
    [
        ("al_cu_fe_real.yaml", False),
        ("al_cu_fe_exec.yaml", True),
    ],
)
def test_real_mode_end_to_end_pipeline_artifacts(
    config_name: str,
    expect_exec_cache: bool,
) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / config_name

    ingest = runner.invoke(app, ["ingest", "--config", str(config_path)])
    assert ingest.exit_code == 0
    ingest_summary = json.loads(ingest.stdout)
    ingest_manifest = Path(ingest_summary["manifest_path"])
    assert ingest_manifest.exists()

    generate = runner.invoke(
        app,
        ["generate", "--config", str(config_path), "--count", "45", "--seed", "1001"],
    )
    assert generate.exit_code == 0
    generate_summary = json.loads(generate.stdout)
    assert Path(generate_summary["manifest_path"]).exists()
    assert Path(generate_summary["calibration_path"]).exists()

    screen = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen.exit_code == 0
    screen_summary = json.loads(screen.stdout)
    assert Path(screen_summary["manifest_path"]).exists()
    assert Path(screen_summary["calibration_path"]).exists()

    validate = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "all"],
    )
    assert validate.exit_code == 0
    validate_summary = json.loads(validate.stdout)
    assert Path(validate_summary["manifest_path"]).exists()
    assert Path(validate_summary["calibration_path"]).exists()

    rank = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert rank.exit_code == 0
    rank_summary = json.loads(rank.stdout)
    assert Path(rank_summary["manifest_path"]).exists()
    assert Path(rank_summary["calibration_path"]).exists()

    active = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert active.exit_code == 0
    active_summary = json.loads(active.stdout)
    assert Path(active_summary["manifest_path"]).exists()
    assert Path(active_summary["feature_store_path"]).exists()
    model_registry_path = Path(active_summary["model_registry_path"])
    assert model_registry_path.exists()

    with model_registry_path.open("r", encoding="utf-8") as handle:
        registry_rows = [json.loads(line) for line in handle if line.strip()]
    assert any(row.get("model_id") == active_summary["model_id"] for row in registry_rows)

    report = runner.invoke(app, ["report", "--config", str(config_path)])
    assert report.exit_code == 0
    report_summary = json.loads(report.stdout)
    assert Path(report_summary["manifest_path"]).exists()
    assert Path(report_summary["calibration_path"]).exists()

    pipeline_manifest_path = Path(report_summary["pipeline_manifest_path"])
    assert pipeline_manifest_path.exists()
    pipeline_manifest = json.loads(pipeline_manifest_path.read_text(encoding="utf-8"))
    assert pipeline_manifest["stage"] == "pipeline"
    assert "report_json" in pipeline_manifest["output_hashes"]

    if expect_exec_cache:
        cache_root = workspace / "data" / "execution_cache" / "al_cu_fe_exec"
        assert (cache_root / "committee").exists()
        assert (cache_root / "phonon").exists()
        assert (cache_root / "md").exists()
        assert (cache_root / "xrd").exists()


def _write_source_registry_real_config(tmp_path: Path) -> Path:
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    data = load_yaml(base_config)
    data["system_name"] = "Al-Cu-Fe-SourceRegistry"
    data["backend"]["ingest_adapter"] = "source_registry_v1"
    data["ingestion"] = {
        "source_key": "hypodx",
        "adapter_key": "fixture_json_v1",
        "snapshot_id": "hypodx_source_registry_real_v1",
        "use_cached_snapshot": False,
        "artifact_root": str(tmp_path / "source_cache"),
    }

    config_path = tmp_path / "al_cu_fe_source_registry_real.yaml"
    config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return config_path


def _write_llm_campaign_spec(tmp_path: Path, config_path: Path) -> Path:
    config = SystemConfig.model_validate(load_yaml(config_path))
    spec_path = tmp_path / "campaign_spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "schema_version": "llm-campaign-spec/v1",
                "campaign_id": "campaign-001",
                "proposal_id": "proposal-001",
                "approval_id": "approval-001",
                "system": "Al-Cu-Fe",
                "created_at_utc": "2026-04-04T16:00:00Z",
                "actions": [
                    {
                        "action_id": "proposal-001_action_01",
                        "family": "prompt_conditioning",
                        "title": "Tighten prompt validity conditioning",
                        "rationale": "Parse reliability is below target.",
                        "priority": "high",
                        "evidence_metrics": ["parse_success_rate"],
                        "preferred_model_lane": "general_purpose",
                        "prompt_conditioning": {
                            "instruction_delta": "Prefer parser-safe symmetry annotations.",
                            "conditioning_strategy": "increase_exact_system_examples",
                            "target_example_family": "acceptance_pack_exact_matches",
                            "preferred_max_conditioning_examples": 4,
                        },
                    }
                ],
                "launch_baseline": {
                    "system_config_path": str(config_path),
                    "system_config_hash": config_sha256(config),
                    "system": "Al-Cu-Fe",
                    "template_family": "icosahedral_approximant_1_1",
                    "default_count": 2,
                    "composition_bounds": {
                        "Al": {"min": 0.6, "max": 0.8},
                        "Cu": {"min": 0.1, "max": 0.25},
                        "Fe": {"min": 0.05, "max": 0.2},
                    },
                    "prompt_template": "zomic_generate_v1",
                    "example_pack_path": None,
                    "max_conditioning_examples": 3,
                    "seed_zomic_path": None,
                },
                "lineage": {
                    "acceptance_pack_path": (
                        "data/benchmarks/llm_acceptance/pack_v1/acceptance_pack.json"
                    ),
                    "eval_set_manifest_path": None,
                    "proposal_path": (
                        "data/benchmarks/llm_acceptance/pack_v1/proposals/proposal-001.json"
                    ),
                    "approval_path": (
                        "data/benchmarks/llm_acceptance/pack_v1/approvals/approval-001.json"
                    ),
                    "source_system_config_path": str(config_path),
                    "source_system_config_hash": config_sha256(config),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return spec_path


@pytest.mark.integration
def test_real_mode_llm_launch_candidates_continue_through_screen_with_lineage(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    repo_workspace = Path(__file__).resolve().parents[1]
    artifact_workspace = tmp_path / "workspace"
    config_path = repo_workspace / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    spec_path = _write_llm_campaign_spec(tmp_path, config_path)

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: artifact_workspace)

    launch = runner.invoke(app, ["llm-launch", "--campaign-spec", str(spec_path)])
    assert launch.exit_code == 0, f"llm-launch failed:\n{launch.stdout}\n{launch.stderr}"
    launch_summary = json.loads(launch.stdout)
    candidates_path = Path(launch_summary["candidates_path"])
    assert candidates_path.exists()

    candidate_rows = [
        json.loads(line)
        for line in candidates_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert candidate_rows
    assert candidate_rows[0]["provenance"]["llm_campaign"]["campaign_id"] == "campaign-001"

    screen = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen.exit_code == 0, f"screen failed:\n{screen.stdout}\n{screen.stderr}"
    screen_summary = json.loads(screen.stdout)
    screen_manifest = json.loads(
        Path(screen_summary["manifest_path"]).read_text(encoding="utf-8")
    )
    assert screen_manifest["source_lineage"]["llm_campaign"]["campaign_id"] == "campaign-001"
    assert screen_manifest["source_lineage"]["llm_campaign"]["campaign_spec_path"] == str(spec_path)
    assert screen_manifest["source_lineage"]["llm_campaign"]["launch_summary_path"].endswith(
        "launch_summary.json"
    )


@pytest.mark.integration
def test_real_mode_end_to_end_pipeline_artifacts_with_source_registry(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = _write_source_registry_real_config(tmp_path)
    fixture_path = workspace / "data" / "external" / "fixtures" / "hypodx_sample.json"

    ingest = runner.invoke(
        app,
        ["ingest", "--config", str(config_path), "--fixture", str(fixture_path)],
    )
    assert ingest.exit_code == 0
    ingest_summary = json.loads(ingest.stdout)
    ingest_manifest = json.loads(Path(ingest_summary["manifest_path"]).read_text(encoding="utf-8"))
    assert ingest_manifest["source_lineage"]["source_key"] == "hypodx"
    assert ingest_manifest["source_lineage"]["projection_summary"]["deduped_count"] >= 1

    generate = runner.invoke(
        app,
        ["generate", "--config", str(config_path), "--count", "45", "--seed", "1101"],
    )
    assert generate.exit_code == 0
    screen = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen.exit_code == 0
    validate = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "all"],
    )
    assert validate.exit_code == 0
    rank = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert rank.exit_code == 0
    active = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert active.exit_code == 0
    report = runner.invoke(app, ["report", "--config", str(config_path)])
    assert report.exit_code == 0

    report_summary = json.loads(report.stdout)
    pipeline_manifest_path = Path(report_summary["pipeline_manifest_path"])
    assert pipeline_manifest_path.exists()
    pipeline_manifest = json.loads(pipeline_manifest_path.read_text(encoding="utf-8"))
    assert pipeline_manifest["stage"] == "pipeline"
    assert "report_json" in pipeline_manifest["output_hashes"]


@pytest.mark.integration
def test_source_registry_ingest_path_stays_no_dft_and_offline(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = _write_source_registry_real_config(tmp_path)
    fixture_path = workspace / "data" / "external" / "fixtures" / "hypodx_sample.json"

    def _unexpected_call(*args, **kwargs):
        raise AssertionError("ingest should not cross the no-DFT boundary")

    for attribute in (
        "run_committee_relaxation",
        "compute_proxy_hull",
        "run_geometry_prefilter",
        "run_mlip_phonon_checks",
        "run_short_md_stability",
        "validate_xrd_signatures",
    ):
        monkeypatch.setattr(f"materials_discovery.cli.{attribute}", _unexpected_call)

    result = runner.invoke(
        app,
        ["ingest", "--config", str(config_path), "--fixture", str(fixture_path)],
    )

    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Phase 4: Two-system end-to-end benchmark regression
#
# These tests exercise the full pipeline for both reference-aware benchmark
# configs introduced in Phase 4 (Al-Cu-Fe and Sc-Zn).  They form a dedicated
# slower benchmark lane, marked with @pytest.mark.benchmark_lane to allow
# selective execution:
#
#   uv run pytest -m benchmark_lane
#
# Both tests stay offline/deterministic because they rely exclusively on
# committed fixture data already present under data/external/sources/.
#
# Sc-Zn note: the sc_zn_reference_aware.yaml config declares a zomic_design,
# which normally requires Java to invoke ./gradlew :core:zomicExport.  When
# Java is absent on the test host, the Zomic export step is gracefully skipped
# and the pipeline falls back to the pinned fixture seed.  The test handles
# this transparently — it still asserts on the full downstream pipeline outputs.
# ---------------------------------------------------------------------------

_java_absent = shutil.which("java") is None


@pytest.mark.integration
@pytest.mark.benchmark_lane
def test_al_cu_fe_reference_aware_benchmark_e2e() -> None:
    """End-to-end benchmark flow for the Al-Cu-Fe reference-aware Phase 4 lane.

    Runs the full mdisc pipeline from ingest through report and asserts that:
    - The ingest manifest carries pack_id + member_sources lineage
    - The pipeline manifest is written with the expected stage key
    - The benchmark_pack.json artifact exists and has the required structure
    - The benchmark_context in the pack reflects the Al-Cu-Fe reference pack
    """
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_reference_aware.yaml"

    ingest = runner.invoke(app, ["ingest", "--config", str(config_path)])
    assert ingest.exit_code == 0, f"ingest failed:\n{ingest.stdout}\n{ingest.exception}"
    ingest_summary = json.loads(ingest.stdout)
    ingest_manifest_path = Path(ingest_summary["manifest_path"])
    assert ingest_manifest_path.exists()

    ingest_manifest = json.loads(ingest_manifest_path.read_text(encoding="utf-8"))
    source_lineage = ingest_manifest.get("source_lineage", {})
    assert source_lineage.get("pack_id") == "al_cu_fe_v1", (
        f"expected pack_id 'al_cu_fe_v1', got {source_lineage.get('pack_id')!r}"
    )
    member_sources = source_lineage.get("member_sources", [])
    member_source_keys = [m["source_key"] for m in member_sources if isinstance(m, dict)]
    assert "hypodx" in member_source_keys
    assert "materials_project" in member_source_keys

    generate = runner.invoke(
        app,
        ["generate", "--config", str(config_path), "--count", "35", "--seed", "4001"],
    )
    assert generate.exit_code == 0, f"generate failed:\n{generate.stdout}\n{generate.exception}"
    generate_summary = json.loads(generate.stdout)
    assert Path(generate_summary["manifest_path"]).exists()
    assert Path(generate_summary["calibration_path"]).exists()

    screen = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen.exit_code == 0, f"screen failed:\n{screen.stdout}\n{screen.exception}"
    screen_summary = json.loads(screen.stdout)
    assert Path(screen_summary["manifest_path"]).exists()

    validate = runner.invoke(
        app, ["hifi-validate", "--config", str(config_path), "--batch", "all"]
    )
    assert validate.exit_code == 0, f"hifi-validate failed:\n{validate.stdout}\n{validate.exception}"
    validate_summary = json.loads(validate.stdout)
    assert Path(validate_summary["manifest_path"]).exists()

    rank = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert rank.exit_code == 0, f"hifi-rank failed:\n{rank.stdout}\n{rank.exception}"
    rank_summary = json.loads(rank.stdout)
    assert Path(rank_summary["manifest_path"]).exists()

    active = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert active.exit_code == 0, f"active-learn failed:\n{active.stdout}\n{active.exception}"

    report = runner.invoke(app, ["report", "--config", str(config_path)])
    assert report.exit_code == 0, f"report failed:\n{report.stdout}\n{report.exception}"
    report_summary = json.loads(report.stdout)

    pipeline_manifest_path = Path(report_summary["pipeline_manifest_path"])
    assert pipeline_manifest_path.exists()
    pipeline_manifest = json.loads(pipeline_manifest_path.read_text(encoding="utf-8"))
    assert pipeline_manifest["stage"] == "pipeline"
    assert "report_json" in pipeline_manifest["output_hashes"]

    system_slug = "al_cu_fe"
    benchmark_pack_path = workspace / "data" / "reports" / f"{system_slug}_benchmark_pack.json"
    assert benchmark_pack_path.exists(), (
        f"benchmark_pack.json not written: {benchmark_pack_path}"
    )
    bp = json.loads(benchmark_pack_path.read_text(encoding="utf-8"))
    assert bp["schema_version"] == "benchmark-pack/v1"
    assert bp["system"] == "Al-Cu-Fe"
    assert bp["backend_mode"] == "real"

    bm_ctx = bp["benchmark_context"]
    assert bm_ctx["reference_pack_id"] == "al_cu_fe_v1"
    assert "hypodx" in bm_ctx["source_keys"]
    assert "materials_project" in bm_ctx["source_keys"]
    assert bm_ctx["backend_mode"] == "real"
    assert bm_ctx["lane_id"].startswith("al_cu_fe_v1:")

    assert "stage_manifest_paths" in bp
    assert "report_metrics" in bp
    report_metrics = bp["report_metrics"]
    assert "report_fingerprint" in report_metrics
    assert "release_gate" in report_metrics


@pytest.mark.integration
@pytest.mark.benchmark_lane
def test_sc_zn_reference_aware_benchmark_e2e() -> None:
    """End-to-end benchmark flow for the Sc-Zn reference-aware Phase 4 lane.

    The Sc-Zn config declares a zomic_design which invokes Java/Gradle for
    Zomic export.  When Java is absent (CI without JDK), the test still runs
    the pipeline with the pre-staged fixture seed — the validation, ranking,
    and reporting stages are unaffected by the Java dependency.

    Asserts that:
    - The ingest manifest carries sc_zn_v1 pack_id + member_sources lineage
    - The pipeline manifest is written with the expected stage key
    - The benchmark_pack.json artifact exists and has the required structure
    - The benchmark_context in the pack reflects the Sc-Zn reference pack
    """
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "sc_zn_reference_aware.yaml"

    ingest = runner.invoke(app, ["ingest", "--config", str(config_path)])
    assert ingest.exit_code == 0, f"ingest failed:\n{ingest.stdout}\n{ingest.exception}"
    ingest_summary = json.loads(ingest.stdout)
    ingest_manifest_path = Path(ingest_summary["manifest_path"])
    assert ingest_manifest_path.exists()

    ingest_manifest = json.loads(ingest_manifest_path.read_text(encoding="utf-8"))
    source_lineage = ingest_manifest.get("source_lineage", {})
    assert source_lineage.get("pack_id") == "sc_zn_v1", (
        f"expected pack_id 'sc_zn_v1', got {source_lineage.get('pack_id')!r}"
    )
    member_sources = source_lineage.get("member_sources", [])
    member_source_keys = [m["source_key"] for m in member_sources if isinstance(m, dict)]
    assert "hypodx" in member_source_keys
    assert "cod" in member_source_keys

    generate = runner.invoke(
        app,
        ["generate", "--config", str(config_path), "--count", "30", "--seed", "4002"],
    )
    if _java_absent and generate.exit_code != 0:
        pytest.skip(
            "Sc-Zn generate requires Java for Zomic export; Java not found on this host. "
            "Skipping the generate-onwards stages — ingest lineage asserted above."
        )
    assert generate.exit_code == 0, f"generate failed:\n{generate.stdout}\n{generate.exception}"
    generate_summary = json.loads(generate.stdout)
    assert Path(generate_summary["manifest_path"]).exists()

    screen = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen.exit_code == 0, f"screen failed:\n{screen.stdout}\n{screen.exception}"

    validate = runner.invoke(
        app, ["hifi-validate", "--config", str(config_path), "--batch", "all"]
    )
    assert validate.exit_code == 0, f"hifi-validate failed:\n{validate.stdout}\n{validate.exception}"

    rank = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert rank.exit_code == 0, f"hifi-rank failed:\n{rank.stdout}\n{rank.exception}"

    active = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert active.exit_code == 0, f"active-learn failed:\n{active.stdout}\n{active.exception}"

    report = runner.invoke(app, ["report", "--config", str(config_path)])
    assert report.exit_code == 0, f"report failed:\n{report.stdout}\n{report.exception}"
    report_summary = json.loads(report.stdout)

    pipeline_manifest_path = Path(report_summary["pipeline_manifest_path"])
    assert pipeline_manifest_path.exists()
    pipeline_manifest = json.loads(pipeline_manifest_path.read_text(encoding="utf-8"))
    assert pipeline_manifest["stage"] == "pipeline"
    assert "report_json" in pipeline_manifest["output_hashes"]

    system_slug = "sc_zn"
    benchmark_pack_path = workspace / "data" / "reports" / f"{system_slug}_benchmark_pack.json"
    assert benchmark_pack_path.exists(), (
        f"benchmark_pack.json not written: {benchmark_pack_path}"
    )
    bp = json.loads(benchmark_pack_path.read_text(encoding="utf-8"))
    assert bp["schema_version"] == "benchmark-pack/v1"
    assert bp["system"] == "Sc-Zn"
    assert bp["backend_mode"] == "real"

    bm_ctx = bp["benchmark_context"]
    assert bm_ctx["reference_pack_id"] == "sc_zn_v1"
    assert "hypodx" in bm_ctx["source_keys"]
    assert "cod" in bm_ctx["source_keys"]
    assert bm_ctx["backend_mode"] == "real"
    assert bm_ctx["lane_id"].startswith("sc_zn_v1:")

    assert "stage_manifest_paths" in bp
    assert "report_metrics" in bp
    report_metrics = bp["report_metrics"]
    assert "report_fingerprint" in report_metrics
    assert "release_gate" in report_metrics
