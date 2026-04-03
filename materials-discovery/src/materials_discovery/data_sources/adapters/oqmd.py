from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover - exercised only when the optional dep is absent
    httpx = None

from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.schema import (
    CanonicalCommonFields,
    CanonicalRawSourceRecord,
    LineageInfo,
    RawPayloadInfo,
    SnapshotInfo,
    SourceIdentity,
    AccessInfo,
    LicenseInfo,
    StructureRepresentation,
    derive_local_record_id,
)
from materials_discovery.data_sources.storage import workspace_relative
from materials_discovery.data_sources.types import SourceAdapter, SourceAdapterInfo


def _require_httpx() -> Any:
    if httpx is None:
        raise RuntimeError(
            "OQMD source adapter requires optional dependency 'httpx'; install with "
            "`uv sync --extra dev --extra ingestion`"
        )
    return httpx


def _row_hash(row: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True).encode("utf-8")).hexdigest()


def _ingestion_query(config: SystemConfig) -> dict[str, Any]:
    ingestion = getattr(config, "ingestion", None)
    query = getattr(ingestion, "query", {}) if ingestion is not None else {}
    return query if isinstance(query, dict) else {}


@dataclass(frozen=True)
class OqmdSourceAdapter(SourceAdapter):
    def info(self) -> SourceAdapterInfo:
        return SourceAdapterInfo(
            adapter_key="direct_api_v1",
            source_key="oqmd",
            adapter_family="direct",
            version="2026.04",
            description="OQMD direct API source adapter",
        )

    def default_snapshot_id(self, config: SystemConfig) -> str:
        return "oqmd_snapshot_v1"

    def load_rows(
        self,
        config: SystemConfig,
        snapshot_path: Path | None,
    ) -> list[dict[str, Any]]:
        query = _ingestion_query(config)
        if snapshot_path is not None:
            parsed = json.loads(snapshot_path.read_text(encoding="utf-8"))
            if isinstance(parsed, list):
                return [row for row in parsed if isinstance(row, dict)]
            raise ValueError("OQMD snapshot must be a JSON array")

        inline_rows = query.get("inline_rows")
        if isinstance(inline_rows, list):
            return [row for row in inline_rows if isinstance(row, dict)]

        client_module = _require_httpx()
        params = query.get("params") if isinstance(query.get("params"), dict) else {}
        endpoint = str(query.get("endpoint") or "https://oqmd.org/oqmdapi/formationenergy")
        with client_module.Client(timeout=30.0) as client:
            response = client.get(endpoint, params=params)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("OQMD response must be a JSON object")
        data = payload.get("data")
        if not isinstance(data, list):
            raise ValueError("OQMD response must include a data list")
        return [row for row in data if isinstance(row, dict)]

    def canonicalize_rows(
        self,
        config: SystemConfig,
        raw_rows: list[dict[str, Any]],
        snapshot_id: str,
        raw_payload_path: Path,
    ) -> list[CanonicalRawSourceRecord]:
        adapter_info = self.info()
        records: list[CanonicalRawSourceRecord] = []
        for raw_row in raw_rows:
            entry_id = str(raw_row.get("entry_id") or raw_row.get("id") or "oqmd-entry")
            structure = raw_row.get("structure")
            structure_repr = None
            if isinstance(structure, dict):
                structure_repr = StructureRepresentation(
                    representation_kind="oqmd_structure",
                    payload_format="oqmd-json",
                    content_hash=_row_hash(structure),
                    structure_summary=structure,
                )

            composition = raw_row.get("composition")
            composition_map = (
                {str(key): float(value) for key, value in composition.items()}
                if isinstance(composition, dict)
                else None
            )
            formula = raw_row.get("name") if isinstance(raw_row.get("name"), str) else None
            records.append(
                CanonicalRawSourceRecord(
                    local_record_id=derive_local_record_id("oqmd", snapshot_id, entry_id),
                    record_kind="structure" if structure_repr is not None else "material_entry",
                    source=SourceIdentity(
                        source_key="oqmd",
                        source_name="OQMD",
                        source_record_id=entry_id,
                        record_title=formula,
                    ),
                    access=AccessInfo(
                        access_level="open",
                        auth_required=False,
                        access_surface="api",
                        redistribution_posture="unknown",
                    ),
                    license=LicenseInfo(
                        license_expression="provider-specific",
                        license_category="custom",
                        attribution_required=True,
                    ),
                    snapshot=SnapshotInfo(
                        snapshot_id=snapshot_id,
                        source_version=adapter_info.version,
                        source_release_date=None,
                        retrieved_at_utc="2026-04-03T00:00:00Z",
                        retrieval_mode="api",
                        snapshot_manifest_path="",
                    ),
                    raw_payload=RawPayloadInfo(
                        payload_path=workspace_relative(raw_payload_path),
                        payload_format="jsonl",
                        content_hash=_row_hash(raw_row),
                    ),
                    common=CanonicalCommonFields(
                        chemical_system=raw_row.get("composition_string"),
                        elements=sorted(composition_map) if composition_map else [],
                        formula_raw=formula,
                        formula_reduced=formula,
                        composition=composition_map,
                        structure_representations=[structure_repr] if structure_repr is not None else [],
                        reported_properties={"delta_e": raw_row.get("delta_e")},
                    ),
                    lineage=LineageInfo(
                        adapter_key=adapter_info.adapter_key,
                        adapter_family=adapter_info.adapter_family,
                        adapter_version=adapter_info.version,
                        fetch_manifest_id=f"oqmd:{adapter_info.adapter_key}:fetch:{snapshot_id}",
                        normalize_manifest_id=f"oqmd:{adapter_info.adapter_key}:normalize:{snapshot_id}",
                    ),
                    source_metadata={"raw_keys": sorted(raw_row)},
                )
            )
        return records


def build_oqmd_source_adapters() -> list[SourceAdapter]:
    return [OqmdSourceAdapter()]
