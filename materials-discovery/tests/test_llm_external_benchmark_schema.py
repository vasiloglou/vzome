from __future__ import annotations

from typing import get_args

import pytest

from materials_discovery.llm import (
    LlmExternalBenchmarkCaseResult,
    LlmExternalBenchmarkControlDelta,
    LlmExternalBenchmarkControlRole,
    LlmExternalBenchmarkExclusionReason,
    LlmExternalBenchmarkExternalTarget,
    LlmExternalBenchmarkInternalControl,
    LlmExternalBenchmarkParseStatus,
    LlmExternalBenchmarkResponseStatus,
    LlmExternalBenchmarkSliceSummary,
    LlmExternalBenchmarkSpec,
    LlmExternalBenchmarkSummary,
    LlmExternalBenchmarkTargetKind,
    LlmExternalBenchmarkTargetRunManifest,
    LlmExternalBenchmarkTargetSummary,
    LlmServingIdentity,
)
from materials_discovery.llm.storage import (
    llm_external_benchmark_dir,
    llm_external_benchmark_scorecard_by_case_path,
    llm_external_benchmark_summary_path,
    llm_external_benchmark_target_case_results_path,
    llm_external_benchmark_target_dir,
    llm_external_benchmark_target_raw_responses_path,
    llm_external_benchmark_target_run_manifest_path,
    llm_external_target_dir,
)


def _valid_external_target_kwargs() -> dict[str, object]:
    return {
        "target_id": "crystallm_cif_demo",
        "label": "CrystaLLM CIF demo",
        "model_id": "al_cu_fe_external_cif_demo",
        "supported_target_families": ["cif"],
        "supported_systems": [" Al-Cu-Fe ", "Sc-Zn", "Al-Cu-Fe"],
        "prompt_contract_id": " translated_cif_v1 ",
        "response_parser_key": " cif_text ",
        "notes": "  external benchmark subject  ",
    }


def _valid_internal_control_kwargs() -> dict[str, object]:
    return {
        "target_id": "promoted_internal_control",
        "label": "Promoted internal control",
        "control_role": "promoted_default",
        "system_config_path": "configs/systems/al_cu_fe_llm_local.yaml",
        "generation_model_lane": "general_purpose",
        "supported_target_families": ["cif"],
        "supported_systems": [" Al-Cu-Fe "],
        "prompt_contract_id": "translated_cif_v1",
        "response_parser_key": "cif_text",
        "notes": "  current promoted family lane  ",
    }


def _valid_spec_kwargs() -> dict[str, object]:
    return {
        "benchmark_id": "al_cu_fe_external_benchmark_v1",
        "benchmark_set_manifest_path": (
            "data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json"
        ),
        "external_targets": [_valid_external_target_kwargs()],
        "internal_controls": [_valid_internal_control_kwargs()],
        "operator_note": "  small translated benchmark comparison  ",
    }


def _valid_case_result_kwargs() -> dict[str, object]:
    return {
        "benchmark_id": "al_cu_fe_external_benchmark_v1",
        "benchmark_set_id": "al_cu_fe_translated_benchmark_v1",
        "benchmark_set_manifest_path": (
            "data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json"
        ),
        "target_id": "crystallm_cif_demo",
        "target_label": "CrystaLLM CIF demo",
        "target_kind": "external_target",
        "model_id": "al_cu_fe_external_cif_demo",
        "candidate_id": "al_cu_fe_fixture_periodic_001",
        "source_export_id": "phase34_demo_al_cu_fe_cif_v1",
        "source_bundle_manifest_path": (
            "data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json"
        ),
        "system": "Al-Cu-Fe",
        "target_family": "cif",
        "fidelity_tier": "anchored",
        "loss_reasons": ["coordinate_derivation_required"],
        "diagnostic_codes": ["coordinate_derivation_required"],
        "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        "prompt_contract_id": "translated_cif_v1",
        "response_parser_key": "cif_text",
        "response_status": "succeeded",
        "parse_status": "passed",
        "prompt_text_hash": "prompt-hash-1234",
        "response_text_hash": "response-hash-5678",
        "latency_s": 0.42,
        "exact_text_match": True,
        "composition_match": True,
    }


def _valid_serving_identity() -> LlmServingIdentity:
    return LlmServingIdentity(
        requested_model_lane="general_purpose",
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        adapter="openai_compat_v1",
        provider="local",
        model="zomic-general-local-v1",
        effective_api_base="http://localhost:8000",
    )


def test_external_benchmark_spec_requires_benchmark_id_and_both_target_classes() -> None:
    with pytest.raises(ValueError, match="field must not be blank"):
        LlmExternalBenchmarkSpec(**{**_valid_spec_kwargs(), "benchmark_id": " "})

    with pytest.raises(ValueError, match="external_targets must not be empty"):
        LlmExternalBenchmarkSpec(**{**_valid_spec_kwargs(), "external_targets": []})

    with pytest.raises(ValueError, match="internal_controls must not be empty"):
        LlmExternalBenchmarkSpec(**{**_valid_spec_kwargs(), "internal_controls": []})

    with pytest.raises(ValueError, match="benchmark target IDs must be unique"):
        duplicated_external = {**_valid_external_target_kwargs(), "target_id": "shared_target"}
        duplicated_control = {**_valid_internal_control_kwargs(), "target_id": "shared_target"}
        LlmExternalBenchmarkSpec(
            **{
                **_valid_spec_kwargs(),
                "external_targets": [duplicated_external],
                "internal_controls": [duplicated_control],
            }
        )


def test_external_benchmark_spec_exposes_explicit_external_and_internal_target_variants() -> None:
    spec = LlmExternalBenchmarkSpec(**_valid_spec_kwargs())
    external_target = spec.external_targets[0]
    internal_control = spec.internal_controls[0]

    assert spec.benchmark_id == "al_cu_fe_external_benchmark_v1"
    assert spec.operator_note == "small translated benchmark comparison"

    assert isinstance(external_target, LlmExternalBenchmarkExternalTarget)
    assert external_target.target_kind == "external_target"
    assert external_target.model_id == "al_cu_fe_external_cif_demo"
    assert external_target.supported_systems == ["Al-Cu-Fe", "Sc-Zn"]
    assert external_target.prompt_contract_id == "translated_cif_v1"
    assert external_target.response_parser_key == "cif_text"

    assert isinstance(internal_control, LlmExternalBenchmarkInternalControl)
    assert internal_control.target_kind == "internal_control"
    assert internal_control.control_role == "promoted_default"
    assert internal_control.generation_model_lane == "general_purpose"
    assert internal_control.supported_systems == ["Al-Cu-Fe"]


def test_external_benchmark_case_result_preserves_lineage_metrics_and_exclusion_state() -> None:
    case_result = LlmExternalBenchmarkCaseResult(**_valid_case_result_kwargs())

    assert case_result.target_kind == "external_target"
    assert case_result.target_family == "cif"
    assert case_result.fidelity_tier == "anchored"
    assert case_result.loss_reasons == ["coordinate_derivation_required"]
    assert case_result.exact_text_match is True
    assert case_result.composition["Al"] == pytest.approx(0.7)

    excluded = LlmExternalBenchmarkCaseResult(
        **{
            **_valid_case_result_kwargs(),
            "response_status": "excluded",
            "parse_status": "not_attempted",
            "exclusion_reason": "target_family_not_supported",
            "exclusion_detail": "material-string-only target",
            "response_text_hash": None,
            "exact_text_match": None,
            "composition_match": None,
            "latency_s": None,
        }
    )
    assert excluded.exclusion_reason == "target_family_not_supported"
    assert excluded.parse_status == "not_attempted"

    with pytest.raises(ValueError, match="excluded results must record exclusion_reason"):
        LlmExternalBenchmarkCaseResult(
            **{
                **_valid_case_result_kwargs(),
                "response_status": "excluded",
                "parse_status": "not_attempted",
                "exclusion_reason": None,
            }
        )


def test_external_benchmark_run_manifest_and_summary_preserve_paths_counts_and_deltas() -> None:
    run_manifest = LlmExternalBenchmarkTargetRunManifest(
        benchmark_id="al_cu_fe_external_benchmark_v1",
        benchmark_set_id="al_cu_fe_translated_benchmark_v1",
        benchmark_set_manifest_path=(
            "data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json"
        ),
        target_id="promoted_internal_control",
        target_label="Promoted internal control",
        target_kind="internal_control",
        control_role="promoted_default",
        prompt_contract_id="translated_cif_v1",
        response_parser_key="cif_text",
        prompt_contract_hash="prompt-hash-1234",
        started_at_utc="2026-04-07T07:30:00Z",
        completed_at_utc="2026-04-07T07:31:00Z",
        eligible_count=12,
        excluded_count=3,
        run_manifest_path=(
            "data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/"
            "promoted_internal_control/run_manifest.json"
        ),
        case_results_path=(
            "data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/"
            "promoted_internal_control/case_results.jsonl"
        ),
        raw_responses_path=(
            "data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/"
            "promoted_internal_control/raw_responses.jsonl"
        ),
        serving_identity=_valid_serving_identity(),
    )

    assert run_manifest.control_role == "promoted_default"
    assert run_manifest.run_manifest_path.endswith("run_manifest.json")
    assert run_manifest.case_results_path.endswith("case_results.jsonl")
    assert run_manifest.raw_responses_path.endswith("raw_responses.jsonl")

    slice_summary = LlmExternalBenchmarkSliceSummary(
        eligible_count=12,
        excluded_count=3,
        response_success_rate=0.75,
        parse_success_rate=0.75,
        exact_text_match_rate=0.5,
        composition_match_rate=0.666667,
        mean_latency_s=0.42,
    )
    delta = LlmExternalBenchmarkControlDelta(
        control_target_id="promoted_internal_control",
        control_label="Promoted internal control",
        control_role="promoted_default",
        shared_eligible_count=10,
        parse_success_rate_delta=0.1,
        exact_text_match_rate_delta=-0.05,
        composition_match_rate_delta=0.08,
    )
    target_summary = LlmExternalBenchmarkTargetSummary(
        target_id="crystallm_cif_demo",
        target_label="CrystaLLM CIF demo",
        target_kind="external_target",
        model_id="al_cu_fe_external_cif_demo",
        registration_path="data/llm_external_models/al_cu_fe_external_cif_demo/registration.json",
        environment_path="data/llm_external_models/al_cu_fe_external_cif_demo/environment.json",
        smoke_check_path="data/llm_external_models/al_cu_fe_external_cif_demo/smoke_check.json",
        run_manifest_path="data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/crystallm_cif_demo/run_manifest.json",
        eligible_count=12,
        excluded_count=3,
        overall=slice_summary,
        by_target_family={"cif": slice_summary},
        by_fidelity_tier={"anchored": slice_summary},
        control_deltas=[delta],
        recommendation_lines=["Targeted follow-up on periodic-safe CIF slice."],
        failed=False,
    )
    summary = LlmExternalBenchmarkSummary(
        benchmark_id="al_cu_fe_external_benchmark_v1",
        benchmark_set_id="al_cu_fe_translated_benchmark_v1",
        benchmark_set_manifest_path=(
            "data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json"
        ),
        generated_at_utc="2026-04-07T07:32:00Z",
        targets=[target_summary],
        recommendation_lines=["Only the periodic-safe CIF slice supports follow-up."],
        failed_targets=[],
        summary_path="data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/benchmark_summary.json",
    )

    assert summary.targets[0].control_deltas[0].shared_eligible_count == 10
    assert summary.targets[0].by_target_family["cif"].exact_text_match_rate == pytest.approx(0.5)
    assert summary.summary_path.endswith("benchmark_summary.json")


def test_external_benchmark_vocabularies_are_typed_and_stable() -> None:
    assert set(get_args(LlmExternalBenchmarkTargetKind)) == {
        "external_target",
        "internal_control",
    }
    assert set(get_args(LlmExternalBenchmarkControlRole)) == {
        "promoted_default",
        "explicit_pin",
    }
    assert set(get_args(LlmExternalBenchmarkResponseStatus)) == {
        "succeeded",
        "excluded",
        "runtime_error",
    }
    assert set(get_args(LlmExternalBenchmarkParseStatus)) == {
        "passed",
        "failed",
        "not_attempted",
    }
    assert set(get_args(LlmExternalBenchmarkExclusionReason)) == {
        "target_family_not_supported",
        "system_not_supported",
        "smoke_check_failed",
    }


def test_external_benchmark_storage_helpers_use_dedicated_benchmark_root(tmp_path) -> None:
    benchmark_id = "al_cu_fe_external_benchmark_v1"
    target_id = "crystallm_cif_demo"
    benchmark_dir = llm_external_benchmark_dir(benchmark_id, root=tmp_path)
    target_dir = llm_external_benchmark_target_dir(benchmark_id, target_id, root=tmp_path)

    assert benchmark_dir == tmp_path / "data" / "benchmarks" / "llm_external" / benchmark_id
    assert llm_external_benchmark_summary_path(benchmark_id, root=tmp_path) == (
        benchmark_dir / "benchmark_summary.json"
    )
    assert llm_external_benchmark_scorecard_by_case_path(benchmark_id, root=tmp_path) == (
        benchmark_dir / "scorecard_by_case.jsonl"
    )
    assert target_dir == benchmark_dir / "targets" / target_id
    assert llm_external_benchmark_target_run_manifest_path(
        benchmark_id, target_id, root=tmp_path
    ) == (target_dir / "run_manifest.json")
    assert llm_external_benchmark_target_case_results_path(
        benchmark_id, target_id, root=tmp_path
    ) == (target_dir / "case_results.jsonl")
    assert llm_external_benchmark_target_raw_responses_path(
        benchmark_id, target_id, root=tmp_path
    ) == (target_dir / "raw_responses.jsonl")
    assert benchmark_dir != llm_external_target_dir(benchmark_id, root=tmp_path)


def test_external_benchmark_storage_helpers_reject_blank_ids(tmp_path) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        llm_external_benchmark_dir(" ", root=tmp_path)

    with pytest.raises(ValueError, match="must not be blank"):
        llm_external_benchmark_target_dir("bench_v1", " ", root=tmp_path)
