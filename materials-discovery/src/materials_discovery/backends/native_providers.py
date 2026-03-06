from __future__ import annotations

import importlib
from functools import lru_cache
from typing import Any

import numpy as np

from materials_discovery.backends.structure_realization import (
    build_ase_atoms,
    build_pymatgen_structure,
)
from materials_discovery.backends.types import (
    CommitteeEvaluation,
    MdEvaluation,
    PhononEvaluation,
    XrdEvaluation,
)
from materials_discovery.common.chemistry import composition_l1_distance
from materials_discovery.common.io import load_jsonl, workspace_root
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _require_module(module_name: str, dependency_name: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        raise RuntimeError(
            f"provider backend requires optional dependency '{dependency_name}'; install with "
            "`uv sync --extra dev --extra mlip`"
        ) from exc


def _as_float(value: Any) -> float:
    if hasattr(value, "item"):
        return float(value.item())
    return float(value)


@lru_cache(maxsize=4)
def _mace_factory(device: str | None) -> Any:
    module = _require_module("mace.calculators", "mace-torch")
    mace_mp = module.mace_mp
    attempts: list[dict[str, object | None]] = [
        {"model": "medium", "dispersion": False, "default_dtype": "float64", "device": device},
        {"model": "medium", "dispersion": False, "device": device},
        {"model": "medium", "device": device},
        {"device": device},
        {},
    ]
    for kwargs in attempts:
        filtered = {key: value for key, value in kwargs.items() if value is not None}
        try:
            return mace_mp(**filtered)
        except TypeError:
            continue
    raise RuntimeError(
        "unable to initialize MACE ASE calculator from available constructor variants"
    )


def _mace_energy_per_atom(candidate: CandidateRecord, device: str | None) -> float:
    atoms = build_ase_atoms(candidate)
    atoms.calc = _mace_factory(device)
    return round(float(atoms.get_potential_energy() / len(atoms)), 6)


def _mace_hessian(candidate: CandidateRecord, device: str | None) -> Any:
    atoms = build_ase_atoms(candidate)
    calc = _mace_factory(device)
    atoms.calc = calc
    hessian = np.asarray(calc.get_hessian(atoms=atoms), dtype=float)
    if hessian.ndim == 4:
        atom_count = len(atoms)
        return hessian.reshape(3 * atom_count, 3 * atom_count)
    if hessian.ndim == 2:
        return hessian
    raise ValueError(f"unsupported MACE hessian shape: {hessian.shape}")


@lru_cache(maxsize=4)
def _chgnet_model() -> Any:
    model_module = _require_module("chgnet.model.model", "chgnet")
    return model_module.CHGNet.load()


def _chgnet_energy_per_atom(candidate: CandidateRecord) -> float:
    structure = build_pymatgen_structure(candidate)
    prediction = _chgnet_model().predict_structure(structure, task="e")
    if not isinstance(prediction, dict):
        raise ValueError("CHGNet prediction must be a mapping")
    for key in ("e", "energy", "energy_per_atom"):
        if key in prediction:
            return round(_as_float(prediction[key]), 6)
    raise ValueError("CHGNet prediction did not expose an energy-per-atom field")


@lru_cache(maxsize=4)
def _mattersim_calculator_factory(device: str | None) -> Any:
    module = _require_module("mattersim.forcefield", "mattersim")
    calculator_cls = module.MatterSimCalculator
    if device is None:
        return calculator_cls()
    return calculator_cls(device=device)


def _mattersim_energy_per_atom(candidate: CandidateRecord, device: str | None) -> float:
    atoms = build_ase_atoms(candidate)
    atoms.calc = _mattersim_calculator_factory(device)
    return round(float(atoms.get_potential_energy() / len(atoms)), 6)


def _committee_native(config: SystemConfig, candidate: CandidateRecord) -> CommitteeEvaluation:
    device = config.backend.committee_device
    energies: dict[str, float] = {}
    failures: list[str] = []

    try:
        energies["MACE"] = _mace_energy_per_atom(candidate, device)
    except Exception as exc:  # pragma: no cover - exercised only when deps are present
        failures.append(f"MACE={exc}")
    try:
        energies["CHGNet"] = _chgnet_energy_per_atom(candidate)
    except Exception as exc:  # pragma: no cover - exercised only when deps are present
        failures.append(f"CHGNet={exc}")
    try:
        energies["MatterSim"] = _mattersim_energy_per_atom(candidate, device)
    except Exception as exc:  # pragma: no cover - exercised only when deps are present
        failures.append(f"MatterSim={exc}")

    if len(energies) < 2:
        detail = "; ".join(failures) if failures else "no provider calculators succeeded"
        raise RuntimeError(
            "ase_committee_v1 requires at least two installed provider calculators "
            f"(MACE, CHGNet, MatterSim). Details: {detail}"
        )
    return CommitteeEvaluation(energies=energies)


def _phonon_native(config: SystemConfig, candidate: CandidateRecord) -> PhononEvaluation:
    hessian = _mace_hessian(candidate, config.backend.committee_device)
    eigenvalues = np.linalg.eigvalsh(hessian)
    imaginary_modes = int(np.count_nonzero(eigenvalues < -1e-8))
    return PhononEvaluation(imaginary_modes=imaginary_modes)


def _best_md_calculator(device: str | None) -> tuple[Any, str]:
    try:
        return _mace_factory(device), "MACE"
    except Exception:
        pass

    try:
        dynamics_module = _require_module("chgnet.model.dynamics", "chgnet")
        calculator_cls = dynamics_module.CHGNetCalculator
        return calculator_cls(use_device=device), "CHGNet"
    except Exception:
        pass

    try:
        return _mattersim_calculator_factory(device), "MatterSim"
    except Exception as exc:
        raise RuntimeError(
            "ase_langevin_v1 requires at least one installed ASE-compatible calculator "
            "(MACE, CHGNet, or MatterSim)"
        ) from exc


def _md_native(config: SystemConfig, candidate: CandidateRecord) -> MdEvaluation:
    units = _require_module("ase.units", "ase")
    md_module = _require_module("ase.md.langevin", "ase")
    velocity_module = _require_module("ase.md.velocitydistribution", "ase")

    Langevin = md_module.Langevin
    MaxwellBoltzmannDistribution = velocity_module.MaxwellBoltzmannDistribution

    atoms = build_ase_atoms(candidate)
    calculator, _ = _best_md_calculator(config.backend.committee_device)
    atoms.calc = calculator

    initial_positions = np.asarray(atoms.get_positions(), dtype=float)
    initial_energy = float(atoms.get_potential_energy() / len(atoms))
    MaxwellBoltzmannDistribution(atoms, config.backend.md_temperature_k * units.kB)

    dynamics = Langevin(
        atoms,
        config.backend.md_timestep_fs * units.fs,
        config.backend.md_temperature_k * units.kB,
        0.001,
    )
    dynamics.run(config.backend.md_steps)

    final_positions = np.asarray(atoms.get_positions(), dtype=float)
    final_energy = float(atoms.get_potential_energy() / len(atoms))
    rms_displacement = float(
        np.sqrt(np.mean(np.sum((final_positions - initial_positions) ** 2, axis=1)))
    )
    cell_scale = max(
        float(candidate.cell["a"]),
        float(candidate.cell["b"]),
        float(candidate.cell["c"]),
    )
    normalized_displacement = rms_displacement / max(1e-6, cell_scale)
    energy_drift = abs(final_energy - initial_energy)
    stability_score = (
        1.0
        - 0.65 * min(1.0, energy_drift / 0.25)
        - 0.35 * min(1.0, normalized_displacement / 0.12)
    )
    return MdEvaluation(stability_score=round(_clamp(stability_score, 0.0, 1.0), 6))


@lru_cache(maxsize=16)
def _reference_compositions(path_str: str) -> list[dict[str, float]]:
    rows = load_jsonl(workspace_root() / path_str)
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


def _xrd_reference_match(config: SystemConfig, candidate: CandidateRecord) -> float:
    system_slug = config.system_name.lower().replace("-", "_")
    relative_path = f"data/processed/{system_slug}_reference_phases.jsonl"
    path = workspace_root() / relative_path
    if not path.exists():
        raise FileNotFoundError(
            "native XRD validation requires ingested reference phases; "
            f"run 'mdisc ingest' first: {path}"
        )
    references = _reference_compositions(relative_path)
    if not references:
        raise ValueError(f"native XRD validation found no usable reference compositions in {path}")
    nearest_distance = min(
        composition_l1_distance(candidate.composition, reference) for reference in references
    )
    return 1.0 - min(1.0, nearest_distance / 0.8)


def _xrd_native(config: SystemConfig, candidate: CandidateRecord) -> XrdEvaluation:
    diffraction_module = _require_module(
        "pymatgen.analysis.diffraction.xrd",
        "pymatgen",
    )
    calculator = diffraction_module.XRDCalculator(wavelength=config.backend.xrd_wavelength)
    structure = build_pymatgen_structure(candidate)
    pattern = calculator.get_pattern(structure, two_theta_range=(10, 90))
    x_values = [float(value) for value in getattr(pattern, "x", [])]
    intensities = [float(value) for value in getattr(pattern, "y", [])]

    peak_count = len(x_values)
    peak_richness = min(1.0, peak_count / 24.0)
    intensity_total = sum(intensities)
    dominant_peak = max(intensities) / intensity_total if intensity_total > 0.0 else 1.0
    pattern_balance = 1.0 - dominant_peak
    pattern_span = (max(x_values) - min(x_values)) if peak_count > 1 else 0.0
    pattern_coverage = min(1.0, pattern_span / 70.0)

    reference_match = _xrd_reference_match(config, candidate)
    uncertainty = candidate.digital_validation.uncertainty_ev_per_atom or 0.05
    md_score = candidate.digital_validation.md_stability_score or 0.0
    phonon_modes = candidate.digital_validation.phonon_imaginary_modes or 0
    confidence = (
        0.16
        + 0.24 * peak_richness
        + 0.18 * pattern_balance
        + 0.12 * pattern_coverage
        + 0.18 * reference_match
        + 0.18 * md_score
        - 0.05 * phonon_modes
        - 0.90 * uncertainty
    )
    return XrdEvaluation(confidence=round(_clamp(confidence, 0.0, 1.0), 6))


def evaluate_committee_provider(
    config: SystemConfig,
    candidate: CandidateRecord,
) -> CommitteeEvaluation:
    provider = config.backend.committee_provider or "pinned"
    if provider == "ase_committee_v1":
        return _committee_native(config, candidate)
    raise ValueError(f"unsupported committee provider: {provider}")


def evaluate_phonon_provider(
    config: SystemConfig,
    candidate: CandidateRecord,
) -> PhononEvaluation:
    provider = config.backend.phonon_provider or "pinned"
    if provider == "mace_hessian_v1":
        return _phonon_native(config, candidate)
    raise ValueError(f"unsupported phonon provider: {provider}")


def evaluate_md_provider(config: SystemConfig, candidate: CandidateRecord) -> MdEvaluation:
    provider = config.backend.md_provider or "pinned"
    if provider == "ase_langevin_v1":
        return _md_native(config, candidate)
    raise ValueError(f"unsupported md provider: {provider}")


def evaluate_xrd_provider(config: SystemConfig, candidate: CandidateRecord) -> XrdEvaluation:
    provider = config.backend.xrd_provider or "pinned"
    if provider == "pymatgen_xrd_v1":
        return _xrd_native(config, candidate)
    raise ValueError(f"unsupported xrd provider: {provider}")
