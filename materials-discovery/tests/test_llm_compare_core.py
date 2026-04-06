from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import load_json_object, load_yaml, write_json_object, write_jsonl
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.compare import (
    build_campaign_comparison,
    build_campaign_outcome_snapshot,
    find_prior_campaign_launch,
)
from materials_discovery.llm.replay import load_campaign_launch_bundle
from materials_discovery.llm.schema import LlmAcceptanceSystemMetrics
from materials_discovery.llm.storage import (
    llm_acceptance_pack_path,
    llm_campaign_comparison_path,
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
    serving_identity: dict[str, object] | None = None,
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
    write_jsonl([], attempts_path)
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
            "serving_identity": serving_identity,
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
            "serving_identity": serving_identity,
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


def _write_stage_artifacts(
    root: Path,
    *,
    launch_id: str,
    launch_summary_path: Path,
    include_validation: bool = True,
    include_report: bool = True,
    include_specialized_evaluation_lineage: bool = False,
) -> None:
    lineage = {
        "llm_campaign": {
            "campaign_id": "campaign-001",
            "launch_id": launch_id,
            "campaign_spec_path": str(
                root / "data" / "llm_campaigns" / "campaign-001" / "campaign_spec.json"
            ),
            "launch_summary_path": str(launch_summary_path),
        }
    }
    manifests_dir = root / "data" / "manifests"
    calibration_dir = root / "data" / "calibration"

    write_json_object(
        {
            "stage": "screen",
            "created_at_utc": "2026-04-04T19:00:00Z",
            "source_lineage": lineage,
        },
        manifests_dir / "al_cu_fe_screen_manifest.json",
    )
    write_json_object({"pass_rate": 0.22}, calibration_dir / "al_cu_fe_screen_calibration.json")

    if include_validation:
        write_json_object(
            {
                "stage": "hifi_validate",
                "created_at_utc": "2026-04-04T19:05:00Z",
                "source_lineage": lineage,
            },
            manifests_dir / "al_cu_fe_batch_a_hifi_validate_manifest.json",
        )
        write_json_object(
            {"pass_rate": 0.07},
            calibration_dir / "al_cu_fe_batch_a_validation_calibration.json",
        )

    write_json_object(
        {
            "stage": "hifi_rank",
            "created_at_utc": "2026-04-04T19:10:00Z",
            "source_lineage": lineage,
        },
        manifests_dir / "al_cu_fe_hifi_rank_manifest.json",
    )
    write_json_object(
        {"novelty_score_mean": 0.33},
        calibration_dir / "al_cu_fe_ranking_calibration.json",
    )

    if include_report:
        write_json_object(
            {
                "stage": "report",
                "created_at_utc": "2026-04-04T19:15:00Z",
                "source_lineage": lineage,
            },
            manifests_dir / "al_cu_fe_report_manifest.json",
        )
        write_json_object(
            {
                "llm_synthesizability_mean": 0.61,
                "release_gate_ready": True,
            },
            calibration_dir / "al_cu_fe_report_calibration.json",
        )
        report_payload = {"entries": []}
        if include_specialized_evaluation_lineage:
            report_payload["entries"] = [
                {
                    "candidate_id": "cand-001",
                    "llm_assessment": {
                        "status": "passed",
                        "run_id": "eval-demo",
                        "requested_model_lanes": ["specialized_materials"],
                        "resolved_model_lane": "specialized_materials",
                        "resolved_model_lane_source": "configured_lane",
                        "serving_identity": {
                            "requested_model_lane": "specialized_materials",
                            "resolved_model_lane": "specialized_materials",
                            "resolved_model_lane_source": "configured_lane",
                            "adapter": "openai_compat_v1",
                            "provider": "openai_compat",
                            "model": "materials-al-cu-fe-specialist-v1",
                            "effective_api_base": "http://localhost:8000",
                            "checkpoint_id": "ckpt-al-cu-fe-specialist",
                        },
                    },
                }
            ]
        write_json_object(report_payload, root / "data" / "reports" / "al_cu_fe_report.json")
        write_json_object(
            {
                "stage": "pipeline",
                "created_at_utc": "2026-04-04T19:20:00Z",
                "source_lineage": lineage,
            },
            manifests_dir / "al_cu_fe_pipeline_manifest.json",
        )


def test_build_campaign_outcome_snapshot_persists_launch_and_downstream_metrics(
    tmp_path: Path,
) -> None:
    launch_summary_path = _write_launch_bundle(tmp_path)
    _write_stage_artifacts(
        tmp_path,
        launch_id="launch-001",
        launch_summary_path=launch_summary_path,
        include_specialized_evaluation_lineage=True,
    )
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)

    snapshot = build_campaign_outcome_snapshot(bundle, root=tmp_path)
    snapshot_path = llm_campaign_outcome_snapshot_path("campaign-001", "launch-001", root=tmp_path)

    assert snapshot_path.exists()
    assert snapshot.parse_success_rate == 1.0
    assert snapshot.compile_success_rate == 0.5
    assert snapshot.generation_success_rate == 0.5
    assert snapshot.shortlist_pass_rate == 0.22
    assert snapshot.validation_pass_rate == 0.07
    assert snapshot.novelty_score_mean == 0.33
    assert snapshot.synthesizability_mean == 0.61
    assert snapshot.report_release_gate_ready is True
    assert snapshot.evaluation_requested_model_lanes == ["specialized_materials"]
    assert snapshot.evaluation_resolved_model_lane == "specialized_materials"
    assert snapshot.evaluation_resolved_model_lane_source == "configured_lane"
    assert snapshot.evaluation_serving_identity is not None
    assert snapshot.evaluation_serving_identity.model == "materials-al-cu-fe-specialist-v1"
    assert snapshot.missing_metrics == []
    assert set(snapshot.stage_manifest_paths) >= {"screen", "hifi_validate", "hifi_rank", "report"}


def test_build_campaign_outcome_snapshot_marks_missing_downstream_metrics_explicitly(
    tmp_path: Path,
) -> None:
    launch_summary_path = _write_launch_bundle(tmp_path)
    _write_stage_artifacts(
        tmp_path,
        launch_id="launch-other",
        launch_summary_path=launch_summary_path,
        include_validation=False,
        include_report=False,
    )
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)

    snapshot = build_campaign_outcome_snapshot(bundle, root=tmp_path)

    assert snapshot.shortlist_pass_rate is None
    assert snapshot.validation_pass_rate is None
    assert snapshot.novelty_score_mean is None
    assert snapshot.synthesizability_mean is None
    assert snapshot.report_release_gate_ready is None
    assert snapshot.missing_metrics == [
        "shortlist_pass_rate",
        "validation_pass_rate",
        "novelty_score_mean",
        "synthesizability_mean",
        "report_release_gate_ready",
    ]


def test_find_prior_campaign_launch_uses_created_at_then_launch_id(tmp_path: Path) -> None:
    _write_launch_bundle(tmp_path, launch_id="launch-001", created_at_utc="2026-04-04T18:00:00Z")
    _write_launch_bundle(tmp_path, launch_id="launch-002", created_at_utc="2026-04-04T19:00:00Z")
    current_path = _write_launch_bundle(
        tmp_path,
        launch_id="launch-003",
        created_at_utc="2026-04-04T19:00:00Z",
    )
    current_summary = load_json_object(current_path)

    prior_path = find_prior_campaign_launch(
        load_campaign_launch_bundle(current_path, root=tmp_path).launch_summary,
        root=tmp_path,
    )

    assert prior_path == llm_campaign_launch_summary_path("campaign-001", "launch-002", root=tmp_path)
    assert current_summary["launch_id"] == "launch-003"


def test_build_campaign_outcome_snapshot_reuses_existing_snapshot(tmp_path: Path) -> None:
    launch_summary_path = _write_launch_bundle(tmp_path)
    _write_stage_artifacts(tmp_path, launch_id="launch-001", launch_summary_path=launch_summary_path)
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)

    first = build_campaign_outcome_snapshot(bundle, root=tmp_path)
    write_json_object(
        {"pass_rate": 0.99},
        tmp_path / "data" / "calibration" / "al_cu_fe_screen_calibration.json",
    )

    second = build_campaign_outcome_snapshot(bundle, root=tmp_path)

    assert first == second
    assert second.shortlist_pass_rate == 0.22


def test_build_campaign_comparison_uses_acceptance_and_prior_snapshot(tmp_path: Path) -> None:
    prior_path = _write_launch_bundle(tmp_path, launch_id="launch-001", created_at_utc="2026-04-04T18:00:00Z")
    _write_stage_artifacts(tmp_path, launch_id="launch-001", launch_summary_path=prior_path)
    prior_bundle = load_campaign_launch_bundle(prior_path, root=tmp_path)
    prior_snapshot = build_campaign_outcome_snapshot(prior_bundle, root=tmp_path)

    current_path = _write_launch_bundle(
        tmp_path,
        launch_id="launch-002",
        created_at_utc="2026-04-04T19:00:00Z",
    )
    _write_stage_artifacts(tmp_path, launch_id="launch-002", launch_summary_path=current_path)
    current_bundle = load_campaign_launch_bundle(current_path, root=tmp_path)

    comparison = build_campaign_comparison(
        current_bundle,
        current_outcome=build_campaign_outcome_snapshot(current_bundle, root=tmp_path),
        prior_outcome=prior_snapshot,
        root=tmp_path,
    )
    comparison_path = llm_campaign_comparison_path(
        "campaign-001",
        "comparison_launch-002",
        root=tmp_path,
    )

    assert comparison_path.exists()
    assert comparison.prior_outcome is not None
    assert comparison.delta_vs_acceptance["parse_success_rate"] == 0.2
    assert comparison.delta_vs_acceptance["report_release_gate_ready"] == 1.0
    assert comparison.delta_vs_prior["parse_success_rate"] == 0.0
    assert any("Prior launch baseline: launch-001" in line for line in comparison.summary_lines)
    assert comparison.system == "Al-Cu-Fe"


def test_build_campaign_comparison_summary_surfaces_generation_selection_metadata(
    tmp_path: Path,
) -> None:
    launch_summary_path = _write_launch_bundle(
        tmp_path,
        serving_identity={
            "requested_model_lane": "general_purpose",
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
            "adapter": "openai_compat_v1",
            "provider": "openai_compat",
            "model": "zomic-al-cu-fe-adapted-v1",
            "effective_api_base": "http://localhost:8000",
            "checkpoint_id": "ckpt-al-cu-fe-zomic-a",
            "checkpoint_selection_source": "family_promoted_default",
            "checkpoint_lifecycle_path": "data/llm_checkpoints/families/adapted-al-cu-fe/lifecycle.json",
            "checkpoint_lifecycle_revision": 3,
            "checkpoint_lineage": {
                "checkpoint_id": "ckpt-al-cu-fe-zomic-a",
                "checkpoint_family": "adapted-al-cu-fe",
                "registration_path": "data/llm_checkpoints/ckpt-al-cu-fe-zomic-a/registration.json",
                "fingerprint": "fp-adapted-001",
                "base_model": "zomic-general-local-v1",
                "adaptation_method": "lora",
                "adaptation_artifact_path": "lineage/adapter_manifest.json",
                "corpus_manifest_path": "lineage/corpus_manifest.json",
                "eval_set_manifest_path": "lineage/eval_manifest.json",
            },
        },
    )
    _write_stage_artifacts(tmp_path, launch_id="launch-001", launch_summary_path=launch_summary_path)
    bundle = load_campaign_launch_bundle(launch_summary_path, root=tmp_path)

    comparison = build_campaign_comparison(
        bundle,
        current_outcome=build_campaign_outcome_snapshot(bundle, root=tmp_path),
        root=tmp_path,
    )

    assert any(
        "Generation serving identity: zomic-al-cu-fe-adapted-v1, checkpoint ckpt-al-cu-fe-zomic-a, via family_promoted_default, lifecycle r3"
        in line
        for line in comparison.summary_lines
    )
