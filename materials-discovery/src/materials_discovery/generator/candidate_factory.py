from __future__ import annotations

import hashlib
import random
from pathlib import Path

from materials_discovery.common.coordinates import (
    cartesian_positions_from_fractional,
    cell_matrix_from_cell,
)
from materials_discovery.common.io import write_jsonl
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    GenerateSummary,
    SiteRecord,
    SystemConfig,
    validate_unique_candidate_ids,
)
from materials_discovery.generator.approximant_templates import resolve_template, template_from_path
from materials_discovery.generator.decorate_sites import assign_species
from materials_discovery.generator.site_positions import site_positions_from_template
from materials_discovery.generator.zomic_bridge import prototype_library_for_config
from materials_discovery.generator.zphi_geometry import (
    cell_scale_multiplier,
    construct_site_qphi,
)


def _build_provenance(
    *,
    idx: int,
    config: SystemConfig,
    seed: int,
    template_override_path: Path | None,
    template_reference: str,
    template_reference_url: str | None,
    template_source_kind: str,
    template_space_group: str | None,
    template_prototype_key: str,
    extra_provenance: dict[str, object] | None = None,
) -> dict[str, object]:
    digest = hashlib.sha256(f"{seed}:{idx}".encode()).hexdigest()
    provenance: dict[str, object] = {
        "generator_version": "0.1.0",
        "seed": seed,
        "config_hash": f"sha256:{digest[:16]}",
        "prototype_key": template_prototype_key,
        "prototype_reference": template_reference,
        "prototype_reference_url": template_reference_url,
        "prototype_source_kind": template_source_kind,
        "prototype_space_group": template_space_group,
    }
    if template_override_path is not None:
        provenance["prototype_library_path"] = str(template_override_path)
    if config.zomic_design is not None:
        provenance["zomic_design"] = config.zomic_design
    if extra_provenance:
        provenance.update(extra_provenance)
    return provenance


def _candidate_from_template(
    *,
    idx: int,
    config: SystemConfig,
    seed: int,
    rng: random.Random,
    template_override_path: Path | None,
    use_compiled_geometry: bool,
    extra_provenance: dict[str, object] | None = None,
) -> CandidateRecord:
    template = (
        template_from_path(template_override_path)
        if template_override_path is not None
        else resolve_template(config.system_name, config.template_family)
    )
    species_assignments, composition = assign_species(
        len(template.sites),
        config.composition_bounds,
        rng,
        site_preferences=[site.preferred_species for site in template.sites],
    )

    if use_compiled_geometry:
        qphi_coords = [template_site.base_qphi for template_site in template.sites]
        cell = dict(template.base_cell)
        fractional_positions = [
            template_site.base_fractional_position for template_site in template.sites
        ]
        cell_matrix = cell_matrix_from_cell(cell)
        cartesian_positions = cartesian_positions_from_fractional(
            fractional_positions,
            cell_matrix,
        )
    else:
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

        multiplier = cell_scale_multiplier(
            seed,
            idx,
            template_source_kind=template.source_kind,
        )
        cell = {
            axis: round(value * multiplier, 6) if axis in {"a", "b", "c"} else value
            for axis, value in template.base_cell.items()
        }
        fractional_positions, cartesian_positions = site_positions_from_template(
            template,
            qphi_coords,
            cell,
        )

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

    provenance = _build_provenance(
        idx=idx,
        config=config,
        seed=seed,
        template_override_path=template_override_path,
        template_reference=template.reference,
        template_reference_url=template.reference_url,
        template_source_kind=template.source_kind,
        template_space_group=template.space_group,
        template_prototype_key=template.prototype_key,
        extra_provenance=extra_provenance,
    )

    return CandidateRecord(
        candidate_id=f"md_{idx:06d}",
        system=config.system_name,
        template_family=config.template_family,
        cell=cell,
        sites=sites,
        composition=composition,
        screen={"model": "MACE", "energy_per_atom_ev": -3.0},
        digital_validation=DigitalValidationRecord(status="pending"),
        provenance=provenance,
    )


def _make_candidate(
    idx: int,
    config: SystemConfig,
    seed: int,
    rng: random.Random,
    template_override_path: Path | None,
) -> CandidateRecord:
    return _candidate_from_template(
        idx=idx,
        config=config,
        seed=seed,
        rng=rng,
        template_override_path=template_override_path,
        use_compiled_geometry=False,
    )

def build_candidate_from_prototype_library(
    config: SystemConfig,
    *,
    seed: int,
    candidate_index: int,
    template_override_path: Path,
    extra_provenance: dict[str, object] | None = None,
) -> CandidateRecord:
    rng = random.Random(f"{seed}:{candidate_index}:{template_override_path.resolve()}")
    return _candidate_from_template(
        idx=candidate_index,
        config=config,
        seed=seed,
        rng=rng,
        template_override_path=template_override_path,
        use_compiled_geometry=True,
        extra_provenance=extra_provenance,
    )


def generate_candidates(
    config: SystemConfig,
    output_path: Path,
    count: int,
    seed: int | None,
    config_path: Path | None = None,
) -> GenerateSummary:
    effective_seed = config.seed if seed is None else seed
    rng = random.Random(effective_seed)
    template_override_path = prototype_library_for_config(config, config_path=config_path)

    candidates: list[CandidateRecord] = []
    invalid_filtered = 0

    next_idx = 1
    while len(candidates) < count:
        try:
            candidate = _make_candidate(
                next_idx,
                config,
                effective_seed,
                rng,
                template_override_path,
            )
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
