from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmAcceptanceSystemMetrics,
    LlmCampaignAction,
    LlmCampaignProposal,
    LlmCampaignProposalSummary,
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
