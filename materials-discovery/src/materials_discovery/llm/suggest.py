from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import write_json_object
from materials_discovery.llm.campaigns import (
    build_campaign_proposals,
    summarize_campaign_proposals,
)
from materials_discovery.llm.schema import LlmAcceptancePack, LlmCampaignProposal, LlmCampaignSuggestion


def _proposal_path(acceptance_pack_path: Path, proposal_id: str) -> Path:
    return acceptance_pack_path.parent / "proposals" / f"{proposal_id}.json"


def _prepare_suggestion_bundle(
    pack: LlmAcceptancePack,
    *,
    acceptance_pack_path: Path,
) -> tuple[LlmCampaignSuggestion, list[LlmCampaignProposal], dict[str, Path]]:
    proposals = build_campaign_proposals(pack, acceptance_pack_path=acceptance_pack_path)
    proposal_paths = {
        proposal.proposal_id: _proposal_path(acceptance_pack_path, proposal.proposal_id)
        for proposal in proposals
    }
    suggestions = summarize_campaign_proposals(
        pack,
        proposals,
        proposal_paths=proposal_paths,
    )
    return suggestions, proposals, proposal_paths


def build_llm_suggestions(
    pack: LlmAcceptancePack,
    *,
    acceptance_pack_path: Path,
) -> LlmCampaignSuggestion:
    suggestions, _, _ = _prepare_suggestion_bundle(
        pack,
        acceptance_pack_path=acceptance_pack_path,
    )
    return suggestions


def write_llm_suggestions(
    pack: LlmAcceptancePack,
    *,
    acceptance_pack_path: Path,
    out_path: Path | None = None,
) -> Path:
    suggestions, proposals, proposal_paths = _prepare_suggestion_bundle(
        pack,
        acceptance_pack_path=acceptance_pack_path,
    )
    for proposal in proposals:
        write_json_object(
            proposal.model_dump(mode="json"),
            proposal_paths[proposal.proposal_id],
        )
    resolved_out_path = out_path or acceptance_pack_path.with_name("suggestions.json")
    write_json_object(suggestions.model_dump(mode="json"), resolved_out_path)
    return resolved_out_path
