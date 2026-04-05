from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from materials_discovery.common.io import load_json_object, workspace_root
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.schema import (
    LlmCampaignLaunchSummary,
    LlmCampaignResolvedLaunch,
    LlmCampaignSpec,
    LlmGenerationRequest,
    LlmRunManifest,
    LlmServingIdentity,
)


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root


def _resolve_artifact_path(path_str: str, *, root: Path | None = None) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (_artifact_root(root) / path).resolve()


def _load_object(path: Path) -> dict[str, Any]:
    return load_json_object(path)


def _current_backend_tuple(config: SystemConfig) -> tuple[str, str, str, str | None]:
    if config.backend.mode == "mock":
        return (
            config.backend.llm_adapter or "llm_fixture_v1",
            config.backend.llm_provider or "mock",
            config.backend.llm_model or "fixture",
            config.backend.llm_api_base,
        )
    return (
        config.backend.llm_adapter or "anthropic_api_v1",
        config.backend.llm_provider or "anthropic",
        config.backend.llm_model or "fixture",
        config.backend.llm_api_base,
    )


def _recorded_serving_identity(bundle: CampaignLaunchBundle) -> LlmServingIdentity:
    if bundle.resolved_launch.serving_identity is not None:
        return bundle.resolved_launch.serving_identity.model_copy(deep=True)
    if bundle.launch_summary.serving_identity is not None:
        return bundle.launch_summary.serving_identity.model_copy(deep=True)
    if bundle.run_manifest.serving_identity is not None:
        return bundle.run_manifest.serving_identity.model_copy(deep=True)

    requested_lane = next(iter(bundle.launch_summary.requested_model_lanes), None)
    return LlmServingIdentity(
        requested_model_lane=requested_lane,
        resolved_model_lane=bundle.launch_summary.resolved_model_lane,
        resolved_model_lane_source=bundle.launch_summary.resolved_model_lane_source,
        adapter=bundle.run_manifest.adapter_key,
        provider=bundle.run_manifest.provider,
        model=bundle.run_manifest.model,
    )


def _has_explicit_serving_identity(bundle: CampaignLaunchBundle) -> bool:
    return any(
        identity is not None
        for identity in (
            bundle.resolved_launch.serving_identity,
            bundle.launch_summary.serving_identity,
            bundle.run_manifest.serving_identity,
        )
    )


def _hard_identity_matches(
    recorded: LlmServingIdentity,
    *,
    adapter: str,
    provider: str,
    model: str,
    checkpoint_id: str | None,
) -> bool:
    if adapter != recorded.adapter or provider != recorded.provider or model != recorded.model:
        return False
    if recorded.checkpoint_id is not None and checkpoint_id != recorded.checkpoint_id:
        return False
    return True


def _format_identity(
    *,
    adapter: str,
    provider: str,
    model: str,
    checkpoint_id: str | None,
) -> str:
    parts = [
        f"adapter={adapter}",
        f"provider={provider}",
        f"model={model}",
    ]
    if checkpoint_id is not None:
        parts.append(f"checkpoint_id={checkpoint_id}")
    return ", ".join(parts)


def build_replay_serving_identity(
    bundle: CampaignLaunchBundle,
    current_config: SystemConfig,
) -> LlmServingIdentity:
    recorded = _recorded_serving_identity(bundle)
    lane_source = recorded.resolved_model_lane_source
    llm_generate = current_config.llm_generate
    if llm_generate is None:
        raise ValueError("config.llm_generate must be configured for replay")

    if not _has_explicit_serving_identity(bundle):
        return LlmServingIdentity(
            requested_model_lane=recorded.requested_model_lane,
            resolved_model_lane=(
                "general_purpose"
                if recorded.resolved_model_lane_source == "baseline_fallback"
                else recorded.resolved_model_lane
            ),
            resolved_model_lane_source=(
                "backend_default"
                if recorded.resolved_model_lane_source == "baseline_fallback"
                else recorded.resolved_model_lane_source
            ),
            adapter=recorded.adapter,
            provider=recorded.provider,
            model=recorded.model,
            effective_api_base=current_config.backend.llm_api_base,
        )

    if lane_source in {"configured_lane", "default_lane", "configured_fallback"}:
        lane_config = llm_generate.model_lanes.get(recorded.resolved_model_lane)
        backend_adapter, backend_provider, backend_model, backend_api_base = _current_backend_tuple(
            current_config
        )
        backend_matches = _hard_identity_matches(
            recorded,
            adapter=backend_adapter,
            provider=backend_provider,
            model=backend_model,
            checkpoint_id=None,
        )
        if lane_config is None:
            if backend_matches:
                return LlmServingIdentity(
                    requested_model_lane=recorded.requested_model_lane,
                    resolved_model_lane=recorded.resolved_model_lane,
                    resolved_model_lane_source="backend_default",
                    adapter=backend_adapter,
                    provider=backend_provider,
                    model=backend_model,
                    effective_api_base=backend_api_base,
                )
            raise ValueError(
                "replay hard serving identity drift: "
                f"resolved lane '{recorded.resolved_model_lane}' is no longer configured "
                f"for recorded {_format_identity(**recorded.model_dump(include={'adapter', 'provider', 'model', 'checkpoint_id'}))}. "
                "Endpoint, revision, and local-path drift are allowed; model or checkpoint drift is not."
            )
        if not _hard_identity_matches(
            recorded,
            adapter=lane_config.adapter,
            provider=lane_config.provider,
            model=lane_config.model,
            checkpoint_id=lane_config.checkpoint_id,
        ):
            if backend_matches:
                return LlmServingIdentity(
                    requested_model_lane=recorded.requested_model_lane,
                    resolved_model_lane=recorded.resolved_model_lane,
                    resolved_model_lane_source="backend_default",
                    adapter=backend_adapter,
                    provider=backend_provider,
                    model=backend_model,
                    effective_api_base=backend_api_base,
                )
            raise ValueError(
                "replay hard serving identity drift: "
                f"recorded {_format_identity(**recorded.model_dump(include={'adapter', 'provider', 'model', 'checkpoint_id'}))} "
                f"but current lane '{recorded.resolved_model_lane}' resolves to "
                f"{_format_identity(adapter=lane_config.adapter, provider=lane_config.provider, model=lane_config.model, checkpoint_id=lane_config.checkpoint_id)}. "
                "Endpoint, revision, and local-path drift are allowed; model or checkpoint drift is not."
            )
        return LlmServingIdentity(
            requested_model_lane=recorded.requested_model_lane,
            resolved_model_lane=recorded.resolved_model_lane,
            resolved_model_lane_source=recorded.resolved_model_lane_source,
            adapter=lane_config.adapter,
            provider=lane_config.provider,
            model=lane_config.model,
            effective_api_base=lane_config.api_base,
            checkpoint_id=lane_config.checkpoint_id,
            model_revision=lane_config.model_revision,
            local_model_path=lane_config.local_model_path,
        )

    adapter, provider, model, api_base = _current_backend_tuple(current_config)
    if not _hard_identity_matches(
        recorded,
        adapter=adapter,
        provider=provider,
        model=model,
        checkpoint_id=None,
    ):
        raise ValueError(
            "replay hard serving identity drift: "
            f"recorded {_format_identity(**recorded.model_dump(include={'adapter', 'provider', 'model', 'checkpoint_id'}))} "
            f"but current backend default resolves to "
            f"{_format_identity(adapter=adapter, provider=provider, model=model, checkpoint_id=None)}. "
            "Endpoint drift is allowed; model or checkpoint drift is not."
        )
    return LlmServingIdentity(
        requested_model_lane=recorded.requested_model_lane,
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="backend_default",
        adapter=adapter,
        provider=provider,
        model=model,
        effective_api_base=api_base,
    )


@dataclass(frozen=True)
class CampaignLaunchBundle:
    launch_summary_path: Path
    resolved_launch_path: Path
    campaign_spec_path: Path
    run_manifest_path: Path
    prompt_path: Path
    launch_summary: LlmCampaignLaunchSummary
    resolved_launch: LlmCampaignResolvedLaunch
    campaign_spec: LlmCampaignSpec
    run_manifest: LlmRunManifest
    prompt_payload: dict[str, Any]
    prompt_request: LlmGenerationRequest


def load_campaign_launch_bundle(
    launch_summary_path: Path,
    root: Path | None = None,
) -> CampaignLaunchBundle:
    resolved_launch_summary_path = (
        launch_summary_path
        if launch_summary_path.is_absolute()
        else (_artifact_root(root) / launch_summary_path).resolve()
    )
    launch_summary = LlmCampaignLaunchSummary.model_validate(
        _load_object(resolved_launch_summary_path)
    )
    if launch_summary.run_manifest_path is None:
        raise ValueError("launch summary is missing run_manifest_path")

    resolved_launch_path = _resolve_artifact_path(
        launch_summary.resolved_launch_path,
        root=root,
    )
    campaign_spec_path = _resolve_artifact_path(
        launch_summary.campaign_spec_path,
        root=root,
    )
    run_manifest_path = _resolve_artifact_path(
        launch_summary.run_manifest_path,
        root=root,
    )

    resolved_launch = LlmCampaignResolvedLaunch.model_validate(_load_object(resolved_launch_path))
    campaign_spec = LlmCampaignSpec.model_validate(_load_object(campaign_spec_path))
    run_manifest = LlmRunManifest.model_validate(_load_object(run_manifest_path))
    prompt_path = _resolve_artifact_path(run_manifest.prompt_path, root=root)
    prompt_payload = _load_object(prompt_path)

    request_payload = prompt_payload.get("request")
    if not isinstance(request_payload, dict):
        raise ValueError("prompt.json is missing a request object")
    prompt_request = LlmGenerationRequest.model_validate(request_payload)

    if launch_summary.launch_id != resolved_launch.launch_id:
        raise ValueError("launch summary and resolved launch disagree on launch_id")
    if launch_summary.campaign_id != resolved_launch.campaign_id:
        raise ValueError("launch summary and resolved launch disagree on campaign_id")
    if launch_summary.campaign_id != campaign_spec.campaign_id:
        raise ValueError("launch summary and campaign spec disagree on campaign_id")
    if launch_summary.system != campaign_spec.system:
        raise ValueError("launch summary and campaign spec disagree on system")
    if run_manifest.launch_id != launch_summary.launch_id:
        raise ValueError("run manifest and launch summary disagree on launch_id")
    if run_manifest.campaign_id != launch_summary.campaign_id:
        raise ValueError("run manifest and launch summary disagree on campaign_id")
    if run_manifest.system != launch_summary.system:
        raise ValueError("run manifest and launch summary disagree on system")
    if prompt_request.system != launch_summary.system:
        raise ValueError("prompt request and launch summary disagree on system")
    if prompt_request.template_family != campaign_spec.launch_baseline.template_family:
        raise ValueError("prompt request and campaign spec disagree on template_family")
    if resolved_launch.campaign_spec_path:
        expected_spec_path = _resolve_artifact_path(resolved_launch.campaign_spec_path, root=root)
        if expected_spec_path != campaign_spec_path:
            raise ValueError("resolved launch campaign_spec_path does not match launch summary")
    if run_manifest.campaign_spec_path:
        expected_spec_path = _resolve_artifact_path(run_manifest.campaign_spec_path, root=root)
        if expected_spec_path != campaign_spec_path:
            raise ValueError("run manifest campaign_spec_path does not match launch summary")
    if run_manifest.launch_summary_path:
        expected_summary_path = _resolve_artifact_path(run_manifest.launch_summary_path, root=root)
        if expected_summary_path != resolved_launch_summary_path:
            raise ValueError("run manifest launch_summary_path does not match replay entrypoint")

    return CampaignLaunchBundle(
        launch_summary_path=resolved_launch_summary_path,
        resolved_launch_path=resolved_launch_path,
        campaign_spec_path=campaign_spec_path,
        run_manifest_path=run_manifest_path,
        prompt_path=prompt_path,
        launch_summary=launch_summary,
        resolved_launch=resolved_launch,
        campaign_spec=campaign_spec,
        run_manifest=run_manifest,
        prompt_payload=prompt_payload,
        prompt_request=prompt_request,
    )


def build_replay_config(
    bundle: CampaignLaunchBundle,
    current_config: SystemConfig,
) -> SystemConfig:
    if current_config.system_name != bundle.campaign_spec.launch_baseline.system:
        raise ValueError("replay requires the same system as the recorded launch")
    if current_config.template_family != bundle.campaign_spec.launch_baseline.template_family:
        raise ValueError("replay requires the same template_family as the recorded launch")
    if current_config.llm_generate is None:
        raise ValueError("config.llm_generate must be configured for replay")

    replay_config = current_config.model_copy(deep=True)
    replay_config.default_count = bundle.launch_summary.requested_count
    replay_config.composition_bounds = {
        species: bound.model_copy(deep=True)
        for species, bound in bundle.resolved_launch.resolved_composition_bounds.items()
    }

    serving_identity = build_replay_serving_identity(bundle, current_config)
    replay_config.backend.llm_adapter = serving_identity.adapter
    replay_config.backend.llm_provider = serving_identity.provider
    replay_config.backend.llm_model = serving_identity.model
    replay_config.backend.llm_api_base = serving_identity.effective_api_base

    replay_config.llm_generate.prompt_template = bundle.run_manifest.prompt_template
    replay_config.llm_generate.temperature = bundle.prompt_request.temperature
    replay_config.llm_generate.max_tokens = bundle.prompt_request.max_tokens
    replay_config.llm_generate.max_attempts = (
        bundle.run_manifest.max_attempts or replay_config.llm_generate.max_attempts
    )
    replay_config.llm_generate.example_pack_path = (
        bundle.resolved_launch.resolved_example_pack_path or bundle.prompt_request.example_pack_path
    )
    replay_config.llm_generate.seed_zomic = (
        bundle.resolved_launch.resolved_seed_zomic_path or bundle.prompt_request.seed_zomic_path
    )

    baseline_cap = bundle.campaign_spec.launch_baseline.max_conditioning_examples
    conditioning_count = len(bundle.run_manifest.conditioning_example_ids)
    cap_candidates = [
        replay_config.llm_generate.max_conditioning_examples,
        conditioning_count,
    ]
    if baseline_cap is not None:
        cap_candidates.append(baseline_cap)
    replay_config.llm_generate.max_conditioning_examples = max(cap_candidates)

    return replay_config


def build_replay_campaign_metadata(bundle: CampaignLaunchBundle) -> dict[str, object]:
    return {
        "campaign_id": bundle.campaign_spec.campaign_id,
        "campaign_spec_path": str(bundle.campaign_spec_path),
        "proposal_id": bundle.campaign_spec.proposal_id,
        "approval_id": bundle.campaign_spec.approval_id,
        "requested_model_lanes": list(bundle.launch_summary.requested_model_lanes),
        "resolved_model_lane": bundle.launch_summary.resolved_model_lane,
        "resolved_model_lane_source": bundle.launch_summary.resolved_model_lane_source,
        "replay_of_launch_id": bundle.launch_summary.launch_id,
        "replay_of_launch_summary_path": str(bundle.launch_summary_path),
    }
