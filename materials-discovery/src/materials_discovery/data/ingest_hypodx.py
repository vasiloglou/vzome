from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from materials_discovery.common.io import load_json_array, write_jsonl
from materials_discovery.common.schema import IngestRecord, IngestSummary, SystemConfig
from materials_discovery.data.normalize import ingest_fingerprint, normalize_raw_record
from materials_discovery.data.qa import evaluate_ingest_quality


def ingest_rows(
    config: SystemConfig,
    raw_rows: list[dict[str, Any]],
    output_path: Path,
    backend_mode: Literal["mock", "real"] = "mock",
    backend_adapter: str = "hypodx_fixture",
) -> IngestSummary:
    normalized_rows: list[IngestRecord] = []
    invalid_count = 0
    for raw in raw_rows:
        try:
            record = normalize_raw_record(raw)
        except ValueError:
            invalid_count += 1
            continue
        if record.system.lower() == config.system_name.lower():
            normalized_rows.append(record)

    deduped: dict[tuple[str, str, tuple[tuple[str, float], ...]], IngestRecord] = {}
    for record in normalized_rows:
        deduped[ingest_fingerprint(record)] = record

    ordered = [deduped[k] for k in sorted(deduped.keys())]

    write_jsonl([row.model_dump() for row in ordered], output_path)
    qa_metrics = evaluate_ingest_quality(
        raw_count=len(raw_rows),
        matched_count=len(normalized_rows),
        deduped_count=len(ordered),
        invalid_count=invalid_count,
    )
    if qa_metrics["passed"] is not True:
        raise ValueError(
            "ingest QA checks failed: "
            f"invalid_rate={qa_metrics['invalid_rate']}, "
            f"duplicate_rate={qa_metrics['duplicate_rate']}, "
            f"deduped_count={qa_metrics['deduped_count']}"
        )

    return IngestSummary(
        raw_count=len(raw_rows),
        matched_count=len(normalized_rows),
        deduped_count=len(ordered),
        output_path=str(output_path),
        invalid_count=invalid_count,
        backend_mode=backend_mode,
        backend_adapter=backend_adapter,
        qa_metrics=qa_metrics,
    )


def ingest_fixture(
    config: SystemConfig,
    fixture_path: Path,
    output_path: Path,
) -> IngestSummary:
    raw_rows = load_json_array(fixture_path)
    return ingest_rows(config, raw_rows, output_path)
