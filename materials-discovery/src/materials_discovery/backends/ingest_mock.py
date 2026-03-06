from __future__ import annotations

from pathlib import Path
from typing import Any

from materials_discovery.backends.types import IngestBackendInfo
from materials_discovery.common.io import load_json_array, workspace_root
from materials_discovery.common.schema import SystemConfig


class MockFixtureIngestBackend:
    """Fixture-backed ingest backend used for deterministic local development."""

    def info(self) -> IngestBackendInfo:
        return IngestBackendInfo(name="hypodx_fixture", version="mock-0.1.0")

    def load_rows(self, config: SystemConfig, fixture_path: Path | None) -> list[dict[str, Any]]:
        _ = config
        default_fixture = workspace_root() / "data" / "external" / "fixtures" / "hypodx_sample.json"
        source = fixture_path or default_fixture
        if not source.exists():
            raise FileNotFoundError(f"Fixture file not found: {source}")
        return load_json_array(source)
