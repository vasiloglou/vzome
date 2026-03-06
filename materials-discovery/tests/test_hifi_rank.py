from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import CandidateRecord, SystemConfig
from materials_discovery.generator.candidate_factory import generate_candidates
from materials_discovery.hifi_digital.rank_candidates import rank_validated_candidates


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _prepare_validated_inputs(config_path: Path, count: int, seed: int) -> Path:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = SystemConfig.model_validate(load_yaml(config_path))

    candidates_path = (
        workspace / "data" / "candidates" / f"{_system_slug(config.system_name)}_candidates.jsonl"
    )
    generate_candidates(config, candidates_path, count=count, seed=seed)

    assert runner.invoke(app, ["screen", "--config", str(config_path)]).exit_code == 0
    assert (
        runner.invoke(
            app,
            ["hifi-validate", "--config", str(config_path), "--batch", "all"],
        ).exit_code
        == 0
    )

    return candidates_path


def test_hifi_rank_runs_pipeline() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _ = _prepare_validated_inputs(config_path, count=70, seed=222)

    result = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert result.exit_code == 0

    summary = json.loads(result.stdout)
    assert summary["ranked_count"] == summary["input_count"]

    output_path = Path(summary["output_path"])
    assert output_path.exists()
    calibration_path = Path(summary["calibration_path"])
    assert calibration_path.exists()

    ranked_rows = _read_jsonl(output_path)
    assert len(ranked_rows) == summary["ranked_count"]
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    assert "top_10_pass_rate" in calibration
    assert "ood_fraction" in calibration
    assert "stability_probability_mean" in calibration

    ranks: list[int] = []
    scores: list[float] = []
    passed_count = 0

    for row in ranked_rows:
        provenance = row["provenance"]
        assert isinstance(provenance, dict)
        hifi_rank = provenance["hifi_rank"]
        assert isinstance(hifi_rank, dict)

        rank = hifi_rank["rank"]
        score = hifi_rank["score"]
        assert isinstance(rank, int)
        assert isinstance(score, float)
        assert isinstance(hifi_rank["decision_score"], float)
        assert isinstance(hifi_rank["stability_probability"], float)
        assert isinstance(hifi_rank["ood_score"], float)
        assert isinstance(hifi_rank["novelty_score"], float)

        ranks.append(rank)
        scores.append(score)

        validation = row["digital_validation"]
        assert isinstance(validation, dict)
        assert validation["status"] == "ranked"
        if validation["passed_checks"]:
            passed_count += 1

    assert ranks == list(range(1, len(ranks) + 1))
    assert scores == sorted(scores, reverse=True)
    assert passed_count == summary["passed_count"]


def test_hifi_rank_is_deterministic() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _ = _prepare_validated_inputs(config_path, count=65, seed=333)

    first = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert first.exit_code == 0
    first_summary = json.loads(first.stdout)

    output_path = Path(first_summary["output_path"])
    content_a = output_path.read_text(encoding="utf-8")

    second = runner.invoke(app, ["hifi-rank", "--config", str(config_path)])
    assert second.exit_code == 0
    assert first.stdout == second.stdout

    content_b = output_path.read_text(encoding="utf-8")
    assert content_a == content_b


def _real_config() -> SystemConfig:
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe_real.yaml"
    return SystemConfig.model_validate(load_yaml(config_path))


def _validated_candidate(
    candidate_id: str,
    composition: dict[str, float],
    *,
    uncertainty: float,
    delta_hull: float,
    md_score: float,
    xrd_confidence: float,
    reference_distance: float,
    qphi_scale: int,
    passed_checks: bool,
) -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": candidate_id,
            "system": "Al-Cu-Fe",
            "template_family": "icosahedral_approximant_1_1",
            "cell": {
                "a": 14.2,
                "b": 14.2,
                "c": 14.2,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            "sites": [
                {
                    "label": "S1",
                    "qphi": [[qphi_scale, 0], [0, qphi_scale], [-qphi_scale, qphi_scale]],
                    "species": "Al",
                    "occ": 1.0,
                }
            ],
            "composition": composition,
            "screen": {"energy_proxy_ev_per_atom": -2.9},
            "digital_validation": {
                "status": "passed" if passed_checks else "failed",
                "committee": ["MACE", "CHGNet", "MatterSim"],
                "uncertainty_ev_per_atom": uncertainty,
                "committee_energy_ev_per_atom": {
                    "MACE": -2.91,
                    "CHGNet": -2.90,
                    "MatterSim": -2.89,
                },
                "committee_std_ev_per_atom": uncertainty,
                "delta_e_proxy_hull_ev_per_atom": delta_hull,
                "proxy_hull_reference_distance": reference_distance,
                "proxy_hull_reference_phases": ["i-phase"],
                "phonon_imaginary_modes": 0,
                "phonon_pass": True,
                "md_stability_score": md_score,
                "md_pass": md_score >= 0.55,
                "xrd_confidence": xrd_confidence,
                "xrd_pass": xrd_confidence >= 0.60,
                "passed_checks": passed_checks,
            },
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def test_real_mode_rank_is_input_order_invariant() -> None:
    config = _real_config()
    candidates = [
        _validated_candidate(
            "md_a",
            {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            uncertainty=0.006,
            delta_hull=0.012,
            md_score=0.90,
            xrd_confidence=0.91,
            reference_distance=0.0,
            qphi_scale=1,
            passed_checks=True,
        ),
        _validated_candidate(
            "md_b",
            {"Al": 0.65, "Cu": 0.2, "Fe": 0.15},
            uncertainty=0.009,
            delta_hull=0.020,
            md_score=0.84,
            xrd_confidence=0.87,
            reference_distance=0.0,
            qphi_scale=2,
            passed_checks=True,
        ),
        _validated_candidate(
            "md_c",
            {"Al": 0.78, "Cu": 0.08, "Fe": 0.14},
            uncertainty=0.020,
            delta_hull=0.050,
            md_score=0.70,
            xrd_confidence=0.72,
            reference_distance=0.16,
            qphi_scale=3,
            passed_checks=False,
        ),
    ]

    ranked_a = rank_validated_candidates(config, candidates)
    ranked_b = rank_validated_candidates(config, list(reversed(candidates)))

    assert [candidate.candidate_id for candidate in ranked_a] == [
        candidate.candidate_id for candidate in ranked_b
    ]


def test_real_mode_rank_penalizes_ood_and_high_risk_candidates() -> None:
    config = _real_config()
    stable_reference = _validated_candidate(
        "md_ref",
        {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        uncertainty=0.004,
        delta_hull=0.010,
        md_score=0.92,
        xrd_confidence=0.93,
        reference_distance=0.0,
        qphi_scale=1,
        passed_checks=True,
    )
    noisy_ood = _validated_candidate(
        "md_ood",
        {"Al": 0.84, "Cu": 0.04, "Fe": 0.12},
        uncertainty=0.028,
        delta_hull=0.075,
        md_score=0.66,
        xrd_confidence=0.68,
        reference_distance=0.20,
        qphi_scale=4,
        passed_checks=False,
    )

    ranked = rank_validated_candidates(config, [noisy_ood, stable_reference])
    top = ranked[0]
    bottom = ranked[1]

    assert top.candidate_id == "md_ref"
    assert bottom.candidate_id == "md_ood"

    top_rank = top.provenance["hifi_rank"]
    bottom_rank = bottom.provenance["hifi_rank"]
    assert isinstance(top_rank, dict)
    assert isinstance(bottom_rank, dict)
    assert top_rank["stability_probability"] > bottom_rank["stability_probability"]
    assert top_rank["ood_score"] < bottom_rank["ood_score"]
    assert top_rank["score"] > bottom_rank["score"]
