from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from materials_discovery.common.io import load_yaml, write_jsonl
from materials_discovery.common.schema import CompositionBound, LlmModelLaneConfig, SystemConfig
from materials_discovery.llm.checkpoints import promote_checkpoint, register_llm_checkpoint
from materials_discovery.llm.schema import (
    LlmCampaignAction,
    LlmCampaignLaunchBaseline,
    LlmCampaignLineage,
    LlmCampaignSpec,
    LlmCompositionWindowActionData,
    LlmEvalSetExample,
    LlmPromptConditioningActionData,
    LlmSeedMotifVariationActionData,
)


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _config_data() -> dict[str, object]:
    return load_yaml(_workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml")


def _base_config(*, include_model_lanes: bool = True) -> SystemConfig:
    data = _config_data()
    assert isinstance(data["llm_generate"], dict)
    data["llm_generate"]["max_conditioning_examples"] = 2
    data["llm_generate"]["seed_zomic"] = None
    data["llm_generate"]["example_pack_path"] = None
    if include_model_lanes:
        data["llm_generate"]["model_lanes"] = {
            "general_purpose": {
                "adapter": "llm_fixture_v1",
                "provider": "mock",
                "model": "fixture-zomic-v1",
            },
            "specialized_materials": {
                "adapter": "anthropic_api_v1",
                "provider": "anthropic",
                "model": "claude-materials-v1",
                "api_base": "https://example.invalid/materials",
            },
        }
    return SystemConfig.model_validate(data)


def _launch_baseline(
    config: SystemConfig,
    *,
    system_config_path: Path,
    example_pack_path: str | None = None,
    seed_zomic_path: str | None = None,
) -> LlmCampaignLaunchBaseline:
    assert config.llm_generate is not None
    return LlmCampaignLaunchBaseline(
        system_config_path=str(system_config_path),
        system_config_hash="config-hash-001",
        system=config.system_name,
        template_family=config.template_family,
        default_count=config.default_count,
        composition_bounds=config.composition_bounds,
        prompt_template=config.llm_generate.prompt_template,
        example_pack_path=example_pack_path,
        max_conditioning_examples=config.llm_generate.max_conditioning_examples,
        seed_zomic_path=seed_zomic_path,
    )


def _spec(
    config: SystemConfig,
    actions: list[LlmCampaignAction],
    *,
    system_config_path: Path,
    example_pack_path: str | None = None,
    seed_zomic_path: str | None = None,
) -> LlmCampaignSpec:
    return LlmCampaignSpec(
        campaign_id="campaign-001",
        proposal_id="proposal-001",
        approval_id="approval-001",
        system=config.system_name,
        created_at_utc="2026-04-04T16:00:00Z",
        actions=actions,
        launch_baseline=_launch_baseline(
            config,
            system_config_path=system_config_path,
            example_pack_path=example_pack_path,
            seed_zomic_path=seed_zomic_path,
        ),
        lineage=LlmCampaignLineage(
            acceptance_pack_path="data/benchmarks/llm_acceptance/pack_v1/acceptance_pack.json",
            proposal_path="data/benchmarks/llm_acceptance/pack_v1/proposals/proposal-001.json",
            approval_path="data/benchmarks/llm_acceptance/pack_v1/approvals/approval-001.json",
            source_system_config_path=str(system_config_path),
            source_system_config_hash="config-hash-001",
        ),
    )


def _prompt_action(
    action_id: str,
    *,
    priority: str,
    lane: str,
    instruction_delta: str,
    preferred_max_conditioning_examples: int | None = None,
) -> LlmCampaignAction:
    return LlmCampaignAction(
        action_id=action_id,
        family="prompt_conditioning",
        title=f"Prompt action {action_id}",
        rationale="Prompt tuning for campaign launch",
        priority=priority,
        evidence_metrics=["compile_success_rate"],
        preferred_model_lane=lane,
        prompt_conditioning=LlmPromptConditioningActionData(
            instruction_delta=instruction_delta,
            conditioning_strategy="increase_exact_system_examples",
            target_example_family="acceptance_pack_exact_matches",
            preferred_max_conditioning_examples=preferred_max_conditioning_examples,
        ),
    )


def _composition_action(
    action_id: str,
    *,
    priority: str = "high",
    lane: str = "general_purpose",
    focus_species: list[str],
    target_bounds: dict[str, CompositionBound] | None = None,
) -> LlmCampaignAction:
    return LlmCampaignAction(
        action_id=action_id,
        family="composition_window",
        title=f"Composition action {action_id}",
        rationale="Tighten composition search window",
        priority=priority,
        evidence_metrics=["validation_pass_rate"],
        preferred_model_lane=lane,
        composition_window=LlmCompositionWindowActionData(
            window_strategy="tighten_around_validated_hits",
            focus_species=focus_species,
            target_bounds=target_bounds,
        ),
    )


def _seed_action(
    action_id: str,
    *,
    priority: str = "low",
    lane: str = "general_purpose",
) -> LlmCampaignAction:
    return LlmCampaignAction(
        action_id=action_id,
        family="seed_motif_variation",
        title=f"Seed action {action_id}",
        rationale="Explore deterministic motif variants",
        priority=priority,
        evidence_metrics=[],
        preferred_model_lane=lane,
        seed_motif_variation=LlmSeedMotifVariationActionData(
            variation_strategy="explore_neighboring_seed_motifs",
            seed_source_hint="accepted_examples",
            motif_tags=["dry_run_exploratory"],
        ),
    )


def _write_eval_set(path: Path) -> None:
    write_jsonl(
        [
            LlmEvalSetExample(
                example_id="eval_same_system",
                system="Al-Cu-Fe",
                release_tier="gold",
                fidelity_tier="exact",
                source_family="materials_design",
                source_record_id="eval_same_system",
                composition={"Al": 0.71, "Cu": 0.19, "Fe": 0.1},
                labels=["same"],
                orbit_names=["orbit.same"],
                tags=["gold"],
                properties={"template_family": "icosahedral_approximant_1_1"},
                zomic_text="label same.system\n",
            ).model_dump(mode="json"),
            LlmEvalSetExample(
                example_id="eval_other_system",
                system="Sc-Zn",
                release_tier="gold",
                fidelity_tier="exact",
                source_family="materials_design",
                source_record_id="eval_other_system",
                composition={"Sc": 0.6, "Zn": 0.4},
                labels=["other"],
                orbit_names=["orbit.other"],
                tags=["gold"],
                properties={"template_family": "icosahedral_approximant_1_1"},
                zomic_text="label other.system\n",
            ).model_dump(mode="json"),
        ],
        path,
    )


def _write_required_lineage_files(root: Path) -> None:
    (root / "lineage").mkdir(parents=True, exist_ok=True)
    (root / "lineage" / "adapter_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "corpus_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "eval_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "acceptance_pack.json").write_text("{}", encoding="utf-8")


def _write_registration_spec(
    root: Path,
    *,
    checkpoint_id: str = "ckpt-al-cu-fe-zomic-adapted",
    checkpoint_family: str | None = None,
) -> Path:
    spec = {
        "checkpoint_id": checkpoint_id,
        "system": "Al-Cu-Fe",
        "template_family": "icosahedral_approximant_1_1",
        "adapter": "openai_compat_v1",
        "provider": "openai_compat",
        "model": "zomic-adapted-local-v1",
        "local_model_path": "/opt/models/zomic-adapted-local-v1",
        "model_revision": "adapted-dev-2026-04-05",
        "base_model": "zomic-general-local-v1",
        "base_model_revision": "local-dev-2026-04-05",
        "adaptation_method": "lora",
        "adaptation_artifact_path": "lineage/adapter_manifest.json",
        "corpus_manifest_path": "lineage/corpus_manifest.json",
        "eval_set_manifest_path": "lineage/eval_manifest.json",
        "acceptance_pack_path": "lineage/acceptance_pack.json",
    }
    if checkpoint_family is not None:
        spec["checkpoint_family"] = checkpoint_family
    spec_path = root / f"{checkpoint_id}.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def _write_promotion_spec(
    root: Path,
    *,
    checkpoint_family: str,
    checkpoint_id: str,
    expected_revision: int,
) -> Path:
    evidence_paths = [
        "reports/serving_benchmark.json",
        "reports/acceptance_eval.json",
    ]
    for relative_path in evidence_paths:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
    spec_path = root / f"{checkpoint_id}-promotion.yaml"
    spec_path.write_text(
        yaml.safe_dump(
            {
                "checkpoint_family": checkpoint_family,
                "checkpoint_id": checkpoint_id,
                "evidence_paths": evidence_paths,
                "expected_revision": expected_revision,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return spec_path


def test_resolve_campaign_model_lane_prefers_first_available_requested_lane_in_priority_order() -> None:
    from materials_discovery.llm import resolve_campaign_model_lane

    config = _base_config()
    system_config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    spec = _spec(
        config,
        actions=[
            _prompt_action(
                "action-20",
                priority="low",
                lane="general_purpose",
                instruction_delta="Low priority delta",
            ),
            _prompt_action(
                "action-10",
                priority="high",
                lane="specialized_materials",
                instruction_delta="High priority delta",
            ),
        ],
        system_config_path=system_config_path,
    )

    requested_lanes, resolved_lane, lane_config, source = resolve_campaign_model_lane(spec, config)

    assert requested_lanes == ["specialized_materials", "general_purpose"]
    assert resolved_lane == "specialized_materials"
    assert lane_config is not None
    assert lane_config.model == "claude-materials-v1"
    assert source == "configured_lane"


def test_resolve_serving_lane_honors_cli_default_fallback_and_backend_precedence() -> None:
    from materials_discovery.llm import resolve_serving_lane

    config = _base_config()
    assert config.llm_generate is not None
    config.llm_generate.default_model_lane = "specialized_materials"
    config.llm_generate.fallback_model_lane = "general_purpose"

    resolved_lane, lane_config, source = resolve_serving_lane(
        "general_purpose",
        config.llm_generate,
        config.backend,
    )
    assert resolved_lane == "general_purpose"
    assert lane_config is not None
    assert source == "configured_lane"

    resolved_lane, lane_config, source = resolve_serving_lane(
        None,
        config.llm_generate,
        config.backend,
    )
    assert resolved_lane == "specialized_materials"
    assert lane_config is not None
    assert source == "default_lane"

    config.llm_generate.default_model_lane = None
    resolved_lane, lane_config, source = resolve_serving_lane(
        None,
        config.llm_generate,
        config.backend,
    )
    assert resolved_lane == "general_purpose"
    assert lane_config is not None
    assert source == "configured_fallback"

    config_no_lanes = _base_config(include_model_lanes=False)
    resolved_lane, lane_config, source = resolve_serving_lane(
        None,
        config_no_lanes.llm_generate,
        config_no_lanes.backend,
    )
    assert resolved_lane == "general_purpose"
    assert lane_config is None
    assert source == "backend_default"


def test_resolve_campaign_launch_collects_deduped_prompt_deltas_and_updates_conditioning_cap() -> None:
    from materials_discovery.llm import resolve_campaign_launch

    config = _base_config()
    system_config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    spec = _spec(
        config,
        actions=[
            _prompt_action(
                "action-30",
                priority="low",
                lane="general_purpose",
                instruction_delta="Prefer accepted exemplars",
                preferred_max_conditioning_examples=3,
            ),
            _prompt_action(
                "action-11",
                priority="high",
                lane="general_purpose",
                instruction_delta="Prefer accepted exemplars",
                preferred_max_conditioning_examples=5,
            ),
            _prompt_action(
                "action-12",
                priority="high",
                lane="specialized_materials",
                instruction_delta="Prefer parser-safe symmetry annotations",
                preferred_max_conditioning_examples=4,
            ),
        ],
        system_config_path=system_config_path,
    )

    resolved_config, resolved = resolve_campaign_launch(
        spec,
        config,
        campaign_spec_path=Path("data/llm_campaigns/campaign-001/campaign_spec.json"),
        launch_id="launch-001",
        artifact_root=_workspace(),
    )

    assert resolved.requested_model_lanes == ["general_purpose", "specialized_materials"]
    assert resolved.resolved_model_lane == "general_purpose"
    assert resolved.resolved_model_lane_source == "configured_lane"
    assert resolved.prompt_instruction_deltas == [
        "Prefer accepted exemplars",
        "Prefer parser-safe symmetry annotations",
    ]
    assert resolved_config.llm_generate is not None
    assert resolved_config.llm_generate.max_conditioning_examples == 5


def test_resolve_campaign_launch_uses_promoted_family_member_identity(
    monkeypatch,
    tmp_path: Path,
) -> None:
    from materials_discovery.llm import resolve_campaign_launch

    _write_required_lineage_files(tmp_path)
    register_llm_checkpoint(
        _write_registration_spec(
            tmp_path,
            checkpoint_family="adapted-al-cu-fe",
        ),
        root=tmp_path,
    )
    promote_checkpoint(
        _write_promotion_spec(
            tmp_path,
            checkpoint_family="adapted-al-cu-fe",
            checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
            expected_revision=1,
        ),
        root=tmp_path,
    )

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    config = _base_config()
    config.backend.mode = "real"
    assert config.llm_generate is not None
    config.llm_generate.default_model_lane = "general_purpose"
    config.llm_generate.model_lanes["general_purpose"] = LlmModelLaneConfig(
        adapter="openai_compat_v1",
        provider="openai_compat",
        model="zomic-adapted-local-v1",
        api_base="http://localhost:8000",
        checkpoint_family="adapted-al-cu-fe",
        require_checkpoint_registration=True,
    )
    system_config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    spec = _spec(
        config,
        actions=[_seed_action("action-01", lane="general_purpose")],
        system_config_path=system_config_path,
    )

    _, resolved = resolve_campaign_launch(
        spec,
        config,
        campaign_spec_path=Path("data/llm_campaigns/campaign-001/campaign_spec.json"),
        launch_id="launch-promotion-aware",
        artifact_root=tmp_path,
    )

    assert resolved.serving_identity is not None
    assert resolved.serving_identity.checkpoint_id == "ckpt-al-cu-fe-zomic-adapted"
    assert resolved.serving_identity.checkpoint_selection_source == "family_promoted_default"
    assert resolved.serving_identity.checkpoint_lifecycle_path == (
        "data/llm_checkpoints/families/adapted-al-cu-fe/lifecycle.json"
    )
    assert resolved.serving_identity.checkpoint_lifecycle_revision == 2


def test_resolve_campaign_launch_uses_exact_target_bounds_when_provided() -> None:
    from materials_discovery.llm import resolve_campaign_launch

    config = _base_config(include_model_lanes=False)
    system_config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    spec = _spec(
        config,
        actions=[
            _composition_action(
                "action-01",
                focus_species=["Al", "Cu"],
                target_bounds={
                    "Al": CompositionBound(min=0.62, max=0.74),
                    "Cu": CompositionBound(min=0.14, max=0.22),
                },
            )
        ],
        system_config_path=system_config_path,
    )

    resolved_config, resolved = resolve_campaign_launch(
        spec,
        config,
        campaign_spec_path=Path("data/llm_campaigns/campaign-001/campaign_spec.json"),
        launch_id="launch-002",
        artifact_root=_workspace(),
    )

    assert resolved.resolved_model_lane_source == "backend_default"
    assert resolved_config.composition_bounds["Al"] == CompositionBound(min=0.62, max=0.74)
    assert resolved_config.composition_bounds["Cu"] == CompositionBound(min=0.14, max=0.22)
    assert resolved_config.composition_bounds["Fe"] == config.composition_bounds["Fe"]


def test_resolve_campaign_launch_shrinks_focus_species_without_mutating_input_config() -> None:
    from materials_discovery.llm import resolve_campaign_launch

    config = _base_config(include_model_lanes=False)
    original_bounds = config.composition_bounds["Al"].model_copy(deep=True)
    config.composition_bounds["Al"] = CompositionBound(min=0.611111, max=0.822222)
    system_config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    spec = _spec(
        config,
        actions=[_composition_action("action-01", focus_species=["Al"])],
        system_config_path=system_config_path,
    )

    resolved_config, resolved = resolve_campaign_launch(
        spec,
        config,
        campaign_spec_path=Path("data/llm_campaigns/campaign-001/campaign_spec.json"),
        launch_id="launch-003",
        artifact_root=_workspace(),
    )

    resolved_bounds = resolved_config.composition_bounds["Al"]
    original_width = 0.822222 - 0.611111
    resolved_width = resolved_bounds.max - resolved_bounds.min

    assert resolved_width == pytest.approx(original_width * 0.9)
    assert 0.611111 <= resolved_bounds.min <= resolved_bounds.max <= 0.822222
    assert resolved.resolved_composition_bounds["Al"] == resolved_bounds
    assert config.composition_bounds["Al"] == CompositionBound(min=0.611111, max=0.822222)
    assert original_bounds == CompositionBound(min=0.6, max=0.8)


def test_materialize_campaign_seed_prefers_existing_baseline_seed_path(tmp_path: Path) -> None:
    from materials_discovery.llm import materialize_campaign_seed

    config = _base_config(include_model_lanes=False)
    seed_path = tmp_path / "baseline_seed.zomic"
    seed_path.write_text("label baseline.seed\n", encoding="utf-8")
    system_config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    spec = _spec(
        config,
        actions=[_seed_action("action-01")],
        system_config_path=system_config_path,
        seed_zomic_path=str(seed_path),
    )

    launch_dir = tmp_path / "launch"
    resolved_seed_path = materialize_campaign_seed(spec, config, launch_dir)

    assert resolved_seed_path == seed_path
    assert not (launch_dir / "seed_from_evalset.zomic").exists()


def test_resolve_campaign_launch_materializes_seed_from_eval_set_into_launch_dir(
    tmp_path: Path,
) -> None:
    from materials_discovery.llm import resolve_campaign_launch

    config = _base_config(include_model_lanes=False)
    eval_set_path = tmp_path / "eval_set.jsonl"
    _write_eval_set(eval_set_path)
    system_config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    spec = _spec(
        config,
        actions=[_seed_action("action-01")],
        system_config_path=system_config_path,
        example_pack_path=str(eval_set_path),
    )

    resolved_config, resolved = resolve_campaign_launch(
        spec,
        config,
        campaign_spec_path=Path("data/llm_campaigns/campaign-001/campaign_spec.json"),
        launch_id="launch-004",
        artifact_root=tmp_path,
    )

    expected_seed_path = (
        tmp_path
        / "data"
        / "llm_campaigns"
        / "campaign-001"
        / "launches"
        / "launch-004"
        / "seed_from_evalset.zomic"
    )
    assert expected_seed_path.exists()
    assert expected_seed_path.read_text(encoding="utf-8") == "label same.system\n"
    assert resolved.resolved_seed_zomic_path == str(expected_seed_path)
    assert resolved.resolved_model_lane_source == "backend_default"
    assert resolved_config.llm_generate is not None
    assert resolved_config.llm_generate.seed_zomic == str(expected_seed_path)


def test_resolve_campaign_model_lane_only_falls_back_for_general_purpose_requests() -> None:
    from materials_discovery.llm import resolve_campaign_model_lane

    config = _base_config(include_model_lanes=False)
    system_config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    general_spec = _spec(
        config,
        actions=[
            _prompt_action(
                "action-01",
                priority="high",
                lane="general_purpose",
                instruction_delta="Hold baseline lane",
            )
        ],
        system_config_path=system_config_path,
    )

    requested_lanes, resolved_lane, lane_config, source = resolve_campaign_model_lane(
        general_spec,
        config,
    )

    assert requested_lanes == ["general_purpose"]
    assert resolved_lane == "general_purpose"
    assert lane_config is None
    assert source == "backend_default"

    specialized_spec = _spec(
        config,
        actions=[
            _prompt_action(
                "action-02",
                priority="high",
                lane="specialized_materials",
                instruction_delta="Use materials-specialized lane",
            )
        ],
        system_config_path=system_config_path,
    )

    with pytest.raises(
        ValueError,
        match="requested model lane 'specialized_materials' is not configured",
    ):
        resolve_campaign_model_lane(specialized_spec, config)
