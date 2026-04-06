from __future__ import annotations

from typing import Any

from materials_discovery.backends.structure_realization import (
    CoordinateSource,
    candidate_cartesian_positions,
    candidate_fractional_positions_with_sources,
)
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm.schema import (
    TranslatedStructureArtifact,
    TranslatedStructureDiagnostic,
    TranslatedStructureSite,
    TranslatedStructureSourceReference,
    TranslationTargetDescriptor,
)

CoordinateSourceEntry = tuple[str, CoordinateSource]


def infer_coordinate_sources(candidate: CandidateRecord) -> tuple[CoordinateSourceEntry, ...]:
    positions_with_sources = candidate_fractional_positions_with_sources(candidate)
    return tuple(
        (site.label, source)
        for site, (_, source) in zip(candidate.sites, positions_with_sources, strict=True)
    )


def assess_translation_fidelity(
    candidate: CandidateRecord,
    target: TranslationTargetDescriptor,
) -> str:
    del candidate, target
    return "anchored"


def prepare_translated_structure(
    candidate: CandidateRecord,
    target: TranslationTargetDescriptor,
) -> TranslatedStructureArtifact:
    positions_with_sources = candidate_fractional_positions_with_sources(candidate)
    cartesian_positions = candidate_cartesian_positions(candidate)
    coordinate_sources = infer_coordinate_sources(candidate)

    diagnostics = _coordinate_source_diagnostics(coordinate_sources)
    return TranslatedStructureArtifact(
        source=TranslatedStructureSourceReference(
            candidate_id=candidate.candidate_id,
            system=candidate.system,
            template_family=candidate.template_family,
            provenance_hints=_sorted_mapping(candidate.provenance),
        ),
        target=target,
        fidelity_tier=assess_translation_fidelity(candidate, target),
        composition=candidate.composition,
        cell=_normalized_cell(candidate.cell),
        sites=[
            TranslatedStructureSite(
                label=site.label,
                species=site.species,
                occupancy=site.occ,
                fractional_position=fractional_position,
                cartesian_position=cartesian_position,
            )
            for site, (fractional_position, _), cartesian_position in zip(
                candidate.sites,
                positions_with_sources,
                cartesian_positions,
                strict=True,
            )
        ],
        diagnostics=diagnostics,
    )


def _coordinate_source_diagnostics(
    coordinate_sources: tuple[CoordinateSourceEntry, ...],
) -> list[TranslatedStructureDiagnostic]:
    if any(source != "stored_fractional" for _, source in coordinate_sources):
        return [
            TranslatedStructureDiagnostic(
                code="coordinate_derivation_required",
                severity="warning",
                message="normalized coordinates required derivation for one or more sites",
                metadata={
                    "site_coordinate_sources": [
                        {
                            "site_label": site_label,
                            "coordinate_source": coordinate_source,
                        }
                        for site_label, coordinate_source in coordinate_sources
                    ]
                },
            )
        ]
    return []


def _normalized_cell(cell: dict[str, float]) -> dict[str, float]:
    ordered_keys = ("a", "b", "c", "alpha", "beta", "gamma")
    return {
        key: float(cell[key])
        for key in ordered_keys
        if key in cell
    }


def _sorted_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    return {key: mapping[key] for key in sorted(mapping)}
