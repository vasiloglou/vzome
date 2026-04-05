from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.common.io import load_jsonl, load_yaml, write_jsonl
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    LlmEvaluateConfig,
    LlmEvaluateSummary,
    SiteRecord,
    SystemConfig,
)
from materials_discovery.llm.evaluate import evaluate_llm_candidates
from materials_discovery.llm.schema import (
    LlmAssessment,
    LlmEvaluationRequest,
    LlmEvaluationRunManifest,
    LlmServingIdentity,
)


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _candidate() -> CandidateRecord:
    return CandidateRecord(
        candidate_id="md_eval_0001",
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        cell={"a": 14.2, "b": 14.2, "c": 14.2, "alpha": 90.0, "beta": 90.0, "gamma": 90.0},
        sites=[
            SiteRecord(
                label="S01",
                qphi=((0, 0), (1, 0), (1, 0)),
                species="Al",
                occ=1.0,
                fractional_position=(0.2, 0.2, 0.2),
                cartesian_position=(2.84, 2.84, 2.84),
            ),
            SiteRecord(
                label="S02",
                qphi=((1, 0), (0, 0), (1, 0)),
                species="Cu",
                occ=1.0,
                fractional_position=(0.7, 0.7, 0.7),
                cartesian_position=(9.94, 9.94, 9.94),
            ),
        ],
        composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        screen={"energy_proxy_ev_per_atom": -0.21},
        digital_validation=DigitalValidationRecord(
            status="passed",
            uncertainty_ev_per_atom=0.01,
            delta_e_proxy_hull_ev_per_atom=0.02,
            phonon_pass=True,
            md_pass=True,
            xrd_pass=True,
            passed_checks=True,
        ),
        provenance={"hifi_rank": {"score": 0.82, "novelty_score": 0.44}},
    )


def test_llm_evaluation_schema_models_validate_expected_fields() -> None:
    request = LlmEvaluationRequest(
        candidate_id="md_eval_0001",
        system="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        composition={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        digital_validation={"passed_checks": True},
        prompt_text="Assess this candidate.",
        temperature=0.1,
        max_tokens=512,
    )
    assessment = LlmAssessment(
        candidate_id="md_eval_0001",
        adapter_key="llm_fixture_v1",
        provider="mock",
        model="fixture-eval-v1",
        status="passed",
        raw_response_path="raw/md_eval_0001.txt",
        requested_model_lanes=[" specialized_materials ", "specialized_materials"],
        resolved_model_lane=" specialized_materials ",
        resolved_model_lane_source="configured_lane",
        serving_identity=LlmServingIdentity(
            requested_model_lane="specialized_materials",
            resolved_model_lane="specialized_materials",
            resolved_model_lane_source="configured_lane",
            adapter="openai_compat_v1",
            provider="openai_compat",
            model="materials-al-cu-fe-specialist-v1",
            effective_api_base="http://localhost:8000/",
            checkpoint_id=" ckpt-specialist ",
            model_revision=" local-dev ",
        ),
        synthesizability_score=0.78,
        precursor_hints=["Al powder", "Cu foil", "Fe powder"],
        anomaly_flags=[],
        literature_context="Matches Tsai-like approximant chemistry.",
        rationale="Validation signals are mutually consistent.",
    )
    run_manifest = LlmEvaluationRunManifest(
        run_id="al_cu_fe_all_123456789abc",
        system="Al-Cu-Fe",
        adapter_key="llm_fixture_v1",
        provider="mock",
        model="fixture-eval-v1",
        prompt_template="materials_assess_v1",
        input_path="data/ranked/al_cu_fe_ranked.jsonl",
        output_path="data/llm_evaluated/al_cu_fe_all_llm_evaluated.jsonl",
        requests_path="data/llm_evaluations/run/requests.jsonl",
        assessments_path="data/llm_evaluations/run/assessments.jsonl",
        requested_count=1,
        assessed_count=1,
        failed_count=0,
        created_at_utc="2026-04-03T20:00:00+00:00",
        requested_model_lanes=["specialized_materials"],
        resolved_model_lane="specialized_materials",
        resolved_model_lane_source="configured_lane",
        serving_identity=assessment.serving_identity,
    )
    summary = LlmEvaluateSummary(
        input_count=1,
        assessed_count=1,
        failed_count=0,
        output_path="data/llm_evaluated/al_cu_fe_all_llm_evaluated.jsonl",
        requested_model_lanes=[" specialized_materials "],
        resolved_model_lane=" specialized_materials ",
        resolved_model_lane_source="configured_lane",
        serving_identity=assessment.serving_identity,
        run_manifest_path="data/llm_evaluations/run/run_manifest.json",
    )

    assert request.schema_version == "llm-evaluation-request/v1"
    assert assessment.synthesizability_score == pytest.approx(0.78)
    assert assessment.requested_model_lanes == ["specialized_materials"]
    assert assessment.resolved_model_lane == "specialized_materials"
    assert assessment.serving_identity is not None
    assert assessment.serving_identity.effective_api_base == "http://localhost:8000"
    assert assessment.serving_identity.checkpoint_id == "ckpt-specialist"
    assert run_manifest.assessed_count == 1
    assert run_manifest.serving_identity is not None
    assert summary.serving_identity is not None
    assert summary.resolved_model_lane == "specialized_materials"


def test_llm_evaluate_config_normalizes_fixture_outputs_and_model_lane() -> None:
    config = LlmEvaluateConfig(
        model_lane=" specialized_materials ",
        fixture_outputs=[
            "  {\"synthesizability_score\": 0.5, \"precursor_hints\": [], \"anomaly_flags\": [], \"literature_context\": \"\", \"rationale\": \"ok\"}  ",
            "",
        ]
    )

    assert config.model_lane == "specialized_materials"
    assert len(config.fixture_outputs) == 1
    assert "synthesizability_score" in config.fixture_outputs[0]


def test_llm_evaluation_run_manifest_reads_legacy_payload() -> None:
    legacy_manifest = LlmEvaluationRunManifest.model_validate(
        {
            "run_id": "al_cu_fe_all_123456789abc",
            "system": "Al-Cu-Fe",
            "adapter_key": "llm_fixture_v1",
            "provider": "mock",
            "model": "fixture-eval-v1",
            "prompt_template": "materials_assess_v1",
            "input_path": "data/ranked/al_cu_fe_ranked.jsonl",
            "output_path": "data/llm_evaluated/al_cu_fe_all_llm_evaluated.jsonl",
            "requests_path": "data/llm_evaluations/run/requests.jsonl",
            "assessments_path": "data/llm_evaluations/run/assessments.jsonl",
            "requested_count": 1,
            "assessed_count": 1,
            "failed_count": 0,
            "created_at_utc": "2026-04-03T20:00:00+00:00",
        }
    )

    assert legacy_manifest.requested_model_lanes == []
    assert legacy_manifest.resolved_model_lane is None
    assert legacy_manifest.serving_identity is None


def test_evaluate_llm_candidates_writes_specialized_lane_lineage_and_uses_specialist_prompt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_data = load_yaml(_workspace() / "configs" / "systems" / "al_cu_fe_llm_local.yaml")
    config_data["llm_evaluate"] = {
        "prompt_template": "materials_assess_v1",
        "temperature": 0.1,
        "max_tokens": 512,
        "model_lane": "specialized_materials",
    }
    system_config = SystemConfig.model_validate(config_data)
    workspace = tmp_path / "workspace"
    ranked_path = workspace / "data" / "ranked" / "al_cu_fe_ranked.jsonl"
    output_path = workspace / "data" / "llm_evaluated" / "al_cu_fe_all_llm_evaluated.jsonl"

    write_jsonl([_candidate().model_dump(mode="json")], ranked_path)
    monkeypatch.setattr("materials_discovery.llm.evaluate.workspace_root", lambda: workspace)

    class _FakeAdapter:
        def __init__(self) -> None:
            self.prompts: list[str] = []

        def generate(self, request: LlmEvaluationRequest) -> str:
            self.prompts.append(request.prompt_text)
            return json_payload

    json_payload = (
        "{\"synthesizability_score\":0.81,"
        "\"precursor_hints\":[\"Al powder\",\"Cu powder\",\"Fe powder\"],"
        "\"anomaly_flags\":[],"
        "\"literature_context\":\"Consistent with known Al-Cu-Fe QC families.\","
        "\"rationale\":\"Screening and validation metrics are mutually supportive.\"}"
    )
    fake_adapter = _FakeAdapter()
    readiness_calls: list[tuple[str, str | None, str | None]] = []

    monkeypatch.setattr(
        "materials_discovery.llm.evaluate.resolve_llm_adapter",
        lambda mode, backend=None: fake_adapter,
    )
    monkeypatch.setattr(
        "materials_discovery.llm.evaluate.validate_llm_adapter_ready",
        lambda adapter, *, adapter_key, requested_lane=None, resolved_lane=None: readiness_calls.append(
            (adapter_key, requested_lane, resolved_lane)
        ),
    )

    summary = evaluate_llm_candidates(system_config, output_path, batch="all")

    assert summary.input_count == 1
    assert summary.assessed_count == 1
    assert summary.failed_count == 0
    assert summary.requested_model_lanes == ["specialized_materials"]
    assert summary.resolved_model_lane == "specialized_materials"
    assert summary.resolved_model_lane_source == "configured_lane"
    assert summary.serving_identity is not None
    assert summary.serving_identity.model == "materials-al-cu-fe-specialist-v1"
    assert readiness_calls == [
        ("openai_compat_v1", "specialized_materials", "specialized_materials")
    ]
    assert fake_adapter.prompts
    assert "\"evaluation_mode\": \"specialized_materials\"" in fake_adapter.prompts[0]
    assert "\"site_geometry\"" in fake_adapter.prompts[0]

    evaluated = [CandidateRecord.model_validate(row) for row in load_jsonl(output_path)]
    assert len(evaluated) == 1
    assessment = evaluated[0].provenance["llm_assessment"]
    assert assessment["status"] == "passed"
    assert assessment["synthesizability_score"] == pytest.approx(0.81)
    assert assessment["precursor_hints"] == ["Al powder", "Cu powder", "Fe powder"]
    assert assessment["requested_model_lanes"] == ["specialized_materials"]
    assert assessment["resolved_model_lane"] == "specialized_materials"
    assert assessment["resolved_model_lane_source"] == "configured_lane"
    assert assessment["serving_identity"]["model"] == "materials-al-cu-fe-specialist-v1"

    run_dir = Path(summary.run_manifest_path).parent
    requests = load_jsonl(run_dir / "requests.jsonl")
    assessments = load_jsonl(run_dir / "assessments.jsonl")
    assert requests[0]["schema_version"] == "llm-evaluation-request/v1"
    assert assessments[0]["schema_version"] == "llm-assessment/v1"
    assert assessments[0]["resolved_model_lane"] == "specialized_materials"
    assert assessments[0]["serving_identity"]["checkpoint_id"] == "ckpt-al-cu-fe-specialist"


def test_evaluate_llm_candidates_preserves_backend_default_when_no_lane_requested(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_data = load_yaml(_workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml")
    config_data["llm_evaluate"] = {
        "prompt_template": "materials_assess_v1",
        "temperature": 0.1,
        "max_tokens": 512,
        "fixture_outputs": [
            "{\"synthesizability_score\":0.66,\"precursor_hints\":[],\"anomaly_flags\":[],\"literature_context\":\"demo\",\"rationale\":\"ok\"}"
        ],
    }
    system_config = SystemConfig.model_validate(config_data)
    workspace = tmp_path / "workspace"
    ranked_path = workspace / "data" / "ranked" / "al_cu_fe_ranked.jsonl"
    output_path = workspace / "data" / "llm_evaluated" / "al_cu_fe_all_llm_evaluated.jsonl"

    write_jsonl([_candidate().model_dump(mode="json")], ranked_path)
    monkeypatch.setattr("materials_discovery.llm.evaluate.workspace_root", lambda: workspace)

    summary = evaluate_llm_candidates(system_config, output_path, batch="all")

    assert summary.requested_model_lanes == []
    assert summary.resolved_model_lane == "general_purpose"
    assert summary.resolved_model_lane_source == "backend_default"
    assert summary.serving_identity is not None
    assert summary.serving_identity.provider == "mock"
