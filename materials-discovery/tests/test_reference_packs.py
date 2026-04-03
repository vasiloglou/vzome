"""Tests for the Phase 4 reference-pack assembly and reuse layer.

All tests are offline and deterministic.  They use thin local canonical-record
fixtures rather than live network access.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from materials_discovery.common.schema import (
    ReferencePackConfig,
    ReferencePackMemberConfig,
    SystemConfig,
)
from materials_discovery.data_sources.reference_packs import (
    assemble_reference_pack,
    assemble_reference_pack_from_config,
    load_cached_pack_manifest,
)
from materials_discovery.data_sources.schema import (
    ReferencePackManifest,
)
from materials_discovery.data_sources.storage import (
    reference_pack_canonical_records_path,
    reference_pack_manifest_path,
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _make_canonical_record(
    source_key: str,
    snapshot_id: str,
    record_idx: int,
    system: str = "Al-Cu-Fe",
    composition: dict[str, float] | None = None,
    phase_name: str | None = None,
) -> dict[str, Any]:
    """Return a minimal CanonicalRawSourceRecord dict suitable for staging."""
    if composition is None:
        composition = {"Al": 0.7, "Cu": 0.2, "Fe": 0.1}
    if phase_name is None:
        phase_name = f"phase_{record_idx}"

    stable_source_key = source_key.strip().lower().replace("-", "_")
    source_record_id = f"{system.lower()}|{phase_name}|{record_idx}"
    payload = f"{stable_source_key}|{snapshot_id}|{source_record_id}".encode("utf-8")
    local_id = f"src_{stable_source_key}_{hashlib.sha256(payload).hexdigest()[:16]}"

    return {
        "schema_version": "raw-source-record/v1",
        "local_record_id": local_id,
        "record_kind": "material_entry",
        "source": {
            "source_key": source_key,
            "source_name": source_key.upper(),
            "source_record_id": source_record_id,
            "source_record_url": None,
            "source_namespace": None,
            "record_title": phase_name,
        },
        "access": {
            "access_level": "open",
            "auth_required": False,
            "access_surface": "api",
            "terms_url": None,
            "redistribution_posture": "allowed",
        },
        "license": {
            "license_expression": "CC-BY-4.0",
            "license_url": None,
            "license_category": "open",
            "attribution_required": True,
            "commercial_use_allowed": True,
            "notes": None,
        },
        "snapshot": {
            "snapshot_id": snapshot_id,
            "source_version": None,
            "source_release_date": None,
            "retrieved_at_utc": "2026-01-01T00:00:00Z",
            "retrieval_mode": "fixture",
            "snapshot_manifest_path": f"data/external/sources/{source_key}/{snapshot_id}/snapshot_manifest.json",
        },
        "raw_payload": {
            "payload_path": f"data/external/sources/{source_key}/{snapshot_id}/raw_rows.jsonl",
            "payload_format": "jsonl",
            "payload_encoding": None,
            "content_hash": hashlib.sha256(b"dummy").hexdigest(),
            "raw_excerpt": None,
        },
        "common": {
            "chemical_system": system,
            "elements": sorted(composition.keys()),
            "formula_raw": None,
            "formula_reduced": None,
            "composition": composition,
            "structure_representations": [],
            "space_group": None,
            "dimension_class": None,
            "reported_properties": {"phase_name": phase_name},
            "citations": [],
            "keywords": [],
        },
        "qa": {
            "schema_valid": True,
            "required_field_gaps": [],
            "normalization_warnings": [],
            "duplicate_keys": [],
            "structure_status": "missing",
            "composition_status": "valid",
            "schema_drift_flags": [],
            "needs_manual_review": False,
        },
        "lineage": {
            "adapter_key": f"{source_key}_fixture_v1",
            "adapter_family": "direct",
            "adapter_version": "0.1.0",
            "fetch_manifest_id": f"{source_key}_{snapshot_id}_fetch",
            "normalize_manifest_id": f"{source_key}_{snapshot_id}_normalize",
            "parent_snapshot_ids": [],
            "projection_status": None,
        },
        "source_metadata": {},
    }


def _write_canonical_records(
    path: Path,
    source_key: str,
    snapshot_id: str,
    count: int = 2,
    system: str = "Al-Cu-Fe",
) -> None:
    """Write *count* minimal canonical records to *path* as JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        _make_canonical_record(source_key, snapshot_id, i, system=system)
        for i in range(count)
    ]
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


# ---------------------------------------------------------------------------
# Tests: ReferencePackConfig schema
# ---------------------------------------------------------------------------


def test_reference_pack_config_validates() -> None:
    cfg = ReferencePackConfig(
        pack_id="test_pack",
        members=[
            ReferencePackMemberConfig(source_key="hypodx", snapshot_id="snap_v1"),
            ReferencePackMemberConfig(source_key="cod", snapshot_id="cod_snap_v1"),
        ],
        reuse_cached_pack=True,
        priority_order=["hypodx", "cod"],
    )
    assert cfg.pack_id == "test_pack"
    assert len(cfg.members) == 2
    assert cfg.priority_order == ["hypodx", "cod"]


def test_reference_pack_config_rejects_duplicate_members() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        ReferencePackConfig(
            pack_id="dup_pack",
            members=[
                ReferencePackMemberConfig(source_key="hypodx", snapshot_id="snap_v1"),
                ReferencePackMemberConfig(source_key="hypodx", snapshot_id="snap_v1"),
            ],
        )


def test_reference_pack_config_rejects_empty_members() -> None:
    with pytest.raises(ValueError, match="members"):
        ReferencePackConfig(pack_id="empty", members=[])


# ---------------------------------------------------------------------------
# Tests: assemble_reference_pack
# ---------------------------------------------------------------------------


def test_assemble_single_source_pack(tmp_path: Path) -> None:
    """Pack with a single source merges correctly and writes manifest."""
    canonical_path = tmp_path / "sources" / "hypodx" / "snap_v1" / "canonical_records.jsonl"
    _write_canonical_records(canonical_path, "hypodx", "snap_v1", count=3)
    pack_root = str(tmp_path / "packs")

    pack_config = ReferencePackConfig(
        pack_id="alcufe_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="hypodx",
                snapshot_id="snap_v1",
                staged_canonical_path=str(canonical_path),
            ),
        ],
        reuse_cached_pack=False,
    )

    manifest = assemble_reference_pack(
        pack_config,
        system_slug="al_cu_fe",
        pack_root=pack_root,
    )

    assert isinstance(manifest, ReferencePackManifest)
    assert manifest.pack_id == "alcufe_v1"
    assert manifest.system_slug == "al_cu_fe"
    assert manifest.total_canonical_records == 3
    assert manifest.duplicate_dropped_count == 0
    assert manifest.overlap_count == 0
    assert len(manifest.members) == 1
    assert manifest.members[0].source_key == "hypodx"
    assert manifest.members[0].canonical_record_count == 3
    assert manifest.pack_fingerprint  # non-empty string


def test_assemble_multi_source_pack_deduplicates(tmp_path: Path) -> None:
    """Multi-source pack: shared record kept from higher-priority source."""
    pack_root = str(tmp_path / "packs")

    # Source 1: hypodx (higher priority) — 2 records, 1 shared
    hypodx_path = tmp_path / "sources" / "hypodx" / "snap_v1" / "canonical_records.jsonl"
    hypodx_path.parent.mkdir(parents=True, exist_ok=True)
    rec_unique = _make_canonical_record("hypodx", "snap_v1", 0)
    rec_shared_hypodx = _make_canonical_record("hypodx", "snap_v1", 99, phase_name="shared_phase")
    with hypodx_path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(rec_unique, sort_keys=True) + "\n")
        fh.write(json.dumps(rec_shared_hypodx, sort_keys=True) + "\n")

    # Source 2: cod (lower priority) — 2 records, 1 shared
    cod_path = tmp_path / "sources" / "cod" / "cod_snap_v1" / "canonical_records.jsonl"
    cod_path.parent.mkdir(parents=True, exist_ok=True)
    rec_unique_cod = _make_canonical_record("cod", "cod_snap_v1", 1)
    rec_shared_cod = _make_canonical_record("cod", "cod_snap_v1", 99, phase_name="shared_phase")
    with cod_path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(rec_unique_cod, sort_keys=True) + "\n")
        fh.write(json.dumps(rec_shared_cod, sort_keys=True) + "\n")

    pack_config = ReferencePackConfig(
        pack_id="multi_source_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="hypodx",
                snapshot_id="snap_v1",
                staged_canonical_path=str(hypodx_path),
            ),
            ReferencePackMemberConfig(
                source_key="cod",
                snapshot_id="cod_snap_v1",
                staged_canonical_path=str(cod_path),
            ),
        ],
        reuse_cached_pack=False,
        priority_order=["hypodx", "cod"],
    )

    manifest = assemble_reference_pack(
        pack_config,
        system_slug="al_cu_fe",
        pack_root=pack_root,
    )

    # 2 + 2 = 4 total input records, 1 duplicate dropped, 3 unique
    assert manifest.total_canonical_records == 3
    assert manifest.duplicate_dropped_count == 1
    assert manifest.overlap_count == 1
    assert len(manifest.members) == 2

    # Confirm canonical records file exists and has correct count
    canonical_out = reference_pack_canonical_records_path("al_cu_fe", "multi_source_v1", pack_root)
    assert canonical_out.exists()
    rows = [json.loads(line) for line in canonical_out.read_text().splitlines() if line.strip()]
    assert len(rows) == 3


def test_assemble_pack_writes_manifest_file(tmp_path: Path) -> None:
    """Pack manifest JSON is written to disk with all required fields."""
    canonical_path = tmp_path / "sources" / "hypodx" / "snap_v1" / "canonical_records.jsonl"
    _write_canonical_records(canonical_path, "hypodx", "snap_v1", count=2)
    pack_root = str(tmp_path / "packs")

    pack_config = ReferencePackConfig(
        pack_id="manifest_check_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="hypodx",
                snapshot_id="snap_v1",
                staged_canonical_path=str(canonical_path),
            ),
        ],
        reuse_cached_pack=False,
    )
    assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)

    manifest_path = reference_pack_manifest_path("al_cu_fe", "manifest_check_v1", pack_root)
    assert manifest_path.exists()
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert raw["schema_version"] == "reference-pack-manifest/v1"
    assert raw["pack_id"] == "manifest_check_v1"
    assert raw["system_slug"] == "al_cu_fe"
    assert "pack_fingerprint" in raw
    assert "created_at_utc" in raw
    assert "members" in raw
    assert "priority_order" in raw
    assert "total_canonical_records" in raw
    assert "duplicate_dropped_count" in raw
    assert "overlap_count" in raw
    assert "canonical_records_path" in raw


def test_assemble_pack_records_member_lineage(tmp_path: Path) -> None:
    """Manifest members record source_key, snapshot_id, path, and count."""
    canonical_path = tmp_path / "sources" / "cod" / "cod_snap_v1" / "canonical_records.jsonl"
    _write_canonical_records(canonical_path, "cod", "cod_snap_v1", count=4)
    pack_root = str(tmp_path / "packs")

    pack_config = ReferencePackConfig(
        pack_id="lineage_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="cod",
                snapshot_id="cod_snap_v1",
                staged_canonical_path=str(canonical_path),
            ),
        ],
        reuse_cached_pack=False,
    )
    manifest = assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)

    member = manifest.members[0]
    assert member.source_key == "cod"
    assert member.snapshot_id == "cod_snap_v1"
    assert member.canonical_record_count == 4
    assert "cod_snap_v1" in member.canonical_records_path or "cod" in member.canonical_records_path


def test_assemble_pack_reuses_cached_when_enabled(tmp_path: Path) -> None:
    """Second assembly with reuse_cached_pack=True skips re-reading snapshots."""
    canonical_path = tmp_path / "sources" / "hypodx" / "snap_v1" / "canonical_records.jsonl"
    _write_canonical_records(canonical_path, "hypodx", "snap_v1", count=2)
    pack_root = str(tmp_path / "packs")

    pack_config = ReferencePackConfig(
        pack_id="cache_reuse_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="hypodx",
                snapshot_id="snap_v1",
                staged_canonical_path=str(canonical_path),
            ),
        ],
        reuse_cached_pack=True,
    )

    # First call assembles and writes to disk
    first = assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)
    assert first.total_canonical_records == 2

    # Delete the source fixture to prove the second call uses the cache
    canonical_path.unlink()

    second = assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)
    assert second.pack_id == first.pack_id
    assert second.total_canonical_records == first.total_canonical_records
    assert second.pack_fingerprint == first.pack_fingerprint


def test_assemble_pack_skips_cache_when_disabled(tmp_path: Path) -> None:
    """With reuse_cached_pack=False, pack is always re-assembled."""
    canonical_path = tmp_path / "sources" / "hypodx" / "snap_v1" / "canonical_records.jsonl"
    _write_canonical_records(canonical_path, "hypodx", "snap_v1", count=2)
    pack_root = str(tmp_path / "packs")

    pack_config = ReferencePackConfig(
        pack_id="no_cache_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="hypodx",
                snapshot_id="snap_v1",
                staged_canonical_path=str(canonical_path),
            ),
        ],
        reuse_cached_pack=False,
    )

    assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)

    # Overwrite the source file to change the data
    _write_canonical_records(canonical_path, "hypodx", "snap_v1", count=5)

    second = assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)
    # The pack was re-assembled, so it reflects the updated source
    assert second.total_canonical_records == 5


def test_assemble_pack_missing_source_raises(tmp_path: Path) -> None:
    """FileNotFoundError is raised when a member's staged path does not exist."""
    pack_root = str(tmp_path / "packs")
    pack_config = ReferencePackConfig(
        pack_id="missing_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="hypodx",
                snapshot_id="snap_v1",
                staged_canonical_path=str(tmp_path / "nonexistent.jsonl"),
            ),
        ],
        reuse_cached_pack=False,
    )
    with pytest.raises(FileNotFoundError):
        assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)


def test_pack_fingerprint_is_deterministic(tmp_path: Path) -> None:
    """Assembling the same pack twice yields the same fingerprint."""
    canonical_path = tmp_path / "sources" / "hypodx" / "snap_v1" / "canonical_records.jsonl"
    _write_canonical_records(canonical_path, "hypodx", "snap_v1", count=2)
    pack_root = str(tmp_path / "packs")

    pack_config = ReferencePackConfig(
        pack_id="fingerprint_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="hypodx",
                snapshot_id="snap_v1",
                staged_canonical_path=str(canonical_path),
            ),
        ],
        reuse_cached_pack=False,
    )

    first = assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)
    second = assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)
    assert first.pack_fingerprint == second.pack_fingerprint


def test_load_cached_pack_manifest_returns_none_when_missing() -> None:
    """Returns None when no complete pack is cached."""
    result = load_cached_pack_manifest("al_cu_fe", "nonexistent_pack_xyz_abc_123")
    assert result is None


def test_assemble_reference_pack_from_config(tmp_path: Path) -> None:
    """Convenience wrapper extracts config and delegates correctly."""
    from materials_discovery.common.io import load_yaml
    workspace = Path(__file__).resolve().parents[1]
    base_data = load_yaml(workspace / "configs" / "systems" / "al_cu_fe.yaml")

    canonical_path = tmp_path / "sources" / "hypodx" / "snap_v1" / "canonical_records.jsonl"
    _write_canonical_records(canonical_path, "hypodx", "snap_v1", count=2)
    pack_root = str(tmp_path / "packs")

    base_data["ingestion"] = {
        "source_key": "",
        "reference_pack": {
            "pack_id": "fromconfig_v1",
            "members": [
                {
                    "source_key": "hypodx",
                    "snapshot_id": "snap_v1",
                    "staged_canonical_path": str(canonical_path),
                }
            ],
            "reuse_cached_pack": False,
        },
    }

    config = SystemConfig.model_validate(base_data)
    manifest = assemble_reference_pack_from_config(
        config, system_slug="al_cu_fe", pack_root=pack_root
    )
    assert manifest.pack_id == "fromconfig_v1"
    assert manifest.total_canonical_records == 2


def test_assemble_reference_pack_from_config_raises_without_pack() -> None:
    """Raises ValueError when no reference_pack block is configured."""
    from materials_discovery.common.io import load_yaml
    workspace = Path(__file__).resolve().parents[1]
    config = SystemConfig.model_validate(load_yaml(workspace / "configs" / "systems" / "al_cu_fe_real.yaml"))

    with pytest.raises(ValueError, match="ingestion.reference_pack"):
        assemble_reference_pack_from_config(config, system_slug="al_cu_fe")


# ---------------------------------------------------------------------------
# Tests: priority ordering
# ---------------------------------------------------------------------------


def test_priority_order_explicit_overrides_default(tmp_path: Path) -> None:
    """When priority_order lists cod before hypodx, cod record wins dedup."""
    pack_root = str(tmp_path / "packs")

    # Build two sources with the same shared record
    for source_key, snap_id in [("hypodx", "snap_v1"), ("cod", "cod_snap_v1")]:
        path = tmp_path / "sources" / source_key / snap_id / "canonical_records.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        rec = _make_canonical_record(source_key, snap_id, 0, phase_name="shared")
        with path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")

    pack_config = ReferencePackConfig(
        pack_id="priority_test_v1",
        members=[
            ReferencePackMemberConfig(
                source_key="hypodx",
                snapshot_id="snap_v1",
                staged_canonical_path=str(
                    tmp_path / "sources" / "hypodx" / "snap_v1" / "canonical_records.jsonl"
                ),
            ),
            ReferencePackMemberConfig(
                source_key="cod",
                snapshot_id="cod_snap_v1",
                staged_canonical_path=str(
                    tmp_path / "sources" / "cod" / "cod_snap_v1" / "canonical_records.jsonl"
                ),
            ),
        ],
        reuse_cached_pack=False,
        priority_order=["cod", "hypodx"],  # cod wins
    )

    manifest = assemble_reference_pack(pack_config, system_slug="al_cu_fe", pack_root=pack_root)
    # Both records share the same dedup key — only 1 survives
    assert manifest.total_canonical_records == 1
    assert manifest.overlap_count == 1
    assert manifest.duplicate_dropped_count == 1
