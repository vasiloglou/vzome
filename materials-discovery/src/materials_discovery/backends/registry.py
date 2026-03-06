from __future__ import annotations

from materials_discovery.backends.ingest_mock import MockFixtureIngestBackend
from materials_discovery.backends.ingest_real_hypodx import RealHypodxPinnedIngestBackend
from materials_discovery.backends.types import IngestBackend

_INGEST_BACKENDS: dict[tuple[str, str], IngestBackend] = {
    ("mock", "hypodx_fixture"): MockFixtureIngestBackend(),
    ("real", "hypodx_pinned_v2026_03_09"): RealHypodxPinnedIngestBackend(),
}

_DEFAULT_ADAPTERS: dict[str, str] = {
    "mock": "hypodx_fixture",
    "real": "hypodx_pinned_v2026_03_09",
}


def resolve_ingest_backend(mode: str, adapter: str | None = None) -> IngestBackend:
    chosen_adapter = adapter or _DEFAULT_ADAPTERS.get(mode)
    if chosen_adapter is None:
        known_modes = ", ".join(sorted(_DEFAULT_ADAPTERS.keys()))
        raise ValueError(f"Unknown backend mode '{mode}'. Expected one of: {known_modes}")

    try:
        return _INGEST_BACKENDS[(mode, chosen_adapter)]
    except KeyError as exc:
        known = ", ".join(
            f"{entry_mode}:{entry_adapter}"
            for entry_mode, entry_adapter in sorted(_INGEST_BACKENDS)
        )
        raise ValueError(
            f"Unknown ingest backend combination '{mode}:{chosen_adapter}'. "
            f"Expected one of: {known}"
        ) from exc
