from __future__ import annotations

import hashlib
import random
from pathlib import Path

from materials_discovery.common.io import write_jsonl
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    GenerateSummary,
    QPhiPair,
    SiteRecord,
    SystemConfig,
    validate_unique_candidate_ids,
)
from materials_discovery.generator.approximant_templates import get_template
from materials_discovery.generator.decorate_sites import assign_species


def _clamp(value: int, min_value: int, max_value: int) -> int:
    return min(max(value, min_value), max_value)


def _perturb_pair(base: QPhiPair, min_coeff: int, max_coeff: int, rng: random.Random) -> QPhiPair:
    a = _clamp(base[0] + rng.randint(-2, 2), min_coeff, max_coeff)
    b = _clamp(base[1] + rng.randint(-2, 2), min_coeff, max_coeff)
    return (a, b)


def _make_candidate(
    idx: int,
    config: SystemConfig,
    seed: int,
    rng: random.Random,
) -> CandidateRecord:
    template = get_template(config.template_family)
    species_assignments, composition = assign_species(
        len(template.sites), config.composition_bounds, rng
    )

    min_coeff = config.coeff_bounds.min
    max_coeff = config.coeff_bounds.max

    sites: list[SiteRecord] = []
    for i, template_site in enumerate(template.sites):
        qphi = (
            _perturb_pair(template_site.base_qphi[0], min_coeff, max_coeff, rng),
            _perturb_pair(template_site.base_qphi[1], min_coeff, max_coeff, rng),
            _perturb_pair(template_site.base_qphi[2], min_coeff, max_coeff, rng),
        )
        sites.append(
            SiteRecord(
                label=template_site.label,
                qphi=qphi,
                species=species_assignments[i],
                occ=1.0,
            )
        )

    cell_jitter = rng.uniform(-0.25, 0.25)
    a_value = round(template.cell_scale + cell_jitter, 6)

    digest = hashlib.sha256(f"{seed}:{idx}".encode()).hexdigest()

    return CandidateRecord(
        candidate_id=f"md_{idx:06d}",
        system=config.system_name,
        template_family=config.template_family,
        cell={"a": a_value, "b": a_value, "c": a_value, "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
        sites=sites,
        composition=composition,
        screen={"model": "MACE", "energy_per_atom_ev": -3.0},
        digital_validation=DigitalValidationRecord(status="pending"),
        provenance={
            "generator_version": "0.1.0",
            "seed": seed,
            "config_hash": f"sha256:{digest[:16]}",
        },
    )


def generate_candidates(
    config: SystemConfig,
    output_path: Path,
    count: int,
    seed: int | None,
) -> GenerateSummary:
    effective_seed = config.seed if seed is None else seed
    rng = random.Random(effective_seed)

    candidates: list[CandidateRecord] = []
    invalid_filtered = 0

    next_idx = 1
    while len(candidates) < count:
        try:
            candidate = _make_candidate(next_idx, config, effective_seed, rng)
            candidates.append(candidate)
            next_idx += 1
        except ValueError:
            invalid_filtered += 1
            next_idx += 1

    validate_unique_candidate_ids(candidates)
    write_jsonl([c.model_dump() for c in candidates], output_path)

    return GenerateSummary(
        requested_count=count,
        generated_count=len(candidates),
        invalid_filtered_count=invalid_filtered,
        output_path=str(output_path),
    )
