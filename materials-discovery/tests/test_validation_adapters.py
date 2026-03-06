from __future__ import annotations

from pathlib import Path

from materials_discovery.backends.registry import resolve_committee_adapter, resolve_xrd_adapter
from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _real_config() -> SystemConfig:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    return SystemConfig.model_validate(load_yaml(config_path))



def _candidate(candidate_id: str) -> CandidateRecord:
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
            "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            "screen": {"energy_proxy_ev_per_atom": -2.95, "min_distance_proxy": 0.82},
            "digital_validation": {
                "status": "pending",
                "uncertainty_ev_per_atom": 0.015,
                "delta_e_proxy_hull_ev_per_atom": 0.02,
                "phonon_imaginary_modes": 0,
                "md_stability_score": 0.7,
            },
            "provenance": {"generator_version": "0.1.0"},
        }
    )



def test_committee_adapter_uses_snapshot_for_known_candidate() -> None:
    config = _real_config()
    adapter = resolve_committee_adapter(config.backend.mode, config.backend.committee_adapter)
    result = adapter.evaluate_candidate(config, _candidate("md_000002"))

    assert result.energies == {
        "MACE": -2.988,
        "CHGNet": -2.982,
        "MatterSim": -2.979,
    }



def test_committee_adapter_falls_back_for_unknown_candidate() -> None:
    config = _real_config()
    adapter = resolve_committee_adapter(config.backend.mode, config.backend.committee_adapter)
    result = adapter.evaluate_candidate(config, _candidate("md_unknown"))

    assert set(result.energies) == {"MACE", "CHGNet", "MatterSim"}
    assert result.energies["MACE"] != -2.988



def test_xrd_adapter_uses_snapshot_for_known_candidate() -> None:
    config = _real_config()
    adapter = resolve_xrd_adapter(config.backend.mode, config.backend.xrd_adapter)
    result = adapter.evaluate_candidate(config, _candidate("md_000005"))

    assert result.confidence == 0.81
