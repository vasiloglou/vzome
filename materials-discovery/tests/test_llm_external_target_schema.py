from __future__ import annotations

from typing import get_args

import pytest

from materials_discovery.llm import (
    LlmExternalTargetEnvironmentManifest,
    LlmExternalTargetRegistration,
    LlmExternalTargetRegistrationSpec,
    LlmExternalTargetRegistrationSummary,
    LlmExternalTargetRunnerKey,
    LlmExternalTargetSmokeCheck,
    LlmExternalTargetSmokeStatus,
)
from materials_discovery.llm.storage import (
    llm_checkpoint_dir,
    llm_external_target_dir,
    llm_external_target_environment_path,
    llm_external_target_registration_path,
    llm_external_target_smoke_path,
)


def _valid_spec_kwargs() -> dict[str, object]:
    return {
        "model_id": "crystallm_cif_v1",
        "model_family": "CrystaLLM",
        "supported_systems": [" Al-Cu-Fe ", "Sc-Zn", "Al-Cu-Fe"],
        "supported_target_families": ["cif"],
        "runner_key": "transformers_causal_lm",
        "provider": "huggingface",
        "model": "lantunes/CrystaLLM-Example",
        "model_revision": "main-sha-1234",
        "tokenizer_revision": " tokenizer-sha-5678 ",
        "local_snapshot_path": "/opt/models/crystallm-cif-v1",
        "snapshot_manifest_path": "data/llm_external_models/crystallm_cif_v1/snapshot_manifest.json",
        "dtype": "bfloat16",
        "quantization": "4bit",
        "prompt_contract_id": "translated_cif_v1",
        "response_parser_key": "cif_text",
        "notes": "  CIF-first benchmark target  ",
    }


def _valid_registration_kwargs() -> dict[str, object]:
    return {
        **_valid_spec_kwargs(),
        "supported_systems": ["Al-Cu-Fe", "Sc-Zn"],
        "tokenizer_revision": "tokenizer-sha-5678",
        "created_at_utc": "2026-04-07T06:59:00Z",
        "fingerprint": "deadbeefcafe1234",
        "registration_path": "data/llm_external_models/crystallm_cif_v1/registration.json",
        "environment_path": "data/llm_external_models/crystallm_cif_v1/environment.json",
        "smoke_check_path": "data/llm_external_models/crystallm_cif_v1/smoke_check.json",
        "notes": "CIF-first benchmark target",
    }


def _valid_environment_kwargs() -> dict[str, object]:
    return {
        "model_id": "crystallm_cif_v1",
        "registration_fingerprint": "deadbeefcafe1234",
        "captured_at_utc": "2026-04-07T06:59:30Z",
        "python_version": "3.11.11",
        "platform_system": "Darwin",
        "platform_release": "24.4.0",
        "platform_machine": "arm64",
        "package_versions": {
            " torch ": " 2.7.1 ",
            "transformers": "4.51.0",
        },
        "cuda_available": False,
        "gpu_count": 0,
        "visible_devices": "cpu-only",
        "local_snapshot_path": "/opt/models/crystallm-cif-v1",
        "snapshot_manifest_path": "data/llm_external_models/crystallm_cif_v1/snapshot_manifest.json",
        "tokenizer_revision": "tokenizer-sha-5678",
        "model_revision": "main-sha-1234",
    }


def _valid_smoke_kwargs() -> dict[str, object]:
    return {
        "model_id": "crystallm_cif_v1",
        "status": "passed",
        "registration_fingerprint": "deadbeefcafe1234",
        "checked_at_utc": "2026-04-07T07:00:00Z",
        "latency_s": 0.42,
        "environment_path": "data/llm_external_models/crystallm_cif_v1/environment.json",
        "runner_key": "transformers_causal_lm",
        "provider": "huggingface",
        "model": "lantunes/CrystaLLM-Example",
        "model_revision": "main-sha-1234",
        "local_snapshot_path": "/opt/models/crystallm-cif-v1",
        "detail": "tokenizer and config resolved successfully",
    }


def test_external_target_registration_spec_rejects_blank_ids_and_empty_target_families() -> None:
    with pytest.raises(ValueError, match="field must not be blank"):
        LlmExternalTargetRegistrationSpec(**{**_valid_spec_kwargs(), "model_id": " "})

    with pytest.raises(ValueError, match="must not be empty"):
        LlmExternalTargetRegistrationSpec(
            **{**_valid_spec_kwargs(), "supported_target_families": []}
        )

    with pytest.raises(ValueError, match="field must not be blank"):
        LlmExternalTargetRegistrationSpec(**{**_valid_spec_kwargs(), "model_revision": " "})


def test_external_target_registration_spec_exposes_explicit_identity_and_compatibility_fields() -> None:
    spec = LlmExternalTargetRegistrationSpec(**_valid_spec_kwargs())

    assert spec.model_id == "crystallm_cif_v1"
    assert spec.model_family == "CrystaLLM"
    assert spec.supported_systems == ["Al-Cu-Fe", "Sc-Zn"]
    assert spec.supported_target_families == ["cif"]
    assert spec.runner_key == "transformers_causal_lm"
    assert spec.provider == "huggingface"
    assert spec.model_revision == "main-sha-1234"
    assert spec.tokenizer_revision == "tokenizer-sha-5678"
    assert spec.prompt_contract_id == "translated_cif_v1"
    assert spec.response_parser_key == "cif_text"
    assert spec.notes == "CIF-first benchmark target"


def test_external_target_registration_carries_fingerprint_and_artifact_paths() -> None:
    registration = LlmExternalTargetRegistration(**_valid_registration_kwargs())
    summary = LlmExternalTargetRegistrationSummary(
        model_id=registration.model_id,
        fingerprint=registration.fingerprint,
        registration_path=registration.registration_path,
    )

    assert registration.fingerprint == "deadbeefcafe1234"
    assert registration.registration_path.endswith("registration.json")
    assert registration.environment_path.endswith("environment.json")
    assert registration.smoke_check_path.endswith("smoke_check.json")
    assert registration.runner_key == "transformers_causal_lm"
    assert registration.supported_target_families == ["cif"]
    assert summary.model_id == "crystallm_cif_v1"
    assert summary.registration_path.endswith("registration.json")


def test_external_target_environment_manifest_carries_reproducibility_fields() -> None:
    manifest = LlmExternalTargetEnvironmentManifest(**_valid_environment_kwargs())

    assert manifest.model_id == "crystallm_cif_v1"
    assert manifest.registration_fingerprint == "deadbeefcafe1234"
    assert manifest.python_version == "3.11.11"
    assert manifest.package_versions == {"torch": "2.7.1", "transformers": "4.51.0"}
    assert manifest.gpu_count == 0
    assert manifest.local_snapshot_path == "/opt/models/crystallm-cif-v1"
    assert manifest.model_revision == "main-sha-1234"

    with pytest.raises(ValueError, match="gpu_count must be >= 0"):
        LlmExternalTargetEnvironmentManifest(**{**_valid_environment_kwargs(), "gpu_count": -1})


def test_external_target_smoke_check_uses_typed_status_and_latency() -> None:
    smoke = LlmExternalTargetSmokeCheck(**_valid_smoke_kwargs())

    assert smoke.status == "passed"
    assert smoke.runner_key == "transformers_causal_lm"
    assert smoke.environment_path.endswith("environment.json")
    assert smoke.detail == "tokenizer and config resolved successfully"

    with pytest.raises(ValueError, match="latency_s must be >= 0"):
        LlmExternalTargetSmokeCheck(**{**_valid_smoke_kwargs(), "latency_s": -0.01})


def test_external_target_vocabularies_are_typed_and_stable() -> None:
    assert set(get_args(LlmExternalTargetRunnerKey)) == {
        "transformers_causal_lm",
        "peft_causal_lm",
    }
    assert set(get_args(LlmExternalTargetSmokeStatus)) == {"passed", "failed"}


def test_external_target_storage_helpers_use_dedicated_model_root(tmp_path) -> None:
    model_id = "crystallm_cif_v1"
    model_dir = llm_external_target_dir(model_id, root=tmp_path)

    assert model_dir == tmp_path / "data" / "llm_external_models" / model_id
    assert llm_external_target_registration_path(model_id, root=tmp_path) == (
        model_dir / "registration.json"
    )
    assert llm_external_target_environment_path(model_id, root=tmp_path) == (
        model_dir / "environment.json"
    )
    assert llm_external_target_smoke_path(model_id, root=tmp_path) == (
        model_dir / "smoke_check.json"
    )
    assert model_dir != llm_checkpoint_dir(model_id, root=tmp_path)


def test_external_target_storage_helpers_reject_blank_model_ids(tmp_path) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        llm_external_target_dir(" ", root=tmp_path)
