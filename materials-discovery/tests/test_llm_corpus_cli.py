from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.llm.schema import CorpusBuildSummary


def test_llm_corpus_build_prints_json_summary(monkeypatch) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "llm" / "corpus_v1.yaml"

    monkeypatch.setattr(
        "materials_discovery.cli.build_llm_corpus",
        lambda config: CorpusBuildSummary(
            build_id=config.build_id,
            syntax_count=3,
            materials_count=2,
            reject_count=1,
            inventory_count=4,
            syntax_corpus_path="data/llm_corpus/zomic_corpus_v1/syntax_corpus.jsonl",
            materials_corpus_path="data/llm_corpus/zomic_corpus_v1/materials_corpus.jsonl",
            rejects_path="data/llm_corpus/zomic_corpus_v1/rejects.jsonl",
            inventory_path="data/llm_corpus/zomic_corpus_v1/inventory.json",
            qa_path="data/llm_corpus/zomic_corpus_v1/qa.json",
            manifest_path="data/llm_corpus/zomic_corpus_v1/manifest.json",
        ),
    )

    result = runner.invoke(app, ["llm-corpus", "build", "--config", str(config_path)])

    assert result.exit_code == 0
    assert '"syntax_count":3' in result.stdout


def test_llm_corpus_build_returns_code_2_for_invalid_config(tmp_path: Path) -> None:
    runner = CliRunner()
    bad_config = tmp_path / "bad.yaml"
    bad_config.write_text(yaml.safe_dump({"build_id": "bad"}), encoding="utf-8")

    result = runner.invoke(app, ["llm-corpus", "build", "--config", str(bad_config)])

    assert result.exit_code == 2


def test_llm_corpus_build_output_includes_manifest_and_qa_paths(monkeypatch) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    config_path = workspace / "configs" / "llm" / "corpus_v1.yaml"

    monkeypatch.setattr(
        "materials_discovery.cli.build_llm_corpus",
        lambda config: CorpusBuildSummary(
            build_id=config.build_id,
            syntax_count=1,
            materials_count=1,
            reject_count=0,
            inventory_count=2,
            syntax_corpus_path="syntax.jsonl",
            materials_corpus_path="materials.jsonl",
            rejects_path="rejects.jsonl",
            inventory_path="inventory.json",
            qa_path="qa.json",
            manifest_path="manifest.json",
        ),
    )

    result = runner.invoke(app, ["llm-corpus", "build", "--config", str(config_path)])

    assert result.exit_code == 0
    assert '"manifest_path":"manifest.json"' in result.stdout
    assert '"qa_path":"qa.json"' in result.stdout


def test_llm_corpus_build_honors_workspace_relative_config_path(monkeypatch) -> None:
    runner = CliRunner()
    workspace = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(workspace)
    monkeypatch.setattr(
        "materials_discovery.cli.build_llm_corpus",
        lambda config: CorpusBuildSummary(
            build_id=config.build_id,
            syntax_count=1,
            materials_count=1,
            reject_count=0,
            inventory_count=2,
            syntax_corpus_path="syntax.jsonl",
            materials_corpus_path="materials.jsonl",
            rejects_path="rejects.jsonl",
            inventory_path="inventory.json",
            qa_path="qa.json",
            manifest_path="manifest.json",
        ),
    )

    result = runner.invoke(app, ["llm-corpus", "build", "--config", "configs/llm/corpus_v1.yaml"])

    assert result.exit_code == 0
