from __future__ import annotations

import re
from pathlib import Path

from materials_discovery.common.io import load_jsonl
from materials_discovery.common.schema import IngestRecord, SystemConfig
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord, ProjectionSummary

_SYSTEM_TOKEN_SPLIT = re.compile(r"[^A-Za-z]+")
_QC_FAMILY_TOKENS: dict[str, str] = {
    "approximant": "approximant",
    "bergman": "bergman_cluster",
    "decagonal": "decagonal",
    "dodecagonal": "dodecagonal",
    "i-phase": "quasicrystal",
    "icosa": "icosahedral",
    "mackay": "mackay_cluster",
    "qc": "quasicrystal",
    "quasicrystal": "quasicrystal",
    "tsai": "tsai_cluster",
}
_RECORD_KIND_PRIORITY = {
    "phase_entry": 0,
    "material_entry": 1,
    "structure": 2,
    "dataset_member": 3,
    "repository_asset": 4,
}


def _normalize_symbol(symbol: str) -> str:
    return symbol.strip().lower()


def _system_from_species(species: list[str]) -> tuple[str, ...]:
    return tuple(sorted({_normalize_symbol(symbol) for symbol in species if symbol.strip()}))


def _system_from_string(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(
        sorted(
            {
                token.lower()
                for token in _SYSTEM_TOKEN_SPLIT.split(value)
                if token and any(character.isalpha() for character in token)
            }
        )
    )


def _provider_system_hints(record: CanonicalRawSourceRecord) -> set[tuple[str, ...]]:
    hints: set[tuple[str, ...]] = set()
    if record.common.elements:
        hints.add(_system_from_species(record.common.elements))
    if record.common.composition:
        hints.add(_system_from_species(list(record.common.composition)))

    hint_strings = [record.common.chemical_system]
    reported_chemical_system = record.common.reported_properties.get("chemical_system")
    if isinstance(reported_chemical_system, str):
        hint_strings.append(reported_chemical_system)

    for key in ("chemical_system", "system", "alloy_system", "alloy"):
        value = record.source_metadata.get(key)
        if isinstance(value, str):
            hint_strings.append(value)
        elif isinstance(value, list):
            hints.add(_system_from_species([str(entry) for entry in value]))

    for value in hint_strings:
        parsed = _system_from_string(value)
        if parsed:
            hints.add(parsed)

    return {hint for hint in hints if hint}


def _matches_system(record: CanonicalRawSourceRecord, config: SystemConfig) -> bool:
    target = _system_from_species(config.species)
    return target in _provider_system_hints(record)


def _non_empty_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _derive_phase_name(record: CanonicalRawSourceRecord) -> tuple[str, str]:
    phase_name = _non_empty_string(record.common.reported_properties.get("phase_name"))
    if phase_name is not None:
        return phase_name, "reported_properties.phase_name"

    phase_name = _non_empty_string(record.source.record_title)
    if phase_name is not None:
        return phase_name, "source.record_title"

    phase_name = _non_empty_string(record.common.formula_reduced)
    if phase_name is not None:
        return phase_name, "common.formula_reduced"

    fallback = _non_empty_string(record.source.source_record_id)
    if fallback is None:
        raise ValueError("canonical record is missing a usable phase-name fallback")
    return fallback, "source.source_record_id"


def _normalized_composition(
    record: CanonicalRawSourceRecord,
) -> tuple[dict[str, float], tuple[tuple[str, float], ...]] | None:
    composition = record.common.composition
    if not composition:
        return None

    normalized = {
        element.strip(): float(value)
        for element, value in composition.items()
        if element.strip() and float(value) > 0.0
    }
    if not normalized:
        return None

    total = sum(normalized.values())
    if total <= 0.0:
        return None

    final = {
        element: value / total
        for element, value in sorted(normalized.items(), key=lambda item: item[0].lower())
    }
    fingerprint = tuple(
        sorted(
            (_normalize_symbol(element), round(value, 8)) for element, value in final.items()
        )
    )
    return final, fingerprint


def projection_fingerprint(record: IngestRecord) -> tuple[str, str, tuple[tuple[str, float], ...]]:
    return (
        _non_empty_string(record.system.lower()) or "",
        _non_empty_string(record.phase_name.lower()) or "",
        tuple(
            sorted(
                (_normalize_symbol(element), round(float(value), 8))
                for element, value in record.composition.items()
            )
        ),
    )


def _structure_tags(record: CanonicalRawSourceRecord) -> list[str]:
    tags: set[str] = {f"record_kind:{record.record_kind}"}
    if record.common.structure_representations:
        tags.add("has_structure")
        for representation in record.common.structure_representations:
            tags.add(f"representation:{representation.representation_kind}")
    if record.common.space_group:
        tags.add(f"space_group:{record.common.space_group}")
    if record.common.dimension_class:
        tags.add(f"dimension:{record.common.dimension_class}")
    return sorted(tags)


def _qc_family_cues(record: CanonicalRawSourceRecord, phase_name: str) -> list[str]:
    token_bag = " ".join(
        filter(
            None,
            [
                phase_name,
                record.source.record_title or "",
                " ".join(record.common.keywords),
                " ".join(
                    str(value)
                    for value in record.source_metadata.values()
                    if isinstance(value, str)
                ),
            ],
        )
    ).lower()
    cues = {cue for token, cue in _QC_FAMILY_TOKENS.items() if token in token_bag}
    return sorted(cues)


def _projection_metadata(
    record: CanonicalRawSourceRecord,
    phase_name: str,
    phase_name_reason: str,
) -> dict[str, object]:
    metadata: dict[str, object] = {
        "local_record_id": record.local_record_id,
        "source_key": record.source.source_key,
        "source_name": record.source.source_name,
        "source_record_id": record.source.source_record_id,
        "snapshot_id": record.snapshot.snapshot_id,
        "adapter_key": record.lineage.adapter_key,
        "record_kind": record.record_kind,
        "projection_reason": phase_name_reason,
        "license_category": record.license.license_category,
        "structure_tags": _structure_tags(record),
    }
    if record.source.source_record_url is not None:
        metadata["source_record_url"] = record.source.source_record_url
    if record.snapshot.snapshot_manifest_path:
        metadata["snapshot_manifest_path"] = record.snapshot.snapshot_manifest_path
    if record.raw_payload.payload_path:
        metadata["raw_payload_path"] = record.raw_payload.payload_path
    if qc_family_cues := _qc_family_cues(record, phase_name):
        metadata["qc_family"] = qc_family_cues
    return metadata


def _dedupe_winner_key(record: CanonicalRawSourceRecord) -> tuple[int, str, str, str]:
    return (
        _RECORD_KIND_PRIORITY.get(record.record_kind, 99),
        record.source.source_key,
        record.snapshot.snapshot_id,
        record.local_record_id,
    )


def project_canonical_records(
    records: list[CanonicalRawSourceRecord],
    config: SystemConfig,
) -> tuple[list[IngestRecord], ProjectionSummary]:
    summary = ProjectionSummary(input_count=len(records))
    deduped: dict[
        tuple[str, str, tuple[tuple[str, float], ...]],
        tuple[tuple[int, str, str, str], IngestRecord],
    ] = {}

    for record in records:
        if not _matches_system(record, config):
            summary.skipped_system_mismatch_count += 1
            continue
        summary.matched_system_count += 1

        normalized = _normalized_composition(record)
        if normalized is None:
            summary.skipped_missing_composition_count += 1
            continue
        composition, _ = normalized

        phase_name, phase_name_reason = _derive_phase_name(record)
        projected = IngestRecord(
            system=config.system_name,
            phase_name=phase_name,
            composition=composition,
            source=record.source.source_key,
            metadata=_projection_metadata(record, phase_name, phase_name_reason),
        )
        summary.projected_count += 1

        key = projection_fingerprint(projected)
        winner_key = _dedupe_winner_key(record)
        current = deduped.get(key)
        if current is None or winner_key < current[0]:
            deduped[key] = (winner_key, projected)

    ordered = [item[1] for _, item in sorted(deduped.items(), key=lambda entry: entry[0])]
    summary.deduped_count = len(ordered)
    summary.duplicate_dropped_count = summary.projected_count - summary.deduped_count
    return ordered, summary


def project_snapshot_to_ingest_records(
    canonical_records_path: Path,
    config: SystemConfig,
) -> tuple[list[IngestRecord], ProjectionSummary]:
    loaded = load_jsonl(canonical_records_path)
    records = [CanonicalRawSourceRecord.model_validate(row) for row in loaded]
    return project_canonical_records(records, config)
