from __future__ import annotations

from dataclasses import dataclass
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
    TranslationFidelityTier,
    TranslationLossReason,
    TranslationTargetDescriptor,
)

CoordinateSourceEntry = tuple[str, CoordinateSource]
_PERIODIC_HINT_TOKENS = ("approximant", "proxy", "periodic", "space_group:")
_QC_NATIVE_HINT_TOKENS = ("quasicrystal", "aperiodic", "pyqcstrc", "superspace")


@dataclass(frozen=True)
class _FidelityAssessment:
    tier: TranslationFidelityTier
    loss_reasons: tuple[TranslationLossReason, ...] = ()
    diagnostics: tuple[TranslatedStructureDiagnostic, ...] = ()


def infer_coordinate_sources(candidate: CandidateRecord) -> tuple[CoordinateSourceEntry, ...]:
    positions_with_sources = candidate_fractional_positions_with_sources(candidate)
    return tuple(
        (site.label, source)
        for site, (_, source) in zip(candidate.sites, positions_with_sources, strict=True)
    )


def assess_translation_fidelity(
    candidate: CandidateRecord,
    target: TranslationTargetDescriptor,
    *,
    requested_fidelity: TranslationFidelityTier | None = None,
) -> TranslationFidelityTier:
    assessment = _build_fidelity_assessment(candidate, target)
    if requested_fidelity == "exact" and assessment.tier != "exact":
        raise ValueError(
            "unsupported exactness claim for normalized translation target "
            f"{target.family}: classified as {assessment.tier}"
        )
    return assessment.tier


def prepare_translated_structure(
    candidate: CandidateRecord,
    target: TranslationTargetDescriptor,
) -> TranslatedStructureArtifact:
    positions_with_sources = candidate_fractional_positions_with_sources(candidate)
    cartesian_positions = candidate_cartesian_positions(candidate)
    coordinate_sources = infer_coordinate_sources(candidate)
    fidelity = _build_fidelity_assessment(candidate, target)

    diagnostics = [
        *_coordinate_source_diagnostics(coordinate_sources),
        *fidelity.diagnostics,
    ]
    return TranslatedStructureArtifact(
        source=TranslatedStructureSourceReference(
            candidate_id=candidate.candidate_id,
            system=candidate.system,
            template_family=candidate.template_family,
            provenance_hints=_sorted_mapping(candidate.provenance),
        ),
        target=target,
        fidelity_tier=fidelity.tier,
        loss_reasons=list(fidelity.loss_reasons),
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


def _build_fidelity_assessment(
    candidate: CandidateRecord,
    target: TranslationTargetDescriptor,
) -> _FidelityAssessment:
    coordinate_sources = infer_coordinate_sources(candidate)
    source_values = {source for _, source in coordinate_sources}
    strong_periodic_evidence = _has_periodic_safe_evidence(candidate)
    qc_native_evidence = _has_qc_native_evidence(candidate)

    if target.requires_periodic_cell and (
        qc_native_evidence or ("qphi_derived" in source_values and not strong_periodic_evidence)
    ):
        loss_reasons: list[TranslationLossReason] = ["aperiodic_to_periodic_proxy"]
        if "qphi_derived" in source_values:
            loss_reasons.append("coordinate_derivation_required")
        if not target.preserves_qc_native_semantics:
            loss_reasons.append("qc_semantics_dropped")
        return _FidelityAssessment(
            tier="lossy",
            loss_reasons=tuple(loss_reasons),
            diagnostics=_loss_diagnostics(
                include_qc_drop=not target.preserves_qc_native_semantics,
            ),
        )

    if strong_periodic_evidence and source_values == {"stored_fractional"}:
        return _FidelityAssessment(tier="exact")
    if strong_periodic_evidence and "qphi_derived" not in source_values:
        return _FidelityAssessment(tier="anchored")
    return _FidelityAssessment(tier="approximate")


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


def _loss_diagnostics(*, include_qc_drop: bool) -> tuple[TranslatedStructureDiagnostic, ...]:
    diagnostics = [
        TranslatedStructureDiagnostic(
            code="periodic_proxy_required",
            severity="warning",
            message="target family requires a periodic proxy for normalized export",
        )
    ]
    if include_qc_drop:
        diagnostics.append(
            TranslatedStructureDiagnostic(
                code="qc_semantics_dropped",
                severity="warning",
                message="target family cannot preserve QC-native semantics exactly",
            )
        )
    return tuple(diagnostics)


def _has_periodic_safe_evidence(candidate: CandidateRecord) -> bool:
    tokens = _candidate_hint_tokens(candidate)
    return any(
        token.startswith("space_group:") or any(hint in token for hint in _PERIODIC_HINT_TOKENS)
        for token in tokens
    )


def _has_qc_native_evidence(candidate: CandidateRecord) -> bool:
    tokens = _candidate_hint_tokens(candidate)
    return any(any(hint in token for hint in _QC_NATIVE_HINT_TOKENS) for token in tokens)


def _candidate_hint_tokens(candidate: CandidateRecord) -> set[str]:
    tokens = {candidate.template_family.strip().lower()}
    tokens.update(_flatten_string_tokens(candidate.provenance))
    return {token for token in tokens if token}


def _flatten_string_tokens(value: object) -> set[str]:
    if isinstance(value, str):
        normalized = value.strip().lower()
        return {normalized} if normalized else set()
    if isinstance(value, dict):
        tokens: set[str] = set()
        for item in value.values():
            tokens.update(_flatten_string_tokens(item))
        return tokens
    if isinstance(value, list | tuple | set):
        tokens: set[str] = set()
        for item in value:
            tokens.update(_flatten_string_tokens(item))
        return tokens
    return set()


def _normalized_cell(cell: dict[str, float]) -> dict[str, float]:
    ordered_keys = ("a", "b", "c", "alpha", "beta", "gamma")
    return {
        key: float(cell[key])
        for key in ordered_keys
        if key in cell
    }


def _sorted_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
    return {key: mapping[key] for key in sorted(mapping)}
