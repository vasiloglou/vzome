from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import SystemConfig


def _base_config() -> dict:
    workspace = Path(__file__).resolve().parents[1]
    return load_yaml(workspace / "configs" / "systems" / "al_cu_fe.yaml")


def test_system_config_accepts_named_model_lanes() -> None:
    data = _base_config()
    data["backend"] = {}
    data["backend"]["llm_api_base"] = "https://baseline.invalid/v1/"
    data["backend"]["llm_request_timeout_s"] = 150.0
    data["backend"]["llm_probe_timeout_s"] = 8.0
    data["backend"]["llm_probe_path"] = "  "
    data["llm_generate"] = {
        "prompt_template": "zomic_generate_v1",
        "temperature": 0.4,
        "max_tokens": 512,
        "max_attempts": 2,
        "default_model_lane": "general_purpose",
        "fallback_model_lane": "specialized_materials",
        "model_lanes": {
            "general_purpose": {
                "adapter": "llm_fixture_v1",
                "provider": "mock",
                "model": "fixture-zomic-v1",
            },
            "specialized_materials": {
                "adapter": "openai_compat_v1",
                "provider": "openai_compat",
                "model": "materials-local-v1",
                "api_base": "https://example.invalid/materials/",
                "checkpoint_id": " ckpt-123 ",
                "model_revision": " rev-a ",
                "local_model_path": " /models/materials ",
            },
        },
    }

    config = SystemConfig.model_validate(data)

    assert config.llm_generate is not None
    assert config.backend.llm_api_base == "https://baseline.invalid/v1"
    assert config.backend.llm_request_timeout_s == 150.0
    assert config.backend.llm_probe_timeout_s == 8.0
    assert config.backend.llm_probe_path is None
    assert config.llm_generate.default_model_lane == "general_purpose"
    assert config.llm_generate.fallback_model_lane == "specialized_materials"
    assert config.llm_generate.model_lanes["general_purpose"].provider == "mock"
    assert config.llm_generate.model_lanes["specialized_materials"].api_base == (
        "https://example.invalid/materials"
    )
    assert config.llm_generate.model_lanes["specialized_materials"].checkpoint_id == "ckpt-123"
    assert config.llm_generate.model_lanes["specialized_materials"].model_revision == "rev-a"
    assert config.llm_generate.model_lanes["specialized_materials"].local_model_path == (
        "/models/materials"
    )


def test_system_config_rejects_unknown_model_lane_keys() -> None:
    data = _base_config()
    data["llm_generate"] = {
        "prompt_template": "zomic_generate_v1",
        "model_lanes": {
            "experimental_lane": {
                "adapter": "llm_fixture_v1",
                "provider": "mock",
                "model": "fixture-zomic-v1",
            }
        },
    }

    with pytest.raises(ValidationError):
        SystemConfig.model_validate(data)


def test_legacy_llm_generate_configs_still_validate_without_model_lanes() -> None:
    data = _base_config()
    data["llm_generate"] = {
        "prompt_template": "zomic_generate_v1",
        "temperature": 0.5,
        "max_tokens": 512,
        "max_attempts": 4,
        "seed_zomic": "designs/demo.zomic",
        "artifact_root": "data/llm_runs/custom",
        "fixture_outputs": ["line 1", "line 2"],
    }

    config = SystemConfig.model_validate(data)

    assert config.llm_generate is not None
    assert config.llm_generate.prompt_template == "zomic_generate_v1"
    assert config.llm_generate.max_attempts == 4
    assert config.llm_generate.model_lanes == {}


def test_launch_contract_models_capture_lane_and_artifact_metadata() -> None:
    from materials_discovery.llm import (  # imported lazily so RED fails on missing exports
        LlmCampaignLaunchSummary,
        LlmCampaignResolvedLaunch,
        LlmServingIdentity,
    )

    resolved = LlmCampaignResolvedLaunch(
        launch_id="launch-001",
        campaign_id="campaign-001",
        campaign_spec_path="data/llm_campaigns/campaign-001/campaign_spec.json",
        system_config_path="configs/systems/al_cu_fe_llm.yaml",
        system_config_hash="abc123",
        requested_model_lanes=["specialized_materials", "general_purpose"],
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="backend_default",
        resolved_adapter="llm_fixture_v1",
        resolved_provider="mock",
        resolved_model="fixture-zomic-v1",
        serving_identity=LlmServingIdentity(
            requested_model_lane="specialized_materials",
            resolved_model_lane="general_purpose",
            resolved_model_lane_source="backend_default",
            adapter="llm_fixture_v1",
            provider="mock",
            model="fixture-zomic-v1",
            effective_api_base="https://baseline.invalid/v1/",
            checkpoint_id="ckpt-123",
            model_revision="rev-a",
            local_model_path="/models/materials",
        ),
        prompt_instruction_deltas=["Prefer Bergman-like motifs"],
        resolved_composition_bounds={
            "Al": {"min": 0.6, "max": 0.75},
            "Cu": {"min": 0.1, "max": 0.25},
            "Fe": {"min": 0.05, "max": 0.2},
        },
        resolved_example_pack_path="data/llm_eval_sets/demo/eval_set.jsonl",
        resolved_seed_zomic_path="data/llm_campaigns/campaign-001/launches/launch-001/seed.zomic",
    )
    summary = LlmCampaignLaunchSummary(
        launch_id="launch-001",
        campaign_id="campaign-001",
        campaign_spec_path="data/llm_campaigns/campaign-001/campaign_spec.json",
        proposal_id="proposal-001",
        approval_id="approval-001",
        system="Al-Cu-Fe",
        status="succeeded",
        created_at_utc="2026-04-04T16:00:00Z",
        requested_count=3,
        requested_model_lanes=["specialized_materials", "general_purpose"],
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        serving_identity=LlmServingIdentity(
            requested_model_lane="specialized_materials",
            resolved_model_lane="general_purpose",
            resolved_model_lane_source="configured_lane",
            adapter="llm_fixture_v1",
            provider="mock",
            model="fixture-zomic-v1",
            effective_api_base="https://example.invalid/materials/",
        ),
        resolved_launch_path="data/llm_campaigns/campaign-001/launches/launch-001/resolved_launch.json",
        run_manifest_path="data/llm_runs/run-001/manifest.json",
        llm_generate_manifest_path="data/manifests/al_cu_fe_llm_generate.json",
        candidates_path="data/candidates/al_cu_fe_generated.jsonl",
    )

    assert resolved.requested_model_lanes == ["specialized_materials", "general_purpose"]
    assert resolved.resolved_model_lane_source == "backend_default"
    assert resolved.serving_identity is not None
    assert resolved.serving_identity.effective_api_base == "https://baseline.invalid/v1"
    assert summary.status == "succeeded"
    assert summary.candidates_path == "data/candidates/al_cu_fe_generated.jsonl"
    assert summary.serving_identity is not None
    assert summary.serving_identity.effective_api_base == "https://example.invalid/materials"


def test_legacy_launch_artifacts_still_load_without_serving_identity() -> None:
    from materials_discovery.llm import LlmCampaignLaunchSummary, LlmCampaignResolvedLaunch

    resolved = LlmCampaignResolvedLaunch.model_validate(
        {
            "launch_id": "launch-001",
            "campaign_id": "campaign-001",
            "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
            "system_config_path": "configs/systems/al_cu_fe_llm.yaml",
            "system_config_hash": "abc123",
            "requested_model_lanes": ["general_purpose"],
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "baseline_fallback",
            "resolved_adapter": "llm_fixture_v1",
            "resolved_provider": "mock",
            "resolved_model": "fixture-zomic-v1",
            "resolved_composition_bounds": {
                "Al": {"min": 0.6, "max": 0.75},
                "Cu": {"min": 0.1, "max": 0.25},
                "Fe": {"min": 0.05, "max": 0.2},
            },
        }
    )
    summary = LlmCampaignLaunchSummary.model_validate(
        {
            "launch_id": "launch-001",
            "campaign_id": "campaign-001",
            "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
            "proposal_id": "proposal-001",
            "approval_id": "approval-001",
            "system": "Al-Cu-Fe",
            "status": "succeeded",
            "created_at_utc": "2026-04-04T16:00:00Z",
            "requested_count": 1,
            "requested_model_lanes": ["general_purpose"],
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "baseline_fallback",
            "resolved_launch_path": "data/llm_campaigns/campaign-001/launches/launch-001/resolved_launch.json",
        }
    )

    assert resolved.serving_identity is None
    assert summary.serving_identity is None


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        (
            {
                "launch_id": " ",
                "campaign_id": "campaign-001",
                "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
                "proposal_id": "proposal-001",
                "approval_id": "approval-001",
                "system": "Al-Cu-Fe",
                "status": "running",
                "created_at_utc": "2026-04-04T16:00:00Z",
                "requested_count": 1,
                "requested_model_lanes": ["general_purpose"],
                "resolved_model_lane": "general_purpose",
                "resolved_model_lane_source": "configured_lane",
                "resolved_launch_path": "data/llm_campaigns/campaign-001/launches/launch-001/resolved_launch.json",
            },
            "field must not be blank",
        ),
        (
            {
                "launch_id": "launch-001",
                "campaign_id": "campaign-001",
                "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
                "proposal_id": "proposal-001",
                "approval_id": "approval-001",
                "system": "Al-Cu-Fe",
                "status": "pending",
                "created_at_utc": "2026-04-04T16:00:00Z",
                "requested_count": 1,
                "requested_model_lanes": ["general_purpose"],
                "resolved_model_lane": "general_purpose",
                "resolved_model_lane_source": "configured_lane",
                "resolved_launch_path": "data/llm_campaigns/campaign-001/launches/launch-001/resolved_launch.json",
            },
            "status",
        ),
        (
            {
                "launch_id": "launch-001",
                "campaign_id": "campaign-001",
                "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
                "proposal_id": "proposal-001",
                "approval_id": "approval-001",
                "system": "Al-Cu-Fe",
                "status": "failed",
                "created_at_utc": "2026-04-04T16:00:00Z",
                "requested_count": 1,
                "requested_model_lanes": ["general_purpose"],
                "resolved_model_lane": "general_purpose",
                "resolved_model_lane_source": "configured_lane",
                "resolved_launch_path": " ",
            },
            "field must not be blank",
        ),
    ],
)
def test_launch_summary_rejects_blank_fields_and_invalid_status(
    payload: dict[str, object],
    match: str,
) -> None:
    from materials_discovery.llm.schema import LlmCampaignLaunchSummary

    with pytest.raises(ValidationError, match=match):
        LlmCampaignLaunchSummary(**payload)


def test_launch_storage_helpers_use_deterministic_campaign_launch_paths(tmp_path: Path) -> None:
    from materials_discovery.llm import (
        llm_campaign_launch_dir,
        llm_campaign_launch_summary_path,
        llm_campaign_launches_dir,
        llm_campaign_materialized_seed_path,
        llm_campaign_resolved_launch_path,
    )

    launches_dir = llm_campaign_launches_dir("campaign-001", root=tmp_path)
    launch_dir = llm_campaign_launch_dir("campaign-001", "launch-001", root=tmp_path)

    assert launches_dir == tmp_path / "data" / "llm_campaigns" / "campaign-001" / "launches"
    assert launch_dir == launches_dir / "launch-001"
    assert llm_campaign_launch_summary_path("campaign-001", "launch-001", root=tmp_path) == (
        launch_dir / "launch_summary.json"
    )
    assert llm_campaign_resolved_launch_path("campaign-001", "launch-001", root=tmp_path) == (
        launch_dir / "resolved_launch.json"
    )
    assert llm_campaign_materialized_seed_path("campaign-001", "launch-001", root=tmp_path) == (
        launch_dir / "seed_from_evalset.zomic"
    )
