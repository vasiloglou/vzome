from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from materials_discovery.common.io import load_yaml
from materials_discovery.llm.schema import (
    CorpusBuildConfig,
    CorpusBuildSummary,
    CorpusExample,
    CorpusInventoryRow,
    CorpusProvenance,
    CorpusValidationState,
)


def _provenance_payload(
    *,
    fidelity_tier: str = "anchored",
    release_tier: str = "pending",
    source_record_id: str = "candidate-001",
) -> dict[str, object]:
    return {
        "example_id": "example-001",
        "source_family": "candidate_record",
        "source_path": "data/candidates/sc_zn_batch.jsonl",
        "source_record_id": source_record_id,
        "system": " Sc-Zn ",
        "fidelity_tier": fidelity_tier,
        "release_tier": release_tier,
        "builder_version": "phase6_v1",
    }


def test_corpus_build_config_round_trips_from_committed_yaml() -> None:
    config_path = (
        Path(__file__).resolve().parents[1] / "configs" / "llm" / "corpus_v1.yaml"
    )
    config = CorpusBuildConfig.model_validate(load_yaml(config_path))

    assert config.build_id == "zomic_corpus_v1"
    assert config.systems == ["Al-Cu-Fe", "Sc-Zn", "Ti-Zr-Ni"]
    assert config.source_keys == ["hypodx", "cod"]
    assert config.reference_pack_ids == ["al_cu_fe_v1", "sc_zn_v1"]
    assert config.include_pyqcstrc_projection is True


def test_corpus_example_accepts_pending_release_tier_with_typed_validation() -> None:
    example = CorpusExample.model_validate(
        {
            "provenance": _provenance_payload(),
            "zomic_text": "label shell_01\nbranch { label shell_02 }\n",
            "labels": [" shell_01 ", "shell_02"],
            "orbit_names": [" shell ", "shell"],
            "composition": {"Zn": 2.0, "Sc": 1.0},
            "properties": {"template_family": "tsai"},
            "validation": {
                "parse_status": "pending",
                "compile_status": "pending",
                "site_count": 2,
            },
        }
    )

    assert example.provenance.release_tier == "pending"
    assert example.provenance.system == "Sc-Zn"
    assert example.labels == ["shell_01", "shell_02"]
    assert example.orbit_names == ["shell"]
    assert example.validation == CorpusValidationState(
        parse_status="pending",
        compile_status="pending",
        site_count=2,
    )
    assert example.composition is not None
    assert example.composition["Sc"] == pytest.approx(1.0 / 3.0)


def test_corpus_provenance_rejects_gold_with_heuristic_fidelity() -> None:
    with pytest.raises(ValidationError):
        CorpusProvenance.model_validate(
            _provenance_payload(fidelity_tier="heuristic", release_tier="gold")
        )


def test_corpus_inventory_row_requires_loader_hint_and_record_locator() -> None:
    with pytest.raises(ValidationError):
        CorpusInventoryRow.model_validate(
            {
                "source_family": "repo_regression",
                "source_path": "core/src/regression/files/Zomic/demo.zomic",
                "system": None,
                "source_record_id": "demo",
                "input_kind": "zomic_file",
                "record_locator": {},
                "loader_hint": " ",
            }
        )


def test_corpus_example_rejects_blank_source_record_id_and_zomic_text() -> None:
    with pytest.raises(ValidationError):
        CorpusExample.model_validate(
            {
                "provenance": _provenance_payload(source_record_id=" "),
                "zomic_text": "   ",
                "labels": [],
                "orbit_names": [],
                "properties": {},
                "validation": {},
            }
        )


def test_corpus_build_summary_validates_counts_and_paths() -> None:
    summary = CorpusBuildSummary.model_validate(
        {
            "build_id": "zomic_corpus_v1",
            "syntax_count": 10,
            "materials_count": 6,
            "reject_count": 1,
            "inventory_count": 12,
            "syntax_corpus_path": "data/llm_corpus/zomic_corpus_v1/syntax_corpus.jsonl",
            "materials_corpus_path": "data/llm_corpus/zomic_corpus_v1/materials_corpus.jsonl",
            "rejects_path": "data/llm_corpus/zomic_corpus_v1/rejects.jsonl",
            "inventory_path": "data/llm_corpus/zomic_corpus_v1/inventory.json",
            "qa_path": "data/llm_corpus/zomic_corpus_v1/qa.json",
            "manifest_path": "data/llm_corpus/zomic_corpus_v1/manifest.json",
        }
    )

    assert summary.syntax_count == 10
    assert summary.manifest_path.endswith("manifest.json")

    with pytest.raises(ValidationError):
        CorpusBuildSummary.model_validate(
            {
                **summary.model_dump(),
                "reject_count": -1,
            }
        )
