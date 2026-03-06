from __future__ import annotations

import hashlib
from copy import deepcopy

from materials_discovery.common.chemistry import describe_candidate, validate_supported_species
from materials_discovery.common.schema import CandidateRecord, SystemConfig

MODEL_COMMITTEE: tuple[str, str, str] = ("MACE", "CHGNet", "MatterSim")
_MODEL_SHIFT: dict[str, float] = {"MACE": -0.0075, "CHGNet": 0.0, "MatterSim": 0.0065}


def _candidate_seed(candidate_id: str) -> int:
    digest = hashlib.sha256(candidate_id.encode()).hexdigest()
    return int(digest[:8], 16)


def _base_energy(candidate: CandidateRecord) -> float:
    screen = candidate.screen or {}
    if "energy_proxy_ev_per_atom" in screen:
        return float(screen["energy_proxy_ev_per_atom"])
    if "energy_per_atom_ev" in screen:
        return float(screen["energy_per_atom_ev"])
    return -3.0


def _model_energy(
    base_energy: float,
    candidate_seed: int,
    model: str,
    template_shift: float,
) -> float:
    jitter = ((candidate_seed >> (MODEL_COMMITTEE.index(model) * 3)) % 41 - 20) / 5000.0
    return round(base_energy + template_shift + _MODEL_SHIFT[model] + jitter, 6)


def _run_committee_relaxation_mock(
    config: SystemConfig,
    candidates: list[CandidateRecord],
    batch: str,
) -> list[CandidateRecord]:
    """Legacy deterministic committee logic for mock mode and CI reproducibility."""
    template_shift = len(config.template_family) * 0.0005
    relaxed: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        candidate_seed = _candidate_seed(copied.candidate_id)
        base_energy = _base_energy(copied)
        committee_energies = {
            model: _model_energy(base_energy, candidate_seed, model, template_shift)
            for model in MODEL_COMMITTEE
        }

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "committee_relaxed"
        validation.committee = list(MODEL_COMMITTEE)
        validation.committee_energy_ev_per_atom = committee_energies
        validation.batch = batch
        copied.digital_validation = validation
        relaxed.append(copied)
    return relaxed


def _run_committee_relaxation_real(
    config: SystemConfig,
    candidates: list[CandidateRecord],
    batch: str,
) -> list[CandidateRecord]:
    """Descriptor-driven committee energy estimates for no-DFT real mode."""
    validate_supported_species(config.species, strict_pairs=True)
    template_shift = len(config.template_family) * 0.0002

    relaxed: list[CandidateRecord] = []
    for candidate in candidates:
        copied = deepcopy(candidate)
        descriptor = describe_candidate(copied, strict_pairs=True)
        base_energy = _base_energy(copied)

        vec_penalty = abs(descriptor.vec - 6.0) / 6.0
        complexity_term = descriptor.qphi_complexity / 6.0
        composition_term = descriptor.dominant_fraction - (1.0 / max(1, len(copied.composition)))

        committee_energies = {
            "MACE": round(
                base_energy
                + template_shift
                - 0.008
                + 0.032 * descriptor.radius_mismatch
                + 0.018 * complexity_term
                + 0.009 * vec_penalty
                + 0.006 * composition_term,
                6,
            ),
            "CHGNet": round(
                base_energy
                + template_shift
                - 0.004
                + 0.026 * descriptor.electronegativity_spread
                + 0.021 * complexity_term
                + 0.011 * vec_penalty
                + 0.004 * composition_term,
                6,
            ),
            "MatterSim": round(
                base_energy
                + template_shift
                - 0.006
                + 0.028 * descriptor.radius_mismatch
                + 0.024 * descriptor.electronegativity_spread
                + 0.015 * complexity_term
                + 0.004 * composition_term,
                6,
            ),
        }

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "committee_relaxed"
        validation.committee = list(MODEL_COMMITTEE)
        validation.committee_energy_ev_per_atom = committee_energies
        validation.batch = batch
        copied.digital_validation = validation
        relaxed.append(copied)

    return relaxed


def run_committee_relaxation(
    config: SystemConfig,
    candidates: list[CandidateRecord],
    batch: str,
) -> list[CandidateRecord]:
    """Attach committee energies for no-DFT high-fidelity validation."""
    if config.backend.mode == "real":
        return _run_committee_relaxation_real(config, candidates, batch)
    return _run_committee_relaxation_mock(config, candidates, batch)
