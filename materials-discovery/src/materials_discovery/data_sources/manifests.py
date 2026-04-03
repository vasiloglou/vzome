from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from materials_discovery.common.io import ensure_parent
from materials_discovery.common.manifest import file_sha256
from materials_discovery.data_sources.schema import (
    SourceQaReport,
    SourceSnapshotManifest,
)
from materials_discovery.data_sources.types import SourceAdapterInfo


def build_source_snapshot_manifest(
    source_key: str,
    snapshot_id: str,
    adapter_info: SourceAdapterInfo,
    output_paths: dict[str, Path],
    qa_report: SourceQaReport,
    license_summary: dict[str, int],
    parent_manifest_id: str | None = None,
) -> SourceSnapshotManifest:
    output_hashes = {name: file_sha256(path) for name, path in output_paths.items()}
    qa_summary: dict[str, int | bool] = {
        "raw_count": qa_report.raw_count,
        "canonical_count": qa_report.canonical_count,
        "valid_count": qa_report.valid_count,
        "duplicate_collision_count": qa_report.duplicate_collision_count,
        "missing_required_core_field_count": qa_report.missing_required_core_field_count,
        "invalid_composition_count": qa_report.invalid_composition_count,
        "malformed_structure_count": qa_report.malformed_structure_count,
        "schema_drift_count": qa_report.schema_drift_count,
        "needs_manual_review_count": qa_report.needs_manual_review_count,
        "passed": qa_report.passed,
    }
    record_counts = {
        "raw_count": qa_report.raw_count,
        "canonical_count": qa_report.canonical_count,
        "valid_count": qa_report.valid_count,
    }
    return SourceSnapshotManifest(
        manifest_id=f"source_snapshot_{uuid4().hex[:12]}",
        stage="source_snapshot",
        source_key=source_key,
        snapshot_id=snapshot_id,
        adapter_key=adapter_info.adapter_key,
        adapter_version=adapter_info.version,
        created_at_utc=datetime.now(UTC).isoformat(),
        output_hashes=output_hashes,
        record_counts=record_counts,
        license_summary=license_summary,
        qa_summary=qa_summary,
        parent_manifest_id=parent_manifest_id,
    )


def write_source_snapshot_manifest(manifest: SourceSnapshotManifest, path: Path) -> None:
    ensure_parent(path)
    path.write_text(manifest.model_dump_json(), encoding="utf-8")
