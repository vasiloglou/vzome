from __future__ import annotations

from pathlib import Path

import pytest

from materials_discovery.common.io import load_jsonl, load_yaml, write_jsonl
from materials_discovery.common.schema import (
    CandidateRecord,
    DigitalValidationRecord,
    LlmEvaluateConfig,
    SiteRecord,
    SystemConfig,
)
from materials_discovery.llm.evaluate import evaluate_llm_candidates
from materials_discovery.llm.schema import (
    LlmAssessment,
    LlmEvaluationRequest,
    LlmEvaluationRunManifest,
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
    )

    assert request.schema_version == "llm-evaluation-request/v1"
    assert assessment.synthesizability_score == pytest.approx(0.78)
    assert run_manifest.assessed_count == 1


def test_llm_evaluate_config_normalizes_fixture_outputs() -> None:
    config = LlmEvaluateConfig(
        fixture_outputs=[
            "  {\"synthesizability_score\": 0.5, \"precursor_hints\": [], \"anomaly_flags\": [], \"literature_context\": \"\", \"rationale\": \"ok\"}  ",
            "",
        ]
    )

    assert len(config.fixture_outputs) == 1
    assert "synthesizability_score" in config.fixture_outputs[0]


def test_evaluate_llm_candidates_writes_typed_artifacts_and_enriched_candidates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_data = load_yaml(_workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml")
    config_data["llm_evaluate"] = {
        "prompt_template": "materials_assess_v1",
        "temperature": 0.1,
        "max_tokens": 512,
        "fixture_outputs": [
            """
            {
              "synthesizability_score": 0.81,
              "precursor_hints": ["Al powder", "Cu powder", "Fe powder"],
              "anomaly_flags": [],
              "literature_context": "Consistent with known Al-Cu-Fe QC families.",
              "rationale": "Screening and validation metrics are mutually supportive."
            }
            """
        ],
    }
    system_config = SystemConfig.model_validate(config_data)
    workspace = tmp_path / "workspace"
    ranked_path = workspace / "data" / "ranked" / "al_cu_fe_ranked.jsonl"
    output_path = workspace / "data" / "llm_evaluated" / "al_cu_fe_all_llm_evaluated.jsonl"

    write_jsonl([_candidate().model_dump(mode="json")], ranked_path)
    monkeypatch.setattr("materials_discovery.llm.evaluate.workspace_root", lambda: workspace)

    summary = evaluate_llm_candidates(system_config, output_path, batch="all")

    assert summary.input_count == 1
    assert summary.assessed_count == 1
    assert summary.failed_count == 0

    evaluated = [CandidateRecord.model_validate(row) for row in load_jsonl(output_path)]
    assert len(evaluated) == 1
    assessment = evaluated[0].provenance["llm_assessment"]
    assert assessment["status"] == "passed"
    assert assessment["synthesizability_score"] == pytest.approx(0.81)
    assert assessment["precursor_hints"] == ["Al powder", "Cu powder", "Fe powder"]

    run_dir = Path(summary.run_manifest_path).parent
    requests = load_jsonl(run_dir / "requests.jsonl")
    assessments = load_jsonl(run_dir / "assessments.jsonl")
    assert requests[0]["schema_version"] == "llm-evaluation-request/v1"
    assert assessments[0]["schema_version"] == "llm-assessment/v1"
