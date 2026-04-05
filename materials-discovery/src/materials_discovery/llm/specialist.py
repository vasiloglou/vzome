from __future__ import annotations

from collections import Counter
from typing import Any

from materials_discovery.common.schema import CandidateRecord


def build_specialized_evaluation_payload(candidate: CandidateRecord) -> dict[str, Any]:
    species_counts = Counter(site.species for site in candidate.sites)
    site_geometry: list[dict[str, Any]] = []
    for site in candidate.sites:
        site_geometry.append(
            {
                "label": site.label,
                "species": site.species,
                "fractional_position": site.fractional_position,
                "cartesian_position": site.cartesian_position,
            }
        )

    return {
        "evaluation_mode": "specialized_materials",
        "candidate_id": candidate.candidate_id,
        "system": candidate.system,
        "template_family": candidate.template_family,
        "composition": candidate.composition,
        "species_counts": dict(sorted(species_counts.items())),
        "cell": candidate.cell,
        "site_count": len(candidate.sites),
        "site_geometry": site_geometry,
        "screen": candidate.screen,
        "digital_validation": candidate.digital_validation.model_dump(mode="json"),
        "rank_context": candidate.provenance.get("hifi_rank"),
    }
