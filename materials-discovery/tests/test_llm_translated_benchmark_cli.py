from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import write_json_object, write_jsonl
from materials_discovery.llm import (
    TranslatedBenchmarkExcludedRow,
    TranslatedBenchmarkIncludedRow,
    TranslatedBenchmarkSetManifest,
    TranslatedBenchmarkSetSpec,
    TranslatedBenchmarkSetSummary,
)


def _write_manifest_fixture(workspace: Path) -> Path:
    benchmark_dir = (
        workspace
        / "data"
        / "benchmarks"
        / "llm_external_sets"
        / "translated_demo_v1"
    )
    contract_path = benchmark_dir / "freeze_contract.json"
    included_path = benchmark_dir / "included.jsonl"
    excluded_path = benchmark_dir / "excluded.jsonl"
    manifest_path = benchmark_dir / "manifest.json"

    write_json_object(
        TranslatedBenchmarkSetSpec(
            benchmark_set_id="translated_demo_v1",
            bundle_manifest_paths=[
                "data/llm_translation_exports/al_cu_fe_demo/manifest.json",
                "data/llm_translation_exports/sc_zn_demo/manifest.json",
            ],
            systems=["Al-Cu-Fe", "Sc-Zn"],
            target_family="cif",
            allowed_fidelity_tiers=["exact", "anchored", "lossy"],
            loss_posture="allow_explicit_loss",
        ).model_dump(mode="json"),
        contract_path,
    )
    write_jsonl(
        [
            TranslatedBenchmarkIncludedRow(
                benchmark_set_id="translated_demo_v1",
                source_export_id="al_cu_fe_demo",
                source_bundle_manifest_path="data/llm_translation_exports/al_cu_fe_demo/manifest.json",
                candidate_id="al_cu_fe_fixture_periodic_001",
                system="Al-Cu-Fe",
                template_family="icosahedral_approximant",
                target_family="cif",
                target_format="cif_text",
                fidelity_tier="exact",
                composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
                payload_path="data/llm_translation_exports/al_cu_fe_demo/payloads/fixture.cif",
                payload_hash="included-hash",
                emitted_text="data_fixture",
            ).model_dump(mode="json")
        ],
        included_path,
    )
    write_jsonl(
        [
            TranslatedBenchmarkExcludedRow(
                benchmark_set_id="translated_demo_v1",
                source_export_id="sc_zn_demo",
                source_bundle_manifest_path="data/llm_translation_exports/sc_zn_demo/manifest.json",
                candidate_id="sc_zn_fixture_qc_001",
                system="Sc-Zn",
                template_family="icosahedral_approximant",
                target_family="cif",
                target_format="cif_text",
                fidelity_tier="lossy",
                composition={"Sc": 0.5, "Zn": 0.5},
                payload_path="data/llm_translation_exports/sc_zn_demo/payloads/fixture.cif",
                payload_hash="excluded-lossy-hash",
                emitted_text="lossy_fixture",
                exclusion_reason="loss_posture_rejected",
                exclusion_detail="lossless_only rejects rows that carry explicit translation loss",
            ).model_dump(mode="json"),
            TranslatedBenchmarkExcludedRow(
                benchmark_set_id="translated_demo_v1",
                source_export_id="al_cu_fe_demo_dup",
                source_bundle_manifest_path="data/llm_translation_exports/al_cu_fe_demo_dup/manifest.json",
                candidate_id="al_cu_fe_fixture_duplicate_002",
                system="Al-Cu-Fe",
                template_family="icosahedral_approximant",
                target_family="cif",
                target_format="cif_text",
                fidelity_tier="exact",
                composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
                payload_path="data/llm_translation_exports/al_cu_fe_demo_dup/payloads/fixture.cif",
                payload_hash="excluded-duplicate-hash",
                emitted_text="duplicate_fixture",
                exclusion_reason="duplicate_translation_row",
                exclusion_detail="duplicate of candidate_id already kept elsewhere",
            ).model_dump(mode="json"),
        ],
        excluded_path,
    )
    write_json_object(
        TranslatedBenchmarkSetManifest(
            benchmark_set_id="translated_demo_v1",
            contract_path="data/benchmarks/llm_external_sets/translated_demo_v1/freeze_contract.json",
            included_inventory_path="data/benchmarks/llm_external_sets/translated_demo_v1/included.jsonl",
            excluded_inventory_path="data/benchmarks/llm_external_sets/translated_demo_v1/excluded.jsonl",
            source_bundle_manifest_paths=[
                "data/llm_translation_exports/al_cu_fe_demo/manifest.json",
                "data/llm_translation_exports/sc_zn_demo/manifest.json",
            ],
            source_export_ids=["al_cu_fe_demo", "sc_zn_demo"],
            included_count=1,
            excluded_count=2,
            target_family="cif",
            systems=["Al-Cu-Fe", "Sc-Zn"],
            exclusion_reason_counts={
                "duplicate_translation_row": 1,
                "loss_posture_rejected": 1,
            },
            filter_contract=TranslatedBenchmarkSetSpec(
                benchmark_set_id="translated_demo_v1",
                bundle_manifest_paths=[
                    "data/llm_translation_exports/al_cu_fe_demo/manifest.json",
                    "data/llm_translation_exports/sc_zn_demo/manifest.json",
                ],
                systems=["Al-Cu-Fe", "Sc-Zn"],
                target_family="cif",
                allowed_fidelity_tiers=["exact", "anchored", "lossy"],
                loss_posture="allow_explicit_loss",
            ),
        ).model_dump(mode="json"),
        manifest_path,
    )
    return manifest_path


def test_cli_llm_translated_benchmark_freeze_prints_summary_json(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    spec_path = tmp_path / "freeze_spec.yaml"
    spec_path.write_text("benchmark_set_id: translated_demo_v1\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def _fake_freeze(spec_path_arg: Path, *, root: Path | None = None) -> TranslatedBenchmarkSetSummary:
        captured["spec_path"] = spec_path_arg
        captured["root"] = root
        return TranslatedBenchmarkSetSummary(
            benchmark_set_id="translated_demo_v1",
            target_family="cif",
            loss_posture="allow_explicit_loss",
            systems=["Al-Cu-Fe", "Sc-Zn"],
            included_count=3,
            excluded_count=2,
            contract_path=str(tmp_path / "data" / "benchmarks" / "llm_external_sets" / "translated_demo_v1" / "freeze_contract.json"),
            manifest_path=str(tmp_path / "data" / "benchmarks" / "llm_external_sets" / "translated_demo_v1" / "manifest.json"),
            included_inventory_path=str(tmp_path / "data" / "benchmarks" / "llm_external_sets" / "translated_demo_v1" / "included.jsonl"),
            excluded_inventory_path=str(tmp_path / "data" / "benchmarks" / "llm_external_sets" / "translated_demo_v1" / "excluded.jsonl"),
        )

    monkeypatch.setattr("materials_discovery.cli.freeze_translated_benchmark_set", _fake_freeze)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-translated-benchmark-freeze",
            "--spec",
            str(spec_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["benchmark_set_id"] == "translated_demo_v1"
    assert payload["manifest_path"].endswith("/manifest.json")
    assert payload["included_inventory_path"].endswith("/included.jsonl")
    assert payload["excluded_inventory_path"].endswith("/excluded.jsonl")
    assert captured["spec_path"] == spec_path
    assert captured["root"] == tmp_path


def test_cli_llm_translated_benchmark_freeze_returns_code_2_for_missing_spec(
    tmp_path: Path,
) -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "llm-translated-benchmark-freeze",
            "--spec",
            str(tmp_path / "missing-freeze-spec.yaml"),
        ],
    )

    assert result.exit_code == 2
    assert "llm-translated-benchmark-freeze failed: translated benchmark spec not found" in result.stderr


def test_cli_llm_translated_benchmark_freeze_returns_code_2_for_invalid_contract(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    spec_path = tmp_path / "freeze_spec.yaml"
    spec_path.write_text("benchmark_set_id: translated_demo_v1\n", encoding="utf-8")

    monkeypatch.setattr(
        "materials_discovery.cli.freeze_translated_benchmark_set",
        lambda spec_path_arg, *, root=None: (_ for _ in ()).throw(ValueError("invalid freeze contract")),
    )
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-translated-benchmark-freeze",
            "--spec",
            str(spec_path),
        ],
    )

    assert result.exit_code == 2
    assert "llm-translated-benchmark-freeze failed: invalid freeze contract" in result.stderr


def test_cli_llm_translated_benchmark_inspect_prints_manifest_summary_and_rows(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    manifest_path = _write_manifest_fixture(tmp_path)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-translated-benchmark-inspect",
            "--manifest",
            str(manifest_path),
        ],
    )

    assert result.exit_code == 0
    assert "Benchmark set: translated_demo_v1" in result.stdout
    assert "Target family: cif" in result.stdout
    assert "Systems: Al-Cu-Fe, Sc-Zn" in result.stdout
    assert "Included count: 1" in result.stdout
    assert "Excluded count: 2" in result.stdout
    assert "Contract: data/benchmarks/llm_external_sets/translated_demo_v1/freeze_contract.json" in result.stdout
    assert "Included: al_cu_fe_fixture_periodic_001 [exact]" in result.stdout
    assert "Excluded: sc_zn_fixture_qc_001 [loss_posture_rejected]" in result.stdout


def test_cli_llm_translated_benchmark_inspect_filters_rows_by_show_and_candidate_id(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    manifest_path = _write_manifest_fixture(tmp_path)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    included_result = runner.invoke(
        app,
        [
            "llm-translated-benchmark-inspect",
            "--manifest",
            str(manifest_path),
            "--show",
            "included",
            "--candidate-id",
            "al_cu_fe_fixture_periodic_001",
        ],
    )

    assert included_result.exit_code == 0
    assert "Included: al_cu_fe_fixture_periodic_001 [exact]" in included_result.stdout
    assert "Excluded:" not in included_result.stdout

    excluded_result = runner.invoke(
        app,
        [
            "llm-translated-benchmark-inspect",
            "--manifest",
            str(manifest_path),
            "--show",
            "excluded",
        ],
    )

    assert excluded_result.exit_code == 0
    assert "Included:" not in excluded_result.stdout
    assert "Excluded: sc_zn_fixture_qc_001 [loss_posture_rejected]" in excluded_result.stdout
    assert "Excluded: al_cu_fe_fixture_duplicate_002 [duplicate_translation_row]" in excluded_result.stdout


def test_cli_llm_translated_benchmark_inspect_returns_code_2_for_missing_candidate(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    manifest_path = _write_manifest_fixture(tmp_path)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-translated-benchmark-inspect",
            "--manifest",
            str(manifest_path),
            "--show",
            "all",
            "--candidate-id",
            "missing_candidate_id",
        ],
    )

    assert result.exit_code == 2
    assert (
        "llm-translated-benchmark-inspect failed: candidate_id not found in translated benchmark set: missing_candidate_id"
        in result.stderr
    )
