from __future__ import annotations

import json
from pathlib import Path

from materials_discovery.llm.converters.generated_export import generated_export_to_corpus_examples
from materials_discovery.llm.converters.native_zomic import (
    extract_zomic_labels,
    zomic_file_to_corpus_example,
)


def test_zomic_file_to_corpus_example_marks_repo_native_script_as_exact() -> None:
    path = Path(__file__).resolve().parents[1] / "designs" / "zomic" / "sc_zn_tsai_bridge.zomic"
    example = zomic_file_to_corpus_example(path, source_family="materials_design", system="Sc-Zn")

    assert example.provenance.fidelity_tier == "exact"
    assert example.provenance.source_family == "materials_design"


def test_extract_zomic_labels_returns_stable_labels_from_committed_script() -> None:
    path = Path(__file__).resolve().parents[1] / "designs" / "zomic" / "sc_zn_tsai_bridge.zomic"
    labels = extract_zomic_labels(path.read_text(encoding="utf-8"))

    assert "pent.top.center" in labels
    assert "joint.bottom.right" in labels


def test_generated_export_to_corpus_examples_preserves_metadata_for_exact_source(tmp_path: Path) -> None:
    zomic_path = tmp_path / "demo.zomic"
    zomic_path.write_text("label shell.01\n", encoding="utf-8")
    raw_path = tmp_path / "demo.raw.json"
    raw_path.write_text(
        json.dumps(
            {
                "zomic_file": str(zomic_path),
                "parser": "antlr4",
                "symmetry": "icosahedral",
                "labeled_points": [{"label": "shell.01"}],
            }
        ),
        encoding="utf-8",
    )

    examples = generated_export_to_corpus_examples(raw_path)

    assert len(examples) == 1
    assert examples[0].provenance.fidelity_tier == "exact"
    assert examples[0].properties["parser"] == "antlr4"


def test_generated_export_conversion_stays_anchored_without_direct_zomic_source(tmp_path: Path) -> None:
    raw_path = tmp_path / "demo.raw.json"
    raw_path.write_text(
        json.dumps(
            {
                "parser": "antlr4",
                "symmetry": "icosahedral",
                "labeled_points": [{"label": "shell.01"}],
            }
        ),
        encoding="utf-8",
    )

    examples = generated_export_to_corpus_examples(raw_path)

    assert examples[0].provenance.fidelity_tier == "anchored"
    assert "label shell.01" in examples[0].zomic_text


def test_native_and_generated_loaders_emit_inventory_aligned_loader_hints(tmp_path: Path) -> None:
    native_path = tmp_path / "demo.zomic"
    native_path.write_text("label shell.01\n", encoding="utf-8")
    raw_path = tmp_path / "demo.raw.json"
    raw_path.write_text(json.dumps({"labeled_points": [{"label": "shell.01"}]}), encoding="utf-8")

    native_example = zomic_file_to_corpus_example(native_path, source_family="repo_regression")
    generated_example = generated_export_to_corpus_examples(raw_path)[0]

    assert native_example.properties["loader_hint"] == "native_zomic"
    assert generated_example.properties["loader_hint"] == "generated_export"
