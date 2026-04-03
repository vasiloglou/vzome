from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from materials_discovery.common.io import write_json_object, write_jsonl, workspace_root
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import CandidateRecord, LlmGenerateSummary, SystemConfig
from materials_discovery.generator.candidate_factory import build_candidate_from_prototype_library
from materials_discovery.llm.compiler import compile_zomic_script
from materials_discovery.llm.prompting import build_generation_prompt, load_seed_zomic_text
from materials_discovery.llm.runtime import resolve_llm_adapter
from materials_discovery.llm.schema import (
    LlmGenerationAttempt,
    LlmGenerationRequest,
    LlmGenerationResult,
    LlmRunManifest,
)


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _resolve_relative_path(path_str: str, *, config_path: Path | None) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if config_path is not None:
        return (config_path.parent / path).resolve()
    return (workspace_root() / path).resolve()


def _effective_seed_path(
    config: SystemConfig,
    seed_zomic_path: Path | None,
    *,
    config_path: Path | None,
) -> Path | None:
    del config_path
    if seed_zomic_path is not None:
        return seed_zomic_path.resolve()
    if config.llm_generate is None or config.llm_generate.seed_zomic is None:
        return None
    return _resolve_relative_path(config.llm_generate.seed_zomic, config_path=None)


def _request_hash(
    config: SystemConfig,
    *,
    count: int,
    temperature: float,
    seed_path: Path | None,
) -> str:
    payload = {
        "config_hash": config_sha256(config),
        "requested_count": count,
        "temperature": temperature,
        "seed_path": "" if seed_path is None else str(seed_path),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]


def _run_root(config: SystemConfig, *, request_hash: str) -> Path:
    base = workspace_root() / "data" / "llm_runs"
    if config.llm_generate is not None and config.llm_generate.artifact_root is not None:
        base = _resolve_relative_path(config.llm_generate.artifact_root, config_path=None)
    return base / f"{_system_slug(config.system_name)}_{request_hash}"


def _seed_validation_error(result: dict[str, object]) -> ValueError:
    error_kind = result.get("error_kind") or "seed_validation_failed"
    error_message = result.get("error_message") or "unknown seed validation error"
    return ValueError(f"Seed Zomic failed validation ({error_kind}): {error_message}")


def generate_llm_candidates(
    config: SystemConfig,
    output_path: Path,
    count: int,
    config_path: Path | None = None,
    seed_zomic_path: Path | None = None,
    temperature_override: float | None = None,
) -> LlmGenerateSummary:
    if config.llm_generate is None:
        raise ValueError("config.llm_generate must be configured for llm-generate")

    llm_config = config.llm_generate
    effective_temperature = (
        llm_config.temperature if temperature_override is None else temperature_override
    )
    effective_seed_path = _effective_seed_path(
        config,
        seed_zomic_path,
        config_path=config_path,
    )
    seed_text = load_seed_zomic_text(effective_seed_path)
    if seed_text is not None:
        seed_result = compile_zomic_script(
            seed_text,
            prototype_key=f"{_system_slug(config.system_name)}_seed_validation",
            system_name=config.system_name,
            template_family=config.template_family,
        )
        if seed_result["parse_status"] != "passed" or seed_result["compile_status"] != "passed":
            raise _seed_validation_error(seed_result)

    prompt_text = build_generation_prompt(config, count=count, seed_zomic_text=seed_text)
    request_hash = _request_hash(
        config,
        count=count,
        temperature=effective_temperature,
        seed_path=effective_seed_path,
    )
    run_dir = _run_root(config, request_hash=request_hash)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    (run_dir / "raw").mkdir(parents=True, exist_ok=True)
    (run_dir / "compiled").mkdir(parents=True, exist_ok=True)

    request = LlmGenerationRequest(
        system=config.system_name,
        template_family=config.template_family,
        composition_bounds=config.composition_bounds,
        prompt_text=prompt_text,
        temperature=effective_temperature,
        max_tokens=llm_config.max_tokens,
        seed_zomic_path=None if effective_seed_path is None else str(effective_seed_path),
    )
    prompt_path = run_dir / "prompt.json"
    write_json_object(
        {
            "request_hash": request_hash,
            "prompt_template": llm_config.prompt_template,
            "request": request.model_dump(mode="json"),
            "prompt_text": prompt_text,
        },
        prompt_path,
    )

    adapter = resolve_llm_adapter(
        config.backend.mode,
        backend=config.backend,
        llm_generate=llm_config,
    )
    adapter_key = config.backend.llm_adapter or "llm_fixture_v1"
    provider = config.backend.llm_provider or "mock"
    model = config.backend.llm_model or "fixture"

    attempts: list[LlmGenerationAttempt] = []
    compile_results: list[LlmGenerationResult] = []
    candidates: list[CandidateRecord] = []
    parse_pass_count = 0
    compile_pass_count = 0
    max_total_attempts = count * llm_config.max_attempts

    for attempt_number in range(1, max_total_attempts + 1):
        if len(candidates) >= count:
            break
        attempt_id = f"llm_attempt_{attempt_number:04d}"
        raw_completion_path = run_dir / "raw" / f"{attempt_id}.zomic"
        parse_status = "failed"
        compile_status = "failed"
        error_kind: str | None = None
        error_message: str | None = None
        orbit_library_path: str | None = None
        raw_export_path: str | None = None
        candidate_id: str | None = None
        passed = False

        try:
            raw_completion = adapter.generate(request)
        except Exception as exc:  # pragma: no cover - exercised via tests
            raw_completion = ""
            error_kind = "provider_error"
            error_message = str(exc)
        raw_completion_path.write_text(raw_completion, encoding="utf-8")

        if error_kind is None:
            compile_result = compile_zomic_script(
                raw_completion,
                prototype_key=f"{_system_slug(config.system_name)}_{attempt_id}",
                system_name=config.system_name,
                template_family=config.template_family,
                artifact_root=run_dir / "compiled" / attempt_id,
            )
            parse_status = compile_result["parse_status"]
            compile_status = compile_result["compile_status"]
            orbit_library_path = compile_result.get("orbit_library_path")
            raw_export_path = compile_result.get("raw_export_path")
            error_kind = compile_result.get("error_kind")
            error_message = compile_result.get("error_message")

            if parse_status == "passed":
                parse_pass_count += 1
            if compile_status == "passed":
                compile_pass_count += 1

            if compile_status == "passed" and orbit_library_path is not None:
                try:
                    candidate = build_candidate_from_prototype_library(
                        config,
                        seed=config.seed,
                        candidate_index=len(candidates) + 1,
                        template_override_path=Path(orbit_library_path),
                        extra_provenance={
                            "source": "llm",
                            "llm_run_id": run_dir.name,
                            "llm_attempt_id": attempt_id,
                            "llm_adapter": adapter_key,
                            "llm_provider": provider,
                            "llm_model": model,
                            "prompt_path": str(prompt_path),
                            "raw_completion_path": str(raw_completion_path),
                            "seed_zomic_path": (
                                None if effective_seed_path is None else str(effective_seed_path)
                            ),
                        },
                    )
                except Exception as exc:  # pragma: no cover - exercised via tests
                    error_kind = "conversion_error"
                    error_message = str(exc)
                else:
                    candidate_id = candidate.candidate_id
                    candidates.append(candidate)
                    passed = True

        attempts.append(
            LlmGenerationAttempt(
                attempt_id=attempt_id,
                adapter_key=adapter_key,
                provider=provider,
                model=model,
                temperature=effective_temperature,
                prompt_path=str(prompt_path),
                raw_completion_path=str(raw_completion_path),
                parse_status=parse_status,
                compile_status=compile_status,
                error_kind=error_kind,
                error_message=error_message,
            )
        )
        compile_results.append(
            LlmGenerationResult(
                attempt_id=attempt_id,
                candidate_id=candidate_id,
                orbit_library_path=orbit_library_path,
                raw_export_path=raw_export_path,
                parse_status=parse_status,
                compile_status=compile_status,
                passed=passed,
            )
        )

    write_jsonl([candidate.model_dump(mode="json") for candidate in candidates], output_path)

    attempts_path = run_dir / "attempts.jsonl"
    compile_results_path = run_dir / "compile_results.jsonl"
    write_jsonl([attempt.model_dump(mode="json") for attempt in attempts], attempts_path)
    write_jsonl(
        [result.model_dump(mode="json") for result in compile_results],
        compile_results_path,
    )

    run_manifest_path = run_dir / "run_manifest.json"
    run_manifest = LlmRunManifest(
        run_id=run_dir.name,
        system=config.system_name,
        adapter_key=adapter_key,
        provider=provider,
        model=model,
        prompt_template=llm_config.prompt_template,
        attempt_count=len(attempts),
        requested_count=count,
        generated_count=len(candidates),
        prompt_path=str(prompt_path),
        attempts_path=str(attempts_path),
        compile_results_path=str(compile_results_path),
        created_at_utc=datetime.now(UTC).isoformat(),
    )
    write_json_object(run_manifest.model_dump(mode="json"), run_manifest_path)

    return LlmGenerateSummary(
        requested_count=count,
        generated_count=len(candidates),
        attempt_count=len(attempts),
        parse_pass_count=parse_pass_count,
        compile_pass_count=compile_pass_count,
        output_path=str(output_path),
        run_manifest_path=str(run_manifest_path),
    )
