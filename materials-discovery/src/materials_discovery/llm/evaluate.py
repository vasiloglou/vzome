from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from materials_discovery.common.io import load_jsonl, write_json_object, write_jsonl, workspace_root
from materials_discovery.common.manifest import config_sha256
from materials_discovery.common.schema import BackendConfig, CandidateRecord, LlmEvaluateSummary, SystemConfig
from materials_discovery.llm.launch import build_serving_identity, resolve_serving_lane
from materials_discovery.llm.runtime import (
    MockLlmAdapter,
    resolve_llm_adapter,
    validate_llm_adapter_ready,
)
from materials_discovery.llm.schema import (
    LlmAssessment,
    LlmEvaluationRequest,
    LlmEvaluationRunManifest,
)
from materials_discovery.llm.specialist import build_specialized_evaluation_payload


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _batch_slug(batch: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", batch.strip().lower()).strip("_")
    return slug or "batch"


def _resolve_relative_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (workspace_root() / path).resolve()


def _run_root(config: SystemConfig, *, batch: str, request_hash: str) -> Path:
    base = workspace_root() / "data" / "llm_evaluations"
    llm_config = config.llm_evaluate
    if llm_config is not None and llm_config.artifact_root is not None:
        base = _resolve_relative_path(llm_config.artifact_root)
    return base / f"{_system_slug(config.system_name)}_{_batch_slug(batch)}_{request_hash}"


def _request_hash(config: SystemConfig, *, batch: str, input_path: Path) -> str:
    payload = {
        "config_hash": config_sha256(config),
        "batch": batch,
        "input_path": str(input_path),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]


def _load_ranked_candidates(input_path: Path) -> list[CandidateRecord]:
    if not input_path.exists():
        raise FileNotFoundError(
            "llm-evaluate input ranked file not found; run 'mdisc hifi-rank' first: "
            f"{input_path}"
        )

    ranked = [CandidateRecord.model_validate(row) for row in load_jsonl(input_path)]
    if not ranked:
        raise ValueError("ranked candidate file was found but contained no records")
    return ranked


def _select_ranked_batch(candidates: list[CandidateRecord], batch: str) -> list[CandidateRecord]:
    token = batch.strip().lower()
    if token == "all":
        return list(candidates)
    if token.startswith("top"):
        suffix = token[3:]
        if not suffix or not suffix.isdigit() or int(suffix) < 1:
            raise ValueError("batch must be 'all' or 'top<N>' with N >= 1, e.g. top20")
        selected = candidates[: int(suffix)]
        if not selected:
            raise ValueError("no ranked candidates available for the requested batch")
        return selected
    raise ValueError("batch must be 'all' or 'top<N>' with N >= 1, e.g. top20")


def _sanitize_token(value: str) -> str:
    token = re.sub(r"[^a-zA-Z0-9._-]+", "_", value).strip("_")
    return token or "candidate"


def _strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if not lines:
        return stripped
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _build_general_evaluation_payload(candidate: CandidateRecord) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "system": candidate.system,
        "template_family": candidate.template_family,
        "composition": candidate.composition,
        "cell": candidate.cell,
        "site_count": len(candidate.sites),
        "screen": candidate.screen,
        "digital_validation": candidate.digital_validation.model_dump(mode="json"),
        "rank_context": candidate.provenance.get("hifi_rank"),
    }


def _build_evaluation_prompt(candidate: CandidateRecord) -> str:
    payload = _build_general_evaluation_payload(candidate)
    serialized = json.dumps(payload, sort_keys=True, indent=2)
    return (
        "You are assessing a quasicrystal candidate for experiment planning.\n"
        "Return strict JSON with keys:\n"
        "- synthesizability_score: number in [0,1]\n"
        "- precursor_hints: array of short strings\n"
        "- anomaly_flags: array of short strings\n"
        "- literature_context: string\n"
        "- rationale: string\n\n"
        "Candidate payload:\n"
        f"{serialized}\n"
    )


def _build_specialized_evaluation_prompt(candidate: CandidateRecord) -> str:
    payload = build_specialized_evaluation_payload(candidate)
    payload = {
        **payload,
        "specialist_focus": [
            "composition plausibility",
            "structural motif consistency",
            "synthesizability heuristics",
        ],
    }
    serialized = json.dumps(payload, sort_keys=True, indent=2)
    return (
        "You are a specialized materials-model lane assessing a quasicrystal candidate "
        "for experiment planning.\n"
        "Return strict JSON with keys:\n"
        "- synthesizability_score: number in [0,1]\n"
        "- precursor_hints: array of short strings\n"
        "- anomaly_flags: array of short strings\n"
        "- literature_context: string\n"
        "- rationale: string\n\n"
        "Use the structure-oriented payload below and keep the response strict JSON.\n\n"
        "Specialized candidate payload:\n"
        f"{serialized}\n"
    )


def _requested_model_lanes(requested_lane: str | None) -> list[str]:
    if requested_lane is None:
        return []
    return [requested_lane]


def _resolve_adapter(config: SystemConfig, backend: BackendConfig):
    llm_config = config.llm_evaluate
    if llm_config is None:
        raise ValueError("config.llm_evaluate must be configured for llm-evaluate")
    if backend.mode == "mock":
        return MockLlmAdapter(fixture_outputs=list(llm_config.fixture_outputs))
    return resolve_llm_adapter(backend.mode, backend=backend)


def _parse_assessment_payload(raw_completion: str) -> dict[str, Any]:
    payload = json.loads(_strip_code_fences(raw_completion))
    if not isinstance(payload, dict):
        raise ValueError("assessment output must be a JSON object")
    return payload


def _provenance_assessment_block(
    assessment: LlmAssessment,
    *,
    run_id: str,
) -> dict[str, Any]:
    return {
        "status": assessment.status,
        "run_id": run_id,
        "synthesizability_score": assessment.synthesizability_score,
        "precursor_hints": list(assessment.precursor_hints),
        "anomaly_flags": list(assessment.anomaly_flags),
        "literature_context": assessment.literature_context,
        "rationale": assessment.rationale,
        "error_kind": assessment.error_kind,
        "error_message": assessment.error_message,
        "requested_model_lanes": list(assessment.requested_model_lanes),
        "resolved_model_lane": assessment.resolved_model_lane,
        "resolved_model_lane_source": assessment.resolved_model_lane_source,
        "serving_identity": (
            None if assessment.serving_identity is None else assessment.serving_identity.model_dump(mode="json")
        ),
    }


def evaluate_llm_candidates(
    config: SystemConfig,
    output_path: Path,
    *,
    batch: str = "all",
    input_path: Path | None = None,
    requested_model_lane: str | None = None,
) -> LlmEvaluateSummary:
    llm_config = config.llm_evaluate
    if llm_config is None:
        raise ValueError("config.llm_evaluate must be configured for llm-evaluate")

    system_slug = _system_slug(config.system_name)
    resolved_input_path = input_path
    if resolved_input_path is None:
        resolved_input_path = workspace_root() / "data" / "ranked" / f"{system_slug}_ranked.jsonl"

    ranked = _load_ranked_candidates(resolved_input_path)
    selected = _select_ranked_batch(ranked, batch)

    request_hash = _request_hash(config, batch=batch, input_path=resolved_input_path)
    run_dir = _run_root(config, batch=batch, request_hash=request_hash)
    if run_dir.exists():
        shutil.rmtree(run_dir)
    (run_dir / "raw").mkdir(parents=True, exist_ok=True)

    configured_requested_lane = llm_config.model_lane
    effective_requested_lane = requested_model_lane or configured_requested_lane
    resolved_lane, lane_config, lane_source = resolve_serving_lane(
        effective_requested_lane,
        config.llm_generate,
        config.backend,
    )
    effective_backend = config.backend.model_copy(deep=True)
    if lane_config is not None:
        effective_backend.llm_adapter = lane_config.adapter
        effective_backend.llm_provider = lane_config.provider
        effective_backend.llm_model = lane_config.model
        effective_backend.llm_api_base = lane_config.api_base

    adapter = _resolve_adapter(config, effective_backend)
    adapter_key = effective_backend.llm_adapter or "llm_fixture_v1"
    provider = effective_backend.llm_provider or "mock"
    model = effective_backend.llm_model or "fixture"
    serving_identity = build_serving_identity(
        requested_lane=effective_requested_lane,
        resolved_lane=resolved_lane,
        lane_source=lane_source,
        backend=config.backend,
        lane_config=lane_config,
    )
    validate_llm_adapter_ready(
        adapter,
        adapter_key=adapter_key,
        requested_lane=effective_requested_lane,
        resolved_lane=resolved_lane,
    )

    requests: list[LlmEvaluationRequest] = []
    assessments: list[LlmAssessment] = []
    enriched_candidates: list[CandidateRecord] = []
    assessed_count = 0

    for candidate in selected:
        if resolved_lane == "specialized_materials":
            prompt_text = _build_specialized_evaluation_prompt(candidate)
        else:
            prompt_text = _build_evaluation_prompt(candidate)
        request = LlmEvaluationRequest(
            candidate_id=candidate.candidate_id,
            system=candidate.system,
            template_family=candidate.template_family,
            composition=candidate.composition,
            digital_validation=candidate.digital_validation.model_dump(mode="json"),
            prompt_text=prompt_text,
            temperature=llm_config.temperature,
            max_tokens=llm_config.max_tokens,
        )
        requests.append(request)

        raw_response_path = run_dir / "raw" / f"{_sanitize_token(candidate.candidate_id)}.txt"
        status = "failed"
        raw_completion = ""
        payload: dict[str, Any] | None = None
        error_kind: str | None = None
        error_message: str | None = None

        try:
            raw_completion = adapter.generate(request)
            payload = _parse_assessment_payload(raw_completion)
            assessment = LlmAssessment(
                candidate_id=candidate.candidate_id,
                adapter_key=adapter_key,
                provider=provider,
                model=model,
                status="passed",
                raw_response_path=str(raw_response_path),
                requested_model_lanes=_requested_model_lanes(effective_requested_lane),
                resolved_model_lane=resolved_lane,
                resolved_model_lane_source=lane_source,
                serving_identity=serving_identity,
                synthesizability_score=payload.get("synthesizability_score"),
                precursor_hints=payload.get("precursor_hints", []),
                anomaly_flags=payload.get("anomaly_flags", []),
                literature_context=payload.get("literature_context"),
                rationale=payload.get("rationale"),
            )
            status = "passed"
            assessed_count += 1
        except json.JSONDecodeError as exc:
            error_kind = "response_parse_error"
            error_message = str(exc)
            assessment = LlmAssessment(
                candidate_id=candidate.candidate_id,
                adapter_key=adapter_key,
                provider=provider,
                model=model,
                status="failed",
                raw_response_path=str(raw_response_path),
                requested_model_lanes=_requested_model_lanes(effective_requested_lane),
                resolved_model_lane=resolved_lane,
                resolved_model_lane_source=lane_source,
                serving_identity=serving_identity,
                error_kind=error_kind,
                error_message=error_message,
            )
        except ValueError as exc:
            error_kind = "response_validation_error"
            error_message = str(exc)
            assessment = LlmAssessment(
                candidate_id=candidate.candidate_id,
                adapter_key=adapter_key,
                provider=provider,
                model=model,
                status="failed",
                raw_response_path=str(raw_response_path),
                requested_model_lanes=_requested_model_lanes(effective_requested_lane),
                resolved_model_lane=resolved_lane,
                resolved_model_lane_source=lane_source,
                serving_identity=serving_identity,
                error_kind=error_kind,
                error_message=error_message,
            )
        except Exception as exc:  # pragma: no cover - exercised via CLI/provider tests
            error_kind = "provider_error"
            error_message = str(exc)
            assessment = LlmAssessment(
                candidate_id=candidate.candidate_id,
                adapter_key=adapter_key,
                provider=provider,
                model=model,
                status="failed",
                raw_response_path=str(raw_response_path),
                requested_model_lanes=_requested_model_lanes(effective_requested_lane),
                resolved_model_lane=resolved_lane,
                resolved_model_lane_source=lane_source,
                serving_identity=serving_identity,
                error_kind=error_kind,
                error_message=error_message,
            )

        if llm_config.persist_raw_responses or raw_completion:
            raw_response_path.write_text(raw_completion, encoding="utf-8")

        candidate_copy = candidate.model_copy(deep=True)
        candidate_copy.provenance["llm_assessment"] = _provenance_assessment_block(
            assessment,
            run_id=run_dir.name,
        )
        candidate_copy.provenance["llm_assessment_status"] = status
        enriched_candidates.append(candidate_copy)
        assessments.append(assessment)

    write_jsonl([candidate.model_dump(mode="json") for candidate in enriched_candidates], output_path)

    requests_path = run_dir / "requests.jsonl"
    assessments_path = run_dir / "assessments.jsonl"
    write_jsonl([request.model_dump(mode="json") for request in requests], requests_path)
    write_jsonl([assessment.model_dump(mode="json") for assessment in assessments], assessments_path)

    run_manifest_path = run_dir / "run_manifest.json"
    run_manifest = LlmEvaluationRunManifest(
        run_id=run_dir.name,
        system=config.system_name,
        adapter_key=adapter_key,
        provider=provider,
        model=model,
        prompt_template=llm_config.prompt_template,
        input_path=str(resolved_input_path),
        output_path=str(output_path),
        requests_path=str(requests_path),
        assessments_path=str(assessments_path),
        requested_count=len(selected),
        assessed_count=assessed_count,
        failed_count=len(selected) - assessed_count,
        created_at_utc=datetime.now(UTC).isoformat(),
        requested_model_lanes=_requested_model_lanes(effective_requested_lane),
        resolved_model_lane=resolved_lane,
        resolved_model_lane_source=lane_source,
        serving_identity=serving_identity,
    )
    write_json_object(run_manifest.model_dump(mode="json"), run_manifest_path)

    return LlmEvaluateSummary(
        input_count=len(selected),
        assessed_count=assessed_count,
        failed_count=len(selected) - assessed_count,
        output_path=str(output_path),
        requested_model_lanes=_requested_model_lanes(effective_requested_lane),
        resolved_model_lane=resolved_lane,
        resolved_model_lane_source=lane_source,
        serving_identity=serving_identity,
        run_manifest_path=str(run_manifest_path),
    )
