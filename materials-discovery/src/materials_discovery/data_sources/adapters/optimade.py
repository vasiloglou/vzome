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
            "OPTIMADE source adapters require optional dependency 'httpx'; install with "
            "`uv sync --extra dev --extra ingestion`"
        )
    return httpx


def _ingestion_query(config: SystemConfig) -> dict[str, Any]:
    ingestion = getattr(config, "ingestion", None)
    query = getattr(ingestion, "query", {}) if ingestion is not None else {}
    return query if isinstance(query, dict) else {}


def _load_json_payload(path: Path) -> list[dict[str, Any]]:
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(parsed, list):
        return [row for row in parsed if isinstance(row, dict)]
    if isinstance(parsed, dict):
        data = parsed.get("data")
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]
    raise ValueError(f"OPTIMADE payload must be a JSON array or an object with a data array: {path}")


def _row_hash(row: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True).encode("utf-8")).hexdigest()


def _composition_from_optimade(attributes: dict[str, Any]) -> dict[str, float] | None:
    elements = attributes.get("elements")
    ratios = attributes.get("elements_ratios")
    if isinstance(elements, list) and isinstance(ratios, list) and len(elements) == len(ratios):
        composition: dict[str, float] = {}
        for element, ratio in zip(elements, ratios, strict=True):
            if isinstance(element, str) and isinstance(ratio, int | float):
                composition[element] = float(ratio)
        return composition or None
    return None


def _formula(attributes: dict[str, Any], composition: dict[str, float] | None) -> str | None:
    reduced = attributes.get("chemical_formula_reduced")
    if isinstance(reduced, str) and reduced:
        return reduced
    if composition:
        return "".join(
            f"{element}{round(amount, 6):g}" for element, amount in sorted(composition.items())
        )
    return None


def _structure_representation(attributes: dict[str, Any]) -> StructureRepresentation | None:
    lattice_vectors = attributes.get("lattice_vectors")
    cartesian_site_positions = attributes.get("cartesian_site_positions")
    species_at_sites = attributes.get("species_at_sites")
    nsites = attributes.get("nsites")

    has_structure = any(
        value is not None
        for value in (lattice_vectors, cartesian_site_positions, species_at_sites, nsites)
    )
    if not has_structure:
        return None

    summary: dict[str, Any] = {}
    if lattice_vectors is not None:
        summary["lattice_vectors"] = lattice_vectors
    if cartesian_site_positions is not None:
        summary["cartesian_site_positions"] = cartesian_site_positions
    if species_at_sites is not None:
        summary["species_at_sites"] = species_at_sites
    if nsites is not None:
        summary["nsites"] = nsites

    return StructureRepresentation(
        representation_kind="optimade_structure",
        payload_format="optimade-json",
        content_hash=_row_hash(attributes),
        structure_summary=summary,
    )


@dataclass(frozen=True)
class OptimadeSourceAdapter(SourceAdapter):
    source_key: str
    base_url: str | None
    adapter_key: str = "optimade_v1"
    version: str = "optimade.v1"
    source_name: str | None = None
    default_snapshot: str = "optimade_snapshot_v1"
    description: str = ""

    def info(self) -> SourceAdapterInfo:
        return SourceAdapterInfo(
            adapter_key=self.adapter_key,
            source_key=self.source_key,
            adapter_family="optimade",
            version=self.version,
            description=self.description or f"{self.source_key} OPTIMADE adapter",
        )

    def default_snapshot_id(self, config: SystemConfig) -> str:
        return self.default_snapshot

    def load_rows(
        self,
        config: SystemConfig,
        snapshot_path: Path | None,
    ) -> list[dict[str, Any]]:
        query = _ingestion_query(config)
        if snapshot_path is not None:
            return _load_json_payload(snapshot_path)

        inline_response = query.get("inline_response")
        if isinstance(inline_response, list):
            return [row for row in inline_response if isinstance(row, dict)]
        if isinstance(inline_response, dict):
            data = inline_response.get("data")
            if isinstance(data, list):
                return [row for row in data if isinstance(row, dict)]

        if self.base_url is None:
            raise ValueError(
                f"{self.source_key} OPTIMADE adapter requires a snapshot path, inline response, or base_url"
            )

        client_module = _require_httpx()
        params = query.get("params") if isinstance(query.get("params"), dict) else None
        with client_module.Client(timeout=30.0) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("OPTIMADE response must be a JSON object")
        data = payload.get("data")
        if not isinstance(data, list):
            raise ValueError("OPTIMADE response must include a data list")
        return [row for row in data if isinstance(row, dict)]

    def canonicalize_rows(
        self,
        config: SystemConfig,
        raw_rows: list[dict[str, Any]],
        snapshot_id: str,
        raw_payload_path: Path,
    ) -> list[CanonicalRawSourceRecord]:
        adapter_info = self.info()
        canonical_records: list[CanonicalRawSourceRecord] = []
        for raw_row in raw_rows:
            source_record_id = str(raw_row.get("id") or raw_row.get("entry_id") or "optimade-record")
            attributes = raw_row.get("attributes")
            attribute_map = attributes if isinstance(attributes, dict) else {}
            composition = _composition_from_optimade(attribute_map)
            formula = _formula(attribute_map, composition)
            structure_repr = _structure_representation(attribute_map)
            structure_representations = [structure_repr] if structure_repr is not None else []
            record_kind = "structure" if structure_representations else "material_entry"
            source_name = self.source_name or self.source_key.replace("_", " ").title()

            canonical_records.append(
                CanonicalRawSourceRecord(
                    local_record_id=derive_local_record_id(self.source_key, snapshot_id, source_record_id),
                    record_kind=record_kind,
                    source=SourceIdentity(
                        source_key=self.source_key,
                        source_name=source_name,
                        source_record_id=source_record_id,
                        record_title=formula,
                    ),
                    access=AccessInfo(
                        access_level="open",
                        auth_required=False,
                        access_surface="optimade",
                        redistribution_posture="unknown",
                    ),
                    license=LicenseInfo(
                        license_expression="provider-specific",
                        license_category="custom",
                        attribution_required=True,
                    ),
                    snapshot=SnapshotInfo(
                        snapshot_id=snapshot_id,
                        source_version=self.version,
                        source_release_date=None,
                        retrieved_at_utc="2026-04-03T00:00:00Z",
                        retrieval_mode="optimade",
                        snapshot_manifest_path="",
                    ),
                    raw_payload=RawPayloadInfo(
                        payload_path=workspace_relative(raw_payload_path),
                        payload_format="jsonl",
                        content_hash=_row_hash(raw_row),
                    ),
                    common=CanonicalCommonFields(
                        chemical_system=attribute_map.get("chemical_system"),
                        elements=attribute_map.get("elements") if isinstance(attribute_map.get("elements"), list) else [],
                        formula_raw=formula,
                        formula_reduced=formula,
                        composition=composition,
                        structure_representations=structure_representations,
                        reported_properties={
                            "nsites": attribute_map.get("nsites"),
                            "nelements": attribute_map.get("nelements"),
                        },
                    ),
                    lineage=LineageInfo(
                        adapter_key=adapter_info.adapter_key,
                        adapter_family=adapter_info.adapter_family,
                        adapter_version=adapter_info.version,
                        fetch_manifest_id=f"{self.source_key}:{adapter_info.adapter_key}:fetch:{snapshot_id}",
                        normalize_manifest_id=f"{self.source_key}:{adapter_info.adapter_key}:normalize:{snapshot_id}",
                    ),
                    source_metadata={
                        "provider_type": raw_row.get("type"),
                        "attribute_keys": sorted(attribute_map),
                    },
                )
            )
        return canonical_records
