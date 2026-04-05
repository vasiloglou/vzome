from __future__ import annotations

import json
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
from materials_discovery.llm.schema import LlmServingIdentity


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

    captured: dict[str, object] = {}

    def _fake_evaluate(system_config, output_path, batch="all", **kwargs):
        captured["requested_model_lane"] = kwargs.get("requested_model_lane")
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
            "requested_model_lanes": ["specialized_materials"],
            "resolved_model_lane": "specialized_materials",
            "resolved_model_lane_source": "configured_lane",
            "serving_identity": {
                "requested_model_lane": "specialized_materials",
                "resolved_model_lane": "specialized_materials",
                "resolved_model_lane_source": "configured_lane",
                "adapter": "openai_compat_v1",
                "provider": "openai_compat",
                "model": "materials-al-cu-fe-specialist-v1",
                "effective_api_base": "http://localhost:8000",
            },
        }
        write_jsonl([candidate.model_dump(mode="json")], output_path)
        return LlmEvaluateSummary(
            input_count=1,
            assessed_count=1,
            failed_count=0,
            output_path=str(output_path),
            requested_model_lanes=["specialized_materials"],
            resolved_model_lane="specialized_materials",
            resolved_model_lane_source="configured_lane",
            serving_identity=LlmServingIdentity(
                requested_model_lane="specialized_materials",
                resolved_model_lane="specialized_materials",
                resolved_model_lane_source="configured_lane",
                adapter="openai_compat_v1",
                provider="openai_compat",
                model="materials-al-cu-fe-specialist-v1",
                effective_api_base="http://localhost:8000",
            ),
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
            "--model-lane",
            "specialized_materials",
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0
    assert out_file.exists()
    assert captured["requested_model_lane"] == "specialized_materials"
    assert '"assessed_count":1' in result.stdout
    assert '"resolved_model_lane":"specialized_materials"' in result.stdout


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


def test_cli_llm_evaluate_uses_configured_lane_and_records_explicit_fallback(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_data = load_yaml(workspace / "configs" / "systems" / "al_cu_fe_llm_local.yaml")
    config_data["llm_generate"]["model_lanes"] = {
        "general_purpose": config_data["llm_generate"]["model_lanes"]["general_purpose"]
    }
    config_data["llm_generate"]["fallback_model_lane"] = "general_purpose"
    config_path = tmp_path / "al_cu_fe_llm_eval_fallback.yaml"
    config_path.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")

    ranked_path = tmp_path / "data" / "ranked" / "al_cu_fe_ranked.jsonl"
    out_file = tmp_path / "data" / "llm_evaluated" / "al_cu_fe_all_llm_evaluated.jsonl"
    write_jsonl([_candidate().model_dump(mode="json")], ranked_path)

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.evaluate.workspace_root", lambda: tmp_path)

    class _FakeAdapter:
        def generate(self, request) -> str:
            del request
            return (
                "{\"synthesizability_score\":0.73,\"precursor_hints\":[],"
                "\"anomaly_flags\":[],\"literature_context\":\"demo\","
                "\"rationale\":\"fallback ok\"}"
            )

    monkeypatch.setattr(
        "materials_discovery.llm.evaluate.resolve_llm_adapter",
        lambda mode, backend=None: _FakeAdapter(),
    )
    monkeypatch.setattr(
        "materials_discovery.llm.evaluate.validate_llm_adapter_ready",
        lambda adapter, **kwargs: None,
    )

    result = runner.invoke(
        app,
        [
            "llm-evaluate",
            "--config",
            str(config_path),
            "--out",
            str(out_file),
        ],
    )

    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["requested_model_lanes"] == ["specialized_materials"]
    assert payload["resolved_model_lane"] == "general_purpose"
    assert payload["resolved_model_lane_source"] == "configured_fallback"


def test_cli_llm_evaluate_fails_requested_unavailable_lane_before_provider(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_data = load_yaml(workspace / "configs" / "systems" / "al_cu_fe_llm_local.yaml")
    config_data["llm_generate"]["model_lanes"] = {
        "general_purpose": config_data["llm_generate"]["model_lanes"]["general_purpose"]
    }
    config_data["llm_generate"]["fallback_model_lane"] = None
    config_data["llm_evaluate"]["model_lane"] = None
    config_path = tmp_path / "al_cu_fe_llm_eval_missing_lane.yaml"
    config_path.write_text(yaml.safe_dump(config_data, sort_keys=False), encoding="utf-8")

    ranked_path = tmp_path / "data" / "ranked" / "al_cu_fe_ranked.jsonl"
    write_jsonl([_candidate().model_dump(mode="json")], ranked_path)

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.evaluate.workspace_root", lambda: tmp_path)
    generate_calls = {"count": 0}

    def _should_not_resolve(*args, **kwargs):
        del args, kwargs
        generate_calls["count"] += 1
        raise AssertionError("provider should not be resolved when lane selection fails")

    monkeypatch.setattr("materials_discovery.llm.evaluate.resolve_llm_adapter", _should_not_resolve)

    result = runner.invoke(
        app,
        [
            "llm-evaluate",
            "--config",
            str(config_path),
            "--model-lane",
            "specialized_materials",
        ],
    )

    assert result.exit_code == 2
    assert "requested model lane 'specialized_materials' is not configured" in result.stderr
    assert generate_calls["count"] == 0
