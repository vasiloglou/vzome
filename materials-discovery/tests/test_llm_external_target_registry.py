from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from materials_discovery.llm import (
    capture_external_target_environment,
    load_registered_external_target,
    register_external_target,
    smoke_external_target,
)
from materials_discovery.llm.external_targets import load_external_target_spec
from materials_discovery.llm.schema import (
    LlmExternalTargetEnvironmentManifest,
    LlmExternalTargetRegistration,
    LlmExternalTargetSmokeCheck,
)
from materials_discovery.llm.storage import (
    llm_external_target_environment_path,
    llm_external_target_registration_path,
    llm_external_target_smoke_path,
)


def _write_snapshot(root: Path, name: str = "crystallm_snapshot") -> tuple[Path, Path]:
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
    model_revision: str = "main-sha-1234",
) -> Path:
    snapshot_dir, manifest_path = _write_snapshot(root, name=model_id)
    spec = {
        "model_id": model_id,
        "model_family": "CrystaLLM",
        "supported_systems": ["Al-Cu-Fe"],
        "supported_target_families": ["cif"],
        "runner_key": "transformers_causal_lm",
        "provider": "huggingface",
        "model": "lantunes/CrystaLLM-Example",
        "model_revision": model_revision,
        "tokenizer_revision": "tokenizer-sha-5678",
        "local_snapshot_path": str(snapshot_dir.relative_to(root)),
        "snapshot_manifest_path": str(manifest_path.relative_to(root)),
        "dtype": "bfloat16",
        "quantization": "4bit",
        "prompt_contract_id": "translated_cif_v1",
        "response_parser_key": "cif_text",
        "notes": "fixture-backed external target",
    }
    spec_path = root / f"{model_id}.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def test_register_external_target_writes_registration_and_fingerprint(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path)

    spec = load_external_target_spec(spec_path)
    summary = register_external_target(spec_path, root=tmp_path)
    registration, registration_path = load_registered_external_target(
        "crystallm_cif_v1",
        root=tmp_path,
    )

    assert summary.model_id == "crystallm_cif_v1"
    assert summary.fingerprint == registration.fingerprint
    assert registration_path == (
        tmp_path / "data" / "llm_external_models" / "crystallm_cif_v1" / "registration.json"
    )
    assert registration.local_snapshot_path == "snapshots/crystallm_cif_v1"
    assert registration.snapshot_manifest_path == "snapshots/crystallm_cif_v1/manifest.json"
    assert registration.supported_target_families == spec.supported_target_families


def test_register_external_target_rejects_missing_snapshot_inputs(tmp_path: Path) -> None:
    spec_path = tmp_path / "missing.yaml"
    spec_path.write_text(
        yaml.safe_dump(
            {
                "model_id": "missing_target",
                "model_family": "CrystaLLM",
                "supported_target_families": ["cif"],
                "runner_key": "transformers_causal_lm",
                "provider": "huggingface",
                "model": "lantunes/CrystaLLM-Example",
                "model_revision": "main-sha-1234",
                "local_snapshot_path": "snapshots/missing_target",
                "prompt_contract_id": "translated_cif_v1",
                "response_parser_key": "cif_text",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="local snapshot"):
        register_external_target(spec_path, root=tmp_path)


def test_register_external_target_is_idempotent_but_rejects_conflicting_fingerprints(
    tmp_path: Path,
) -> None:
    spec_path = _write_spec(tmp_path)
    register_external_target(spec_path, root=tmp_path)

    summary = register_external_target(spec_path, root=tmp_path)
    assert summary.model_id == "crystallm_cif_v1"

    conflicting_spec_path = _write_spec(
        tmp_path,
        model_id="crystallm_cif_v1",
        model_revision="changed-sha-9999",
    )
    with pytest.raises(ValueError, match="different fingerprint"):
        register_external_target(conflicting_spec_path, root=tmp_path)


def test_capture_external_target_environment_writes_environment_manifest(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path)
    register_external_target(spec_path, root=tmp_path)
    registration, _ = load_registered_external_target("crystallm_cif_v1", root=tmp_path)

    manifest = capture_external_target_environment(registration, root=tmp_path)
    environment_path = llm_external_target_environment_path("crystallm_cif_v1", root=tmp_path)

    assert environment_path.exists()
    stored = LlmExternalTargetEnvironmentManifest.model_validate(
        json.loads(environment_path.read_text(encoding="utf-8"))
    )
    assert manifest.model_id == "crystallm_cif_v1"
    assert stored.registration_fingerprint == registration.fingerprint
    assert stored.local_snapshot_path == registration.local_snapshot_path
    assert "pydantic" in stored.package_versions


def test_smoke_external_target_persists_passed_and_failed_results(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path)
    register_external_target(spec_path, root=tmp_path)

    passed = smoke_external_target("crystallm_cif_v1", root=tmp_path)
    smoke_path = llm_external_target_smoke_path("crystallm_cif_v1", root=tmp_path)

    assert passed.status == "passed"
    assert smoke_path.exists()
    stored_pass = LlmExternalTargetSmokeCheck.model_validate(
        json.loads(smoke_path.read_text(encoding="utf-8"))
    )
    assert stored_pass.status == "passed"
    assert stored_pass.environment_path == "data/llm_external_models/crystallm_cif_v1/environment.json"

    snapshot_dir = tmp_path / "snapshots" / "crystallm_cif_v1"
    for path in snapshot_dir.iterdir():
        path.unlink()
    snapshot_dir.rmdir()

    failed = smoke_external_target("crystallm_cif_v1", root=tmp_path)
    assert failed.status == "failed"
    assert "local snapshot not found" in (failed.detail or "")


def test_load_registered_external_target_raises_for_missing_model_id(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="external target registration 'unknown_target'"):
        load_registered_external_target("unknown_target", root=tmp_path)


def test_registration_artifact_round_trips_through_typed_model(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path)
    register_external_target(spec_path, root=tmp_path)
    registration_path = llm_external_target_registration_path("crystallm_cif_v1", root=tmp_path)

    registration = LlmExternalTargetRegistration.model_validate(
        json.loads(registration_path.read_text(encoding="utf-8"))
    )
    assert registration.model_id == "crystallm_cif_v1"
    assert registration.registration_path == "data/llm_external_models/crystallm_cif_v1/registration.json"
