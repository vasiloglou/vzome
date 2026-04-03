from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from materials_discovery.common.io import ensure_parent, write_json_object, write_jsonl
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.manifests import (
    build_source_snapshot_manifest,
    write_source_snapshot_manifest,
)
from materials_discovery.data_sources.qa import evaluate_source_qa, prepare_records_for_staging
from materials_discovery.data_sources.schema import SourceStageSummary
from materials_discovery.data_sources.storage import (
    canonical_records_path,
    qa_report_path,
    raw_rows_path,
    snapshot_manifest_path,
    source_snapshot_dir,
    workspace_relative,
)
from materials_discovery.data_sources.types import SourceAdapter


def _ingestion_settings(config: SystemConfig) -> dict[str, Any]:
    ingestion = getattr(config, "ingestion", None)
    if ingestion is None:
        return {}
    if hasattr(ingestion, "model_dump"):
        return dict(ingestion.model_dump(mode="json"))
    return {}


def stage_source_snapshot(
    config: SystemConfig,
    adapter: SourceAdapter,
    snapshot_path: Path | None = None,
) -> SourceStageSummary:
    settings = _ingestion_settings(config)
    adapter_info = adapter.info()
    source_key = str(settings.get("source_key") or adapter_info.source_key)
    configured_adapter_key = settings.get("adapter_key")
    if configured_adapter_key is not None and str(configured_adapter_key) != adapter_info.adapter_key:
        raise ValueError(
            "ingestion.adapter_key does not match the supplied adapter: "
            f"{configured_adapter_key} != {adapter_info.adapter_key}"
        )
    snapshot_id = str(settings.get("snapshot_id") or adapter.default_snapshot_id(config))
    artifact_root = settings.get("artifact_root")

    output_dir = source_snapshot_dir(source_key, snapshot_id, artifact_root)
    raw_path = raw_rows_path(source_key, snapshot_id, artifact_root)
    canonical_path = canonical_records_path(source_key, snapshot_id, artifact_root)
    qa_path = qa_report_path(source_key, snapshot_id, artifact_root)
    manifest_path = snapshot_manifest_path(source_key, snapshot_id, artifact_root)

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_rows = adapter.load_rows(config, snapshot_path)
    write_jsonl(raw_rows, raw_path)

    canonical_records = adapter.canonicalize_rows(config, raw_rows, snapshot_id, raw_path)
    canonical_records = prepare_records_for_staging(canonical_records)

    manifest_relpath = workspace_relative(manifest_path)
    for index, record in enumerate(canonical_records):
        patched = record.model_copy(deep=True)
        patched.snapshot.snapshot_manifest_path = manifest_relpath
        canonical_records[index] = patched

    write_jsonl(
        [record.model_dump(mode="json") for record in canonical_records],
        canonical_path,
    )

    qa_report = evaluate_source_qa(source_key, snapshot_id, len(raw_rows), canonical_records)
    write_json_object(qa_report.model_dump(mode="json"), qa_path)

    license_summary = dict(
        Counter(record.license.license_category for record in canonical_records)
    )
    manifest = build_source_snapshot_manifest(
        source_key=source_key,
        snapshot_id=snapshot_id,
        adapter_info=adapter_info,
        output_paths={
            "raw_rows_jsonl": raw_path,
            "canonical_records_jsonl": canonical_path,
            "qa_report_json": qa_path,
        },
        qa_report=qa_report,
        license_summary=license_summary,
    )
    write_source_snapshot_manifest(manifest, manifest_path)

    ensure_parent(manifest_path)
    return SourceStageSummary(
        source_key=source_key,
        snapshot_id=snapshot_id,
        raw_count=len(raw_rows),
        canonical_count=len(canonical_records),
        output_dir=workspace_relative(output_dir),
        raw_rows_path=workspace_relative(raw_path),
        canonical_records_path=workspace_relative(canonical_path),
        qa_report_path=workspace_relative(qa_path),
        snapshot_manifest_path=workspace_relative(manifest_path),
    )
