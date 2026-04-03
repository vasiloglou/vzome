from __future__ import annotations

from math import isclose

import pytest
from pydantic import ValidationError

from materials_discovery.data_sources.schema import (
    CanonicalRawSourceRecord,
    derive_local_record_id,
)


def _record_payload(
    *,
    source_key: str = "hypodx",
    source_record_id: str = "phase-001",
    snapshot_id: str = "2026-04-03",
    local_record_id: str | None = None,
    record_kind: str = "phase_entry",
    structure_representations: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    structure_representations = structure_representations or []
    computed_local_record_id = local_record_id or derive_local_record_id(
        source_key,
        snapshot_id,
        source_record_id,
    )
    return {
        "local_record_id": computed_local_record_id,
        "record_kind": record_kind,
        "source": {
            "source_key": source_key,
            "source_name": "HYPOD-X",
            "source_record_id": source_record_id,
            "source_record_url": f"https://example.test/{source_record_id}",
            "record_title": "Example phase entry",
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
            "commercial_use_allowed": True,
        },
        "snapshot": {
            "snapshot_id": snapshot_id,
            "source_version": "2026.04",
            "retrieved_at_utc": "2026-04-03T13:00:00Z",
            "retrieval_mode": "fixture",
            "snapshot_manifest_path": "data/external/sources/hypodx/2026-04-03/snapshot_manifest.json",
        },
        "raw_payload": {
            "payload_path": "data/external/sources/hypodx/2026-04-03/raw_rows.jsonl",
            "payload_format": "json",
            "content_hash": "sha256:raw-payload",
        },
        "common": {
            "chemical_system": "Sc-Zn",
            "elements": [" Zn ", "Sc", "Sc"],
            "formula_raw": "Sc1Zn2",
            "formula_reduced": "ScZn2",
            "composition": {"Zn": 2.0, "Sc": 1.0},
            "structure_representations": structure_representations,
            "space_group": "Im-3",
        },
        "lineage": {
            "adapter_key": "fixture_direct",
            "adapter_family": "direct",
            "adapter_version": "v1",
            "fetch_manifest_id": "fetch_manifest_001",
            "normalize_manifest_id": "normalize_manifest_001",
        },
    }


def test_canonical_raw_source_record_phase_entry_parses_and_normalizes() -> None:
    record = CanonicalRawSourceRecord.model_validate(_record_payload())

    assert record.record_kind == "phase_entry"
    assert record.common.elements == ["Sc", "Zn"]
    assert isclose(record.common.composition["Sc"], 1.0 / 3.0)
    assert isclose(record.common.composition["Zn"], 2.0 / 3.0)


def test_canonical_raw_source_record_structure_preserves_structure_payload() -> None:
    record = CanonicalRawSourceRecord.model_validate(
        _record_payload(
            record_kind="structure",
            source_record_id="structure-001",
            structure_representations=[
                {
                    "representation_kind": "cif",
                    "payload_path": "data/external/sources/hypodx/2026-04-03/structure-001.cif",
                    "payload_format": "cif",
                    "content_hash": "sha256:cif",
                    "structure_summary": {"site_count": 12},
                }
            ],
        )
    )

    assert record.record_kind == "structure"
    assert len(record.common.structure_representations) == 1
    assert record.common.structure_representations[0].representation_kind == "cif"


def test_canonical_raw_source_record_derive_local_record_id_is_deterministic() -> None:
    first = derive_local_record_id("materials-project", "mp-2026-04", "mp-123")
    second = derive_local_record_id("materials-project", "mp-2026-04", "mp-123")

    assert first == second
    assert first.startswith("src_materials_project_")


def test_canonical_raw_source_record_rejects_invalid_local_record_id() -> None:
    with pytest.raises(ValidationError):
        CanonicalRawSourceRecord.model_validate(
            _record_payload(local_record_id="bad-record-id")
        )


def test_canonical_raw_source_record_rejects_wrong_source_prefix() -> None:
    mismatched = derive_local_record_id("cod", "2026-04-03", "phase-001")

    with pytest.raises(ValidationError):
        CanonicalRawSourceRecord.model_validate(
            _record_payload(local_record_id=mismatched)
        )
