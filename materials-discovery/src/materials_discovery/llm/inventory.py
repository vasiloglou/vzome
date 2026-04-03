from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from materials_discovery.common.schema import CandidateRecord
from materials_discovery.common.io import load_json_object, workspace_root
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord
from materials_discovery.llm.schema import CorpusBuildConfig, CorpusInventoryRow


def _repo_root(root: Path | None = None) -> Path:
    return root.resolve() if root is not None else workspace_root().parent.resolve()


def _relative_path(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root))


def _system_slug(value: str | None) -> str | None:
    if value is None:
        return None
    slug = value.strip().lower().replace("-", "_").replace(" ", "_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug or None


def _matches_configured_systems(system: str | None, systems: list[str]) -> bool:
    if not systems or system is None:
        return True
    allowed = {_system_slug(entry) for entry in systems}
    return _system_slug(system) in allowed


def _infer_system_from_stem(stem: str) -> str | None:
    tokens = [token for token in stem.split("_") if token]
    if len(tokens) < 2:
        return None
    system_tokens: list[str] = []
    for token in tokens:
        if len(token) > 2:
            break
        system_tokens.append(token)
        if len(system_tokens) == 3:
            break
    if len(system_tokens) < 2:
        return None
    return "-".join(token.capitalize() for token in system_tokens)


def _relative_metadata_path(root: Path, value: str | None) -> str | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        return value
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return value


def _iter_jsonl_rows(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            payload = line.strip()
            if not payload:
                continue
            parsed = json.loads(payload)
            if not isinstance(parsed, dict):
                raise ValueError(f"Expected JSON object on line {line_number} in {path}")
            rows.append((line_number, parsed))
    return rows


def _inventory_row(
    *,
    source_family: str,
    source_path: str,
    system: str | None,
    source_record_id: str,
    input_kind: str,
    record_locator: dict[str, Any],
    loader_hint: str,
    metadata: dict[str, Any],
) -> CorpusInventoryRow:
    return CorpusInventoryRow.model_validate(
        {
            "source_family": source_family,
            "source_path": source_path,
            "system": system,
            "source_record_id": source_record_id,
            "input_kind": input_kind,
            "record_locator": record_locator,
            "loader_hint": loader_hint,
            "metadata": metadata,
        }
    )


def collect_repo_zomic_inventory(root: Path) -> list[CorpusInventoryRow]:
    repo_root = _repo_root(root)
    rows: list[CorpusInventoryRow] = []
    families = [
        ("repo_regression", repo_root / "core/src/regression/files/Zomic/**/*.zomic"),
        ("repo_parts", repo_root / "core/src/main/resources/com/vzome/core/parts/**/*.zomic"),
        ("materials_design", repo_root / "materials-discovery/designs/zomic/*.zomic"),
    ]
    for source_family, pattern in families:
        for path in sorted(repo_root.glob(str(pattern.relative_to(repo_root)))):
            relative_path = _relative_path(repo_root, path)
            rows.append(
                _inventory_row(
                    source_family=source_family,
                    source_path=relative_path,
                    system=_infer_system_from_stem(path.stem)
                    if source_family == "materials_design"
                    else None,
                    source_record_id=relative_path,
                    input_kind="zomic_file",
                    record_locator={"path": relative_path},
                    loader_hint="native_zomic",
                    metadata={
                        "file_name": path.name,
                        "path_kind": source_family,
                    },
                )
            )
    return rows


def collect_candidate_inventory(root: Path, systems: list[str]) -> list[CorpusInventoryRow]:
    repo_root = _repo_root(root)
    rows: list[CorpusInventoryRow] = []
    candidates_dir = repo_root / "materials-discovery/data/candidates"
    for path in sorted(candidates_dir.glob("*.jsonl")):
        relative_path = _relative_path(repo_root, path)
        for line_number, payload in _iter_jsonl_rows(path):
            record = CandidateRecord.model_validate(payload)
            if not _matches_configured_systems(record.system, systems):
                continue
            rows.append(
                _inventory_row(
                    source_family="candidate_record",
                    source_path=relative_path,
                    system=record.system,
                    source_record_id=record.candidate_id,
                    input_kind="candidate_record",
                    record_locator={"path": relative_path, "line": line_number},
                    loader_hint="candidate_record",
                    metadata={
                        "template_family": record.template_family,
                        "site_count": len(record.sites),
                        "prototype_key": record.provenance.get("prototype_key"),
                    },
                )
            )
    return rows


def collect_generated_export_inventory(root: Path) -> list[CorpusInventoryRow]:
    repo_root = _repo_root(root)
    rows: list[CorpusInventoryRow] = []
    generated_dir = repo_root / "materials-discovery/data/prototypes/generated"
    for path in sorted(generated_dir.glob("*.raw.json")):
        payload = load_json_object(path)
        relative_path = _relative_path(repo_root, path)
        record_id = path.name[: -len(".raw.json")]
        rows.append(
            _inventory_row(
                source_family="generated_export",
                source_path=relative_path,
                system=_infer_system_from_stem(record_id),
                source_record_id=record_id,
                input_kind="generated_export",
                record_locator={"path": relative_path, "json_pointer": "$"},
                loader_hint="generated_export",
                metadata={
                    "parser": payload.get("parser"),
                    "symmetry": payload.get("symmetry"),
                    "zomic_file": _relative_metadata_path(repo_root, payload.get("zomic_file")),
                    "labeled_point_count": len(payload.get("labeled_points", [])),
                },
            )
        )
    return rows


def collect_source_inventory(
    root: Path,
    source_keys: list[str],
    reference_pack_ids: list[str],
) -> list[CorpusInventoryRow]:
    repo_root = _repo_root(root)
    rows: list[CorpusInventoryRow] = []

    source_root = repo_root / "materials-discovery/data/external/sources"
    source_patterns = (
        [source_root / source_key / "*/canonical_records.jsonl" for source_key in source_keys]
        if source_keys
        else [source_root / "*" / "*/canonical_records.jsonl"]
    )
    for pattern in source_patterns:
        for path in sorted(repo_root.glob(str(pattern.relative_to(repo_root)))):
            relative_path = _relative_path(repo_root, path)
            for line_number, payload in _iter_jsonl_rows(path):
                record = CanonicalRawSourceRecord.model_validate(payload)
                system = (
                    record.common.chemical_system
                    or record.common.reported_properties.get("system")
                    or record.source_metadata.get("system")
                )
                rows.append(
                    _inventory_row(
                        source_family="canonical_source",
                        source_path=relative_path,
                        system=system,
                        source_record_id=record.local_record_id,
                        input_kind="canonical_record",
                        record_locator={"path": relative_path, "line": line_number},
                        loader_hint="canonical_source",
                        metadata={
                            "snapshot_id": record.snapshot.snapshot_id,
                            "source_key": record.source.source_key,
                            "source_name": record.source.source_name,
                            "upstream_record_id": record.source.source_record_id,
                        },
                    )
                )

    pack_root = repo_root / "materials-discovery/data/external/reference_packs"
    pack_patterns = (
        [pack_root / "*" / pack_id / "canonical_records.jsonl" for pack_id in reference_pack_ids]
        if reference_pack_ids
        else [pack_root / "*" / "*" / "canonical_records.jsonl"]
    )
    for pattern in pack_patterns:
        for path in sorted(repo_root.glob(str(pattern.relative_to(repo_root)))):
            relative_path = _relative_path(repo_root, path)
            pack_id = path.parent.name
            system_slug = path.parent.parent.name
            for line_number, payload in _iter_jsonl_rows(path):
                record = CanonicalRawSourceRecord.model_validate(payload)
                system = (
                    record.common.chemical_system
                    or record.common.reported_properties.get("system")
                    or system_slug.replace("_", "-").title()
                )
                rows.append(
                    _inventory_row(
                        source_family="reference_pack",
                        source_path=relative_path,
                        system=system,
                        source_record_id=f"{pack_id}:{record.local_record_id}",
                        input_kind="canonical_record",
                        record_locator={"path": relative_path, "line": line_number},
                        loader_hint="reference_pack",
                        metadata={
                            "pack_id": pack_id,
                            "system_slug": system_slug,
                            "source_key": record.source.source_key,
                            "snapshot_id": record.snapshot.snapshot_id,
                            "upstream_record_id": record.source.source_record_id,
                        },
                    )
                )

    return rows


def collect_pyqcstrc_inventory(root: Path) -> list[CorpusInventoryRow]:
    repo_root = _repo_root(root)
    path = repo_root / "materials-discovery/tests/fixtures/pyqcstrc_projection_sample.json"
    if not path.exists():
        return []
    payload = load_json_object(path)
    relative_path = _relative_path(repo_root, path)
    return [
        _inventory_row(
            source_family="pyqcstrc_projection",
            source_path=relative_path,
            system=payload.get("system"),
            source_record_id=str(payload.get("model_id", path.stem)),
            input_kind="projection_payload",
            record_locator={"path": relative_path, "json_pointer": "$"},
            loader_hint="pyqcstrc_projection",
            metadata={
                "coordinate_system": payload.get("coordinate_system"),
                "position_count": len(payload.get("positions", [])),
                "source": payload.get("source"),
            },
        )
    ]


def build_inventory(
    config: CorpusBuildConfig,
    root: Path | None = None,
) -> list[CorpusInventoryRow]:
    repo_root = _repo_root(root)
    rows: list[CorpusInventoryRow] = []
    if config.include_repo_regression or config.include_repo_parts or config.include_materials_designs:
        repo_rows = collect_repo_zomic_inventory(repo_root)
        for row in repo_rows:
            if row.source_family == "repo_regression" and not config.include_repo_regression:
                continue
            if row.source_family == "repo_parts" and not config.include_repo_parts:
                continue
            if row.source_family == "materials_design" and not config.include_materials_designs:
                continue
            rows.append(row)
    if config.include_candidate_records:
        rows.extend(collect_candidate_inventory(repo_root, config.systems))
    if config.include_generated_exports:
        rows.extend(collect_generated_export_inventory(repo_root))
    if config.include_canonical_sources or config.include_reference_packs:
        source_rows = collect_source_inventory(repo_root, config.source_keys, config.reference_pack_ids)
        for row in source_rows:
            if row.source_family == "canonical_source" and not config.include_canonical_sources:
                continue
            if row.source_family == "reference_pack" and not config.include_reference_packs:
                continue
            rows.append(row)
    if config.include_pyqcstrc_projection:
        rows.extend(collect_pyqcstrc_inventory(repo_root))

    filtered_rows = [
        row
        for row in rows
        if _matches_configured_systems(row.system, config.systems)
    ]
    return sorted(
        filtered_rows,
        key=lambda row: (
            row.source_family,
            row.system or "",
            row.source_path,
            row.source_record_id,
        ),
    )
