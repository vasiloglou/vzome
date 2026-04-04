from __future__ import annotations

import pytest
from pydantic import ValidationError

from materials_discovery.llm.schema import (
    DEFAULT_LLM_CAMPAIGN_PROPOSAL_VERSION,
    DEFAULT_LLM_CAMPAIGN_SUGGESTION_VERSION,
    LlmCampaignAction,
    LlmCampaignApproval,
    LlmCampaignLaunchBaseline,
    LlmCampaignLineage,
    LlmCampaignProposal,
    LlmCampaignProposalSummary,
    LlmCampaignSpec,
    LlmCampaignSuggestion,
)


def _prompt_action(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "action_id": "prompt_1",
        "family": "prompt_conditioning",
        "title": "Tighten prompt instructions",
        "rationale": "Parsing metrics regressed in the last lane.",
        "priority": "high",
        "evidence_metrics": [" parse_success_rate ", "compile_success_rate", "parse_success_rate"],
        "preferred_model_lane": "general_purpose",
        "prompt_conditioning": {
            "instruction_delta": "Emphasize exact species labels and compile-safe syntax.",
            "conditioning_strategy": "exact_match_examples",
            "target_example_family": "gold",
            "preferred_max_conditioning_examples": 4,
        },
        "composition_window": None,
        "seed_motif_variation": None,
    }
    payload.update(overrides)
    return payload


def _launch_baseline(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "system_config_path": "configs/systems/al_cu_fe_reference_aware.yaml",
        "system_config_hash": "sha256:config123",
        "system": "Al-Cu-Fe",
        "template_family": "icosahedral_approximant_1_1",
        "default_count": 8,
        "composition_bounds": {
            "Al": {"min": 0.6, "max": 0.75},
            "Cu": {"min": 0.15, "max": 0.25},
            "Fe": {"min": 0.05, "max": 0.15},
        },
        "prompt_template": "zomic_generate_v1",
        "example_pack_path": "data/llm_eval_sets/acceptance_eval_v1/eval_set.jsonl",
        "max_conditioning_examples": 3,
        "seed_zomic_path": "designs/zomic/al_cu_fe_seed.zomic",
    }
    payload.update(overrides)
    return payload


def _lineage(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "acceptance_pack_path": "data/benchmarks/llm_acceptance/pack_v1/acceptance_pack.json",
        "eval_set_manifest_path": "data/llm_eval_sets/acceptance_eval_v1/manifest.json",
        "proposal_path": "data/benchmarks/llm_acceptance/pack_v1/proposals/proposal_1.json",
        "approval_path": "data/benchmarks/llm_acceptance/pack_v1/approvals/approval_1.json",
        "source_system_config_path": "configs/systems/al_cu_fe_reference_aware.yaml",
        "source_system_config_hash": "sha256:config123",
    }
    payload.update(overrides)
    return payload


def test_campaign_action_limits_family_values() -> None:
    with pytest.raises(ValidationError):
        LlmCampaignAction.model_validate(_prompt_action(family="provider_bakeoff"))


def test_campaign_action_supports_general_and_specialized_model_lanes() -> None:
    general = LlmCampaignAction.model_validate(_prompt_action())
    specialized = LlmCampaignAction.model_validate(
        _prompt_action(
            action_id="prompt_2",
            preferred_model_lane="specialized_materials",
            preferred_provider=None,
            preferred_model=None,
            specialized_model_family="  CrystaLLM  ",
        )
    )

    assert general.preferred_model_lane == "general_purpose"
    assert general.preferred_provider is None
    assert general.preferred_model is None
    assert specialized.preferred_model_lane == "specialized_materials"
    assert specialized.specialized_model_family == "CrystaLLM"


def test_campaign_action_requires_matching_payload_and_rejects_non_matching_payloads() -> None:
    with pytest.raises(ValidationError):
        LlmCampaignAction.model_validate(_prompt_action(prompt_conditioning=None))

    with pytest.raises(ValidationError):
        LlmCampaignAction.model_validate(
            _prompt_action(
                composition_window={
                    "window_strategy": "tighten",
                    "focus_species": ["Al", "Cu"],
                }
            )
        )


def test_campaign_proposal_is_system_scoped_and_normalizes_evidence_lists() -> None:
    proposal = LlmCampaignProposal.model_validate(
        {
            "schema_version": DEFAULT_LLM_CAMPAIGN_PROPOSAL_VERSION,
            "proposal_id": " proposal_1 ",
            "pack_id": " pack_v1 ",
            "system": " Al-Cu-Fe ",
            "generated_at_utc": "2026-04-04T00:00:00Z",
            "acceptance_pack_path": " data/benchmarks/llm_acceptance/pack_v1/acceptance_pack.json ",
            "eval_set_manifest_path": " data/llm_eval_sets/acceptance_eval_v1/manifest.json ",
            "generate_comparison_path": " data/benchmarks/llm_generate/al_cu_fe_comparison.json ",
            "pipeline_comparison_path": " data/benchmarks/llm_pipeline/al_cu_fe_comparison.json ",
            "overall_status": "needs_improvement",
            "priority": "high",
            "failing_metrics": [" parse_success_rate ", "compile_success_rate", "parse_success_rate"],
            "actions": [_prompt_action()],
        }
    )

    assert proposal.proposal_id == "proposal_1"
    assert proposal.pack_id == "pack_v1"
    assert proposal.system == "Al-Cu-Fe"
    assert proposal.acceptance_pack_path.endswith("acceptance_pack.json")
    assert proposal.failing_metrics == ["parse_success_rate", "compile_success_rate"]
    assert proposal.actions[0].evidence_metrics == [
        "parse_success_rate",
        "compile_success_rate",
    ]


def test_campaign_approval_is_a_separate_typed_artifact_for_approved_and_rejected() -> None:
    approved = LlmCampaignApproval.model_validate(
        {
            "approval_id": "approval_1",
            "proposal_id": "proposal_1",
            "proposal_path": "data/benchmarks/llm_acceptance/pack_v1/proposals/proposal_1.json",
            "decision": "approved",
            "operator": "operator@example.com",
            "decided_at_utc": "2026-04-04T00:05:00Z",
            "campaign_id": "campaign_1",
        }
    )
    rejected = LlmCampaignApproval.model_validate(
        {
            "approval_id": "approval_2",
            "proposal_id": "proposal_1",
            "proposal_path": "data/benchmarks/llm_acceptance/pack_v1/proposals/proposal_1.json",
            "decision": "rejected",
            "operator": "operator@example.com",
            "decided_at_utc": "2026-04-04T00:10:00Z",
            "notes": "Need stronger exact-match conditioning first.",
        }
    )

    assert approved.decision == "approved"
    assert approved.campaign_id == "campaign_1"
    assert rejected.decision == "rejected"
    assert rejected.campaign_id is None


def test_campaign_suggestion_tracks_proposal_summaries_without_implying_launch() -> None:
    suggestion = LlmCampaignSuggestion.model_validate(
        {
            "schema_version": DEFAULT_LLM_CAMPAIGN_SUGGESTION_VERSION,
            "pack_id": "pack_v1",
            "overall_status": "needs_improvement",
            "generated_at_utc": "2026-04-04T00:00:00Z",
            "proposal_count": 1,
            "proposals": [
                LlmCampaignProposalSummary(
                    proposal_id="proposal_1",
                    system="Al-Cu-Fe",
                    priority="high",
                    failing_metrics=["parse_success_rate"],
                    action_families=["prompt_conditioning"],
                    proposal_path="data/benchmarks/llm_acceptance/pack_v1/proposals/proposal_1.json",
                ).model_dump(mode="json")
            ],
        }
    )

    assert suggestion.proposal_count == 1
    assert suggestion.proposals[0].action_families == ["prompt_conditioning"]


def test_campaign_spec_pins_lineage_and_launch_baseline_without_run_materialization() -> None:
    spec = LlmCampaignSpec.model_validate(
        {
            "campaign_id": "campaign_1",
            "proposal_id": "proposal_1",
            "approval_id": "approval_1",
            "system": "Al-Cu-Fe",
            "created_at_utc": "2026-04-04T00:15:00Z",
            "actions": [_prompt_action()],
            "launch_baseline": _launch_baseline(),
            "lineage": _lineage(),
        }
    )

    assert spec.campaign_id == "campaign_1"
    assert spec.launch_baseline.system == "Al-Cu-Fe"
    assert spec.lineage.proposal_path.endswith("proposal_1.json")
    assert not hasattr(spec, "run_id")


def test_campaign_validators_reject_blank_ids_blank_paths_and_empty_actions() -> None:
    with pytest.raises(ValidationError):
        LlmCampaignProposal.model_validate(
            {
                "proposal_id": "  ",
                "pack_id": "pack_v1",
                "system": "Al-Cu-Fe",
                "generated_at_utc": "2026-04-04T00:00:00Z",
                "acceptance_pack_path": "data/benchmarks/llm_acceptance/pack_v1/acceptance_pack.json",
                "generate_comparison_path": "data/benchmarks/llm_generate/al_cu_fe_comparison.json",
                "pipeline_comparison_path": "data/benchmarks/llm_pipeline/al_cu_fe_comparison.json",
                "overall_status": "needs_improvement",
                "priority": "high",
                "failing_metrics": ["parse_success_rate"],
                "actions": [_prompt_action()],
            }
        )

    with pytest.raises(ValidationError):
        LlmCampaignLineage.model_validate(_lineage(approval_path=" "))

    with pytest.raises(ValidationError):
        LlmCampaignSpec.model_validate(
            {
                "campaign_id": "campaign_1",
                "proposal_id": "proposal_1",
                "approval_id": "approval_1",
                "system": "Al-Cu-Fe",
                "created_at_utc": "2026-04-04T00:15:00Z",
                "actions": [],
                "launch_baseline": _launch_baseline(),
                "lineage": _lineage(),
            }
        )


def test_launch_baseline_rejects_default_count_below_one() -> None:
    with pytest.raises(ValidationError):
        LlmCampaignLaunchBaseline.model_validate(_launch_baseline(default_count=0))
