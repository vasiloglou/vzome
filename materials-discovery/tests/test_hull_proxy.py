from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import CandidateRecord, SystemConfig
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
