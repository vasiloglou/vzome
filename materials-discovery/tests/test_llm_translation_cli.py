from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import write_json_object, write_jsonl
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm import (
    TranslationBundleManifest,
    TranslationExportSummary,
    TranslationInventoryRow,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_translation"


def _load_candidate_fixture(name: str) -> CandidateRecord:
    fixture_path = FIXTURE_DIR / name
    return CandidateRecord.model_validate(json.loads(fixture_path.read_text()))


class _FakeBenchmarkContext:
    def as_dict(self) -> dict[str, object]:
        return {
            "lane_id": "phase33_demo_lane",
            "benchmark_corpus": "data/benchmarks/al_cu_fe_benchmark.json",
        }


def test_cli_llm_translate_writes_stage_manifest_and_passes_lineage_hooks(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    repo_root = Path(__file__).resolve().parents[1]
    config = repo_root / "configs" / "systems" / "al_cu_fe.yaml"
    input_path = tmp_path / "ranked.jsonl"
    candidate = _load_candidate_fixture("al_cu_fe_periodic_candidate.json")
    write_jsonl([candidate.model_dump(mode="json")], input_path)

    captured: dict[str, object] = {}

    def _fake_export_bundle(
        *,
        candidates,
        input_path,
        target_family,
        export_id,
        root,
        stage_manifest_path=None,
        source_lineage=None,
        benchmark_context=None,
    ):
        captured["candidate_count"] = len(candidates)
        captured["input_path"] = input_path
        captured["target_family"] = target_family
        captured["export_id"] = export_id
        captured["root"] = root
        captured["stage_manifest_path"] = stage_manifest_path
        captured["source_lineage"] = source_lineage
        captured["benchmark_context"] = benchmark_context

        bundle_dir = tmp_path / "data" / "llm_translation_exports" / export_id
        payload_dir = bundle_dir / "payloads"
        payload_dir.mkdir(parents=True, exist_ok=True)
        payload_path = payload_dir / f"{candidate.candidate_id}.cif"
        payload_path.write_text("# source_candidate_id=fixture\n", encoding="utf-8")

        bundle_manifest = bundle_dir / "manifest.json"
        inventory_path = bundle_dir / "inventory.jsonl"
        write_json_object(
            TranslationBundleManifest(
                export_id=export_id,
                created_at_utc="2026-04-07T00:04:00Z",
                input_path=str(input_path),
                target_family="cif",
                target_format="cif_text",
                inventory_path=str(inventory_path),
                payload_dir=str(payload_dir),
                candidate_count=1,
                exported_count=1,
                lossy_count=0,
                stage_manifest_path=stage_manifest_path,
                source_lineage=source_lineage,
                benchmark_context=benchmark_context,
            ).model_dump(mode="json"),
            bundle_manifest,
        )
        write_jsonl(
            [
                TranslationInventoryRow(
                    export_id=export_id,
                    candidate_id=candidate.candidate_id,
                    system=candidate.system,
                    template_family=candidate.template_family,
                    target_family="cif",
                    target_format="cif_text",
                    fidelity_tier="exact",
                    composition=candidate.composition,
                    payload_path=str(payload_path),
                    payload_hash="deadbeef",
                    emitted_text="# source_candidate_id=fixture\n",
                ).model_dump(mode="json")
            ],
            inventory_path,
        )
        return TranslationExportSummary(
            export_id=export_id,
            target_family="cif",
            target_format="cif_text",
            candidate_count=1,
            exported_count=1,
            lossy_count=0,
            manifest_path=str(bundle_manifest),
            inventory_path=str(inventory_path),
            payload_dir=str(payload_dir),
            stage_manifest_path=stage_manifest_path,
        )

    monkeypatch.setattr("materials_discovery.cli.export_translation_bundle", _fake_export_bundle)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)
    monkeypatch.setattr(
        "materials_discovery.cli._resolve_campaign_lineage",
        lambda system_slug, candidates: {"llm_campaign": {"campaign_id": "cmp_001", "launch_id": "launch_001"}},
    )
    monkeypatch.setattr(
        "materials_discovery.cli._load_benchmark_context",
        lambda config, system_slug: _FakeBenchmarkContext(),
    )

    result = runner.invoke(
        app,
        [
            "llm-translate",
            "--config",
            str(config),
            "--input",
            str(input_path),
            "--target",
            "cif",
            "--export-id",
            "al_cu_fe_cif_v1",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["export_id"] == "al_cu_fe_cif_v1"
    assert Path(payload["stage_manifest_path"]).exists()
    assert captured["candidate_count"] == 1
    assert captured["input_path"] == input_path
    assert captured["target_family"] == "cif"
    assert captured["export_id"] == "al_cu_fe_cif_v1"
    assert captured["source_lineage"] == {
        "llm_campaign": {"campaign_id": "cmp_001", "launch_id": "launch_001"}
    }
    assert captured["benchmark_context"] == {
        "lane_id": "phase33_demo_lane",
        "benchmark_corpus": "data/benchmarks/al_cu_fe_benchmark.json",
    }


def test_cli_llm_translate_returns_code_2_when_input_is_missing(tmp_path: Path) -> None:
    runner = CliRunner()
    repo_root = Path(__file__).resolve().parents[1]
    config = repo_root / "configs" / "systems" / "al_cu_fe.yaml"

    result = runner.invoke(
        app,
        [
            "llm-translate",
            "--config",
            str(config),
            "--input",
            str(tmp_path / "missing.jsonl"),
            "--target",
            "cif",
            "--export-id",
            "missing_export",
        ],
    )

    assert result.exit_code == 2
    assert "llm-translate failed: translation input candidates file not found" in result.stderr


def test_cli_llm_translate_inspect_prints_bundle_summary_and_candidate_details(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    bundle_dir = tmp_path / "data" / "llm_translation_exports" / "demo_export"
    payload_dir = bundle_dir / "payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)
    payload_path = payload_dir / "fixture.cif"
    payload_path.write_text("# source_candidate_id=fixture\n", encoding="utf-8")

    manifest_path = bundle_dir / "manifest.json"
    inventory_path = bundle_dir / "inventory.jsonl"
    write_json_object(
        TranslationBundleManifest(
            export_id="demo_export",
            created_at_utc="2026-04-07T00:04:00Z",
            input_path="data/ranked/al_cu_fe_ranked.jsonl",
            target_family="cif",
            target_format="cif_text",
            inventory_path="data/llm_translation_exports/demo_export/inventory.jsonl",
            payload_dir="data/llm_translation_exports/demo_export/payloads",
            candidate_count=1,
            exported_count=1,
            lossy_count=0,
            stage_manifest_path="data/manifests/al_cu_fe_demo_export_llm_translate_manifest.json",
        ).model_dump(mode="json"),
        manifest_path,
    )
    write_jsonl(
        [
            TranslationInventoryRow(
                export_id="demo_export",
                candidate_id="al_cu_fe_fixture_periodic_001",
                system="Al-Cu-Fe",
                template_family="icosahedral_approximant",
                target_family="cif",
                target_format="cif_text",
                fidelity_tier="exact",
                composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
                payload_path="data/llm_translation_exports/demo_export/payloads/fixture.cif",
                payload_hash="deadbeef",
                emitted_text="# source_candidate_id=fixture\n",
            ).model_dump(mode="json")
        ],
        inventory_path,
    )

    result = runner.invoke(
        app,
        [
            "llm-translate-inspect",
            "--manifest",
            str(manifest_path),
            "--candidate-id",
            "al_cu_fe_fixture_periodic_001",
        ],
    )

    assert result.exit_code == 0
    assert "Export ID: demo_export" in result.stdout
    assert "Target: cif (cif_text)" in result.stdout
    assert "Input: data/ranked/al_cu_fe_ranked.jsonl" in result.stdout
    assert "Candidate count: 1" in result.stdout
    assert "Lossy count: 0" in result.stdout
    assert "al_cu_fe_fixture_periodic_001 [exact]" in result.stdout
    assert "Payload: data/llm_translation_exports/demo_export/payloads/fixture.cif" in result.stdout


def test_cli_llm_translate_inspect_missing_manifest_returns_code_2(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "llm-translate-inspect",
            "--manifest",
            str(tmp_path / "missing_manifest.json"),
        ],
    )

    assert result.exit_code == 2
    assert "llm-translate-inspect failed: translation bundle manifest not found" in result.stderr
