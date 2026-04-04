from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_json_object, load_yaml, write_json_object, write_jsonl
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import LlmGenerateSummary, SystemConfig
from materials_discovery.llm.storage import (
    llm_acceptance_pack_path,
    llm_campaign_launch_summary_path,
    llm_campaign_resolved_launch_path,
    llm_campaign_spec_path,
)


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _system_config(config_name: str = "al_cu_fe_llm_mock.yaml") -> tuple[SystemConfig, Path]:
    config_path = _workspace() / "configs" / "systems" / config_name
    return SystemConfig.model_validate(load_yaml(config_path)), config_path


def _write_launch_bundle(root: Path) -> Path:
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
                {
                    "system": "Al-Cu-Fe",
                    "generate_comparison_path": "generate.json",
                    "pipeline_comparison_path": "pipeline.json",
                    "parse_success_rate": 0.8,
                    "compile_success_rate": 0.75,
                    "generation_success_rate": 0.4,
                    "shortlist_pass_rate": 0.12,
                    "validation_pass_rate": 0.05,
                    "novelty_score_mean": 0.3,
                    "synthesizability_mean": 0.6,
                    "report_release_gate_ready": False,
                    "failing_metrics": ["compile_success_rate"],
                    "passed": False,
                }
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
                "proposal_path": "proposal.json",
                "approval_path": "approval.json",
                "source_system_config_path": str(config_path),
                "source_system_config_hash": config_hash,
            },
        },
        campaign_spec_path,
    )

    run_dir = root / "data" / "llm_runs" / "run_launch_001"
    prompt_path = run_dir / "prompt.json"
    run_manifest_path = run_dir / "run_manifest.json"
    compile_results_path = run_dir / "compile_results.jsonl"
    attempts_path = run_dir / "attempts.jsonl"

    write_json_object(
        {
            "request_hash": "request-launch-001",
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
                "conditioning_example_ids": ["eval_001"],
            },
            "prompt_text": "Generate two parser-safe candidates.",
            "conditioning_example_ids": ["eval_001"],
        },
        prompt_path,
    )
    write_jsonl([], attempts_path)
    write_jsonl([], compile_results_path)
    write_json_object(
        {
            "schema_version": "llm-run-manifest/v1",
            "run_id": "run_launch_001",
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
            "created_at_utc": "2026-04-04T18:00:00Z",
            "example_pack_path": str(root / "data" / "llm_eval_sets" / "demo" / "eval_set.jsonl"),
            "prompt_instruction_deltas": ["Prefer parser-safe symmetry annotations."],
            "conditioning_example_ids": ["eval_001"],
            "campaign_id": "campaign-001",
            "launch_id": "launch-001",
            "campaign_spec_path": str(campaign_spec_path),
            "proposal_id": "proposal-001",
            "approval_id": "approval-001",
            "requested_model_lanes": ["general_purpose"],
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
            "launch_summary_path": str(
                llm_campaign_launch_summary_path("campaign-001", "launch-001", root=root)
            ),
            "temperature": 0.15,
            "max_tokens": 900,
            "max_attempts": 4,
            "seed_zomic_path": str(root / "designs" / "demo.zomic"),
        },
        run_manifest_path,
    )

    resolved_launch_path = llm_campaign_resolved_launch_path("campaign-001", "launch-001", root=root)
    write_json_object(
        {
            "launch_id": "launch-001",
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

    launch_summary_path = llm_campaign_launch_summary_path("campaign-001", "launch-001", root=root)
    write_json_object(
        {
            "launch_id": "launch-001",
            "campaign_id": "campaign-001",
            "campaign_spec_path": str(campaign_spec_path),
            "proposal_id": "proposal-001",
            "approval_id": "approval-001",
            "system": "Al-Cu-Fe",
            "status": "succeeded",
            "created_at_utc": "2026-04-04T18:00:00Z",
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


def test_cli_llm_replay_success(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    source_launch_summary = _write_launch_bundle(tmp_path)
    source_config, _ = _system_config()

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.cli._new_launch_id", lambda: "launch-replay-002")

    def _fake_generate(system_config, output_path, count, **kwargs):
        assert system_config.backend.llm_model == "fixture-al-cu-fe-v1"
        assert system_config.llm_generate.temperature == pytest.approx(0.15)
        assert system_config.llm_generate.max_tokens == 900
        assert system_config.llm_generate.max_attempts == 4
        assert output_path == (
            tmp_path / "data" / "candidates" / "al_cu_fe_replay_launch-replay-002.jsonl"
        )
        assert count == 2
        assert kwargs["campaign_metadata"]["replay_of_launch_id"] == "launch-001"
        assert kwargs["campaign_metadata"]["replay_of_launch_summary_path"] == str(
            source_launch_summary
        )
        write_jsonl([], output_path)
        run_manifest_path = tmp_path / "data" / "llm_runs" / "replay_run" / "run_manifest.json"
        write_json_object(
            {
                "schema_version": "llm-run-manifest/v1",
                "run_id": "replay_run",
                "system": source_config.system_name,
                "adapter_key": "llm_fixture_v1",
                "provider": "mock",
                "model": "fixture-al-cu-fe-v1",
                "prompt_template": "zomic_generate_v1",
                "attempt_count": 1,
                "requested_count": 2,
                "generated_count": 0,
                "prompt_path": str(tmp_path / "data" / "llm_runs" / "replay_run" / "prompt.json"),
                "attempts_path": str(tmp_path / "data" / "llm_runs" / "replay_run" / "attempts.jsonl"),
                "compile_results_path": str(
                    tmp_path / "data" / "llm_runs" / "replay_run" / "compile_results.jsonl"
                ),
                "created_at_utc": "2026-04-04T19:00:00Z",
            },
            run_manifest_path,
        )
        return LlmGenerateSummary(
            requested_count=2,
            generated_count=0,
            attempt_count=1,
            parse_pass_count=1,
            compile_pass_count=0,
            output_path=str(output_path),
            run_manifest_path=str(run_manifest_path),
        )

    monkeypatch.setattr("materials_discovery.cli.generate_llm_candidates", _fake_generate)

    result = runner.invoke(
        app,
        [
            "llm-replay",
            "--launch-summary",
            str(source_launch_summary),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["launch_id"] == "launch-replay-002"
    assert payload["replay_of_launch_id"] == "launch-001"
    assert payload["current_system_config_hash"] == config_sha256(source_config)
    resolved_launch = load_json_object(Path(payload["resolved_launch_path"]))
    assert resolved_launch["replay_of_launch_id"] == "launch-001"
    assert resolved_launch["effective_candidates_path"].endswith(
        "al_cu_fe_replay_launch-replay-002.jsonl"
    )


def test_cli_llm_replay_records_config_drift_without_failing(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    source_launch_summary = _write_launch_bundle(tmp_path)
    drifted_config, _ = _system_config()
    drifted_config.backend.llm_model = "drifted-model"
    drifted_hash = config_sha256(drifted_config)

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.cli._new_launch_id", lambda: "launch-replay-drift")
    monkeypatch.setattr("materials_discovery.cli._load_system_config", lambda path: drifted_config)

    def _fake_generate(system_config, output_path, count, **kwargs):
        assert system_config.backend.llm_model == "fixture-al-cu-fe-v1"
        write_jsonl([], output_path)
        run_manifest_path = tmp_path / "data" / "llm_runs" / "replay_drift" / "run_manifest.json"
        write_json_object({}, run_manifest_path)
        return LlmGenerateSummary(
            requested_count=count,
            generated_count=0,
            attempt_count=1,
            parse_pass_count=1,
            compile_pass_count=0,
            output_path=str(output_path),
            run_manifest_path=str(run_manifest_path),
        )

    monkeypatch.setattr("materials_discovery.cli.generate_llm_candidates", _fake_generate)

    result = runner.invoke(
        app,
        ["llm-replay", "--launch-summary", str(source_launch_summary)],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["current_system_config_hash"] == drifted_hash
    assert payload["replay_of_launch_id"] == "launch-001"
