from __future__ import annotations

import json
from pathlib import Path

from pytest import MonkeyPatch

from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import CandidateRecord, SystemConfig
from materials_discovery.data_sources.projection import (
    project_canonical_records,
    project_snapshot_to_ingest_records,
    projection_fingerprint,
)
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord, derive_local_record_id
from materials_discovery.hifi_digital.hull_proxy import compute_proxy_hull


def _canonical_record(
    *,
    source_key: str = "hypodx",
    source_name: str = "HYPOD-X",
    source_record_id: str = "phase-001",
    record_kind: str = "phase_entry",
    chemical_system: str = "Al-Cu-Fe",
    elements: list[str] | None = None,
    composition: dict[str, float] | None = None,
    phase_name: str | None = None,
    record_title: str | None = None,
    formula_reduced: str | None = "Al7Cu2Fe",
    keywords: list[str] | None = None,
    source_metadata: dict[str, object] | None = None,
    structure_representations: list[dict[str, object]] | None = None,
    snapshot_id: str = "fixture_snapshot_v1",
) -> CanonicalRawSourceRecord:
    payload = {
        "local_record_id": derive_local_record_id(source_key, snapshot_id, source_record_id),
        "record_kind": record_kind,
        "source": {
            "source_key": source_key,
            "source_name": source_name,
            "source_record_id": source_record_id,
            "source_record_url": f"https://example.test/{source_record_id}",
            "record_title": record_title,
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
            "retrieved_at_utc": "2026-04-03T13:00:00Z",
            "retrieval_mode": "fixture",
            "snapshot_manifest_path": f"data/external/sources/{source_key}/{snapshot_id}/snapshot_manifest.json",
        },
        "raw_payload": {
            "payload_path": f"data/external/sources/{source_key}/{snapshot_id}/raw_rows.jsonl",
            "payload_format": "jsonl",
            "content_hash": f"sha256:{source_record_id}",
        },
        "common": {
            "chemical_system": chemical_system,
            "elements": elements or ["Al", "Cu", "Fe"],
            "formula_raw": formula_reduced,
            "formula_reduced": formula_reduced,
            "composition": composition,
            "structure_representations": structure_representations or [],
            "reported_properties": {"phase_name": phase_name} if phase_name is not None else {},
            "keywords": keywords or [],
        },
        "lineage": {
            "adapter_key": "fixture_direct",
            "adapter_family": "direct",
            "adapter_version": "v1",
            "fetch_manifest_id": "fetch_manifest_001",
            "normalize_manifest_id": "normalize_manifest_001",
        },
        "source_metadata": source_metadata or {},
    }
    return CanonicalRawSourceRecord.model_validate(payload)


def _real_config() -> SystemConfig:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    return SystemConfig.model_validate(load_yaml(config_path))


def _candidate() -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": "md_projected",
            "system": "Al-Cu-Fe",
            "template_family": "icosahedral_approximant_1_1",
            "cell": {
                "a": 14.2,
                "b": 14.2,
                "c": 14.2,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            "sites": [
                {
                    "label": "S1",
                    "qphi": [[1, 0], [0, 1], [-1, 1]],
                    "species": "Al",
                    "occ": 1.0,
                }
            ],
            "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            "screen": {"energy_proxy_ev_per_atom": -2.91},
            "digital_validation": {
                "status": "uncertainty_scored",
                "committee": ["MACE", "CHGNet", "MatterSim"],
                "committee_energy_ev_per_atom": {
                    "MACE": -2.922,
                    "CHGNet": -2.92,
                    "MatterSim": -2.918,
                },
                "committee_std_ev_per_atom": 0.002,
                "uncertainty_ev_per_atom": 0.002,
            },
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def test_source_projection_phase_entry_projects_qc_metadata() -> None:
    config = _real_config()
    projected, summary = project_canonical_records(
        [
            _canonical_record(
                source_record_id="i-phase-001",
                phase_name="i-phase",
                composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
                keywords=["icosahedral", "quasicrystal"],
            )
        ],
        config,
    )

    assert summary.input_count == 1
    assert summary.matched_system_count == 1
    assert summary.deduped_count == 1
    assert projected[0].phase_name == "i-phase"
    assert projected[0].system == "Al-Cu-Fe"
    assert projected[0].source == "hypodx"
    assert projected[0].metadata["source_key"] == "hypodx"
    assert projected[0].metadata["record_kind"] == "phase_entry"
    assert projected[0].metadata["projection_reason"] == "reported_properties.phase_name"
    assert projected[0].metadata["snapshot_id"] == "fixture_snapshot_v1"
    assert projected[0].metadata["qc_family"] == ["icosahedral", "quasicrystal"]


def test_source_projection_structure_record_uses_formula_fallback() -> None:
    config = _real_config()
    projected, summary = project_canonical_records(
        [
            _canonical_record(
                source_key="materials_project",
                source_name="Materials Project",
                source_record_id="mp-123",
                record_kind="structure",
                phase_name=None,
                record_title=None,
                formula_reduced="Al6Cu2Fe",
                composition={"Al": 0.6666667, "Cu": 0.2222222, "Fe": 0.1111111},
                structure_representations=[
                    {
                        "representation_kind": "materials_project_structure",
                        "payload_format": "materials-project-json",
                        "content_hash": "sha256:structure",
                        "structure_summary": {"site_count": 36},
                    }
                ],
            )
        ],
        config,
    )

    assert summary.deduped_count == 1
    assert projected[0].phase_name == "Al6Cu2Fe"
    assert projected[0].metadata["projection_reason"] == "common.formula_reduced"
    assert projected[0].metadata["structure_tags"] == [
        "has_structure",
        "record_kind:structure",
        "representation:materials_project_structure",
    ]


def test_source_projection_filters_mismatched_systems_and_skips_missing_composition() -> None:
    config = _real_config()
    projected, summary = project_canonical_records(
        [
            _canonical_record(
                source_record_id="sc-zn-001",
                chemical_system="Sc-Zn",
                elements=["Sc", "Zn"],
                composition={"Sc": 0.3333333, "Zn": 0.6666667},
            ),
            _canonical_record(
                source_record_id="missing-comp-001",
                composition=None,
                phase_name="beta",
            ),
            _canonical_record(
                source_record_id="good-001",
                phase_name="beta",
                composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            ),
        ],
        config,
    )

    assert len(projected) == 1
    assert summary.skipped_system_mismatch_count == 1
    assert summary.skipped_missing_composition_count == 1
    assert summary.matched_system_count == 2
    assert summary.deduped_count == 1


def test_source_projection_dedupe_prefers_phase_entries_and_uses_locked_fingerprint() -> None:
    config = _real_config()
    projected, summary = project_canonical_records(
        [
            _canonical_record(
                source_key="materials_project",
                source_name="Materials Project",
                source_record_id="mp-123",
                record_kind="structure",
                phase_name="beta",
                composition={"Fe": 0.1, "Cu": 0.2, "Al": 0.7},
                structure_representations=[
                    {
                        "representation_kind": "materials_project_structure",
                        "payload_format": "materials-project-json",
                        "content_hash": "sha256:structure",
                    }
                ],
            ),
            _canonical_record(
                source_key="hypodx",
                source_name="HYPOD-X",
                source_record_id="beta-001",
                record_kind="phase_entry",
                phase_name="beta",
                composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            ),
        ],
        config,
    )

    assert summary.projected_count == 2
    assert summary.deduped_count == 1
    assert summary.duplicate_dropped_count == 1
    assert projected[0].metadata["record_kind"] == "phase_entry"
    assert projection_fingerprint(projected[0]) == (
        "al-cu-fe",
        "beta",
        (("al", 0.7), ("cu", 0.2), ("fe", 0.1)),
    )


def test_source_projection_snapshot_wrapper_and_downstream_consumer_compatibility(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    config = _real_config()
    canonical_path = tmp_path / "canonical_records.jsonl"
    rows = [
        _canonical_record(
            source_record_id="i-phase-001",
            phase_name="i-phase",
            composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            keywords=["quasicrystal"],
        ).model_dump(mode="json"),
        _canonical_record(
            source_record_id="beta-001",
            phase_name="beta",
            composition={"Al": 0.8, "Cu": 0.15, "Fe": 0.05},
        ).model_dump(mode="json"),
    ]
    canonical_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    projected, summary = project_snapshot_to_ingest_records(canonical_path, config)
    assert summary.deduped_count == 2

    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    processed_path = processed_dir / "al_cu_fe_reference_phases.jsonl"
    processed_path.write_text(
        "".join(json.dumps(row.model_dump(mode="json"), sort_keys=True) + "\n" for row in projected),
        encoding="utf-8",
    )

    monkeypatch.setattr("materials_discovery.hifi_digital.hull_proxy.workspace_root", lambda: tmp_path)
    scored = compute_proxy_hull([_candidate()], config=config)
    validation = scored[0].digital_validation

    assert validation.proxy_hull_reference_phases == ["i-phase"]
    assert validation.proxy_hull_reference_distance == 0.0
