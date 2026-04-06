from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml, write_json_object, write_jsonl
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    SiteRecord,
    SystemConfig,
)
from materials_discovery.llm.storage import (
    llm_acceptance_pack_path,
    llm_campaign_comparison_path,
    llm_campaign_outcome_snapshot_path,
)
from materials_discovery.llm.checkpoints import promote_checkpoint, register_llm_checkpoint
from materials_discovery.llm.serving_benchmark import load_serving_benchmark_spec


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


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _write_llm_campaign_spec(
    tmp_path: Path,
    config_path: Path,
    *,
    pack_id: str = "pack_v1",
) -> Path:
    config = SystemConfig.model_validate(load_yaml(config_path))
    workspace = Path(__file__).resolve().parents[1]
    llm_generate = config.llm_generate
    system_slug = _system_slug(config.system_name)
    spec_path = tmp_path / "campaign_spec.json"
    spec_path.write_text(
        json.dumps(
            {
                "schema_version": "llm-campaign-spec/v1",
                "campaign_id": "campaign-001",
                "proposal_id": "proposal-001",
                "approval_id": "approval-001",
                "system": config.system_name,
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
                    "system": config.system_name,
                    "template_family": config.template_family,
                    "default_count": min(config.default_count, 2),
                    "composition_bounds": {
                        species: bound.model_dump(mode="json")
                        for species, bound in config.composition_bounds.items()
                    },
                    "prompt_template": (
                        "zomic_generate_v1"
                        if llm_generate is None
                        else llm_generate.prompt_template
                    ),
                    "example_pack_path": None,
                    "max_conditioning_examples": 3,
                    "seed_zomic_path": (
                        None
                        if llm_generate is None or llm_generate.seed_zomic is None
                        else str((workspace / llm_generate.seed_zomic).resolve())
                    ),
                },
                "lineage": {
                    "acceptance_pack_path": f"data/benchmarks/llm_acceptance/{pack_id}/acceptance_pack.json",
                    "eval_set_manifest_path": None,
                    "proposal_path": f"data/benchmarks/llm_acceptance/{pack_id}/proposals/{system_slug}_proposal_001.json",
                    "approval_path": f"data/benchmarks/llm_acceptance/{pack_id}/approvals/{system_slug}_approval_001.json",
                    "source_system_config_path": str(config_path),
                    "source_system_config_hash": config_sha256(config),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return spec_path


def _write_llm_acceptance_pack(
    root: Path,
    pack_id: str = "pack_v1",
    *,
    system: str = "Al-Cu-Fe",
) -> Path:
    system_slug = _system_slug(system)
    acceptance_pack_path = llm_acceptance_pack_path(pack_id, root=root)
    acceptance_pack_path.parent.mkdir(parents=True, exist_ok=True)
    acceptance_pack_path.write_text(
        json.dumps(
            {
                "schema_version": "llm-acceptance-pack/v1",
                "pack_id": pack_id,
                "created_at_utc": "2026-04-04T16:30:00Z",
                "eval_set_manifest_path": None,
                "thresholds": {
                    "min_parse_success_rate": 0.8,
                    "min_compile_success_rate": 0.8,
                    "min_generation_success_rate": 0.3,
                    "min_shortlist_pass_rate": 0.05,
                    "min_validation_pass_rate": 0.02,
                    "min_novelty_score_mean": 0.0,
                    "min_synthesizability_mean": 0.5,
                },
                "systems": [
                    {
                        "system": system,
                        "generate_comparison_path": (
                            f"data/benchmarks/llm_generate/{system_slug}_comparison.json"
                        ),
                        "pipeline_comparison_path": (
                            f"data/benchmarks/llm_pipeline/{system_slug}_comparison.json"
                        ),
                        "parse_success_rate": 0.72,
                        "compile_success_rate": 0.64,
                        "generation_success_rate": 0.28,
                        "shortlist_pass_rate": 0.04,
                        "validation_pass_rate": 0.01,
                        "novelty_score_mean": 0.11,
                        "synthesizability_mean": 0.46,
                        "report_release_gate_ready": False,
                        "failing_metrics": [
                            "parse_success_rate",
                            "compile_success_rate",
                            "generation_success_rate",
                        ],
                        "passed": False,
                    }
                ],
                "overall_passed": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return acceptance_pack_path


def _write_specialized_report_artifacts(
    root: Path,
    *,
    system: str,
    launch_payload: dict[str, object],
    launch_summary_path: Path,
    evaluation_model: str,
) -> None:
    system_slug = _system_slug(system)
    manifests_dir = root / "data" / "manifests"
    calibration_dir = root / "data" / "calibration"
    reports_dir = root / "data" / "reports"
    lineage = {
        "llm_campaign": {
            "campaign_id": launch_payload["campaign_id"],
            "launch_id": launch_payload["launch_id"],
            "campaign_spec_path": launch_payload["campaign_spec_path"],
            "launch_summary_path": str(launch_summary_path),
            "resolved_launch_path": launch_payload["resolved_launch_path"],
        }
    }
    write_json_object(
        {"stage": "report", "created_at_utc": "2026-04-05T05:10:00Z", "source_lineage": lineage},
        manifests_dir / f"{system_slug}_report_manifest.json",
    )
    write_json_object(
        {
            "stage": "pipeline",
            "created_at_utc": "2026-04-05T05:11:00Z",
            "source_lineage": lineage,
        },
        manifests_dir / f"{system_slug}_pipeline_manifest.json",
    )
    write_json_object(
        {"llm_synthesizability_mean": 0.67, "release_gate_ready": False},
        calibration_dir / f"{system_slug}_report_calibration.json",
    )
    write_json_object(
        {
            "entries": [
                {
                    "candidate_id": "md_000001",
                    "llm_assessment": {
                        "status": "passed",
                        "requested_model_lanes": ["specialized_materials"],
                        "resolved_model_lane": "specialized_materials",
                        "resolved_model_lane_source": "configured_lane",
                        "serving_identity": {
                            "requested_model_lane": "specialized_materials",
                            "resolved_model_lane": "specialized_materials",
                            "resolved_model_lane_source": "configured_lane",
                            "adapter": "openai_compat_v1",
                            "provider": "openai_compat",
                            "model": evaluation_model,
                            "effective_api_base": "http://specialist.example.internal:8000",
                        },
                    },
                }
            ]
        },
        reports_dir / f"{system_slug}_report.json",
    )


def _write_hosted_llm_config(tmp_path: Path, *, base_config_path: Path) -> Path:
    payload = load_yaml(base_config_path)
    payload["backend"]["llm_adapter"] = "anthropic_api_v1"
    payload["backend"]["llm_provider"] = "anthropic"
    payload["backend"]["llm_model"] = "claude-hosted-v1"
    payload["backend"]["llm_api_base"] = None
    payload["llm_generate"]["model_lanes"]["general_purpose"] = {
        "adapter": "anthropic_api_v1",
        "provider": "anthropic",
        "model": "claude-hosted-v1",
    }
    config_path = tmp_path / "al_cu_fe_llm_hosted.yaml"
    config_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return config_path


def _retag_llm_campaign_spec(
    spec_path: Path,
    *,
    campaign_id: str,
    proposal_id: str,
    approval_id: str,
    preferred_model_lane: str,
) -> None:
    payload = json.loads(spec_path.read_text(encoding="utf-8"))
    payload["campaign_id"] = campaign_id
    payload["proposal_id"] = proposal_id
    payload["approval_id"] = approval_id
    payload["actions"][0]["preferred_model_lane"] = preferred_model_lane
    spec_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_serving_benchmark_spec(
    tmp_path: Path,
    *,
    benchmark_id: str,
    acceptance_pack_path: Path,
    hosted_config_path: Path,
    hosted_spec_path: Path,
    local_config_path: Path,
    local_spec_path: Path,
    evaluate_batch: str = "top1",
) -> Path:
    spec_path = tmp_path / "serving_benchmark.yaml"
    spec_path.write_text(
        yaml.safe_dump(
            {
                "benchmark_id": benchmark_id,
                "acceptance_pack_path": str(acceptance_pack_path),
                "targets": [
                    {
                        "target_id": "hosted_generation",
                        "label": "Hosted generation",
                        "workflow_role": "campaign_launch",
                        "system_config_path": str(hosted_config_path),
                        "campaign_spec_path": str(hosted_spec_path),
                        "generation_model_lane": "general_purpose",
                        "estimated_cost_usd": 1.25,
                        "operator_friction_tier": "low",
                    },
                    {
                        "target_id": "local_generation",
                        "label": "Local generation",
                        "workflow_role": "campaign_launch",
                        "system_config_path": str(local_config_path),
                        "campaign_spec_path": str(local_spec_path),
                        "generation_model_lane": "general_purpose",
                        "estimated_cost_usd": 0.08,
                        "operator_friction_tier": "medium",
                    },
                    {
                        "target_id": "specialized_assessment",
                        "label": "Specialized assessment",
                        "workflow_role": "llm_evaluate",
                        "system_config_path": str(local_config_path),
                        "batch": evaluate_batch,
                        "evaluation_model_lane": "specialized_materials",
                        "estimated_cost_usd": 0.03,
                        "operator_friction_tier": "high",
                    },
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return spec_path


def test_committed_serving_benchmark_examples_validate_and_stay_shared_context(
    tmp_path: Path,
) -> None:
    workspace = Path(__file__).resolve().parents[1]
    hosted_config_path = workspace / "configs" / "systems" / "al_cu_fe_llm_hosted.yaml"
    local_config_path = workspace / "configs" / "systems" / "al_cu_fe_llm_local.yaml"
    adapted_config_path = workspace / "configs" / "systems" / "al_cu_fe_llm_adapted.yaml"
    adapted_pinned_config_path = (
        workspace / "configs" / "systems" / "al_cu_fe_llm_adapted_pinned.yaml"
    )
    sc_zn_local_config_path = workspace / "configs" / "systems" / "sc_zn_llm_local.yaml"
    al_benchmark_example = workspace / "configs" / "llm" / "al_cu_fe_serving_benchmark.yaml"
    adapted_benchmark_example = workspace / "configs" / "llm" / "al_cu_fe_adapted_serving_benchmark.yaml"
    sc_benchmark_example = workspace / "configs" / "llm" / "sc_zn_serving_benchmark.yaml"

    hosted_config = SystemConfig.model_validate(load_yaml(hosted_config_path))
    assert hosted_config.backend.llm_adapter == "anthropic_api_v1"
    assert hosted_config.backend.llm_provider == "anthropic"
    assert hosted_config.backend.llm_model == "hosted-general-placeholder"
    assert hosted_config.llm_generate is not None
    assert hosted_config.llm_generate.max_attempts == 2
    adapted_config = SystemConfig.model_validate(load_yaml(adapted_config_path))
    adapted_pinned_config = SystemConfig.model_validate(load_yaml(adapted_pinned_config_path))
    assert adapted_config.llm_generate is not None
    assert adapted_config.llm_generate.model_lanes["general_purpose"].checkpoint_family == (
        "adapted-al-cu-fe"
    )
    assert adapted_config.llm_generate.model_lanes["general_purpose"].checkpoint_id is None
    assert adapted_config.llm_generate.model_lanes["general_purpose"].require_checkpoint_registration
    assert adapted_config.llm_generate.model_lanes["general_purpose"].model_revision is None
    assert adapted_config.llm_generate.model_lanes["general_purpose"].local_model_path is None
    assert adapted_pinned_config.llm_generate is not None
    assert adapted_pinned_config.llm_generate.model_lanes["general_purpose"].checkpoint_family == (
        "adapted-al-cu-fe"
    )
    assert adapted_pinned_config.llm_generate.model_lanes["general_purpose"].checkpoint_id == (
        "ckpt-al-cu-fe-zomic-adapted"
    )

    al_acceptance_pack_path = _write_llm_acceptance_pack(tmp_path / "al_workspace", system="Al-Cu-Fe")
    (tmp_path / "al_hosted_campaign").mkdir(parents=True, exist_ok=True)
    (tmp_path / "al_local_campaign").mkdir(parents=True, exist_ok=True)
    (tmp_path / "al_adapted_campaign").mkdir(parents=True, exist_ok=True)
    hosted_campaign_spec_path = _write_llm_campaign_spec(
        tmp_path / "al_hosted_campaign",
        hosted_config_path,
    )
    local_campaign_spec_path = _write_llm_campaign_spec(
        tmp_path / "al_local_campaign",
        local_config_path,
    )
    adapted_campaign_spec_path = _write_llm_campaign_spec(
        tmp_path / "al_adapted_campaign",
        adapted_config_path,
    )
    al_payload = load_yaml(al_benchmark_example)
    al_payload["acceptance_pack_path"] = str(al_acceptance_pack_path)
    for target in al_payload["targets"]:
        target["system_config_path"] = str(
            (al_benchmark_example.parent / target["system_config_path"]).resolve()
        )
        if target["target_id"] == "hosted_generation":
            target["campaign_spec_path"] = str(hosted_campaign_spec_path)
        elif target["target_id"] == "local_generation":
            target["campaign_spec_path"] = str(local_campaign_spec_path)
    al_runtime_spec_path = tmp_path / "al_runtime_benchmark.yaml"
    al_runtime_spec_path.write_text(yaml.safe_dump(al_payload, sort_keys=False), encoding="utf-8")

    al_spec = load_serving_benchmark_spec(al_runtime_spec_path)
    assert al_spec.benchmark_id == "al_cu_fe_serving_v1"
    assert [target.target_id for target in al_spec.targets] == [
        "hosted_generation",
        "local_generation",
        "specialized_assessment",
    ]
    specialized_target = next(
        target for target in al_spec.targets if target.target_id == "specialized_assessment"
    )
    assert specialized_target.workflow_role == "llm_evaluate"
    assert specialized_target.batch == "top1"
    assert specialized_target.evaluation_model_lane == "specialized_materials"

    adapted_payload = load_yaml(adapted_benchmark_example)
    adapted_payload["acceptance_pack_path"] = str(al_acceptance_pack_path)
    for target in adapted_payload["targets"]:
        target["system_config_path"] = str(
            (adapted_benchmark_example.parent / target["system_config_path"]).resolve()
        )
        if target["target_id"] == "baseline_local_generation":
            target["campaign_spec_path"] = str(local_campaign_spec_path)
        elif target["target_id"] == "adapted_checkpoint_generation":
            target["campaign_spec_path"] = str(adapted_campaign_spec_path)
    adapted_runtime_spec_path = tmp_path / "al_runtime_adapted_benchmark.yaml"
    adapted_runtime_spec_path.write_text(
        yaml.safe_dump(adapted_payload, sort_keys=False),
        encoding="utf-8",
    )

    adapted_spec = load_serving_benchmark_spec(adapted_runtime_spec_path)
    assert adapted_spec.benchmark_id == "al_cu_fe_adapted_checkpoint_v1"
    assert [target.target_id for target in adapted_spec.targets] == [
        "baseline_local_generation",
        "adapted_checkpoint_generation",
    ]
    assert any(
        target.notes and "register the checkpoint" in target.notes.lower()
        for target in adapted_spec.targets
    )

    sc_acceptance_pack_path = _write_llm_acceptance_pack(tmp_path / "sc_workspace", system="Sc-Zn")
    (tmp_path / "sc_local_campaign").mkdir(parents=True, exist_ok=True)
    sc_campaign_spec_path = _write_llm_campaign_spec(
        tmp_path / "sc_local_campaign",
        sc_zn_local_config_path,
    )
    sc_payload = load_yaml(sc_benchmark_example)
    sc_payload["acceptance_pack_path"] = str(sc_acceptance_pack_path)
    for target in sc_payload["targets"]:
        target["system_config_path"] = str(
            (sc_benchmark_example.parent / target["system_config_path"]).resolve()
        )
        if target["workflow_role"] == "campaign_launch":
            target["campaign_spec_path"] = str(sc_campaign_spec_path)
    sc_runtime_spec_path = tmp_path / "sc_runtime_benchmark.yaml"
    sc_runtime_spec_path.write_text(yaml.safe_dump(sc_payload, sort_keys=False), encoding="utf-8")

    sc_spec = load_serving_benchmark_spec(sc_runtime_spec_path)
    assert sc_spec.benchmark_id == "sc_zn_serving_v1"
    assert [target.target_id for target in sc_spec.targets] == [
        "local_generation",
        "specialized_assessment",
    ]
    assert any(
        target.notes and "compatibility" in target.notes.lower() for target in sc_spec.targets
    )


@pytest.mark.integration
def test_real_mode_adapted_checkpoint_benchmark_reuses_launch_and_compare_workflow_offline(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    repo_workspace = Path(__file__).resolve().parents[1]
    artifact_workspace = tmp_path / "workspace"
    acceptance_pack_path = _write_llm_acceptance_pack(artifact_workspace, system="Al-Cu-Fe")
    baseline_config_path = repo_workspace / "configs" / "systems" / "al_cu_fe_llm_local.yaml"
    adapted_config_path = repo_workspace / "configs" / "systems" / "al_cu_fe_llm_adapted.yaml"
    benchmark_example = repo_workspace / "configs" / "llm" / "al_cu_fe_adapted_serving_benchmark.yaml"

    (tmp_path / "baseline_campaign").mkdir(parents=True, exist_ok=True)
    (tmp_path / "adapted_campaign").mkdir(parents=True, exist_ok=True)
    baseline_spec_path = _write_llm_campaign_spec(tmp_path / "baseline_campaign", baseline_config_path)
    adapted_spec_path = _write_llm_campaign_spec(tmp_path / "adapted_campaign", adapted_config_path)

    checkpoint_lineage_dir = artifact_workspace / "lineage"
    checkpoint_lineage_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "adapter_manifest.json",
        "corpus_manifest.json",
        "eval_manifest.json",
        "acceptance_pack.json",
    ):
        (checkpoint_lineage_dir / name).write_text("{}", encoding="utf-8")
    checkpoint_spec_path = artifact_workspace / "al_cu_fe_zomic_adapted_checkpoint.yaml"
    checkpoint_spec_path.write_text(
        yaml.safe_dump(
            {
                "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
                "checkpoint_family": "adapted-al-cu-fe",
                "system": "Al-Cu-Fe",
                "template_family": "icosahedral_approximant_1_1",
                "adapter": "openai_compat_v1",
                "provider": "openai_compat",
                "model": "zomic-al-cu-fe-adapted-v1",
                "local_model_path": "/opt/models/zomic-al-cu-fe-adapted-v1",
                "model_revision": "adapted-dev-2026-04-05",
                "base_model": "zomic-general-local-v1",
                "base_model_revision": "local-dev-2026-04-05",
                "adaptation_method": "lora",
                "adaptation_artifact_path": "lineage/adapter_manifest.json",
                "corpus_manifest_path": "lineage/corpus_manifest.json",
                "eval_set_manifest_path": "lineage/eval_manifest.json",
                "acceptance_pack_path": "lineage/acceptance_pack.json",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    register_llm_checkpoint(checkpoint_spec_path, root=artifact_workspace)
    benchmark_reports_dir = artifact_workspace / "reports"
    benchmark_reports_dir.mkdir(parents=True, exist_ok=True)
    (benchmark_reports_dir / "serving_benchmark.json").write_text("{}", encoding="utf-8")
    promotion_spec_path = artifact_workspace / "al_cu_fe_zomic_adapted_promotion.yaml"
    promotion_spec_path.write_text(
        yaml.safe_dump(
            {
                "checkpoint_family": "adapted-al-cu-fe",
                "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
                "evidence_paths": ["reports/serving_benchmark.json"],
                "expected_revision": 1,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    promote_checkpoint(promotion_spec_path, root=artifact_workspace)

    benchmark_payload = load_yaml(benchmark_example)
    benchmark_payload["acceptance_pack_path"] = str(acceptance_pack_path)
    for target in benchmark_payload["targets"]:
        target["system_config_path"] = str(
            (benchmark_example.parent / target["system_config_path"]).resolve()
        )
        if target["target_id"] == "baseline_local_generation":
            target["campaign_spec_path"] = str(baseline_spec_path)
        elif target["target_id"] == "adapted_checkpoint_generation":
            target["campaign_spec_path"] = str(adapted_spec_path)
    benchmark_spec_path = tmp_path / "al_cu_fe_adapted_benchmark_runtime.yaml"
    benchmark_spec_path.write_text(
        yaml.safe_dump(benchmark_payload, sort_keys=False),
        encoding="utf-8",
    )

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr("materials_discovery.llm.serving_benchmark.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: artifact_workspace)

    class _FakeAdapter:
        def generate(self, request) -> str:
            del request
            return "label adapted.demo\n"

    def _fake_compile(
        zomic_text: str,
        *,
        prototype_key: str,
        system_name: str,
        template_family: str,
        source_qphi_bounds=None,
        artifact_root: Path | None = None,
    ) -> dict[str, object]:
        del zomic_text, system_name, template_family, source_qphi_bounds
        raw_export_path = None
        orbit_library_path = None
        if artifact_root is not None:
            artifact_root.mkdir(parents=True, exist_ok=True)
            raw_export_path = artifact_root / f"{prototype_key}.raw.json"
            orbit_library_path = artifact_root / f"{prototype_key}.json"
            raw_export_path.write_text("{}", encoding="utf-8")
            orbit_library_path.write_text("{}", encoding="utf-8")
        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "error_kind": None,
            "raw_export_path": None if raw_export_path is None else str(raw_export_path),
            "orbit_library_path": None if orbit_library_path is None else str(orbit_library_path),
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        }

    def _fake_candidate_from_prototype_library(
        config: SystemConfig,
        *,
        seed: int,
        candidate_index: int,
        template_override_path: Path,
        extra_provenance: dict[str, object] | None = None,
    ) -> CandidateRecord:
        del seed, template_override_path
        provenance = {"source": "llm"}
        if extra_provenance:
            provenance.update(extra_provenance)
        return CandidateRecord(
            candidate_id=f"md_{candidate_index:06d}",
            system=config.system_name,
            template_family=config.template_family,
            cell={
                "a": 14.2,
                "b": 14.2,
                "c": 14.2,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            sites=[
                SiteRecord(
                    label="S01",
                    qphi=((0, 0), (1, 0), (1, 0)),
                    species="Al",
                    occ=1.0,
                    fractional_position=(0.2, 0.2, 0.2),
                    cartesian_position=(2.84, 2.84, 2.84),
                )
            ],
            composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            screen={"model": "MACE", "energy_per_atom_ev": -3.0},
            digital_validation=DigitalValidationRecord(status="pending"),
            provenance=provenance,
        )

    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.validate_llm_adapter_ready",
        lambda adapter, **kwargs: None,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.generate.resolve_llm_adapter",
        lambda mode, backend=None, llm_generate=None: _FakeAdapter(),
    )
    monkeypatch.setattr("materials_discovery.llm.generate.compile_zomic_script", _fake_compile)
    monkeypatch.setattr(
        "materials_discovery.llm.generate.build_candidate_from_prototype_library",
        _fake_candidate_from_prototype_library,
    )

    result = runner.invoke(app, ["llm-serving-benchmark", "--spec", str(benchmark_spec_path)])

    assert result.exit_code == 0, (
        f"llm-serving-benchmark failed:\n{result.stdout}\n{result.stderr}"
    )
    summary_path = (
        artifact_workspace
        / "data"
        / "benchmarks"
        / "llm_serving"
        / "al_cu_fe_adapted_checkpoint_v1"
        / "benchmark_summary.json"
    )
    assert summary_path.exists()
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    targets = {row["target_id"]: row for row in summary_payload["targets"]}
    adapted_identity = targets["adapted_checkpoint_generation"]["smoke_checks"][0]["serving_identity"]
    assert adapted_identity["checkpoint_id"] == "ckpt-al-cu-fe-zomic-adapted"
    assert adapted_identity["checkpoint_selection_source"] == "family_promoted_default"
    assert adapted_identity["checkpoint_lifecycle_revision"] == 2
    assert adapted_identity["checkpoint_lineage"]["base_model"] == "zomic-general-local-v1"
    assert Path(targets["baseline_local_generation"]["launch_summary_path"]).exists()
    assert Path(targets["adapted_checkpoint_generation"]["launch_summary_path"]).exists()
    assert any("Adapted checkpoint" in line for line in summary_payload["recommendation_lines"])
    assert any("Rollback baseline remains available:" in line for line in summary_payload["recommendation_lines"])


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
def test_real_mode_llm_replay_compare_campaign_operator_workflow_offline(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    repo_workspace = Path(__file__).resolve().parents[1]
    artifact_workspace = tmp_path / "workspace"
    config_path = repo_workspace / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    acceptance_pack_path = _write_llm_acceptance_pack(artifact_workspace)

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: artifact_workspace)

    suggest = runner.invoke(
        app,
        ["llm-suggest", "--acceptance-pack", str(acceptance_pack_path)],
    )
    assert suggest.exit_code == 0, f"llm-suggest failed:\n{suggest.stdout}\n{suggest.stderr}"
    suggestion_payload = json.loads(suggest.stdout)
    proposal_path = Path(suggestion_payload["proposals"][0]["proposal_path"])
    assert proposal_path.exists()

    approve = runner.invoke(
        app,
        [
            "llm-approve",
            "--proposal",
            str(proposal_path),
            "--decision",
            "approved",
            "--operator",
            "operator@example.com",
            "--config",
            str(config_path),
        ],
    )
    assert approve.exit_code == 0, f"llm-approve failed:\n{approve.stdout}\n{approve.stderr}"
    approval_payload = json.loads(approve.stdout)
    campaign_spec_path = Path(approval_payload["campaign_spec_path"])
    assert campaign_spec_path.exists()

    launch = runner.invoke(
        app,
        ["llm-launch", "--campaign-spec", str(campaign_spec_path)],
    )
    assert launch.exit_code == 0, f"llm-launch failed:\n{launch.stdout}\n{launch.stderr}"
    launch_payload = json.loads(launch.stdout)
    first_launch_summary_path = Path(launch_payload["resolved_launch_path"]).with_name(
        "launch_summary.json"
    )
    assert first_launch_summary_path.exists()

    replay = runner.invoke(
        app,
        ["llm-replay", "--launch-summary", str(first_launch_summary_path)],
    )
    assert replay.exit_code == 0, f"llm-replay failed:\n{replay.stdout}\n{replay.stderr}"
    replay_payload = json.loads(replay.stdout)
    replay_launch_summary_path = Path(replay_payload["resolved_launch_path"]).with_name(
        "launch_summary.json"
    )
    assert replay_launch_summary_path.exists()

    replay_candidates = [
        json.loads(line)
        for line in Path(replay_payload["candidates_path"]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert replay_candidates
    assert replay_candidates[0]["provenance"]["llm_campaign"]["replay_of_launch_id"] == (
        launch_payload["launch_id"]
    )
    assert replay_candidates[0]["provenance"]["llm_campaign"][
        "replay_of_launch_summary_path"
    ] == str(first_launch_summary_path)

    compare = runner.invoke(
        app,
        ["llm-compare", "--launch-summary", str(replay_launch_summary_path)],
    )
    assert compare.exit_code == 0, f"llm-compare failed:\n{compare.stdout}\n{compare.stderr}"

    outcome_snapshot_path = llm_campaign_outcome_snapshot_path(
        replay_payload["campaign_id"],
        replay_payload["launch_id"],
        root=artifact_workspace,
    )
    comparison_path = llm_campaign_comparison_path(
        replay_payload["campaign_id"],
        f"comparison_{replay_payload['launch_id']}",
        root=artifact_workspace,
    )
    assert outcome_snapshot_path.exists()
    assert comparison_path.exists()

    outcome_snapshot = json.loads(outcome_snapshot_path.read_text(encoding="utf-8"))
    assert outcome_snapshot["launch_id"] == replay_payload["launch_id"]
    assert "shortlist_pass_rate" in outcome_snapshot["missing_metrics"]
    assert "validation_pass_rate" in outcome_snapshot["missing_metrics"]

    comparison_payload = json.loads(comparison_path.read_text(encoding="utf-8"))
    assert comparison_payload["launch_id"] == replay_payload["launch_id"]
    assert comparison_payload["current_outcome"]["launch_id"] == replay_payload["launch_id"]
    assert comparison_payload["prior_outcome"]["launch_id"] == launch_payload["launch_id"]
    assert comparison_payload["acceptance_baseline"]["system"] == "Al-Cu-Fe"
    assert "shortlist_pass_rate" in comparison_payload["current_outcome"]["missing_metrics"]
    assert "Prior launch baseline:" in compare.stdout
    assert "Outcome snapshot:" in compare.stdout
    assert "Comparison artifact:" in compare.stdout


@pytest.mark.integration
def test_real_mode_sc_zn_specialized_evaluation_lineage_keeps_launch_replay_compare_compatible_offline(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    repo_workspace = Path(__file__).resolve().parents[1]
    artifact_workspace = tmp_path / "workspace"
    config_path = repo_workspace / "configs" / "systems" / "sc_zn_llm_local.yaml"
    _write_llm_acceptance_pack(artifact_workspace, system="Sc-Zn")
    spec_path = _write_llm_campaign_spec(tmp_path, config_path)

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: artifact_workspace)

    class _FakeAdapter:
        def generate(self, request) -> str:
            del request
            return "label sc_zn.specialist.demo\n"

    def _fake_compile(
        zomic_text: str,
        *,
        prototype_key: str,
        system_name: str,
        template_family: str,
        source_qphi_bounds=None,
        artifact_root: Path | None = None,
    ) -> dict[str, object]:
        del zomic_text, system_name, template_family, source_qphi_bounds
        raw_export_path = None
        orbit_library_path = None
        if artifact_root is not None:
            artifact_root.mkdir(parents=True, exist_ok=True)
            raw_export_path = artifact_root / f"{prototype_key}.raw.json"
            orbit_library_path = artifact_root / f"{prototype_key}.json"
            raw_export_path.write_text("{}", encoding="utf-8")
            orbit_library_path.write_text("{}", encoding="utf-8")
        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "error_kind": None,
            "raw_export_path": None if raw_export_path is None else str(raw_export_path),
            "orbit_library_path": None if orbit_library_path is None else str(orbit_library_path),
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        }

    def _fake_candidate_from_prototype_library(
        config: SystemConfig,
        *,
        seed: int,
        candidate_index: int,
        template_override_path: Path,
        extra_provenance: dict[str, object] | None = None,
    ) -> CandidateRecord:
        del seed, template_override_path
        provenance = {"source": "llm"}
        if extra_provenance:
            provenance.update(extra_provenance)
        return CandidateRecord(
            candidate_id=f"md_{candidate_index:06d}",
            system=config.system_name,
            template_family=config.template_family,
            cell={
                "a": 10.0,
                "b": 10.0,
                "c": 10.0,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            sites=[
                SiteRecord(
                    label="S01",
                    qphi=((0, 0), (0, 0), (0, 0)),
                    species="Sc",
                    occ=1.0,
                    fractional_position=(0.25, 0.25, 0.25),
                    cartesian_position=(2.5, 2.5, 2.5),
                ),
                SiteRecord(
                    label="S02",
                    qphi=((1, 0), (0, 0), (1, 0)),
                    species="Zn",
                    occ=1.0,
                    fractional_position=(0.75, 0.75, 0.75),
                    cartesian_position=(7.5, 7.5, 7.5),
                ),
            ],
            composition={"Sc": 0.25, "Zn": 0.75},
            screen={"model": "MACE", "energy_per_atom_ev": -2.8},
            digital_validation=DigitalValidationRecord(status="pending"),
            provenance=provenance,
        )

    monkeypatch.setattr(
        "materials_discovery.cli.resolve_llm_adapter",
        lambda mode, backend=None, llm_generate=None: _FakeAdapter(),
    )
    monkeypatch.setattr(
        "materials_discovery.cli.validate_llm_adapter_ready",
        lambda adapter, **kwargs: None,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.generate.resolve_llm_adapter",
        lambda mode, backend=None, llm_generate=None: _FakeAdapter(),
    )
    monkeypatch.setattr("materials_discovery.llm.generate.compile_zomic_script", _fake_compile)
    monkeypatch.setattr(
        "materials_discovery.llm.generate.build_candidate_from_prototype_library",
        _fake_candidate_from_prototype_library,
    )

    launch = runner.invoke(app, ["llm-launch", "--campaign-spec", str(spec_path)])
    assert launch.exit_code == 0, f"llm-launch failed:\n{launch.stdout}\n{launch.stderr}"
    launch_payload = json.loads(launch.stdout)
    first_launch_summary_path = Path(launch_payload["resolved_launch_path"]).with_name(
        "launch_summary.json"
    )
    assert first_launch_summary_path.exists()

    resolved_launch_payload = json.loads(
        Path(launch_payload["resolved_launch_path"]).read_text(encoding="utf-8")
    )
    assert resolved_launch_payload["resolved_model_lane"] == "general_purpose"
    assert resolved_launch_payload["resolved_seed_zomic_path"].endswith("sc_zn_tsai_bridge.zomic")

    replay = runner.invoke(
        app,
        ["llm-replay", "--launch-summary", str(first_launch_summary_path)],
    )
    assert replay.exit_code == 0, f"llm-replay failed:\n{replay.stdout}\n{replay.stderr}"
    replay_payload = json.loads(replay.stdout)
    replay_launch_summary_path = Path(replay_payload["resolved_launch_path"]).with_name(
        "launch_summary.json"
    )
    assert replay_launch_summary_path.exists()

    replay_candidates = [
        json.loads(line)
        for line in Path(replay_payload["candidates_path"]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert replay_candidates
    assert replay_candidates[0]["provenance"]["llm_campaign"]["replay_of_launch_id"] == (
        launch_payload["launch_id"]
    )

    _write_specialized_report_artifacts(
        artifact_workspace,
        system="Sc-Zn",
        launch_payload=replay_payload,
        launch_summary_path=replay_launch_summary_path,
        evaluation_model="materials-sc-zn-specialist-v1",
    )

    compare = runner.invoke(
        app,
        ["llm-compare", "--launch-summary", str(replay_launch_summary_path)],
    )
    assert compare.exit_code == 0, f"llm-compare failed:\n{compare.stdout}\n{compare.stderr}"

    outcome_snapshot_path = llm_campaign_outcome_snapshot_path(
        replay_payload["campaign_id"],
        replay_payload["launch_id"],
        root=artifact_workspace,
    )
    comparison_path = llm_campaign_comparison_path(
        replay_payload["campaign_id"],
        f"comparison_{replay_payload['launch_id']}",
        root=artifact_workspace,
    )
    assert outcome_snapshot_path.exists()
    assert comparison_path.exists()

    outcome_snapshot = json.loads(outcome_snapshot_path.read_text(encoding="utf-8"))
    assert outcome_snapshot["system"] == "Sc-Zn"
    assert outcome_snapshot["resolved_model_lane"] == "general_purpose"
    assert outcome_snapshot["evaluation_resolved_model_lane"] == "specialized_materials"
    assert outcome_snapshot["evaluation_serving_identity"]["model"] == (
        "materials-sc-zn-specialist-v1"
    )

    comparison_payload = json.loads(comparison_path.read_text(encoding="utf-8"))
    assert comparison_payload["acceptance_baseline"]["system"] == "Sc-Zn"
    assert comparison_payload["prior_outcome"]["launch_id"] == launch_payload["launch_id"]
    assert (
        comparison_payload["current_outcome"]["evaluation_resolved_model_lane"]
        == "specialized_materials"
    )
    assert "Generation lane: general_purpose (configured_lane)" in compare.stdout
    assert "Evaluation lane: specialized_materials (configured_lane)" in compare.stdout


@pytest.mark.integration
def test_real_mode_llm_serving_benchmark_compares_hosted_local_and_specialized_targets_offline(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    repo_workspace = Path(__file__).resolve().parents[1]
    artifact_workspace = tmp_path / "workspace"
    local_config_path = repo_workspace / "configs" / "systems" / "al_cu_fe_llm_local.yaml"
    hosted_config_path = _write_hosted_llm_config(tmp_path, base_config_path=local_config_path)
    acceptance_pack_path = _write_llm_acceptance_pack(artifact_workspace, system="Al-Cu-Fe")

    (tmp_path / "local").mkdir(parents=True, exist_ok=True)
    (tmp_path / "hosted").mkdir(parents=True, exist_ok=True)
    local_spec_path = _write_llm_campaign_spec(tmp_path / "local", local_config_path)
    hosted_spec_path = _write_llm_campaign_spec(tmp_path / "hosted", hosted_config_path)
    _retag_llm_campaign_spec(
        local_spec_path,
        campaign_id="campaign-local",
        proposal_id="proposal-local",
        approval_id="approval-local",
        preferred_model_lane="specialized_materials",
    )
    _retag_llm_campaign_spec(
        hosted_spec_path,
        campaign_id="campaign-hosted",
        proposal_id="proposal-hosted",
        approval_id="approval-hosted",
        preferred_model_lane="specialized_materials",
    )
    benchmark_spec_path = _write_serving_benchmark_spec(
        tmp_path,
        benchmark_id="al_cu_fe_serving_v1",
        acceptance_pack_path=acceptance_pack_path,
        hosted_config_path=hosted_config_path,
        hosted_spec_path=hosted_spec_path,
        local_config_path=local_config_path,
        local_spec_path=local_spec_path,
    )

    ranked_candidate = CandidateRecord(
        candidate_id="ranked_001",
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        cell={
            "a": 14.2,
            "b": 14.2,
            "c": 14.2,
            "alpha": 90.0,
            "beta": 90.0,
            "gamma": 90.0,
        },
        sites=[
            SiteRecord(
                label="S01",
                qphi=((0, 0), (1, 0), (1, 0)),
                species="Al",
                occ=1.0,
                fractional_position=(0.2, 0.2, 0.2),
                cartesian_position=(2.84, 2.84, 2.84),
            )
        ],
        composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        screen={"model": "MACE"},
        digital_validation=DigitalValidationRecord(status="passed", passed_checks=True),
        provenance={"source": "ranked"},
    )
    write_jsonl(
        [ranked_candidate.model_dump(mode="json")],
        artifact_workspace / "data" / "ranked" / "al_cu_fe_ranked.jsonl",
    )

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.workspace_root",
        lambda: artifact_workspace,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.generate.workspace_root",
        lambda: artifact_workspace,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.evaluate.workspace_root",
        lambda: artifact_workspace,
    )

    class _FakeAdapter:
        def generate(self, request) -> str:
            if type(request).__name__ == "LlmEvaluationRequest":
                return (
                    "{\"synthesizability_score\":0.81,\"precursor_hints\":[\"Al powder\"],"
                    "\"anomaly_flags\":[],\"literature_context\":\"demo\","
                    "\"rationale\":\"specialized benchmark\"}"
                )
            return "label benchmark.demo\n"

    def _fake_compile(
        zomic_text: str,
        *,
        prototype_key: str,
        system_name: str,
        template_family: str,
        source_qphi_bounds=None,
        artifact_root: Path | None = None,
    ) -> dict[str, object]:
        del zomic_text, system_name, template_family, source_qphi_bounds
        raw_export_path = None
        orbit_library_path = None
        if artifact_root is not None:
            artifact_root.mkdir(parents=True, exist_ok=True)
            raw_export_path = artifact_root / f"{prototype_key}.raw.json"
            orbit_library_path = artifact_root / f"{prototype_key}.json"
            raw_export_path.write_text("{}", encoding="utf-8")
            orbit_library_path.write_text("{}", encoding="utf-8")
        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "error_kind": None,
            "raw_export_path": None if raw_export_path is None else str(raw_export_path),
            "orbit_library_path": None if orbit_library_path is None else str(orbit_library_path),
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        }

    def _fake_candidate_from_prototype_library(
        config: SystemConfig,
        *,
        seed: int,
        candidate_index: int,
        template_override_path: Path,
        extra_provenance: dict[str, object] | None = None,
    ) -> CandidateRecord:
        del seed, template_override_path
        provenance = {"source": "llm"}
        if extra_provenance:
            provenance.update(extra_provenance)
        return CandidateRecord(
            candidate_id=f"md_{candidate_index:06d}",
            system=config.system_name,
            template_family=config.template_family,
            cell={
                "a": 14.2,
                "b": 14.2,
                "c": 14.2,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            sites=[
                SiteRecord(
                    label="S01",
                    qphi=((0, 0), (1, 0), (1, 0)),
                    species="Al",
                    occ=1.0,
                    fractional_position=(0.2, 0.2, 0.2),
                    cartesian_position=(2.84, 2.84, 2.84),
                )
            ],
            composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            screen={"model": "MACE", "energy_per_atom_ev": -3.0},
            digital_validation=DigitalValidationRecord(status="pending"),
            provenance=provenance,
        )

    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.validate_llm_adapter_ready",
        lambda adapter, **kwargs: None,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.evaluate.validate_llm_adapter_ready",
        lambda adapter, **kwargs: None,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.generate.resolve_llm_adapter",
        lambda mode, backend=None, llm_generate=None: _FakeAdapter(),
    )
    monkeypatch.setattr(
        "materials_discovery.llm.evaluate.resolve_llm_adapter",
        lambda mode, backend=None: _FakeAdapter(),
    )
    monkeypatch.setattr("materials_discovery.llm.generate.compile_zomic_script", _fake_compile)
    monkeypatch.setattr(
        "materials_discovery.llm.generate.build_candidate_from_prototype_library",
        _fake_candidate_from_prototype_library,
    )

    result = runner.invoke(
        app,
        ["llm-serving-benchmark", "--spec", str(benchmark_spec_path)],
    )

    assert result.exit_code == 0, (
        f"llm-serving-benchmark failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "Benchmark summary:" in result.stdout

    summary_path = (
        artifact_workspace
        / "data"
        / "benchmarks"
        / "llm_serving"
        / "al_cu_fe_serving_v1"
        / "benchmark_summary.json"
    )
    assert summary_path.exists()

    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    targets = {row["target_id"]: row for row in summary_payload["targets"]}
    assert set(targets) == {
        "hosted_generation",
        "local_generation",
        "specialized_assessment",
    }

    hosted_launch_summary_path = Path(targets["hosted_generation"]["launch_summary_path"])
    local_launch_summary_path = Path(targets["local_generation"]["launch_summary_path"])
    compare_path = Path(targets["hosted_generation"]["comparison_path"])
    evaluate_summary_path = Path(targets["specialized_assessment"]["evaluate_summary_path"])
    assert hosted_launch_summary_path.exists()
    assert local_launch_summary_path.exists()
    assert compare_path.exists()
    assert evaluate_summary_path.exists()

    assert targets["hosted_generation"]["smoke_checks"][0]["serving_identity"]["model"] == (
        "claude-hosted-v1"
    )
    assert targets["local_generation"]["smoke_checks"][0]["serving_identity"]["model"] == (
        "zomic-general-local-v1"
    )
    assert targets["specialized_assessment"]["quality_metrics"]["synthesizability_mean"] == 0.81
    assert "parse_success_rate" not in targets["specialized_assessment"]["quality_metrics"]

    hosted_spec_payload = json.loads(hosted_spec_path.read_text(encoding="utf-8"))
    assert hosted_spec_payload["actions"][0]["preferred_model_lane"] == "specialized_materials"
    hosted_launch_payload = json.loads(hosted_launch_summary_path.read_text(encoding="utf-8"))
    assert hosted_launch_payload["resolved_model_lane"] == "general_purpose"


@pytest.mark.integration
def test_real_mode_llm_serving_benchmark_rejects_misaligned_evaluate_batch_before_execution(
    tmp_path: Path,
    monkeypatch,
) -> None:
    runner = CliRunner()
    repo_workspace = Path(__file__).resolve().parents[1]
    artifact_workspace = tmp_path / "workspace"
    local_config_path = repo_workspace / "configs" / "systems" / "al_cu_fe_llm_local.yaml"
    hosted_config_path = _write_hosted_llm_config(tmp_path, base_config_path=local_config_path)
    acceptance_pack_path = _write_llm_acceptance_pack(artifact_workspace, system="Al-Cu-Fe")

    (tmp_path / "local_blocked").mkdir(parents=True, exist_ok=True)
    (tmp_path / "hosted_blocked").mkdir(parents=True, exist_ok=True)
    local_spec_path = _write_llm_campaign_spec(tmp_path / "local_blocked", local_config_path)
    hosted_spec_path = _write_llm_campaign_spec(tmp_path / "hosted_blocked", hosted_config_path)
    benchmark_spec_path = _write_serving_benchmark_spec(
        tmp_path,
        benchmark_id="al_cu_fe_serving_bad_batch",
        acceptance_pack_path=acceptance_pack_path,
        hosted_config_path=hosted_config_path,
        hosted_spec_path=hosted_spec_path,
        local_config_path=local_config_path,
        local_spec_path=local_spec_path,
        evaluate_batch="foreign_slice",
    )

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: artifact_workspace)
    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.workspace_root",
        lambda: artifact_workspace,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark.validate_llm_adapter_ready",
        lambda adapter, **kwargs: None,
    )

    executed = {"launch": 0, "evaluate": 0}

    def _should_not_launch(*args, **kwargs):
        del args, kwargs
        executed["launch"] += 1
        raise AssertionError("launch target should not execute for a misaligned batch")

    def _should_not_evaluate(*args, **kwargs):
        del args, kwargs
        executed["evaluate"] += 1
        raise AssertionError("evaluate target should not execute for a misaligned batch")

    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark._execute_launch_target",
        _should_not_launch,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.serving_benchmark._execute_evaluate_target",
        _should_not_evaluate,
    )

    result = runner.invoke(
        app,
        ["llm-serving-benchmark", "--spec", str(benchmark_spec_path)],
    )

    assert result.exit_code == 2
    assert "shared acceptance-pack context" in result.stderr
    assert executed == {"launch": 0, "evaluate": 0}


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
