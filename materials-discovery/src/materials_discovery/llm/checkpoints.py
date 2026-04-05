from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from materials_discovery.common.io import load_json_object, load_yaml, workspace_root, write_json_object
from materials_discovery.common.schema import LlmModelLaneConfig
from materials_discovery.llm.schema import (
    LlmCheckpointLineage,
    LlmCheckpointRegistration,
    LlmCheckpointRegistrationSpec,
    LlmCheckpointRegistrationSummary,
)
from materials_discovery.llm.storage import llm_checkpoint_registration_path


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
    registration = LlmCheckpointRegistration(
        checkpoint_id=normalized_spec.checkpoint_id,
        system=normalized_spec.system,
        template_family=normalized_spec.template_family,
        created_at_utc=_utc_now(),
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

    registration_path = llm_checkpoint_registration_path(registration.checkpoint_id, root=root)
    if registration_path.exists():
        existing = LlmCheckpointRegistration.model_validate(load_json_object(registration_path))
        if existing.fingerprint != registration.fingerprint:
            raise ValueError(
                f"checkpoint_id '{registration.checkpoint_id}' is already registered with a different fingerprint"
            )

    write_json_object(registration.model_dump(mode="json"), registration_path)
    return LlmCheckpointRegistrationSummary(
        checkpoint_id=registration.checkpoint_id,
        fingerprint=registration.fingerprint,
        registration_path=str(registration_path),
    )


def resolve_checkpoint_lane(
    lane_config: LlmModelLaneConfig,
    *,
    root: Path | None = None,
) -> tuple[LlmModelLaneConfig, LlmCheckpointLineage | None]:
    if lane_config.checkpoint_id is None:
        return lane_config, None

    try:
        registration, registration_path = load_registered_checkpoint(
            lane_config.checkpoint_id,
            root=root,
        )
    except FileNotFoundError:
        if lane_config.require_checkpoint_registration:
            raise
        return lane_config, None

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

    resolved_lane = lane_config.model_copy(
        update={
            "model_revision": lane_config.model_revision or registration.model_revision,
            "local_model_path": lane_config.local_model_path or registration.local_model_path,
        }
    )
    checkpoint_lineage = LlmCheckpointLineage(
        checkpoint_id=registration.checkpoint_id,
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
    return resolved_lane, checkpoint_lineage
