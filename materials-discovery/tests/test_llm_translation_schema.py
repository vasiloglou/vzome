from __future__ import annotations

from typing import get_args

import pytest
from pydantic import ValidationError

from materials_discovery.llm import (
    CorpusExample,
    FidelityTier,
    TranslatedStructureArtifact,
    TranslationFidelityTier,
    TranslationTargetDescriptor,
    list_translation_targets,
    resolve_translation_target,
)
from materials_discovery.llm.schema import TranslatedStructureDiagnostic


def _artifact_payload(
    *,
    fidelity_tier: str = "anchored",
    loss_reasons: list[str] | None = None,
    diagnostics: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return {
        "source": {
            "candidate_id": "candidate-001",
            "system": "Al-Cu-Fe",
            "template_family": "icosahedral_approximant_1_1",
            "provenance_hints": {
                "candidate_manifest_path": "data/candidates/al_cu_fe_batch.jsonl",
                "compile_batch": "batch-001",
            },
        },
        "target": {
            "family": "cif",
            "target_format": "cif_text",
            "requires_periodic_cell": True,
            "requires_fractional_coordinates": True,
            "preserves_qc_native_semantics": False,
            "emission_kind": "file",
        },
        "fidelity_tier": fidelity_tier,
        "loss_reasons": loss_reasons or [],
        "composition": {"Al": 0.6, "Cu": 0.2, "Fe": 0.2},
        "cell": {
            "a": 14.2,
            "b": 14.2,
            "c": 14.2,
            "alpha": 90.0,
            "beta": 90.0,
            "gamma": 90.0,
        },
        "sites": [
            {
                "label": "site-001",
                "species": "Al",
                "occupancy": 1.0,
                "fractional_position": (0.1, 0.2, 0.3),
            }
        ],
        "diagnostics": diagnostics or [],
    }


def test_translated_structure_artifact_records_source_target_and_schema_version() -> None:
    artifact = TranslatedStructureArtifact.model_validate(_artifact_payload())

    assert artifact.schema_version == "translated-structure-artifact/v1"
    assert artifact.source.candidate_id == "candidate-001"
    assert artifact.source.provenance_hints == {
        "candidate_manifest_path": "data/candidates/al_cu_fe_batch.jsonl",
        "compile_batch": "batch-001",
    }
    assert artifact.target == TranslationTargetDescriptor(
        family="cif",
        target_format="cif_text",
        requires_periodic_cell=True,
        requires_fractional_coordinates=True,
        preserves_qc_native_semantics=False,
        emission_kind="file",
    )


def test_translation_fidelity_enum_stays_additive_to_corpus_fidelity() -> None:
    assert set(get_args(TranslationFidelityTier)) == {
        "exact",
        "anchored",
        "approximate",
        "lossy",
    }
    assert set(get_args(FidelityTier)) == {
        "exact",
        "anchored",
        "approximate",
        "heuristic",
    }


def test_lossy_translated_artifacts_require_explicit_loss_reasons() -> None:
    with pytest.raises(ValidationError):
        TranslatedStructureArtifact.model_validate(
            _artifact_payload(fidelity_tier="lossy", loss_reasons=[])
        )


def test_translated_artifact_preserves_diagnostics_without_emitted_text() -> None:
    diagnostic = TranslatedStructureDiagnostic(
        code="coordinate_derivation_required",
        severity="warning",
        message="fractional positions were derived from qphi coordinates",
        metadata={"site_labels": ["site-001"]},
    )
    artifact = TranslatedStructureArtifact.model_validate(
        _artifact_payload(diagnostics=[diagnostic.model_dump()])
    )

    assert artifact.emitted_text is None
    assert artifact.diagnostics == [diagnostic]


def test_llm_imports_remain_additive_for_existing_schema_users() -> None:
    example = CorpusExample.model_validate(
        {
            "provenance": {
                "example_id": "example-001",
                "source_family": "candidate_record",
                "source_path": "data/candidates/al_cu_fe_batch.jsonl",
                "source_record_id": "candidate-001",
                "system": "Al-Cu-Fe",
                "fidelity_tier": "anchored",
                "release_tier": "pending",
                "builder_version": "phase6_v1",
            },
            "zomic_text": "label shell_01\n",
            "properties": {},
            "validation": {},
        }
    )

    assert example.provenance.fidelity_tier == "anchored"
    assert "lossy" not in get_args(FidelityTier)


def test_translated_artifact_rejects_missing_source_candidate_linkage() -> None:
    with pytest.raises(ValidationError):
        TranslatedStructureArtifact.model_validate(
            {
                **_artifact_payload(),
                "source": {
                    "candidate_id": " ",
                    "system": "Al-Cu-Fe",
                    "template_family": "icosahedral_approximant_1_1",
                    "provenance_hints": {"compile_batch": "batch-001"},
                },
            }
        )


def test_builtin_translation_registry_exposes_cif_and_material_string_targets() -> None:
    targets = list_translation_targets()

    assert {target.family for target in targets} == {"cif", "material_string"}
    assert {target.target_format for target in targets} == {
        "cif_text",
        "crystaltextllm_material_string",
    }


def test_resolve_translation_target_returns_cif_descriptor() -> None:
    descriptor = resolve_translation_target("cif")

    assert descriptor == TranslationTargetDescriptor(
        family="cif",
        target_format="cif_text",
        requires_periodic_cell=True,
        requires_fractional_coordinates=True,
        preserves_qc_native_semantics=False,
        emission_kind="file",
        description="Periodic CIF export for downstream crystal-LLM workflows.",
    )


def test_translation_target_descriptors_expose_periodic_and_qc_semantics_expectations() -> None:
    descriptor = resolve_translation_target("material_string")

    assert descriptor.requires_periodic_cell is True
    assert descriptor.requires_fractional_coordinates is True
    assert descriptor.preserves_qc_native_semantics is False
    assert descriptor.emission_kind == "line_oriented"


def test_unknown_translation_target_lookup_fails_clearly() -> None:
    with pytest.raises(KeyError, match="unknown translation target family: imaginary"):
        resolve_translation_target("imaginary")
