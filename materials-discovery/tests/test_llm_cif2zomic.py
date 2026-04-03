from __future__ import annotations

from pathlib import Path

from materials_discovery.data_sources.adapters.cif_conversion import cif_to_canonical_record
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord
from materials_discovery.data_sources.types import SourceAdapterInfo
from materials_discovery.llm.converters.cif2zomic import (
    canonical_record_to_zomic,
    cif_path_to_zomic,
)


def _cod_fixture() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "cod_sample.cif"


def _hypodx_fixture() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "hypodx_approximant_sample.cif"


def test_cif_path_to_zomic_converts_cod_fixture_into_corpus_example() -> None:
    example = cif_path_to_zomic(
        _cod_fixture(),
        source_family="canonical_source",
        source_record_id="cod-001",
        system="Sc-Zn",
    )

    assert example.provenance.source_family == "canonical_source"
    assert example.provenance.system == "Sc-Zn"
    assert example.labels


def test_canonical_record_to_zomic_accepts_canonical_cif_representation() -> None:
    record = cif_to_canonical_record(
        {
            "cif_path": str(_cod_fixture()),
            "cod_id": "cod-001",
        },
        "cod_fixture_v1",
        Path("materials-discovery/data/external/sources/cod/raw_rows.jsonl"),
        SourceAdapterInfo(
            adapter_key="cif_archive_v1",
            source_key="cod",
            adapter_family="cif_conversion",
            version="0.1.0",
            description="fixture",
        ),
    )

    example = canonical_record_to_zomic(record)

    assert example.provenance.source_record_id == record.local_record_id
    assert example.properties["source_name"] == "Crystallography Open Database"


def test_cif_conversion_marks_approximate_fidelity_by_default() -> None:
    example = cif_path_to_zomic(
        _cod_fixture(),
        source_family="canonical_source",
        source_record_id="cod-001",
        system="Sc-Zn",
    )

    assert example.provenance.fidelity_tier == "approximate"


def test_hypodx_style_fixture_follows_same_conversion_path() -> None:
    example = cif_path_to_zomic(
        _hypodx_fixture(),
        source_family="canonical_source",
        source_record_id="hypodx-001",
        system="Al-Cu-Fe",
    )

    assert example.provenance.system == "Al-Cu-Fe"
    assert example.composition is not None
    assert set(example.composition) == {"Al", "Cu", "Fe"}


def test_canonical_record_fallback_handles_non_cif_records() -> None:
    record = CanonicalRawSourceRecord.model_validate(
        {
            "schema_version": "raw-source-record/v1",
            "local_record_id": "src_hypodx_1234567890abcdef",
            "record_kind": "phase_entry",
            "source": {
                "source_key": "hypodx",
                "source_name": "HYPOD-X",
                "source_record_id": "al-cu-fe|i-phase|0",
            },
            "access": {
                "access_level": "open",
                "auth_required": False,
                "access_surface": "fixture",
                "redistribution_posture": "allowed",
            },
            "license": {
                "license_expression": "CC-BY-4.0",
                "license_category": "open",
                "attribution_required": True,
            },
            "snapshot": {
                "snapshot_id": "hypodx_fixture",
                "retrieved_at_utc": "2026-04-03T00:00:00Z",
                "retrieval_mode": "fixture",
                "snapshot_manifest_path": "data/external/sources/hypodx/hypodx_fixture/snapshot_manifest.json",
            },
            "raw_payload": {
                "payload_path": "data/external/sources/hypodx/hypodx_fixture/raw_rows.jsonl",
                "payload_format": "jsonl",
                "content_hash": "abc123",
            },
            "common": {
                "chemical_system": "Al-Cu-Fe",
                "elements": ["Al", "Cu", "Fe"],
                "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
                "structure_representations": [],
            },
            "lineage": {
                "adapter_key": "hypodx_fixture_v1",
                "adapter_family": "direct",
                "adapter_version": "0.1.0",
                "fetch_manifest_id": "fetch-001",
                "normalize_manifest_id": "normalize-001",
            },
        }
    )

    example = canonical_record_to_zomic(record)

    assert example.provenance.fidelity_tier == "approximate"
    assert example.properties["source_name"] == "HYPOD-X"
