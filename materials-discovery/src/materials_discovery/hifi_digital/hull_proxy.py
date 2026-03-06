from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from statistics import mean

import numpy as np

from materials_discovery.common.chemistry import composition_l1_distance, describe_composition
from materials_discovery.common.io import load_jsonl, workspace_root
from materials_discovery.common.schema import CandidateRecord, SystemConfig


@dataclass(frozen=True)
class ReferencePhasePoint:
    phase_name: str
    composition: dict[str, float]
    energy_ev_per_atom: float


@dataclass(frozen=True)
class HullBaseline:
    baseline_energy_ev_per_atom: float
    reference_distance: float
    reference_phases: tuple[str, ...]


def _committee_mean_energy(candidate: CandidateRecord) -> float:
    committee_energies = candidate.digital_validation.committee_energy_ev_per_atom
    if not committee_energies:
        raise ValueError("committee energies missing for proxy-hull calculation")
    return mean(float(v) for v in committee_energies.values())


def _composition_imbalance(composition: dict[str, float]) -> float:
    target = 1.0 / len(composition)
    return sum(abs(frac - target) for frac in composition.values()) / 2.0


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _phase_stability_bias(phase_name: str) -> float:
    token = phase_name.strip().lower()
    if "i-phase" in token or token.startswith("i"):
        return -0.030
    if "approximant" in token:
        return -0.022
    if "beta" in token:
        return -0.014
    if "lambda" in token:
        return -0.010
    return -0.006


def _reference_phase_energy_ev_per_atom(
    phase_name: str,
    composition: dict[str, float],
) -> float:
    descriptor = describe_composition(composition, strict_pairs=True)
    vec_penalty = abs(descriptor.vec - 6.0)
    ordering_penalty = descriptor.dominant_fraction - (1.0 / max(1, len(composition)))
    energy = (
        -2.88
        + 0.56 * descriptor.pair_mixing_enthalpy_ev_per_atom
        + 0.24 * descriptor.radius_mismatch
        + 0.10 * descriptor.electronegativity_spread
        + 0.013 * vec_penalty
        + 0.016 * ordering_penalty
        + _phase_stability_bias(phase_name)
    )
    return round(energy, 6)


def _load_reference_phase_points(config: SystemConfig) -> list[ReferencePhasePoint]:
    processed_path = (
        workspace_root()
        / "data"
        / "processed"
        / f"{_system_slug(config.system_name)}_reference_phases.jsonl"
    )
    if not processed_path.exists():
        raise FileNotFoundError(
            "real-mode proxy hull requires ingested reference phases; "
            f"run 'mdisc ingest' first: {processed_path}"
        )

    points: list[ReferencePhasePoint] = []
    for row in load_jsonl(processed_path):
        phase_name = row.get("phase_name")
        composition = row.get("composition")
        if not isinstance(phase_name, str) or not isinstance(composition, dict):
            continue

        parsed_composition: dict[str, float] = {}
        for symbol, value in composition.items():
            if not isinstance(symbol, str) or not isinstance(value, int | float):
                parsed_composition = {}
                break
            parsed_composition[symbol] = float(value)
        if not parsed_composition:
            continue

        points.append(
            ReferencePhasePoint(
                phase_name=phase_name,
                composition=parsed_composition,
                energy_ev_per_atom=_reference_phase_energy_ev_per_atom(
                    phase_name,
                    parsed_composition,
                ),
            )
        )

    if not points:
        raise ValueError(
            "real-mode proxy hull found no usable reference phases for "
            f"{config.system_name} in {processed_path}"
        )
    return points


def _composition_vector(
    composition: dict[str, float],
    species: list[str],
) -> np.ndarray:
    return np.array([float(composition.get(symbol, 0.0)) for symbol in species], dtype=float)


def _choose_reference_mixture(
    target_composition: dict[str, float],
    species: list[str],
    references: list[ReferencePhasePoint],
) -> HullBaseline | None:
    target_vector = _composition_vector(target_composition, species)
    reduced_target = np.concatenate([target_vector[:-1], np.array([1.0], dtype=float)])

    best_baseline: HullBaseline | None = None
    max_size = min(len(references), len(species))

    for size in range(1, max_size + 1):
        for indices in combinations(range(len(references)), size):
            columns = []
            for index in indices:
                reference_vector = _composition_vector(references[index].composition, species)
                columns.append(np.concatenate([reference_vector[:-1], np.array([1.0])]))

            matrix = np.column_stack(columns)
            weights, _, _, _ = np.linalg.lstsq(matrix, reduced_target, rcond=None)
            if any(float(weight) < -1e-8 for weight in weights):
                continue

            weights = np.maximum(weights, 0.0)
            weight_sum = float(weights.sum())
            if weight_sum <= 1e-8:
                continue
            weights = weights / weight_sum

            mixture_vector = np.zeros(len(species), dtype=float)
            for local_index, reference_index in enumerate(indices):
                mixture_vector += weights[local_index] * _composition_vector(
                    references[reference_index].composition,
                    species,
                )

            reconstructed = np.concatenate([mixture_vector[:-1], np.array([weights.sum()])])
            residual = float(np.max(np.abs(reconstructed - reduced_target)))
            if residual > 1e-6:
                continue

            baseline_energy = 0.0
            for local_index, reference_index in enumerate(indices):
                baseline_energy += (
                    float(weights[local_index]) * references[reference_index].energy_ev_per_atom
                )

            candidate_distance = composition_l1_distance(
                target_composition,
                {symbol: float(mixture_vector[idx]) for idx, symbol in enumerate(species)},
            )
            baseline = HullBaseline(
                baseline_energy_ev_per_atom=round(baseline_energy, 6),
                reference_distance=round(candidate_distance, 6),
                reference_phases=tuple(references[index].phase_name for index in indices),
            )
            if best_baseline is None or (
                baseline.baseline_energy_ev_per_atom < best_baseline.baseline_energy_ev_per_atom
            ):
                best_baseline = baseline

    return best_baseline


def _nearest_reference_baseline(
    target_composition: dict[str, float],
    references: list[ReferencePhasePoint],
) -> HullBaseline:
    nearest = min(
        references,
        key=lambda reference: (
            composition_l1_distance(target_composition, reference.composition),
            reference.energy_ev_per_atom,
            reference.phase_name,
        ),
    )
    return HullBaseline(
        baseline_energy_ev_per_atom=nearest.energy_ev_per_atom,
        reference_distance=round(
            composition_l1_distance(target_composition, nearest.composition),
            6,
        ),
        reference_phases=(nearest.phase_name,),
    )


def _compute_proxy_hull_mock(candidates: list[CandidateRecord]) -> list[CandidateRecord]:
    """Legacy batch-relative hull proxy for mock mode."""
    if not candidates:
        return []

    mean_energies = {c.candidate_id: _committee_mean_energy(c) for c in candidates}
    best_energy = min(mean_energies.values())

    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = candidate.model_copy(deep=True)
        energy_term = mean_energies[copied.candidate_id] - best_energy
        balance_term = 0.04 * _composition_imbalance(copied.composition)
        delta_hull = round(max(0.0, energy_term + balance_term), 6)

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "hull_scored"
        validation.delta_e_proxy_hull_ev_per_atom = delta_hull
        copied.digital_validation = validation
        scored.append(copied)
    return scored


def _compute_proxy_hull_real(
    config: SystemConfig,
    candidates: list[CandidateRecord],
) -> list[CandidateRecord]:
    """Reference-aware hull proxy for real mode."""
    if not candidates:
        return []

    references = _load_reference_phase_points(config)
    species = list(config.species)

    scored: list[CandidateRecord] = []
    for candidate in candidates:
        copied = candidate.model_copy(deep=True)
        candidate_energy = _committee_mean_energy(copied)

        baseline = _choose_reference_mixture(copied.composition, species, references)
        if baseline is None:
            baseline = _nearest_reference_baseline(copied.composition, references)

        extrapolation_penalty = 0.05 * baseline.reference_distance
        delta_hull = round(
            max(0.0, candidate_energy - baseline.baseline_energy_ev_per_atom)
            + extrapolation_penalty,
            6,
        )

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "hull_scored"
        validation.delta_e_proxy_hull_ev_per_atom = delta_hull
        validation.proxy_hull_baseline_ev_per_atom = baseline.baseline_energy_ev_per_atom
        validation.proxy_hull_reference_distance = baseline.reference_distance
        validation.proxy_hull_reference_phases = list(baseline.reference_phases)
        copied.digital_validation = validation
        scored.append(copied)

    return scored


def compute_proxy_hull(
    candidates: list[CandidateRecord],
    config: SystemConfig | None = None,
) -> list[CandidateRecord]:
    """Compute a proxy hull metric against either the batch or a reference phase set."""
    if config is not None and config.backend.mode == "real":
        return _compute_proxy_hull_real(config, candidates)
    return _compute_proxy_hull_mock(candidates)
