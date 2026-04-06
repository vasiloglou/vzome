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
from materials_discovery.llm.checkpoints import promote_checkpoint, register_llm_checkpoint
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


def test_cli_llm_generate_uses_registered_checkpoint_lineage_for_adapted_lane(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    lineage_dir = tmp_path / "lineage"
    lineage_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "adapter_manifest.json",
        "corpus_manifest.json",
        "eval_manifest.json",
        "acceptance_pack.json",
    ):
        (lineage_dir / name).write_text("{}", encoding="utf-8")

    checkpoint_spec = tmp_path / "checkpoint.yaml"
    checkpoint_spec.write_text(
        yaml.safe_dump(
            {
                "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
                "checkpoint_family": "adapted-al-cu-fe",
                "system": "Al-Cu-Fe",
                "template_family": "icosahedral_approximant_1_1",
                "adapter": "openai_compat_v1",
                "provider": "openai_compat",
                "model": "zomic-adapted-local-v1",
                "local_model_path": "/opt/models/zomic-adapted-local-v1",
                "model_revision": "adapted-dev-2026-04-05",
                "base_model": "zomic-general-local-v1",
                "base_model_revision": "local-dev-2026-04-05",
                "adaptation_method": "lora",
                "adaptation_artifact_path": "lineage/adapter_manifest.json",
                "corpus_manifest_path": "lineage/corpus_manifest.json",
                "eval_set_manifest_path": "lineage/eval_manifest.json",
                "acceptance_pack_path": "lineage/acceptance_pack.json",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    register_llm_checkpoint(checkpoint_spec, root=tmp_path)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "serving_benchmark.json").write_text("{}", encoding="utf-8")
    promotion_spec = tmp_path / "checkpoint-promotion.yaml"
    promotion_spec.write_text(
        yaml.safe_dump(
            {
                "checkpoint_family": "adapted-al-cu-fe",
                "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
                "evidence_paths": ["reports/serving_benchmark.json"],
                "expected_revision": 1,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    promote_checkpoint(promotion_spec, root=tmp_path)

    config_path = tmp_path / "al_cu_fe_llm_adapted.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "system_name": "Al-Cu-Fe",
                "template_family": "icosahedral_approximant_1_1",
                "species": ["Al", "Cu", "Fe"],
                "composition_bounds": {
                    "Al": {"min": 0.6, "max": 0.8},
                    "Cu": {"min": 0.1, "max": 0.25},
                    "Fe": {"min": 0.05, "max": 0.2},
                },
                "coeff_bounds": {"min": -3, "max": 3},
                "seed": 17,
                "default_count": 5,
                "backend": {
                    "mode": "real",
                    "llm_adapter": "openai_compat_v1",
                    "llm_provider": "openai_compat",
                    "llm_model": "zomic-general-local-v1",
                    "llm_api_base": "http://localhost:8000",
                },
                "llm_generate": {
                    "prompt_template": "zomic_generate_v1",
                    "temperature": 0.2,
                    "max_tokens": 1024,
                    "max_attempts": 2,
                    "default_model_lane": "general_purpose",
                    "model_lanes": {
                        "general_purpose": {
                            "adapter": "openai_compat_v1",
                            "provider": "openai_compat",
                            "model": "zomic-adapted-local-v1",
                            "api_base": "http://localhost:8000",
                            "checkpoint_family": "adapted-al-cu-fe",
                            "require_checkpoint_registration": True,
                        }
                    },
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    out_file = tmp_path / "llm_adapted.jsonl"
    run_manifest = tmp_path / "run_manifest.json"
    run_manifest.write_text("{}", encoding="utf-8")

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    class _Adapter:
        pass

    monkeypatch.setattr("materials_discovery.cli.resolve_llm_adapter", lambda *args, **kwargs: _Adapter())
    monkeypatch.setattr("materials_discovery.cli.validate_llm_adapter_ready", lambda *args, **kwargs: None)

    def _fake_generate(system_config, output_path, count, **kwargs):
        del count
        assert system_config.backend.llm_model == "zomic-adapted-local-v1"
        serving_identity = kwargs["serving_identity"]
        assert serving_identity.checkpoint_id == "ckpt-al-cu-fe-zomic-adapted"
        assert serving_identity.model_revision == "adapted-dev-2026-04-05"
        assert serving_identity.local_model_path == "/opt/models/zomic-adapted-local-v1"
        assert serving_identity.checkpoint_lineage is not None
        assert serving_identity.checkpoint_lineage.checkpoint_family == "adapted-al-cu-fe"
        assert serving_identity.checkpoint_lineage.base_model == "zomic-general-local-v1"
        assert serving_identity.checkpoint_selection_source == "family_promoted_default"
        assert serving_identity.checkpoint_lifecycle_path == (
            "data/llm_checkpoints/families/adapted-al-cu-fe/lifecycle.json"
        )
        assert serving_identity.checkpoint_lifecycle_revision == 2
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
