from __future__ import annotations

import hashlib
import importlib
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from materials_discovery.common.io import (
    load_json_object,
    load_jsonl,
    load_yaml,
    workspace_root,
    write_json_object,
    write_jsonl,
)
from materials_discovery.common.schema import CompositionBound, SystemConfig
from materials_discovery.generator.prototype_import import parse_cif
from materials_discovery.llm.external_targets import (
    capture_external_target_environment,
    load_registered_external_target,
    smoke_external_target,
)
from materials_discovery.llm.launch import build_serving_identity, resolve_serving_lane
from materials_discovery.llm.runtime import resolve_llm_adapter
from materials_discovery.llm.schema import (
    LlmExternalBenchmarkCaseResult,
    LlmExternalBenchmarkControlDelta,
    LlmExternalBenchmarkExternalTarget,
    LlmExternalBenchmarkInternalControl,
    LlmExternalBenchmarkSliceSummary,
    LlmExternalBenchmarkSpec,
    LlmExternalBenchmarkSummary,
    LlmExternalBenchmarkTargetRunManifest,
    LlmExternalBenchmarkTargetSummary,
    LlmExternalTargetRegistration,
    LlmExternalTargetSmokeCheck,
    LlmGenerationRequest,
    LlmServingIdentity,
    TranslatedBenchmarkIncludedRow,
    TranslatedBenchmarkSetManifest,
)
from materials_discovery.llm.storage import (
    llm_external_benchmark_scorecard_by_case_path,
    llm_external_benchmark_smoke_path,
    llm_external_benchmark_summary_path,
    llm_external_benchmark_target_case_results_path,
    llm_external_benchmark_target_raw_responses_path,
    llm_external_benchmark_target_run_manifest_path,
)

_PERIODIC_SAFE_FIDELITY_TIERS = {"exact", "anchored"}


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root.resolve()


def _resolve_spec_relative_path(spec_path: Path, candidate: str) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path.resolve()
    return (spec_path.parent / path).resolve()


def _resolve_stored_path(candidate: str, *, root: Path | None = None) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path.resolve()
    return (_artifact_root(root) / path).resolve()


def _path_for_storage(path: Path, *, root: Path | None = None) -> str:
    resolved = path.resolve()
    artifact_root = _artifact_root(root)
    try:
        return str(resolved.relative_to(artifact_root))
    except ValueError:
        return str(resolved)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _normalize_text(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.strip().splitlines())


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 6)


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 6)


def load_external_benchmark_spec(spec_path: Path) -> LlmExternalBenchmarkSpec:
    spec_path = spec_path.resolve()
    spec = LlmExternalBenchmarkSpec.model_validate(load_yaml(spec_path))
    return spec.model_copy(
        update={
            "benchmark_set_manifest_path": str(
                _resolve_spec_relative_path(spec_path, spec.benchmark_set_manifest_path)
            ),
            "internal_controls": [
                control.model_copy(
                    update={
                        "system_config_path": str(
                            _resolve_spec_relative_path(spec_path, control.system_config_path)
                        )
                    }
                )
                for control in spec.internal_controls
            ],
        }
    )


def _load_benchmark_rows(
    benchmark_set_manifest_path: str,
    *,
    root: Path | None = None,
) -> tuple[TranslatedBenchmarkSetManifest, list[TranslatedBenchmarkIncludedRow]]:
    manifest_path = _resolve_stored_path(benchmark_set_manifest_path, root=root)
    manifest = TranslatedBenchmarkSetManifest.model_validate(load_json_object(manifest_path))
    included_path = _resolve_stored_path(manifest.included_inventory_path, root=root)
    rows = [TranslatedBenchmarkIncludedRow.model_validate(row) for row in load_jsonl(included_path)]
    return manifest, rows


def _format_composition(composition: dict[str, float]) -> str:
    return ", ".join(f"{species} {fraction:.3f}" for species, fraction in sorted(composition.items()))


def _render_prompt(case: TranslatedBenchmarkIncludedRow, prompt_contract_id: str) -> str:
    composition_text = _format_composition(case.composition)
    if prompt_contract_id == "translated_cif_v1":
        return (
            f"System: {case.system}\n"
            f"Template family: {case.template_family}\n"
            f"Composition: {composition_text}\n"
            f"Target family: {case.target_family}\n"
            "Return one candidate structure as CIF text only.\n"
            "Do not add explanations or markdown fences."
        )
    if prompt_contract_id == "crystaltextllm_material_string_v1":
        return (
            f"System: {case.system}\n"
            f"Template family: {case.template_family}\n"
            f"Composition: {composition_text}\n"
            f"Target family: {case.target_family}\n"
            "Return one candidate structure in CrystalTextLLM-style material-string format only.\n"
            "Do not add explanations or markdown fences."
        )
    raise ValueError(f"unsupported prompt_contract_id: {prompt_contract_id}")


def _normalize_composition(values: Counter[str] | dict[str, float]) -> dict[str, float] | None:
    if not values:
        return None
    total = float(sum(values.values()))
    if total <= 0.0:
        return None
    return {key: round(float(value) / total, 6) for key, value in sorted(values.items())}


def _parse_material_string_composition(text: str) -> dict[str, float] | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 4 or (len(lines) - 2) % 2 != 0:
        raise ValueError("material-string body must contain species/coordinate pairs after two header lines")

    counts: Counter[str] = Counter()
    for idx in range(2, len(lines), 2):
        species = lines[idx]
        coords = lines[idx + 1].split()
        if len(coords) != 3:
            raise ValueError("material-string coordinate rows must contain three values")
        for value in coords:
            float(value)
        counts[species] += 1
    return _normalize_composition(counts)


def _parse_cif_composition(text: str) -> dict[str, float] | None:
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".cif", delete=False, encoding="utf-8") as handle:
            handle.write(text)
            tmp_path = Path(handle.name)
        cif = parse_cif(tmp_path)
        counts: Counter[str] = Counter()
        for loop in cif.get("loops", []):
            headers = set(loop.get("headers", []))
            required = {
                "_atom_site_label",
                "_atom_site_type_symbol",
                "_atom_site_fract_x",
                "_atom_site_fract_y",
                "_atom_site_fract_z",
            }
            if not required.issubset(headers):
                continue
            for row in loop.get("rows", []):
                symbol = str(row.get("_atom_site_type_symbol", "")).strip()
                if symbol:
                    counts[symbol] += 1
            break
        return _normalize_composition(counts)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)


def _parse_response_composition(text: str, parser_key: str) -> dict[str, float] | None:
    normalized_text = _normalize_text(text)
    if not normalized_text:
        raise ValueError("response text must not be blank")
    if parser_key == "cif_text":
        return _parse_cif_composition(normalized_text)
    if parser_key == "crystaltextllm_material_string":
        return _parse_material_string_composition(normalized_text)
    raise ValueError(f"unsupported response_parser_key: {parser_key}")


def _composition_match(
    parsed: dict[str, float] | None, expected: dict[str, float], *, tolerance: float = 1e-3
) -> bool | None:
    if parsed is None:
        return None
    expected_normalized = _normalize_composition(expected)
    if expected_normalized is None:
        return None
    if set(parsed) != set(expected_normalized):
        return False
    return all(abs(parsed[key] - expected_normalized[key]) <= tolerance for key in parsed)


def _build_transformers_runner(
    registration: LlmExternalTargetRegistration,
    *,
    root: Path | None = None,
) -> Callable[[TranslatedBenchmarkIncludedRow, str], str]:
    snapshot_path = _resolve_stored_path(registration.local_snapshot_path, root=root)
    transformers = importlib.import_module("transformers")
    torch = importlib.import_module("torch")

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        str(snapshot_path),
        revision=registration.tokenizer_revision or registration.model_revision,
        local_files_only=True,
    )
    model = transformers.AutoModelForCausalLM.from_pretrained(
        str(snapshot_path),
        revision=registration.model_revision,
        local_files_only=True,
    )
    if registration.dtype == "bfloat16" and hasattr(torch, "bfloat16"):
        model = model.to(dtype=torch.bfloat16)

    def _runner(case: TranslatedBenchmarkIncludedRow, prompt_text: str) -> str:
        del case
        encoded = tokenizer(prompt_text, return_tensors="pt")
        outputs = model.generate(**encoded, max_new_tokens=256, do_sample=False)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if decoded.startswith(prompt_text):
            decoded = decoded[len(prompt_text) :]
        return decoded.strip()

    return _runner


def _build_peft_runner(
    registration: LlmExternalTargetRegistration,
    *,
    root: Path | None = None,
) -> Callable[[TranslatedBenchmarkIncludedRow, str], str]:
    snapshot_path = _resolve_stored_path(registration.local_snapshot_path, root=root)
    peft = importlib.import_module("peft")
    transformers = importlib.import_module("transformers")

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        str(snapshot_path),
        revision=registration.tokenizer_revision or registration.model_revision,
        local_files_only=True,
    )
    model = peft.AutoPeftModelForCausalLM.from_pretrained(
        str(snapshot_path),
        revision=registration.model_revision,
        local_files_only=True,
    )

    def _runner(case: TranslatedBenchmarkIncludedRow, prompt_text: str) -> str:
        del case
        encoded = tokenizer(prompt_text, return_tensors="pt")
        outputs = model.generate(**encoded, max_new_tokens=256, do_sample=False)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if decoded.startswith(prompt_text):
            decoded = decoded[len(prompt_text) :]
        return decoded.strip()

    return _runner


def _build_external_runner(
    registration: LlmExternalTargetRegistration,
    *,
    root: Path | None = None,
) -> Callable[[TranslatedBenchmarkIncludedRow, str], str]:
    if registration.runner_key == "transformers_causal_lm":
        return _build_transformers_runner(registration, root=root)
    if registration.runner_key == "peft_causal_lm":
        return _build_peft_runner(registration, root=root)
    raise ValueError(f"unsupported external runner_key: {registration.runner_key}")


def _resolve_internal_control_backend(
    control: LlmExternalBenchmarkInternalControl,
) -> tuple[SystemConfig, LlmServingIdentity, Callable[[TranslatedBenchmarkIncludedRow, str], str]]:
    config = SystemConfig.model_validate(load_yaml(Path(control.system_config_path)))
    resolved_lane, lane_config, lane_source = resolve_serving_lane(
        control.generation_model_lane,
        config.llm_generate,
        config.backend,
    )
    effective_backend = config.backend.model_copy(deep=True)
    if lane_config is not None:
        effective_backend = effective_backend.model_copy(
            update={
                "llm_adapter": lane_config.adapter,
                "llm_provider": lane_config.provider,
                "llm_model": lane_config.model,
                "llm_api_base": lane_config.api_base,
            }
        )
    serving_identity = build_serving_identity(
        requested_lane=control.generation_model_lane,
        resolved_lane=resolved_lane,
        lane_source=lane_source,
        backend=config.backend,
        lane_config=lane_config,
    )
    adapter = resolve_llm_adapter(
        effective_backend.mode,
        backend=effective_backend,
        llm_generate=config.llm_generate,
    )

    def _runner(case: TranslatedBenchmarkIncludedRow, prompt_text: str) -> str:
        composition_bounds = {
            species: CompositionBound(min=value, max=value)
            for species, value in case.composition.items()
        }
        request = LlmGenerationRequest(
            system=case.system,
            template_family=case.template_family,
            composition_bounds=composition_bounds,
            prompt_text=prompt_text,
            temperature=0.0,
            max_tokens=512,
        )
        return adapter.generate(request)

    return config, serving_identity, _runner


def _eligible_for_target(
    case: TranslatedBenchmarkIncludedRow,
    *,
    supported_target_families: list[str],
    supported_systems: list[str],
) -> tuple[bool, str | None, str | None]:
    if supported_target_families and case.target_family not in supported_target_families:
        return False, "target_family_not_supported", (
            f"target_family '{case.target_family}' is not supported by this target"
        )
    if supported_systems and case.system not in supported_systems:
        return False, "system_not_supported", f"system '{case.system}' is not supported by this target"
    return True, None, None


def _excluded_case_result(
    *,
    benchmark_id: str,
    benchmark_set_id: str,
    benchmark_set_manifest_path: str,
    target_id: str,
    target_label: str,
    target_kind: str,
    control_role: str | None,
    model_id: str | None,
    case: TranslatedBenchmarkIncludedRow,
    prompt_contract_id: str,
    response_parser_key: str,
    exclusion_reason: str,
    exclusion_detail: str,
    prompt_hash: str,
) -> LlmExternalBenchmarkCaseResult:
    return LlmExternalBenchmarkCaseResult(
        benchmark_id=benchmark_id,
        benchmark_set_id=benchmark_set_id,
        benchmark_set_manifest_path=benchmark_set_manifest_path,
        target_id=target_id,
        target_label=target_label,
        target_kind=target_kind,
        control_role=control_role,
        model_id=model_id,
        candidate_id=case.candidate_id,
        source_export_id=case.source_export_id,
        source_bundle_manifest_path=case.source_bundle_manifest_path,
        system=case.system,
        target_family=case.target_family,
        fidelity_tier=case.fidelity_tier,
        loss_reasons=case.loss_reasons,
        diagnostic_codes=case.diagnostic_codes,
        composition=case.composition,
        prompt_contract_id=prompt_contract_id,
        response_parser_key=response_parser_key,
        response_status="excluded",
        parse_status="not_attempted",
        exclusion_reason=exclusion_reason,
        exclusion_detail=exclusion_detail,
        prompt_text_hash=prompt_hash,
    )


def _raw_response_record(
    *,
    case: TranslatedBenchmarkIncludedRow,
    prompt_hash: str,
    response_status: str,
    parse_status: str,
    response_text: str | None = None,
    latency_s: float | None = None,
    error_detail: str | None = None,
) -> dict[str, object]:
    return {
        "candidate_id": case.candidate_id,
        "target_family": case.target_family,
        "fidelity_tier": case.fidelity_tier,
        "prompt_text_hash": prompt_hash,
        "response_status": response_status,
        "parse_status": parse_status,
        "response_text_hash": None if response_text is None else _hash_text(_normalize_text(response_text)),
        "response_text": response_text,
        "latency_s": latency_s,
        "error_detail": error_detail,
    }


def _slice_summary(results: list[LlmExternalBenchmarkCaseResult]) -> LlmExternalBenchmarkSliceSummary:
    eligible_results = [result for result in results if result.response_status != "excluded"]
    excluded_count = len(results) - len(eligible_results)
    response_success_count = sum(result.response_status == "succeeded" for result in eligible_results)
    parse_success_count = sum(result.parse_status == "passed" for result in eligible_results)
    exact_match_count = sum(result.exact_text_match is True for result in eligible_results)
    composition_match_count = sum(result.composition_match is True for result in eligible_results)
    latencies = [result.latency_s for result in eligible_results if result.latency_s is not None]
    return LlmExternalBenchmarkSliceSummary(
        eligible_count=len(eligible_results),
        excluded_count=excluded_count,
        response_success_rate=_rate(response_success_count, len(eligible_results)),
        parse_success_rate=_rate(parse_success_count, len(eligible_results)),
        exact_text_match_rate=_rate(exact_match_count, len(eligible_results)),
        composition_match_rate=_rate(composition_match_count, len(eligible_results)),
        mean_latency_s=_mean(latencies),
    )


def _periodic_safe_results(
    results: list[LlmExternalBenchmarkCaseResult],
) -> list[LlmExternalBenchmarkCaseResult]:
    return [
        result
        for result in results
        if result.response_status != "excluded"
        and result.fidelity_tier in _PERIODIC_SAFE_FIDELITY_TIERS
    ]


def _shared_slice_deltas(
    target_results: list[LlmExternalBenchmarkCaseResult],
    control_results: list[LlmExternalBenchmarkCaseResult],
    control_target_id: str,
    control_label: str,
    control_role: str,
) -> LlmExternalBenchmarkControlDelta | None:
    target_lookup = {
        result.candidate_id: result for result in target_results if result.response_status != "excluded"
    }
    control_lookup = {
        result.candidate_id: result for result in control_results if result.response_status != "excluded"
    }
    shared_case_ids = sorted(set(target_lookup).intersection(control_lookup))
    if not shared_case_ids:
        return None

    target_shared = [target_lookup[candidate_id] for candidate_id in shared_case_ids]
    control_shared = [control_lookup[candidate_id] for candidate_id in shared_case_ids]

    target_summary = _slice_summary(target_shared)
    control_summary = _slice_summary(control_shared)

    def _delta(target_value: float | None, control_value: float | None) -> float | None:
        if target_value is None or control_value is None:
            return None
        return round(target_value - control_value, 6)

    return LlmExternalBenchmarkControlDelta(
        control_target_id=control_target_id,
        control_label=control_label,
        control_role=control_role,
        shared_eligible_count=len(shared_case_ids),
        parse_success_rate_delta=_delta(
            target_summary.parse_success_rate,
            control_summary.parse_success_rate,
        ),
        exact_text_match_rate_delta=_delta(
            target_summary.exact_text_match_rate,
            control_summary.exact_text_match_rate,
        ),
        composition_match_rate_delta=_delta(
            target_summary.composition_match_rate,
            control_summary.composition_match_rate,
        ),
    )


def _recommendation_lines(
    target_id: str,
    periodic_safe_results: list[LlmExternalBenchmarkCaseResult],
    periodic_safe_control_deltas: list[LlmExternalBenchmarkControlDelta],
    *,
    failed: bool,
) -> list[str]:
    if failed:
        return [
            f"Benchmark recommendation: {target_id} failed benchmark execution or smoke checks; resolve runtime issues before comparing it to the control arm."
        ]

    if not periodic_safe_results:
        return [
            f"Benchmark recommendation: {target_id} has no periodic-safe eligible slice; keep any proxy-slice signal diagnostic-only."
        ]

    aligned_deltas = [
        delta for delta in periodic_safe_control_deltas if delta.shared_eligible_count > 0
    ]
    if not aligned_deltas:
        return [
            f"Benchmark recommendation: {target_id} has no shared eligible control slice; collect a better aligned benchmark before making a roadmap decision."
        ]

    best_delta = max(
        (
            delta.exact_text_match_rate_delta
            if delta.exact_text_match_rate_delta is not None
            else delta.composition_match_rate_delta
            if delta.composition_match_rate_delta is not None
            else -1.0
        )
        for delta in aligned_deltas
    )

    if best_delta >= 0.1:
        return [
            f"Benchmark recommendation: {target_id} warrants deeper external-model investment on the periodic-safe slice."
        ]
    if best_delta >= -0.05:
        return [
            f"Benchmark recommendation: {target_id} merits targeted follow-up on the periodic-safe slice before any broader workflow expansion."
        ]
    return [
        f"Benchmark recommendation: {target_id} is not competitive with the current control arm on the periodic-safe slice."
    ]


def build_external_benchmark_summary(
    spec: LlmExternalBenchmarkSpec,
    target_manifests: dict[str, LlmExternalBenchmarkTargetRunManifest],
    target_results: dict[str, list[LlmExternalBenchmarkCaseResult]],
    *,
    summary_path: Path | None = None,
    root: Path | None = None,
) -> LlmExternalBenchmarkSummary:
    target_summaries: list[LlmExternalBenchmarkTargetSummary] = []
    internal_controls = {
        control.target_id: control
        for control in spec.internal_controls
    }

    for target in [*spec.external_targets, *spec.internal_controls]:
        manifest = target_manifests[target.target_id]
        results = target_results[target.target_id]
        periodic_safe_results = _periodic_safe_results(results)
        by_target_family = {
            family: _slice_summary([result for result in results if result.target_family == family])
            for family in sorted({result.target_family for result in results})
        }
        by_fidelity_tier = {
            fidelity: _slice_summary([result for result in results if result.fidelity_tier == fidelity])
            for fidelity in sorted({result.fidelity_tier for result in results})
        }
        failed = any(
            result.response_status == "runtime_error"
            or result.exclusion_reason == "smoke_check_failed"
            for result in results
        )
        control_deltas: list[LlmExternalBenchmarkControlDelta] = []
        periodic_safe_control_deltas: list[LlmExternalBenchmarkControlDelta] = []
        if target.target_kind == "external_target":
            for control_id, control in internal_controls.items():
                delta = _shared_slice_deltas(
                    results,
                    target_results[control_id],
                    control_target_id=control_id,
                    control_label=control.label,
                    control_role=control.control_role,
                )
                if delta is not None:
                    control_deltas.append(delta)
                periodic_safe_delta = _shared_slice_deltas(
                    periodic_safe_results,
                    _periodic_safe_results(target_results[control_id]),
                    control_target_id=control_id,
                    control_label=control.label,
                    control_role=control.control_role,
                )
                if periodic_safe_delta is not None:
                    periodic_safe_control_deltas.append(periodic_safe_delta)

        recommendation_lines = (
            _recommendation_lines(
                target.target_id,
                periodic_safe_results,
                periodic_safe_control_deltas,
                failed=failed,
            )
            if target.target_kind == "external_target"
            else []
        )

        target_summaries.append(
            LlmExternalBenchmarkTargetSummary(
                target_id=target.target_id,
                target_label=target.label,
                target_kind=target.target_kind,
                control_role=getattr(target, "control_role", None),
                model_id=manifest.model_id,
                registration_path=manifest.registration_path,
                environment_path=manifest.environment_path,
                smoke_check_path=manifest.smoke_check_path,
                run_manifest_path=manifest.run_manifest_path,
                eligible_count=manifest.eligible_count,
                excluded_count=manifest.excluded_count,
                overall=_slice_summary(results),
                by_target_family=by_target_family,
                by_fidelity_tier=by_fidelity_tier,
                control_deltas=control_deltas,
                recommendation_lines=recommendation_lines,
                failed=failed,
                serving_identity=manifest.serving_identity,
            )
        )

    benchmark_recommendations = [
        line
        for target_summary in target_summaries
        for line in target_summary.recommendation_lines
    ]
    failed_targets = sorted(target.target_id for target in target_summaries if target.failed)
    return LlmExternalBenchmarkSummary(
        benchmark_id=spec.benchmark_id,
        benchmark_set_id=target_manifests[next(iter(target_manifests))].benchmark_set_id,
        benchmark_set_manifest_path=_path_for_storage(
            Path(spec.benchmark_set_manifest_path),
            root=root,
        ),
        generated_at_utc=_utc_now(),
        targets=target_summaries,
        recommendation_lines=benchmark_recommendations,
        failed_targets=failed_targets,
        summary_path=None if summary_path is None else _path_for_storage(summary_path, root=root),
    )


def execute_external_benchmark(
    spec_path: Path,
    *,
    root: Path | None = None,
    out_path: Path | None = None,
) -> LlmExternalBenchmarkSummary:
    artifact_root = _artifact_root(root)
    spec = load_external_benchmark_spec(spec_path)
    benchmark_manifest, benchmark_rows = _load_benchmark_rows(
        spec.benchmark_set_manifest_path,
        root=artifact_root,
    )
    benchmark_manifest_path = _resolve_stored_path(spec.benchmark_set_manifest_path, root=artifact_root)

    smoke_records: list[dict[str, object]] = []
    target_manifests: dict[str, LlmExternalBenchmarkTargetRunManifest] = {}
    target_results: dict[str, list[LlmExternalBenchmarkCaseResult]] = {}

    for target in [*spec.external_targets, *spec.internal_controls]:
        case_results: list[LlmExternalBenchmarkCaseResult] = []
        raw_responses: list[dict[str, object]] = []
        run_manifest_path = llm_external_benchmark_target_run_manifest_path(
            spec.benchmark_id,
            target.target_id,
            root=artifact_root,
        )
        case_results_path = llm_external_benchmark_target_case_results_path(
            spec.benchmark_id,
            target.target_id,
            root=artifact_root,
        )
        raw_responses_path = llm_external_benchmark_target_raw_responses_path(
            spec.benchmark_id,
            target.target_id,
            root=artifact_root,
        )
        started_at_utc = _utc_now()

        if target.target_kind == "external_target":
            registration, registration_path = load_registered_external_target(target.model_id, root=artifact_root)
            environment = capture_external_target_environment(registration, root=artifact_root)
            smoke = smoke_external_target(target.model_id, root=artifact_root)
            smoke_records.append(smoke.model_dump(mode="json"))
            prompt_contract_id = target.prompt_contract_id or registration.prompt_contract_id
            response_parser_key = target.response_parser_key or registration.response_parser_key
            supported_target_families = list(target.supported_target_families)
            supported_systems = list(target.supported_systems)

            if not set(supported_target_families).issubset(set(registration.supported_target_families)):
                raise ValueError(
                    f"benchmark target '{target.target_id}' requests unsupported target families"
                )
            if supported_systems and registration.supported_systems:
                missing_systems = set(supported_systems).difference(registration.supported_systems)
                if missing_systems:
                    raise ValueError(
                        f"benchmark target '{target.target_id}' requests unsupported systems: {sorted(missing_systems)}"
                    )

            runner = None if smoke.status != "passed" else _build_external_runner(registration, root=artifact_root)
            serving_identity = None
        else:
            _, serving_identity, runner = _resolve_internal_control_backend(target)
            registration = None
            smoke = None
            prompt_contract_id = target.prompt_contract_id
            response_parser_key = target.response_parser_key
            supported_target_families = list(target.supported_target_families)
            supported_systems = list(target.supported_systems)
            registration_path_text = None

        for case in benchmark_rows:
            prompt_text = _render_prompt(case, prompt_contract_id)
            prompt_hash = _hash_text(prompt_text)
            eligible, exclusion_reason, exclusion_detail = _eligible_for_target(
                case,
                supported_target_families=supported_target_families,
                supported_systems=supported_systems,
            )
            if target.target_kind == "external_target" and smoke is not None and smoke.status != "passed":
                eligible = False
                exclusion_reason = "smoke_check_failed"
                exclusion_detail = smoke.detail or "external target smoke check failed"

            if not eligible:
                case_result = _excluded_case_result(
                    benchmark_id=spec.benchmark_id,
                    benchmark_set_id=benchmark_manifest.benchmark_set_id,
                    benchmark_set_manifest_path=_path_for_storage(
                        benchmark_manifest_path,
                        root=artifact_root,
                    ),
                    target_id=target.target_id,
                    target_label=target.label,
                    target_kind=target.target_kind,
                    control_role=getattr(target, "control_role", None),
                    model_id=getattr(target, "model_id", None),
                    case=case,
                    prompt_contract_id=prompt_contract_id,
                    response_parser_key=response_parser_key,
                    exclusion_reason=exclusion_reason or "target_family_not_supported",
                    exclusion_detail=exclusion_detail or "case is not eligible for this target",
                    prompt_hash=prompt_hash,
                )
                case_results.append(case_result)
                raw_responses.append(
                    _raw_response_record(
                        case=case,
                        prompt_hash=prompt_hash,
                        response_status="excluded",
                        parse_status="not_attempted",
                        error_detail=exclusion_detail,
                    )
                )
                continue

            start = time.perf_counter()
            try:
                response_text = runner(case, prompt_text) if runner is not None else ""
                latency_s = round(max(time.perf_counter() - start, 0.0), 6)
                normalized_response = _normalize_text(response_text)
                parsed_composition = _parse_response_composition(normalized_response, response_parser_key)
                case_result = LlmExternalBenchmarkCaseResult(
                    benchmark_id=spec.benchmark_id,
                    benchmark_set_id=benchmark_manifest.benchmark_set_id,
                    benchmark_set_manifest_path=_path_for_storage(
                        benchmark_manifest_path,
                        root=artifact_root,
                    ),
                    target_id=target.target_id,
                    target_label=target.label,
                    target_kind=target.target_kind,
                    control_role=getattr(target, "control_role", None),
                    model_id=getattr(target, "model_id", None),
                    candidate_id=case.candidate_id,
                    source_export_id=case.source_export_id,
                    source_bundle_manifest_path=case.source_bundle_manifest_path,
                    system=case.system,
                    target_family=case.target_family,
                    fidelity_tier=case.fidelity_tier,
                    loss_reasons=case.loss_reasons,
                    diagnostic_codes=case.diagnostic_codes,
                    composition=case.composition,
                    prompt_contract_id=prompt_contract_id,
                    response_parser_key=response_parser_key,
                    response_status="succeeded",
                    parse_status="passed",
                    prompt_text_hash=prompt_hash,
                    response_text_hash=_hash_text(normalized_response),
                    latency_s=latency_s,
                    exact_text_match=normalized_response == _normalize_text(case.emitted_text),
                    composition_match=_composition_match(parsed_composition, case.composition),
                )
                raw_responses.append(
                    _raw_response_record(
                        case=case,
                        prompt_hash=prompt_hash,
                        response_status="succeeded",
                        parse_status="passed",
                        response_text=response_text,
                        latency_s=latency_s,
                    )
                )
            except Exception as exc:
                latency_s = round(max(time.perf_counter() - start, 0.0), 6)
                case_result = LlmExternalBenchmarkCaseResult(
                    benchmark_id=spec.benchmark_id,
                    benchmark_set_id=benchmark_manifest.benchmark_set_id,
                    benchmark_set_manifest_path=_path_for_storage(
                        benchmark_manifest_path,
                        root=artifact_root,
                    ),
                    target_id=target.target_id,
                    target_label=target.label,
                    target_kind=target.target_kind,
                    control_role=getattr(target, "control_role", None),
                    model_id=getattr(target, "model_id", None),
                    candidate_id=case.candidate_id,
                    source_export_id=case.source_export_id,
                    source_bundle_manifest_path=case.source_bundle_manifest_path,
                    system=case.system,
                    target_family=case.target_family,
                    fidelity_tier=case.fidelity_tier,
                    loss_reasons=case.loss_reasons,
                    diagnostic_codes=case.diagnostic_codes,
                    composition=case.composition,
                    prompt_contract_id=prompt_contract_id,
                    response_parser_key=response_parser_key,
                    response_status="runtime_error",
                    parse_status="failed",
                    prompt_text_hash=prompt_hash,
                    latency_s=latency_s,
                    error_detail=str(exc),
                )
                raw_responses.append(
                    _raw_response_record(
                        case=case,
                        prompt_hash=prompt_hash,
                        response_status="runtime_error",
                        parse_status="failed",
                        latency_s=latency_s,
                        error_detail=str(exc),
                    )
                )
            case_results.append(case_result)

        write_jsonl([record.model_dump(mode="json") for record in case_results], case_results_path)
        write_jsonl(raw_responses, raw_responses_path)

        target_manifest = LlmExternalBenchmarkTargetRunManifest(
            benchmark_id=spec.benchmark_id,
            benchmark_set_id=benchmark_manifest.benchmark_set_id,
            benchmark_set_manifest_path=_path_for_storage(benchmark_manifest_path, root=artifact_root),
            target_id=target.target_id,
            target_label=target.label,
            target_kind=target.target_kind,
            control_role=getattr(target, "control_role", None),
            model_id=getattr(target, "model_id", None),
            registration_path=(
                None
                if target.target_kind != "external_target"
                else _path_for_storage(
                    registration_path,
                    root=artifact_root,
                )
            ),
            environment_path=(
                None
                if target.target_kind != "external_target"
                else registration.environment_path
            ),
            smoke_check_path=(
                None
                if target.target_kind != "external_target"
                else registration.smoke_check_path
            ),
            prompt_contract_id=prompt_contract_id,
            response_parser_key=response_parser_key,
            prompt_contract_hash=_hash_text(prompt_contract_id),
            started_at_utc=started_at_utc,
            completed_at_utc=_utc_now(),
            eligible_count=sum(result.response_status != "excluded" for result in case_results),
            excluded_count=sum(result.response_status == "excluded" for result in case_results),
            run_manifest_path=_path_for_storage(run_manifest_path, root=artifact_root),
            case_results_path=_path_for_storage(case_results_path, root=artifact_root),
            raw_responses_path=_path_for_storage(raw_responses_path, root=artifact_root),
            serving_identity=serving_identity if target.target_kind == "internal_control" else None,
        )
        write_json_object(target_manifest.model_dump(mode="json"), run_manifest_path)
        target_manifests[target.target_id] = target_manifest
        target_results[target.target_id] = case_results

    smoke_path = llm_external_benchmark_smoke_path(spec.benchmark_id, root=artifact_root)
    write_json_object({"benchmark_id": spec.benchmark_id, "checks": smoke_records}, smoke_path)

    scorecard_by_case_path = llm_external_benchmark_scorecard_by_case_path(
        spec.benchmark_id,
        root=artifact_root,
    )
    write_jsonl(
        [
            result.model_dump(mode="json")
            for results in target_results.values()
            for result in results
        ],
        scorecard_by_case_path,
    )

    summary_path = (
        llm_external_benchmark_summary_path(spec.benchmark_id, root=artifact_root)
        if out_path is None
        else (out_path if out_path.is_absolute() else (artifact_root / out_path).resolve())
    )
    summary = build_external_benchmark_summary(
        spec,
        target_manifests,
        target_results,
        summary_path=summary_path,
        root=artifact_root,
    )
    write_json_object(summary.model_dump(mode="json"), summary_path)
    return summary


__all__ = [
    "build_external_benchmark_summary",
    "execute_external_benchmark",
    "load_external_benchmark_spec",
]
