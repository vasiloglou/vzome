from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from materials_discovery.common.manifest import config_sha256, file_sha256
from materials_discovery.common.schema import ArtifactManifest, SystemConfig


def build_pipeline_manifest(
    config: SystemConfig,
    backend_mode: Literal["mock", "real"],
    backend_versions: dict[str, str],
    stage_paths: dict[str, Path],
) -> ArtifactManifest:
    output_hashes = {name: file_sha256(path) for name, path in stage_paths.items()}
    return ArtifactManifest(
        run_id=f"pipeline_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
        stage="pipeline",
        system=config.system_name,
        config_hash=config_sha256(config),
        backend_mode=backend_mode,
        backend_versions=backend_versions,
        output_hashes=output_hashes,
        created_at_utc=datetime.now(UTC).isoformat(),
    )


def write_pipeline_manifest(manifest: ArtifactManifest, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.model_dump(mode="json"), sort_keys=True), encoding="utf-8")
