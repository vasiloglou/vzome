from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.active_learning.select_next_batch import select_next_candidate_batch
from materials_discovery.active_learning.train_surrogate import SurrogateModelSnapshot
from materials_discovery.cli import app
from materials_discovery.common.io import load_yaml
from materials_discovery.common.schema import CandidateRecord, SystemConfig
from materials_discovery.generator.candidate_factory import generate_candidates


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            rows.append(json.loads(line))
    return rows


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _prepare_validated_inputs(
    config_path: Path, count: int, seed: int
) -> tuple[SystemConfig, Path]:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config = SystemConfig.model_validate(load_yaml(config_path))

    candidates_path = (
        workspace / "data" / "candidates" / f"{_system_slug(config.system_name)}_candidates.jsonl"
    )
    generate_candidates(config, candidates_path, count=count, seed=seed)

    screen_result = runner.invoke(app, ["screen", "--config", str(config_path)])
    assert screen_result.exit_code == 0

    validate_result = runner.invoke(
        app,
        ["hifi-validate", "--config", str(config_path), "--batch", "all"],
    )
    assert validate_result.exit_code == 0

    summary = json.loads(validate_result.stdout)
    validated_path = Path(summary["output_path"])
    return config, validated_path


def test_active_learn_command_runs_m5_pipeline() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    config, validated_path = _prepare_validated_inputs(config_path, count=80, seed=515)
    validated_rows = _read_jsonl(validated_path)

    result = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert result.exit_code == 0

    summary = json.loads(result.stdout)
    assert summary["validated_count"] == len({row["candidate_id"] for row in validated_rows})
    assert summary["selected_count"] > 0
    assert 0.0 <= summary["pass_rate"] <= 1.0

    surrogate_path = Path(summary["surrogate_path"])
    batch_path = Path(summary["batch_path"])
    assert surrogate_path.exists()
    assert batch_path.exists()

    surrogate = json.loads(surrogate_path.read_text(encoding="utf-8"))
    assert surrogate["system"] == config.system_name
    assert surrogate["training_rows"] == summary["validated_count"]
    assert isinstance(surrogate["decision_threshold"], float)
    assert isinstance(surrogate["benchmark_decision_threshold"], float)
    assert isinstance(surrogate["separation_margin"], float)
    assert isinstance(surrogate["top_k_precision"], float)

    next_batch = _read_jsonl(batch_path)
    assert len(next_batch) == summary["selected_count"]

    validated_ids = {row["candidate_id"] for row in validated_rows}
    selected_ids = {row["candidate_id"] for row in next_batch}
    assert validated_ids.isdisjoint(selected_ids)

    for row in next_batch:
        provenance = row["provenance"]
        assert isinstance(provenance, dict)
        active = provenance["active_learning"]
        assert isinstance(active, dict)
        assert active["system"] == config.system_name
        assert isinstance(active["predicted_success"], float)
        assert isinstance(active["uncertainty_proxy"], float)
        assert isinstance(active["novelty_score"], float)
        assert isinstance(active["ood_score"], float)
        assert isinstance(active["energy_desirability"], float)
        assert isinstance(active["acquisition_score"], float)


def test_active_learn_is_deterministic_for_fixed_inputs() -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "systems" / "al_cu_fe.yaml"

    _, _ = _prepare_validated_inputs(config_path, count=75, seed=818)

    first = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert first.exit_code == 0
    first_summary = json.loads(first.stdout)

    batch_path = Path(first_summary["batch_path"])
    assert batch_path.exists()
    content_a = batch_path.read_text(encoding="utf-8")

    second = runner.invoke(app, ["active-learn", "--config", str(config_path)])
    assert second.exit_code == 0
    assert first.stdout == second.stdout

    content_b = batch_path.read_text(encoding="utf-8")
    assert content_a == content_b


def _candidate(
    candidate_id: str,
    composition: dict[str, float],
    *,
    qphi_scale: int,
    energy_proxy: float,
    min_distance: float,
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
            "screen": {
                "energy_proxy_ev_per_atom": energy_proxy,
                "min_distance_proxy": min_distance,
                "shortlist_rank": 1,
            },
            "digital_validation": {"status": "pending"},
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def test_active_learn_selection_penalizes_ood_candidates() -> None:
    config_path = (
        Path(__file__).resolve().parents[1]
        / "configs"
        / "systems"
        / "al_cu_fe_real.yaml"
    )
    config = SystemConfig.model_validate(
        load_yaml(config_path)
    )
    surrogate = SurrogateModelSnapshot(
        system="Al-Cu-Fe",
        species=["Al", "Cu", "Fe"],
        training_rows=20,
        positive_count=6,
        negative_count=14,
        pass_rate=0.3,
        positive_centroid={"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        negative_centroid={"Al": 0.8, "Cu": 0.1, "Fe": 0.1},
        feature_names=[
            "frac_Al",
            "frac_Cu",
            "frac_Fe",
            "qphi_complexity_norm",
            "radius_mismatch_norm",
            "en_spread_norm",
            "pair_mixing_preference",
            "energy_preference",
            "packing_preference",
            "shortlist_signal",
        ],
        positive_feature_centroid={
            "frac_Al": 0.7,
            "frac_Cu": 0.2,
            "frac_Fe": 0.1,
            "qphi_complexity_norm": 0.3,
            "radius_mismatch_norm": 0.2,
            "en_spread_norm": 0.25,
            "pair_mixing_preference": 0.75,
            "energy_preference": 0.8,
            "packing_preference": 0.85,
            "shortlist_signal": 0.5,
        },
        negative_feature_centroid={
            "frac_Al": 0.82,
            "frac_Cu": 0.08,
            "frac_Fe": 0.1,
            "qphi_complexity_norm": 0.8,
            "radius_mismatch_norm": 0.7,
            "en_spread_norm": 0.65,
            "pair_mixing_preference": 0.25,
            "energy_preference": 0.35,
            "packing_preference": 0.45,
            "shortlist_signal": 0.1,
        },
        benchmark_positive_feature_centroid={
            "frac_Al": 0.69,
            "frac_Cu": 0.19,
            "frac_Fe": 0.12,
            "qphi_complexity_norm": 0.33,
            "radius_mismatch_norm": 0.25,
            "en_spread_norm": 0.23,
            "pair_mixing_preference": 0.77,
            "energy_preference": 0.82,
            "packing_preference": 0.8,
            "shortlist_signal": 0.45,
        },
        benchmark_negative_feature_centroid={
            "frac_Al": 0.81,
            "frac_Cu": 0.09,
            "frac_Fe": 0.10,
            "qphi_complexity_norm": 0.74,
            "radius_mismatch_norm": 0.57,
            "en_spread_norm": 0.58,
            "pair_mixing_preference": 0.29,
            "energy_preference": 0.35,
            "packing_preference": 0.42,
            "shortlist_signal": 0.14,
        },
        uncertainty_mean=0.01,
        delta_hull_mean=0.03,
        decision_threshold=0.52,
        benchmark_decision_threshold=0.56,
        separation_margin=0.28,
        training_radius=0.12,
        top_k_precision=0.8,
        mean_predicted_success=0.46,
    )

    near_reference = _candidate(
        "md_good",
        {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
        qphi_scale=1,
        energy_proxy=-3.05,
        min_distance=1.02,
    )
    ood_candidate = _candidate(
        "md_ood",
        {"Al": 0.9, "Cu": 0.03, "Fe": 0.07},
        qphi_scale=4,
        energy_proxy=-2.7,
        min_distance=0.66,
    )

    selected = select_next_candidate_batch(
        config,
        [ood_candidate, near_reference],
        validated_ids=set(),
        surrogate=surrogate,
        batch_size=2,
    )

    assert [candidate.candidate_id for candidate in selected] == ["md_good", "md_ood"]

    top_metrics = selected[0].provenance["active_learning"]
    bottom_metrics = selected[1].provenance["active_learning"]
    assert isinstance(top_metrics, dict)
    assert isinstance(bottom_metrics, dict)
    assert top_metrics["predicted_success"] > bottom_metrics["predicted_success"]
    assert top_metrics["ood_score"] < bottom_metrics["ood_score"]
    assert top_metrics["acquisition_score"] > bottom_metrics["acquisition_score"]
