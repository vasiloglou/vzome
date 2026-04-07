from __future__ import annotations

from collections import Counter
from pathlib import Path

from materials_discovery.common.io import (
    load_json_object,
    load_jsonl,
    load_yaml,
    write_json_object,
    write_jsonl,
    workspace_root,
)
from materials_discovery.llm.schema import (
    TranslatedBenchmarkExcludedRow,
    TranslatedBenchmarkExclusionReason,
    TranslatedBenchmarkIncludedRow,
    TranslatedBenchmarkSetManifest,
    TranslatedBenchmarkSetSpec,
    TranslatedBenchmarkSetSummary,
    TranslationBundleManifest,
    TranslationInventoryRow,
)
from materials_discovery.llm.storage import (
    translated_benchmark_contract_path,
    translated_benchmark_excluded_path,
    translated_benchmark_included_path,
    translated_benchmark_manifest_path,
)


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root.resolve()


def _resolve_artifact_path(path: Path, *, root: Path | None = None) -> Path:
    return path if path.is_absolute() else _artifact_root(root) / path


def _translation_bundle_root(bundle_manifest_path: Path) -> Path:
    marker = ("data", "llm_translation_exports")
    parts = bundle_manifest_path.resolve().parts
    for idx in range(len(parts) - len(marker) + 1):
        if parts[idx : idx + len(marker)] == marker:
            return Path(*parts[:idx]) if idx > 0 else Path(".")
    return bundle_manifest_path.resolve().parents[2]


def load_translated_benchmark_spec(spec_path: Path) -> TranslatedBenchmarkSetSpec:
    return TranslatedBenchmarkSetSpec.model_validate(load_yaml(spec_path))


def _path_for_storage(path: Path, *, root: Path | None = None) -> str:
    resolved = path.resolve()
    artifact_root = _artifact_root(root)
    try:
        return str(resolved.relative_to(artifact_root))
    except ValueError:
        return str(resolved)


def _load_translation_bundle(
    bundle_manifest_path: Path,
) -> tuple[TranslationBundleManifest, list[TranslationInventoryRow]]:
    manifest = TranslationBundleManifest.model_validate(load_json_object(bundle_manifest_path))
    inventory_path = Path(manifest.inventory_path)
    if not inventory_path.is_absolute():
        inventory_path = _translation_bundle_root(bundle_manifest_path) / inventory_path
    rows = [TranslationInventoryRow.model_validate(row) for row in load_jsonl(inventory_path)]
    return manifest, rows


def _evaluate_translation_row(
    *,
    row: TranslationInventoryRow,
    spec: TranslatedBenchmarkSetSpec,
) -> tuple[bool, TranslatedBenchmarkExclusionReason | None, str | None]:
    if spec.systems and row.system not in spec.systems:
        return False, "system_not_selected", f"system '{row.system}' is not in selected systems"
    if row.target_family != spec.target_family:
        return (
            False,
            "target_family_mismatch",
            f"row target_family '{row.target_family}' does not match '{spec.target_family}'",
        )
    if row.fidelity_tier not in spec.allowed_fidelity_tiers:
        return (
            False,
            "fidelity_tier_not_selected",
            f"fidelity_tier '{row.fidelity_tier}' is not allowed by this freeze spec",
        )

    has_explicit_loss = row.fidelity_tier == "lossy" or bool(row.loss_reasons)
    if spec.loss_posture == "lossless_only" and has_explicit_loss:
        return (
            False,
            "loss_posture_rejected",
            "lossless_only rejects rows that carry explicit translation loss",
        )
    if spec.loss_posture == "lossy_only" and not has_explicit_loss:
        return (
            False,
            "loss_posture_rejected",
            "lossy_only requires rows with explicit translation loss",
        )
    return True, None, None


def _build_included_row(
    *,
    benchmark_set_id: str,
    source_export_id: str,
    source_bundle_manifest_path: str,
    row: TranslationInventoryRow,
) -> TranslatedBenchmarkIncludedRow:
    return TranslatedBenchmarkIncludedRow(
        benchmark_set_id=benchmark_set_id,
        source_export_id=source_export_id,
        source_bundle_manifest_path=source_bundle_manifest_path,
        **row.model_dump(mode="json", exclude={"export_id"}),
    )


def _build_excluded_row(
    *,
    benchmark_set_id: str,
    source_export_id: str,
    source_bundle_manifest_path: str,
    row: TranslationInventoryRow,
    exclusion_reason: TranslatedBenchmarkExclusionReason,
    exclusion_detail: str | None,
) -> TranslatedBenchmarkExcludedRow:
    return TranslatedBenchmarkExcludedRow(
        benchmark_set_id=benchmark_set_id,
        source_export_id=source_export_id,
        source_bundle_manifest_path=source_bundle_manifest_path,
        exclusion_reason=exclusion_reason,
        exclusion_detail=exclusion_detail,
        **row.model_dump(mode="json", exclude={"export_id"}),
    )


def _normalized_freeze_spec(spec: TranslatedBenchmarkSetSpec) -> TranslatedBenchmarkSetSpec:
    return spec.model_copy(update={"bundle_manifest_paths": sorted(spec.bundle_manifest_paths)})


def freeze_translated_benchmark_set(
    spec_path: Path, root: Path | None = None
) -> TranslatedBenchmarkSetSummary:
    artifact_root = _artifact_root(root)
    resolved_spec_path = _resolve_artifact_path(spec_path, root=artifact_root)
    spec = _normalized_freeze_spec(load_translated_benchmark_spec(resolved_spec_path))

    # The frozen artifact family is fixed: freeze_contract.json, manifest.json,
    # included.jsonl, and excluded.jsonl, all resolved through storage helpers.
    included_path = translated_benchmark_included_path(spec.benchmark_set_id, root=artifact_root)
    excluded_path = translated_benchmark_excluded_path(spec.benchmark_set_id, root=artifact_root)
    contract_path = translated_benchmark_contract_path(spec.benchmark_set_id, root=artifact_root)
    manifest_path = translated_benchmark_manifest_path(spec.benchmark_set_id, root=artifact_root)

    source_export_ids: list[str] = []
    bundle_rows: list[tuple[str, TranslationBundleManifest, TranslationInventoryRow]] = []
    for bundle_manifest_text in spec.bundle_manifest_paths:
        bundle_manifest_path = _resolve_artifact_path(Path(bundle_manifest_text), root=artifact_root)
        manifest, rows = _load_translation_bundle(bundle_manifest_path)
        source_export_ids.append(manifest.export_id)
        for row in rows:
            bundle_rows.append((bundle_manifest_text, manifest, row))

    bundle_rows.sort(key=lambda item: (item[0], item[2].candidate_id, item[2].payload_hash))

    included_rows: list[TranslatedBenchmarkIncludedRow] = []
    excluded_rows: list[TranslatedBenchmarkExcludedRow] = []
    seen_candidates: dict[str, tuple[str, str]] = {}

    for bundle_manifest_text, manifest, row in bundle_rows:
        allowed, exclusion_reason, exclusion_detail = _evaluate_translation_row(row=row, spec=spec)
        if not allowed:
            excluded_rows.append(
                _build_excluded_row(
                    benchmark_set_id=spec.benchmark_set_id,
                    source_export_id=manifest.export_id,
                    source_bundle_manifest_path=bundle_manifest_text,
                    row=row,
                    exclusion_reason=exclusion_reason or "loss_posture_rejected",
                    exclusion_detail=exclusion_detail,
                )
            )
            continue

        prior = seen_candidates.get(row.candidate_id)
        if prior is None:
            included_rows.append(
                _build_included_row(
                    benchmark_set_id=spec.benchmark_set_id,
                    source_export_id=manifest.export_id,
                    source_bundle_manifest_path=bundle_manifest_text,
                    row=row,
                )
            )
            seen_candidates[row.candidate_id] = (row.payload_hash, bundle_manifest_text)
            continue

        prior_payload_hash, prior_bundle_manifest_path = prior
        if prior_payload_hash != row.payload_hash:
            raise ValueError(
                "conflicting translated benchmark rows for "
                f"candidate_id '{row.candidate_id}' from "
                f"'{prior_bundle_manifest_path}' and '{bundle_manifest_text}'"
            )

        excluded_rows.append(
            _build_excluded_row(
                benchmark_set_id=spec.benchmark_set_id,
                source_export_id=manifest.export_id,
                source_bundle_manifest_path=bundle_manifest_text,
                row=row,
                exclusion_reason="duplicate_translation_row",
                exclusion_detail=(
                    "duplicate of candidate_id "
                    f"'{row.candidate_id}' already kept from '{prior_bundle_manifest_path}'"
                ),
            )
        )

    exclusion_reason_counts = dict(
        sorted(Counter(row.exclusion_reason for row in excluded_rows).items())
    )

    write_json_object(spec.model_dump(mode="json"), contract_path)
    write_jsonl([row.model_dump(mode="json") for row in included_rows], included_path)
    write_jsonl([row.model_dump(mode="json") for row in excluded_rows], excluded_path)
    manifest = TranslatedBenchmarkSetManifest(
        benchmark_set_id=spec.benchmark_set_id,
        contract_path=_path_for_storage(contract_path, root=artifact_root),
        included_inventory_path=_path_for_storage(included_path, root=artifact_root),
        excluded_inventory_path=_path_for_storage(excluded_path, root=artifact_root),
        source_bundle_manifest_paths=spec.bundle_manifest_paths,
        source_export_ids=source_export_ids,
        included_count=len(included_rows),
        excluded_count=len(excluded_rows),
        target_family=spec.target_family,
        systems=spec.systems,
        exclusion_reason_counts=exclusion_reason_counts,
        filter_contract=spec,
    )
    write_json_object(manifest.model_dump(mode="json"), manifest_path)

    return TranslatedBenchmarkSetSummary(
        benchmark_set_id=spec.benchmark_set_id,
        target_family=spec.target_family,
        loss_posture=spec.loss_posture,
        systems=spec.systems,
        included_count=len(included_rows),
        excluded_count=len(excluded_rows),
        contract_path=str(contract_path.resolve()),
        manifest_path=str(manifest_path.resolve()),
        included_inventory_path=str(included_path.resolve()),
        excluded_inventory_path=str(excluded_path.resolve()),
    )


__all__ = [
    "freeze_translated_benchmark_set",
    "load_translated_benchmark_spec",
]
