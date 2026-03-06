from __future__ import annotations

import hashlib
import random
from pathlib import Path

from materials_discovery.common.io import write_jsonl
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    GenerateSummary,
    SiteRecord,
    SystemConfig,
    validate_unique_candidate_ids,
)
from materials_discovery.generator.approximant_templates import get_template
from materials_discovery.generator.decorate_sites import assign_species
from materials_discovery.generator.site_positions import site_positions_from_qphi
from materials_discovery.generator.zphi_geometry import (
    cell_scale_multiplier,
    construct_site_qphi,
)


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

    qphi_coords: list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = []
    for i, template_site in enumerate(template.sites):
        qphi = construct_site_qphi(
            template_site.base_qphi,
            template_family=config.template_family,
            candidate_index=idx,
            site_index=i,
            seed=seed,
            min_coeff=min_coeff,
            max_coeff=max_coeff,
        )
        qphi_coords.append(qphi)

    a_value = round(template.cell_scale * cell_scale_multiplier(seed, idx), 6)
    cell = {"a": a_value, "b": a_value, "c": a_value, "alpha": 90.0, "beta": 90.0, "gamma": 90.0}

    fractional_positions, cartesian_positions = site_positions_from_qphi(qphi_coords, cell)

    sites: list[SiteRecord] = []
    for i, template_site in enumerate(template.sites):
        sites.append(
            SiteRecord(
                label=template_site.label,
                qphi=qphi_coords[i],
                species=species_assignments[i],
                occ=1.0,
                fractional_position=fractional_positions[i],
                cartesian_position=cartesian_positions[i],
            )
        )

    digest = hashlib.sha256(f"{seed}:{idx}".encode()).hexdigest()

    return CandidateRecord(
        candidate_id=f"md_{idx:06d}",
        system=config.system_name,
        template_family=config.template_family,
        cell=cell,
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
