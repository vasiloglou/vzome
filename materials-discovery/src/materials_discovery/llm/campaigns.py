from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmAcceptanceSystemMetrics,
    LlmCampaignAction,
    LlmCampaignApproval,
    LlmCampaignLaunchBaseline,
    LlmCampaignLineage,
    LlmCampaignProposal,
    LlmCampaignProposalSummary,
    LlmCampaignSpec,
    LlmCampaignSuggestion,
    LlmCompositionWindowActionData,
    LlmPromptConditioningActionData,
    LlmSeedMotifVariationActionData,
)


def _system_slug(value: str) -> str:
    slug = value.strip().lower().replace("-", "_").replace(" ", "_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug


def _proposal_id(pack_id: str, system: str) -> str:
    return f"{pack_id}_{_system_slug(system)}"


def _action_id(proposal_id: str, ordinal: int) -> str:
    return f"{proposal_id}_action_{ordinal:02d}"


def _digest(*parts: str) -> str:
    payload = "||".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _approval_id(
    proposal_id: str,
    *,
    decision: str,
    operator: str,
    decided_at_utc: str,
    notes: str | None,
) -> str:
    digest = _digest(
        proposal_id,
        decision,
        operator.strip(),
        decided_at_utc,
        (notes or "").strip(),
    )
    return f"{proposal_id}_approval_{digest[:12]}"


def _campaign_id(proposal: LlmCampaignProposal, approval_id: str) -> str:
    digest = _digest(proposal.proposal_id, approval_id)
    return f"{_system_slug(proposal.system)}_{digest[:16]}"


def _overall_status(pack: LlmAcceptancePack) -> str:
    return "ready" if pack.overall_passed else "needs_improvement"


def _focus_species(system: str) -> list[str]:
    return [token.strip() for token in system.split("-") if token.strip()]


def _parse_compile_actions(
    system: LlmAcceptanceSystemMetrics,
    proposal_id: str,
) -> tuple[str, list[LlmCampaignAction]]:
    evidence_metrics = [
        metric
        for metric in ("parse_success_rate", "compile_success_rate")
        if metric in system.failing_metrics
    ]
    return (
        "high",
        [
            LlmCampaignAction(
                action_id=_action_id(proposal_id, 1),
                family="prompt_conditioning",
                title="Tighten prompt validity conditioning",
                rationale=(
                    "Parse or compile reliability is below the acceptance threshold, so "
                    "the next dry-run proposal should tighten prompt constraints before "
                    "widening the search."
                ),
                priority="high",
                evidence_metrics=evidence_metrics,
                preferred_model_lane="general_purpose",
                prompt_conditioning=LlmPromptConditioningActionData(
                    instruction_delta=(
                        "Emphasize parser-safe Zomic syntax, bounded operator use, and "
                        "system-matched exact examples."
                    ),
                    conditioning_strategy="increase_exact_system_examples",
                    target_example_family="acceptance_pack_exact_matches",
                    preferred_max_conditioning_examples=6,
                ),
            )
        ],
    )


def _pass_through_actions(
    system: LlmAcceptanceSystemMetrics,
    proposal_id: str,
) -> tuple[str, list[LlmCampaignAction]]:
    evidence_metrics = [
        metric
        for metric in ("shortlist_pass_rate", "validation_pass_rate")
        if metric in system.failing_metrics
    ]
    focus_species = _focus_species(system.system)
    return (
        "high",
        [
            LlmCampaignAction(
                action_id=_action_id(proposal_id, 1),
                family="composition_window",
                title="Narrow the composition window around validated chemistry",
                rationale=(
                    "The lane is producing candidates, but too few survive screening or "
                    "digital validation; tighten the composition window before approval."
                ),
                priority="high",
                evidence_metrics=evidence_metrics,
                preferred_model_lane="general_purpose",
                composition_window=LlmCompositionWindowActionData(
                    window_strategy="tighten_around_validated_hits",
                    focus_species=focus_species,
                ),
            ),
            LlmCampaignAction(
                action_id=_action_id(proposal_id, 2),
                family="prompt_conditioning",
                title="Bias prompt conditioning toward accepted exemplars",
                rationale=(
                    "The next dry-run iteration should favor examples that already pass "
                    "screening and validation for this chemistry."
                ),
                priority="high",
                evidence_metrics=evidence_metrics,
                preferred_model_lane="general_purpose",
                prompt_conditioning=LlmPromptConditioningActionData(
                    instruction_delta=(
                        "Prefer benchmark-aligned examples and reject broad exploratory "
                        "motifs that do not survive downstream filtering."
                    ),
                    conditioning_strategy="bias_to_accepted_examples",
                    target_example_family="accepted_validation_examples",
                    preferred_max_conditioning_examples=6,
                ),
            ),
        ],
    )


def _synthesizability_actions(
    proposal_id: str,
) -> tuple[str, list[LlmCampaignAction]]:
    return (
        "medium",
        [
            LlmCampaignAction(
                action_id=_action_id(proposal_id, 1),
                family="prompt_conditioning",
                title="Shift conditioning toward synthesis-aware exemplars",
                rationale=(
                    "Structural validity is acceptable, but synthesizability remains "
                    "weak, so the dry-run proposal should prefer materials-aware "
                    "conditioning before launch."
                ),
                priority="medium",
                evidence_metrics=["synthesizability_mean"],
                preferred_model_lane="specialized_materials",
                specialized_model_family="csllm_inspired",
                prompt_conditioning=LlmPromptConditioningActionData(
                    instruction_delta=(
                        "Favor examples and instructions that surface precursor realism, "
                        "synthesis plausibility, and known QC-family context."
                    ),
                    conditioning_strategy="synthesis_aware_examples",
                    target_example_family="synthesizability_anchors",
                    preferred_max_conditioning_examples=4,
                ),
            )
        ],
    )


def _release_gate_actions(
    proposal_id: str,
) -> tuple[str, list[LlmCampaignAction]]:
    return (
        "medium",
        [
            LlmCampaignAction(
                action_id=_action_id(proposal_id, 1),
                family="prompt_conditioning",
                title="Keep the lane in audit mode until the release gate is ready",
                rationale=(
                    "Core metrics are acceptable, but the release gate is not ready yet, "
                    "so keep this proposal dry-run and gather more evidence before any "
                    "approval decision."
                ),
                priority="medium",
                evidence_metrics=[],
                preferred_model_lane="general_purpose",
                prompt_conditioning=LlmPromptConditioningActionData(
                    instruction_delta=(
                        "Preserve the current prompt shape and collect one more benchmark "
                        "iteration before promoting the lane."
                    ),
                    conditioning_strategy="audit_only_hold",
                    target_example_family="current_release_candidate",
                    preferred_max_conditioning_examples=3,
                ),
            )
        ],
    )


def _healthy_actions(
    proposal_id: str,
) -> tuple[str, list[LlmCampaignAction]]:
    return (
        "low",
        [
            LlmCampaignAction(
                action_id=_action_id(proposal_id, 1),
                family="seed_motif_variation",
                title="Explore low-risk motif variants in dry-run mode",
                rationale=(
                    "Acceptance metrics and release posture look healthy enough for a "
                    "low-priority exploratory proposal, but approval still remains a "
                    "separate later step."
                ),
                priority="low",
                evidence_metrics=[],
                preferred_model_lane="general_purpose",
                seed_motif_variation=LlmSeedMotifVariationActionData(
                    variation_strategy="explore_neighboring_seed_motifs",
                    seed_source_hint="accepted_examples",
                    motif_tags=["dry_run_exploratory"],
                ),
            )
        ],
    )


def _build_actions(
    system: LlmAcceptanceSystemMetrics,
    proposal_id: str,
) -> tuple[str, list[LlmCampaignAction]]:
    if "parse_success_rate" in system.failing_metrics or "compile_success_rate" in system.failing_metrics:
        return _parse_compile_actions(system, proposal_id)
    if "shortlist_pass_rate" in system.failing_metrics or "validation_pass_rate" in system.failing_metrics:
        return _pass_through_actions(system, proposal_id)
    if "synthesizability_mean" in system.failing_metrics:
        return _synthesizability_actions(proposal_id)
    if not system.report_release_gate_ready:
        return _release_gate_actions(proposal_id)
    return _healthy_actions(proposal_id)


def build_campaign_proposals(
    pack: LlmAcceptancePack,
    *,
    acceptance_pack_path: Path,
) -> list[LlmCampaignProposal]:
    generated_at_utc = datetime.now(UTC).isoformat()
    overall_status = _overall_status(pack)
    proposals: list[LlmCampaignProposal] = []

    for system in pack.systems:
        proposal_id = _proposal_id(pack.pack_id, system.system)
        priority, actions = _build_actions(system, proposal_id)
        proposals.append(
            LlmCampaignProposal(
                proposal_id=proposal_id,
                pack_id=pack.pack_id,
                system=system.system,
                generated_at_utc=generated_at_utc,
                acceptance_pack_path=str(acceptance_pack_path),
                eval_set_manifest_path=pack.eval_set_manifest_path,
                generate_comparison_path=system.generate_comparison_path,
                pipeline_comparison_path=system.pipeline_comparison_path,
                overall_status=overall_status,
                priority=priority,
                failing_metrics=system.failing_metrics,
                actions=actions,
            )
        )

    return proposals


def summarize_campaign_proposals(
    pack: LlmAcceptancePack,
    proposals: list[LlmCampaignProposal],
    *,
    proposal_paths: dict[str, Path],
) -> LlmCampaignSuggestion:
    summaries: list[LlmCampaignProposalSummary] = []
    for proposal in proposals:
        proposal_path = proposal_paths.get(proposal.proposal_id)
        if proposal_path is None:
            raise ValueError(f"missing proposal path for {proposal.proposal_id}")
        summaries.append(
            LlmCampaignProposalSummary(
                proposal_id=proposal.proposal_id,
                system=proposal.system,
                priority=proposal.priority,
                failing_metrics=proposal.failing_metrics,
                action_families=[action.family for action in proposal.actions],
                proposal_path=str(proposal_path),
            )
        )
    return LlmCampaignSuggestion(
        pack_id=pack.pack_id,
        overall_status=_overall_status(pack),
        generated_at_utc=datetime.now(UTC).isoformat(),
        proposal_count=len(summaries),
        proposals=summaries,
    )


def create_campaign_approval(
    proposal: LlmCampaignProposal,
    *,
    proposal_path: Path,
    decision: str,
    operator: str,
    notes: str | None = None,
    decided_at_utc: str | None = None,
) -> LlmCampaignApproval:
    decision_value = decision.strip().lower()
    decided_at = decided_at_utc or datetime.now(UTC).isoformat()
    approval_id = _approval_id(
        proposal.proposal_id,
        decision=decision_value,
        operator=operator,
        decided_at_utc=decided_at,
        notes=notes,
    )
    campaign_id = (
        _campaign_id(proposal, approval_id)
        if decision_value == "approved"
        else None
    )
    return LlmCampaignApproval(
        approval_id=approval_id,
        proposal_id=proposal.proposal_id,
        proposal_path=str(proposal_path),
        decision=decision_value,
        operator=operator,
        decided_at_utc=decided_at,
        notes=notes,
        campaign_id=campaign_id,
    )


def materialize_campaign_spec(
    proposal: LlmCampaignProposal,
    approval: LlmCampaignApproval,
    *,
    approval_path: Path,
    system_config: SystemConfig,
    system_config_path: Path,
) -> LlmCampaignSpec:
    if approval.decision != "approved" or approval.campaign_id is None:
        raise ValueError("only approved proposals can be materialized into campaign specs")
    if approval.proposal_id != proposal.proposal_id:
        raise ValueError("approval proposal_id must match the proposal being materialized")
    if system_config.system_name != proposal.system:
        raise ValueError("system config system_name must match the proposal system")

    llm_generate = system_config.llm_generate
    launch_baseline = LlmCampaignLaunchBaseline(
        system_config_path=str(system_config_path),
        system_config_hash=config_sha256(system_config),
        system=system_config.system_name,
        template_family=system_config.template_family,
        default_count=system_config.default_count,
        composition_bounds=system_config.composition_bounds,
        prompt_template=llm_generate.prompt_template if llm_generate is not None else None,
        example_pack_path=llm_generate.example_pack_path if llm_generate is not None else None,
        max_conditioning_examples=(
            llm_generate.max_conditioning_examples if llm_generate is not None else None
        ),
        seed_zomic_path=llm_generate.seed_zomic if llm_generate is not None else None,
    )
    lineage = LlmCampaignLineage(
        acceptance_pack_path=proposal.acceptance_pack_path,
        eval_set_manifest_path=proposal.eval_set_manifest_path,
        proposal_path=approval.proposal_path,
        approval_path=str(approval_path),
        source_system_config_path=str(system_config_path),
        source_system_config_hash=config_sha256(system_config),
    )
    return LlmCampaignSpec(
        campaign_id=approval.campaign_id,
        proposal_id=proposal.proposal_id,
        approval_id=approval.approval_id,
        system=proposal.system,
        created_at_utc=approval.decided_at_utc,
        actions=[action.model_copy(deep=True) for action in proposal.actions],
        launch_baseline=launch_baseline,
        lineage=lineage,
    )
