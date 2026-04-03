from __future__ import annotations

import json
from pathlib import Path

from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import CandidateRecord, SystemConfig
from materials_discovery.data_sources.projection import project_canonical_records
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord, derive_local_record_id
from materials_discovery.hifi_digital.hull_proxy import compute_proxy_hull


def _candidate(
    candidate_id: str,
    composition: dict[str, float],
    committee_mean_energy: float,
) -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": candidate_id,
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
            "composition": composition,
            "screen": {"energy_proxy_ev_per_atom": committee_mean_energy},
            "digital_validation": {
                "status": "uncertainty_scored",
                "committee": ["MACE", "CHGNet", "MatterSim"],
                "committee_energy_ev_per_atom": {
                    "MACE": round(committee_mean_energy - 0.002, 6),
                    "CHGNet": round(committee_mean_energy, 6),
                    "MatterSim": round(committee_mean_energy + 0.002, 6),
                },
                "committee_std_ev_per_atom": 0.002,
                "uncertainty_ev_per_atom": 0.002,
            },
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def _real_config() -> SystemConfig:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    return SystemConfig.model_validate(load_yaml(config_path))


def _canonical_record(
    *,
    source_record_id: str,
    phase_name: str,
    composition: dict[str, float],
    record_kind: str = "phase_entry",
) -> CanonicalRawSourceRecord:
    return CanonicalRawSourceRecord.model_validate(
        {
            "local_record_id": derive_local_record_id("hypodx", "projected-v1", source_record_id),
            "record_kind": record_kind,
            "source": {
                "source_key": "hypodx",
                "source_name": "HYPOD-X",
                "source_record_id": source_record_id,
                "record_title": phase_name,
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
                "snapshot_id": "projected-v1",
                "retrieved_at_utc": "2026-04-03T15:30:00Z",
                "retrieval_mode": "fixture",
                "snapshot_manifest_path": "data/external/sources/hypodx/projected-v1/snapshot_manifest.json",
            },
            "raw_payload": {
                "payload_path": "data/external/sources/hypodx/projected-v1/raw_rows.jsonl",
                "payload_format": "jsonl",
                "content_hash": f"sha256:{source_record_id}",
            },
            "common": {
                "chemical_system": "Al-Cu-Fe",
                "elements": ["Al", "Cu", "Fe"],
                "formula_raw": phase_name,
                "formula_reduced": phase_name,
                "composition": composition,
                "reported_properties": {"phase_name": phase_name},
                "keywords": ["quasicrystal"] if phase_name == "i-phase" else [],
                "structure_representations": (
                    [
                        {
                            "representation_kind": "cif",
                            "payload_format": "cif",
                            "content_hash": f"sha256:{source_record_id}:cif",
                        }
                    ]
                    if record_kind == "structure"
                    else []
                ),
            },
            "lineage": {
                "adapter_key": "fixture_json_v1",
                "adapter_family": "direct",
                "adapter_version": "v1",
                "fetch_manifest_id": "fetch_manifest_001",
                "normalize_manifest_id": "normalize_manifest_001",
            },
        }
    )


def test_reference_aware_hull_matches_exact_reference_phase() -> None:
    config = _real_config()
    candidate = _candidate("md_ref", {"Al": 0.7, "Cu": 0.2, "Fe": 0.1}, committee_mean_energy=-2.92)

    scored = compute_proxy_hull([candidate], config=config)
    validation = scored[0].digital_validation

    assert validation.proxy_hull_reference_phases == ["i-phase"]
    assert validation.proxy_hull_reference_distance == 0.0
    assert validation.proxy_hull_baseline_ev_per_atom is not None
    assert validation.delta_e_proxy_hull_ev_per_atom is not None


def test_reference_aware_hull_uses_convex_mixture_when_available() -> None:
    config = _real_config()
    candidate = _candidate(
        "md_mix",
        {"Al": 0.625, "Cu": 0.25, "Fe": 0.125},
        committee_mean_energy=-2.84,
    )

    scored = compute_proxy_hull([candidate], config=config)
    validation = scored[0].digital_validation

    assert validation.proxy_hull_reference_distance == 0.0
    assert validation.proxy_hull_reference_phases is not None
    assert len(validation.proxy_hull_reference_phases) >= 2
    assert set(validation.proxy_hull_reference_phases).issubset({"beta", "i-phase", "lambda"})


def test_reference_aware_hull_accepts_projected_reference_rows(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config = _real_config()
    projected, _ = project_canonical_records(
        [
            _canonical_record(
                source_record_id="i-phase-001",
                phase_name="i-phase",
                composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            ),
            _canonical_record(
                source_record_id="beta-001",
                phase_name="beta",
                composition={"Al": 0.8, "Cu": 0.15, "Fe": 0.05},
                record_kind="structure",
            ),
        ],
        config,
    )
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    processed_path = processed_dir / "al_cu_fe_reference_phases.jsonl"
    processed_path.write_text(
        "".join(json.dumps(row.model_dump(mode="json"), sort_keys=True) + "\n" for row in projected),
        encoding="utf-8",
    )

    monkeypatch.setattr("materials_discovery.hifi_digital.hull_proxy.workspace_root", lambda: tmp_path)
    candidate = _candidate("md_projected", {"Al": 0.7, "Cu": 0.2, "Fe": 0.1}, committee_mean_energy=-2.92)
    scored = compute_proxy_hull([candidate], config=config)
    validation = scored[0].digital_validation

    assert validation.proxy_hull_reference_phases == ["i-phase"]
    assert validation.proxy_hull_reference_distance == 0.0
