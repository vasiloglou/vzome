from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class PhaseDataConnector(Protocol):
    def load(self, snapshot_path: Path) -> list[dict[str, Any]]:
        ...
