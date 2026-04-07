from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from materials_discovery.common.io import load_json_object, load_jsonl, write_json_object, write_jsonl
from materials_discovery.llm import (
    build_external_benchmark_summary,
    LlmExternalBenchmarkSummary,
    LlmExternalTargetSmokeCheck,
    TranslatedBenchmarkIncludedRow,
    TranslatedBenchmarkSetManifest,
    TranslatedBenchmarkSetSpec,
    execute_external_benchmark,
    register_external_target,
    smoke_external_target,
)
from materials_discovery.llm.schema import (
    LlmExternalBenchmarkCaseResult,
    LlmExternalBenchmarkExternalTarget,
    LlmExternalBenchmarkInternalControl,
    LlmExternalBenchmarkSpec,
    LlmExternalBenchmarkTargetRunManifest,
    LlmServingIdentity,
)
from materials_discovery.llm.storage import (
    llm_external_benchmark_scorecard_by_case_path,
    llm_external_benchmark_summary_path,
    llm_external_benchmark_target_case_results_path,
    llm_external_benchmark_target_raw_responses_path,
    llm_external_benchmark_target_run_manifest_path,
    translated_benchmark_excluded_path,
    translated_benchmark_included_path,
    translated_benchmark_manifest_path,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _repo_system_config() -> Path:
    return _repo_root() / "configs" / "systems" / "al_cu_fe_llm_local.yaml"


def _valid_cif_text(label_suffix: str) -> str:
    return "\n".join(
        [
            "# translated candidate payload",
            f"data_demo_{label_suffix}",
            "_symmetry_space_group_name_H-M 'P 1'",
            "_cell_length_a 1.0",
            "_cell_length_b 1.0",
            "_cell_length_c 1.0",
            "_cell_angle_alpha 90.0",
            "_cell_angle_beta 90.0",
            "_cell_angle_gamma 90.0",
            "loop_",
            "_atom_site_label",
            "_atom_site_type_symbol",
            "_atom_site_fract_x",
            "_atom_site_fract_y",
            "_atom_site_fract_z",
            "Al1 Al 0.0 0.0 0.0",
            "Cu1 Cu 0.5 0.5 0.5",
            "Fe1 Fe 0.25 0.25 0.25",
        ]
    )


def _valid_material_string_text() -> str:
    return "\n".join(
        [
            "1.0 1.0 1.0",
            "90.0 90.0 90.0",
            "Al",
            "0.0 0.0 0.0",
            "Cu",
            "0.5 0.5 0.5",
            "Fe",
            "0.25 0.25 0.25",
        ]
    )


def _included_row(
    *,
    candidate_id: str,
    target_family: str = "cif",
    fidelity_tier: str = "anchored",
    emitted_text: str | None = None,
) -> TranslatedBenchmarkIncludedRow:
    payload_name = f"{candidate_id}.cif" if target_family == "cif" else f"{candidate_id}.material_string.txt"
    parser_format = "cif_text" if target_family == "cif" else "crystaltextllm_material_string"
    text = emitted_text or (_valid_cif_text(candidate_id) if target_family == "cif" else _valid_material_string_text())
    return TranslatedBenchmarkIncludedRow(
        benchmark_set_id="al_cu_fe_translated_benchmark_v1",
        source_export_id="phase34_demo_al_cu_fe_cif_v1",
        source_bundle_manifest_path="data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json",
        candidate_id=candidate_id,
        system="Al-Cu-Fe",
        template_family="ico",
        target_family=target_family,
        target_format=parser_format,
        fidelity_tier=fidelity_tier,
        loss_reasons=[] if fidelity_tier in {"exact", "anchored"} else ["coordinate_derivation_required"],
        diagnostic_codes=[] if fidelity_tier in {"exact", "anchored"} else ["coordinate_derivation_required"],
        composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        payload_path=f"data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/payloads/{payload_name}",
        payload_hash=f"hash-{candidate_id}",
        emitted_text=text,
    )


def _write_benchmark_set(root: Path, rows: list[TranslatedBenchmarkIncludedRow]) -> Path:
    manifest_path = translated_benchmark_manifest_path("al_cu_fe_translated_benchmark_v1", root=root)
    included_path = translated_benchmark_included_path("al_cu_fe_translated_benchmark_v1", root=root)
    excluded_path = translated_benchmark_excluded_path("al_cu_fe_translated_benchmark_v1", root=root)
    write_jsonl([row.model_dump(mode="json") for row in rows], included_path)
    write_jsonl([], excluded_path)
    manifest = TranslatedBenchmarkSetManifest(
        benchmark_set_id="al_cu_fe_translated_benchmark_v1",
        contract_path="data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/freeze_contract.json",
        included_inventory_path="data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/included.jsonl",
        excluded_inventory_path="data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/excluded.jsonl",
        source_bundle_manifest_paths=[
            "data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json"
        ],
        source_export_ids=["phase34_demo_al_cu_fe_cif_v1"],
        included_count=len(rows),
        excluded_count=0,
        target_family=rows[0].target_family,
        systems=["Al-Cu-Fe"],
        filter_contract=TranslatedBenchmarkSetSpec(
            benchmark_set_id="al_cu_fe_translated_benchmark_v1",
            bundle_manifest_paths=[
                "data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json"
            ],
            systems=["Al-Cu-Fe"],
            target_family=rows[0].target_family,
            allowed_fidelity_tiers=["exact", "anchored", "approximate", "lossy"],
            loss_posture="allow_explicit_loss",
        ),
    )
    write_json_object(manifest.model_dump(mode="json"), manifest_path)
    return manifest_path


def _write_external_registration_spec(root: Path, *, model_id: str) -> Path:
    snapshot_root = root / "data" / "llm_external_snapshots" / model_id
    snapshot_root.mkdir(parents=True, exist_ok=True)
    write_json_object({"snapshot_id": model_id}, snapshot_root / "manifest.json")
    spec_path = root / f"{model_id}.yaml"
    spec_path.write_text(
        yaml.safe_dump(
            {
                "model_id": model_id,
                "model_family": "CrystaLLM-compatible",
                "supported_systems": ["Al-Cu-Fe"],
                "supported_target_families": ["cif"],
                "runner_key": "transformers_causal_lm",
                "provider": "huggingface",
                "model": f"example-org/{model_id}",
                "model_revision": "demo-sha",
                "tokenizer_revision": "demo-tokenizer",
                "local_snapshot_path": str(snapshot_root.relative_to(root)),
                "snapshot_manifest_path": str((snapshot_root / "manifest.json").relative_to(root)),
                "prompt_contract_id": "translated_cif_v1",
                "response_parser_key": "cif_text",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return spec_path


def _register_external_target(root: Path, *, model_id: str) -> None:
    spec_path = _write_external_registration_spec(root, model_id=model_id)
    register_external_target(spec_path, root=root)
    smoke_external_target(model_id, root=root)


def _write_benchmark_spec(
    root: Path,
    *,
    manifest_path: Path,
    external_targets: list[dict[str, object]],
    internal_controls: list[dict[str, object]],
) -> Path:
    spec_path = root / "al_cu_fe_external_benchmark.yaml"
    payload = {
        "benchmark_id": "al_cu_fe_external_benchmark_v1",
        "benchmark_set_manifest_path": str(manifest_path.relative_to(root)),
        "external_targets": external_targets,
        "internal_controls": internal_controls,
    }
    spec_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return spec_path


def _mock_internal_runner():
    identity = LlmServingIdentity(
        requested_model_lane="general_purpose",
        resolved_model_lane="general_purpose",
        resolved_model_lane_source="configured_lane",
        adapter="openai_compat_v1",
        provider="local",
        model="zomic-general-local-v1",
        effective_api_base="http://localhost:8000",
    )

    def _builder(control, *, root=None):
        del control, root

        def _runner(case: TranslatedBenchmarkIncludedRow, prompt_text: str) -> str:
            del prompt_text
            if case.candidate_id.endswith("001"):
                return case.emitted_text
            return case.emitted_text.replace("Fe1 Fe", "Zn1 Zn")

        return None, identity, _runner

    return _builder


def _case_result(
    *,
    target_id: str,
    target_label: str,
    target_kind: str,
    candidate_id: str,
    fidelity_tier: str,
    exact_text_match: bool,
    composition_match: bool,
    control_role: str | None = None,
    model_id: str | None = None,
) -> LlmExternalBenchmarkCaseResult:
    return LlmExternalBenchmarkCaseResult(
        benchmark_id="al_cu_fe_external_benchmark_v1",
        benchmark_set_id="al_cu_fe_translated_benchmark_v1",
        benchmark_set_manifest_path="data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json",
        target_id=target_id,
        target_label=target_label,
        target_kind=target_kind,
        control_role=control_role,
        model_id=model_id,
        candidate_id=candidate_id,
        source_export_id="phase34_demo_al_cu_fe_cif_v1",
        source_bundle_manifest_path="data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json",
        system="Al-Cu-Fe",
        target_family="cif",
        fidelity_tier=fidelity_tier,
        loss_reasons=[] if fidelity_tier in {"exact", "anchored"} else ["coordinate_derivation_required"],
        diagnostic_codes=[] if fidelity_tier in {"exact", "anchored"} else ["coordinate_derivation_required"],
        composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        prompt_contract_id="translated_cif_v1",
        response_parser_key="cif_text",
        response_status="succeeded",
        parse_status="passed",
        prompt_text_hash=f"prompt-{candidate_id}",
        response_text_hash=f"response-{target_id}-{candidate_id}",
        latency_s=0.01,
        exact_text_match=exact_text_match,
        composition_match=composition_match,
    )


def _run_manifest(
    *,
    target_id: str,
    target_label: str,
    target_kind: str,
    eligible_count: int,
    excluded_count: int = 0,
    control_role: str | None = None,
    model_id: str | None = None,
) -> LlmExternalBenchmarkTargetRunManifest:
    return LlmExternalBenchmarkTargetRunManifest(
        benchmark_id="al_cu_fe_external_benchmark_v1",
        benchmark_set_id="al_cu_fe_translated_benchmark_v1",
        benchmark_set_manifest_path="data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json",
        target_id=target_id,
        target_label=target_label,
        target_kind=target_kind,
        control_role=control_role,
        model_id=model_id,
        registration_path=(
            None
            if target_kind != "external_target"
            else f"data/llm_external_models/{model_id}/registration.json"
        ),
        environment_path=(
            None
            if target_kind != "external_target"
            else f"data/llm_external_models/{model_id}/environment.json"
        ),
        smoke_check_path=(
            None
            if target_kind != "external_target"
            else f"data/llm_external_models/{model_id}/smoke_check.json"
        ),
        prompt_contract_id="translated_cif_v1",
        response_parser_key="cif_text",
        prompt_contract_hash="prompt-contract-hash",
        started_at_utc="2026-04-07T08:00:00Z",
        completed_at_utc="2026-04-07T08:00:01Z",
        eligible_count=eligible_count,
        excluded_count=excluded_count,
        run_manifest_path=f"data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/{target_id}/run_manifest.json",
        case_results_path=f"data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/{target_id}/case_results.jsonl",
        raw_responses_path=f"data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/{target_id}/raw_responses.jsonl",
    )


def test_execute_external_benchmark_writes_per_target_artifacts_and_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_path = _write_benchmark_set(
        tmp_path,
        [
            _included_row(candidate_id="candidate_001", fidelity_tier="exact"),
            _included_row(candidate_id="candidate_002", fidelity_tier="anchored"),
        ],
    )
    _register_external_target(tmp_path, model_id="al_cu_fe_external_cif_demo")
    spec_path = _write_benchmark_spec(
        tmp_path,
        manifest_path=manifest_path,
        external_targets=[
            {
                "target_id": "crystallm_cif_demo",
                "label": "CrystaLLM CIF demo",
                "model_id": "al_cu_fe_external_cif_demo",
                "supported_target_families": ["cif"],
                "supported_systems": ["Al-Cu-Fe"],
            }
        ],
        internal_controls=[
            {
                "target_id": "promoted_internal_control",
                "label": "Promoted internal control",
                "control_role": "promoted_default",
                "system_config_path": str(_repo_system_config()),
                "generation_model_lane": "general_purpose",
                "supported_target_families": ["cif"],
                "supported_systems": ["Al-Cu-Fe"],
                "prompt_contract_id": "translated_cif_v1",
                "response_parser_key": "cif_text",
            }
        ],
    )
    monkeypatch.setattr(
        "materials_discovery.llm.external_benchmark._build_external_runner",
        lambda registration, *, root=None: (lambda case, prompt_text: case.emitted_text),
    )
    monkeypatch.setattr(
        "materials_discovery.llm.external_benchmark._resolve_internal_control_backend",
        _mock_internal_runner(),
    )

    summary = execute_external_benchmark(spec_path, root=tmp_path)

    assert isinstance(summary, LlmExternalBenchmarkSummary)
    assert summary.benchmark_id == "al_cu_fe_external_benchmark_v1"
    assert len(summary.targets) == 2
    assert any("warrants deeper external-model investment" in line for line in summary.recommendation_lines)

    external_target = next(target for target in summary.targets if target.target_id == "crystallm_cif_demo")
    internal_target = next(
        target for target in summary.targets if target.target_id == "promoted_internal_control"
    )
    assert external_target.control_deltas[0].exact_text_match_rate_delta == pytest.approx(0.5)
    assert internal_target.serving_identity is not None

    summary_path = llm_external_benchmark_summary_path(summary.benchmark_id, root=tmp_path)
    external_manifest_path = llm_external_benchmark_target_run_manifest_path(
        summary.benchmark_id,
        "crystallm_cif_demo",
        root=tmp_path,
    )
    external_results_path = llm_external_benchmark_target_case_results_path(
        summary.benchmark_id,
        "crystallm_cif_demo",
        root=tmp_path,
    )
    external_raw_path = llm_external_benchmark_target_raw_responses_path(
        summary.benchmark_id,
        "crystallm_cif_demo",
        root=tmp_path,
    )
    assert summary_path.exists()
    assert external_manifest_path.exists()
    assert external_results_path.exists()
    assert external_raw_path.exists()
    assert len(load_jsonl(external_results_path)) == 2
    assert len(load_jsonl(external_raw_path)) == 2


def test_execute_external_benchmark_records_explicit_target_family_exclusions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_path = _write_benchmark_set(
        tmp_path,
        [
            _included_row(candidate_id="candidate_001", target_family="cif", fidelity_tier="anchored"),
            _included_row(
                candidate_id="candidate_002",
                target_family="material_string",
                fidelity_tier="lossy",
                emitted_text=_valid_material_string_text(),
            ),
        ],
    )
    _register_external_target(tmp_path, model_id="al_cu_fe_external_cif_demo")
    spec_path = _write_benchmark_spec(
        tmp_path,
        manifest_path=manifest_path,
        external_targets=[
            {
                "target_id": "crystallm_cif_demo",
                "label": "CrystaLLM CIF demo",
                "model_id": "al_cu_fe_external_cif_demo",
                "supported_target_families": ["cif"],
                "supported_systems": ["Al-Cu-Fe"],
            }
        ],
        internal_controls=[
            {
                "target_id": "promoted_internal_control",
                "label": "Promoted internal control",
                "control_role": "promoted_default",
                "system_config_path": str(_repo_system_config()),
                "generation_model_lane": "general_purpose",
                "supported_target_families": ["cif"],
                "supported_systems": ["Al-Cu-Fe"],
                "prompt_contract_id": "translated_cif_v1",
                "response_parser_key": "cif_text",
            }
        ],
    )
    monkeypatch.setattr(
        "materials_discovery.llm.external_benchmark._build_external_runner",
        lambda registration, *, root=None: (lambda case, prompt_text: case.emitted_text),
    )
    monkeypatch.setattr(
        "materials_discovery.llm.external_benchmark._resolve_internal_control_backend",
        _mock_internal_runner(),
    )

    summary = execute_external_benchmark(spec_path, root=tmp_path)
    case_results = load_jsonl(
        llm_external_benchmark_target_case_results_path(
            summary.benchmark_id,
            "crystallm_cif_demo",
            root=tmp_path,
        )
    )

    excluded = [row for row in case_results if row["response_status"] == "excluded"]
    assert len(excluded) == 1
    assert excluded[0]["exclusion_reason"] == "target_family_not_supported"

    external_target = next(target for target in summary.targets if target.target_id == "crystallm_cif_demo")
    assert external_target.eligible_count == 1
    assert external_target.excluded_count == 1
    assert set(external_target.by_target_family) == {"cif", "material_string"}
    assert external_target.by_target_family["material_string"].eligible_count == 0

    scorecard_rows = load_jsonl(
        llm_external_benchmark_scorecard_by_case_path(summary.benchmark_id, root=tmp_path)
    )
    assert len(scorecard_rows) == 4


def test_execute_external_benchmark_marks_smoke_failed_external_targets_as_failed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_path = _write_benchmark_set(
        tmp_path,
        [_included_row(candidate_id="candidate_001", fidelity_tier="anchored")],
    )
    _register_external_target(tmp_path, model_id="al_cu_fe_external_cif_demo")
    spec_path = _write_benchmark_spec(
        tmp_path,
        manifest_path=manifest_path,
        external_targets=[
            {
                "target_id": "crystallm_cif_demo",
                "label": "CrystaLLM CIF demo",
                "model_id": "al_cu_fe_external_cif_demo",
                "supported_target_families": ["cif"],
                "supported_systems": ["Al-Cu-Fe"],
            }
        ],
        internal_controls=[
            {
                "target_id": "promoted_internal_control",
                "label": "Promoted internal control",
                "control_role": "promoted_default",
                "system_config_path": str(_repo_system_config()),
                "generation_model_lane": "general_purpose",
                "supported_target_families": ["cif"],
                "supported_systems": ["Al-Cu-Fe"],
                "prompt_contract_id": "translated_cif_v1",
                "response_parser_key": "cif_text",
            }
        ],
    )
    monkeypatch.setattr(
        "materials_discovery.llm.external_benchmark.smoke_external_target",
        lambda model_id, *, root=None: LlmExternalTargetSmokeCheck(
            model_id=model_id,
            status="failed",
            registration_fingerprint="deadbeefcafe1234",
            checked_at_utc="2026-04-07T08:00:00Z",
            latency_s=0.01,
            environment_path="data/llm_external_models/al_cu_fe_external_cif_demo/environment.json",
            runner_key="transformers_causal_lm",
            provider="huggingface",
            model="example-org/al_cu_fe_external_cif_demo",
            model_revision="demo-sha",
            local_snapshot_path="data/llm_external_snapshots/al_cu_fe_external_cif_demo",
            detail="smoke check failed in test",
        ),
    )
    monkeypatch.setattr(
        "materials_discovery.llm.external_benchmark._resolve_internal_control_backend",
        _mock_internal_runner(),
    )

    summary = execute_external_benchmark(spec_path, root=tmp_path)

    assert "crystallm_cif_demo" in summary.failed_targets
    external_target = next(target for target in summary.targets if target.target_id == "crystallm_cif_demo")
    assert external_target.failed is True
    assert any("failed benchmark execution or smoke checks" in line for line in external_target.recommendation_lines)

    case_results = load_jsonl(
        llm_external_benchmark_target_case_results_path(
            summary.benchmark_id,
            "crystallm_cif_demo",
            root=tmp_path,
        )
    )
    assert case_results[0]["exclusion_reason"] == "smoke_check_failed"


def test_build_external_benchmark_summary_privileges_periodic_safe_slice_for_recommendations(
    tmp_path: Path,
) -> None:
    spec = LlmExternalBenchmarkSpec(
        benchmark_id="al_cu_fe_external_benchmark_v1",
        benchmark_set_manifest_path="data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json",
        external_targets=[
            LlmExternalBenchmarkExternalTarget(
                target_id="crystallm_cif_demo",
                label="CrystaLLM CIF demo",
                model_id="al_cu_fe_external_cif_demo",
                supported_target_families=["cif"],
                supported_systems=["Al-Cu-Fe"],
                prompt_contract_id="translated_cif_v1",
                response_parser_key="cif_text",
            )
        ],
        internal_controls=[
            LlmExternalBenchmarkInternalControl(
                target_id="promoted_internal_control",
                label="Promoted internal control",
                control_role="promoted_default",
                system_config_path=str(_repo_system_config()),
                generation_model_lane="general_purpose",
                supported_target_families=["cif"],
                supported_systems=["Al-Cu-Fe"],
                prompt_contract_id="translated_cif_v1",
                response_parser_key="cif_text",
            )
        ],
    )
    target_manifests = {
        "crystallm_cif_demo": _run_manifest(
            target_id="crystallm_cif_demo",
            target_label="CrystaLLM CIF demo",
            target_kind="external_target",
            model_id="al_cu_fe_external_cif_demo",
            eligible_count=4,
        ),
        "promoted_internal_control": _run_manifest(
            target_id="promoted_internal_control",
            target_label="Promoted internal control",
            target_kind="internal_control",
            control_role="promoted_default",
            eligible_count=4,
        ),
    }
    target_results = {
        "crystallm_cif_demo": [
            _case_result(
                target_id="crystallm_cif_demo",
                target_label="CrystaLLM CIF demo",
                target_kind="external_target",
                model_id="al_cu_fe_external_cif_demo",
                candidate_id="safe_exact_001",
                fidelity_tier="exact",
                exact_text_match=False,
                composition_match=False,
            ),
            _case_result(
                target_id="crystallm_cif_demo",
                target_label="CrystaLLM CIF demo",
                target_kind="external_target",
                model_id="al_cu_fe_external_cif_demo",
                candidate_id="lossy_001",
                fidelity_tier="lossy",
                exact_text_match=True,
                composition_match=True,
            ),
            _case_result(
                target_id="crystallm_cif_demo",
                target_label="CrystaLLM CIF demo",
                target_kind="external_target",
                model_id="al_cu_fe_external_cif_demo",
                candidate_id="lossy_002",
                fidelity_tier="lossy",
                exact_text_match=True,
                composition_match=True,
            ),
            _case_result(
                target_id="crystallm_cif_demo",
                target_label="CrystaLLM CIF demo",
                target_kind="external_target",
                model_id="al_cu_fe_external_cif_demo",
                candidate_id="lossy_003",
                fidelity_tier="lossy",
                exact_text_match=True,
                composition_match=True,
            ),
        ],
        "promoted_internal_control": [
            _case_result(
                target_id="promoted_internal_control",
                target_label="Promoted internal control",
                target_kind="internal_control",
                control_role="promoted_default",
                candidate_id="safe_exact_001",
                fidelity_tier="exact",
                exact_text_match=True,
                composition_match=True,
            ),
            _case_result(
                target_id="promoted_internal_control",
                target_label="Promoted internal control",
                target_kind="internal_control",
                control_role="promoted_default",
                candidate_id="lossy_001",
                fidelity_tier="lossy",
                exact_text_match=False,
                composition_match=False,
            ),
            _case_result(
                target_id="promoted_internal_control",
                target_label="Promoted internal control",
                target_kind="internal_control",
                control_role="promoted_default",
                candidate_id="lossy_002",
                fidelity_tier="lossy",
                exact_text_match=False,
                composition_match=False,
            ),
            _case_result(
                target_id="promoted_internal_control",
                target_label="Promoted internal control",
                target_kind="internal_control",
                control_role="promoted_default",
                candidate_id="lossy_003",
                fidelity_tier="lossy",
                exact_text_match=False,
                composition_match=False,
            ),
        ],
    }

    summary = build_external_benchmark_summary(
        spec,
        target_manifests,
        target_results,
        summary_path=tmp_path
        / "data"
        / "benchmarks"
        / "llm_external"
        / "al_cu_fe_external_benchmark_v1"
        / "benchmark_summary.json",
        root=tmp_path,
    )

    external_target = next(target for target in summary.targets if target.target_id == "crystallm_cif_demo")
    assert external_target.control_deltas[0].exact_text_match_rate_delta == pytest.approx(0.5)
    assert external_target.by_fidelity_tier["exact"].exact_text_match_rate == pytest.approx(0.0)
    assert external_target.by_fidelity_tier["lossy"].exact_text_match_rate == pytest.approx(1.0)
    assert any("not competitive with the current control arm on the periodic-safe slice" in line for line in external_target.recommendation_lines)
    assert any("periodic-safe slice" in line for line in summary.recommendation_lines)
