from __future__ import annotations

from pathlib import Path
from typing import Any

from materials_discovery.backends.types import IngestBackendInfo
from materials_discovery.common.io import workspace_root
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data.connectors.hypodx_pinned import load_hypodx_pinned_snapshot


class RealHypodxPinnedIngestBackend:
    """Pinned-snapshot HYPOD-X ingest backend for reproducible real-mode ingestion."""

    def info(self) -> IngestBackendInfo:
        return IngestBackendInfo(name="hypodx_pinned_v2026_03_09", version="2026.03.09")

    def load_rows(self, config: SystemConfig, fixture_path: Path | None) -> list[dict[str, Any]]:
        pinned_from_config = config.backend.pinned_snapshot
        default_snapshot = (
            workspace_root()
            / "data"
            / "external"
            / "pinned"
            / "hypodx_pinned_2026_03_09.json"
        )

        if fixture_path is not None:
            snapshot_path = fixture_path
        elif pinned_from_config is not None:
            snapshot_path = Path(pinned_from_config)
            if not snapshot_path.is_absolute():
                snapshot_path = workspace_root() / snapshot_path
        else:
            snapshot_path = default_snapshot

        return load_hypodx_pinned_snapshot(snapshot_path)
