from __future__ import annotations

from pytest import MonkeyPatch

from materials_discovery.common.schema import CandidateRecord, SystemConfig
from materials_discovery.hifi_digital.geometry_prefilter import run_geometry_prefilter
from materials_discovery.hifi_digital.md_stability import run_short_md_stability
from materials_discovery.hifi_digital.phonon_mlip import run_mlip_phonon_checks
from materials_discovery.hifi_digital.xrd_validate import validate_xrd_signatures


def _crowded_candidate() -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": "md_prefilter_001",
            "system": "Sc-Zn",
            "template_family": "cubic_proxy_1_0",
            "cell": {
                "a": 10.0,
                "b": 10.0,
                "c": 10.0,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            "sites": [
                {
                    "label": "A1",
                    "qphi": [[0, 0], [0, 0], [0, 0]],
                    "species": "Sc",
                    "occ": 1.0,
                    "fractional_position": [0.50, 0.50, 0.50],
                },
                {
                    "label": "A2",
                    "qphi": [[1, 0], [0, 0], [0, 0]],
                    "species": "Zn",
                    "occ": 1.0,
                    "fractional_position": [0.505, 0.50, 0.50],
                },
                {
                    "label": "A3",
                    "qphi": [[0, 1], [0, 0], [0, 0]],
                    "species": "Zn",
                    "occ": 1.0,
                    "fractional_position": [0.51, 0.50, 0.50],
                },
            ],
            "composition": {"Sc": 0.333333, "Zn": 0.666667},
            "digital_validation": {
                "status": "committee_relaxed",
                "committee_energy_ev_per_atom": {"MACE": -2.9, "CHGNet": -2.91},
                "uncertainty_ev_per_atom": 0.01,
                "delta_e_proxy_hull_ev_per_atom": 0.02,
            },
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def _real_config() -> SystemConfig:
    return SystemConfig.model_validate(
        {
            "system_name": "Sc-Zn",
            "template_family": "cubic_proxy_1_0",
            "species": ["Sc", "Zn"],
            "composition_bounds": {
                "Sc": {"min": 0.2, "max": 0.4},
                "Zn": {"min": 0.6, "max": 0.8},
            },
            "coeff_bounds": {"min": -2, "max": 2},
            "seed": 31,
            "default_count": 8,
            "backend": {
                "mode": "real",
                "phonon_adapter": "phonon_exec_cache_v1",
                "md_adapter": "md_exec_cache_v1",
                "xrd_adapter": "xrd_exec_cache_v1",
            },
        }
    )


def test_geometry_prefilter_short_circuits_expensive_real_backends(
    monkeypatch: MonkeyPatch,
) -> None:
    config = _real_config()
    filtered = run_geometry_prefilter([_crowded_candidate()], config=config)

    validation = filtered[0].digital_validation
    assert validation.geometry_prefilter_pass is False
    assert validation.geometry_prefilter_reason == "min_distance"
    assert validation.phonon_pass is False
    assert validation.md_pass is False
    assert validation.xrd_pass is False

    def fail(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("expensive adapter should not be resolved for prefiltered candidates")

    monkeypatch.setattr(
        "materials_discovery.hifi_digital.phonon_mlip.resolve_phonon_adapter",
        fail,
    )
    monkeypatch.setattr(
        "materials_discovery.hifi_digital.md_stability.resolve_md_adapter",
        fail,
    )
    monkeypatch.setattr(
        "materials_discovery.hifi_digital.xrd_validate.resolve_xrd_adapter",
        fail,
    )

    phonon_checked = run_mlip_phonon_checks(filtered, config=config)
    md_checked = run_short_md_stability(phonon_checked, config=config)
    xrd_checked = validate_xrd_signatures(config, md_checked)

    final_validation = xrd_checked[0].digital_validation
    assert final_validation.geometry_prefilter_pass is False
    assert final_validation.phonon_imaginary_modes == 99
    assert final_validation.md_stability_score == 0.0
    assert final_validation.xrd_confidence == 0.0
