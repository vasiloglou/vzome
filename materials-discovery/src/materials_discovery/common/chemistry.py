from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from itertools import combinations
from math import sqrt
from statistics import mean

from materials_discovery.common.schema import CandidateRecord


@dataclass(frozen=True)
class ElementProperties:
    atomic_number: int
    covalent_radius_pm: float
    pauling_electronegativity: float
    valence_electrons: float


@dataclass(frozen=True)
class CompositionDescriptors:
    vec: float
    radius_mismatch: float
    electronegativity_spread: float
    pair_mixing_enthalpy_ev_per_atom: float
    dominant_fraction: float
    avg_atomic_number: float


@dataclass(frozen=True)
class CandidateDescriptors(CompositionDescriptors):
    qphi_complexity: float


# Coarse no-DFT priors for alloys used in the baseline systems.
# Values are approximate pairwise mixing-enthalpy proxies (eV/atom).
PAIR_MIXING_ENTHALPY_EV: dict[tuple[str, str], float] = {
    ("Al", "Cu"): -0.12,
    ("Al", "Fe"): -0.18,
    ("Cu", "Fe"): 0.04,
    ("Al", "Pd"): -0.35,
    ("Al", "Mn"): -0.20,
    ("Mn", "Pd"): -0.15,
    ("Sc", "Zn"): -0.16,
    ("Ni", "Ti"): -0.35,
    ("Ni", "Zr"): -0.49,
    ("Ti", "Zr"): 0.00,
}


ELEMENT_PROPERTIES: dict[str, ElementProperties] = {
    "Al": ElementProperties(
        atomic_number=13,
        covalent_radius_pm=121.0,
        pauling_electronegativity=1.61,
        valence_electrons=3.0,
    ),
    "Cu": ElementProperties(
        atomic_number=29,
        covalent_radius_pm=132.0,
        pauling_electronegativity=1.90,
        valence_electrons=11.0,
    ),
    "Fe": ElementProperties(
        atomic_number=26,
        covalent_radius_pm=124.0,
        pauling_electronegativity=1.83,
        valence_electrons=8.0,
    ),
    "Pd": ElementProperties(
        atomic_number=46,
        covalent_radius_pm=139.0,
        pauling_electronegativity=2.20,
        valence_electrons=10.0,
    ),
    "Mn": ElementProperties(
        atomic_number=25,
        covalent_radius_pm=127.0,
        pauling_electronegativity=1.55,
        valence_electrons=7.0,
    ),
    "Sc": ElementProperties(
        atomic_number=21,
        covalent_radius_pm=148.0,
        pauling_electronegativity=1.36,
        valence_electrons=3.0,
    ),
    "Zn": ElementProperties(
        atomic_number=30,
        covalent_radius_pm=122.0,
        pauling_electronegativity=1.65,
        valence_electrons=12.0,
    ),
    "Ti": ElementProperties(
        atomic_number=22,
        covalent_radius_pm=160.0,
        pauling_electronegativity=1.54,
        valence_electrons=4.0,
    ),
    "Zr": ElementProperties(
        atomic_number=40,
        covalent_radius_pm=175.0,
        pauling_electronegativity=1.33,
        valence_electrons=4.0,
    ),
    "Ni": ElementProperties(
        atomic_number=28,
        covalent_radius_pm=124.0,
        pauling_electronegativity=1.91,
        valence_electrons=10.0,
    ),
}


def composition_l1_distance(a: dict[str, float], b: dict[str, float]) -> float:
    species = sorted(set(a) | set(b))
    return sum(abs(float(a.get(s, 0.0)) - float(b.get(s, 0.0))) for s in species)


def validate_supported_species(species: list[str], *, strict_pairs: bool) -> None:
    missing_elements = [symbol for symbol in species if symbol not in ELEMENT_PROPERTIES]
    if missing_elements:
        raise ValueError(
            "missing element property priors for species: "
            + ", ".join(sorted(missing_elements))
        )

    if not strict_pairs:
        return

    missing_pairs: list[str] = []
    for first, second in combinations(sorted(species), 2):
        pair = tuple(sorted((first, second)))
        if pair not in PAIR_MIXING_ENTHALPY_EV:
            missing_pairs.append(f"{pair[0]}-{pair[1]}")
    if missing_pairs:
        raise ValueError(
            "missing pair-mixing priors for species pairs: "
            + ", ".join(sorted(missing_pairs))
        )


def qphi_complexity(candidate: CandidateRecord) -> float:
    coeffs: list[int] = []
    for site in candidate.sites:
        for pair in site.qphi:
            coeffs.extend(pair)
    if not coeffs:
        return 0.0
    return mean(abs(value) for value in coeffs)


def _weighted_mean(
    composition: dict[str, float],
    selector: Callable[[ElementProperties], float],
) -> float:
    return sum(
        float(frac) * selector(ELEMENT_PROPERTIES[symbol]) for symbol, frac in composition.items()
    )


def _pair_mixing_enthalpy(composition: dict[str, float], *, strict_pairs: bool) -> float:
    total = 0.0
    species = sorted(composition)
    for first, second in combinations(species, 2):
        pair: tuple[str, str]
        if first <= second:
            pair = (first, second)
        else:
            pair = (second, first)
        if pair not in PAIR_MIXING_ENTHALPY_EV:
            if strict_pairs:
                raise ValueError(
                    "missing pair-mixing prior for pair "
                    f"{pair[0]}-{pair[1]} in composition {sorted(composition)}"
                )
            enthalpy = 0.0
        else:
            enthalpy = PAIR_MIXING_ENTHALPY_EV[pair]
        total += 4.0 * float(composition[first]) * float(composition[second]) * enthalpy
    return total


def describe_composition(
    composition: dict[str, float],
    *,
    strict_pairs: bool,
) -> CompositionDescriptors:
    validate_supported_species(list(composition), strict_pairs=strict_pairs)

    radius_mean = _weighted_mean(composition, lambda props: props.covalent_radius_pm)
    en_mean = _weighted_mean(composition, lambda props: props.pauling_electronegativity)
    vec = _weighted_mean(composition, lambda props: props.valence_electrons)
    avg_atomic_number = _weighted_mean(composition, lambda props: float(props.atomic_number))

    if radius_mean <= 0.0:
        raise ValueError("invalid radius mean for composition")

    radius_mismatch_sq = sum(
        float(frac)
        * (1.0 - ELEMENT_PROPERTIES[symbol].covalent_radius_pm / radius_mean) ** 2
        for symbol, frac in composition.items()
    )
    radius_mismatch = sqrt(max(0.0, radius_mismatch_sq))

    en_spread_sq = sum(
        float(frac)
        * (ELEMENT_PROPERTIES[symbol].pauling_electronegativity - en_mean) ** 2
        for symbol, frac in composition.items()
    )
    electronegativity_spread = sqrt(max(0.0, en_spread_sq))

    pair_mixing = _pair_mixing_enthalpy(composition, strict_pairs=strict_pairs)
    dominant_fraction = max(composition.values())

    return CompositionDescriptors(
        vec=round(vec, 6),
        radius_mismatch=round(radius_mismatch, 6),
        electronegativity_spread=round(electronegativity_spread, 6),
        pair_mixing_enthalpy_ev_per_atom=round(pair_mixing, 6),
        dominant_fraction=round(float(dominant_fraction), 6),
        avg_atomic_number=round(avg_atomic_number, 6),
    )


def describe_candidate(
    candidate: CandidateRecord,
    *,
    strict_pairs: bool,
) -> CandidateDescriptors:
    composition = describe_composition(candidate.composition, strict_pairs=strict_pairs)
    return CandidateDescriptors(
        vec=composition.vec,
        radius_mismatch=composition.radius_mismatch,
        electronegativity_spread=composition.electronegativity_spread,
        pair_mixing_enthalpy_ev_per_atom=composition.pair_mixing_enthalpy_ev_per_atom,
        dominant_fraction=composition.dominant_fraction,
        avg_atomic_number=composition.avg_atomic_number,
        qphi_complexity=round(qphi_complexity(candidate), 6),
    )
