from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from materials_discovery.common.io import load_yaml, write_json_object, write_jsonl
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.replay import (
    build_replay_campaign_metadata,
    build_replay_config,
    load_campaign_launch_bundle,
)
from materials_discovery.llm.schema import (
    LlmAcceptanceSystemMetrics,
    LlmCampaignComparisonResult,
    LlmCampaignLaunchSummary,
    LlmCampaignOutcomeSnapshot,
    LlmCampaignResolvedLaunch,
)
from materials_discovery.llm.storage import (
    llm_acceptance_pack_path,
    llm_campaign_comparison_path,
    llm_campaign_comparisons_dir,
    llm_campaign_launch_summary_path,
    llm_campaign_outcome_snapshot_path,
    llm_campaign_resolved_launch_path,
    llm_campaign_spec_path,
)


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _system_config(config_name: str = "al_cu_fe_llm_mock.yaml") -> tuple[SystemConfig, Path]:
    config_path = _workspace() / "configs" / "systems" / config_name
    return SystemConfig.model_validate(load_yaml(config_path)), config_path


def _write_launch_bundle(
    root: Path,
    *,
    launch_id: str = "launch-001",
    created_at_utc: str = "2026-04-04T18:00:00Z",
) -> Path:
    config, config_path = _system_config()
    config_hash = config_sha256(config)
    acceptance_pack_path = llm_acceptance_pack_path("pack_v1", root=root)
    write_json_object(
        {
            "schema_version": "llm-acceptance-pack/v1",
            "pack_id": "pack_v1",
            "created_at_utc": "2026-04-04T12:00:00Z",
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
                LlmAcceptanceSystemMetrics(
                    system="Al-Cu-Fe",
                    generate_comparison_path="data/benchmarks/llm_generate/al_cu_fe.json",
                    pipeline_comparison_path="data/benchmarks/llm_pipeline/al_cu_fe.json",
                    parse_success_rate=0.8,
                    compile_success_rate=0.75,
                    generation_success_rate=0.4,
                    shortlist_pass_rate=0.12,
                    validation_pass_rate=0.05,
                    novelty_score_mean=0.3,
                    synthesizability_mean=0.6,
                    report_release_gate_ready=False,
                    failing_metrics=["compile_success_rate"],
                    passed=False,
                ).model_dump(mode="json")
            ],
            "overall_passed": False,
        },
        acceptance_pack_path,
    )

    campaign_spec_path = llm_campaign_spec_path("campaign-001", root=root)
    write_json_object(
        {
            "schema_version": "llm-campaign-spec/v1",
            "campaign_id": "campaign-001",
            "proposal_id": "proposal-001",
            "approval_id": "approval-001",
            "system": "Al-Cu-Fe",
            "created_at_utc": "2026-04-04T17:00:00Z",
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
                "system_config_hash": config_hash,
                "system": "Al-Cu-Fe",
                "template_family": config.template_family,
                "default_count": 2,
                "composition_bounds": {
                    species: bound.model_dump(mode="json")
                    for species, bound in config.composition_bounds.items()
                },
                "prompt_template": "zomic_generate_v1",
                "example_pack_path": str(root / "data" / "llm_eval_sets" / "demo" / "eval_set.jsonl"),
                "max_conditioning_examples": 3,
                "seed_zomic_path": str(root / "designs" / "demo.zomic"),
            },
            "lineage": {
                "acceptance_pack_path": str(acceptance_pack_path),
                "eval_set_manifest_path": None,
                "proposal_path": "data/benchmarks/llm_acceptance/pack_v1/proposals/proposal-001.json",
                "approval_path": "data/benchmarks/llm_acceptance/pack_v1/approvals/approval-001.json",
                "source_system_config_path": str(config_path),
                "source_system_config_hash": config_hash,
            },
        },
        campaign_spec_path,
    )

    run_dir = root / "data" / "llm_runs" / f"run_{launch_id}"
    prompt_path = run_dir / "prompt.json"
    run_manifest_path = run_dir / "run_manifest.json"
    attempts_path = run_dir / "attempts.jsonl"
    compile_results_path = run_dir / "compile_results.jsonl"
    write_json_object(
        {
            "request_hash": f"request-{launch_id}",
            "prompt_template": "zomic_generate_v1",
            "request": {
                "system": "Al-Cu-Fe",
                "template_family": config.template_family,
                "composition_bounds": {
                    species: bound.model_dump(mode="json")
                    for species, bound in config.composition_bounds.items()
                },
                "prompt_text": "Generate two parser-safe candidates.",
                "temperature": 0.15,
                "max_tokens": 900,
                "seed_zomic_path": str(root / "designs" / "demo.zomic"),
                "example_pack_path": str(root / "data" / "llm_eval_sets" / "demo" / "eval_set.jsonl"),
                "prompt_instruction_deltas": ["Prefer parser-safe symmetry annotations."],
                "conditioning_example_ids": ["eval_001", "eval_002"],
            },
            "prompt_text": "Generate two parser-safe candidates.",
            "conditioning_example_ids": ["eval_001", "eval_002"],
        },
        prompt_path,
    )
    write_jsonl(
        [
            {
                "schema_version": "llm-generation-attempt/v1",
                "attempt_id": "llm_attempt_0001",
                "adapter_key": "llm_fixture_v1",
                "provider": "mock",
                "model": "fixture-al-cu-fe-v1",
                "temperature": 0.15,
                "prompt_path": str(prompt_path),
                "raw_completion_path": str(run_dir / "raw" / "llm_attempt_0001.zomic"),
                "parse_status": "passed",
                "compile_status": "passed",
                "error_kind": None,
                "error_message": None,
            }
        ],
        attempts_path,
    )
    write_jsonl(
        [
            {
                "schema_version": "llm-generation-result/v1",
                "attempt_id": "llm_attempt_0001",
                "candidate_id": "cand-001",
                "orbit_library_path": str(run_dir / "compiled" / "orbit_library.json"),
                "raw_export_path": str(run_dir / "compiled" / "export.json"),
                "parse_status": "passed",
                "compile_status": "passed",
                "passed": True,
            },
            {
                "schema_version": "llm-generation-result/v1",
                "attempt_id": "llm_attempt_0002",
                "candidate_id": None,
                "orbit_library_path": None,
                "raw_export_path": None,
                "parse_status": "passed",
                "compile_status": "failed",
                "passed": False,
            },
        ],
        compile_results_path,
    )
    write_json_object(
        {
            "schema_version": "llm-run-manifest/v1",
            "run_id": run_dir.name,
            "system": "Al-Cu-Fe",
            "adapter_key": "llm_fixture_v1",
            "provider": "mock",
            "model": "fixture-al-cu-fe-v1",
            "prompt_template": "zomic_generate_v1",
            "attempt_count": 2,
            "requested_count": 2,
            "generated_count": 1,
            "prompt_path": str(prompt_path),
            "attempts_path": str(attempts_path),
            "compile_results_path": str(compile_results_path),
            "created_at_utc": created_at_utc,
            "example_pack_path": str(root / "data" / "llm_eval_sets" / "demo" / "eval_set.jsonl"),
            "prompt_instruction_deltas": ["Prefer parser-safe symmetry annotations."],
            "conditioning_example_ids": ["eval_001", "eval_002"],
            "campaign_id": "campaign-001",
            "launch_id": launch_id,
            "campaign_spec_path": str(campaign_spec_path),
            "proposal_id": "proposal-001",
            "approval_id": "approval-001",
            "requested_model_lanes": ["general_purpose"],
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
            "launch_summary_path": str(
                llm_campaign_launch_summary_path("campaign-001", launch_id, root=root)
            ),
            "temperature": 0.15,
            "max_tokens": 900,
            "max_attempts": 4,
            "seed_zomic_path": str(root / "designs" / "demo.zomic"),
        },
        run_manifest_path,
    )

    resolved_launch_path = llm_campaign_resolved_launch_path("campaign-001", launch_id, root=root)
    write_json_object(
        {
            "launch_id": launch_id,
            "campaign_id": "campaign-001",
            "campaign_spec_path": str(campaign_spec_path),
            "system_config_path": str(config_path),
            "system_config_hash": config_hash,
            "requested_model_lanes": ["general_purpose"],
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
            "resolved_adapter": "llm_fixture_v1",
            "resolved_provider": "mock",
            "resolved_model": "fixture-al-cu-fe-v1",
            "prompt_instruction_deltas": ["Prefer parser-safe symmetry annotations."],
            "resolved_composition_bounds": {
                species: bound.model_dump(mode="json")
                for species, bound in config.composition_bounds.items()
            },
            "resolved_example_pack_path": str(root / "data" / "llm_eval_sets" / "demo" / "eval_set.jsonl"),
            "resolved_seed_zomic_path": str(root / "designs" / "demo.zomic"),
            "effective_candidates_path": str(root / "data" / "candidates" / "al_cu_fe_candidates.jsonl"),
            "output_override_used": False,
        },
        resolved_launch_path,
    )

    launch_summary_path = llm_campaign_launch_summary_path("campaign-001", launch_id, root=root)
    write_json_object(
        {
            "launch_id": launch_id,
            "campaign_id": "campaign-001",
            "campaign_spec_path": str(campaign_spec_path),
            "proposal_id": "proposal-001",
            "approval_id": "approval-001",
            "system": "Al-Cu-Fe",
            "status": "succeeded",
            "created_at_utc": created_at_utc,
            "requested_count": 2,
            "requested_model_lanes": ["general_purpose"],
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
            "resolved_launch_path": str(resolved_launch_path),
            "run_manifest_path": str(run_manifest_path),
            "llm_generate_manifest_path": str(
                root / "data" / "manifests" / "al_cu_fe_llm_generate_manifest.json"
            ),
            "candidates_path": str(root / "data" / "candidates" / "al_cu_fe_candidates.jsonl"),
        },
        launch_summary_path,
    )
    return launch_summary_path


def test_launch_models_accept_additive_replay_fields_and_storage_paths(tmp_path: Path) -> None:
    resolved = LlmCampaignResolvedLaunch(
        launch_id="launch-002",
        campaign_id="campaign-001",
        campaign_spec_path="data/llm_campaigns/campaign-001/campaign_spec.json",
        system_config_path="configs/systems/al_cu_fe_llm_mock.yaml",
        system_config_hash="hash",
        requested_model_lanes=["general_purpose"],
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        resolved_adapter="llm_fixture_v1",
        resolved_provider="mock",
        resolved_model="fixture-al-cu-fe-v1",
        prompt_instruction_deltas=["Prefer parser-safe symmetry annotations."],
        resolved_composition_bounds={
            "Al": {"min": 0.6, "max": 0.8},
            "Cu": {"min": 0.1, "max": 0.25},
            "Fe": {"min": 0.05, "max": 0.2},
        },
        replay_of_launch_id="launch-001",
        replay_of_launch_summary_path="data/llm_campaigns/campaign-001/launches/launch-001/launch_summary.json",
        current_system_config_hash="current-hash",
    )
    summary = LlmCampaignLaunchSummary(
        launch_id="launch-002",
        campaign_id="campaign-001",
        campaign_spec_path="data/llm_campaigns/campaign-001/campaign_spec.json",
        proposal_id="proposal-001",
        approval_id="approval-001",
        system="Al-Cu-Fe",
        status="succeeded",
        created_at_utc="2026-04-04T18:00:00Z",
        requested_count=2,
        requested_model_lanes=["general_purpose"],
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        resolved_launch_path="data/llm_campaigns/campaign-001/launches/launch-002/resolved_launch.json",
        replay_of_launch_id="launch-001",
        replay_of_launch_summary_path="data/llm_campaigns/campaign-001/launches/launch-001/launch_summary.json",
        current_system_config_hash="current-hash",
    )

    assert resolved.replay_of_launch_id == "launch-001"
    assert summary.replay_of_launch_summary_path.endswith("launch_summary.json")
    assert llm_campaign_outcome_snapshot_path("campaign-001", "launch-002", root=tmp_path) == (
        tmp_path
        / "data"
        / "llm_campaigns"
        / "campaign-001"
        / "launches"
        / "launch-002"
        / "outcome_snapshot.json"
    )
    assert llm_campaign_comparisons_dir("campaign-001", root=tmp_path) == (
        tmp_path / "data" / "llm_campaigns" / "campaign-001" / "comparisons"
    )
    assert llm_campaign_comparison_path("campaign-001", "comparison_launch-002", root=tmp_path) == (
        tmp_path
        / "data"
        / "llm_campaigns"
        / "campaign-001"
        / "comparisons"
        / "comparison_launch-002.json"
    )


def test_outcome_and_comparison_models_reject_blank_and_invalid_metric_structures() -> None:
    with pytest.raises(ValidationError, match="field must not be blank"):
        LlmCampaignOutcomeSnapshot(
            campaign_id=" ",
            launch_id="launch-001",
            system="Al-Cu-Fe",
            launch_summary_path="launch_summary.json",
            campaign_spec_path="campaign_spec.json",
            acceptance_pack_path="acceptance_pack.json",
            requested_model_lanes=["general_purpose"],
            resolved_model_lane="general_purpose",
            resolved_model_lane_source="configured_lane",
            parse_success_rate=0.5,
            compile_success_rate=0.5,
            generation_success_rate=0.5,
        )

    current_outcome = LlmCampaignOutcomeSnapshot(
        campaign_id="campaign-001",
        launch_id="launch-001",
        system="Al-Cu-Fe",
        launch_summary_path="launch_summary.json",
        campaign_spec_path="campaign_spec.json",
        acceptance_pack_path="acceptance_pack.json",
        requested_model_lanes=["general_purpose"],
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        parse_success_rate=0.5,
        compile_success_rate=0.5,
        generation_success_rate=0.5,
        missing_metrics=["validation_pass_rate"],
    )

    with pytest.raises(ValidationError, match="unsupported delta metric key"):
        LlmCampaignComparisonResult(
            comparison_id="comparison_launch-001",
            campaign_id="campaign-001",
            launch_id="launch-001",
            system="Al-Cu-Fe",
            generated_at_utc="2026-04-04T18:00:00Z",
            current_outcome=current_outcome,
            acceptance_baseline=LlmAcceptanceSystemMetrics(
                system="Al-Cu-Fe",
                generate_comparison_path="generate.json",
                pipeline_comparison_path="pipeline.json",
                parse_success_rate=0.8,
                compile_success_rate=0.8,
                generation_success_rate=0.4,
                shortlist_pass_rate=0.1,
                validation_pass_rate=0.05,
                novelty_score_mean=0.3,
                synthesizability_mean=0.6,
                report_release_gate_ready=False,
                failing_metrics=[],
                passed=True,
            ),
            delta_vs_acceptance={"unknown_metric": 0.1},
        )


def test_load_campaign_launch_bundle_and_build_replay_config_preserve_recorded_runtime(
    tmp_path: Path,
) -> None:
    launch_summary_path = _write_launch_bundle(tmp_path)
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
    current_config, _ = _system_config()
    current_config.backend.llm_model = "drifted-model"
    current_config.llm_generate.temperature = 0.9
    current_config.llm_generate.max_tokens = 42
    current_config.llm_generate.max_attempts = 1
    current_config.llm_generate.example_pack_path = None
    current_config.llm_generate.seed_zomic = None
    current_config.llm_generate.max_conditioning_examples = 1

    replay_config = build_replay_config(bundle, current_config)
    replay_metadata = build_replay_campaign_metadata(bundle)

    assert replay_config.backend.llm_adapter == "llm_fixture_v1"
    assert replay_config.backend.llm_provider == "mock"
    assert replay_config.backend.llm_model == "fixture-al-cu-fe-v1"
    assert replay_config.llm_generate.prompt_template == "zomic_generate_v1"
    assert replay_config.llm_generate.temperature == pytest.approx(0.15)
    assert replay_config.llm_generate.max_tokens == 900
    assert replay_config.llm_generate.max_attempts == 4
    assert replay_config.llm_generate.example_pack_path is not None
    assert replay_config.llm_generate.seed_zomic is not None
    assert replay_config.llm_generate.max_conditioning_examples >= 3
    assert replay_metadata["replay_of_launch_id"] == "launch-001"
    assert str(launch_summary_path) == replay_metadata["replay_of_launch_summary_path"]


def test_build_replay_config_rejects_system_or_template_mismatch(tmp_path: Path) -> None:
    launch_summary_path = _write_launch_bundle(tmp_path)
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
    other_config, _ = _system_config("sc_zn_llm_mock.yaml")

    with pytest.raises(ValueError, match="same system"):
        build_replay_config(bundle, other_config)


def test_load_campaign_launch_bundle_requires_full_bundle(tmp_path: Path) -> None:
    launch_summary_path = _write_launch_bundle(tmp_path)
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
    bundle.prompt_path.unlink()

    with pytest.raises(FileNotFoundError):
        load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
