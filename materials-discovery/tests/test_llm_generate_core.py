from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.common.io import load_json_object, load_jsonl, load_yaml, write_jsonl
from materials_discovery.common.schema import CandidateRecord, SystemConfig
from materials_discovery.common.stage_metrics import llm_generation_metrics
from materials_discovery.llm.eval_set import load_eval_set
from materials_discovery.llm.generate import generate_llm_candidates
from materials_discovery.llm.prompting import (
    build_generation_prompt,
    load_seed_zomic_text,
    select_conditioning_examples,
)
from materials_discovery.llm.schema import LlmEvalSetExample


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _config_data(name: str) -> dict[str, object]:
    return load_yaml(_workspace() / "configs" / "systems" / name)


def _prototype_path(name: str) -> Path:
    return _workspace() / "data" / "prototypes" / name


def _write_compile_outputs(artifact_root: Path, fixture_name: str) -> tuple[str, str]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    orbit_library_path = artifact_root / "compiled.json"
    orbit_library_path.write_text(
        _prototype_path(fixture_name).read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    raw_export_path = artifact_root / "compiled.raw.json"
    raw_export_path.write_text("{}", encoding="utf-8")
    return str(raw_export_path), str(orbit_library_path)


def test_prompt_builder_and_seed_loader_include_expected_context(tmp_path: Path) -> None:
    config = SystemConfig.model_validate(_config_data("al_cu_fe_llm_mock.yaml"))
    seed_path = tmp_path / "seed.zomic"
    seed_path.write_text("label seed.demo\n", encoding="utf-8")

    seed_text = load_seed_zomic_text(seed_path)
    prompt = build_generation_prompt(config, count=3, seed_zomic_text=seed_text)

    assert "SYSTEM_NAME: Al-Cu-Fe" in prompt
    assert "TEMPLATE_FAMILY: icosahedral_approximant_1_1" in prompt
    assert "- Al: min=0.6000, max=0.8000" in prompt
    assert "SEED_ZOMIC" in prompt
    assert "label seed.demo" in prompt


def test_prompt_builder_can_include_conditioning_examples() -> None:
    config = SystemConfig.model_validate(_config_data("al_cu_fe_llm_mock.yaml"))
    examples = [
        LlmEvalSetExample(
            example_id="eval_001",
            system="Al-Cu-Fe",
            release_tier="gold",
            fidelity_tier="exact",
            source_family="materials_design",
            source_record_id="eval_001",
            composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            labels=["demo"],
            orbit_names=["orbit.demo"],
            tags=["gold"],
            properties={"template_family": "icosahedral_approximant_1_1"},
            zomic_text="label demo.site\n",
        )
    ]

    prompt = build_generation_prompt(
        config,
        count=2,
        seed_zomic_text=None,
        conditioning_examples=examples,
    )

    assert "CONDITIONING_EXAMPLES" in prompt
    assert "EXAMPLE_ID: eval_001" in prompt
    assert "label demo.site" in prompt


def test_prompt_builder_places_instruction_deltas_before_seed_and_examples() -> None:
    config = SystemConfig.model_validate(_config_data("al_cu_fe_llm_mock.yaml"))
    examples = [
        LlmEvalSetExample(
            example_id="eval_001",
            system="Al-Cu-Fe",
            release_tier="gold",
            fidelity_tier="exact",
            source_family="materials_design",
            source_record_id="eval_001",
            composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            labels=["demo"],
            orbit_names=["orbit.demo"],
            tags=["gold"],
            properties={"template_family": "icosahedral_approximant_1_1"},
            zomic_text="label demo.site\n",
        )
    ]

    prompt = build_generation_prompt(
        config,
        count=1,
        seed_zomic_text="label seed.demo\n",
        conditioning_examples=examples,
        instruction_deltas=[
            "Prefer parser-safe symmetry annotations.",
            "Keep motifs benchmark-aligned.",
        ],
    )

    assert prompt.index("Prefer parser-safe symmetry annotations.") < prompt.index("SEED_ZOMIC")
    assert prompt.index("Keep motifs benchmark-aligned.") < prompt.index(
        "CONDITIONING_EXAMPLES"
    )


def test_generate_llm_candidates_writes_run_artifacts_and_candidate_records(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = SystemConfig.model_validate(_config_data("al_cu_fe_llm_mock.yaml"))
    workspace = tmp_path / "workspace"
    output_path = workspace / "data" / "candidates" / "al_cu_fe_candidates.jsonl"

    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: workspace)

    def _fake_compile(
        zomic_text: str,
        *,
        artifact_root: Path | None = None,
        **_: object,
    ) -> dict[str, object]:
        assert zomic_text.strip()
        assert artifact_root is not None
        raw_export_path, orbit_library_path = _write_compile_outputs(
            artifact_root,
            "al_cu_fe_mackay_1_1.json",
        )
        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "error_kind": None,
            "error_message": None,
            "raw_export_path": raw_export_path,
            "orbit_library_path": orbit_library_path,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
        }

    monkeypatch.setattr("materials_discovery.llm.generate.compile_zomic_script", _fake_compile)

    summary = generate_llm_candidates(config, output_path, count=2)

    assert summary.generated_count == 2
    assert summary.attempt_count == 2
    assert summary.parse_pass_count == 2
    assert summary.compile_pass_count == 2

    run_dir = Path(summary.run_manifest_path).parent
    assert (run_dir / "prompt.json").exists()
    assert (run_dir / "attempts.jsonl").exists()
    assert (run_dir / "compile_results.jsonl").exists()
    assert (run_dir / "run_manifest.json").exists()

    candidates = [CandidateRecord.model_validate(row) for row in load_jsonl(output_path)]
    assert len(candidates) == 2
    assert candidates[0].provenance["source"] == "llm"
    assert candidates[0].provenance["llm_adapter"] == "llm_fixture_v1"
    assert candidates[0].provenance["llm_provider"] == "mock"


def test_generate_llm_candidates_records_campaign_metadata_in_run_manifest_and_provenance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = SystemConfig.model_validate(_config_data("al_cu_fe_llm_mock.yaml"))
    workspace = tmp_path / "workspace"
    output_path = workspace / "data" / "candidates" / "al_cu_fe_campaign_candidates.jsonl"

    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: workspace)

    def _fake_compile(
        zomic_text: str,
        *,
        artifact_root: Path | None = None,
        **_: object,
    ) -> dict[str, object]:
        assert zomic_text.strip()
        assert artifact_root is not None
        raw_export_path, orbit_library_path = _write_compile_outputs(
            artifact_root,
            "al_cu_fe_mackay_1_1.json",
        )
        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "error_kind": None,
            "error_message": None,
            "raw_export_path": raw_export_path,
            "orbit_library_path": orbit_library_path,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
        }

    monkeypatch.setattr("materials_discovery.llm.generate.compile_zomic_script", _fake_compile)

    summary = generate_llm_candidates(
        config,
        output_path,
        count=1,
        prompt_instruction_deltas=[
            "Prefer parser-safe symmetry annotations.",
            "Keep motifs benchmark-aligned.",
        ],
        campaign_metadata={
            "campaign_id": "campaign-001",
            "launch_id": "launch-001",
            "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
            "proposal_id": "proposal-001",
            "approval_id": "approval-001",
            "requested_model_lanes": ["general_purpose"],
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
            "launch_summary_path": "data/llm_campaigns/campaign-001/launches/launch-001/launch_summary.json",
        },
    )

    run_manifest = load_json_object(Path(summary.run_manifest_path))
    assert run_manifest["campaign_id"] == "campaign-001"
    assert run_manifest["launch_id"] == "launch-001"
    assert run_manifest["resolved_model_lane_source"] == "configured_lane"
    assert run_manifest["conditioning_example_ids"] == []

    prompt_payload = load_json_object(Path(summary.run_manifest_path).parent / "prompt.json")
    assert prompt_payload["request"]["prompt_instruction_deltas"] == [
        "Prefer parser-safe symmetry annotations.",
        "Keep motifs benchmark-aligned.",
    ]

    candidates = [CandidateRecord.model_validate(row) for row in load_jsonl(output_path)]
    assert candidates[0].provenance["llm_campaign"] == {
        "campaign_id": "campaign-001",
        "launch_id": "launch-001",
        "proposal_id": "proposal-001",
        "approval_id": "approval-001",
        "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
    }


def test_generate_llm_candidates_records_conditioning_example_ids(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    data = _config_data("al_cu_fe_llm_mock.yaml")
    data["llm_generate"]["example_pack_path"] = "eval_set.jsonl"
    data["llm_generate"]["max_conditioning_examples"] = 1
    config = SystemConfig.model_validate(data)
    workspace = tmp_path / "workspace"
    output_path = workspace / "data" / "candidates" / "al_cu_fe_candidates.jsonl"
    eval_set_path = tmp_path / "eval_set.jsonl"
    write_jsonl(
        [
            LlmEvalSetExample(
                example_id="eval_001",
                system="Al-Cu-Fe",
                release_tier="gold",
                fidelity_tier="exact",
                source_family="materials_design",
                source_record_id="eval_001",
                composition={"Al": 0.71, "Cu": 0.19, "Fe": 0.1},
                labels=["demo"],
                orbit_names=["orbit.demo"],
                tags=["gold"],
                properties={"template_family": "icosahedral_approximant_1_1"},
                zomic_text="label conditioning.site\n",
            ).model_dump(mode="json")
        ],
        eval_set_path,
    )
    assert load_eval_set(eval_set_path)[0].example_id == "eval_001"

    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: workspace)

    def _fake_compile(
        zomic_text: str,
        *,
        artifact_root: Path | None = None,
        **_: object,
    ) -> dict[str, object]:
        assert zomic_text.strip()
        assert artifact_root is not None
        raw_export_path, orbit_library_path = _write_compile_outputs(
            artifact_root,
            "al_cu_fe_mackay_1_1.json",
        )
        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "error_kind": None,
            "error_message": None,
            "raw_export_path": raw_export_path,
            "orbit_library_path": orbit_library_path,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
        }

    monkeypatch.setattr("materials_discovery.llm.generate.compile_zomic_script", _fake_compile)

    summary = generate_llm_candidates(
        config,
        output_path,
        count=1,
        config_path=tmp_path / "al_cu_fe_llm_mock.yaml",
    )

    run_dir = Path(summary.run_manifest_path).parent
    prompt_payload = load_json_object(run_dir / "prompt.json")
    assert prompt_payload["conditioning_example_ids"] == ["eval_001"]

    manifest_payload = load_json_object(run_dir / "run_manifest.json")
    assert manifest_payload["conditioning_example_ids"] == ["eval_001"]
    assert manifest_payload["example_pack_path"] == str(eval_set_path)


def test_generate_llm_candidates_preserves_failed_attempts_and_retry_cap(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    data = _config_data("al_cu_fe_llm_mock.yaml")
    data["llm_generate"]["max_attempts"] = 2
    config = SystemConfig.model_validate(data)
    workspace = tmp_path / "workspace"
    output_path = workspace / "data" / "candidates" / "al_cu_fe_candidates.jsonl"

    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: workspace)

    def _fake_compile(
        zomic_text: str,
        *,
        artifact_root: Path | None = None,
        **_: object,
    ) -> dict[str, object]:
        del zomic_text, artifact_root
        return {
            "parse_status": "failed",
            "compile_status": "failed",
            "error_kind": "parse_error",
            "error_message": "synthetic parse failure",
            "raw_export_path": None,
            "orbit_library_path": None,
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
        }

    monkeypatch.setattr("materials_discovery.llm.generate.compile_zomic_script", _fake_compile)

    summary = generate_llm_candidates(config, output_path, count=1)

    assert summary.generated_count == 0
    assert summary.attempt_count == 2
    attempts = load_jsonl(Path(summary.run_manifest_path).parent / "attempts.jsonl")
    assert len(attempts) == 2
    assert attempts[0]["error_kind"] == "parse_error"
    assert load_jsonl(output_path) == []


def test_generate_llm_candidates_validates_seed_before_provider_calls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = SystemConfig.model_validate(_config_data("al_cu_fe_llm_mock.yaml"))
    workspace = tmp_path / "workspace"
    seed_path = tmp_path / "seed.zomic"
    seed_path.write_text("label seed.demo\n", encoding="utf-8")

    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: workspace)

    calls = {"generate": 0, "compile": 0}

    class _NeverCalledAdapter:
        def generate(self, request):  # pragma: no cover - guarded by assertion
            del request
            calls["generate"] += 1
            raise AssertionError("provider should not be called when seed validation fails")

    def _failing_seed_compile(
        zomic_text: str,
        *,
        prototype_key: str,
        **_: object,
    ) -> dict[str, object]:
        del zomic_text
        calls["compile"] += 1
        if prototype_key.endswith("seed_validation"):
            return {
                "parse_status": "failed",
                "compile_status": "failed",
                "error_kind": "parse_error",
                "error_message": "seed parse failed",
                "raw_export_path": None,
                "orbit_library_path": None,
                "cell_scale_used": 10.0,
                "geometry_equivalence": None,
                "geometry_error": None,
            }
        raise AssertionError("no generation compile should happen after seed failure")

    monkeypatch.setattr(
        "materials_discovery.llm.generate.resolve_llm_adapter",
        lambda *args, **kwargs: _NeverCalledAdapter(),
    )
    monkeypatch.setattr("materials_discovery.llm.generate.compile_zomic_script", _failing_seed_compile)

    with pytest.raises(ValueError, match="Seed Zomic failed validation"):
        generate_llm_candidates(
            config,
            workspace / "data" / "candidates" / "seed.jsonl",
            count=1,
            seed_zomic_path=seed_path,
        )

    assert calls["compile"] == 1
    assert calls["generate"] == 0


def test_generate_llm_candidates_fails_early_for_missing_seed_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = SystemConfig.model_validate(_config_data("al_cu_fe_llm_mock.yaml"))
    workspace = tmp_path / "workspace"
    missing_seed = tmp_path / "missing.zomic"

    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: workspace)

    with pytest.raises(FileNotFoundError, match="Seed Zomic file not found"):
        generate_llm_candidates(
            config,
            workspace / "data" / "candidates" / "missing.jsonl",
            count=1,
            seed_zomic_path=missing_seed,
        )


def test_llm_generation_metrics_capture_parse_compile_and_success_rates() -> None:
    metrics = llm_generation_metrics(
        requested_count=4,
        generated_count=2,
        attempt_count=5,
        parse_pass_count=4,
        compile_pass_count=3,
    )

    assert metrics["parse_pass_rate"] == 0.8
    assert metrics["compile_pass_rate"] == 0.6
    assert metrics["generation_success_rate"] == 0.5


def test_select_conditioning_examples_prefers_same_system_and_nearest_composition() -> None:
    config = SystemConfig.model_validate(_config_data("al_cu_fe_llm_mock.yaml"))
    examples = [
        LlmEvalSetExample(
            example_id="far_match",
            system="Al-Cu-Fe",
            release_tier="gold",
            fidelity_tier="exact",
            source_family="materials_design",
            source_record_id="far_match",
            composition={"Al": 0.6, "Cu": 0.3, "Fe": 0.1},
            labels=["far"],
            orbit_names=[],
            tags=[],
            properties={},
            zomic_text="label far\n",
        ),
        LlmEvalSetExample(
            example_id="near_match",
            system="Al-Cu-Fe",
            release_tier="gold",
            fidelity_tier="exact",
            source_family="materials_design",
            source_record_id="near_match",
            composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            labels=["near"],
            orbit_names=[],
            tags=[],
            properties={},
            zomic_text="label near\n",
        ),
        LlmEvalSetExample(
            example_id="other_system",
            system="Sc-Zn",
            release_tier="gold",
            fidelity_tier="exact",
            source_family="materials_design",
            source_record_id="other_system",
            composition={"Sc": 0.3, "Zn": 0.7},
            labels=["other"],
            orbit_names=[],
            tags=[],
            properties={},
            zomic_text="label other\n",
        ),
    ]

    selected = select_conditioning_examples(config, examples, max_examples=1)
    assert [example.example_id for example in selected] == ["near_match"]
