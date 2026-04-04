from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import load_json_object
from materials_discovery.llm.acceptance import build_llm_acceptance_pack, write_llm_acceptance_pack
from materials_discovery.llm.schema import (
    LlmAcceptanceBenchmarkInput,
    LlmAcceptanceThresholds,
)
from materials_discovery.llm.storage import llm_acceptance_pack_path
from materials_discovery.llm.suggest import build_llm_suggestions, write_llm_suggestions


def test_build_acceptance_pack_and_suggestions_round_trip(tmp_path: Path) -> None:
    benchmark = LlmAcceptanceBenchmarkInput(
        system="Al-Cu-Fe",
        generate_comparison_path="data/benchmarks/llm_generate/al_cu_fe_comparison.json",
        pipeline_comparison_path="data/benchmarks/llm_pipeline/al_cu_fe_comparison.json",
        generate_comparison={
            "llm_generation": {
                "parse_pass_rate": 0.95,
                "compile_pass_rate": 0.92,
                "generation_success_rate": 0.4,
            }
        },
        pipeline_comparison={
            "llm": {
                "screen": {"pass_rate": 0.12},
                "hifi_validate": {"pass_rate": 0.08},
                "hifi_rank": {"novelty_score_mean": 0.2},
                "report": {"llm_synthesizability_mean": 0.71, "release_gate_ready": True},
            }
        },
    )

    pack = build_llm_acceptance_pack(
        pack_id="acceptance_demo",
        benchmark_inputs=[benchmark],
        thresholds=LlmAcceptanceThresholds(
            min_parse_success_rate=0.8,
            min_compile_success_rate=0.8,
            min_generation_success_rate=0.2,
            min_shortlist_pass_rate=0.05,
            min_validation_pass_rate=0.05,
            min_synthesizability_mean=0.6,
        ),
    )
    pack_path = write_llm_acceptance_pack(
        pack,
        llm_acceptance_pack_path("acceptance_demo", root=tmp_path),
    )

    assert pack_path.exists()
    suggestions = build_llm_suggestions(pack)
    suggestion_path = write_llm_suggestions(suggestions, pack_path.with_name("suggestions.json"))
    assert suggestion_path.exists()
    loaded = load_json_object(suggestion_path)
    assert loaded["overall_status"] == "ready"
    assert loaded["items"][0]["priority"] == "low"


def test_build_acceptance_pack_flags_validation_shortfalls() -> None:
    benchmark = LlmAcceptanceBenchmarkInput(
        system="Sc-Zn",
        generate_comparison_path="data/benchmarks/llm_generate/sc_zn_comparison.json",
        pipeline_comparison_path="data/benchmarks/llm_pipeline/sc_zn_comparison.json",
        generate_comparison={
            "llm_generation": {
                "parse_pass_rate": 0.9,
                "compile_pass_rate": 0.9,
                "generation_success_rate": 0.35,
            }
        },
        pipeline_comparison={
            "llm": {
                "screen": {"pass_rate": 0.02},
                "hifi_validate": {"pass_rate": 0.0},
                "hifi_rank": {"novelty_score_mean": 0.05},
                "report": {"llm_synthesizability_mean": 0.55, "release_gate_ready": False},
            }
        },
    )

    pack = build_llm_acceptance_pack(
        pack_id="acceptance_gap",
        benchmark_inputs=[benchmark],
        thresholds=LlmAcceptanceThresholds(min_shortlist_pass_rate=0.05, min_validation_pass_rate=0.01),
    )

    suggestions = build_llm_suggestions(pack)
    assert pack.overall_passed is False
    assert suggestions.overall_status == "needs_improvement"
    assert suggestions.items[0].priority == "high"
