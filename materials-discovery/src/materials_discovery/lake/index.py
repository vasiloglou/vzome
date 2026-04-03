"""Lake-wide index builder and mdisc lake index CLI wiring."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from materials_discovery.common.io import ensure_parent
from materials_discovery.data_sources.storage import workspace_relative
from materials_discovery.lake.catalog import (
    ARTIFACT_DIRECTORIES,
    DirectoryCatalog,
    build_directory_catalog,
    write_catalog,
)


def _workspace_root() -> Path:
    """Return the workspace root. Indirection allows monkeypatching in tests."""
    from materials_discovery.common.io import workspace_root
    return workspace_root()


# ---------------------------------------------------------------------------
# Pydantic model
# ---------------------------------------------------------------------------


class LakeIndex(BaseModel):
    """Lake-wide index aggregating all artifact directory catalogs."""

    schema_version: str = "lake-index/v1"
    generated_at_utc: str
    workspace_root: str
    artifact_directories: int  # count of scanned (existing) directories
    total_entries: int  # sum of entries across all catalogs
    stale_count: int  # total stale entries
    catalogs: dict[str, DirectoryCatalog]  # keyed by workspace-relative dir path


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def build_lake_index(root: Path | None = None) -> LakeIndex:
    """Build a LakeIndex by scanning all ARTIFACT_DIRECTORIES.

    Args:
        root: Workspace root override. Defaults to workspace_root().

    Returns:
        A LakeIndex aggregating all existing artifact directories.
    """
    if root is None:
        root = _workspace_root()

    now_utc = datetime.now(UTC).isoformat()
    catalogs: dict[str, DirectoryCatalog] = {}
    total_entries = 0
    stale_count = 0
    scanned = 0

    for rel_path, artifact_type in ARTIFACT_DIRECTORIES.items():
        directory = root / rel_path
        if not directory.exists():
            continue

        catalog = build_directory_catalog(directory, artifact_type)
        # Write _catalog.json into the directory
        write_catalog(catalog, directory)

        # Key by workspace-relative path
        key = workspace_relative(directory)
        catalogs[key] = catalog

        scanned += 1
        total_entries += len(catalog.entries)
        stale_count += sum(1 for e in catalog.entries if e.is_stale)

    return LakeIndex(
        generated_at_utc=now_utc,
        workspace_root=workspace_relative(root),
        artifact_directories=scanned,
        total_entries=total_entries,
        stale_count=stale_count,
        catalogs=catalogs,
    )


def write_lake_index(
    index: LakeIndex,
    output_path: Path | None = None,
) -> Path:
    """Write *index* to JSON.

    Args:
        index: The LakeIndex to serialise.
        output_path: Override output path. Defaults to ``data/lake_index.json``
            inside the workspace root.

    Returns:
        Path to the written file.
    """
    if output_path is None:
        output_path = _workspace_root() / "data" / "lake_index.json"
    ensure_parent(output_path)
    output_path.write_text(
        json.dumps(index.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return output_path


def lake_stats(index: LakeIndex) -> dict[str, Any]:
    """Compute a human-readable summary of a LakeIndex.

    Args:
        index: A LakeIndex produced by build_lake_index.

    Returns:
        Summary dict with artifact_directories, total_entries, stale_count,
        systems, sources, and latest_run_utc.
    """
    systems: list[str] = []
    sources: list[str] = []
    latest_run_utc: str | None = None

    for catalog in index.catalogs.values():
        for entry in catalog.entries:
            # Collect source lineage pointers
            for key, value in entry.lineage.items():
                if "source" in key.lower() and value not in sources:
                    sources.append(value)
            # Track latest modification
            if latest_run_utc is None or entry.last_modified_utc > latest_run_utc:
                latest_run_utc = entry.last_modified_utc

    return {
        "artifact_directories": index.artifact_directories,
        "total_entries": index.total_entries,
        "stale_count": index.stale_count,
        "systems": systems,
        "sources": sources,
        "latest_run_utc": latest_run_utc,
        "generated_at_utc": index.generated_at_utc,
        "workspace_root": index.workspace_root,
    }
