from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml, write_jsonl
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    LlmGenerateSummary,
    SiteRecord,
)
from materials_discovery.llm.schema import LlmServingIdentity


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


def test_cli_llm_generate_passes_optional_example_pack_config(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    config_data = load_yaml(base_config)
    config_data["llm_generate"]["example_pack_path"] = "data/llm_eval_sets/demo/eval_set.jsonl"
    config_path = tmp_path / "al_cu_fe_llm_conditioned.yaml"
    config_path.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")

    out_file = tmp_path / "llm_conditioned.jsonl"
    run_manifest = tmp_path / "run_manifest.json"
    run_manifest.write_text("{}", encoding="utf-8")

    def _fake_generate(system_config, output_path, count, **kwargs):
        del count
        assert system_config.llm_generate is not None
        assert system_config.llm_generate.example_pack_path == "data/llm_eval_sets/demo/eval_set.jsonl"
        assert kwargs["config_path"] == config_path
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
            str(config_path),
            "--count",
            "1",
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()


def test_cli_llm_generate_model_lane_overrides_default_and_records_serving_identity(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    base_config = workspace / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    config_data = load_yaml(base_config)
    config_data["backend"] = {"mode": "real"}
    config_data["llm_generate"]["default_model_lane"] = "general_purpose"
    config_data["llm_generate"]["model_lanes"] = {
        "general_purpose": {
            "adapter": "llm_fixture_v1",
            "provider": "mock",
            "model": "fixture-zomic-v1",
        },
        "specialized_materials": {
            "adapter": "openai_compat_v1",
            "provider": "openai_compat",
            "model": "materials-local-v1",
            "api_base": "http://localhost:8000",
            "checkpoint_id": "ckpt-123",
        },
    }
    config_path = tmp_path / "al_cu_fe_llm_local.yaml"
    config_path.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")

    out_file = tmp_path / "llm_local.jsonl"
    run_manifest = tmp_path / "run_manifest.json"
    run_manifest.write_text("{}", encoding="utf-8")
    ready_calls: list[tuple[str | None, str | None]] = []

    class _Adapter:
        pass

    monkeypatch.setattr("materials_discovery.cli.resolve_llm_adapter", lambda *args, **kwargs: _Adapter())

    def _fake_ready(adapter, *, adapter_key, requested_lane=None, resolved_lane=None):
        del adapter
        ready_calls.append((requested_lane, resolved_lane))
        assert adapter_key == "openai_compat_v1"

    def _fake_generate(system_config, output_path, count, **kwargs):
        del count
        assert system_config.backend.llm_adapter == "openai_compat_v1"
        assert system_config.backend.llm_model == "materials-local-v1"
        assert system_config.backend.llm_api_base == "http://localhost:8000"
        serving_identity = kwargs["serving_identity"]
        assert isinstance(serving_identity, LlmServingIdentity)
        assert serving_identity.requested_model_lane == "specialized_materials"
        assert serving_identity.resolved_model_lane == "specialized_materials"
        assert serving_identity.checkpoint_id == "ckpt-123"
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

    monkeypatch.setattr("materials_discovery.cli.validate_llm_adapter_ready", _fake_ready)
    monkeypatch.setattr("materials_discovery.cli.generate_llm_candidates", _fake_generate)

    result = runner.invoke(
        app,
        [
            "llm-generate",
            "--config",
            str(config_path),
            "--count",
            "1",
            "--model-lane",
            "specialized_materials",
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()
    assert ready_calls == [("specialized_materials", "specialized_materials")]
