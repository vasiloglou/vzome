from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import workspace_root


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root


def corpus_build_dir(build_id: str, root: Path | None = None) -> Path:
    return _artifact_root(root) / "data" / "llm_corpus" / build_id


def syntax_corpus_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "syntax_corpus.jsonl"


def materials_corpus_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "materials_corpus.jsonl"


def corpus_rejects_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "rejects.jsonl"


def corpus_inventory_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "inventory.json"


def corpus_qa_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "qa.json"


def corpus_manifest_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "manifest.json"
