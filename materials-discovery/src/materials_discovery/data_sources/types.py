from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.schema import AdapterFamily, CanonicalRawSourceRecord


@dataclass(frozen=True)
class SourceAdapterInfo:
    adapter_key: str
    source_key: str
    adapter_family: AdapterFamily
    version: str
    description: str = ""


class SourceAdapter(Protocol):
    def info(self) -> SourceAdapterInfo:
        ...

    def default_snapshot_id(self, config: SystemConfig) -> str:
        ...

    def load_rows(
        self,
        config: SystemConfig,
        snapshot_path: Path | None,
    ) -> list[dict[str, Any]]:
        ...

    def canonicalize_rows(
        self,
        config: SystemConfig,
        raw_rows: list[dict[str, Any]],
        snapshot_id: str,
        raw_payload_path: Path,
    ) -> list[CanonicalRawSourceRecord]:
        ...
