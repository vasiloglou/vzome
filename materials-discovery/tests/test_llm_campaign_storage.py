from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.llm.storage import (
    llm_acceptance_approval_path,
    llm_acceptance_proposal_path,
    llm_acceptance_proposals_dir,
    llm_acceptance_suggestion_path,
    llm_campaign_dir,
    llm_campaign_spec_path,
)


def test_acceptance_suggestion_path_stays_under_pack_root(tmp_path: Path) -> None:
    assert llm_acceptance_suggestion_path("pack_v1", root=tmp_path) == (
        tmp_path / "data" / "benchmarks" / "llm_acceptance" / "pack_v1" / "suggestions.json"
    )


def test_proposal_and_approval_artifacts_live_under_acceptance_pack_root(tmp_path: Path) -> None:
    proposals_dir = llm_acceptance_proposals_dir("pack_v1", root=tmp_path)

    assert proposals_dir == tmp_path / "data" / "benchmarks" / "llm_acceptance" / "pack_v1" / "proposals"
    assert llm_acceptance_proposal_path("pack_v1", "proposal_1", root=tmp_path) == (
        proposals_dir / "proposal_1.json"
    )
    assert llm_acceptance_approval_path("pack_v1", "approval_1", root=tmp_path) == (
        tmp_path / "data" / "benchmarks" / "llm_acceptance" / "pack_v1" / "approvals" / "approval_1.json"
    )


def test_campaign_spec_helpers_use_dedicated_campaign_root(tmp_path: Path) -> None:
    campaign_root = llm_campaign_dir("campaign_1", root=tmp_path)

    assert campaign_root == tmp_path / "data" / "llm_campaigns" / "campaign_1"
    assert llm_campaign_spec_path("campaign_1", root=tmp_path) == campaign_root / "campaign_spec.json"


def test_storage_helpers_honor_optional_root_override(tmp_path: Path) -> None:
    override_root = tmp_path / "isolated"

    assert llm_acceptance_proposal_path("pack_v1", "proposal_1", root=override_root) == (
        override_root
        / "data"
        / "benchmarks"
        / "llm_acceptance"
        / "pack_v1"
        / "proposals"
        / "proposal_1.json"
    )
    assert llm_campaign_spec_path("campaign_1", root=override_root) == (
        override_root / "data" / "llm_campaigns" / "campaign_1" / "campaign_spec.json"
    )


@pytest.mark.parametrize(
    ("factory", "args"),
    [
        (llm_acceptance_suggestion_path, (" ",)),
        (llm_acceptance_proposals_dir, (" ",)),
        (llm_acceptance_proposal_path, ("pack_v1", " ")),
        (llm_acceptance_approval_path, ("pack_v1", " ")),
        (llm_campaign_dir, (" ",)),
        (llm_campaign_spec_path, (" ",)),
    ],
)
def test_storage_helpers_reject_blank_ids(factory: object, args: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        factory(*args)  # type: ignore[misc]
