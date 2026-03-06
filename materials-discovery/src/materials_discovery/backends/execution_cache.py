from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from materials_discovery.common.io import ensure_parent, load_json_object, workspace_root
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def validation_cache_root(config: SystemConfig) -> Path:
    configured = config.backend.validation_cache_dir
    if configured is not None:
        configured_path = Path(configured)
        if configured_path.is_absolute():
            return configured_path
        return workspace_root() / configured_path
    return workspace_root() / "data" / "execution_cache" / _system_slug(config.system_name)


def candidate_input_digest(
    *,
    stage: str,
    adapter_name: str,
    config: SystemConfig,
    candidate: CandidateRecord,
    command: list[str] | None,
) -> str:
    payload = {
        "stage": stage,
        "adapter_name": adapter_name,
        "backend_mode": config.backend.mode,
        "backend_versions": config.backend.versions,
        "system": config.system_name,
        "template_family": config.template_family,
        "candidate": candidate.model_dump(mode="json"),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def cache_file_path(
    config: SystemConfig,
    *,
    stage: str,
    candidate_id: str,
) -> Path:
    safe_candidate_id = candidate_id.replace("/", "_")
    return validation_cache_root(config) / stage / f"{safe_candidate_id}.json"


def load_cached_result(
    config: SystemConfig,
    *,
    stage: str,
    candidate_id: str,
    input_digest: str,
) -> dict[str, Any] | None:
    path = cache_file_path(config, stage=stage, candidate_id=candidate_id)
    if not path.exists():
        return None

    payload = load_json_object(path)
    cached_digest = payload.get("input_digest")
    if cached_digest != input_digest:
        return None

    result = payload.get("result")
    if not isinstance(result, dict):
        raise ValueError(f"cached execution result is invalid: {path}")
    return result


def write_cached_result(
    config: SystemConfig,
    *,
    stage: str,
    candidate_id: str,
    input_digest: str,
    adapter_name: str,
    command: list[str],
    result: dict[str, Any],
) -> Path:
    path = cache_file_path(config, stage=stage, candidate_id=candidate_id)
    ensure_parent(path)
    payload = {
        "stage": stage,
        "candidate_id": candidate_id,
        "system": config.system_name,
        "adapter_name": adapter_name,
        "command": command,
        "input_digest": input_digest,
        "result": result,
        "created_at_utc": datetime.now(UTC).isoformat(),
    }
    path.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
    return path
