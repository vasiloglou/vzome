from __future__ import annotations

import json
import shutil
from pathlib import Path

from materials_discovery.common.io import workspace_root, write_json_object, write_jsonl
from materials_discovery.common.io import load_yaml
from materials_discovery.llm.manifests import (
    build_corpus_manifest,
    corpus_build_fingerprint,
    write_corpus_manifest,
)
from materials_discovery.llm.schema import CorpusBuildConfig
from materials_discovery.llm.storage import (
    corpus_inventory_path,
    corpus_manifest_path,
    corpus_qa_path,
    corpus_rejects_path,
    materials_corpus_path,
    syntax_corpus_path,
)


def _config() -> CorpusBuildConfig:
    config_path = workspace_root() / "configs" / "llm" / "corpus_v1.yaml"
    return CorpusBuildConfig.model_validate(load_yaml(config_path))


def test_corpus_build_fingerprint_is_deterministic() -> None:
    config = _config()
    first = corpus_build_fingerprint(config, 10, 5)
    second = corpus_build_fingerprint(config, 10, 5)
    assert first == second


def test_build_corpus_manifest_uses_workspace_relative_paths() -> None:
    root = workspace_root()
    build_root = root / "data" / "_test_llm_manifest"
    build_root.mkdir(parents=True, exist_ok=True)
    try:
        syntax_path = syntax_corpus_path("demo_build", root=build_root)
        materials_path = materials_corpus_path("demo_build", root=build_root)
        rejects_path = corpus_rejects_path("demo_build", root=build_root)
        inventory_path = corpus_inventory_path("demo_build", root=build_root)
        qa_path = corpus_qa_path("demo_build", root=build_root)

        write_jsonl([{"zomic_text": "label a"}], syntax_path)
        write_jsonl([{"zomic_text": "label b"}], materials_path)
        write_jsonl([{"zomic_text": "label c"}], rejects_path)
        write_json_object({"rows": 3}, inventory_path)
        write_json_object({"gold_count": 1}, qa_path)

        config = _config()
        config_path = root / "configs" / "llm" / "corpus_v1.yaml"
        manifest = build_corpus_manifest(
            config=config,
            config_path=config_path,
            syntax_count=1,
            materials_count=1,
            reject_count=1,
            inventory_count=3,
            syntax_path=syntax_path,
            materials_path=materials_path,
            rejects_path=rejects_path,
            inventory_path=inventory_path,
            qa_path=qa_path,
        )

        assert not manifest.syntax_corpus_path.startswith("/")
        assert manifest.syntax_corpus_path.endswith("syntax_corpus.jsonl")
        assert not manifest.config_path.startswith("/")
        assert manifest.output_hashes["inventory"]
    finally:
        shutil.rmtree(build_root, ignore_errors=True)


def test_write_corpus_manifest_persists_json_payload() -> None:
    root = workspace_root()
    build_root = root / "data" / "_test_llm_manifest_write"
    build_root.mkdir(parents=True, exist_ok=True)
    try:
        syntax_path = syntax_corpus_path("demo_build", root=build_root)
        materials_path = materials_corpus_path("demo_build", root=build_root)
        rejects_path = corpus_rejects_path("demo_build", root=build_root)
        inventory_path = corpus_inventory_path("demo_build", root=build_root)
        qa_path = corpus_qa_path("demo_build", root=build_root)
        manifest_path = corpus_manifest_path("demo_build", root=build_root)

        write_jsonl([{"zomic_text": "label a"}], syntax_path)
        write_jsonl([{"zomic_text": "label b"}], materials_path)
        write_jsonl([{"zomic_text": "label c"}], rejects_path)
        write_json_object({"rows": 3}, inventory_path)
        write_json_object({"gold_count": 1}, qa_path)

        manifest = build_corpus_manifest(
            config=_config(),
            config_path=root / "configs" / "llm" / "corpus_v1.yaml",
            syntax_count=1,
            materials_count=1,
            reject_count=1,
            inventory_count=3,
            syntax_path=syntax_path,
            materials_path=materials_path,
            rejects_path=rejects_path,
            inventory_path=inventory_path,
            qa_path=qa_path,
        )

        written = write_corpus_manifest(manifest, manifest_path)
        payload = json.loads(written.read_text(encoding="utf-8"))
        assert payload["build_id"] == "zomic_corpus_v1"
        assert payload["syntax_count"] == 1
        assert payload["materials_count"] == 1
    finally:
        shutil.rmtree(build_root, ignore_errors=True)
