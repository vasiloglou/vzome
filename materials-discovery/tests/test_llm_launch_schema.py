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


def test_system_config_accepts_checkpoint_family_with_explicit_pin() -> None:
    data = _base_config()
    data["llm_generate"] = {
        "prompt_template": "zomic_generate_v1",
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
                "checkpoint_family": " adapted-al-cu-fe ",
                "checkpoint_id": " ckpt-123 ",
            },
        },
    }

    config = SystemConfig.model_validate(data)
    lane = config.llm_generate.model_lanes["specialized_materials"]

    assert lane.checkpoint_family == "adapted-al-cu-fe"
    assert lane.checkpoint_id == "ckpt-123"


def test_system_config_normalizes_blank_checkpoint_family_to_none() -> None:
    data = _base_config()
    data["llm_generate"] = {
        "prompt_template": "zomic_generate_v1",
        "model_lanes": {
            "general_purpose": {
                "adapter": "llm_fixture_v1",
                "provider": "mock",
                "model": "fixture-zomic-v1",
                "checkpoint_family": "   ",
            }
        },
    }

    config = SystemConfig.model_validate(data)

    assert config.llm_generate.model_lanes["general_purpose"].checkpoint_family is None


def test_checkpoint_family_does_not_change_registration_fingerprint() -> None:
    from materials_discovery.llm import LlmCheckpointRegistrationSpec
    from materials_discovery.llm.checkpoints import _checkpoint_fingerprint

    baseline = LlmCheckpointRegistrationSpec(
        checkpoint_id="ckpt-123",
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        adapter="openai_compat_v1",
        provider="openai_compat",
        model="materials-local-v1",
        local_model_path="/models/materials-local-v1",
        model_revision="rev-a",
        base_model="materials-baseline-v1",
        base_model_revision="base-rev-a",
        adaptation_method="lora",
        adaptation_artifact_path="lineage/adapter_manifest.json",
        corpus_manifest_path="lineage/corpus_manifest.json",
        eval_set_manifest_path="lineage/eval_manifest.json",
        acceptance_pack_path="lineage/acceptance_pack.json",
    )
    with_family = baseline.model_copy(update={"checkpoint_family": "adapted-al-cu-fe"})

    assert _checkpoint_fingerprint(baseline) == _checkpoint_fingerprint(with_family)


def test_checkpoint_registration_and_lineage_models_support_checkpoint_family() -> None:
    from materials_discovery.llm import (
        LlmCheckpointLineage,
        LlmCheckpointRegistration,
        LlmCheckpointRegistrationSummary,
    )

    registration = LlmCheckpointRegistration(
        checkpoint_id="ckpt-123",
        checkpoint_family="adapted-al-cu-fe",
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        created_at_utc="2026-04-05T19:00:00Z",
        adapter="openai_compat_v1",
        provider="openai_compat",
        model="materials-local-v1",
        local_model_path="/models/materials-local-v1",
        model_revision="rev-a",
        fingerprint="abc123def4567890",
        base_model="materials-baseline-v1",
        base_model_revision="base-rev-a",
        adaptation_method="lora",
        adaptation_artifact_path="lineage/adapter_manifest.json",
        corpus_manifest_path="lineage/corpus_manifest.json",
        eval_set_manifest_path="lineage/eval_manifest.json",
        acceptance_pack_path="lineage/acceptance_pack.json",
    )
    lineage = LlmCheckpointLineage(
        checkpoint_id="ckpt-123",
        checkpoint_family="adapted-al-cu-fe",
        registration_path="data/llm_checkpoints/ckpt-123/registration.json",
        fingerprint="abc123def4567890",
        base_model="materials-baseline-v1",
        base_model_revision="base-rev-a",
        adaptation_method="lora",
        adaptation_artifact_path="lineage/adapter_manifest.json",
        corpus_manifest_path="lineage/corpus_manifest.json",
        eval_set_manifest_path="lineage/eval_manifest.json",
        acceptance_pack_path="lineage/acceptance_pack.json",
    )
    legacy_registration = LlmCheckpointRegistration.model_validate(
        {
            "checkpoint_id": "ckpt-legacy",
            "system": "Al-Cu-Fe",
            "template_family": "icosahedral_approximant_1_1",
            "created_at_utc": "2026-04-05T19:00:00Z",
            "adapter": "openai_compat_v1",
            "provider": "openai_compat",
            "model": "materials-local-v1",
            "local_model_path": "/models/materials-local-v1",
            "model_revision": "rev-a",
            "fingerprint": "abc123def4567890",
            "base_model": "materials-baseline-v1",
            "base_model_revision": "base-rev-a",
            "adaptation_method": "lora",
            "adaptation_artifact_path": "lineage/adapter_manifest.json",
            "corpus_manifest_path": "lineage/corpus_manifest.json",
            "eval_set_manifest_path": "lineage/eval_manifest.json",
        }
    )
    legacy_lineage = LlmCheckpointLineage.model_validate(
        {
            "checkpoint_id": "ckpt-legacy",
            "registration_path": "data/llm_checkpoints/ckpt-legacy/registration.json",
            "fingerprint": "abc123def4567890",
            "base_model": "materials-baseline-v1",
            "base_model_revision": "base-rev-a",
            "adaptation_method": "lora",
            "adaptation_artifact_path": "lineage/adapter_manifest.json",
            "corpus_manifest_path": "lineage/corpus_manifest.json",
            "eval_set_manifest_path": "lineage/eval_manifest.json",
        }
    )
    summary = LlmCheckpointRegistrationSummary(
        checkpoint_id="ckpt-123",
        checkpoint_family="adapted-al-cu-fe",
        fingerprint="abc123def4567890",
        registration_path="data/llm_checkpoints/ckpt-123/registration.json",
    )

    assert registration.checkpoint_family == "adapted-al-cu-fe"
    assert lineage.checkpoint_family == "adapted-al-cu-fe"
    assert summary.checkpoint_family == "adapted-al-cu-fe"
    assert legacy_registration.checkpoint_family is None
    assert legacy_lineage.checkpoint_family is None


def test_checkpoint_lifecycle_contract_models_round_trip() -> None:
    from materials_discovery.llm import (
        LlmCheckpointLifecycleIndex,
        LlmCheckpointLifecycleMemberSummary,
        LlmCheckpointPinSelectionSpec,
        LlmCheckpointPromotionSpec,
        LlmCheckpointRetirementSpec,
    )

    index = LlmCheckpointLifecycleIndex(
        checkpoint_family="adapted-al-cu-fe",
        revision=3,
        promoted_checkpoint_id="ckpt-123",
        members=[
            LlmCheckpointLifecycleMemberSummary(
                checkpoint_id="ckpt-123",
                fingerprint="abc123def4567890",
                registration_path="data/llm_checkpoints/ckpt-123/registration.json",
                lifecycle_state="promoted",
                registered_at_utc="2026-04-05T19:00:00Z",
                promoted_at_utc="2026-04-05T19:10:00Z",
                last_action_path=(
                    "data/llm_checkpoints/families/adapted-al-cu-fe/actions/"
                    "promotion-r3-ckpt-123.json"
                ),
            ),
            LlmCheckpointLifecycleMemberSummary(
                checkpoint_id="ckpt-122",
                fingerprint="fff222def4567890",
                registration_path="data/llm_checkpoints/ckpt-122/registration.json",
                lifecycle_state="retired",
                registered_at_utc="2026-04-05T18:00:00Z",
                retired_at_utc="2026-04-05T18:30:00Z",
                retirement_reason="superseded",
                last_action_path=(
                    "data/llm_checkpoints/families/adapted-al-cu-fe/actions/"
                    "retirement-r2-ckpt-122.json"
                ),
            ),
        ],
        action_history_paths=[
            " data/llm_checkpoints/families/adapted-al-cu-fe/actions/promotion-r3-ckpt-123.json ",
            "data/llm_checkpoints/families/adapted-al-cu-fe/actions/retirement-r2-ckpt-122.json",
        ],
    )
    promotion = LlmCheckpointPromotionSpec(
        checkpoint_family="adapted-al-cu-fe",
        checkpoint_id="ckpt-123",
        evidence_paths=[
            " reports/serving_benchmark.json ",
            "reports/acceptance_eval.json",
        ],
        expected_revision=2,
        expected_promoted_checkpoint_id=" ",
        note=" promoted after benchmark comparison ",
    )
    retirement = LlmCheckpointRetirementSpec(
        checkpoint_family="adapted-al-cu-fe",
        checkpoint_id="ckpt-122",
        reason="superseded",
        expected_revision=3,
        replacement_checkpoint_id="ckpt-123",
        note=" retired after promotion ",
    )
    pin_selection = LlmCheckpointPinSelectionSpec(
        checkpoint_family="adapted-al-cu-fe",
        checkpoint_id="ckpt-123",
        selection_source="campaign",
        campaign_id=" campaign-001 ",
        note=" pin for replay ",
    )

    round_tripped_index = LlmCheckpointLifecycleIndex.model_validate(index.model_dump(mode="json"))
    round_tripped_pin = LlmCheckpointPinSelectionSpec.model_validate(
        pin_selection.model_dump(mode="json")
    )

    assert round_tripped_index.revision == 3
    assert round_tripped_index.promoted_checkpoint_id == "ckpt-123"
    assert round_tripped_index.action_history_paths == [
        "data/llm_checkpoints/families/adapted-al-cu-fe/actions/promotion-r3-ckpt-123.json",
        "data/llm_checkpoints/families/adapted-al-cu-fe/actions/retirement-r2-ckpt-122.json",
    ]
    assert promotion.expected_promoted_checkpoint_id is None
    assert promotion.evidence_paths == [
        "reports/serving_benchmark.json",
        "reports/acceptance_eval.json",
    ]
    assert retirement.replacement_checkpoint_id == "ckpt-123"
    assert round_tripped_pin.campaign_id == "campaign-001"


@pytest.mark.parametrize(
    ("factory", "match"),
    [
        (
            lambda: __import__("materials_discovery.llm", fromlist=["LlmCheckpointLifecycleIndex"])
            .LlmCheckpointLifecycleIndex(
                checkpoint_family="adapted-al-cu-fe",
                revision=1,
                promoted_checkpoint_id="ckpt-123",
                members=[],
            ),
            "promoted_checkpoint_id must reference a known family member",
        ),
        (
            lambda: __import__(
                "materials_discovery.llm", fromlist=["LlmCheckpointPinSelectionSpec"]
            ).LlmCheckpointPinSelectionSpec(
                checkpoint_family="adapted-al-cu-fe",
                checkpoint_id="ckpt-123",
                selection_source="manual",
                campaign_id="campaign-001",
            ),
            "manual pin selections cannot include campaign_id",
        ),
    ],
)
def test_checkpoint_lifecycle_contract_models_reject_conflicts(factory, match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        factory()


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
