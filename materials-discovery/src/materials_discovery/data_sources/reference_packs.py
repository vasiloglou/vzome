"""Phase 4 reference-pack assembly and reuse.

A **reference pack** is an upstream, no-DFT artifact built from multiple
staged canonical-source snapshots.  It is assembled once, written to a
dedicated directory, and can be reused in downstream pipeline runs.

Pack directory layout::

    data/external/reference_packs/{system_slug}/{pack_id}/
        canonical_records.jsonl   # merged, deduplicated canonical records
        pack_manifest.json        # deterministic lineage + fingerprint

Usage::

    from materials_discovery.data_sources.reference_packs import assemble_reference_pack

    manifest = assemble_reference_pack(config, system_slug="al_cu_fe")

The function respects ``ingestion.reference_pack.reuse_cached_pack``: when
``True`` and a complete cached pack already exists it returns immediately
without re-reading source snapshots.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from materials_discovery.common.io import (
    load_jsonl,
    write_json_object,
    write_jsonl,
)
from materials_discovery.common.schema import (
    ReferencePackConfig,
    ReferencePackMemberConfig,
    SystemConfig,
)
from materials_discovery.data_sources.schema import (
    CanonicalRawSourceRecord,
    ReferencePackManifest,
    ReferencePackMemberResult,
)
from materials_discovery.data_sources.storage import (
    canonical_records_path as snapshot_canonical_records_path,
    reference_pack_canonical_records_path,
    reference_pack_dir,
    reference_pack_manifest_path,
    snapshot_manifest_path as snapshot_manifest_path_fn,
    workspace_relative,
)

# Source keys that are QC/approximant-specific receive a higher priority than
# generic periodic-crystal sources when both describe the same record.
_QC_PRIORITY_SOURCES: frozenset[str] = frozenset(
    {
        "hypodx",
        "hypodx_v2",
        "hypodx_pinned",
    }
)

# Lower number = higher priority (wins deduplication).
_DEFAULT_PRIORITY_ORDER: list[str] = [
    "hypodx",
    "hypodx_v2",
    "hypodx_pinned",
    "cod",
    "oqmd",
    "jarvis",
    "materials_project",
    "alexandria",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _source_priority(source_key: str, explicit_order: list[str]) -> int:
    """Return numeric priority for *source_key* (lower = wins dedup)."""
    order = explicit_order if explicit_order else _DEFAULT_PRIORITY_ORDER
    try:
        return order.index(source_key)
    except ValueError:
        # Unknown sources get lower priority than any known source.
        return len(order) + 999


def _pack_fingerprint(members: list[ReferencePackMemberResult]) -> str:
    """Deterministic fingerprint based on member source keys, snapshot IDs,
    and canonical record counts.  Stable across Python invocations."""
    payload = json.dumps(
        [
            {
                "source_key": m.source_key,
                "snapshot_id": m.snapshot_id,
                "canonical_record_count": m.canonical_record_count,
                "priority_rank": m.priority_rank,
            }
            for m in sorted(members, key=lambda m: (m.priority_rank, m.source_key))
        ],
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:32]


def _normalize_system_slug(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def _load_member_records(
    member: ReferencePackMemberConfig,
    artifact_root: str | None = None,
) -> tuple[list[CanonicalRawSourceRecord], str, str | None]:
    """Load canonical records for one pack member.

    Returns (records, canonical_path_str, manifest_path_str | None).
    """
    # Allow explicit override paths in the config (useful for fixtures / tests)
    if member.staged_canonical_path is not None:
        canonical_path = Path(member.staged_canonical_path)
    else:
        canonical_path = snapshot_canonical_records_path(
            member.source_key,
            member.snapshot_id,
            artifact_root,
        )

    if not canonical_path.exists():
        raise FileNotFoundError(
            f"canonical records not found for {member.source_key}:{member.snapshot_id} "
            f"at {canonical_path}"
        )

    raw_rows = load_jsonl(canonical_path)
    records = [CanonicalRawSourceRecord.model_validate(row) for row in raw_rows]

    manifest_path_str: str | None = None
    if member.staged_manifest_path is not None:
        manifest_path_str = member.staged_manifest_path
    else:
        mp = snapshot_manifest_path_fn(member.source_key, member.snapshot_id, artifact_root)
        if mp.exists():
            manifest_path_str = workspace_relative(mp)

    return records, workspace_relative(canonical_path), manifest_path_str


# ---------------------------------------------------------------------------
# Deduplication (uses the same semantics as the Phase 3 projection seam)
# ---------------------------------------------------------------------------


def _composition_fingerprint(record: CanonicalRawSourceRecord) -> tuple[tuple[str, float], ...]:
    if record.common.composition:
        return tuple(
            sorted(
                (elem.strip().lower(), round(frac, 8))
                for elem, frac in record.common.composition.items()
            )
        )
    return ()


def _record_dedup_key(
    record: CanonicalRawSourceRecord,
) -> tuple[str, str, tuple[tuple[str, float], ...]]:
    """Normalized (system, phase_name, composition) key for overlap detection."""
    system = (record.common.chemical_system or "").strip().lower()
    phase_name = (
        (record.common.reported_properties.get("phase_name") or "")
        if isinstance(record.common.reported_properties, dict)
        else ""
    )
    if not isinstance(phase_name, str):
        phase_name = ""
    phase_name = phase_name.strip().lower()
    comp_fp = _composition_fingerprint(record)
    return system, phase_name, comp_fp


def _merge_records(
    all_records: list[tuple[str, CanonicalRawSourceRecord]],
    priority_order: list[str],
) -> tuple[list[CanonicalRawSourceRecord], int]:
    """Deduplicate records across sources, keeping the highest-priority record
    when two records share the same (system, phase_name, composition) key.

    Returns (deduped_records, overlap_count).
    """
    # Map: dedup_key -> (priority_rank, source_key, record)
    winners: dict[
        tuple[str, str, tuple[tuple[str, float], ...]],
        tuple[int, str, CanonicalRawSourceRecord],
    ] = {}
    overlap_count = 0

    for source_key, record in all_records:
        key = _record_dedup_key(record)
        priority = _source_priority(source_key, priority_order)
        current = winners.get(key)
        if current is None:
            winners[key] = (priority, source_key, record)
        else:
            overlap_count += 1
            current_priority = current[0]
            if priority < current_priority:
                winners[key] = (priority, source_key, record)

    ordered = [rec for _, _, rec in winners.values()]
    return ordered, overlap_count


# ---------------------------------------------------------------------------
# Cached-pack detection
# ---------------------------------------------------------------------------


def _cached_pack_is_complete(
    system_slug: str,
    pack_id: str,
    pack_root: str | None = None,
) -> bool:
    canonical_path = reference_pack_canonical_records_path(system_slug, pack_id, pack_root)
    manifest_path = reference_pack_manifest_path(system_slug, pack_id, pack_root)
    return canonical_path.exists() and manifest_path.exists()


def load_cached_pack_manifest(
    system_slug: str,
    pack_id: str,
    pack_root: str | None = None,
) -> ReferencePackManifest | None:
    """Return a cached ReferencePackManifest if a complete pack exists, else None."""
    if not _cached_pack_is_complete(system_slug, pack_id, pack_root):
        return None
    manifest_path = reference_pack_manifest_path(system_slug, pack_id, pack_root)
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    return ReferencePackManifest.model_validate(raw)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def assemble_reference_pack(
    pack_config: ReferencePackConfig,
    system_slug: str,
    artifact_root: str | None = None,
    pack_root: str | None = None,
) -> ReferencePackManifest:
    """Assemble (or reuse) a reference pack from staged canonical source snapshots.

    Parameters
    ----------
    pack_config:
        The ``ingestion.reference_pack`` config block from the system config.
    system_slug:
        URL-safe slug for the benchmark system (e.g. ``"al_cu_fe"``).
    artifact_root:
        Optional override for the source-snapshot staging root directory.
        Passed through to ``canonical_records_path()`` / ``snapshot_manifest_path()``.
    pack_root:
        Optional override for the reference-pack output root directory.
        Defaults to ``data/external/reference_packs/`` under the workspace root.

    Returns
    -------
    ReferencePackManifest
        The manifest written (or loaded from cache) for the assembled pack.
    """
    slug = _normalize_system_slug(system_slug)

    # -- Cache reuse ----------------------------------------------------------
    if pack_config.reuse_cached_pack and _cached_pack_is_complete(slug, pack_config.pack_id, pack_root):
        cached = load_cached_pack_manifest(slug, pack_config.pack_id, pack_root)
        if cached is not None:
            return cached

    # -- Load per-member records ----------------------------------------------
    all_tagged: list[tuple[str, CanonicalRawSourceRecord]] = []
    member_results: list[ReferencePackMemberResult] = []

    for member in pack_config.members:
        records, canonical_path_str, manifest_path_str = _load_member_records(
            member, artifact_root
        )
        priority_rank = _source_priority(member.source_key, pack_config.priority_order)
        member_results.append(
            ReferencePackMemberResult(
                source_key=member.source_key,
                snapshot_id=member.snapshot_id,
                canonical_records_path=canonical_path_str,
                snapshot_manifest_path=manifest_path_str,
                canonical_record_count=len(records),
                priority_rank=priority_rank,
            )
        )
        all_tagged.extend((member.source_key, record) for record in records)

    # -- Deduplicate -----------------------------------------------------------
    deduped, overlap_count = _merge_records(all_tagged, pack_config.priority_order)
    total_input = sum(m.canonical_record_count for m in member_results)
    duplicate_dropped = total_input - len(deduped)

    # -- Write output ----------------------------------------------------------
    pack_dir = reference_pack_dir(slug, pack_config.pack_id, pack_root)
    pack_dir.mkdir(parents=True, exist_ok=True)

    canonical_out_path = reference_pack_canonical_records_path(slug, pack_config.pack_id, pack_root)
    write_jsonl(
        [record.model_dump(mode="json") for record in deduped],
        canonical_out_path,
    )

    # -- Build manifest -------------------------------------------------------
    fingerprint = _pack_fingerprint(member_results)
    manifest = ReferencePackManifest(
        pack_id=pack_config.pack_id,
        system_slug=slug,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        pack_fingerprint=fingerprint,
        members=member_results,
        priority_order=pack_config.priority_order or _DEFAULT_PRIORITY_ORDER,
        total_canonical_records=len(deduped),
        duplicate_dropped_count=duplicate_dropped,
        overlap_count=overlap_count,
        canonical_records_path=workspace_relative(canonical_out_path),
    )

    manifest_path = reference_pack_manifest_path(slug, pack_config.pack_id, pack_root)
    write_json_object(manifest.model_dump(mode="json"), manifest_path)

    return manifest


def assemble_reference_pack_from_config(
    config: SystemConfig,
    system_slug: str | None = None,
    pack_root: str | None = None,
) -> ReferencePackManifest:
    """Convenience wrapper that extracts the reference-pack block from a
    ``SystemConfig`` and delegates to :func:`assemble_reference_pack`.

    Parameters
    ----------
    config:
        The system config.  Must have ``ingestion.reference_pack`` set.
    system_slug:
        Optional override for the system slug.  Defaults to the normalised
        ``config.system_name``.
    pack_root:
        Optional override for the reference-pack output root directory.
        Defaults to ``data/external/reference_packs/`` under the workspace root.
    """
    if config.ingestion is None or config.ingestion.reference_pack is None:
        raise ValueError(
            "assemble_reference_pack_from_config requires ingestion.reference_pack to be set "
            f"in the system config for '{config.system_name}'"
        )
    slug = system_slug or _normalize_system_slug(config.system_name)
    artifact_root = config.ingestion.artifact_root if config.ingestion else None
    return assemble_reference_pack(config.ingestion.reference_pack, slug, artifact_root, pack_root)
