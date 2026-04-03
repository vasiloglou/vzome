from __future__ import annotations

from pathlib import Path

from materials_discovery.llm.storage import (
    corpus_build_dir,
    corpus_inventory_path,
    corpus_manifest_path,
    corpus_qa_path,
    corpus_rejects_path,
    materials_corpus_path,
    syntax_corpus_path,
)


def test_corpus_build_dir_uses_llm_corpus_subdirectory(tmp_path: Path) -> None:
    build_dir = corpus_build_dir("demo_build", root=tmp_path)
    assert build_dir == tmp_path / "data" / "llm_corpus" / "demo_build"


def test_all_public_paths_resolve_under_same_build_directory(tmp_path: Path) -> None:
    build_dir = corpus_build_dir("demo_build", root=tmp_path)
    paths = [
        syntax_corpus_path("demo_build", root=tmp_path),
        materials_corpus_path("demo_build", root=tmp_path),
        corpus_rejects_path("demo_build", root=tmp_path),
        corpus_inventory_path("demo_build", root=tmp_path),
        corpus_qa_path("demo_build", root=tmp_path),
        corpus_manifest_path("demo_build", root=tmp_path),
    ]
    for path in paths:
        assert path.parent == build_dir

