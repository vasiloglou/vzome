from __future__ import annotations

from pathlib import Path

from materials_discovery.llm.campaigns import (
    build_campaign_proposals,
    summarize_campaign_proposals,
)
from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmAcceptanceSystemMetrics,
    LlmAcceptanceThresholds,
)
from materials_discovery.llm.storage import llm_acceptance_proposal_path


def _system_metrics(
    system: str,
    *,
    failing_metrics: list[str] | None = None,
    report_release_gate_ready: bool = True,
    parse_success_rate: float = 0.95,
    compile_success_rate: float = 0.92,
    generation_success_rate: float = 0.40,
    shortlist_pass_rate: float = 0.12,
    validation_pass_rate: float = 0.08,
    novelty_score_mean: float = 0.20,
    synthesizability_mean: float = 0.71,
    passed: bool | None = None,
) -> LlmAcceptanceSystemMetrics:
    normalized_failing_metrics = list(failing_metrics or [])
    return LlmAcceptanceSystemMetrics(
        system=system,
        generate_comparison_path=f"data/benchmarks/llm_generate/{system.lower().replace('-', '_')}.json",
        pipeline_comparison_path=f"data/benchmarks/llm_pipeline/{system.lower().replace('-', '_')}.json",
        parse_success_rate=parse_success_rate,
        compile_success_rate=compile_success_rate,
        generation_success_rate=generation_success_rate,
        shortlist_pass_rate=shortlist_pass_rate,
        validation_pass_rate=validation_pass_rate,
        novelty_score_mean=novelty_score_mean,
        synthesizability_mean=synthesizability_mean,
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


def test_build_campaign_proposals_is_system_scoped_and_action_ids_are_stable() -> None:
    pack = _acceptance_pack(
        _system_metrics("Al-Cu-Fe", failing_metrics=["parse_success_rate", "compile_success_rate"]),
        _system_metrics("Sc-Zn", failing_metrics=["shortlist_pass_rate", "validation_pass_rate"]),
    )

    first = build_campaign_proposals(
        pack,
        acceptance_pack_path=Path("data/benchmarks/llm_acceptance/acceptance_demo/acceptance_pack.json"),
    )
    second = build_campaign_proposals(
        pack,
        acceptance_pack_path=Path("data/benchmarks/llm_acceptance/acceptance_demo/acceptance_pack.json"),
    )

    assert [proposal.system for proposal in first] == ["Al-Cu-Fe", "Sc-Zn"]
    assert len(first) == len(pack.systems)
    assert len({proposal.proposal_id for proposal in first}) == len(first)
    assert [proposal.proposal_id for proposal in first] == [proposal.proposal_id for proposal in second]
    assert [
        [action.action_id for action in proposal.actions]
        for proposal in first
    ] == [
        [action.action_id for action in proposal.actions]
        for proposal in second
    ]
    for proposal in first:
        action_ids = [action.action_id for action in proposal.actions]
        assert len(action_ids) == len(set(action_ids))


def test_build_campaign_proposals_maps_parse_compile_failures_to_prompt_conditioning() -> None:
    pack = _acceptance_pack(
        _system_metrics(
            "Al-Cu-Fe",
            failing_metrics=["parse_success_rate", "compile_success_rate"],
            parse_success_rate=0.45,
            compile_success_rate=0.42,
            passed=False,
        )
    )

    proposal = build_campaign_proposals(
        pack,
        acceptance_pack_path=Path("data/benchmarks/llm_acceptance/acceptance_demo/acceptance_pack.json"),
    )[0]

    assert proposal.priority == "high"
    assert proposal.overall_status == "needs_improvement"
    assert proposal.failing_metrics == ["parse_success_rate", "compile_success_rate"]
    assert len(proposal.actions) == 1
    action = proposal.actions[0]
    assert action.family == "prompt_conditioning"
    assert action.priority == "high"
    assert set(action.evidence_metrics) == {"parse_success_rate", "compile_success_rate"}
    assert action.preferred_model_lane == "general_purpose"


def test_build_campaign_proposals_maps_pass_through_weakness_to_campaign_actions() -> None:
    pack = _acceptance_pack(
        _system_metrics(
            "Sc-Zn",
            failing_metrics=["shortlist_pass_rate", "validation_pass_rate"],
            shortlist_pass_rate=0.01,
            validation_pass_rate=0.00,
            passed=False,
        )
    )

    proposal = build_campaign_proposals(
        pack,
        acceptance_pack_path=Path("data/benchmarks/llm_acceptance/acceptance_demo/acceptance_pack.json"),
    )[0]

    action_families = {action.family for action in proposal.actions}
    evidence_metrics = {
        metric
        for action in proposal.actions
        for metric in action.evidence_metrics
    }

    assert proposal.priority == "high"
    assert action_families
    assert action_families.issubset({"composition_window", "prompt_conditioning"})
    assert {"shortlist_pass_rate", "validation_pass_rate"}.issubset(evidence_metrics)
    assert all(action.priority == "high" for action in proposal.actions)


def test_build_campaign_proposals_maps_synthesizability_to_specialized_materials_lane() -> None:
    pack = _acceptance_pack(
        _system_metrics(
            "Ti-Zr-Ni",
            failing_metrics=["synthesizability_mean"],
            synthesizability_mean=0.31,
            passed=False,
        )
    )

    proposal = build_campaign_proposals(
        pack,
        acceptance_pack_path=Path("data/benchmarks/llm_acceptance/acceptance_demo/acceptance_pack.json"),
    )[0]

    assert proposal.priority == "medium"
    assert len(proposal.actions) == 1
    action = proposal.actions[0]
    assert action.family == "prompt_conditioning"
    assert action.priority == "medium"
    assert action.evidence_metrics == ["synthesizability_mean"]
    assert action.preferred_model_lane == "specialized_materials"
    assert action.specialized_model_family == "csllm_inspired"


def test_build_campaign_proposals_keeps_release_gate_and_healthy_systems_dry_run() -> None:
    pack = _acceptance_pack(
        _system_metrics("Al-Cu-Fe", report_release_gate_ready=False),
        _system_metrics("Sc-Zn"),
    )

    proposals = build_campaign_proposals(
        pack,
        acceptance_pack_path=Path("data/benchmarks/llm_acceptance/acceptance_demo/acceptance_pack.json"),
    )

    proposal_by_system = {proposal.system: proposal for proposal in proposals}
    gate_proposal = proposal_by_system["Al-Cu-Fe"]
    healthy_proposal = proposal_by_system["Sc-Zn"]

    assert gate_proposal.overall_status == "ready"
    assert gate_proposal.priority == "medium"
    assert any(
        "release" in action.title.lower()
        or "audit" in action.title.lower()
        or "release" in action.rationale.lower()
        for action in gate_proposal.actions
    )
    assert healthy_proposal.overall_status == "ready"
    assert healthy_proposal.priority == "low"
    assert all(action.priority == "low" for action in healthy_proposal.actions)


def test_summarize_campaign_proposals_points_to_deterministic_proposal_paths(
    tmp_path: Path,
) -> None:
    pack = _acceptance_pack(
        _system_metrics("Al-Cu-Fe", report_release_gate_ready=False),
        _system_metrics("Sc-Zn", failing_metrics=["synthesizability_mean"], passed=False),
        overall_passed=False,
    )
    proposals = build_campaign_proposals(
        pack,
        acceptance_pack_path=Path("data/benchmarks/llm_acceptance/acceptance_demo/acceptance_pack.json"),
    )
    proposal_paths = {
        proposal.proposal_id: llm_acceptance_proposal_path(
            pack.pack_id,
            proposal.proposal_id,
            root=tmp_path,
        )
        for proposal in proposals
    }

    suggestion = summarize_campaign_proposals(
        pack,
        proposals,
        proposal_paths=proposal_paths,
    )

    assert suggestion.overall_status == "needs_improvement"
    assert suggestion.proposal_count == 2
    assert [summary.proposal_path for summary in suggestion.proposals] == [
        str(proposal_paths[proposal.proposal_id]) for proposal in proposals
    ]
    assert suggestion.proposals[0].system == "Al-Cu-Fe"
    assert suggestion.proposals[1].system == "Sc-Zn"
