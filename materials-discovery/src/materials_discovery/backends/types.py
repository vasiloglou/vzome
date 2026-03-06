from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from materials_discovery.common.schema import SystemConfig


@dataclass(frozen=True)
class IngestBackendInfo:
    name: str
    version: str


class IngestBackend(Protocol):
    def info(self) -> IngestBackendInfo:
        ...

    def load_rows(self, config: SystemConfig, fixture_path: Path | None) -> list[dict[str, Any]]:
        ...
