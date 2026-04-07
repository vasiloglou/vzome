from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

from materials_discovery.common.io import load_json_object, write_json_object, write_jsonl, workspace_root
from materials_discovery.common.manifest import file_sha256
from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm.schema import (
    TranslationBundleManifest,
    TranslationExportSummary,
    TranslationInventoryRow,
    resolve_translation_target,
)
from materials_discovery.llm.storage import (
    llm_translation_inventory_path,
    llm_translation_manifest_path,
    llm_translation_payload_dir,
)
from materials_discovery.llm.translation import prepare_translated_structure
from materials_discovery.llm.translation_export import emit_translated_structure


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root.resolve()


def _path_for_storage(path: Path, *, root: Path | None = None) -> str:
    resolved = path.resolve()
    artifact_root = _artifact_root(root)
    try:
        return str(resolved.relative_to(artifact_root))
    except ValueError:
        return str(resolved)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _safe_filename(candidate_id: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", candidate_id.strip())
    return sanitized or "translated_candidate"


def _payload_suffix(target_family: str) -> str:
    if target_family == "cif":
        return ".cif"
    if target_family == "material_string":
        return ".material_string.txt"
    raise ValueError(f"unsupported translation target family: {target_family}")


def export_translation_bundle(
    *,
    candidates: Sequence[CandidateRecord],
    input_path: Path,
    target_family: str,
    export_id: str,
    root: Path | None = None,
    stage_manifest_path: str | None = None,
    source_lineage: dict[str, Any] | None = None,
    benchmark_context: dict[str, Any] | None = None,
) -> TranslationExportSummary:
    if not candidates:
        raise ValueError("translation bundle export requires at least one candidate")

    artifact_root = _artifact_root(root)
    descriptor = resolve_translation_target(target_family)
    manifest_path = llm_translation_manifest_path(export_id, root=artifact_root)
    inventory_path = llm_translation_inventory_path(export_id, root=artifact_root)
    payload_dir = llm_translation_payload_dir(export_id, root=artifact_root)

    existing_manifest: TranslationBundleManifest | None = None
    if manifest_path.exists():
        existing_manifest = TranslationBundleManifest.model_validate(load_json_object(manifest_path))
        if stage_manifest_path is None:
            stage_manifest_path = existing_manifest.stage_manifest_path
        if source_lineage is None:
            source_lineage = existing_manifest.source_lineage
        if benchmark_context is None:
            benchmark_context = existing_manifest.benchmark_context
        created_at_utc = existing_manifest.created_at_utc
    else:
        created_at_utc = _utc_now()

    payload_dir.mkdir(parents=True, exist_ok=True)

    rows: list[TranslationInventoryRow] = []
    for candidate in candidates:
        translated = prepare_translated_structure(candidate, descriptor)
        emitted = emit_translated_structure(translated)
        assert emitted.emitted_text is not None

        payload_path = payload_dir / f"{_safe_filename(candidate.candidate_id)}{_payload_suffix(descriptor.family)}"
        payload_path.write_text(emitted.emitted_text, encoding="utf-8")

        rows.append(
            TranslationInventoryRow(
                export_id=export_id,
                candidate_id=candidate.candidate_id,
                system=candidate.system,
                template_family=candidate.template_family,
                target_family=descriptor.family,
                target_format=descriptor.target_format,
                fidelity_tier=emitted.fidelity_tier,
                loss_reasons=emitted.loss_reasons,
                diagnostic_codes=[diagnostic.code for diagnostic in emitted.diagnostics],
                composition=emitted.composition,
                payload_path=_path_for_storage(payload_path, root=artifact_root),
                payload_hash=file_sha256(payload_path),
                emitted_text=emitted.emitted_text,
            )
        )

    write_jsonl([row.model_dump(mode="json") for row in rows], inventory_path)

    manifest = TranslationBundleManifest(
        export_id=export_id,
        created_at_utc=created_at_utc,
        input_path=_path_for_storage(input_path, root=artifact_root),
        target_family=descriptor.family,
        target_format=descriptor.target_format,
        inventory_path=_path_for_storage(inventory_path, root=artifact_root),
        payload_dir=_path_for_storage(payload_dir, root=artifact_root),
        candidate_count=len(candidates),
        exported_count=len(rows),
        lossy_count=sum(row.fidelity_tier == "lossy" for row in rows),
        stage_manifest_path=stage_manifest_path,
        source_lineage=source_lineage,
        benchmark_context=benchmark_context,
    )
    write_json_object(manifest.model_dump(mode="json"), manifest_path)

    return TranslationExportSummary(
        export_id=export_id,
        target_family=descriptor.family,
        target_format=descriptor.target_format,
        candidate_count=len(candidates),
        exported_count=len(rows),
        lossy_count=manifest.lossy_count,
        manifest_path=str(manifest_path),
        inventory_path=str(inventory_path),
        payload_dir=str(payload_dir),
        stage_manifest_path=stage_manifest_path,
    )
