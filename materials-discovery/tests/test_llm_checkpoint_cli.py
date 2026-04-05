from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app


def _write_lineage_files(root: Path) -> None:
    (root / "lineage").mkdir(parents=True, exist_ok=True)
    for name in (
        "adapter_manifest.json",
        "corpus_manifest.json",
        "eval_manifest.json",
        "acceptance_pack.json",
    ):
        (root / "lineage" / name).write_text("{}", encoding="utf-8")


def _write_spec(root: Path) -> Path:
    spec = {
        "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
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
    }
    spec_path = root / "checkpoint.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def test_llm_register_checkpoint_cli_writes_registration(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    _write_lineage_files(tmp_path)
    spec_path = _write_spec(tmp_path)

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        ["llm-register-checkpoint", "--spec", str(spec_path)],
    )

    assert result.exit_code == 0
    registration_path = (
        tmp_path / "data" / "llm_checkpoints" / "ckpt-al-cu-fe-zomic-adapted" / "registration.json"
    )
    assert registration_path.exists()
    assert '"checkpoint_id":"ckpt-al-cu-fe-zomic-adapted"' in result.stdout


def test_llm_register_checkpoint_cli_returns_code_2_for_missing_lineage(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    spec_path = _write_spec(tmp_path)

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    result = runner.invoke(
        app,
        ["llm-register-checkpoint", "--spec", str(spec_path)],
    )

    assert result.exit_code == 2
    assert "llm-register-checkpoint failed:" in result.stderr
