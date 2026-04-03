from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from materials_discovery.common.io import write_json_object
from materials_discovery.common.manifest import file_sha256
from materials_discovery.data_sources.storage import workspace_relative
from materials_discovery.llm.schema import CorpusBuildConfig, CorpusManifest


def corpus_build_fingerprint(
    config: CorpusBuildConfig,
    syntax_count: int,
    materials_count: int,
) -> str:
    payload = {
        "config": config.model_dump(mode="json"),
        "syntax_count": syntax_count,
        "materials_count": materials_count,
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_corpus_manifest(
    *,
    config: CorpusBuildConfig,
    config_path: Path,
    syntax_count: int,
    materials_count: int,
    reject_count: int,
    inventory_count: int,
    syntax_path: Path,
    materials_path: Path,
    rejects_path: Path,
    inventory_path: Path,
    qa_path: Path,
) -> CorpusManifest:
    output_paths = {
        "syntax_corpus": syntax_path,
        "materials_corpus": materials_path,
        "rejects": rejects_path,
        "inventory": inventory_path,
        "qa": qa_path,
    }
    output_hashes = {name: file_sha256(path) for name, path in output_paths.items() if path.exists()}
    return CorpusManifest(
        build_id=config.build_id,
        build_fingerprint=corpus_build_fingerprint(config, syntax_count, materials_count),
        created_at_utc=datetime.now(UTC).isoformat(),
        config_path=workspace_relative(config_path),
        syntax_count=syntax_count,
        materials_count=materials_count,
        reject_count=reject_count,
        inventory_count=inventory_count,
        syntax_corpus_path=workspace_relative(syntax_path),
        materials_corpus_path=workspace_relative(materials_path),
        rejects_path=workspace_relative(rejects_path),
        inventory_path=workspace_relative(inventory_path),
        qa_path=workspace_relative(qa_path),
        output_hashes=output_hashes,
    )


def write_corpus_manifest(manifest: CorpusManifest, output_path: Path) -> Path:
    write_json_object(manifest.model_dump(mode="json"), output_path)
    return output_path
