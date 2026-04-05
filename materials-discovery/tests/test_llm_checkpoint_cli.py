from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _write_lineage_files(root: Path) -> None:
    (root / "lineage").mkdir(parents=True, exist_ok=True)
    for name in (
        "adapter_manifest.json",
        "corpus_manifest.json",
        "eval_manifest.json",
        "acceptance_pack.json",
    ):
        (root / "lineage" / name).write_text("{}", encoding="utf-8")


def _write_spec(
    root: Path,
    *,
    checkpoint_id: str = "ckpt-al-cu-fe-zomic-adapted",
    checkpoint_family: str | None = None,
) -> Path:
    spec = {
        "checkpoint_id": checkpoint_id,
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
    if checkpoint_family is not None:
        spec["checkpoint_family"] = checkpoint_family
    spec_path = root / f"{checkpoint_id}.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def _write_evidence_files(root: Path) -> list[str]:
    paths = [
        "reports/serving_benchmark.json",
        "reports/acceptance_eval.json",
    ]
    for relative_path in paths:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
    return paths


def _write_promotion_spec(
    root: Path,
    *,
    checkpoint_family: str,
    checkpoint_id: str,
    expected_revision: int,
    expected_promoted_checkpoint_id: str | None = None,
) -> Path:
    spec = {
        "checkpoint_family": checkpoint_family,
        "checkpoint_id": checkpoint_id,
        "evidence_paths": _write_evidence_files(root),
        "expected_revision": expected_revision,
    }
    if expected_promoted_checkpoint_id is not None:
        spec["expected_promoted_checkpoint_id"] = expected_promoted_checkpoint_id
    spec_path = root / f"{checkpoint_id}-promotion.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def _write_retirement_spec(
    root: Path,
    *,
    checkpoint_family: str,
    checkpoint_id: str,
    expected_revision: int,
) -> Path:
    spec = {
        "checkpoint_family": checkpoint_family,
        "checkpoint_id": checkpoint_id,
        "reason": "superseded",
        "expected_revision": expected_revision,
    }
    spec_path = root / f"{checkpoint_id}-retirement.yaml"
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


def test_llm_register_checkpoint_cli_family_registration_is_visible_in_list(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    _write_lineage_files(tmp_path)
    spec_path = _write_spec(
        tmp_path,
        checkpoint_family="adapted-al-cu-fe",
    )

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    register_result = runner.invoke(
        app,
        ["llm-register-checkpoint", "--spec", str(spec_path)],
    )
    list_result = runner.invoke(
        app,
        ["llm-list-checkpoints", "--checkpoint-family", "adapted-al-cu-fe"],
    )

    assert register_result.exit_code == 0
    assert list_result.exit_code == 0
    payload = json.loads(list_result.stdout)
    assert payload["checkpoint_family"] == "adapted-al-cu-fe"
    assert payload["revision"] == 1
    assert payload["members"] == [
        {
            "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
            "fingerprint": payload["members"][0]["fingerprint"],
            "lifecycle_state": "candidate",
            "promoted_at": None,
            "retired_at": None,
        }
    ]


def test_llm_promote_checkpoint_cli_updates_lifecycle_and_is_listed(monkeypatch, tmp_path: Path) -> None:
    runner = CliRunner()
    _write_lineage_files(tmp_path)
    first_spec = _write_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        checkpoint_family="adapted-al-cu-fe",
    )
    second_spec = _write_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-b",
        checkpoint_family="adapted-al-cu-fe",
    )

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    assert runner.invoke(app, ["llm-register-checkpoint", "--spec", str(first_spec)]).exit_code == 0
    assert runner.invoke(app, ["llm-register-checkpoint", "--spec", str(second_spec)]).exit_code == 0

    promote_result = runner.invoke(
        app,
        [
            "llm-promote-checkpoint",
            "--spec",
            str(
                _write_promotion_spec(
                    tmp_path,
                    checkpoint_family="adapted-al-cu-fe",
                    checkpoint_id="ckpt-al-cu-fe-zomic-a",
                    expected_revision=2,
                )
            ),
        ],
    )
    list_result = runner.invoke(
        app,
        ["llm-list-checkpoints", "--checkpoint-family", "adapted-al-cu-fe"],
    )

    assert promote_result.exit_code == 0
    promote_payload = json.loads(promote_result.stdout)
    assert promote_payload == {
        "checkpoint_family": "adapted-al-cu-fe",
        "checkpoint_id": "ckpt-al-cu-fe-zomic-a",
        "promoted_checkpoint_id": "ckpt-al-cu-fe-zomic-a",
        "revision": 3,
    }
    assert list_result.exit_code == 0
    listed_payload = json.loads(list_result.stdout)
    promoted_member = next(
        member
        for member in listed_payload["members"]
        if member["checkpoint_id"] == "ckpt-al-cu-fe-zomic-a"
    )
    assert promoted_member["lifecycle_state"] == "promoted"
    assert promoted_member["promoted_at"] is not None


def test_llm_promote_checkpoint_cli_returns_code_2_for_stale_revision(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    _write_lineage_files(tmp_path)
    first_spec = _write_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        checkpoint_family="adapted-al-cu-fe",
    )
    second_spec = _write_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-b",
        checkpoint_family="adapted-al-cu-fe",
    )

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    assert runner.invoke(app, ["llm-register-checkpoint", "--spec", str(first_spec)]).exit_code == 0
    assert runner.invoke(app, ["llm-register-checkpoint", "--spec", str(second_spec)]).exit_code == 0
    assert (
        runner.invoke(
            app,
            [
                "llm-promote-checkpoint",
                "--spec",
                str(
                    _write_promotion_spec(
                        tmp_path,
                        checkpoint_family="adapted-al-cu-fe",
                        checkpoint_id="ckpt-al-cu-fe-zomic-a",
                        expected_revision=2,
                    )
                ),
            ],
        ).exit_code
        == 0
    )

    result = runner.invoke(
        app,
        [
            "llm-promote-checkpoint",
            "--spec",
            str(
                _write_promotion_spec(
                    tmp_path,
                    checkpoint_family="adapted-al-cu-fe",
                    checkpoint_id="ckpt-al-cu-fe-zomic-b",
                    expected_revision=2,
                )
            ),
        ],
    )

    assert result.exit_code == 2
    assert "llm-promote-checkpoint failed:" in result.stderr
    assert "reload the current lifecycle revision and retry" in result.stderr


def test_llm_retire_checkpoint_cli_returns_code_2_for_unsafe_retirement(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    _write_lineage_files(tmp_path)
    first_spec = _write_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        checkpoint_family="adapted-al-cu-fe",
    )
    second_spec = _write_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-b",
        checkpoint_family="adapted-al-cu-fe",
    )

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    assert runner.invoke(app, ["llm-register-checkpoint", "--spec", str(first_spec)]).exit_code == 0
    assert runner.invoke(app, ["llm-register-checkpoint", "--spec", str(second_spec)]).exit_code == 0
    assert (
        runner.invoke(
            app,
            [
                "llm-promote-checkpoint",
                "--spec",
                str(
                    _write_promotion_spec(
                        tmp_path,
                        checkpoint_family="adapted-al-cu-fe",
                        checkpoint_id="ckpt-al-cu-fe-zomic-a",
                        expected_revision=2,
                    )
                ),
            ],
        ).exit_code
        == 0
    )

    result = runner.invoke(
        app,
        [
            "llm-retire-checkpoint",
            "--spec",
            str(
                _write_retirement_spec(
                    tmp_path,
                    checkpoint_family="adapted-al-cu-fe",
                    checkpoint_id="ckpt-al-cu-fe-zomic-a",
                    expected_revision=3,
                )
            ),
        ],
    )

    assert result.exit_code == 2
    assert "llm-retire-checkpoint failed:" in result.stderr
    assert "promote a different checkpoint first" in result.stderr


def test_committed_checkpoint_lifecycle_example_specs_validate_and_run_through_cli(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    _write_lineage_files(tmp_path)
    promotion_spec = _workspace() / "configs" / "llm" / "al_cu_fe_checkpoint_promotion.yaml"
    retirement_spec = _workspace() / "configs" / "llm" / "al_cu_fe_checkpoint_retirement.yaml"
    promotion_payload = yaml.safe_load(promotion_spec.read_text(encoding="utf-8"))
    retirement_payload = yaml.safe_load(retirement_spec.read_text(encoding="utf-8"))

    monkeypatch.setattr("materials_discovery.llm.checkpoints.workspace_root", lambda: tmp_path)
    monkeypatch.setattr("materials_discovery.llm.storage.workspace_root", lambda: tmp_path)

    assert promotion_payload["checkpoint_family"] == "adapted-al-cu-fe"
    assert retirement_payload["checkpoint_family"] == "adapted-al-cu-fe"
    assert "placeholder" in promotion_payload["note"].lower()
    assert "placeholder" in retirement_payload["note"].lower()

    assert (
        runner.invoke(
            app,
            [
                "llm-register-checkpoint",
                "--spec",
                str(
                    _write_spec(
                        tmp_path,
                        checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
                        checkpoint_family="adapted-al-cu-fe",
                    )
                ),
            ],
        ).exit_code
        == 0
    )
    assert (
        runner.invoke(
            app,
            [
                "llm-register-checkpoint",
                "--spec",
                str(
                    _write_spec(
                        tmp_path,
                        checkpoint_id="ckpt-al-cu-fe-zomic-adapted-legacy",
                        checkpoint_family="adapted-al-cu-fe",
                    )
                ),
            ],
        ).exit_code
        == 0
    )

    promote_result = runner.invoke(
        app,
        ["llm-promote-checkpoint", "--spec", str(promotion_spec)],
    )
    retire_result = runner.invoke(
        app,
        ["llm-retire-checkpoint", "--spec", str(retirement_spec)],
    )

    assert promote_result.exit_code == 0
    assert retire_result.exit_code == 0
    assert json.loads(promote_result.stdout)["revision"] == 3
    assert json.loads(retire_result.stdout)["revision"] == 4


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
