from __future__ import annotations

from typing import Any

from materials_discovery.common.schema import IngestRecord


def normalize_raw_record(raw: dict[str, Any]) -> IngestRecord:
    system = raw.get("system") or raw.get("alloy_system") or raw.get("alloy")
    if not isinstance(system, str) or not system:
        raise ValueError("missing system/alloy_system value")

    phase_name = raw.get("phase_name") or raw.get("phase")
    if not isinstance(phase_name, str) or not phase_name:
        raise ValueError("missing phase_name/phase value")

    composition = raw.get("composition")
    if not isinstance(composition, dict) or not composition:
        raise ValueError("missing composition mapping")

    normalized_composition: dict[str, float] = {}
    for key, value in composition.items():
        if not isinstance(key, str):
            raise ValueError("composition keys must be strings")
        if not isinstance(value, (int, float)):
            raise ValueError("composition values must be numeric")
        normalized_composition[key] = float(value)

    source = raw.get("source")
    source_str = source if isinstance(source, str) else "hypodx_fixture"

    return IngestRecord(
        system=system,
        phase_name=phase_name,
        composition=normalized_composition,
        source=source_str,
        metadata={"raw_keys": sorted(raw.keys())},
    )


def ingest_fingerprint(record: IngestRecord) -> tuple[str, str, tuple[tuple[str, float], ...]]:
    return (
        record.system.strip().lower(),
        record.phase_name.strip().lower(),
        tuple(sorted((k, round(v, 8)) for k, v in record.composition.items())),
    )
