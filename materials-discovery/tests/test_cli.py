from __future__ import annotations

import json
from pathlib import Path

import yaml
from pytest import MonkeyPatch
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import ZomicExportSummary


def test_cli_ingest_success(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    fixture = workspace / "data" / "external" / "fixtures" / "hypodx_sample.json"
    out_file = tmp_path / "ingest.jsonl"

    result = runner.invoke(
        app,
        [
            "ingest",
            "--config",
            str(config),
            "--fixture",
            str(fixture),
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()


def test_cli_legacy_config_without_ingestion_still_succeeds(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    out_file = tmp_path / "legacy_ingest.jsonl"

    result = runner.invoke(
        app,
        [
            "ingest",
            "--config",
            str(config),
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()


def test_cli_source_registry_config_succeeds(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    out_file = tmp_path / "source_registry_ingest.jsonl"

    data = load_yaml(base_config)
    data["backend"] = {"mode": "real", "ingest_adapter": "source_registry_v1"}
    data["ingestion"] = {
        "source_key": "materials_project",
        "adapter_key": "direct_api_v1",
        "snapshot_id": "cli_source_registry_v1",
        "use_cached_snapshot": False,
        "artifact_root": str(tmp_path / "source_cache"),
        "query": {
            "inline_rows": [
                {
                    "material_id": "mp-001",
                    "formula_pretty": "Al7Cu2Fe",
                    "chemsys": "Al-Cu-Fe",
                    "composition_reduced": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
                    "symmetry": {"symbol": "Pm-3"},
                    "structure": {"site_count": 36},
                }
            ]
        },
    }
    config_path = tmp_path / "source_registry.yaml"
    config_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "ingest",
            "--config",
            str(config_path),
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()


def test_cli_generate_success(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe.yaml"
    out_file = tmp_path / "generated.jsonl"

    result = runner.invoke(
        app,
        [
            "generate",
            "--config",
            str(config),
            "--count",
            "12",
            "--seed",
            "7",
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()


def test_cli_llm_generate_missing_seed_returns_2() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"

    result = runner.invoke(
        app,
        [
            "llm-generate",
            "--config",
            str(config),
            "--count",
            "1",
            "--seed-zomic",
            str(workspace / "does-not-exist.zomic"),
        ],
    )

    assert result.exit_code == 2


def test_cli_llm_launch_missing_spec_returns_2() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    spec = workspace / "does-not-exist-campaign-spec.json"

    result = runner.invoke(
        app,
        [
            "llm-launch",
            "--campaign-spec",
            str(spec),
        ],
    )

    assert result.exit_code == 2


def test_cli_export_zomic_success(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    runner = CliRunner()
    design_path = tmp_path / "demo.yaml"
    design_path.write_text("zomic_file: demo.zomic\n", encoding="utf-8")

    monkeypatch.setattr(
        "materials_discovery.cli.export_zomic_design",
        lambda design, output_path=None, force=False: ZomicExportSummary(
            design_path=str(design),
            zomic_file="demo.zomic",
            raw_export_path="raw.json",
            orbit_library_path=str(output_path or tmp_path / "demo.json"),
            labeled_site_count=3,
            orbit_count=2,
        ),
    )

    result = runner.invoke(
        app,
        [
            "export-zomic",
            "--design",
            str(design_path),
            "--out",
            str(tmp_path / "orbit.json"),
        ],
    )

    assert result.exit_code == 0
    assert "orbit_library_path" in result.stdout


def test_cli_invalid_config_returns_2() -> None:
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "ingest",
            "--config",
            "does/not/exist.yaml",
        ],
    )

    assert result.exit_code == 2


def test_cli_invalid_backend_mode_returns_2(tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    data = load_yaml(base_config)
    data["backend"] = {"mode": "unknown"}
    bad_backend_config = tmp_path / "bad_backend.yaml"
    bad_backend_config.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "ingest",
            "--config",
            str(bad_backend_config),
        ],
    )

    assert result.exit_code == 2


def test_cli_llm_suggest_success(tmp_path: Path) -> None:
    runner = CliRunner()
    acceptance_pack = tmp_path / "acceptance_pack.json"
    acceptance_pack.write_text(
        """
{
  "schema_version": "llm-acceptance-pack/v1",
  "pack_id": "acceptance_demo",
  "created_at_utc": "2026-04-03T00:00:00Z",
  "eval_set_manifest_path": null,
  "thresholds": {
    "min_parse_success_rate": 0.8,
    "min_compile_success_rate": 0.8,
    "min_generation_success_rate": 0.3,
    "min_shortlist_pass_rate": 0.05,
    "min_validation_pass_rate": 0.02,
    "min_novelty_score_mean": 0.0,
    "min_synthesizability_mean": 0.5
  },
  "systems": [
    {
      "system": "Al-Cu-Fe",
      "generate_comparison_path": "data/benchmarks/llm_generate/al_cu_fe_comparison.json",
      "pipeline_comparison_path": "data/benchmarks/llm_pipeline/al_cu_fe_comparison.json",
      "parse_success_rate": 0.95,
      "compile_success_rate": 0.92,
      "generation_success_rate": 0.4,
      "shortlist_pass_rate": 0.12,
      "validation_pass_rate": 0.08,
      "novelty_score_mean": 0.2,
      "synthesizability_mean": 0.71,
      "report_release_gate_ready": true,
      "failing_metrics": [],
      "passed": true
    }
  ],
  "overall_passed": true
}
""".strip(),
        encoding="utf-8",
    )
    out_path = tmp_path / "custom" / "typed_suggestions.json"

    result = runner.invoke(
        app,
        [
            "llm-suggest",
            "--acceptance-pack",
            str(acceptance_pack),
            "--out",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert out_path.exists()
    stdout_payload = json.loads(result.stdout)
    written_payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert stdout_payload == written_payload
    assert stdout_payload["schema_version"] == "llm-campaign-suggestion/v1"
    assert stdout_payload["proposal_count"] == 1
    assert "items" not in stdout_payload
    proposal_path = Path(stdout_payload["proposals"][0]["proposal_path"])
    assert proposal_path.parent == tmp_path / "proposals"
    assert proposal_path.exists()


def test_cli_llm_approve_rejected_success(tmp_path: Path) -> None:
    runner = CliRunner()
    acceptance_pack_path = (
        tmp_path
        / "data"
        / "benchmarks"
        / "llm_acceptance"
        / "acceptance_demo"
        / "acceptance_pack.json"
    )
    acceptance_pack_path.parent.mkdir(parents=True, exist_ok=True)
    acceptance_pack_path.write_text("{}", encoding="utf-8")
    proposal_path = tmp_path / "data" / "benchmarks" / "llm_acceptance" / "acceptance_demo" / "proposals" / "acceptance_demo_al_cu_fe.json"
    proposal_path.parent.mkdir(parents=True, exist_ok=True)
    proposal_path.write_text(
        """
{
  "schema_version": "llm-campaign-proposal/v1",
  "proposal_id": "acceptance_demo_al_cu_fe",
  "pack_id": "acceptance_demo",
  "system": "Al-Cu-Fe",
  "generated_at_utc": "2026-04-04T00:00:00Z",
  "acceptance_pack_path": "__ACCEPTANCE_PACK_PATH__",
  "eval_set_manifest_path": "data/llm_eval_sets/eval_demo/manifest.json",
  "generate_comparison_path": "data/benchmarks/llm_generate/al_cu_fe_comparison.json",
  "pipeline_comparison_path": "data/benchmarks/llm_pipeline/al_cu_fe_comparison.json",
  "overall_status": "needs_improvement",
  "priority": "high",
  "failing_metrics": ["parse_success_rate"],
  "actions": [
    {
      "action_id": "acceptance_demo_al_cu_fe_action_01",
      "family": "prompt_conditioning",
      "title": "Tighten prompt validity conditioning",
      "rationale": "Parse reliability is below the acceptance threshold.",
      "priority": "high",
      "evidence_metrics": ["parse_success_rate"],
      "preferred_model_lane": "general_purpose",
      "prompt_conditioning": {
        "instruction_delta": "Emphasize parser-safe Zomic syntax.",
        "conditioning_strategy": "increase_exact_system_examples",
        "target_example_family": "acceptance_pack_exact_matches",
        "preferred_max_conditioning_examples": 6
      }
    }
  ]
}
""".replace("__ACCEPTANCE_PACK_PATH__", str(acceptance_pack_path)).strip(),
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "llm-approve",
            "--proposal",
            str(proposal_path),
            "--decision",
            "rejected",
            "--operator",
            "operator@example.com",
        ],
    )

    assert result.exit_code == 0
    stdout_payload = json.loads(result.stdout)
    assert stdout_payload["decision"] == "rejected"
    assert stdout_payload["campaign_spec_path"] is None
