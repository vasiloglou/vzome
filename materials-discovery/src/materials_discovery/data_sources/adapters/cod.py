from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from materials_discovery.common.io import workspace_root
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.adapters.cif_conversion import cif_to_canonical_record
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord
from materials_discovery.data_sources.types import SourceAdapter, SourceAdapterInfo


def _discover_cif_paths(config: SystemConfig, snapshot_path: Path | None) -> list[Path]:
    if snapshot_path is not None:
        if snapshot_path.is_dir():
            return sorted(snapshot_path.glob("*.cif"))
        return [snapshot_path]

    ingestion = getattr(config, "ingestion", None)
    query = getattr(ingestion, "query", {}) if ingestion is not None else {}
    cif_paths = query.get("cif_paths") if isinstance(query, dict) else None
    if isinstance(cif_paths, list):
        resolved: list[Path] = []
        for entry in cif_paths:
            path = Path(str(entry))
            if not path.is_absolute():
                path = workspace_root() / path
            resolved.append(path)
        return resolved

    raise ValueError("COD adapter requires a CIF snapshot path or ingestion.query.cif_paths")


@dataclass(frozen=True)
class CodSourceAdapter(SourceAdapter):
    def info(self) -> SourceAdapterInfo:
        return SourceAdapterInfo(
            adapter_key="cif_archive_v1",
            source_key="cod",
            adapter_family="cif_conversion",
            version="2026.04",
            description="COD local CIF conversion adapter",
        )

    def default_snapshot_id(self, config: SystemConfig) -> str:
        return "cod_local_snapshot_v1"

    def load_rows(
        self,
        config: SystemConfig,
        snapshot_path: Path | None,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for cif_path in _discover_cif_paths(config, snapshot_path):
            rows.append(
                {
                    "cod_id": cif_path.stem,
                    "cif_path": str(cif_path.resolve()),
                    "retrieved_at_utc": "2026-04-03T00:00:00Z",
                }
            )
        return rows

    def canonicalize_rows(
        self,
        config: SystemConfig,
        raw_rows: list[dict[str, Any]],
        snapshot_id: str,
        raw_payload_path: Path,
    ) -> list[CanonicalRawSourceRecord]:
        adapter_info = self.info()
        return [
            cif_to_canonical_record(row, snapshot_id, raw_payload_path, adapter_info)
            for row in raw_rows
        ]


def build_cod_source_adapters() -> list[SourceAdapter]:
    return [CodSourceAdapter()]
