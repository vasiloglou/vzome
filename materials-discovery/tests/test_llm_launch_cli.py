from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml, write_json_object, write_jsonl
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import LlmGenerateSummary, SystemConfig
from materials_discovery.llm.schema import LlmCampaignResolvedLaunch, LlmServingIdentity


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _campaign_spec_payload(config_path: Path, *, config_hash: str) -> dict[str, object]:
    return {
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
            "system_config_hash": config_hash,
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
            "acceptance_pack_path": "data/benchmarks/llm_acceptance/pack_v1/acceptance_pack.json",
            "eval_set_manifest_path": None,
            "proposal_path": "data/benchmarks/llm_acceptance/pack_v1/proposals/proposal-001.json",
            "approval_path": "data/benchmarks/llm_acceptance/pack_v1/approvals/approval-001.json",
            "source_system_config_path": str(config_path),
            "source_system_config_hash": config_hash,
        },
    }


def test_cli_llm_launch_success(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))
    spec_path = tmp_path / "campaign_spec.json"
    spec_path.write_text(
        json.dumps(
            _campaign_spec_payload(config_path, config_hash=config_sha256(config)),
            indent=2,
        ),
        encoding="utf-8",
    )
    out_file = tmp_path / "custom" / "campaign_candidates.jsonl"

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    def _fake_resolve(spec, system_config, *, campaign_spec_path, launch_id, artifact_root=None):
        del spec, system_config
        return config, LlmCampaignResolvedLaunch(
            launch_id=launch_id,
            campaign_id="campaign-001",
            campaign_spec_path=str(campaign_spec_path),
            system_config_path=str(config_path),
            system_config_hash=config_sha256(config),
            requested_model_lanes=["general_purpose"],
            resolved_model_lane="general_purpose",
            resolved_model_lane_source="configured_lane",
            resolved_adapter="llm_fixture_v1",
            resolved_provider="mock",
            resolved_model="fixture-al-cu-fe-v1",
            serving_identity=LlmServingIdentity(
                requested_model_lane="general_purpose",
                resolved_model_lane="general_purpose",
                resolved_model_lane_source="configured_lane",
                adapter="llm_fixture_v1",
                provider="mock",
                model="fixture-al-cu-fe-v1",
            ),
            prompt_instruction_deltas=["Prefer parser-safe symmetry annotations."],
            resolved_composition_bounds=config.composition_bounds,
            resolved_example_pack_path=None,
            resolved_seed_zomic_path=None,
        )

    def _fake_generate(system_config, output_path, count, **kwargs):
        del system_config, count
        write_jsonl([], output_path)
        run_manifest = tmp_path / "data" / "llm_runs" / "launch_run" / "run_manifest.json"
        write_json_object({}, run_manifest)
        return LlmGenerateSummary(
            requested_count=2,
            generated_count=0,
            attempt_count=1,
            parse_pass_count=1,
            compile_pass_count=0,
            output_path=str(output_path),
            run_manifest_path=str(run_manifest),
        )

    monkeypatch.setattr("materials_discovery.cli.resolve_campaign_launch", _fake_resolve)
    monkeypatch.setattr("materials_discovery.cli.generate_llm_candidates", _fake_generate)

    result = runner.invoke(
        app,
        [
            "llm-launch",
            "--campaign-spec",
            str(spec_path),
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["campaign_id"] == "campaign-001"
    assert Path(payload["resolved_launch_path"]).exists()
    assert Path(payload["candidates_path"]) == out_file
    resolved_payload = json.loads(Path(payload["resolved_launch_path"]).read_text(encoding="utf-8"))
    assert resolved_payload["serving_identity"]["resolved_model_lane"] == "general_purpose"


def test_cli_llm_launch_rejects_config_hash_drift_before_generation(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))
    spec_path = tmp_path / "campaign_spec.json"
    spec_path.write_text(
        json.dumps(
            _campaign_spec_payload(config_path, config_hash="sha256:mismatched"),
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)
    calls = {"resolve": 0, "generate": 0}

    def _fake_resolve(*args, **kwargs):
        del args, kwargs
        calls["resolve"] += 1
        raise AssertionError("resolve_campaign_launch should not run on config drift")

    def _fake_generate(*args, **kwargs):
        del args, kwargs
        calls["generate"] += 1
        raise AssertionError("generate_llm_candidates should not run on config drift")

    monkeypatch.setattr("materials_discovery.cli.resolve_campaign_launch", _fake_resolve)
    monkeypatch.setattr("materials_discovery.cli.generate_llm_candidates", _fake_generate)

    result = runner.invoke(
        app,
        [
            "llm-launch",
            "--campaign-spec",
            str(spec_path),
        ],
    )

    assert result.exit_code == 2
    assert str(config_path) in result.stderr
    assert "re-approval may be required" in result.stderr
    assert calls == {"resolve": 0, "generate": 0}


def test_cli_llm_launch_surfaces_local_lane_readiness_before_generation(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))
    config.backend.mode = "real"
    config.backend.llm_adapter = "openai_compat_v1"
    config.backend.llm_provider = "openai_compat"
    config.backend.llm_model = "materials-local-v1"
    config.backend.llm_api_base = "http://localhost:8000"
    spec_path = tmp_path / "campaign_spec.json"
    spec_path.write_text(
        json.dumps(
            _campaign_spec_payload(config_path, config_hash=config_sha256(config)),
            indent=2,
        ),
        encoding="utf-8",
    )

    class _Adapter:
        pass

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.cli._load_system_config", lambda path: config)
    monkeypatch.setattr("materials_discovery.cli.resolve_llm_adapter", lambda *args, **kwargs: _Adapter())

    def _fake_resolve(spec, system_config, *, campaign_spec_path, launch_id, artifact_root=None):
        del spec, system_config, artifact_root
        return config, LlmCampaignResolvedLaunch(
            launch_id=launch_id,
            campaign_id="campaign-001",
            campaign_spec_path=str(campaign_spec_path),
            system_config_path=str(config_path),
            system_config_hash=config_sha256(config),
            requested_model_lanes=["specialized_materials"],
            resolved_model_lane="specialized_materials",
            resolved_model_lane_source="configured_lane",
            resolved_adapter="openai_compat_v1",
            resolved_provider="openai_compat",
            resolved_model="materials-local-v1",
            serving_identity=LlmServingIdentity(
                requested_model_lane="specialized_materials",
                resolved_model_lane="specialized_materials",
                resolved_model_lane_source="configured_lane",
                adapter="openai_compat_v1",
                provider="openai_compat",
                model="materials-local-v1",
                effective_api_base="http://localhost:8000",
                checkpoint_id="ckpt-123",
            ),
            prompt_instruction_deltas=[],
            resolved_composition_bounds=config.composition_bounds,
            resolved_example_pack_path=None,
            resolved_seed_zomic_path=None,
        )

    def _fake_ready(adapter, *, adapter_key, requested_lane=None, resolved_lane=None):
        del adapter
        raise RuntimeError(
            f"{adapter_key} readiness probe failed for requested lane '{requested_lane}', "
            f"resolved lane '{resolved_lane}' at http://localhost:8000/v1/models. "
            "Confirm the local server is already running."
        )

    generate_calls = {"count": 0}

    def _fake_generate(*args, **kwargs):
        del args, kwargs
        generate_calls["count"] += 1
        raise AssertionError("generation should not run when readiness fails")

    monkeypatch.setattr("materials_discovery.cli.resolve_campaign_launch", _fake_resolve)
    monkeypatch.setattr("materials_discovery.cli.validate_llm_adapter_ready", _fake_ready)
    monkeypatch.setattr("materials_discovery.cli.generate_llm_candidates", _fake_generate)

    result = runner.invoke(
        app,
        [
            "llm-launch",
            "--campaign-spec",
            str(spec_path),
        ],
    )

    assert result.exit_code == 2
    assert "requested lane 'specialized_materials'" in result.stderr
    assert "http://localhost:8000/v1/models" in result.stderr
    assert generate_calls["count"] == 0
