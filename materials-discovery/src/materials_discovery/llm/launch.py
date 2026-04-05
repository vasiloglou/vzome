from __future__ import annotations

from pathlib import Path
from typing import Literal

from materials_discovery.common.io import workspace_root
from materials_discovery.common.schema import (
    BackendConfig,
    CompositionBound,
    LlmGenerateConfig,
    LlmModelLaneConfig,
    SystemConfig,
)
from materials_discovery.llm.eval_set import load_eval_set
from materials_discovery.llm.prompting import select_conditioning_examples
from materials_discovery.llm.schema import (
    LlmCampaignAction,
    LlmCampaignResolvedLaunch,
    LlmCampaignSpec,
    LlmServingIdentity,
    ResolvedModelLaneSource,
)
from materials_discovery.llm.storage import (
    llm_campaign_launch_dir,
    llm_campaign_materialized_seed_path,
)

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _action_sort_key(action: LlmCampaignAction) -> tuple[int, str]:
    return (_PRIORITY_ORDER.get(action.priority, 99), action.action_id)


def _ordered_actions(spec: LlmCampaignSpec) -> list[LlmCampaignAction]:
    return sorted(spec.actions, key=_action_sort_key)


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        stripped = value.strip()
        if stripped and stripped not in out:
            out.append(stripped)
    return out


def _resolved_baseline_path(path_str: str, *, system_config_path: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    config_path = Path(system_config_path)
    if config_path.is_absolute():
        return (config_path.parent / path).resolve()
    return (workspace_root() / config_path.parent / path).resolve()


def _baseline_backend_tuple(
    config: SystemConfig,
) -> tuple[str, str, str, str | None]:
    return (
        config.backend.llm_adapter or "llm_fixture_v1",
        config.backend.llm_provider or "mock",
        config.backend.llm_model or "fixture",
        config.backend.llm_api_base,
    )


def _baseline_backend_tuple_from_backend(
    backend: BackendConfig,
) -> tuple[str, str, str, str | None]:
    if backend.mode == "mock":
        return (
            backend.llm_adapter or "llm_fixture_v1",
            backend.llm_provider or "mock",
            backend.llm_model or "fixture",
            backend.llm_api_base,
        )
    return (
        backend.llm_adapter or "anthropic_api_v1",
        backend.llm_provider or "anthropic",
        backend.llm_model or "fixture",
        backend.llm_api_base,
    )


def build_serving_identity(
    *,
    requested_lane: str | None,
    resolved_lane: str,
    lane_source: ResolvedModelLaneSource,
    backend: BackendConfig,
    lane_config: LlmModelLaneConfig | None,
) -> LlmServingIdentity:
    adapter, provider, model, api_base = _baseline_backend_tuple_from_backend(backend)
    checkpoint_id = None
    model_revision = None
    local_model_path = None
    if lane_config is not None:
        adapter = lane_config.adapter
        provider = lane_config.provider
        model = lane_config.model
        api_base = lane_config.api_base
        checkpoint_id = lane_config.checkpoint_id
        model_revision = lane_config.model_revision
        local_model_path = lane_config.local_model_path

    return LlmServingIdentity(
        requested_model_lane=requested_lane,
        resolved_model_lane=resolved_lane,
        resolved_model_lane_source=lane_source,
        adapter=adapter,
        provider=provider,
        model=model,
        effective_api_base=api_base,
        checkpoint_id=checkpoint_id,
        model_revision=model_revision,
        local_model_path=local_model_path,
    )


def _resolved_conditioning_cap(spec: LlmCampaignSpec, config: SystemConfig) -> int:
    baseline = spec.launch_baseline.max_conditioning_examples
    if baseline is None:
        if config.llm_generate is None:
            raise ValueError("config.llm_generate must be configured for campaign launch")
        baseline = config.llm_generate.max_conditioning_examples
    max_examples = baseline
    for action in _ordered_actions(spec):
        payload = action.prompt_conditioning
        if payload is None or payload.preferred_max_conditioning_examples is None:
            continue
        max_examples = max(max_examples, payload.preferred_max_conditioning_examples)
    return max_examples


def _resolved_prompt_deltas(spec: LlmCampaignSpec) -> list[str]:
    deltas: list[str] = []
    for action in _ordered_actions(spec):
        payload = action.prompt_conditioning
        if payload is None:
            continue
        instruction_delta = payload.instruction_delta.strip()
        if instruction_delta and instruction_delta not in deltas:
            deltas.append(instruction_delta)
    return deltas


def _resolved_composition_bounds(
    spec: LlmCampaignSpec,
    config: SystemConfig,
) -> dict[str, CompositionBound]:
    bounds = {
        species: value.model_copy(deep=True)
        for species, value in config.composition_bounds.items()
    }

    for action in _ordered_actions(spec):
        payload = action.composition_window
        if payload is None:
            continue
        if payload.target_bounds:
            for species, target in payload.target_bounds.items():
                bounds[species] = target.model_copy(deep=True)
            continue

        for species in payload.focus_species:
            existing = bounds.get(species)
            if existing is None:
                continue
            midpoint = (existing.min + existing.max) / 2.0
            half_width = (existing.max - existing.min) * 0.45
            new_min = max(existing.min, midpoint - half_width)
            new_max = min(existing.max, midpoint + half_width)
            if new_min > new_max:
                new_min = new_max = min(max(midpoint, existing.min), existing.max)
            bounds[species] = CompositionBound(min=new_min, max=new_max)
    return bounds


def resolve_serving_lane(
    requested_lane: str | None,
    llm_generate_config: LlmGenerateConfig | None,
    backend_config: BackendConfig,
    *,
    allow_backend_default: bool = True,
) -> tuple[str, LlmModelLaneConfig | None, ResolvedModelLaneSource]:
    del backend_config
    available_lanes = {} if llm_generate_config is None else llm_generate_config.model_lanes

    if requested_lane is not None:
        lane_config = available_lanes.get(requested_lane)
        if lane_config is not None:
            return requested_lane, lane_config, "configured_lane"

        fallback_lane = (
            None if llm_generate_config is None else llm_generate_config.fallback_model_lane
        )
        if fallback_lane is not None:
            fallback_config = available_lanes.get(fallback_lane)
            if fallback_config is None:
                raise ValueError(
                    f"fallback model lane '{fallback_lane}' is not configured"
                )
            return fallback_lane, fallback_config, "configured_fallback"

        if requested_lane == "general_purpose" and allow_backend_default:
            return "general_purpose", None, "backend_default"

        raise ValueError(
            f"requested model lane '{requested_lane}' is not configured and no explicit fallback is available"
        )

    if llm_generate_config is not None and llm_generate_config.default_model_lane is not None:
        default_lane = llm_generate_config.default_model_lane
        default_config = available_lanes.get(default_lane)
        if default_config is None:
            raise ValueError(f"default model lane '{default_lane}' is not configured")
        return default_lane, default_config, "default_lane"

    if llm_generate_config is not None and llm_generate_config.fallback_model_lane is not None:
        fallback_lane = llm_generate_config.fallback_model_lane
        fallback_config = available_lanes.get(fallback_lane)
        if fallback_config is None:
            raise ValueError(f"fallback model lane '{fallback_lane}' is not configured")
        return fallback_lane, fallback_config, "configured_fallback"

    if allow_backend_default:
        return "general_purpose", None, "backend_default"

    raise ValueError("no configured model lane is available and backend default is disabled")


def resolve_campaign_model_lane(
    spec: LlmCampaignSpec,
    config: SystemConfig,
) -> tuple[
    list[str],
    str,
    LlmModelLaneConfig | None,
    ResolvedModelLaneSource,
]:
    requested_lanes = _dedupe_preserve_order(
        [
            action.preferred_model_lane
            for action in _ordered_actions(spec)
            if action.preferred_model_lane is not None
        ]
    )
    for lane in requested_lanes:
        llm_generate_config = config.llm_generate
        available_lanes = {} if llm_generate_config is None else llm_generate_config.model_lanes
        lane_config = available_lanes.get(lane)
        if lane_config is not None:
            resolved_lane, resolved_config, source = resolve_serving_lane(
                lane,
                config.llm_generate,
                config.backend,
            )
            return requested_lanes, resolved_lane, resolved_config, source

    resolved_lane, lane_config, source = resolve_serving_lane(
        requested_lanes[0] if requested_lanes else None,
        config.llm_generate,
        config.backend,
    )
    return requested_lanes, resolved_lane, lane_config, source


def materialize_campaign_seed(
    spec: LlmCampaignSpec,
    config: SystemConfig,
    launch_dir: Path,
) -> Path | None:
    baseline_seed = spec.launch_baseline.seed_zomic_path
    if baseline_seed:
        return _resolved_baseline_path(
            baseline_seed,
            system_config_path=spec.launch_baseline.system_config_path,
        )

    example_pack_path = spec.launch_baseline.example_pack_path
    if example_pack_path is None:
        return None

    eval_set_path = _resolved_baseline_path(
        example_pack_path,
        system_config_path=spec.launch_baseline.system_config_path,
    )
    examples = load_eval_set(eval_set_path)
    selected = select_conditioning_examples(
        config,
        examples,
        max_examples=1,
    )
    if not selected:
        raise ValueError("campaign launch example pack did not yield a seed candidate")

    launch_dir.mkdir(parents=True, exist_ok=True)
    seed_path = llm_campaign_materialized_seed_path(
        spec.campaign_id,
        launch_dir.name,
        root=launch_dir.parents[4],
    )
    seed_text = selected[0].zomic_text
    if not seed_text.endswith("\n"):
        seed_text = f"{seed_text}\n"
    seed_path.write_text(seed_text, encoding="utf-8")
    return seed_path


def resolve_campaign_launch(
    spec: LlmCampaignSpec,
    config: SystemConfig,
    *,
    campaign_spec_path: Path,
    launch_id: str,
    artifact_root: Path | None = None,
) -> tuple[SystemConfig, LlmCampaignResolvedLaunch]:
    if config.llm_generate is None:
        raise ValueError("config.llm_generate must be configured for campaign launch")

    launch_root = artifact_root.resolve() if artifact_root is not None else workspace_root()
    launch_dir = llm_campaign_launch_dir(spec.campaign_id, launch_id, root=launch_root)
    requested_lanes, resolved_lane, lane_config, lane_source = resolve_campaign_model_lane(
        spec,
        config,
    )
    prompt_deltas = _resolved_prompt_deltas(spec)
    composition_bounds = _resolved_composition_bounds(spec, config)
    resolved_seed = materialize_campaign_seed(spec, config, launch_dir)

    resolved_config = config.model_copy(deep=True)
    resolved_config.composition_bounds = {
        species: value.model_copy(deep=True) for species, value in composition_bounds.items()
    }
    resolved_config.llm_generate.max_conditioning_examples = _resolved_conditioning_cap(spec, config)
    resolved_config.llm_generate.example_pack_path = spec.launch_baseline.example_pack_path
    resolved_config.llm_generate.seed_zomic = None if resolved_seed is None else str(resolved_seed)

    adapter, provider, model, api_base = _baseline_backend_tuple(config)
    serving_identity = build_serving_identity(
        requested_lane=requested_lanes[0] if requested_lanes else None,
        resolved_lane=resolved_lane,
        lane_source=lane_source,
        backend=config.backend,
        lane_config=lane_config,
    )
    if lane_config is not None:
        adapter = serving_identity.adapter
        provider = serving_identity.provider
        model = serving_identity.model
        api_base = serving_identity.effective_api_base

    resolved_config.backend.llm_adapter = adapter
    resolved_config.backend.llm_provider = provider
    resolved_config.backend.llm_model = model
    resolved_config.backend.llm_api_base = api_base

    resolved = LlmCampaignResolvedLaunch(
        launch_id=launch_id,
        campaign_id=spec.campaign_id,
        campaign_spec_path=str(campaign_spec_path),
        system_config_path=spec.launch_baseline.system_config_path,
        system_config_hash=spec.launch_baseline.system_config_hash,
        requested_model_lanes=requested_lanes,
        resolved_model_lane=resolved_lane,
        resolved_model_lane_source=lane_source,
        resolved_adapter=adapter,
        resolved_provider=provider,
        resolved_model=model,
        serving_identity=serving_identity,
        prompt_instruction_deltas=prompt_deltas,
        resolved_composition_bounds=resolved_config.composition_bounds,
        resolved_example_pack_path=spec.launch_baseline.example_pack_path,
        resolved_seed_zomic_path=None if resolved_seed is None else str(resolved_seed),
    )
    return resolved_config, resolved
