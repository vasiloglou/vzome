from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from materials_discovery.common.io import load_json_object, workspace_root
from materials_discovery.common.schema import SystemConfig


@dataclass(frozen=True)
class BenchmarkCase:
    label: str
    outcome: str
    composition: dict[str, float]
    features: dict[str, float]
    metrics: dict[str, float]


@dataclass(frozen=True)
class CalibrationProfile:
    system: str
    source: str
    stable_feature_centroid: dict[str, float]
    unstable_feature_centroid: dict[str, float]
    delta_hull_soft_cap: float
    uncertainty_soft_cap: float
    reference_distance_soft_cap: float
    md_stability_floor: float
    xrd_confidence_floor: float
    report_distinctiveness_floor: float
    ood_ceiling: float
    active_learning_threshold: float


_DEFAULT_STABLE_FEATURES = {
    "frac_Al": 0.68,
    "frac_Cu": 0.20,
    "frac_Fe": 0.12,
    "qphi_complexity_norm": 0.34,
    "radius_mismatch_norm": 0.26,
    "en_spread_norm": 0.24,
    "pair_mixing_preference": 0.76,
    "energy_preference": 0.81,
    "packing_preference": 0.79,
    "shortlist_signal": 0.42,
}

_DEFAULT_UNSTABLE_FEATURES = {
    "frac_Al": 0.82,
    "frac_Cu": 0.08,
    "frac_Fe": 0.10,
    "qphi_complexity_norm": 0.73,
    "radius_mismatch_norm": 0.59,
    "en_spread_norm": 0.58,
    "pair_mixing_preference": 0.28,
    "energy_preference": 0.34,
    "packing_preference": 0.44,
    "shortlist_signal": 0.16,
}


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")



def _benchmark_path(config: SystemConfig) -> Path | None:
    configured = config.backend.benchmark_corpus
    if configured is not None:
        path = Path(configured)
        return path if path.is_absolute() else workspace_root() / path

    default = (
        workspace_root()
        / "data"
        / "benchmarks"
        / f"{_system_slug(config.system_name)}_benchmark.json"
    )
    return default if default.exists() else None



def _mean(values: list[float], fallback: float) -> float:
    return mean(values) if values else fallback



def _midpoint_lower_better(stable: list[float], unstable: list[float], fallback: float) -> float:
    if stable and unstable:
        return max(1e-6, (max(stable) + min(unstable)) / 2.0)
    if stable:
        return max(1e-6, max(stable) * 1.15)
    if unstable:
        return max(1e-6, min(unstable) * 0.85)
    return fallback



def _midpoint_higher_better(stable: list[float], unstable: list[float], fallback: float) -> float:
    if stable and unstable:
        return min(0.999999, max(1e-6, (min(stable) + max(unstable)) / 2.0))
    if stable:
        return min(0.999999, min(stable) * 0.95)
    if unstable:
        return min(0.999999, max(unstable) * 1.05)
    return fallback



def _centroid(
    rows: list[dict[str, float]],
    feature_names: list[str],
    fallback: dict[str, float],
) -> dict[str, float]:
    if not feature_names:
        return {}
    if not rows:
        return {
            name: round(float(fallback.get(name, 0.0)), 6)
            for name in feature_names
        }
    return {
        name: round(
            _mean(
                [float(row.get(name, 0.0)) for row in rows],
                float(fallback.get(name, 0.0)),
            ),
            6,
        )
        for name in feature_names
    }



def load_benchmark_cases(config: SystemConfig) -> list[BenchmarkCase]:
    path = _benchmark_path(config)
    if path is None or not path.exists():
        return []

    payload = load_json_object(path)
    raw_cases = payload.get("cases", [])
    if not isinstance(raw_cases, list):
        raise ValueError(f"benchmark corpus cases must be a list: {path}")

    cases: list[BenchmarkCase] = []
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            continue
        label = raw_case.get("label")
        outcome = raw_case.get("outcome")
        composition = raw_case.get("composition")
        features = raw_case.get("features")
        metrics = raw_case.get("metrics")
        if not isinstance(label, str) or outcome not in {"stable", "unstable"}:
            continue
        if (
            not isinstance(composition, dict)
            or not isinstance(features, dict)
            or not isinstance(metrics, dict)
        ):
            continue
        parsed_composition = {
            str(symbol): float(frac)
            for symbol, frac in composition.items()
            if isinstance(symbol, str) and isinstance(frac, int | float)
        }
        parsed_features = {
            str(name): float(value)
            for name, value in features.items()
            if isinstance(name, str) and isinstance(value, int | float)
        }
        parsed_metrics = {
            str(name): float(value)
            for name, value in metrics.items()
            if isinstance(name, str) and isinstance(value, int | float)
        }
        cases.append(
            BenchmarkCase(
                label=label,
                outcome=outcome,
                composition=parsed_composition,
                features=parsed_features,
                metrics=parsed_metrics,
            )
        )
    return cases



def load_calibration_profile(
    config: SystemConfig,
    feature_names: list[str] | None = None,
) -> CalibrationProfile:
    feature_names = feature_names or []
    path = _benchmark_path(config)
    cases = load_benchmark_cases(config)
    stable_cases = [case for case in cases if case.outcome == "stable"]
    unstable_cases = [case for case in cases if case.outcome == "unstable"]

    if not cases:
        return CalibrationProfile(
            system=config.system_name,
            source="builtin_fallback",
            stable_feature_centroid=_centroid([], feature_names, _DEFAULT_STABLE_FEATURES),
            unstable_feature_centroid=_centroid([], feature_names, _DEFAULT_UNSTABLE_FEATURES),
            delta_hull_soft_cap=0.10,
            uncertainty_soft_cap=0.05,
            reference_distance_soft_cap=0.18,
            md_stability_floor=0.62,
            xrd_confidence_floor=0.63,
            report_distinctiveness_floor=0.12,
            ood_ceiling=0.48,
            active_learning_threshold=0.56,
        )

    stable_features = [case.features for case in stable_cases]
    unstable_features = [case.features for case in unstable_cases]

    stable_delta = [case.metrics.get("delta_hull_ev_per_atom", 0.0) for case in stable_cases]
    unstable_delta = [case.metrics.get("delta_hull_ev_per_atom", 0.0) for case in unstable_cases]
    stable_uncertainty = [case.metrics.get("uncertainty_ev_per_atom", 0.0) for case in stable_cases]
    unstable_uncertainty = [
        case.metrics.get("uncertainty_ev_per_atom", 0.0) for case in unstable_cases
    ]
    stable_reference = [case.metrics.get("reference_distance", 0.0) for case in stable_cases]
    unstable_reference = [case.metrics.get("reference_distance", 0.0) for case in unstable_cases]
    stable_md = [case.metrics.get("md_stability_score", 0.0) for case in stable_cases]
    unstable_md = [case.metrics.get("md_stability_score", 0.0) for case in unstable_cases]
    stable_xrd = [case.metrics.get("xrd_confidence", 0.0) for case in stable_cases]
    unstable_xrd = [case.metrics.get("xrd_confidence", 0.0) for case in unstable_cases]
    stable_distinctiveness = [case.metrics.get("xrd_distinctiveness", 0.0) for case in stable_cases]
    unstable_distinctiveness = [
        case.metrics.get("xrd_distinctiveness", 0.0) for case in unstable_cases
    ]
    stable_ood = [case.metrics.get("ood_score", 0.0) for case in stable_cases]
    unstable_ood = [case.metrics.get("ood_score", 0.0) for case in unstable_cases]

    stable_signal = [
        0.40 * case.features.get("energy_preference", 0.0)
        + 0.25 * case.features.get("packing_preference", 0.0)
        + 0.20 * case.features.get("pair_mixing_preference", 0.0)
        + 0.15 * (1.0 - case.metrics.get("ood_score", 0.0))
        for case in stable_cases
    ]
    unstable_signal = [
        0.40 * case.features.get("energy_preference", 0.0)
        + 0.25 * case.features.get("packing_preference", 0.0)
        + 0.20 * case.features.get("pair_mixing_preference", 0.0)
        + 0.15 * (1.0 - case.metrics.get("ood_score", 0.0))
        for case in unstable_cases
    ]

    return CalibrationProfile(
        system=config.system_name,
        source=str(path) if path is not None else "benchmark_corpus",
        stable_feature_centroid=_centroid(
            stable_features,
            feature_names,
            _DEFAULT_STABLE_FEATURES,
        ),
        unstable_feature_centroid=_centroid(
            unstable_features,
            feature_names,
            _DEFAULT_UNSTABLE_FEATURES,
        ),
        delta_hull_soft_cap=round(_midpoint_lower_better(stable_delta, unstable_delta, 0.10), 6),
        uncertainty_soft_cap=round(
            _midpoint_lower_better(stable_uncertainty, unstable_uncertainty, 0.05),
            6,
        ),
        reference_distance_soft_cap=round(
            _midpoint_lower_better(stable_reference, unstable_reference, 0.18),
            6,
        ),
        md_stability_floor=round(_midpoint_higher_better(stable_md, unstable_md, 0.62), 6),
        xrd_confidence_floor=round(_midpoint_higher_better(stable_xrd, unstable_xrd, 0.63), 6),
        report_distinctiveness_floor=round(
            _midpoint_higher_better(stable_distinctiveness, unstable_distinctiveness, 0.12),
            6,
        ),
        ood_ceiling=round(_midpoint_lower_better(stable_ood, unstable_ood, 0.48), 6),
        active_learning_threshold=round(
            _midpoint_higher_better(stable_signal, unstable_signal, 0.56),
            6,
        ),
    )
