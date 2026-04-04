from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml, write_jsonl
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    LlmEvaluateSummary,
    SiteRecord,
)


def _candidate() -> CandidateRecord:
    return CandidateRecord(
        candidate_id="md_eval_cli_0001",
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        cell={"a": 14.2, "b": 14.2, "c": 14.2, "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
        sites=[
            SiteRecord(
                label="S01",
                qphi=((0, 0), (1, 0), (1, 0)),
                species="Al",
                occ=1.0,
                fractional_position=(0.2, 0.2, 0.2),
                cartesian_position=(2.84, 2.84, 2.84),
            ),
            SiteRecord(
                label="S02",
                qphi=((1, 0), (0, 0), (1, 0)),
                species="Cu",
                occ=1.0,
                fractional_position=(0.7, 0.7, 0.7),
                cartesian_position=(9.94, 9.94, 9.94),
            ),
        ],
        composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        screen={"model": "MACE"},
        digital_validation=DigitalValidationRecord(status="passed", passed_checks=True),
        provenance={"source": "llm"},
    )


def test_cli_llm_evaluate_success(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    config_data = load_yaml(base_config)
    config_data["llm_evaluate"] = {
        "prompt_template": "materials_assess_v1",
        "temperature": 0.1,
        "max_tokens": 512,
        "fixture_outputs": [
            "{\"synthesizability_score\":0.8,\"precursor_hints\":[\"Al powder\"],\"anomaly_flags\":[],\"literature_context\":\"demo\",\"rationale\":\"demo\"}"
        ],
    }
    config_path = tmp_path / "al_cu_fe_llm_eval.yaml"
    config_path.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")

    out_file = tmp_path / "llm_evaluated.jsonl"
    run_manifest = tmp_path / "run_manifest.json"
    run_manifest.write_text("{}", encoding="utf-8")

    def _fake_evaluate(system_config, output_path, batch="all", **kwargs):
        del system_config, batch, kwargs
        candidate = _candidate().model_copy(deep=True)
        candidate.provenance["llm_assessment"] = {
            "status": "passed",
            "synthesizability_score": 0.8,
            "precursor_hints": ["Al powder"],
            "anomaly_flags": [],
            "literature_context": "demo",
            "rationale": "demo",
            "run_id": "demo",
            "error_kind": None,
            "error_message": None,
        }
        write_jsonl([candidate.model_dump(mode="json")], output_path)
        return LlmEvaluateSummary(
            input_count=1,
            assessed_count=1,
            failed_count=0,
            output_path=str(output_path),
            run_manifest_path=str(run_manifest),
        )

    monkeypatch.setattr("materials_discovery.cli.evaluate_llm_candidates", _fake_evaluate)

    result = runner.invoke(
        app,
        [
            "llm-evaluate",
            "--config",
            str(config_path),
            "--batch",
            "top1",
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()
    assert '"assessed_count":1' in result.stdout


def test_cli_llm_evaluate_returns_code_2_when_config_is_missing_section() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    result = runner.invoke(
        app,
        [
            "llm-evaluate",
            "--config",
            str(config),
        ],
    )

    assert result.exit_code == 2
