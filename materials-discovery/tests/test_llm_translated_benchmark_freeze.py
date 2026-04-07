from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from materials_discovery.common.io import load_json_object, load_jsonl, write_json_object, write_jsonl
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    TranslatedBenchmarkExcludedRow,
    TranslatedBenchmarkIncludedRow,
    TranslatedBenchmarkSetManifest,
    TranslatedBenchmarkSetSpec,
    export_translation_bundle,
)
from materials_discovery.llm.storage import (
    translated_benchmark_excluded_path,
    translated_benchmark_included_path,
)
from materials_discovery.llm.translated_benchmark import (
    freeze_translated_benchmark_set,
    load_translated_benchmark_spec,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_translation"


def _load_candidate_fixture(name: str) -> CandidateRecord:
    fixture_path = FIXTURE_DIR / name
    return CandidateRecord.model_validate(json.loads(fixture_path.read_text()))


def _write_candidate_jsonl(path: Path, candidates: list[CandidateRecord]) -> None:
    write_jsonl([candidate.model_dump(mode="json") for candidate in candidates], path)


def _export_bundle(
    workspace: Path,
    *,
    candidate: CandidateRecord,
    export_id: str,
    target_family: str = "cif",
) -> Path:
    input_path = workspace / "inputs" / f"{export_id}.jsonl"
    _write_candidate_jsonl(input_path, [candidate])
    summary = export_translation_bundle(
        candidates=[candidate],
        input_path=input_path,
        target_family=target_family,
        export_id=export_id,
        root=workspace,
    )
    return Path(summary.manifest_path)


def _rewrite_bundle_row(manifest_path: Path, **updates: object) -> None:
    manifest = load_json_object(manifest_path)
    inventory_path = manifest_path.parent / Path(manifest["inventory_path"]).name
    rows = load_jsonl(inventory_path)
    rows[0].update(updates)
    write_jsonl(rows, inventory_path)


def _write_spec(
    workspace: Path,
    *,
    benchmark_set_id: str,
    bundle_manifest_paths: list[str],
    systems: list[str],
    target_family: str = "cif",
    allowed_fidelity_tiers: list[str] | None = None,
    loss_posture: str = "allow_explicit_loss",
) -> Path:
    spec_path = workspace / "specs" / f"{benchmark_set_id}.json"
    write_json_object(
        {
            "benchmark_set_id": benchmark_set_id,
            "bundle_manifest_paths": bundle_manifest_paths,
            "systems": systems,
            "target_family": target_family,
            "allowed_fidelity_tiers": allowed_fidelity_tiers or ["exact", "anchored"],
            "loss_posture": loss_posture,
        },
        spec_path,
    )
    return spec_path


def _load_included_rows(summary_path: str) -> list[TranslatedBenchmarkIncludedRow]:
    return [
        TranslatedBenchmarkIncludedRow.model_validate(row)
        for row in load_jsonl(Path(summary_path))
    ]


def _load_excluded_rows(summary_path: str) -> list[TranslatedBenchmarkExcludedRow]:
    return [
        TranslatedBenchmarkExcludedRow.model_validate(row)
        for row in load_jsonl(Path(summary_path))
    ]


def _row_identity(
    row: TranslatedBenchmarkIncludedRow | TranslatedBenchmarkExcludedRow,
) -> tuple[str, str, str]:
    return (row.source_bundle_manifest_path, row.candidate_id, row.payload_hash)


def test_freeze_translated_benchmark_set_keeps_only_rows_matching_filters(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    exact_candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    lossy_candidate = _load_candidate_fixture("sc_zn_qc_candidate.json")

    exact_manifest = _export_bundle(
        workspace, candidate=exact_candidate, export_id="02-al-cu-fe-cif"
    )
    target_mismatch_manifest = _export_bundle(
        workspace,
        candidate=exact_candidate,
        export_id="00-al-cu-fe-material",
        target_family="material_string",
    )
    system_mismatch_manifest = _export_bundle(
        workspace, candidate=lossy_candidate, export_id="01-sc-zn-cif"
    )

    spec_path = _write_spec(
        workspace,
        benchmark_set_id="freeze_filter_slice_v1",
        bundle_manifest_paths=[
            str(exact_manifest),
            str(system_mismatch_manifest),
            str(target_mismatch_manifest),
        ],
        systems=["Al-Cu-Fe"],
        allowed_fidelity_tiers=["exact", "anchored"],
        loss_posture="lossless_only",
    )

    spec = load_translated_benchmark_spec(spec_path)
    summary = freeze_translated_benchmark_set(spec_path, root=workspace)

    included_rows = _load_included_rows(summary.included_inventory_path)
    excluded_rows = _load_excluded_rows(summary.excluded_inventory_path)

    assert spec.benchmark_set_id == "freeze_filter_slice_v1"
    assert summary.included_count == 1
    assert summary.excluded_count == 2
    assert [row.candidate_id for row in included_rows] == [exact_candidate.candidate_id]
    assert {row.exclusion_reason for row in excluded_rows} == {
        "system_not_selected",
        "target_family_mismatch",
    }


def test_freeze_translated_benchmark_set_writes_typed_exclusion_reasons(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    exact_candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    lossy_candidate = _load_candidate_fixture("sc_zn_qc_candidate.json")

    exact_manifest = _export_bundle(
        workspace, candidate=exact_candidate, export_id="00-eligible-cif"
    )
    system_manifest = _export_bundle(
        workspace, candidate=exact_candidate, export_id="01-system-mismatch"
    )
    fidelity_manifest = _export_bundle(
        workspace, candidate=exact_candidate, export_id="02-fidelity-mismatch"
    )
    target_manifest = _export_bundle(
        workspace,
        candidate=exact_candidate,
        export_id="03-target-mismatch",
        target_family="material_string",
    )
    loss_posture_manifest = _export_bundle(
        workspace, candidate=lossy_candidate, export_id="04-loss-posture"
    )

    _rewrite_bundle_row(system_manifest, system="Ti-Zr-Ni")
    _rewrite_bundle_row(fidelity_manifest, fidelity_tier="approximate")

    spec_path = _write_spec(
        workspace,
        benchmark_set_id="freeze_exclusion_reasons_v1",
        bundle_manifest_paths=[
            str(target_manifest),
            str(loss_posture_manifest),
            str(fidelity_manifest),
            str(system_manifest),
            str(exact_manifest),
        ],
        systems=["Al-Cu-Fe", "Sc-Zn"],
        allowed_fidelity_tiers=["exact", "lossy"],
        loss_posture="lossless_only",
    )

    summary = freeze_translated_benchmark_set(spec_path, root=workspace)
    excluded_rows = _load_excluded_rows(summary.excluded_inventory_path)

    assert summary.included_count == 1
    assert summary.excluded_count == 4
    assert {row.exclusion_reason for row in excluded_rows} == {
        "system_not_selected",
        "target_family_mismatch",
        "fidelity_tier_not_selected",
        "loss_posture_rejected",
    }


def test_freeze_translated_benchmark_set_excludes_exact_duplicates_after_first_keep(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")

    later_manifest = _export_bundle(
        workspace, candidate=candidate, export_id="02-duplicate-later"
    )
    earlier_manifest = _export_bundle(
        workspace, candidate=candidate, export_id="01-duplicate-earlier"
    )

    spec_path = _write_spec(
        workspace,
        benchmark_set_id="freeze_duplicates_v1",
        bundle_manifest_paths=[str(later_manifest), str(earlier_manifest)],
        systems=["Al-Cu-Fe"],
    )

    summary = freeze_translated_benchmark_set(spec_path, root=workspace)
    included_rows = _load_included_rows(summary.included_inventory_path)
    excluded_rows = _load_excluded_rows(summary.excluded_inventory_path)

    assert [row.source_export_id for row in included_rows] == ["01-duplicate-earlier"]
    assert [row.exclusion_reason for row in excluded_rows] == ["duplicate_translation_row"]
    assert [row.source_export_id for row in excluded_rows] == ["02-duplicate-later"]


def test_freeze_translated_benchmark_set_fails_closed_on_conflicting_duplicates(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")

    first_manifest = _export_bundle(
        workspace, candidate=candidate, export_id="01-conflict-first"
    )
    mutated_payload = candidate.model_dump(mode="json")
    mutated_payload["sites"][0]["fractional_position"] = [0.5, 0.25, 0.375]
    conflicting_candidate = CandidateRecord.model_validate(mutated_payload)
    second_manifest = _export_bundle(
        workspace, candidate=conflicting_candidate, export_id="02-conflict-second"
    )

    spec_path = _write_spec(
        workspace,
        benchmark_set_id="freeze_conflicts_v1",
        bundle_manifest_paths=[str(second_manifest), str(first_manifest)],
        systems=["Al-Cu-Fe"],
    )

    with pytest.raises(ValueError) as exc_info:
        freeze_translated_benchmark_set(spec_path, root=workspace)

    message = str(exc_info.value)
    assert candidate.candidate_id in message
    assert str(first_manifest) in message
    assert str(second_manifest) in message


def test_freeze_translated_benchmark_set_sorts_rows_deterministically_across_spec_order(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    exact_candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    lossy_candidate = _load_candidate_fixture("sc_zn_qc_candidate.json")

    manifests = [
        _export_bundle(workspace, candidate=exact_candidate, export_id="03-duplicate"),
        _export_bundle(workspace, candidate=exact_candidate, export_id="01-eligible"),
        _export_bundle(
            workspace,
            candidate=exact_candidate,
            export_id="02-target-mismatch",
            target_family="material_string",
        ),
        _export_bundle(workspace, candidate=lossy_candidate, export_id="04-lossy"),
    ]

    first_spec = _write_spec(
        workspace,
        benchmark_set_id="freeze_order_a_v1",
        bundle_manifest_paths=[str(path) for path in manifests],
        systems=["Al-Cu-Fe", "Sc-Zn"],
        allowed_fidelity_tiers=["exact", "anchored", "lossy"],
        loss_posture="allow_explicit_loss",
    )
    second_spec = _write_spec(
        workspace,
        benchmark_set_id="freeze_order_b_v1",
        bundle_manifest_paths=[str(path) for path in reversed(manifests)],
        systems=["Al-Cu-Fe", "Sc-Zn"],
        allowed_fidelity_tiers=["exact", "anchored", "lossy"],
        loss_posture="allow_explicit_loss",
    )

    first_summary = freeze_translated_benchmark_set(first_spec, root=workspace)
    second_summary = freeze_translated_benchmark_set(second_spec, root=workspace)

    first_included = [
        _row_identity(row) for row in _load_included_rows(first_summary.included_inventory_path)
    ]
    second_included = [
        _row_identity(row) for row in _load_included_rows(second_summary.included_inventory_path)
    ]
    first_excluded = [
        (_row_identity(row), row.exclusion_reason)
        for row in _load_excluded_rows(first_summary.excluded_inventory_path)
    ]
    second_excluded = [
        (_row_identity(row), row.exclusion_reason)
        for row in _load_excluded_rows(second_summary.excluded_inventory_path)
    ]

    assert first_included == second_included
    assert first_excluded == second_excluded
    assert Path(translated_benchmark_included_path("freeze_order_a_v1", root=workspace)).exists()
    assert Path(translated_benchmark_excluded_path("freeze_order_a_v1", root=workspace)).exists()


def test_freeze_translated_benchmark_set_writes_contract_manifest_and_lineage(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    exact_candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    lossy_candidate = _load_candidate_fixture("sc_zn_qc_candidate.json")

    target_manifest = _export_bundle(
        workspace,
        candidate=exact_candidate,
        export_id="03-target-mismatch",
        target_family="material_string",
    )
    lossy_manifest = _export_bundle(
        workspace, candidate=lossy_candidate, export_id="02-loss-posture"
    )
    exact_manifest = _export_bundle(
        workspace, candidate=exact_candidate, export_id="01-eligible-cif"
    )

    spec_path = _write_spec(
        workspace,
        benchmark_set_id="freeze_artifacts_v1",
        bundle_manifest_paths=[
            str(target_manifest),
            str(lossy_manifest),
            str(exact_manifest),
        ],
        systems=["Al-Cu-Fe", "Sc-Zn"],
        allowed_fidelity_tiers=["exact", "anchored", "lossy"],
        loss_posture="lossless_only",
    )

    summary = freeze_translated_benchmark_set(spec_path, root=workspace)
    contract_path = Path(summary.contract_path)
    manifest_path = Path(summary.manifest_path)

    assert contract_path.exists()
    assert manifest_path.exists()
    assert Path(summary.included_inventory_path).exists()
    assert Path(summary.excluded_inventory_path).exists()
    assert contract_path.name == "freeze_contract.json"
    assert manifest_path.name == "manifest.json"
    assert Path(summary.included_inventory_path).name == "included.jsonl"
    assert Path(summary.excluded_inventory_path).name == "excluded.jsonl"

    contract = TranslatedBenchmarkSetSpec.model_validate(load_json_object(contract_path))
    manifest = TranslatedBenchmarkSetManifest.model_validate(load_json_object(manifest_path))
    included_rows = _load_included_rows(summary.included_inventory_path)
    excluded_rows = _load_excluded_rows(summary.excluded_inventory_path)

    assert contract.bundle_manifest_paths == sorted(
        [str(target_manifest), str(lossy_manifest), str(exact_manifest)]
    )
    assert manifest.source_bundle_manifest_paths == contract.bundle_manifest_paths
    assert set(manifest.source_export_ids) == {
        "01-eligible-cif",
        "02-loss-posture",
        "03-target-mismatch",
    }
    assert manifest.exclusion_reason_counts == {
        "loss_posture_rejected": 1,
        "target_family_mismatch": 1,
    }
    assert manifest.included_count == summary.included_count == len(included_rows)
    assert manifest.excluded_count == summary.excluded_count == len(excluded_rows)
    assert summary.manifest_path == str(manifest_path.resolve())
    assert summary.included_inventory_path == str(Path(summary.included_inventory_path).resolve())


def test_freeze_translated_benchmark_set_rewrites_stable_artifacts_on_repeat_run(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")

    later_manifest = _export_bundle(
        workspace, candidate=candidate, export_id="02-duplicate-later"
    )
    earlier_manifest = _export_bundle(
        workspace, candidate=candidate, export_id="01-duplicate-earlier"
    )

    spec_path = _write_spec(
        workspace,
        benchmark_set_id="freeze_repeatability_v1",
        bundle_manifest_paths=[str(later_manifest), str(earlier_manifest)],
        systems=["Al-Cu-Fe"],
    )

    first_summary = freeze_translated_benchmark_set(spec_path, root=workspace)
    first_contract = Path(first_summary.contract_path).read_text(encoding="utf-8")
    first_manifest = Path(first_summary.manifest_path).read_text(encoding="utf-8")
    first_included = Path(first_summary.included_inventory_path).read_text(encoding="utf-8")
    first_excluded = Path(first_summary.excluded_inventory_path).read_text(encoding="utf-8")

    second_summary = freeze_translated_benchmark_set(spec_path, root=workspace)

    assert Path(second_summary.contract_path).read_text(encoding="utf-8") == first_contract
    assert Path(second_summary.manifest_path).read_text(encoding="utf-8") == first_manifest
    assert Path(second_summary.included_inventory_path).read_text(encoding="utf-8") == first_included
    assert Path(second_summary.excluded_inventory_path).read_text(encoding="utf-8") == first_excluded


def test_llm_public_freeze_surface_reexports_freeze_helpers() -> None:
    llm_module = importlib.import_module("materials_discovery.llm")

    assert llm_module.freeze_translated_benchmark_set is freeze_translated_benchmark_set
    assert llm_module.load_translated_benchmark_spec is load_translated_benchmark_spec
