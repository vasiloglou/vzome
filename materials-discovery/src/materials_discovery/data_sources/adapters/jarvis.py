from __future__ import annotations

from materials_discovery.data_sources.adapters.optimade import OptimadeSourceAdapter
from materials_discovery.data_sources.types import SourceAdapter


def build_jarvis_source_adapters() -> list[SourceAdapter]:
    return [
        OptimadeSourceAdapter(
            source_key="jarvis",
            base_url="https://jarvis.nist.gov/optimade/jarvisdft/v1/structures",
            adapter_key="optimade_v1",
            version="2026.04",
            source_name="JARVIS",
            default_snapshot="jarvis_optimade_snapshot_v1",
            description="JARVIS OPTIMADE source adapter",
        )
    ]
