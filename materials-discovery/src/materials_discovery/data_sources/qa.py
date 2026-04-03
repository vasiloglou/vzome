from __future__ import annotations

from collections import Counter

from materials_discovery.data_sources.schema import (
    CanonicalRawSourceRecord,
    SourceQaReport,
)


def prepare_records_for_staging(
    records: list[CanonicalRawSourceRecord],
) -> list[CanonicalRawSourceRecord]:
    duplicate_counts = Counter(record.local_record_id for record in records)
    prepared: list[CanonicalRawSourceRecord] = []

    for record in records:
        staged = record.model_copy(deep=True)

        if staged.common.composition is not None and staged.qa.composition_status == "missing":
            staged.qa.composition_status = "valid"

        if staged.record_kind == "structure":
            if staged.common.structure_representations:
                if staged.qa.structure_status == "missing":
                    staged.qa.structure_status = "valid"
            else:
                staged.qa.structure_status = "missing"
                staged.qa.needs_manual_review = True
        elif staged.qa.structure_status == "valid" and not staged.common.structure_representations:
            staged.qa.structure_status = "missing"

        if duplicate_counts[staged.local_record_id] > 1:
            staged.qa.duplicate_keys = [staged.local_record_id]
            staged.qa.needs_manual_review = True

        if (
            staged.qa.required_field_gaps
            or staged.qa.schema_drift_flags
            or staged.qa.composition_status in {"malformed", "partial"}
            or staged.qa.structure_status == "malformed"
        ):
            staged.qa.needs_manual_review = True

        prepared.append(staged)

    return prepared


def evaluate_source_qa(
    source_key: str,
    snapshot_id: str,
    raw_count: int,
    records: list[CanonicalRawSourceRecord],
) -> SourceQaReport:
    duplicate_collision_count = sum(1 for record in records if record.qa.duplicate_keys)
    missing_required_core_field_count = sum(
        1 for record in records if record.qa.required_field_gaps
    )
    invalid_composition_count = sum(
        1 for record in records if record.qa.composition_status != "valid"
    )
    malformed_structure_count = sum(
        1 for record in records if record.qa.structure_status == "malformed"
    )
    schema_drift_count = sum(1 for record in records if record.qa.schema_drift_flags)
    needs_manual_review_count = sum(1 for record in records if record.qa.needs_manual_review)

    valid_count = sum(
        1
        for record in records
        if not record.qa.required_field_gaps
        and not record.qa.duplicate_keys
        and record.qa.composition_status == "valid"
        and record.qa.structure_status != "malformed"
        and not record.qa.schema_drift_flags
    )

    passed = (
        missing_required_core_field_count == 0
        and duplicate_collision_count == 0
        and invalid_composition_count == 0
        and malformed_structure_count == 0
        and schema_drift_count == 0
    )

    return SourceQaReport(
        source_key=source_key,
        snapshot_id=snapshot_id,
        raw_count=raw_count,
        canonical_count=len(records),
        valid_count=valid_count,
        duplicate_collision_count=duplicate_collision_count,
        missing_required_core_field_count=missing_required_core_field_count,
        invalid_composition_count=invalid_composition_count,
        malformed_structure_count=malformed_structure_count,
        schema_drift_count=schema_drift_count,
        needs_manual_review_count=needs_manual_review_count,
        passed=passed,
    )
