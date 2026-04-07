from __future__ import annotations

from typing import get_args

import pytest

from materials_discovery.llm import (
    TranslatedBenchmarkExcludedRow,
    TranslatedBenchmarkExclusionReason,
    TranslatedBenchmarkIncludedRow,
    TranslatedBenchmarkLossPosture,
    TranslatedBenchmarkSetManifest,
    TranslatedBenchmarkSetSpec,
)
from materials_discovery.llm.storage import (
    llm_serving_benchmark_dir,
    llm_translation_export_dir,
    translated_benchmark_contract_path,
    translated_benchmark_excluded_path,
    translated_benchmark_included_path,
    translated_benchmark_manifest_path,
    translated_benchmark_set_dir,
)


def _valid_spec_kwargs() -> dict[str, object]:
    return {
        "benchmark_set_id": "external_cif_slice_v1",
        "bundle_manifest_paths": [
            "data/llm_translation_exports/al_cu_fe_cif_v1/manifest.json",
            "data/llm_translation_exports/sc_zn_cif_v1/manifest.json",
        ],
        "systems": ["Al-Cu-Fe", "Sc-Zn"],
        "target_family": "cif",
        "allowed_fidelity_tiers": ["exact", "anchored"],
        "loss_posture": "allow_explicit_loss",
        "operator_note": "  benchmark slice for external model smoke tests  ",
    }


def _valid_row_kwargs() -> dict[str, object]:
    return {
        "benchmark_set_id": "external_cif_slice_v1",
        "source_export_id": "al_cu_fe_cif_v1",
        "source_bundle_manifest_path": "data/llm_translation_exports/al_cu_fe_cif_v1/manifest.json",
        "candidate_id": "candidate_001",
        "system": "Al-Cu-Fe",
        "template_family": "ico",
        "target_family": "cif",
        "target_format": "cif_text",
        "fidelity_tier": "anchored",
        "loss_reasons": ["coordinate_derivation_required"],
        "diagnostic_codes": ["coordinate_derivation_required"],
        "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        "payload_path": "data/llm_translation_exports/al_cu_fe_cif_v1/payloads/candidate_001.cif",
        "payload_hash": "deadbeef",
        "emitted_text": "# translated candidate payload\n",
    }


def test_translated_benchmark_set_spec_rejects_blank_ids_and_empty_filters() -> None:
    with pytest.raises(ValueError, match="field must not be blank"):
        TranslatedBenchmarkSetSpec(**{**_valid_spec_kwargs(), "benchmark_set_id": " "})

    with pytest.raises(ValueError, match="must not be empty"):
        TranslatedBenchmarkSetSpec(**{**_valid_spec_kwargs(), "bundle_manifest_paths": []})

    with pytest.raises(ValueError, match="field must not be blank"):
        TranslatedBenchmarkSetSpec(
            **{
                **_valid_spec_kwargs(),
                "bundle_manifest_paths": [" ", "data/llm_translation_exports/sc_zn_cif_v1/manifest.json"],
            }
        )

    with pytest.raises(ValueError, match="must not be empty"):
        TranslatedBenchmarkSetSpec(**{**_valid_spec_kwargs(), "allowed_fidelity_tiers": []})


def test_translated_benchmark_set_spec_exposes_explicit_filter_fields() -> None:
    spec = TranslatedBenchmarkSetSpec(**_valid_spec_kwargs())

    assert spec.benchmark_set_id == "external_cif_slice_v1"
    assert spec.bundle_manifest_paths == [
        "data/llm_translation_exports/al_cu_fe_cif_v1/manifest.json",
        "data/llm_translation_exports/sc_zn_cif_v1/manifest.json",
    ]
    assert spec.systems == ["Al-Cu-Fe", "Sc-Zn"]
    assert spec.target_family == "cif"
    assert spec.allowed_fidelity_tiers == ["exact", "anchored"]
    assert spec.loss_posture == "allow_explicit_loss"
    assert spec.operator_note == "benchmark slice for external model smoke tests"


def test_translated_benchmark_rows_preserve_source_lineage_and_translation_surface() -> None:
    included = TranslatedBenchmarkIncludedRow(**_valid_row_kwargs())
    excluded = TranslatedBenchmarkExcludedRow(
        **{
            **_valid_row_kwargs(),
            "exclusion_reason": "loss_posture_rejected",
            "exclusion_detail": "lossless_only excludes anchored rows with explicit loss reasons",
        }
    )

    assert included.benchmark_set_id == "external_cif_slice_v1"
    assert included.source_export_id == "al_cu_fe_cif_v1"
    assert included.source_bundle_manifest_path.endswith("manifest.json")
    assert included.candidate_id == "candidate_001"
    assert included.fidelity_tier == "anchored"
    assert included.loss_reasons == ["coordinate_derivation_required"]

    assert excluded.source_export_id == "al_cu_fe_cif_v1"
    assert excluded.source_bundle_manifest_path.endswith("manifest.json")
    assert excluded.exclusion_reason == "loss_posture_rejected"
    assert excluded.exclusion_detail == (
        "lossless_only excludes anchored rows with explicit loss reasons"
    )
    assert excluded.fidelity_tier == "anchored"
    assert excluded.loss_reasons == ["coordinate_derivation_required"]


def test_translated_benchmark_set_manifest_carries_contract_and_inventory_paths_with_totals() -> None:
    spec = TranslatedBenchmarkSetSpec(**_valid_spec_kwargs())
    manifest = TranslatedBenchmarkSetManifest(
        benchmark_set_id="external_cif_slice_v1",
        contract_path="data/benchmarks/llm_external_sets/external_cif_slice_v1/freeze_contract.json",
        included_inventory_path="data/benchmarks/llm_external_sets/external_cif_slice_v1/included.jsonl",
        excluded_inventory_path="data/benchmarks/llm_external_sets/external_cif_slice_v1/excluded.jsonl",
        source_bundle_manifest_paths=spec.bundle_manifest_paths,
        source_export_ids=["al_cu_fe_cif_v1", "sc_zn_cif_v1"],
        included_count=18,
        excluded_count=7,
        target_family=spec.target_family,
        systems=spec.systems,
        filter_contract=spec,
    )

    assert manifest.contract_path.endswith("freeze_contract.json")
    assert manifest.included_inventory_path.endswith("included.jsonl")
    assert manifest.excluded_inventory_path.endswith("excluded.jsonl")
    assert manifest.source_bundle_manifest_paths == spec.bundle_manifest_paths
    assert manifest.source_export_ids == ["al_cu_fe_cif_v1", "sc_zn_cif_v1"]
    assert manifest.included_count == 18
    assert manifest.excluded_count == 7
    assert manifest.target_family == "cif"
    assert manifest.systems == ["Al-Cu-Fe", "Sc-Zn"]
    assert manifest.filter_contract.loss_posture == "allow_explicit_loss"


def test_translated_benchmark_vocabularies_are_typed_and_stable() -> None:
    assert set(get_args(TranslatedBenchmarkLossPosture)) == {
        "lossless_only",
        "allow_explicit_loss",
        "lossy_only",
    }
    assert set(get_args(TranslatedBenchmarkExclusionReason)) == {
        "system_not_selected",
        "target_family_mismatch",
        "fidelity_tier_not_selected",
        "loss_posture_rejected",
        "duplicate_translation_row",
    }


def test_translated_benchmark_storage_helpers_use_dedicated_external_set_root(
    tmp_path,
) -> None:
    benchmark_set_id = "external_cif_slice_v1"
    benchmark_dir = translated_benchmark_set_dir(benchmark_set_id, root=tmp_path)

    assert benchmark_dir == (
        tmp_path / "data" / "benchmarks" / "llm_external_sets" / benchmark_set_id
    )
    assert translated_benchmark_contract_path(benchmark_set_id, root=tmp_path) == (
        benchmark_dir / "freeze_contract.json"
    )
    assert translated_benchmark_manifest_path(benchmark_set_id, root=tmp_path) == (
        benchmark_dir / "manifest.json"
    )
    assert translated_benchmark_included_path(benchmark_set_id, root=tmp_path) == (
        benchmark_dir / "included.jsonl"
    )
    assert translated_benchmark_excluded_path(benchmark_set_id, root=tmp_path) == (
        benchmark_dir / "excluded.jsonl"
    )
    assert benchmark_dir != llm_translation_export_dir(benchmark_set_id, root=tmp_path)
    assert benchmark_dir != llm_serving_benchmark_dir(benchmark_set_id, root=tmp_path)


def test_translated_benchmark_storage_helpers_reject_blank_benchmark_ids(
    tmp_path,
) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        translated_benchmark_set_dir(" ", root=tmp_path)
