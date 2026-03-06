from __future__ import annotations

from pathlib import Path
from typing import Any

from materials_discovery.common.io import load_json_array


class HypodxPinnedConnector:
    """Connector for pinned local HYPOD-X-style snapshots."""

    def load(self, snapshot_path: Path) -> list[dict[str, Any]]:
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Pinned snapshot not found: {snapshot_path}")
        return load_json_array(snapshot_path)


def load_hypodx_pinned_snapshot(snapshot_path: Path) -> list[dict[str, Any]]:
    connector = HypodxPinnedConnector()
    rows: list[dict[str, Any]] = connector.load(snapshot_path)
    return rows
