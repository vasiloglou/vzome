"""Catalog schema, per-directory catalog generator, and catalog writer."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from materials_discovery.common.io import ensure_parent
from materials_discovery.data_sources.storage import workspace_relative
from materials_discovery.lake.staleness import _hash_output_hashes, check_staleness

# ---------------------------------------------------------------------------
# Full artifact directory inventory (addresses review concern #3)
# ---------------------------------------------------------------------------

ARTIFACT_DIRECTORIES: dict[str, str] = {
    "data/external/sources": "source_snapshot",
    "data/external/reference_packs": "reference_pack",
    "data/external/fixtures": "external_fixtures",
    "data/external/pinned": "external_pinned",
    "data/processed": "processed",
    "data/candidates": "candidates",
    "data/screened": "screened",
    "data/hifi_validated": "hifi_validated",
    "data/ranked": "ranked",
    "data/active_learning": "active_learning",
    "data/prototypes": "prototypes",
    "data/calibration": "calibration",
    "data/benchmarks": "benchmarks",
    "data/reports": "reports",
    "data/manifests": "manifests",
    "data/execution_cache": "execution_cache",
    "data/registry": "registry",
}


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class CatalogEntry(BaseModel):
    """Metadata for one artifact directory."""

    artifact_type: str
    directory_path: str  # workspace-relative (per D-04 and review concern #5)
    schema_version: str  # from artifact files, or "unknown"
    record_count: int  # JSONL line count or JSON file count
    last_modified_utc: str  # ISO8601 from newest file mtime
    lineage: dict[str, str]  # workspace-relative pointers
    size_bytes: int  # total directory size
    is_stale: bool  # from staleness check
    content_hash: str | None  # SHA256 of output_hashes from manifest, if present


class DirectoryCatalog(BaseModel):
    """Catalog for a single artifact directory."""

    schema_version: str = "catalog/v1"
    generated_at_utc: str
    entries: list[CatalogEntry]


# ---------------------------------------------------------------------------
# Core builder
# ---------------------------------------------------------------------------


def build_directory_catalog(directory: Path, artifact_type: str) -> DirectoryCatalog:
    """Scan *directory* and produce a DirectoryCatalog with one CatalogEntry.

    Args:
        directory: Absolute or workspace-relative path to the artifact directory.
        artifact_type: Logical type string (e.g. "processed", "candidates").

    Returns:
        A DirectoryCatalog describing the directory.
    """
    now_utc = datetime.now(UTC).isoformat()
    catalog_path = directory / "_catalog.json"

    if not directory.exists():
        return DirectoryCatalog(
            generated_at_utc=now_utc,
            entries=[
                CatalogEntry(
                    artifact_type=artifact_type,
                    directory_path=workspace_relative(directory),
                    schema_version="unknown",
                    record_count=0,
                    last_modified_utc=now_utc,
                    lineage={},
                    size_bytes=0,
                    is_stale=True,
                    content_hash=None,
                )
            ],
        )

    # --- Count records and size ---
    record_count, size_bytes, schema_version = _scan_artifacts(directory)

    # --- Last-modified timestamp ---
    last_modified_utc = _newest_mtime_utc(directory) or now_utc

    # --- Lineage from manifest ---
    lineage, content_hash = _extract_lineage_and_hash(directory)

    # --- Staleness check ---
    is_stale = check_staleness(directory, catalog_path if catalog_path.exists() else None)

    entry = CatalogEntry(
        artifact_type=artifact_type,
        directory_path=workspace_relative(directory),
        schema_version=schema_version,
        record_count=record_count,
        last_modified_utc=last_modified_utc,
        lineage=lineage,
        size_bytes=size_bytes,
        is_stale=is_stale,
        content_hash=content_hash,
    )

    return DirectoryCatalog(generated_at_utc=now_utc, entries=[entry])


def write_catalog(catalog: DirectoryCatalog, directory: Path) -> Path:
    """Write *catalog* as ``_catalog.json`` inside *directory*.

    Args:
        catalog: The DirectoryCatalog to serialise.
        directory: Target directory (must exist or parent must be writable).

    Returns:
        Path to the written file.
    """
    catalog_path = directory / "_catalog.json"
    ensure_parent(catalog_path)
    catalog_path.write_text(
        json.dumps(catalog.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return catalog_path


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _scan_artifacts(directory: Path) -> tuple[int, int, str]:
    """Return (record_count, size_bytes, schema_version) for artifact files in directory.

    Record counting strategy:
    - ``.jsonl`` files: count non-empty lines (each is one record).
    - ``.json`` files (excluding ``_catalog.json`` and manifest files): count as files.

    Schema version is taken from the first JSON/JSONL file that contains a
    ``schema_version`` field.
    """
    _MANIFEST_NAMES = {
        "manifest.json",
        "snapshot_manifest.json",
        "pack_manifest.json",
        "_catalog.json",
    }

    record_count = 0
    size_bytes = 0
    schema_version = "unknown"
    found_schema = False

    for path in sorted(directory.iterdir()):
        if not path.is_file():
            continue
        if path.name in _MANIFEST_NAMES:
            continue

        size_bytes += path.stat().st_size

        if path.suffix == ".jsonl":
            lines = _count_jsonl_lines(path)
            record_count += lines
            if not found_schema:
                sv = _extract_schema_version_jsonl(path)
                if sv:
                    schema_version = sv
                    found_schema = True
        elif path.suffix == ".json":
            record_count += 1
            if not found_schema:
                sv = _extract_schema_version_json(path)
                if sv:
                    schema_version = sv
                    found_schema = True

    return record_count, size_bytes, schema_version


def _count_jsonl_lines(path: Path) -> int:
    count = 0
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    count += 1
    except OSError:
        pass
    return count


def _extract_schema_version_jsonl(path: Path) -> str | None:
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    return data.get("schema_version")
    except (OSError, json.JSONDecodeError):
        pass
    return None


def _extract_schema_version_json(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("schema_version")
    except (OSError, json.JSONDecodeError):
        pass
    return None


def _newest_mtime_utc(directory: Path) -> str | None:
    newest: float | None = None
    try:
        for child in directory.iterdir():
            if child.is_file():
                mtime = child.stat().st_mtime
                if newest is None or mtime > newest:
                    newest = mtime
    except OSError:
        pass
    if newest is None:
        return None
    return datetime.fromtimestamp(newest, tz=UTC).isoformat()


def _extract_lineage_and_hash(directory: Path) -> tuple[dict[str, str], str | None]:
    """Extract workspace-relative lineage pointers and content hash from manifest.

    Returns:
        (lineage dict with workspace-relative paths, SHA256 of output_hashes or None)
    """
    _MANIFEST_NAMES = [
        "manifest.json",
        "snapshot_manifest.json",
        "pack_manifest.json",
    ]
    manifest_path: Path | None = None
    for name in _MANIFEST_NAMES:
        candidate = directory / name
        if candidate.exists():
            manifest_path = candidate
            break

    if manifest_path is None:
        # Try glob fallback
        for path in directory.glob("*manifest*.json"):
            manifest_path = path
            break

    if manifest_path is None:
        return {}, None

    try:
        data: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}, None

    lineage: dict[str, str] = {}

    # Record the manifest itself
    lineage["manifest"] = workspace_relative(manifest_path)

    # Extract source_lineage pointers
    source_lineage = data.get("source_lineage")
    if isinstance(source_lineage, dict):
        for key, value in source_lineage.items():
            if isinstance(value, str):
                # Convert absolute paths to workspace-relative
                try:
                    rel = workspace_relative(Path(value))
                except Exception:
                    rel = value
                lineage[f"source_lineage.{key}"] = rel

    # Content hash from output_hashes
    output_hashes = data.get("output_hashes")
    content_hash: str | None = None
    if isinstance(output_hashes, dict):
        content_hash = _hash_output_hashes(output_hashes)

    return lineage, content_hash
