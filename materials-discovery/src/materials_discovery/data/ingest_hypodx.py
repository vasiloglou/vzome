from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import load_json_array, write_jsonl
from materials_discovery.common.schema import IngestRecord, IngestSummary, SystemConfig
from materials_discovery.data.normalize import ingest_fingerprint, normalize_raw_record


def ingest_fixture(
    config: SystemConfig,
    fixture_path: Path,
    output_path: Path,
) -> IngestSummary:
    raw_rows = load_json_array(fixture_path)

    normalized_rows: list[IngestRecord] = []
    for raw in raw_rows:
        record = normalize_raw_record(raw)
        if record.system.lower() == config.system_name.lower():
            normalized_rows.append(record)

    deduped: dict[tuple[str, str, tuple[tuple[str, float], ...]], IngestRecord] = {}
    for record in normalized_rows:
        deduped[ingest_fingerprint(record)] = record

    ordered = [deduped[k] for k in sorted(deduped.keys())]

    write_jsonl([row.model_dump() for row in ordered], output_path)

    return IngestSummary(
        raw_count=len(raw_rows),
        matched_count=len(normalized_rows),
        deduped_count=len(ordered),
        output_path=str(output_path),
    )
