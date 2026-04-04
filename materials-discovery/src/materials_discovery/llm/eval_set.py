from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from materials_discovery.common.io import load_json_object, load_jsonl, write_json_object, write_jsonl
from materials_discovery.common.manifest import file_sha256
from materials_discovery.data_sources.storage import workspace_relative
from materials_discovery.llm.schema import (
    LlmEvalSetExample,
    LlmEvalSetManifest,
    LlmEvalSetSummary,
    CorpusExample,
    CorpusManifest,
)
from materials_discovery.llm.storage import (
    corpus_manifest_path,
    llm_eval_set_manifest_path,
    llm_eval_set_path,
)

_RELEASE_ORDER = {"gold": 0, "silver": 1, "pending": 2, "reject": 3}


def _resolve_workspace_path(root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return root / path


def _example_tags(example: CorpusExample) -> list[str]:
    tags: list[str] = [
        example.provenance.source_family,
        example.provenance.fidelity_tier,
        example.provenance.release_tier,
    ]
    template_family = example.properties.get("template_family")
    if isinstance(template_family, str) and template_family.strip():
        tags.append(template_family.strip())
    unique: list[str] = []
    for tag in tags:
        if tag not in unique:
            unique.append(tag)
    return unique


def load_eval_set(path: Path) -> list[LlmEvalSetExample]:
    return [LlmEvalSetExample.model_validate(row) for row in load_jsonl(path)]


def export_llm_eval_set(
    *,
    build_id: str,
    export_id: str,
    systems: list[str] | None = None,
    release_tiers: tuple[str, ...] = ("gold", "silver"),
    max_examples_per_system: int | None = None,
    root: Path | None = None,
) -> LlmEvalSetSummary:
    workspace = Path.cwd() if root is None else root.resolve()
    manifest_path = corpus_manifest_path(build_id, root=workspace)
    corpus_manifest = CorpusManifest.model_validate(load_json_object(manifest_path))
    materials_path = _resolve_workspace_path(workspace, corpus_manifest.materials_corpus_path)
    examples = [CorpusExample.model_validate(row) for row in load_jsonl(materials_path)]

    allowed_systems = {system.strip() for system in (systems or []) if system.strip()}
    allowed_tiers = {tier.strip() for tier in release_tiers if tier.strip()}

    filtered = [
        example
        for example in examples
        if example.provenance.release_tier in allowed_tiers
        and (not allowed_systems or (example.provenance.system in allowed_systems))
    ]
    filtered.sort(
        key=lambda example: (
            example.provenance.system or "",
            _RELEASE_ORDER.get(example.provenance.release_tier, 99),
            example.provenance.source_family,
            example.provenance.source_record_id,
            example.provenance.example_id,
        )
    )

    selected: list[CorpusExample] = []
    if max_examples_per_system is None:
        selected = filtered
    else:
        counts: dict[str, int] = defaultdict(int)
        for example in filtered:
            system = example.provenance.system or "unknown"
            if counts[system] >= max_examples_per_system:
                continue
            counts[system] += 1
            selected.append(example)

    rows = [
        LlmEvalSetExample(
            example_id=example.provenance.example_id,
            system=example.provenance.system or "Unknown",
            release_tier=example.provenance.release_tier,
            fidelity_tier=example.provenance.fidelity_tier,
            source_family=example.provenance.source_family,
            source_record_id=example.provenance.source_record_id,
            composition=example.composition or {},
            labels=example.labels,
            orbit_names=example.orbit_names,
            tags=_example_tags(example),
            properties=example.properties,
            zomic_text=example.zomic_text,
        )
        for example in selected
    ]

    output_path = llm_eval_set_path(export_id, root=workspace)
    manifest_out_path = llm_eval_set_manifest_path(export_id, root=workspace)
    write_jsonl([row.model_dump(mode="json") for row in rows], output_path)

    manifest = LlmEvalSetManifest(
        export_id=export_id,
        build_id=build_id,
        created_at_utc=datetime.now(UTC).isoformat(),
        corpus_manifest_path=workspace_relative(manifest_path),
        eval_set_path=workspace_relative(output_path),
        systems=sorted({row.system for row in rows}),
        release_tiers=sorted(allowed_tiers, key=lambda tier: _RELEASE_ORDER.get(tier, 99)),
        example_count=len(rows),
        max_examples_per_system=max_examples_per_system,
        output_hashes={"eval_set": file_sha256(output_path)},
    )
    write_json_object(manifest.model_dump(mode="json"), manifest_out_path)

    return LlmEvalSetSummary(
        export_id=export_id,
        example_count=len(rows),
        eval_set_path=str(output_path),
        manifest_path=str(manifest_out_path),
    )
