from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from materials_discovery.backends.types import (
    AdapterInfo,
    CommitteeEvaluation,
    MdEvaluation,
    PhononEvaluation,
    XrdEvaluation,
)
from materials_discovery.common.chemistry import (
    composition_l1_distance,
    describe_candidate,
    validate_supported_species,
)
from materials_discovery.common.io import load_json_object, load_jsonl, workspace_root
from materials_discovery.common.schema import CandidateRecord, SystemConfig

MODEL_COMMITTEE: tuple[str, str, str] = ("MACE", "CHGNet", "MatterSim")
_DEFAULT_MODEL_SHIFT: dict[str, float] = {"MACE": -0.008, "CHGNet": -0.004, "MatterSim": -0.006}


@dataclass(frozen=True)
class ValidationSnapshot:
    version: str
    by_candidate_id: dict[str, dict[str, Any]]



def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)



def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")



def _default_snapshot_path(config: SystemConfig) -> Path:
    return (
        workspace_root()
        / "data"
        / "external"
        / "pinned"
        / f"{_system_slug(config.system_name)}_validation_snapshot_2026_03_09.json"
    )



def _snapshot_path(config: SystemConfig) -> Path | None:
    configured = config.backend.validation_snapshot
    if configured is not None:
        path = Path(configured)
        return path if path.is_absolute() else workspace_root() / path
    default = _default_snapshot_path(config)
    return default if default.exists() else None


@lru_cache(maxsize=16)
def _load_snapshot(path_str: str) -> ValidationSnapshot:
    path = Path(path_str)
    payload = load_json_object(path)
    raw_candidates = payload.get("candidates", [])
    if not isinstance(raw_candidates, list):
        raise ValueError(f"validation snapshot candidates must be a list: {path}")
    by_candidate_id: dict[str, dict[str, Any]] = {}
    for raw_candidate in raw_candidates:
        if not isinstance(raw_candidate, dict):
            continue
        candidate_id = raw_candidate.get("candidate_id")
        if isinstance(candidate_id, str):
            by_candidate_id[candidate_id] = raw_candidate
    version = str(payload.get("version", "snapshot"))
    return ValidationSnapshot(version=version, by_candidate_id=by_candidate_id)



def _snapshot_row(config: SystemConfig, candidate: CandidateRecord) -> dict[str, Any] | None:
    path = _snapshot_path(config)
    if path is None or not path.exists():
        return None
    snapshot = _load_snapshot(str(path.resolve()))
    return snapshot.by_candidate_id.get(candidate.candidate_id)



def _snapshot_version(config: SystemConfig) -> str:
    path = _snapshot_path(config)
    if path is None or not path.exists():
        return "analytic"
    return _load_snapshot(str(path.resolve())).version



def _base_energy(candidate: CandidateRecord) -> float:
    screen = candidate.screen or {}
    if "energy_proxy_ev_per_atom" in screen:
        return float(screen["energy_proxy_ev_per_atom"])
    if "energy_per_atom_ev" in screen:
        return float(screen["energy_per_atom_ev"])
    return -3.0



def _committee_analytic(config: SystemConfig, candidate: CandidateRecord) -> CommitteeEvaluation:
    validate_supported_species(config.species, strict_pairs=True)
    descriptor = describe_candidate(candidate, strict_pairs=True)
    base_energy = _base_energy(candidate)
    template_shift = len(config.template_family) * 0.0002
    vec_penalty = abs(descriptor.vec - 6.0) / 6.0
    complexity_term = descriptor.qphi_complexity / 6.0
    composition_term = descriptor.dominant_fraction - (1.0 / max(1, len(candidate.composition)))

    energies = {
        "MACE": round(
            base_energy
            + template_shift
            + _DEFAULT_MODEL_SHIFT["MACE"]
            + 0.032 * descriptor.radius_mismatch
            + 0.018 * complexity_term
            + 0.009 * vec_penalty
            + 0.006 * composition_term,
            6,
        ),
        "CHGNet": round(
            base_energy
            + template_shift
            + _DEFAULT_MODEL_SHIFT["CHGNet"]
            + 0.026 * descriptor.electronegativity_spread
            + 0.021 * complexity_term
            + 0.011 * vec_penalty
            + 0.004 * composition_term,
            6,
        ),
        "MatterSim": round(
            base_energy
            + template_shift
            + _DEFAULT_MODEL_SHIFT["MatterSim"]
            + 0.028 * descriptor.radius_mismatch
            + 0.024 * descriptor.electronegativity_spread
            + 0.015 * complexity_term
            + 0.004 * composition_term,
            6,
        ),
    }
    return CommitteeEvaluation(energies=energies)



def _phonon_analytic(candidate: CandidateRecord) -> PhononEvaluation:
    descriptor = describe_candidate(candidate, strict_pairs=True)
    delta_hull = candidate.digital_validation.delta_e_proxy_hull_ev_per_atom or 0.0
    uncertainty = candidate.digital_validation.uncertainty_ev_per_atom or 0.05
    instability_index = (
        2.7 * descriptor.radius_mismatch
        + 1.8 * descriptor.electronegativity_spread
        + 0.30 * min(1.0, descriptor.qphi_complexity / 3.0)
        + 4.0 * delta_hull
        + 3.0 * uncertainty
    )
    imaginary_modes = max(0, int(round(instability_index * 2.0)))
    if descriptor.pair_mixing_enthalpy_ev_per_atom <= -0.12 and imaginary_modes > 0:
        imaginary_modes -= 1
    return PhononEvaluation(imaginary_modes=imaginary_modes)



def _md_analytic(candidate: CandidateRecord) -> MdEvaluation:
    descriptor = describe_candidate(candidate, strict_pairs=True)
    uncertainty = candidate.digital_validation.uncertainty_ev_per_atom or 0.05
    delta_hull = candidate.digital_validation.delta_e_proxy_hull_ev_per_atom or 0.1
    imaginary_modes = candidate.digital_validation.phonon_imaginary_modes or 0
    min_distance = float((candidate.screen or {}).get("min_distance_proxy", 0.6))

    packing_bonus = max(0.0, min(0.16, (min_distance - 0.55) * 0.45))
    vec_penalty = abs(descriptor.vec - 6.0) / 6.0
    stability_score = (
        0.95
        - 2.4 * uncertainty
        - 1.8 * delta_hull
        - 0.05 * max(0, imaginary_modes - 1)
        - 0.30 * descriptor.radius_mismatch
        - 0.22 * descriptor.electronegativity_spread
        - 0.08 * vec_penalty
        + packing_bonus
    )
    return MdEvaluation(stability_score=round(_clamp(stability_score, 0.0, 1.0), 6))


@lru_cache(maxsize=16)
def _load_reference_compositions(path_str: str) -> list[dict[str, float]]:
    path = Path(path_str)
    rows = load_jsonl(path)
    compositions: list[dict[str, float]] = []
    for row in rows:
        composition = row.get("composition")
        if not isinstance(composition, dict):
            continue
        parsed = {
            str(symbol): float(frac)
            for symbol, frac in composition.items()
            if isinstance(symbol, str) and isinstance(frac, int | float)
        }
        if parsed:
            compositions.append(parsed)
    return compositions



def _xrd_reference_compositions(config: SystemConfig) -> list[dict[str, float]]:
    processed_path = (
        workspace_root()
        / "data"
        / "processed"
        / f"{_system_slug(config.system_name)}_reference_phases.jsonl"
    )
    if not processed_path.exists():
        raise FileNotFoundError(
            "real-mode XRD validation requires ingested reference phases; "
            f"run 'mdisc ingest' first: {processed_path}"
        )
    compositions = _load_reference_compositions(str(processed_path.resolve()))
    if not compositions:
        raise ValueError(
            "real-mode XRD validation found no usable reference compositions in "
            f"{processed_path}"
        )
    return compositions



def _xrd_analytic(config: SystemConfig, candidate: CandidateRecord) -> XrdEvaluation:
    references = _xrd_reference_compositions(config)
    nearest_distance = min(
        composition_l1_distance(candidate.composition, reference)
        for reference in references
    )
    composition_match = 1.0 - min(1.0, nearest_distance / 0.8)
    uncertainty = candidate.digital_validation.uncertainty_ev_per_atom or 0.05
    md_score = candidate.digital_validation.md_stability_score or 0.0
    phonon_modes = candidate.digital_validation.phonon_imaginary_modes or 0
    confidence = (
        0.45
        + 0.38 * composition_match
        + 0.18 * md_score
        - 0.06 * phonon_modes
        - 0.90 * uncertainty
    )
    return XrdEvaluation(confidence=round(_clamp(confidence, 0.0, 1.0), 6))


class FixtureBackedCommitteeAdapter:
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name="committee_fixture_fallback_v2026_03_09",
            version="2026.03.09+analytic",
        )

    def evaluate_candidate(
        self,
        config: SystemConfig,
        candidate: CandidateRecord,
    ) -> CommitteeEvaluation:
        row = _snapshot_row(config, candidate)
        if row is not None:
            committee = row.get("committee_energy_ev_per_atom")
            if isinstance(committee, dict) and set(committee.keys()) == set(MODEL_COMMITTEE):
                return CommitteeEvaluation(
                    energies={model: round(float(committee[model]), 6) for model in MODEL_COMMITTEE}
                )
        return _committee_analytic(config, candidate)


class FixtureBackedPhononAdapter:
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name="phonon_fixture_fallback_v2026_03_09",
            version="2026.03.09+analytic",
        )

    def evaluate_candidate(
        self,
        config: SystemConfig,
        candidate: CandidateRecord,
    ) -> PhononEvaluation:
        row = _snapshot_row(config, candidate)
        if row is not None and isinstance(row.get("phonon_imaginary_modes"), int):
            return PhononEvaluation(imaginary_modes=int(row["phonon_imaginary_modes"]))
        return _phonon_analytic(candidate)


class FixtureBackedMdAdapter:
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name="md_fixture_fallback_v2026_03_09",
            version="2026.03.09+analytic",
        )

    def evaluate_candidate(self, config: SystemConfig, candidate: CandidateRecord) -> MdEvaluation:
        row = _snapshot_row(config, candidate)
        if row is not None and isinstance(row.get("md_stability_score"), int | float):
            return MdEvaluation(stability_score=round(float(row["md_stability_score"]), 6))
        return _md_analytic(candidate)


class FixtureBackedXrdAdapter:
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name="xrd_fixture_fallback_v2026_03_09",
            version="2026.03.09+analytic",
        )

    def evaluate_candidate(self, config: SystemConfig, candidate: CandidateRecord) -> XrdEvaluation:
        row = _snapshot_row(config, candidate)
        if row is not None and isinstance(row.get("xrd_confidence"), int | float):
            return XrdEvaluation(confidence=round(float(row["xrd_confidence"]), 6))
        return _xrd_analytic(config, candidate)
