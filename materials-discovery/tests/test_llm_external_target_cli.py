from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app


def _write_snapshot(root: Path, name: str) -> tuple[Path, Path]:
    snapshot_dir = root / "snapshots" / name
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "config.json").write_text("{}", encoding="utf-8")
    (snapshot_dir / "tokenizer.json").write_text("{}", encoding="utf-8")
    manifest_path = snapshot_dir / "manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")
    return snapshot_dir, manifest_path


def _write_spec(
    root: Path,
    *,
    model_id: str = "crystallm_cif_v1",
    target_family: str = "cif",
) -> Path:
    snapshot_dir, manifest_path = _write_snapshot(root, name=model_id)
    spec = {
        "model_id": model_id,
        "model_family": "CrystaLLM",
        "supported_systems": ["Al-Cu-Fe"],
        "supported_target_families": [target_family],
        "runner_key": "transformers_causal_lm",
        "provider": "huggingface",
        "model": "lantunes/CrystaLLM-Example",
        "model_revision": "main-sha-1234",
        "tokenizer_revision": "tokenizer-sha-5678",
        "local_snapshot_path": str(snapshot_dir.relative_to(root)),
        "snapshot_manifest_path": str(manifest_path.relative_to(root)),
        "dtype": "bfloat16",
        "quantization": "4bit",
        "prompt_contract_id": (
            "translated_cif_v1"
            if target_family == "cif"
            else "crystaltextllm_material_string_v1"
        ),
        "response_parser_key": (
            "cif_text"
            if target_family == "cif"
            else "crystaltextllm_material_string"
        ),
        "notes": "fixture-backed external target",
    }
    spec_path = root / f"{model_id}.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def test_cli_llm_register_external_target_writes_registration_json(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    spec_path = _write_spec(tmp_path)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-register-external-target",
            "--spec",
            str(spec_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["model_id"] == "crystallm_cif_v1"
    assert payload["registration_path"].endswith("/registration.json")
    registration_path = (
        tmp_path / "data" / "llm_external_models" / "crystallm_cif_v1" / "registration.json"
    )
    assert registration_path.exists()


def test_cli_llm_inspect_external_target_prints_identity_and_artifact_trace(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    spec_path = _write_spec(tmp_path)
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    assert (
        runner.invoke(
            app,
            ["llm-register-external-target", "--spec", str(spec_path)],
        ).exit_code
        == 0
    )
    assert (
        runner.invoke(
            app,
            ["llm-smoke-external-target", "--model-id", "crystallm_cif_v1"],
        ).exit_code
        == 0
    )

    result = runner.invoke(
        app,
        [
            "llm-inspect-external-target",
            "--model-id",
            "crystallm_cif_v1",
        ],
    )

    assert result.exit_code == 0
    assert "Model ID: crystallm_cif_v1" in result.stdout
    assert "Target families: cif" in result.stdout
    assert "Environment artifact: data/llm_external_models/crystallm_cif_v1/environment.json" in result.stdout
    assert "Smoke artifact: data/llm_external_models/crystallm_cif_v1/smoke_check.json" in result.stdout
    assert "Smoke status: passed" in result.stdout


def test_cli_llm_smoke_external_target_prints_json_summary(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    spec_path = _write_spec(tmp_path, model_id="crystallm_material_string_v1", target_family="material_string")
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    assert (
        runner.invoke(
            app,
            ["llm-register-external-target", "--spec", str(spec_path)],
        ).exit_code
        == 0
    )

    result = runner.invoke(
        app,
        [
            "llm-smoke-external-target",
            "--model-id",
            "crystallm_material_string_v1",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["model_id"] == "crystallm_material_string_v1"
    assert payload["status"] == "passed"
    assert payload["environment_path"].endswith("/environment.json")
    smoke_path = (
        tmp_path
        / "data"
        / "llm_external_models"
        / "crystallm_material_string_v1"
        / "smoke_check.json"
    )
    assert smoke_path.exists()


def test_cli_llm_register_external_target_returns_code_2_for_missing_spec(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-register-external-target",
            "--spec",
            str(tmp_path / "missing-external-target.yaml"),
        ],
    )

    assert result.exit_code == 2
    assert "llm-register-external-target failed:" in result.stderr


def test_cli_llm_register_external_target_returns_code_2_for_invalid_contract(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    spec_path = tmp_path / "invalid.yaml"
    spec_path.write_text("model_id: broken_target\n", encoding="utf-8")
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-register-external-target",
            "--spec",
            str(spec_path),
        ],
    )

    assert result.exit_code == 2
    assert "llm-register-external-target failed:" in result.stderr


def test_cli_llm_inspect_external_target_returns_code_2_for_unknown_model_id(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-inspect-external-target",
            "--model-id",
            "missing_target",
        ],
    )

    assert result.exit_code == 2
    assert "llm-inspect-external-target failed:" in result.stderr


def test_cli_llm_smoke_external_target_returns_code_2_for_unknown_model_id(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        [
            "llm-smoke-external-target",
            "--model-id",
            "missing_target",
        ],
    )

    assert result.exit_code == 2
    assert "llm-smoke-external-target failed:" in result.stderr


def test_external_target_cli_commands_expose_help_surface() -> None:
    runner = CliRunner()

    command_expectations = {
        "llm-register-external-target": "--spec",
        "llm-inspect-external-target": "--model-id",
        "llm-smoke-external-target": "--model-id",
    }

    for command, expected_flag in command_expectations.items():
        result = runner.invoke(app, [command, "--help"])

        assert result.exit_code == 0
        assert expected_flag in result.stdout
