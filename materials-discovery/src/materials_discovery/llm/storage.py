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


def llm_eval_set_dir(export_id: str, root: Path | None = None) -> Path:
    return _artifact_root(root) / "data" / "llm_eval_sets" / export_id


def llm_eval_set_path(export_id: str, root: Path | None = None) -> Path:
    return llm_eval_set_dir(export_id, root) / "eval_set.jsonl"


def llm_eval_set_manifest_path(export_id: str, root: Path | None = None) -> Path:
    return llm_eval_set_dir(export_id, root) / "manifest.json"


def llm_acceptance_dir(pack_id: str, root: Path | None = None) -> Path:
    return _artifact_root(root) / "data" / "benchmarks" / "llm_acceptance" / pack_id


def llm_acceptance_pack_path(pack_id: str, root: Path | None = None) -> Path:
    return llm_acceptance_dir(pack_id, root) / "acceptance_pack.json"
