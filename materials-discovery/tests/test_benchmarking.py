from __future__ import annotations

from pathlib import Path

from materials_discovery.active_learning.train_surrogate import feature_names
from materials_discovery.common.benchmarking import load_calibration_profile
from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import SystemConfig


def test_benchmark_profile_loads_for_real_config() -> None:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))

    names = feature_names(config)
    profile = load_calibration_profile(config, feature_names=names)

    assert profile.source.endswith("al_cu_fe_benchmark.json")
    assert set(profile.stable_feature_centroid) == set(names)
    assert set(profile.unstable_feature_centroid) == set(names)
    assert 0.0 < profile.delta_hull_soft_cap < 0.10
    assert 0.0 < profile.uncertainty_soft_cap < 0.05
    assert 0.5 < profile.md_stability_floor < 0.9
    assert 0.5 < profile.xrd_confidence_floor < 0.9
    assert 0.05 < profile.report_distinctiveness_floor < 0.2
    assert 0.2 < profile.ood_ceiling < 0.6
    assert 0.4 < profile.active_learning_threshold < 0.8
