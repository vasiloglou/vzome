from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import workspace_root


def _artifact_root(artifact_root: str | None = None) -> Path:
    if artifact_root is None:
        return workspace_root() / "data" / "external" / "sources"
    path = Path(artifact_root)
    if path.is_absolute():
        return path
    return workspace_root() / path


def source_snapshot_dir(
    source_key: str,
    snapshot_id: str,
    artifact_root: str | None = None,
) -> Path:
    return _artifact_root(artifact_root) / source_key / snapshot_id


def raw_rows_path(source_key: str, snapshot_id: str, artifact_root: str | None = None) -> Path:
    return source_snapshot_dir(source_key, snapshot_id, artifact_root) / "raw_rows.jsonl"


def canonical_records_path(
    source_key: str,
    snapshot_id: str,
    artifact_root: str | None = None,
) -> Path:
    return source_snapshot_dir(source_key, snapshot_id, artifact_root) / "canonical_records.jsonl"


def qa_report_path(source_key: str, snapshot_id: str, artifact_root: str | None = None) -> Path:
    return source_snapshot_dir(source_key, snapshot_id, artifact_root) / "qa_report.json"


def snapshot_manifest_path(
    source_key: str,
    snapshot_id: str,
    artifact_root: str | None = None,
) -> Path:
    return source_snapshot_dir(source_key, snapshot_id, artifact_root) / "snapshot_manifest.json"


def workspace_relative(path: Path) -> str:
    root = workspace_root()
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
