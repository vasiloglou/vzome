from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from materials_discovery.common.io import ensure_parent, load_json_object, write_json_object, write_jsonl
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord, StructureRepresentation
from materials_discovery.llm.compiler import compile_zomic_script
from materials_discovery.llm.converters.cif2zomic import canonical_record_to_zomic
from materials_discovery.llm.converters.generated_export import generated_export_to_corpus_examples
from materials_discovery.llm.converters.native_zomic import zomic_file_to_corpus_example
from materials_discovery.llm.converters.projection2zomic import projection_payload_to_zomic
from materials_discovery.llm.converters.record2zomic import candidate_to_zomic
from materials_discovery.llm.inventory import build_inventory
from materials_discovery.llm.manifests import build_corpus_manifest, write_corpus_manifest
from materials_discovery.llm.qa import dedupe_corpus_examples, grade_corpus_example, summarize_corpus_quality
from materials_discovery.llm.schema import CorpusBuildConfig, CorpusBuildSummary, CorpusExample, CorpusInventoryRow
from materials_discovery.llm.storage import (
    corpus_inventory_path,
    corpus_manifest_path,
    corpus_qa_path,
    corpus_rejects_path,
    materials_corpus_path,
    syntax_corpus_path,
)


def _repo_root(root: Path | None = None) -> Path:
    if root is None:
        return Path(__file__).resolve().parents[4]
    return root.resolve()


def _workspace_root(repo_root: Path) -> Path:
    return repo_root / "materials-discovery"


def _resolve_repo_path(repo_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return repo_root / path


def _read_json_line(path: Path, line_number: int) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        for current_line, line in enumerate(handle, start=1):
            if current_line != line_number:
                continue
            payload = line.strip()
            if not payload:
                raise ValueError(f"expected JSON object on line {line_number} in {path}")
            parsed = json.loads(payload)
            if not isinstance(parsed, dict):
                raise ValueError(f"expected JSON object on line {line_number} in {path}")
            return parsed
    raise ValueError(f"line {line_number} not found in {path}")


def _override_inventory_provenance(example: CorpusExample, row: CorpusInventoryRow) -> CorpusExample:
    provenance = example.provenance.model_copy(
        update={
            "source_family": row.source_family,
            "source_path": row.source_path,
            "source_record_id": row.source_record_id,
            "system": row.system or example.provenance.system,
        }
    )
    properties = dict(example.properties)
    properties["loader_hint"] = row.loader_hint
    properties["input_kind"] = row.input_kind
    return example.model_copy(update={"provenance": provenance, "properties": properties})


def _resolve_canonical_paths(record: CanonicalRawSourceRecord, workspace_root: Path) -> CanonicalRawSourceRecord:
    structure_representations = []
    for representation in record.common.structure_representations:
        payload_path = representation.payload_path
        if payload_path and not Path(payload_path).is_absolute():
            payload_path = str(workspace_root / payload_path)
        structure_representations.append(
            StructureRepresentation.model_validate(
                {
                    **representation.model_dump(mode="json"),
                    "payload_path": payload_path,
                }
            )
        )
    common = record.common.model_copy(update={"structure_representations": structure_representations})
    return record.model_copy(update={"common": common})


def _validate_for_corpus(example: CorpusExample) -> CorpusExample:
    exact_native = (
        example.provenance.fidelity_tier == "exact"
        and example.provenance.source_family in {"repo_regression", "repo_parts", "materials_design", "generated_export"}
    )
    if exact_native:
        validation = example.validation.model_copy(
            update={
                "parse_status": "passed",
                "compile_status": "passed",
                "collision_free": True,
                "site_count": example.validation.site_count or len(example.labels),
            }
        )
        return example.model_copy(update={"validation": validation})

    compile_result = compile_zomic_script(
        example.zomic_text,
        prototype_key=str(example.properties.get("prototype_key", example.provenance.source_record_id)),
        system_name=example.provenance.system or "Unknown",
        template_family=str(example.properties.get("template_family", "generic")),
    )
    validation = example.validation.model_copy(
        update={
            "parse_status": compile_result["parse_status"],
            "compile_status": compile_result["compile_status"],
            "collision_free": compile_result["compile_status"] == "passed",
            "site_count": example.validation.site_count or len(example.labels),
            "raw_export_path": compile_result.get("raw_export_path"),
            "geometry_equivalence": compile_result.get("geometry_equivalence"),
            "geometry_error": compile_result.get("geometry_error"),
            "error_message": compile_result.get("error_message"),
        }
    )
    return example.model_copy(update={"validation": validation})


def _examples_from_inventory_row(row: CorpusInventoryRow, repo_root: Path) -> list[CorpusExample]:
    path = _resolve_repo_path(repo_root, row.source_path)
    workspace_root = _workspace_root(repo_root)

    if row.loader_hint == "native_zomic":
        return [
            _override_inventory_provenance(
                zomic_file_to_corpus_example(path, source_family=row.source_family, system=row.system),
                row,
            )
        ]

    if row.loader_hint == "candidate_record":
        payload = _read_json_line(path, int(row.record_locator["line"]))
        record = CandidateRecord.model_validate(payload)
        return [_override_inventory_provenance(candidate_to_zomic(record), row)]

    if row.loader_hint == "generated_export":
        return [_override_inventory_provenance(example, row) for example in generated_export_to_corpus_examples(path)]

    if row.loader_hint in {"canonical_source", "reference_pack"}:
        payload = _read_json_line(path, int(row.record_locator["line"]))
        record = CanonicalRawSourceRecord.model_validate(payload)
        record = _resolve_canonical_paths(record, workspace_root)
        return [_override_inventory_provenance(canonical_record_to_zomic(record), row)]

    if row.loader_hint == "pyqcstrc_projection":
        payload = load_json_object(path)
        return [_override_inventory_provenance(projection_payload_to_zomic(payload), row)]

    raise ValueError(f"unsupported inventory loader_hint: {row.loader_hint}")


def _write_json_array(rows: list[dict[str, Any]], path: Path) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")


def build_llm_corpus(config: CorpusBuildConfig, *, root: Path | None = None) -> CorpusBuildSummary:
    repo_root = _repo_root(root)
    workspace_root = _workspace_root(repo_root)
    inventory = build_inventory(config, root=repo_root)

    examples: list[CorpusExample] = []
    for row in inventory:
        examples.extend(_examples_from_inventory_row(row, repo_root))

    validated = [_validate_for_corpus(example) for example in examples]
    graded = [grade_corpus_example(example, config) for example in validated]
    deduped = dedupe_corpus_examples(graded)

    syntax_examples = [example for example in deduped if example.provenance.release_tier != "reject"]
    materials_examples = [
        example
        for example in deduped
        if example.provenance.release_tier != "reject" and example.composition is not None
    ]
    reject_examples = [example for example in deduped if example.provenance.release_tier == "reject"]
    qa_summary = summarize_corpus_quality(deduped)

    syntax_path = syntax_corpus_path(config.build_id, root=workspace_root)
    materials_path = materials_corpus_path(config.build_id, root=workspace_root)
    rejects_path = corpus_rejects_path(config.build_id, root=workspace_root)
    inventory_path = corpus_inventory_path(config.build_id, root=workspace_root)
    qa_path = corpus_qa_path(config.build_id, root=workspace_root)
    manifest_path = corpus_manifest_path(config.build_id, root=workspace_root)

    write_jsonl([example.model_dump(mode="json") for example in syntax_examples], syntax_path)
    write_jsonl([example.model_dump(mode="json") for example in materials_examples], materials_path)
    write_jsonl([example.model_dump(mode="json") for example in reject_examples], rejects_path)
    _write_json_array([row.model_dump(mode="json") for row in inventory], inventory_path)
    write_json_object(qa_summary.model_dump(mode="json"), qa_path)

    manifest = build_corpus_manifest(
        config=config,
        config_path=workspace_root / "configs" / "llm" / f"{config.build_id}.yaml",
        syntax_count=len(syntax_examples),
        materials_count=len(materials_examples),
        reject_count=len(reject_examples),
        inventory_count=len(inventory),
        syntax_path=syntax_path,
        materials_path=materials_path,
        rejects_path=rejects_path,
        inventory_path=inventory_path,
        qa_path=qa_path,
    )
    write_corpus_manifest(manifest, manifest_path)

    return CorpusBuildSummary(
        build_id=config.build_id,
        syntax_count=len(syntax_examples),
        materials_count=len(materials_examples),
        reject_count=len(reject_examples),
        inventory_count=len(inventory),
        syntax_corpus_path=str(syntax_path),
        materials_corpus_path=str(materials_path),
        rejects_path=str(rejects_path),
        inventory_path=str(inventory_path),
        qa_path=str(qa_path),
        manifest_path=str(manifest_path),
    )
