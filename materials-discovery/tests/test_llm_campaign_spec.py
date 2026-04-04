from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.common.io import load_json_object, load_yaml, write_json_object
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.campaigns import (
    build_campaign_proposals,
    create_campaign_approval,
    materialize_campaign_spec,
)
from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmAcceptanceSystemMetrics,
    LlmAcceptanceThresholds,
)
from materials_discovery.llm.storage import (
    llm_acceptance_approval_path,
    llm_acceptance_pack_path,
    llm_acceptance_proposal_path,
    llm_campaign_spec_path,
)


def _system_metrics(
    system: str,
    *,
    failing_metrics: list[str] | None = None,
    report_release_gate_ready: bool = True,
    passed: bool | None = None,
) -> LlmAcceptanceSystemMetrics:
    normalized_failing_metrics = list(failing_metrics or [])
    return LlmAcceptanceSystemMetrics(
        system=system,
        generate_comparison_path=f"data/benchmarks/llm_generate/{system.lower().replace('-', '_')}.json",
        pipeline_comparison_path=f"data/benchmarks/llm_pipeline/{system.lower().replace('-', '_')}.json",
        parse_success_rate=0.95,
        compile_success_rate=0.92,
        generation_success_rate=0.40,
        shortlist_pass_rate=0.12,
        validation_pass_rate=0.08,
        novelty_score_mean=0.20,
        synthesizability_mean=0.71,
        report_release_gate_ready=report_release_gate_ready,
        failing_metrics=normalized_failing_metrics,
        passed=(not normalized_failing_metrics) if passed is None else passed,
    )


def _acceptance_pack(
    *systems: LlmAcceptanceSystemMetrics,
    overall_passed: bool | None = None,
) -> LlmAcceptancePack:
    return LlmAcceptancePack(
        pack_id="acceptance_demo",
        created_at_utc="2026-04-04T00:00:00Z",
        eval_set_manifest_path="data/llm_eval_sets/eval_demo/manifest.json",
        thresholds=LlmAcceptanceThresholds(),
        systems=list(systems),
        overall_passed=all(system.passed for system in systems)
        if overall_passed is None
        else overall_passed,
    )


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_system_config(config_name: str) -> tuple[SystemConfig, Path]:
    config_path = _workspace() / "configs" / "systems" / config_name
    return SystemConfig.model_validate(load_yaml(config_path)), config_path


def _write_proposal_fixture(tmp_path: Path) -> tuple[Path, object]:
    pack = _acceptance_pack(
        _system_metrics(
            "Al-Cu-Fe",
            failing_metrics=["parse_success_rate", "compile_success_rate"],
            passed=False,
        )
    )
    acceptance_pack_path = llm_acceptance_pack_path(pack.pack_id, root=tmp_path)
    write_json_object(pack.model_dump(mode="json"), acceptance_pack_path)

    proposal = build_campaign_proposals(pack, acceptance_pack_path=acceptance_pack_path)[0]
    proposal_path = llm_acceptance_proposal_path(pack.pack_id, proposal.proposal_id, root=tmp_path)
    write_json_object(proposal.model_dump(mode="json"), proposal_path)
    return proposal_path, proposal


def test_materialize_campaign_spec_for_approved_proposal_is_deterministic(tmp_path: Path) -> None:
    proposal_path, proposal = _write_proposal_fixture(tmp_path)
    approval = create_campaign_approval(
        proposal,
        proposal_path=proposal_path,
        decision="approved",
        operator="operator@example.com",
        decided_at_utc="2026-04-04T02:00:00Z",
    )
    approval_path = llm_acceptance_approval_path(proposal.pack_id, approval.approval_id, root=tmp_path)
    write_json_object(approval.model_dump(mode="json"), approval_path)

    system_config, config_path = _load_system_config("al_cu_fe_llm_mock.yaml")
    spec = materialize_campaign_spec(
        proposal,
        approval,
        approval_path=approval_path,
        system_config=system_config,
        system_config_path=config_path,
    )
    spec_again = materialize_campaign_spec(
        proposal,
        approval,
        approval_path=approval_path,
        system_config=system_config,
        system_config_path=config_path,
    )
    spec_path = llm_campaign_spec_path(spec.campaign_id, root=tmp_path)
    write_json_object(spec.model_dump(mode="json"), spec_path)

    assert spec == spec_again
    assert spec_path.exists()
    assert load_json_object(spec_path) == spec.model_dump(mode="json")
    assert spec.campaign_id == approval.campaign_id
    assert spec.launch_baseline.system_config_hash == config_sha256(system_config)
    assert spec.launch_baseline.system_config_path == str(config_path)
    assert spec.launch_baseline.system == proposal.system
    assert spec.launch_baseline.prompt_template == system_config.llm_generate.prompt_template
    assert spec.lineage.acceptance_pack_path == proposal.acceptance_pack_path
    assert spec.lineage.proposal_path == str(proposal_path)
    assert spec.lineage.approval_path == str(approval_path)
    assert spec.lineage.eval_set_manifest_path == proposal.eval_set_manifest_path


def test_rejected_campaign_approval_writes_no_campaign_spec(tmp_path: Path) -> None:
    proposal_path, proposal = _write_proposal_fixture(tmp_path)
    approval = create_campaign_approval(
        proposal,
        proposal_path=proposal_path,
        decision="rejected",
        operator="operator@example.com",
        notes="Need stronger exact-match conditioning first.",
        decided_at_utc="2026-04-04T02:05:00Z",
    )
    approval_path = llm_acceptance_approval_path(proposal.pack_id, approval.approval_id, root=tmp_path)
    write_json_object(approval.model_dump(mode="json"), approval_path)

    system_config, config_path = _load_system_config("al_cu_fe_llm_mock.yaml")
    with pytest.raises(ValueError):
        materialize_campaign_spec(
            proposal,
            approval,
            approval_path=approval_path,
            system_config=system_config,
            system_config_path=config_path,
        )

    assert approval_path.exists()
    assert approval.campaign_id is None
    assert not (tmp_path / "data" / "llm_campaigns").exists()


def test_reapproving_same_proposal_creates_new_approval_and_campaign_ids(tmp_path: Path) -> None:
    proposal_path, proposal = _write_proposal_fixture(tmp_path)
    system_config, config_path = _load_system_config("al_cu_fe_llm_mock.yaml")

    first_approval = create_campaign_approval(
        proposal,
        proposal_path=proposal_path,
        decision="approved",
        operator="operator@example.com",
        decided_at_utc="2026-04-04T02:10:00Z",
    )
    first_approval_path = llm_acceptance_approval_path(
        proposal.pack_id,
        first_approval.approval_id,
        root=tmp_path,
    )
    write_json_object(first_approval.model_dump(mode="json"), first_approval_path)
    first_spec = materialize_campaign_spec(
        proposal,
        first_approval,
        approval_path=first_approval_path,
        system_config=system_config,
        system_config_path=config_path,
    )
    first_spec_path = llm_campaign_spec_path(first_spec.campaign_id, root=tmp_path)
    write_json_object(first_spec.model_dump(mode="json"), first_spec_path)

    second_approval = create_campaign_approval(
        proposal,
        proposal_path=proposal_path,
        decision="approved",
        operator="operator@example.com",
        notes="Approved after second review.",
        decided_at_utc="2026-04-04T02:15:00Z",
    )
    second_approval_path = llm_acceptance_approval_path(
        proposal.pack_id,
        second_approval.approval_id,
        root=tmp_path,
    )
    write_json_object(second_approval.model_dump(mode="json"), second_approval_path)
    second_spec = materialize_campaign_spec(
        proposal,
        second_approval,
        approval_path=second_approval_path,
        system_config=system_config,
        system_config_path=config_path,
    )
    second_spec_path = llm_campaign_spec_path(second_spec.campaign_id, root=tmp_path)
    write_json_object(second_spec.model_dump(mode="json"), second_spec_path)

    assert first_approval.approval_id != second_approval.approval_id
    assert first_spec.campaign_id != second_spec.campaign_id
    assert first_spec_path.exists()
    assert second_spec_path.exists()
