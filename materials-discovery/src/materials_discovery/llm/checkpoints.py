from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from materials_discovery.common.io import load_json_object, load_yaml, workspace_root, write_json_object
from materials_discovery.common.schema import LlmModelLaneConfig
from materials_discovery.llm.schema import (
    LlmCheckpointLifecycleIndex,
    LlmCheckpointLifecycleMemberSummary,
    LlmCheckpointLineage,
    LlmCheckpointPromotionSpec,
    LlmCheckpointRegistration,
    LlmCheckpointRegistrationSpec,
    LlmCheckpointRegistrationSummary,
    LlmCheckpointRetirementSpec,
    CheckpointSelectionSource,
)
from materials_discovery.llm.storage import (
    llm_checkpoint_lifecycle_index_path,
    llm_checkpoint_promotion_action_path,
    llm_checkpoint_registration_path,
    llm_checkpoint_retirement_action_path,
)


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root.resolve()


def _resolve_spec_relative_path(spec_path: Path, candidate: str) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path.resolve()
    return (spec_path.parent / path).resolve()


def _path_for_storage(path: Path, *, root: Path | None = None) -> str:
    resolved = path.resolve()
    artifact_root = _artifact_root(root)
    try:
        return str(resolved.relative_to(artifact_root))
    except ValueError:
        return str(resolved)


def _fingerprint_payload(spec: LlmCheckpointRegistrationSpec) -> dict[str, object]:
    return {
        "checkpoint_id": spec.checkpoint_id,
        "system": spec.system,
        "template_family": spec.template_family,
        "adapter": spec.adapter,
        "provider": spec.provider,
        "model": spec.model,
        "local_model_path": spec.local_model_path,
        "model_revision": spec.model_revision,
        "base_model": spec.base_model,
        "base_model_revision": spec.base_model_revision,
        "adaptation_method": spec.adaptation_method,
        "adaptation_artifact_path": spec.adaptation_artifact_path,
        "corpus_manifest_path": spec.corpus_manifest_path,
        "eval_set_manifest_path": spec.eval_set_manifest_path,
        "acceptance_pack_path": spec.acceptance_pack_path,
    }


def _checkpoint_fingerprint(spec: LlmCheckpointRegistrationSpec) -> str:
    payload = json.dumps(_fingerprint_payload(spec), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _validate_existing_path(path: Path, *, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _update_lifecycle_member(
    member: LlmCheckpointLifecycleMemberSummary,
    **updates: object,
) -> LlmCheckpointLifecycleMemberSummary:
    payload = member.model_dump(mode="json")
    payload.update(updates)
    return LlmCheckpointLifecycleMemberSummary.model_validate(payload)


def _update_lifecycle_index(
    lifecycle: LlmCheckpointLifecycleIndex,
    **updates: object,
) -> LlmCheckpointLifecycleIndex:
    payload = lifecycle.model_dump(mode="json")
    payload.update(updates)
    return LlmCheckpointLifecycleIndex.model_validate(payload)


def _sorted_lifecycle_members(
    members: list[LlmCheckpointLifecycleMemberSummary],
) -> list[LlmCheckpointLifecycleMemberSummary]:
    return sorted(members, key=lambda member: member.checkpoint_id)


def _write_lifecycle_index(lifecycle: LlmCheckpointLifecycleIndex, path: Path) -> None:
    write_json_object(lifecycle.model_dump(mode="json"), path)


def _validate_repo_relative_path(value: str, *, field_name: str) -> None:
    normalized = value.strip()
    if normalized.startswith("http://") or normalized.startswith("https://"):
        raise ValueError(f"{field_name} must use repo-relative paths")
    if Path(normalized).is_absolute():
        raise ValueError(f"{field_name} must use repo-relative paths")


def _validate_lifecycle_expectations(
    lifecycle: LlmCheckpointLifecycleIndex,
    *,
    expected_revision: int | None,
    expected_promoted_checkpoint_id: str | None,
) -> None:
    if expected_revision is not None and lifecycle.revision != expected_revision:
        raise ValueError(
            f"stale lifecycle revision for checkpoint_family '{lifecycle.checkpoint_family}': "
            f"expected revision {expected_revision} but current revision is {lifecycle.revision}; "
            "reload the current lifecycle revision and retry"
        )
    if (
        expected_promoted_checkpoint_id is not None
        and lifecycle.promoted_checkpoint_id != expected_promoted_checkpoint_id
    ):
        current_promoted = lifecycle.promoted_checkpoint_id or "none"
        raise ValueError(
            f"stale promoted checkpoint for checkpoint_family '{lifecycle.checkpoint_family}': "
            f"expected '{expected_promoted_checkpoint_id}' but current promoted checkpoint is "
            f"'{current_promoted}'; reload the current lifecycle revision and retry"
        )


def _find_checkpoint_family_member(
    lifecycle: LlmCheckpointLifecycleIndex,
    checkpoint_id: str,
) -> LlmCheckpointLifecycleMemberSummary:
    for member in lifecycle.members:
        if member.checkpoint_id == checkpoint_id:
            return member
    raise ValueError(
        f"checkpoint '{checkpoint_id}' is not registered in checkpoint_family "
        f"'{lifecycle.checkpoint_family}'"
    )


@dataclass(frozen=True)
class ResolvedCheckpointLaneBinding:
    resolved_lane: LlmModelLaneConfig
    checkpoint_lineage: LlmCheckpointLineage | None
    checkpoint_selection_source: CheckpointSelectionSource | None = None
    checkpoint_lifecycle_path: str | None = None
    checkpoint_lifecycle_revision: int | None = None


def load_checkpoint_lifecycle(
    checkpoint_family: str,
    *,
    root: Path | None = None,
    create: bool = False,
) -> tuple[LlmCheckpointLifecycleIndex, Path]:
    lifecycle_path = llm_checkpoint_lifecycle_index_path(checkpoint_family, root=root)
    if not lifecycle_path.exists():
        if not create:
            raise FileNotFoundError(
                f"checkpoint lifecycle '{checkpoint_family}' not found: {lifecycle_path}"
            )
        lifecycle = LlmCheckpointLifecycleIndex(checkpoint_family=checkpoint_family)
        _write_lifecycle_index(lifecycle, lifecycle_path)
        return lifecycle, lifecycle_path

    lifecycle = LlmCheckpointLifecycleIndex.model_validate(load_json_object(lifecycle_path))
    if lifecycle.checkpoint_family != checkpoint_family.strip():
        raise ValueError(
            f"lifecycle index mismatch: expected checkpoint_family '{checkpoint_family.strip()}' "
            f"but found '{lifecycle.checkpoint_family}'"
        )
    return lifecycle, lifecycle_path


def list_checkpoint_family_members(
    checkpoint_family: str,
    *,
    root: Path | None = None,
) -> list[LlmCheckpointLifecycleMemberSummary]:
    lifecycle, _ = load_checkpoint_lifecycle(checkpoint_family, root=root)
    return _sorted_lifecycle_members(list(lifecycle.members))


def _enroll_registered_checkpoint(
    registration: LlmCheckpointRegistration,
    registration_path: Path,
    *,
    root: Path | None = None,
) -> None:
    if registration.checkpoint_family is None:
        return

    lifecycle, lifecycle_path = load_checkpoint_lifecycle(
        registration.checkpoint_family,
        root=root,
        create=True,
    )
    registration_path_for_storage = _path_for_storage(registration_path, root=root)
    for member in lifecycle.members:
        if member.checkpoint_id == registration.checkpoint_id:
            if member.fingerprint != registration.fingerprint:
                raise ValueError(
                    f"checkpoint '{registration.checkpoint_id}' already exists in checkpoint_family "
                    f"'{registration.checkpoint_family}' with a different fingerprint"
                )
            return

    new_member = LlmCheckpointLifecycleMemberSummary(
        checkpoint_id=registration.checkpoint_id,
        fingerprint=registration.fingerprint,
        registration_path=registration_path_for_storage,
        lifecycle_state="candidate",
        registered_at_utc=registration.created_at_utc,
    )
    updated_lifecycle = _update_lifecycle_index(
        lifecycle,
        revision=lifecycle.revision + 1,
        members=_sorted_lifecycle_members([*lifecycle.members, new_member]),
    )
    _write_lifecycle_index(updated_lifecycle, lifecycle_path)


def load_registered_checkpoint(
    checkpoint_id: str,
    *,
    root: Path | None = None,
) -> tuple[LlmCheckpointRegistration, Path]:
    registration_path = llm_checkpoint_registration_path(checkpoint_id, root=root)
    if not registration_path.exists():
        raise FileNotFoundError(
            f"checkpoint registration '{checkpoint_id}' not found: {registration_path}"
        )
    payload = load_json_object(registration_path)
    return LlmCheckpointRegistration.model_validate(payload), registration_path


def register_llm_checkpoint(
    spec_path: Path,
    *,
    root: Path | None = None,
) -> LlmCheckpointRegistrationSummary:
    spec_path = spec_path.resolve()
    raw_spec = load_yaml(spec_path)
    spec = LlmCheckpointRegistrationSpec.model_validate(raw_spec)

    adaptation_artifact_path = _resolve_spec_relative_path(spec_path, spec.adaptation_artifact_path)
    corpus_manifest_path = _resolve_spec_relative_path(spec_path, spec.corpus_manifest_path)
    eval_set_manifest_path = _resolve_spec_relative_path(spec_path, spec.eval_set_manifest_path)
    acceptance_pack_path = (
        None
        if spec.acceptance_pack_path is None
        else _resolve_spec_relative_path(spec_path, spec.acceptance_pack_path)
    )

    _validate_existing_path(adaptation_artifact_path, label="adaptation artifact")
    _validate_existing_path(corpus_manifest_path, label="corpus manifest")
    _validate_existing_path(eval_set_manifest_path, label="eval-set manifest")
    if acceptance_pack_path is not None:
        _validate_existing_path(acceptance_pack_path, label="acceptance pack")

    normalized_spec = spec.model_copy(
        update={
            "adaptation_artifact_path": _path_for_storage(adaptation_artifact_path, root=root),
            "corpus_manifest_path": _path_for_storage(corpus_manifest_path, root=root),
            "eval_set_manifest_path": _path_for_storage(eval_set_manifest_path, root=root),
            "acceptance_pack_path": (
                None
                if acceptance_pack_path is None
                else _path_for_storage(acceptance_pack_path, root=root)
            ),
        }
    )
    fingerprint = _checkpoint_fingerprint(normalized_spec)
    registration_path = llm_checkpoint_registration_path(normalized_spec.checkpoint_id, root=root)
    checkpoint_family = normalized_spec.checkpoint_family
    created_at_utc = _utc_now()
    if registration_path.exists():
        existing = LlmCheckpointRegistration.model_validate(load_json_object(registration_path))
        if existing.fingerprint != fingerprint:
            raise ValueError(
                f"checkpoint_id '{normalized_spec.checkpoint_id}' is already registered with a different fingerprint"
            )
        created_at_utc = existing.created_at_utc
        if existing.checkpoint_family is not None and checkpoint_family is None:
            checkpoint_family = existing.checkpoint_family
        elif (
            existing.checkpoint_family is not None
            and checkpoint_family is not None
            and existing.checkpoint_family != checkpoint_family
        ):
            raise ValueError(
                f"checkpoint_id '{normalized_spec.checkpoint_id}' is already registered in "
                f"checkpoint_family '{existing.checkpoint_family}'"
            )

    registration = LlmCheckpointRegistration(
        checkpoint_id=normalized_spec.checkpoint_id,
        checkpoint_family=checkpoint_family,
        system=normalized_spec.system,
        template_family=normalized_spec.template_family,
        created_at_utc=created_at_utc,
        adapter=normalized_spec.adapter,
        provider=normalized_spec.provider,
        model=normalized_spec.model,
        local_model_path=normalized_spec.local_model_path,
        model_revision=normalized_spec.model_revision,
        fingerprint=fingerprint,
        base_model=normalized_spec.base_model,
        base_model_revision=normalized_spec.base_model_revision,
        adaptation_method=normalized_spec.adaptation_method,
        adaptation_artifact_path=normalized_spec.adaptation_artifact_path,
        corpus_manifest_path=normalized_spec.corpus_manifest_path,
        eval_set_manifest_path=normalized_spec.eval_set_manifest_path,
        acceptance_pack_path=normalized_spec.acceptance_pack_path,
        notes=normalized_spec.notes,
    )

    write_json_object(registration.model_dump(mode="json"), registration_path)
    _enroll_registered_checkpoint(registration, registration_path, root=root)
    return LlmCheckpointRegistrationSummary(
        checkpoint_id=registration.checkpoint_id,
        checkpoint_family=registration.checkpoint_family,
        fingerprint=registration.fingerprint,
        registration_path=str(registration_path),
    )


def promote_checkpoint(
    spec_path: Path,
    *,
    root: Path | None = None,
) -> LlmCheckpointLifecycleIndex:
    spec = LlmCheckpointPromotionSpec.model_validate(load_yaml(spec_path.resolve()))
    for evidence_path in spec.evidence_paths:
        _validate_repo_relative_path(evidence_path, field_name="evidence_paths")

    lifecycle, lifecycle_path = load_checkpoint_lifecycle(spec.checkpoint_family, root=root)
    _validate_lifecycle_expectations(
        lifecycle,
        expected_revision=spec.expected_revision,
        expected_promoted_checkpoint_id=spec.expected_promoted_checkpoint_id,
    )
    target_member = _find_checkpoint_family_member(lifecycle, spec.checkpoint_id)
    if (
        lifecycle.promoted_checkpoint_id == spec.checkpoint_id
        and target_member.lifecycle_state == "promoted"
    ):
        return lifecycle

    new_revision = lifecycle.revision + 1
    action_path = llm_checkpoint_promotion_action_path(
        spec.checkpoint_family,
        spec.checkpoint_id,
        revision=new_revision,
        root=root,
    )
    action_path_for_storage = _path_for_storage(action_path, root=root)
    promoted_at_utc = _utc_now()
    updated_members: list[LlmCheckpointLifecycleMemberSummary] = []
    for member in lifecycle.members:
        if member.checkpoint_id == spec.checkpoint_id:
            updated_members.append(
                _update_lifecycle_member(
                    member,
                    lifecycle_state="promoted",
                    promoted_at_utc=promoted_at_utc,
                    retired_at_utc=None,
                    retirement_reason=None,
                    last_action_path=action_path_for_storage,
                )
            )
            continue
        if member.lifecycle_state == "promoted":
            updated_members.append(
                _update_lifecycle_member(
                    member,
                    lifecycle_state="candidate",
                    last_action_path=action_path_for_storage,
                )
            )
            continue
        updated_members.append(member)

    updated_lifecycle = _update_lifecycle_index(
        lifecycle,
        revision=new_revision,
        promoted_checkpoint_id=spec.checkpoint_id,
        members=_sorted_lifecycle_members(updated_members),
        action_history_paths=[*lifecycle.action_history_paths, action_path_for_storage],
    )
    write_json_object(spec.model_dump(mode="json"), action_path)
    _write_lifecycle_index(updated_lifecycle, lifecycle_path)
    return updated_lifecycle


def retire_checkpoint(
    spec_path: Path,
    *,
    root: Path | None = None,
) -> LlmCheckpointLifecycleIndex:
    spec = LlmCheckpointRetirementSpec.model_validate(load_yaml(spec_path.resolve()))
    lifecycle, lifecycle_path = load_checkpoint_lifecycle(spec.checkpoint_family, root=root)
    _validate_lifecycle_expectations(
        lifecycle,
        expected_revision=spec.expected_revision,
        expected_promoted_checkpoint_id=spec.expected_promoted_checkpoint_id,
    )
    if lifecycle.promoted_checkpoint_id == spec.checkpoint_id:
        raise ValueError(
            f"cannot retire currently promoted checkpoint '{spec.checkpoint_id}' in "
            f"checkpoint_family '{spec.checkpoint_family}'; promote a different checkpoint first"
        )

    target_member = _find_checkpoint_family_member(lifecycle, spec.checkpoint_id)
    if target_member.lifecycle_state == "retired":
        return lifecycle

    new_revision = lifecycle.revision + 1
    action_path = llm_checkpoint_retirement_action_path(
        spec.checkpoint_family,
        spec.checkpoint_id,
        revision=new_revision,
        root=root,
    )
    action_path_for_storage = _path_for_storage(action_path, root=root)
    retired_at_utc = _utc_now()
    updated_members: list[LlmCheckpointLifecycleMemberSummary] = []
    for member in lifecycle.members:
        if member.checkpoint_id == spec.checkpoint_id:
            updated_members.append(
                _update_lifecycle_member(
                    member,
                    lifecycle_state="retired",
                    retired_at_utc=retired_at_utc,
                    retirement_reason=spec.reason,
                    last_action_path=action_path_for_storage,
                )
            )
            continue
        updated_members.append(member)

    updated_lifecycle = _update_lifecycle_index(
        lifecycle,
        revision=new_revision,
        members=_sorted_lifecycle_members(updated_members),
        action_history_paths=[*lifecycle.action_history_paths, action_path_for_storage],
    )
    write_json_object(spec.model_dump(mode="json"), action_path)
    _write_lifecycle_index(updated_lifecycle, lifecycle_path)
    return updated_lifecycle


def _checkpoint_lineage_from_registration(
    registration: LlmCheckpointRegistration,
    registration_path: Path,
    *,
    root: Path | None = None,
) -> LlmCheckpointLineage:
    return LlmCheckpointLineage(
        checkpoint_id=registration.checkpoint_id,
        checkpoint_family=registration.checkpoint_family,
        registration_path=_path_for_storage(registration_path, root=root),
        fingerprint=registration.fingerprint,
        base_model=registration.base_model,
        base_model_revision=registration.base_model_revision,
        adaptation_method=registration.adaptation_method,
        adaptation_artifact_path=registration.adaptation_artifact_path,
        corpus_manifest_path=registration.corpus_manifest_path,
        eval_set_manifest_path=registration.eval_set_manifest_path,
        acceptance_pack_path=registration.acceptance_pack_path,
    )


def _load_registration_for_lane(
    lane_config: LlmModelLaneConfig,
    *,
    root: Path | None = None,
    allow_retired: bool = False,
) -> tuple[
    LlmCheckpointRegistration,
    Path,
    CheckpointSelectionSource,
    str | None,
    int | None,
] | None:
    if lane_config.checkpoint_family is not None:
        if lane_config.checkpoint_id is None:
            lifecycle, lifecycle_path = load_checkpoint_lifecycle(
                lane_config.checkpoint_family,
                root=root,
            )
            lifecycle_path_for_storage = _path_for_storage(lifecycle_path, root=root)
            lifecycle_revision = lifecycle.revision
            if lifecycle.promoted_checkpoint_id is None:
                raise ValueError(
                    f"checkpoint_family '{lane_config.checkpoint_family}' has no promoted checkpoint for new execution"
                )
            target_checkpoint_id = lifecycle.promoted_checkpoint_id
            target_member = _find_checkpoint_family_member(lifecycle, target_checkpoint_id)
            if target_member.lifecycle_state == "retired" and not allow_retired:
                raise ValueError(
                    f"checkpoint '{target_checkpoint_id}' in checkpoint_family "
                    f"'{lane_config.checkpoint_family}' is retired and cannot be used for new execution"
                )
            registration, registration_path = load_registered_checkpoint(
                target_checkpoint_id,
                root=root,
            )
            return (
                registration,
                registration_path,
                "family_promoted_default",
                lifecycle_path_for_storage,
                lifecycle_revision,
            )

        registration, registration_path = load_registered_checkpoint(
            lane_config.checkpoint_id,
            root=root,
        )
        if registration.checkpoint_family != lane_config.checkpoint_family:
            return registration, registration_path, "family_explicit_pin", None, None

        lifecycle, lifecycle_path = load_checkpoint_lifecycle(
            lane_config.checkpoint_family,
            root=root,
        )
        lifecycle_path_for_storage = _path_for_storage(lifecycle_path, root=root)
        lifecycle_revision = lifecycle.revision
        target_member = _find_checkpoint_family_member(lifecycle, lane_config.checkpoint_id)
        if target_member.lifecycle_state == "retired" and not allow_retired:
            raise ValueError(
                f"checkpoint '{lane_config.checkpoint_id}' in checkpoint_family "
                f"'{lane_config.checkpoint_family}' is retired and cannot be used for new execution"
            )
        return (
            registration,
            registration_path,
            "family_explicit_pin",
            lifecycle_path_for_storage,
            lifecycle_revision,
        )

    if lane_config.checkpoint_id is None:
        return None

    try:
        registration, registration_path = load_registered_checkpoint(
            lane_config.checkpoint_id,
            root=root,
        )
    except FileNotFoundError:
        if lane_config.require_checkpoint_registration:
            raise
        return None
    return registration, registration_path, "legacy_checkpoint_id", None, None


def _validate_lane_registration_match(
    lane_config: LlmModelLaneConfig,
    registration: LlmCheckpointRegistration,
) -> None:
    if (
        lane_config.checkpoint_family is not None
        and registration.checkpoint_family != lane_config.checkpoint_family
    ):
        raise ValueError(
            f"checkpoint '{registration.checkpoint_id}' does not belong to checkpoint_family "
            f"'{lane_config.checkpoint_family}'; reload the current lifecycle revision and retry "
            "with a matching checkpoint pin"
        )

    if lane_config.adapter != registration.adapter:
        raise ValueError(
            f"checkpoint '{registration.checkpoint_id}' adapter mismatch: "
            f"lane uses '{lane_config.adapter}' but registration pins '{registration.adapter}'"
        )
    if lane_config.provider != registration.provider:
        raise ValueError(
            f"checkpoint '{registration.checkpoint_id}' provider mismatch: "
            f"lane uses '{lane_config.provider}' but registration pins '{registration.provider}'"
        )
    if lane_config.model != registration.model:
        raise ValueError(
            f"checkpoint '{registration.checkpoint_id}' model mismatch: "
            f"lane uses '{lane_config.model}' but registration pins '{registration.model}'"
        )
    if (
        lane_config.model_revision is not None
        and registration.model_revision is not None
        and lane_config.model_revision != registration.model_revision
    ):
        raise ValueError(
            f"checkpoint '{registration.checkpoint_id}' revision mismatch: "
            f"lane uses '{lane_config.model_revision}' but registration pins '{registration.model_revision}'"
        )
    if (
        lane_config.local_model_path is not None
        and lane_config.local_model_path != registration.local_model_path
    ):
        raise ValueError(
            f"checkpoint '{registration.checkpoint_id}' local model path mismatch: "
            f"lane uses '{lane_config.local_model_path}' but registration pins '{registration.local_model_path}'"
        )


def resolve_checkpoint_lane_binding(
    lane_config: LlmModelLaneConfig,
    *,
    root: Path | None = None,
    allow_retired: bool = False,
) -> ResolvedCheckpointLaneBinding:
    loaded = _load_registration_for_lane(
        lane_config,
        root=root,
        allow_retired=allow_retired,
    )
    if loaded is None:
        return ResolvedCheckpointLaneBinding(
            resolved_lane=lane_config,
            checkpoint_lineage=None,
        )

    (
        registration,
        registration_path,
        checkpoint_selection_source,
        checkpoint_lifecycle_path,
        checkpoint_lifecycle_revision,
    ) = loaded
    _validate_lane_registration_match(lane_config, registration)

    resolved_lane = lane_config.model_copy(
        update={
            "checkpoint_id": registration.checkpoint_id,
            "model_revision": lane_config.model_revision or registration.model_revision,
            "local_model_path": lane_config.local_model_path or registration.local_model_path,
        }
    )
    checkpoint_lineage = _checkpoint_lineage_from_registration(
        registration,
        registration_path,
        root=root,
    )
    return ResolvedCheckpointLaneBinding(
        resolved_lane=resolved_lane,
        checkpoint_lineage=checkpoint_lineage,
        checkpoint_selection_source=checkpoint_selection_source,
        checkpoint_lifecycle_path=checkpoint_lifecycle_path,
        checkpoint_lifecycle_revision=checkpoint_lifecycle_revision,
    )


def resolve_checkpoint_lane(
    lane_config: LlmModelLaneConfig,
    *,
    root: Path | None = None,
    allow_retired: bool = False,
) -> tuple[LlmModelLaneConfig, LlmCheckpointLineage | None]:
    binding = resolve_checkpoint_lane_binding(
        lane_config,
        root=root,
        allow_retired=allow_retired,
    )
    return binding.resolved_lane, binding.checkpoint_lineage
