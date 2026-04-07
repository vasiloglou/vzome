from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from materials_discovery.common.io import (
    load_json_object,
    load_yaml,
    workspace_root,
    write_json_object,
)
from materials_discovery.llm.schema import (
    LlmExternalTargetEnvironmentManifest,
    LlmExternalTargetRegistration,
    LlmExternalTargetRegistrationSpec,
    LlmExternalTargetRegistrationSummary,
    LlmExternalTargetSmokeCheck,
)
from materials_discovery.llm.storage import (
    llm_external_target_environment_path,
    llm_external_target_registration_path,
    llm_external_target_smoke_path,
)


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root.resolve()


def _resolve_spec_relative_path(spec_path: Path, candidate: str) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path.resolve()
    return (spec_path.parent / path).resolve()


def _resolve_stored_path(candidate: str, *, root: Path | None = None) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path.resolve()
    return (_artifact_root(root) / path).resolve()


def _path_for_storage(path: Path, *, root: Path | None = None) -> str:
    resolved = path.resolve()
    artifact_root = _artifact_root(root)
    try:
        return str(resolved.relative_to(artifact_root))
    except ValueError:
        return str(resolved)


def _validate_existing_path(path: Path, *, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _fingerprint_payload(spec: LlmExternalTargetRegistrationSpec) -> dict[str, object]:
    return {
        "model_id": spec.model_id,
        "model_family": spec.model_family,
        "supported_systems": spec.supported_systems,
        "supported_target_families": spec.supported_target_families,
        "runner_key": spec.runner_key,
        "provider": spec.provider,
        "model": spec.model,
        "model_revision": spec.model_revision,
        "tokenizer_revision": spec.tokenizer_revision,
        "local_snapshot_path": spec.local_snapshot_path,
        "snapshot_manifest_path": spec.snapshot_manifest_path,
        "dtype": spec.dtype,
        "quantization": spec.quantization,
        "prompt_contract_id": spec.prompt_contract_id,
        "response_parser_key": spec.response_parser_key,
    }


def _fingerprint_external_target(spec: LlmExternalTargetRegistrationSpec) -> str:
    payload = json.dumps(_fingerprint_payload(spec), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _collect_package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for package_name in (
        "pydantic",
        "typer",
        "torch",
        "transformers",
        "huggingface_hub",
        "safetensors",
        "accelerate",
        "peft",
    ):
        try:
            versions[package_name] = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            continue
    return dict(sorted(versions.items()))


def _collect_cuda_context() -> tuple[bool | None, int | None, str | None]:
    visible_devices = os.environ.get("CUDA_VISIBLE_DEVICES")
    try:
        import torch  # type: ignore[import-not-found]
    except Exception:
        return None, None, visible_devices

    try:
        cuda_available = bool(torch.cuda.is_available())
        gpu_count = int(torch.cuda.device_count()) if cuda_available else 0
        return cuda_available, gpu_count, visible_devices
    except Exception:
        return None, None, visible_devices


def load_external_target_spec(spec_path: Path) -> LlmExternalTargetRegistrationSpec:
    return LlmExternalTargetRegistrationSpec.model_validate(load_yaml(spec_path.resolve()))


def load_registered_external_target(
    model_id: str,
    *,
    root: Path | None = None,
) -> tuple[LlmExternalTargetRegistration, Path]:
    registration_path = llm_external_target_registration_path(model_id, root=root)
    if not registration_path.exists():
        raise FileNotFoundError(
            f"external target registration '{model_id}' not found: {registration_path}"
        )
    payload = load_json_object(registration_path)
    return LlmExternalTargetRegistration.model_validate(payload), registration_path


def register_external_target(
    spec_path: Path,
    *,
    root: Path | None = None,
) -> LlmExternalTargetRegistrationSummary:
    spec_path = spec_path.resolve()
    spec = load_external_target_spec(spec_path)

    local_snapshot_path = _resolve_spec_relative_path(spec_path, spec.local_snapshot_path)
    _validate_existing_path(local_snapshot_path, label="local snapshot")
    snapshot_manifest_path = (
        None
        if spec.snapshot_manifest_path is None
        else _resolve_spec_relative_path(spec_path, spec.snapshot_manifest_path)
    )
    if snapshot_manifest_path is not None:
        _validate_existing_path(snapshot_manifest_path, label="snapshot manifest")

    normalized_spec = spec.model_copy(
        update={
            "local_snapshot_path": _path_for_storage(local_snapshot_path, root=root),
            "snapshot_manifest_path": (
                None
                if snapshot_manifest_path is None
                else _path_for_storage(snapshot_manifest_path, root=root)
            ),
        }
    )
    fingerprint = _fingerprint_external_target(normalized_spec)
    registration_path = llm_external_target_registration_path(normalized_spec.model_id, root=root)
    environment_path = llm_external_target_environment_path(normalized_spec.model_id, root=root)
    smoke_path = llm_external_target_smoke_path(normalized_spec.model_id, root=root)

    created_at_utc = _utc_now()
    if registration_path.exists():
        existing = LlmExternalTargetRegistration.model_validate(load_json_object(registration_path))
        if existing.fingerprint != fingerprint:
            raise ValueError(
                f"model_id '{normalized_spec.model_id}' is already registered with a different fingerprint"
            )
        created_at_utc = existing.created_at_utc

    registration = LlmExternalTargetRegistration(
        model_id=normalized_spec.model_id,
        model_family=normalized_spec.model_family,
        supported_systems=normalized_spec.supported_systems,
        supported_target_families=normalized_spec.supported_target_families,
        runner_key=normalized_spec.runner_key,
        provider=normalized_spec.provider,
        model=normalized_spec.model,
        model_revision=normalized_spec.model_revision,
        tokenizer_revision=normalized_spec.tokenizer_revision,
        local_snapshot_path=normalized_spec.local_snapshot_path,
        snapshot_manifest_path=normalized_spec.snapshot_manifest_path,
        dtype=normalized_spec.dtype,
        quantization=normalized_spec.quantization,
        prompt_contract_id=normalized_spec.prompt_contract_id,
        response_parser_key=normalized_spec.response_parser_key,
        created_at_utc=created_at_utc,
        fingerprint=fingerprint,
        registration_path=_path_for_storage(registration_path, root=root),
        environment_path=_path_for_storage(environment_path, root=root),
        smoke_check_path=_path_for_storage(smoke_path, root=root),
        notes=normalized_spec.notes,
    )
    write_json_object(registration.model_dump(mode="json"), registration_path)
    return LlmExternalTargetRegistrationSummary(
        model_id=registration.model_id,
        fingerprint=registration.fingerprint,
        registration_path=str(registration_path),
    )


def capture_external_target_environment(
    registration: LlmExternalTargetRegistration,
    *,
    root: Path | None = None,
) -> LlmExternalTargetEnvironmentManifest:
    snapshot_path = _resolve_stored_path(registration.local_snapshot_path, root=root)
    _validate_existing_path(snapshot_path, label="local snapshot")

    snapshot_manifest_path = None
    if registration.snapshot_manifest_path is not None:
        snapshot_manifest_path = _resolve_stored_path(registration.snapshot_manifest_path, root=root)
        _validate_existing_path(snapshot_manifest_path, label="snapshot manifest")

    cuda_available, gpu_count, visible_devices = _collect_cuda_context()
    environment = LlmExternalTargetEnvironmentManifest(
        model_id=registration.model_id,
        registration_fingerprint=registration.fingerprint,
        captured_at_utc=_utc_now(),
        python_version=sys.version.split()[0],
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_machine=platform.machine(),
        package_versions=_collect_package_versions(),
        cuda_available=cuda_available,
        gpu_count=gpu_count,
        visible_devices=visible_devices,
        local_snapshot_path=registration.local_snapshot_path,
        snapshot_manifest_path=registration.snapshot_manifest_path,
        tokenizer_revision=registration.tokenizer_revision,
        model_revision=registration.model_revision,
    )
    environment_path = llm_external_target_environment_path(registration.model_id, root=root)
    write_json_object(environment.model_dump(mode="json"), environment_path)
    return environment


def smoke_external_target(
    model_id: str,
    *,
    root: Path | None = None,
) -> LlmExternalTargetSmokeCheck:
    start = time.perf_counter()
    registration, _ = load_registered_external_target(model_id, root=root)
    environment_path = llm_external_target_environment_path(model_id, root=root)
    smoke_path = llm_external_target_smoke_path(model_id, root=root)

    status = "passed"
    detail = "snapshot path and environment manifest resolved successfully"
    try:
        capture_external_target_environment(registration, root=root)
    except Exception as exc:
        status = "failed"
        detail = str(exc)

    smoke = LlmExternalTargetSmokeCheck(
        model_id=registration.model_id,
        status=status,
        registration_fingerprint=registration.fingerprint,
        checked_at_utc=_utc_now(),
        latency_s=max(time.perf_counter() - start, 0.0),
        environment_path=_path_for_storage(environment_path, root=root),
        runner_key=registration.runner_key,
        provider=registration.provider,
        model=registration.model,
        model_revision=registration.model_revision,
        local_snapshot_path=registration.local_snapshot_path,
        detail=detail,
    )
    write_json_object(smoke.model_dump(mode="json"), smoke_path)
    return smoke
