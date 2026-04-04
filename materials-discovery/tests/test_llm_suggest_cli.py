from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_json_object


def _write_acceptance_pack(path: Path) -> None:
    payload = {
        "schema_version": "llm-acceptance-pack/v1",
        "pack_id": "acceptance_demo",
        "created_at_utc": "2026-04-04T00:00:00Z",
        "eval_set_manifest_path": "data/llm_eval_sets/eval_demo/manifest.json",
        "thresholds": {
            "min_parse_success_rate": 0.8,
            "min_compile_success_rate": 0.8,
            "min_generation_success_rate": 0.3,
            "min_shortlist_pass_rate": 0.05,
            "min_validation_pass_rate": 0.02,
            "min_novelty_score_mean": 0.0,
            "min_synthesizability_mean": 0.5,
        },
        "systems": [
            {
                "system": "Al-Cu-Fe",
                "generate_comparison_path": "data/benchmarks/llm_generate/al_cu_fe_comparison.json",
                "pipeline_comparison_path": "data/benchmarks/llm_pipeline/al_cu_fe_comparison.json",
                "parse_success_rate": 0.45,
                "compile_success_rate": 0.40,
                "generation_success_rate": 0.4,
                "shortlist_pass_rate": 0.12,
                "validation_pass_rate": 0.08,
                "novelty_score_mean": 0.2,
                "synthesizability_mean": 0.71,
                "report_release_gate_ready": False,
                "failing_metrics": [
                    "parse_success_rate",
                    "compile_success_rate",
                ],
                "passed": False,
            }
        ],
        "overall_passed": False,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_llm_suggest_writes_bundle_and_per_system_proposals_by_default(tmp_path: Path) -> None:
    runner = CliRunner()
    acceptance_pack = tmp_path / "acceptance_pack.json"
    _write_acceptance_pack(acceptance_pack)

    result = runner.invoke(
        app,
        [
            "llm-suggest",
            "--acceptance-pack",
            str(acceptance_pack),
        ],
    )

    assert result.exit_code == 0
    stdout_payload = json.loads(result.stdout)
    assert stdout_payload["schema_version"] == "llm-campaign-suggestion/v1"
    assert stdout_payload["proposal_count"] == 1
    assert "items" not in stdout_payload

    suggestion_path = tmp_path / "suggestions.json"
    assert suggestion_path.exists()
    assert load_json_object(suggestion_path) == stdout_payload

    proposal_path = Path(stdout_payload["proposals"][0]["proposal_path"])
    assert proposal_path == tmp_path / "proposals" / "acceptance_demo_al_cu_fe.json"
    assert proposal_path.exists()
    proposal_payload = load_json_object(proposal_path)
    assert proposal_payload["schema_version"] == "llm-campaign-proposal/v1"
    assert proposal_payload["actions"][0]["family"] == "prompt_conditioning"


def test_llm_suggest_invalid_input_exits_2_with_clear_error(tmp_path: Path) -> None:
    runner = CliRunner()
    acceptance_pack = tmp_path / "acceptance_pack.json"
    acceptance_pack.write_text("{}", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "llm-suggest",
            "--acceptance-pack",
            str(acceptance_pack),
        ],
    )

    assert result.exit_code == 2
    assert "llm-suggest failed" in result.output
