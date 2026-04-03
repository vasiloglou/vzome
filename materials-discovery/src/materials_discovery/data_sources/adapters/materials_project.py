from __future__ import annotations

import hashlib
import json
import os
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

MP_API_KEY_ENV = "MP_API_KEY"


def _require_httpx() -> Any:
    if httpx is None:
        raise RuntimeError(
            "Materials Project source adapter requires optional dependency 'httpx'; install with "
            "`uv sync --extra dev --extra ingestion`"
        )
    return httpx


def _row_hash(row: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True).encode("utf-8")).hexdigest()


def _ingestion_query(config: SystemConfig) -> dict[str, Any]:
    ingestion = getattr(config, "ingestion", None)
    query = getattr(ingestion, "query", {}) if ingestion is not None else {}
    return query if isinstance(query, dict) else {}


def _load_rows(snapshot_path: Path | None, query: dict[str, Any]) -> list[dict[str, Any]]:
    if snapshot_path is not None:
        parsed = json.loads(snapshot_path.read_text(encoding="utf-8"))
        if isinstance(parsed, list):
            return [row for row in parsed if isinstance(row, dict)]
        if isinstance(parsed, dict):
            data = parsed.get("data")
            if isinstance(data, list):
                return [row for row in data if isinstance(row, dict)]
        raise ValueError("Materials Project snapshot must be a JSON array or an object with data")

    inline_rows = query.get("inline_rows")
    if isinstance(inline_rows, list):
        return [row for row in inline_rows if isinstance(row, dict)]

    api_key = str(query.get("api_key") or os.getenv(MP_API_KEY_ENV) or "").strip()
    if not api_key:
        raise RuntimeError(f"Materials Project adapter requires {MP_API_KEY_ENV} or ingestion.query.api_key")

    client_module = _require_httpx()
    params = query.get("params") if isinstance(query.get("params"), dict) else {}
    headers = {"X-API-KEY": api_key}
    endpoint = str(query.get("endpoint") or "https://api.materialsproject.org/materials/summary")
    with client_module.Client(timeout=30.0, headers=headers) as client:
        response = client.get(endpoint, params=params)
        response.raise_for_status()
        payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Materials Project response must be a JSON object")
    data = payload.get("data")
    if not isinstance(data, list):
        raise ValueError("Materials Project response must include a data list")
    return [row for row in data if isinstance(row, dict)]


@dataclass(frozen=True)
class MaterialsProjectSourceAdapter(SourceAdapter):
    def info(self) -> SourceAdapterInfo:
        return SourceAdapterInfo(
            adapter_key="direct_api_v1",
            source_key="materials_project",
            adapter_family="direct",
            version="2026.04",
            description="Materials Project direct API source adapter",
        )

    def default_snapshot_id(self, config: SystemConfig) -> str:
        return "materials_project_snapshot_v1"

    def load_rows(
        self,
        config: SystemConfig,
        snapshot_path: Path | None,
    ) -> list[dict[str, Any]]:
        return _load_rows(snapshot_path, _ingestion_query(config))

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
            material_id = str(raw_row.get("material_id") or raw_row.get("task_id") or "mp-record")
            structure = raw_row.get("structure")
            structure_repr = None
            if isinstance(structure, dict):
                structure_repr = StructureRepresentation(
                    representation_kind="materials_project_structure",
                    payload_format="materials-project-json",
                    content_hash=_row_hash(structure),
                    structure_summary=structure,
                )

            composition = raw_row.get("composition_reduced")
            composition_map = (
                {str(key): float(value) for key, value in composition.items()}
                if isinstance(composition, dict)
                else None
            )
            formula = raw_row.get("formula_pretty") if isinstance(raw_row.get("formula_pretty"), str) else None
            records.append(
                CanonicalRawSourceRecord(
                    local_record_id=derive_local_record_id("materials_project", snapshot_id, material_id),
                    record_kind="structure" if structure_repr is not None else "material_entry",
                    source=SourceIdentity(
                        source_key="materials_project",
                        source_name="Materials Project",
                        source_record_id=material_id,
                        source_record_url=f"https://materialsproject.org/materials/{material_id}",
                        record_title=formula,
                    ),
                    access=AccessInfo(
                        access_level="open",
                        auth_required=True,
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
                        chemical_system=raw_row.get("chemsys"),
                        elements=sorted(composition_map) if composition_map else [],
                        formula_raw=formula,
                        formula_reduced=formula,
                        composition=composition_map,
                        structure_representations=[structure_repr] if structure_repr is not None else [],
                        space_group=(
                            raw_row.get("symmetry", {}).get("symbol")
                            if isinstance(raw_row.get("symmetry"), dict)
                            else None
                        ),
                        reported_properties={"energy_above_hull": raw_row.get("energy_above_hull")},
                    ),
                    lineage=LineageInfo(
                        adapter_key=adapter_info.adapter_key,
                        adapter_family=adapter_info.adapter_family,
                        adapter_version=adapter_info.version,
                        fetch_manifest_id=f"materials_project:{adapter_info.adapter_key}:fetch:{snapshot_id}",
                        normalize_manifest_id=f"materials_project:{adapter_info.adapter_key}:normalize:{snapshot_id}",
                    ),
                    source_metadata={"raw_keys": sorted(raw_row)},
                )
            )
        return records


def build_materials_project_source_adapters() -> list[SourceAdapter]:
    return [MaterialsProjectSourceAdapter()]
