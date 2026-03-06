from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

from materials_discovery.common.io import ensure_parent
from materials_discovery.common.schema import ArtifactManifest, SystemConfig


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def config_sha256(config: SystemConfig) -> str:
    payload = json.dumps(config.model_dump(mode="json"), sort_keys=True).encode()
    return _sha256_bytes(payload)


def build_manifest(
    stage: str,
    config: SystemConfig,
    backend_mode: Literal["mock", "real"],
    backend_versions: dict[str, str],
    output_paths: dict[str, Path],
) -> ArtifactManifest:
    output_hashes = {key: file_sha256(path) for key, path in output_paths.items()}

    return ArtifactManifest(
        run_id=f"{stage}_{uuid4().hex[:12]}",
        stage=stage,
        system=config.system_name,
        config_hash=config_sha256(config),
        backend_mode=backend_mode,
        backend_versions=backend_versions,
        output_hashes=output_hashes,
        created_at_utc=datetime.now(UTC).isoformat(),
    )


def write_manifest(manifest: ArtifactManifest, path: Path) -> None:
    ensure_parent(path)
    path.write_text(manifest.model_dump_json(), encoding="utf-8")
