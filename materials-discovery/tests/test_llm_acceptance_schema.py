from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import load_json_object, write_jsonl
from materials_discovery.llm.acceptance import build_llm_acceptance_pack, write_llm_acceptance_pack
from materials_discovery.llm.eval_set import export_llm_eval_set, load_eval_set
from materials_discovery.llm.schema import (
    CorpusBuildConfig,
    CorpusExample,
    CorpusManifest,
    LlmAcceptanceBenchmarkInput,
    LlmAcceptanceThresholds,
    LlmEvalSetManifest,
)
from materials_discovery.llm.storage import (
    corpus_manifest_path,
    llm_acceptance_pack_path,
    llm_eval_set_manifest_path,
)


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def _corpus_example(example_id: str, system: str, release_tier: str) -> dict[str, object]:
    return CorpusExample.model_validate(
        {
            "provenance": {
                "example_id": example_id,
                "source_family": "materials_design",
                "source_path": "designs/zomic/demo.zomic",
                "source_record_id": example_id,
                "system": system,
                "fidelity_tier": "exact",
                "release_tier": release_tier,
            },
            "zomic_text": f"label {example_id}\n",
            "labels": [example_id],
            "orbit_names": ["orbit.demo"],
            "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1} if system == "Al-Cu-Fe" else {"Sc": 0.3, "Zn": 0.7},
            "properties": {"template_family": "demo_family"},
            "validation": {"parse_status": "passed", "compile_status": "passed"},
        }
    ).model_dump(mode="json")


def test_export_llm_eval_set_filters_by_system_and_release_tier(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    build_id = "corpus_v1"
    materials_path = workspace / "data" / "llm_corpus" / build_id / "materials_corpus.jsonl"
    write_jsonl(
        [
            _corpus_example("ex_gold_a", "Al-Cu-Fe", "gold"),
            _corpus_example("ex_silver_a", "Al-Cu-Fe", "silver"),
            _corpus_example("ex_gold_b", "Sc-Zn", "gold"),
        ],
        materials_path,
    )

    manifest = CorpusManifest(
        build_id=build_id,
        build_fingerprint="fingerprint",
        created_at_utc="2026-04-03T00:00:00Z",
        config_path="configs/llm/corpus_v1.yaml",
        syntax_count=3,
        materials_count=3,
        reject_count=0,
        inventory_count=3,
        syntax_corpus_path="data/llm_corpus/corpus_v1/syntax_corpus.jsonl",
        materials_corpus_path="data/llm_corpus/corpus_v1/materials_corpus.jsonl",
        rejects_path="data/llm_corpus/corpus_v1/rejects.jsonl",
        inventory_path="data/llm_corpus/corpus_v1/inventory.json",
        qa_path="data/llm_corpus/corpus_v1/qa.json",
    )
    load_json_object  # keep import used for style parity
    manifest_path = corpus_manifest_path(build_id, root=workspace)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

    summary = export_llm_eval_set(
        build_id=build_id,
        export_id="acceptance_eval_v1",
        systems=["Al-Cu-Fe"],
        release_tiers=("gold",),
        max_examples_per_system=1,
        root=workspace,
    )

    rows = load_eval_set(Path(summary.eval_set_path))
    assert len(rows) == 1
    assert rows[0].system == "Al-Cu-Fe"
    assert rows[0].release_tier == "gold"

    manifest_out = LlmEvalSetManifest.model_validate(load_json_object(llm_eval_set_manifest_path("acceptance_eval_v1", root=workspace)))
    assert manifest_out.example_count == 1
    assert manifest_out.systems == ["Al-Cu-Fe"]


def test_build_llm_acceptance_pack_captures_threshold_failures(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    input_row = LlmAcceptanceBenchmarkInput(
        system="Al-Cu-Fe",
        generate_comparison_path="data/benchmarks/llm_generate/al_cu_fe_comparison.json",
        pipeline_comparison_path="data/benchmarks/llm_pipeline/al_cu_fe_comparison.json",
        generate_comparison={
            "llm_generation": {
                "parse_pass_rate": 0.9,
                "compile_pass_rate": 0.7,
                "generation_success_rate": 0.4,
            }
        },
        pipeline_comparison={
            "llm": {
                "screen": {"pass_rate": 0.04},
                "hifi_validate": {"pass_rate": 0.03},
                "hifi_rank": {"novelty_score_mean": 0.12},
                "report": {
                    "llm_synthesizability_mean": 0.61,
                    "release_gate_ready": False,
                },
            }
        },
    )

    pack = build_llm_acceptance_pack(
        pack_id="phase9_acceptance_v1",
        benchmark_inputs=[input_row],
        thresholds=LlmAcceptanceThresholds(min_compile_success_rate=0.8, min_shortlist_pass_rate=0.05),
        eval_set_manifest_path="data/llm_eval_sets/acceptance_eval_v1/manifest.json",
    )
    out_path = write_llm_acceptance_pack(
        pack,
        llm_acceptance_pack_path("phase9_acceptance_v1", root=workspace),
    )

    assert out_path.exists()
    loaded = load_json_object(out_path)
    assert loaded["pack_id"] == "phase9_acceptance_v1"
    assert loaded["overall_passed"] is False
    assert loaded["systems"][0]["failing_metrics"] == [
        "compile_success_rate",
        "shortlist_pass_rate",
    ]
