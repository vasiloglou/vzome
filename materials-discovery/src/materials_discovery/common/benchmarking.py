from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import Any

from materials_discovery.common.io import ensure_parent, load_json_object, workspace_root
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


@dataclass
class BenchmarkRunContext:
    """Additive run-context block that makes Phase 4 lanes comparable.

    Assembled once in ``cli.py`` from config + ingest/reference-pack lineage
    and then threaded forward to downstream stage manifests and the
    benchmark-pack summary artifact.  All fields are optional to preserve
    backward-compatibility when the context is absent.
    """

    reference_pack_id: str | None = None
    reference_pack_fingerprint: str | None = None
    source_keys: list[str] = field(default_factory=list)
    benchmark_corpus: str | None = None
    backend_mode: str | None = None
    lane_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "reference_pack_id": self.reference_pack_id,
            "reference_pack_fingerprint": self.reference_pack_fingerprint,
            "source_keys": list(self.source_keys),
            "benchmark_corpus": self.benchmark_corpus,
            "backend_mode": self.backend_mode,
            "lane_id": self.lane_id,
        }


def build_benchmark_run_context(
    config: SystemConfig,
    source_lineage: dict[str, Any] | None = None,
) -> BenchmarkRunContext:
    """Assemble a :class:`BenchmarkRunContext` from a system config and optional
    ingest source-lineage dict.

    The lineage dict is produced by ``_ingest_via_reference_pack`` or
    ``_ingest_via_source_registry`` in ``cli.py`` and stored as
    ``ArtifactManifest.source_lineage``.  When absent the context still records
    the config-level fields (backend mode, benchmark corpus, reference-pack
    config if present).
    """
    reference_pack_id: str | None = None
    reference_pack_fingerprint: str | None = None
    source_keys: list[str] = []

    ingestion = config.ingestion
    if ingestion is not None and ingestion.reference_pack is not None:
        reference_pack_id = ingestion.reference_pack.pack_id
        source_keys = [m.source_key for m in ingestion.reference_pack.members]

    if source_lineage is not None:
        # Lineage from _ingest_via_reference_pack path
        if "pack_id" in source_lineage and reference_pack_id is None:
            reference_pack_id = str(source_lineage["pack_id"])
        if "pack_fingerprint" in source_lineage:
            reference_pack_fingerprint = str(source_lineage["pack_fingerprint"])
        if "member_sources" in source_lineage and not source_keys:
            members = source_lineage.get("member_sources")
            if isinstance(members, list):
                source_keys = [
                    str(m.get("source_key", ""))
                    for m in members
                    if isinstance(m, dict) and m.get("source_key")
                ]
        # Lineage from _ingest_via_source_registry path (single source)
        if not source_keys and "source_key" in source_lineage:
            source_keys = [str(source_lineage["source_key"])]

    if not source_keys and ingestion is not None and ingestion.source_key:
        source_keys = [ingestion.source_key]

    benchmark_corpus = config.backend.benchmark_corpus
    backend_mode = config.backend.mode

    # Derive a lane identifier: pack_id:backend_mode or source_key:backend_mode
    if reference_pack_id:
        lane_id = f"{reference_pack_id}:{backend_mode}"
    elif source_keys:
        lane_id = f"{source_keys[0]}:{backend_mode}"
    else:
        lane_id = f"{config.system_name.lower().replace('-', '_')}:{backend_mode}"

    return BenchmarkRunContext(
        reference_pack_id=reference_pack_id,
        reference_pack_fingerprint=reference_pack_fingerprint,
        source_keys=source_keys,
        benchmark_corpus=benchmark_corpus,
        backend_mode=backend_mode,
        lane_id=lane_id,
    )


def write_benchmark_pack(
    config: SystemConfig,
    benchmark_context: BenchmarkRunContext,
    stage_manifest_paths: dict[str, str],
    report_metrics: dict[str, Any],
    output_path: Path,
) -> None:
    """Write the dedicated ``benchmark_pack.json`` output artifact.

    The benchmark-pack artifact is a high-level index that references the key
    stage manifests and calibration JSONs together with the benchmark/reference
    metadata needed for operator comparison.  It deliberately does NOT
    duplicate full payload content from those artifacts.

    Parameters
    ----------
    config:
        The active system config.
    benchmark_context:
        The assembled run context (reference-pack identity, sources, lane).
    stage_manifest_paths:
        Mapping of artifact role -> relative-or-absolute path string for key
        stage manifests and calibration outputs.
    report_metrics:
        Top-level report metrics surfaced for comparison (e.g. release_gate,
        summary slice).
    output_path:
        Where to write the artifact.
    """
    payload: dict[str, Any] = {
        "schema_version": "benchmark-pack/v1",
        "system": config.system_name,
        "backend_mode": config.backend.mode,
        "benchmark_context": benchmark_context.as_dict(),
        "stage_manifest_paths": stage_manifest_paths,
        "report_metrics": report_metrics,
    }
    content = json.dumps(payload, sort_keys=True)
    ensure_parent(output_path)
    output_path.write_text(content, encoding="utf-8")


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
