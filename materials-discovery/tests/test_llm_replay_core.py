from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from materials_discovery.common.io import load_yaml, write_json_object, write_jsonl
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.checkpoints import (
    load_registered_checkpoint,
    register_llm_checkpoint,
    retire_checkpoint,
)
from materials_discovery.llm.replay import (
    build_replay_campaign_metadata,
    build_replay_config,
    build_replay_serving_identity,
    load_campaign_launch_bundle,
)
from materials_discovery.llm.schema import (
    LlmAcceptanceSystemMetrics,
    LlmCampaignComparisonResult,
    LlmCampaignLaunchSummary,
    LlmCampaignOutcomeSnapshot,
    LlmCampaignResolvedLaunch,
    LlmServingIdentity,
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
import yaml


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _system_config(config_name: str = "al_cu_fe_llm_mock.yaml") -> tuple[SystemConfig, Path]:
    config_path = _workspace() / "configs" / "systems" / config_name
    return SystemConfig.model_validate(load_yaml(config_path)), config_path


def _register_checkpoint_for_test(
    root: Path,
    *,
    checkpoint_id: str,
    model: str,
    checkpoint_family: str | None = None,
) -> None:
    lineage_dir = root / "lineage"
    lineage_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "adapter_manifest.json",
        "corpus_manifest.json",
        "eval_manifest.json",
        "acceptance_pack.json",
    ):
        (lineage_dir / name).write_text("{}", encoding="utf-8")
    spec_path = root / f"{checkpoint_id}.yaml"
    spec_path.write_text(
        yaml.safe_dump(
            {
                "checkpoint_id": checkpoint_id,
                **(
                    {}
                    if checkpoint_family is None
                    else {"checkpoint_family": checkpoint_family}
                ),
                "system": "Al-Cu-Fe",
                "template_family": "icosahedral_approximant_1_1",
                "adapter": "openai_compat_v1",
                "provider": "openai_compat",
                "model": model,
                "local_model_path": f"/opt/models/{model}",
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
    register_llm_checkpoint(spec_path, root=root)


def _write_retirement_spec(
    root: Path,
    *,
    checkpoint_family: str,
    checkpoint_id: str,
    expected_revision: int,
) -> Path:
    spec_path = root / f"{checkpoint_id}-retirement.yaml"
    spec_path.write_text(
        yaml.safe_dump(
            {
                "checkpoint_family": checkpoint_family,
                "checkpoint_id": checkpoint_id,
                "reason": "superseded",
                "expected_revision": expected_revision,
                "note": "Illustrative repo-relative placeholder retirement example.",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return spec_path


def _write_launch_bundle(
    root: Path,
    *,
    launch_id: str = "launch-001",
    created_at_utc: str = "2026-04-04T18:00:00Z",
    config_name: str = "al_cu_fe_llm_mock.yaml",
    requested_model_lanes: list[str] | None = None,
    resolved_model_lane: str | None = None,
    resolved_model_lane_source: str = "configured_lane",
    serving_identity: dict[str, object] | LlmServingIdentity | None = None,
) -> Path:
    config, config_path = _system_config(config_name)
    config_hash = config_sha256(config)
    requested_model_lanes = ["general_purpose"] if requested_model_lanes is None else requested_model_lanes
    identity_model = (
        None
        if serving_identity is None
        else (
            serving_identity
            if isinstance(serving_identity, LlmServingIdentity)
            else LlmServingIdentity.model_validate(serving_identity)
        )
    )
    resolved_model_lane = (
        "general_purpose"
        if resolved_model_lane is None and identity_model is None
        else (
            identity_model.resolved_model_lane
            if resolved_model_lane is None and identity_model is not None
            else resolved_model_lane
        )
    )
    adapter = config.backend.llm_adapter or "llm_fixture_v1"
    provider = config.backend.llm_provider or "mock"
    model = config.backend.llm_model or "fixture"
    if identity_model is not None:
        adapter = identity_model.adapter
        provider = identity_model.provider
        model = identity_model.model
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
                "adapter_key": adapter,
                "provider": provider,
                "model": model,
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
            "adapter_key": adapter,
            "provider": provider,
            "model": model,
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
            "requested_model_lanes": requested_model_lanes,
            "resolved_model_lane": resolved_model_lane,
            "resolved_model_lane_source": resolved_model_lane_source,
            **(
                {}
                if identity_model is None
                else {"serving_identity": identity_model.model_dump(mode="json")}
            ),
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
            "requested_model_lanes": requested_model_lanes,
            "resolved_model_lane": resolved_model_lane,
            "resolved_model_lane_source": resolved_model_lane_source,
            "resolved_adapter": adapter,
            "resolved_provider": provider,
            "resolved_model": model,
            **(
                {}
                if identity_model is None
                else {"serving_identity": identity_model.model_dump(mode="json")}
            ),
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
            "requested_model_lanes": requested_model_lanes,
            "resolved_model_lane": resolved_model_lane,
            "resolved_model_lane_source": resolved_model_lane_source,
            **(
                {}
                if identity_model is None
                else {"serving_identity": identity_model.model_dump(mode="json")}
            ),
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


def test_build_replay_config_tolerates_transport_drift_for_local_serving_identity(
    tmp_path: Path,
) -> None:
    launch_summary_path = _write_launch_bundle(
        tmp_path,
        config_name="al_cu_fe_llm_local.yaml",
        requested_model_lanes=["specialized_materials"],
        resolved_model_lane="specialized_materials",
        resolved_model_lane_source="configured_lane",
        serving_identity={
            "requested_model_lane": "specialized_materials",
            "resolved_model_lane": "specialized_materials",
            "resolved_model_lane_source": "configured_lane",
            "adapter": "openai_compat_v1",
            "provider": "openai_compat",
            "model": "materials-al-cu-fe-specialist-v1",
            "effective_api_base": "http://localhost:8000",
            "checkpoint_id": "ckpt-al-cu-fe-specialist",
            "model_revision": "local-dev-2026-04-05",
            "local_model_path": "/opt/models/materials-al-cu-fe-specialist-v1",
        },
    )
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
    current_config, _ = _system_config("al_cu_fe_llm_local.yaml")
    assert current_config.llm_generate is not None
    current_config.llm_generate.model_lanes["specialized_materials"].api_base = "http://localhost:8001"
    current_config.llm_generate.model_lanes[
        "specialized_materials"
    ].model_revision = "local-dev-2026-04-06"
    current_config.llm_generate.model_lanes[
        "specialized_materials"
    ].local_model_path = "/srv/models/materials-al-cu-fe-specialist-v1"

    replay_config = build_replay_config(bundle, current_config)
    replay_identity = build_replay_serving_identity(bundle, current_config)

    assert replay_config.backend.llm_adapter == "openai_compat_v1"
    assert replay_config.backend.llm_provider == "openai_compat"
    assert replay_config.backend.llm_model == "materials-al-cu-fe-specialist-v1"
    assert replay_config.backend.llm_api_base == "http://localhost:8001"
    assert replay_identity.effective_api_base == "http://localhost:8001"
    assert replay_identity.checkpoint_id == "ckpt-al-cu-fe-specialist"
    assert replay_identity.local_model_path == "/srv/models/materials-al-cu-fe-specialist-v1"


def test_build_replay_config_rejects_hard_local_identity_drift(
    tmp_path: Path,
) -> None:
    launch_summary_path = _write_launch_bundle(
        tmp_path,
        config_name="al_cu_fe_llm_local.yaml",
        requested_model_lanes=["specialized_materials"],
        resolved_model_lane="specialized_materials",
        resolved_model_lane_source="configured_lane",
        serving_identity={
            "requested_model_lane": "specialized_materials",
            "resolved_model_lane": "specialized_materials",
            "resolved_model_lane_source": "configured_lane",
            "adapter": "openai_compat_v1",
            "provider": "openai_compat",
            "model": "materials-al-cu-fe-specialist-v1",
            "effective_api_base": "http://localhost:8000",
            "checkpoint_id": "ckpt-al-cu-fe-specialist",
        },
    )
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
    current_config, _ = _system_config("al_cu_fe_llm_local.yaml")
    assert current_config.llm_generate is not None
    current_config.llm_generate.model_lanes["specialized_materials"].checkpoint_id = (
        "ckpt-al-cu-fe-specialist-v2"
    )

    with pytest.raises(ValueError, match="hard serving identity drift"):
        build_replay_config(bundle, current_config)


def test_build_replay_config_rejects_registered_checkpoint_fingerprint_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)
    _register_checkpoint_for_test(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
        model="zomic-al-cu-fe-adapted-v1",
    )

    launch_summary_path = _write_launch_bundle(
        tmp_path,
        config_name="al_cu_fe_llm_local.yaml",
        requested_model_lanes=["general_purpose"],
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        serving_identity={
            "requested_model_lane": "general_purpose",
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
            "adapter": "openai_compat_v1",
            "provider": "openai_compat",
            "model": "zomic-al-cu-fe-adapted-v1",
            "effective_api_base": "http://localhost:8000",
            "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
            "model_revision": "adapted-dev-2026-04-05",
            "local_model_path": "/opt/models/zomic-al-cu-fe-adapted-v1",
            "checkpoint_lineage": {
                "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
                "registration_path": "data/llm_checkpoints/ckpt-al-cu-fe-zomic-adapted/registration.json",
                "fingerprint": "stale-fingerprint",
                "base_model": "zomic-general-local-v1",
                "base_model_revision": "local-dev-2026-04-05",
                "adaptation_method": "lora",
                "adaptation_artifact_path": "lineage/adapter_manifest.json",
                "corpus_manifest_path": "lineage/corpus_manifest.json",
                "eval_set_manifest_path": "lineage/eval_manifest.json",
                "acceptance_pack_path": "lineage/acceptance_pack.json",
            },
        },
    )
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
    current_config, _ = _system_config("al_cu_fe_llm_local.yaml")
    assert current_config.llm_generate is not None
    current_config.llm_generate.model_lanes["general_purpose"].model = "zomic-al-cu-fe-adapted-v1"
    current_config.llm_generate.model_lanes["general_purpose"].api_base = "http://localhost:8001"
    current_config.llm_generate.model_lanes["general_purpose"].checkpoint_id = (
        "ckpt-al-cu-fe-zomic-adapted"
    )
    current_config.llm_generate.model_lanes["general_purpose"].require_checkpoint_registration = True
    current_config.llm_generate.model_lanes["general_purpose"].model_revision = None
    current_config.llm_generate.model_lanes["general_purpose"].local_model_path = None

    with pytest.raises(ValueError, match="fingerprint drift"):
        build_replay_config(bundle, current_config)


def test_build_replay_config_keeps_retired_checkpoint_replayable_by_fingerprint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)
    _register_checkpoint_for_test(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
        checkpoint_family="adapted-al-cu-fe",
        model="zomic-al-cu-fe-adapted-v1",
    )
    registration, _ = load_registered_checkpoint("ckpt-al-cu-fe-zomic-adapted", root=tmp_path)

    launch_summary_path = _write_launch_bundle(
        tmp_path,
        config_name="al_cu_fe_llm_adapted.yaml",
        requested_model_lanes=["general_purpose"],
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        serving_identity={
            "requested_model_lane": "general_purpose",
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
            "adapter": "openai_compat_v1",
            "provider": "openai_compat",
            "model": "zomic-al-cu-fe-adapted-v1",
            "effective_api_base": "http://localhost:8000",
            "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
            "model_revision": "adapted-dev-2026-04-05",
            "local_model_path": "/opt/models/zomic-al-cu-fe-adapted-v1",
            "checkpoint_lineage": {
                "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
                "checkpoint_family": "adapted-al-cu-fe",
                "registration_path": "data/llm_checkpoints/ckpt-al-cu-fe-zomic-adapted/registration.json",
                "fingerprint": registration.fingerprint,
                "base_model": "zomic-general-local-v1",
                "base_model_revision": "local-dev-2026-04-05",
                "adaptation_method": "lora",
                "adaptation_artifact_path": "lineage/adapter_manifest.json",
                "corpus_manifest_path": "lineage/corpus_manifest.json",
                "eval_set_manifest_path": "lineage/eval_manifest.json",
                "acceptance_pack_path": "lineage/acceptance_pack.json",
            },
        },
    )
    retire_checkpoint(
        _write_retirement_spec(
            tmp_path,
            checkpoint_family="adapted-al-cu-fe",
            checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
            expected_revision=1,
        ),
        root=tmp_path,
    )
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
    current_config, _ = _system_config("al_cu_fe_llm_adapted.yaml")
    assert current_config.llm_generate is not None
    current_config.llm_generate.model_lanes["general_purpose"].checkpoint_family = (
        "adapted-al-cu-fe"
    )

    replay_config = build_replay_config(bundle, current_config)
    replay_identity = build_replay_serving_identity(bundle, current_config)

    assert replay_config.backend.llm_model == "zomic-al-cu-fe-adapted-v1"
    assert replay_identity.checkpoint_id == "ckpt-al-cu-fe-zomic-adapted"
    assert replay_identity.checkpoint_lineage is not None
    assert replay_identity.checkpoint_lineage.fingerprint == registration.fingerprint
    assert replay_identity.checkpoint_lineage.checkpoint_family == "adapted-al-cu-fe"


def test_committed_local_serving_configs_validate_without_live_server() -> None:
    for config_name in ("al_cu_fe_llm_local.yaml", "sc_zn_llm_local.yaml"):
        config, _ = _system_config(config_name)
        assert config.backend.llm_adapter == "openai_compat_v1"
        assert config.backend.llm_api_base == "http://localhost:8000"
        assert config.llm_generate is not None
        assert config.llm_generate.default_model_lane == "general_purpose"
        assert config.llm_generate.fallback_model_lane == "general_purpose"
        assert "specialized_materials" in config.llm_generate.model_lanes


def test_legacy_baseline_fallback_launch_bundle_still_replays(tmp_path: Path) -> None:
    launch_summary_path = _write_launch_bundle(
        tmp_path,
        requested_model_lanes=["general_purpose"],
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="baseline_fallback",
    )
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)
    current_config, _ = _system_config()

    replay_config = build_replay_config(bundle, current_config)
    replay_identity = build_replay_serving_identity(bundle, current_config)

    assert replay_config.backend.llm_adapter == "llm_fixture_v1"
    assert replay_config.backend.llm_provider == "mock"
    assert replay_config.backend.llm_model == "fixture-al-cu-fe-v1"
    assert replay_identity.resolved_model_lane_source == "backend_default"
