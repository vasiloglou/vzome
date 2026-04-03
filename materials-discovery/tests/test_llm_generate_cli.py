from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import write_jsonl
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    LlmGenerateSummary,
    SiteRecord,
)


def _candidate() -> CandidateRecord:
    return CandidateRecord(
        candidate_id="md_000001",
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        cell={"a": 14.2, "b": 14.2, "c": 14.2, "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
        sites=[
            SiteRecord(
                label="S01",
                qphi=((0, 0), (1, 0), (2, 0)),
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
        composition={"Al": 0.5, "Cu": 0.5},
        screen={"model": "MACE"},
        digital_validation=DigitalValidationRecord(status="pending"),
        provenance={"source": "llm"},
    )


def test_cli_llm_generate_success(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    out_file = tmp_path / "llm_generated.jsonl"
    run_manifest = tmp_path / "run_manifest.json"
    run_manifest.write_text("{}", encoding="utf-8")

    def _fake_generate(system_config, output_path, count, **kwargs):
        del system_config, count, kwargs
        write_jsonl([_candidate().model_dump(mode="json")], output_path)
        return LlmGenerateSummary(
            requested_count=1,
            generated_count=1,
            attempt_count=1,
            parse_pass_count=1,
            compile_pass_count=1,
            output_path=str(output_path),
            run_manifest_path=str(run_manifest),
        )

    monkeypatch.setattr("materials_discovery.cli.generate_llm_candidates", _fake_generate)

    result = runner.invoke(
        app,
        [
            "llm-generate",
            "--config",
            str(config),
            "--count",
            "1",
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()
    assert '"generated_count":1' in result.stdout


def test_cli_llm_generate_returns_code_2_when_config_is_missing_llm_section() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    result = runner.invoke(
        app,
        [
            "llm-generate",
            "--config",
            str(config),
            "--count",
            "1",
        ],
    )

    assert result.exit_code == 2
