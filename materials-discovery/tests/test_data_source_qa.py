from __future__ import annotations

from materials_discovery.data_sources.qa import (
    evaluate_source_qa,
    prepare_records_for_staging,
)
from materials_discovery.data_sources.schema import (
    CanonicalRawSourceRecord,
    derive_local_record_id,
)


def _record(
    *,
    source_record_id: str,
    local_record_id: str | None = None,
    record_kind: str = "phase_entry",
    structure_representations: list[dict[str, object]] | None = None,
    required_field_gaps: list[str] | None = None,
    structure_status: str = "missing",
    schema_drift_flags: list[str] | None = None,
) -> CanonicalRawSourceRecord:
    snapshot_id = "2026-04-03"
    source_key = "hypodx"
    computed_local_record_id = local_record_id or derive_local_record_id(
        source_key,
        snapshot_id,
        source_record_id,
    )
    return CanonicalRawSourceRecord.model_validate(
        {
            "local_record_id": computed_local_record_id,
            "record_kind": record_kind,
            "source": {
                "source_key": source_key,
                "source_name": "HYPOD-X",
                "source_record_id": source_record_id,
            },
            "access": {
                "access_level": "open",
                "auth_required": False,
                "access_surface": "fixture",
                "redistribution_posture": "allowed_with_attribution",
            },
            "license": {
                "license_expression": "CC-BY-4.0",
                "license_category": "open",
                "attribution_required": True,
            },
            "snapshot": {
                "snapshot_id": snapshot_id,
                "retrieved_at_utc": "2026-04-03T13:00:00Z",
                "retrieval_mode": "fixture",
                "snapshot_manifest_path": "data/external/sources/hypodx/2026-04-03/snapshot_manifest.json",
            },
            "raw_payload": {
                "payload_path": "data/external/sources/hypodx/2026-04-03/raw_rows.jsonl",
                "payload_format": "json",
                "content_hash": f"sha256:{source_record_id}",
            },
            "common": {
                "chemical_system": "Sc-Zn",
                "elements": ["Sc", "Zn"],
                "formula_raw": "Sc1Zn2",
                "formula_reduced": "ScZn2",
                "composition": {"Sc": 1.0, "Zn": 2.0},
                "structure_representations": structure_representations or [],
            },
            "qa": {
                "required_field_gaps": required_field_gaps or [],
                "structure_status": structure_status,
                "schema_drift_flags": schema_drift_flags or [],
            },
            "lineage": {
                "adapter_key": "fixture_direct",
                "adapter_family": "direct",
                "adapter_version": "v1",
                "fetch_manifest_id": "fetch_manifest_001",
                "normalize_manifest_id": "normalize_manifest_001",
            },
        }
    )


def test_source_qa_prepare_records_promotes_valid_statuses() -> None:
    prepared = prepare_records_for_staging(
        [
            _record(
                source_record_id="structure-001",
                record_kind="structure",
                structure_representations=[
                    {
                        "representation_kind": "cif",
                        "payload_path": "data/external/sources/hypodx/2026-04-03/structure-001.cif",
                        "payload_format": "cif",
                        "content_hash": "sha256:cif",
                    }
                ],
            )
        ]
    )

    assert prepared[0].qa.composition_status == "valid"
    assert prepared[0].qa.structure_status == "valid"
    assert prepared[0].qa.needs_manual_review is False


def test_source_qa_prepare_records_flags_duplicate_structure_records() -> None:
    duplicate_id = derive_local_record_id("hypodx", "2026-04-03", "duplicate-001")
    prepared = prepare_records_for_staging(
        [
            _record(source_record_id="duplicate-a", local_record_id=duplicate_id),
            _record(source_record_id="duplicate-b", local_record_id=duplicate_id),
            _record(source_record_id="structure-missing", record_kind="structure"),
        ]
    )

    assert prepared[0].qa.duplicate_keys == [duplicate_id]
    assert prepared[1].qa.duplicate_keys == [duplicate_id]
    assert prepared[0].qa.needs_manual_review is True
    assert prepared[2].qa.structure_status == "missing"
    assert prepared[2].qa.needs_manual_review is True


def test_source_qa_report_counts_missing_fields_drift_and_malformed_payloads() -> None:
    duplicate_id = derive_local_record_id("hypodx", "2026-04-03", "duplicate-001")
    prepared = prepare_records_for_staging(
        [
            _record(source_record_id="valid-001"),
            _record(source_record_id="duplicate-a", local_record_id=duplicate_id),
            _record(source_record_id="duplicate-b", local_record_id=duplicate_id),
            _record(source_record_id="missing-fields", required_field_gaps=["formula_reduced"]),
            _record(
                source_record_id="malformed-structure",
                record_kind="structure",
                structure_representations=[
                    {
                        "representation_kind": "cif",
                        "payload_path": "data/external/sources/hypodx/2026-04-03/malformed.cif",
                        "payload_format": "cif",
                        "content_hash": "sha256:malformed",
                    }
                ],
                structure_status="malformed",
            ),
            _record(source_record_id="schema-drift", schema_drift_flags=["source.extra_field"]),
        ]
    )

    report = evaluate_source_qa("hypodx", "2026-04-03", raw_count=9, records=prepared)

    assert report.raw_count == 9
    assert report.canonical_count == 6
    assert report.valid_count == 1
    assert report.duplicate_collision_count == 2
    assert report.missing_required_core_field_count == 1
    assert report.invalid_composition_count == 0
    assert report.malformed_structure_count == 1
    assert report.schema_drift_count == 1
    assert report.needs_manual_review_count == 5
    assert report.passed is False
