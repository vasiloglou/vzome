from __future__ import annotations

import json
from pathlib import Path

from pytest import MonkeyPatch
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_json_object, write_json_object
from materials_discovery.llm.campaigns import build_campaign_proposals
from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmAcceptanceSystemMetrics,
    LlmAcceptanceThresholds,
)
from materials_discovery.llm.storage import llm_acceptance_pack_path, llm_acceptance_proposal_path


def _system_metrics(system: str) -> LlmAcceptanceSystemMetrics:
    return LlmAcceptanceSystemMetrics(
        system=system,
        generate_comparison_path=f"data/benchmarks/llm_generate/{system.lower().replace('-', '_')}.json",
        pipeline_comparison_path=f"data/benchmarks/llm_pipeline/{system.lower().replace('-', '_')}.json",
        parse_success_rate=0.45,
        compile_success_rate=0.40,
        generation_success_rate=0.40,
        shortlist_pass_rate=0.12,
        validation_pass_rate=0.08,
        novelty_score_mean=0.20,
        synthesizability_mean=0.71,
        report_release_gate_ready=False,
        failing_metrics=["parse_success_rate", "compile_success_rate"],
        passed=False,
    )


def _proposal_fixture(tmp_path: Path) -> Path:
    pack = LlmAcceptancePack(
        pack_id="acceptance_demo",
        created_at_utc="2026-04-04T00:00:00Z",
        eval_set_manifest_path="data/llm_eval_sets/eval_demo/manifest.json",
        thresholds=LlmAcceptanceThresholds(),
        systems=[_system_metrics("Al-Cu-Fe")],
        overall_passed=False,
    )
    acceptance_pack_path = llm_acceptance_pack_path(pack.pack_id, root=tmp_path)
    write_json_object(pack.model_dump(mode="json"), acceptance_pack_path)
    proposal = build_campaign_proposals(pack, acceptance_pack_path=acceptance_pack_path)[0]
    proposal_path = llm_acceptance_proposal_path(pack.pack_id, proposal.proposal_id, root=tmp_path)
    write_json_object(proposal.model_dump(mode="json"), proposal_path)
    return proposal_path


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _fail_if_called(*args: object, **kwargs: object) -> None:
    raise AssertionError("Phase 10 approval must not launch downstream LLM execution")


def test_llm_approve_approved_writes_approval_and_spec_without_launching(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    proposal_path = _proposal_fixture(tmp_path)
    config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"

    monkeypatch.setattr("materials_discovery.cli.generate_llm_candidates", _fail_if_called)
    monkeypatch.setattr("materials_discovery.cli.evaluate_llm_candidates", _fail_if_called)

    result = runner.invoke(
        app,
        [
            "llm-approve",
            "--proposal",
            str(proposal_path),
            "--decision",
            "approved",
            "--operator",
            "operator@example.com",
            "--config",
            str(config_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    approval_path = Path(payload["approval_path"])
    spec_path = Path(payload["campaign_spec_path"])
    assert approval_path.exists()
    assert spec_path.exists()
    assert load_json_object(approval_path)["decision"] == "approved"
    assert load_json_object(spec_path)["proposal_id"] == load_json_object(approval_path)["proposal_id"]


def test_llm_approve_rejected_writes_only_approval_artifact(tmp_path: Path) -> None:
    runner = CliRunner()
    proposal_path = _proposal_fixture(tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-approve",
            "--proposal",
            str(proposal_path),
            "--decision",
            "rejected",
            "--operator",
            "operator@example.com",
            "--notes",
            "Need stronger exact examples first.",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    approval_path = Path(payload["approval_path"])
    assert approval_path.exists()
    assert payload["campaign_id"] is None
    assert payload["campaign_spec_path"] is None
    assert not (tmp_path / "data" / "llm_campaigns").exists()


def test_llm_approve_requires_operator_identity(tmp_path: Path) -> None:
    runner = CliRunner()
    proposal_path = _proposal_fixture(tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-approve",
            "--proposal",
            str(proposal_path),
            "--decision",
            "rejected",
            "--operator",
            "   ",
        ],
    )

    assert result.exit_code == 2
    assert "llm-approve failed" in result.output


def test_llm_approve_requires_config_for_approved_decisions(tmp_path: Path) -> None:
    runner = CliRunner()
    proposal_path = _proposal_fixture(tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-approve",
            "--proposal",
            str(proposal_path),
            "--decision",
            "approved",
            "--operator",
            "operator@example.com",
        ],
    )

    assert result.exit_code == 2
    assert "llm-approve failed" in result.output
