from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import LlmGenerateSummary, SystemConfig
from materials_discovery.llm.schema import (
    LlmGenerationAttempt,
    LlmGenerationRequest,
    LlmGenerationResult,
    LlmRunManifest,
)


def _base_config() -> dict:
    workspace = Path(__file__).resolve().parents[1]
    return load_yaml(workspace / "configs" / "systems" / "al_cu_fe.yaml")


def test_system_config_preserves_optional_llm_generate_when_omitted() -> None:
    config = SystemConfig.model_validate(_base_config())

    assert config.llm_generate is None
    assert config.backend.llm_adapter == "llm_fixture_v1"
    assert config.backend.llm_provider == "mock"


def test_system_config_accepts_nested_llm_generate_block() -> None:
    data = _base_config()
    data["llm_generate"] = {
        "prompt_template": "zomic_generate_v1",
        "temperature": 0.5,
        "max_tokens": 512,
        "max_attempts": 4,
        "seed_zomic": "designs/demo.zomic",
        "artifact_root": "data/llm_runs/custom",
        "fixture_outputs": ["line 1", "line 2"],
    }
    config = SystemConfig.model_validate(data)

    assert config.llm_generate is not None
    assert config.llm_generate.prompt_template == "zomic_generate_v1"
    assert config.llm_generate.max_attempts == 4
    assert config.llm_generate.fixture_outputs == ["line 1", "line 2"]


def test_real_llm_provider_fields_must_be_explicit() -> None:
    data = _base_config()
    data["backend"] = {
        "mode": "real",
        "llm_adapter": "anthropic_api_v1",
        "llm_provider": "anthropic",
    }

    with pytest.raises(ValidationError):
        SystemConfig.model_validate(data)


def test_llm_generate_summary_validates_counts_and_paths() -> None:
    summary = LlmGenerateSummary(
        requested_count=3,
        generated_count=2,
        attempt_count=4,
        parse_pass_count=3,
        compile_pass_count=2,
        output_path="data/candidates/demo.jsonl",
        calibration_path="data/calibration/demo.json",
        manifest_path="data/manifests/demo.json",
        run_manifest_path="data/llm_runs/demo/manifest.json",
    )

    assert summary.generated_count == 2
    assert summary.run_manifest_path == "data/llm_runs/demo/manifest.json"


def test_llm_generation_models_reuse_shared_contracts() -> None:
    request = LlmGenerationRequest(
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        composition_bounds={
            "Al": {"min": 0.6, "max": 0.8},
            "Cu": {"min": 0.1, "max": 0.25},
            "Fe": {"min": 0.05, "max": 0.2},
        },
        prompt_text="build only zomic",
        temperature=0.2,
        max_tokens=256,
        seed_zomic_path="designs/example.zomic",
    )
    attempt = LlmGenerationAttempt(
        attempt_id="attempt-001",
        adapter_key="llm_fixture_v1",
        provider="mock",
        model="fixture-zomic-v1",
        temperature=0.2,
        prompt_path="data/llm_runs/demo/prompt.json",
        raw_completion_path="data/llm_runs/demo/raw-001.zomic",
        parse_status="passed",
        compile_status="failed",
        error_kind="bridge_failure",
    )
    result = LlmGenerationResult(
        attempt_id="attempt-001",
        candidate_id="md_000001",
        orbit_library_path="data/prototypes/generated/demo.json",
        raw_export_path="data/prototypes/generated/demo.raw.json",
        parse_status="passed",
        compile_status="passed",
        passed=True,
    )
    manifest = LlmRunManifest(
        run_id="run-demo",
        system="Al-Cu-Fe",
        adapter_key="llm_fixture_v1",
        provider="mock",
        model="fixture-zomic-v1",
        prompt_template="zomic_generate_v1",
        attempt_count=3,
        requested_count=2,
        generated_count=2,
        prompt_path="data/llm_runs/demo/prompt.json",
        attempts_path="data/llm_runs/demo/attempts.jsonl",
        compile_results_path="data/llm_runs/demo/compile_results.jsonl",
        created_at_utc="2026-04-03T22:00:00Z",
    )

    assert request.composition_bounds["Al"].min == 0.6
    assert attempt.parse_status == "passed"
    assert result.schema_version == "llm-generation-result/v1"
    assert manifest.schema_version == "llm-run-manifest/v1"


def test_llm_generation_request_rejects_blank_prompt_text() -> None:
    with pytest.raises(ValidationError):
        LlmGenerationRequest(
            system="Al-Cu-Fe",
            template_family="icosahedral_approximant_1_1",
            composition_bounds={"Al": {"min": 0.6, "max": 0.8}},
            prompt_text="   ",
            temperature=0.2,
            max_tokens=256,
        )
