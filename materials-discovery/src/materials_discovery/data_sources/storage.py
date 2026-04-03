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


# ---------------------------------------------------------------------------
# Reference-pack storage paths (Phase 4)
# ---------------------------------------------------------------------------


def _reference_pack_root(pack_root: str | None = None) -> Path:
    if pack_root is not None:
        path = Path(pack_root)
        if path.is_absolute():
            return path
        return workspace_root() / path
    return workspace_root() / "data" / "external" / "reference_packs"


def reference_pack_dir(
    system_slug: str,
    pack_id: str,
    pack_root: str | None = None,
) -> Path:
    return _reference_pack_root(pack_root) / system_slug / pack_id


def reference_pack_canonical_records_path(
    system_slug: str,
    pack_id: str,
    pack_root: str | None = None,
) -> Path:
    return reference_pack_dir(system_slug, pack_id, pack_root) / "canonical_records.jsonl"


def reference_pack_manifest_path(
    system_slug: str,
    pack_id: str,
    pack_root: str | None = None,
) -> Path:
    return reference_pack_dir(system_slug, pack_id, pack_root) / "pack_manifest.json"
