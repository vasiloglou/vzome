from __future__ import annotations

from typing import TypeVar

from materials_discovery.backends.ingest_mock import MockFixtureIngestBackend
from materials_discovery.backends.ingest_real_hypodx import RealHypodxPinnedIngestBackend
from materials_discovery.backends.types import (
    CommitteeAdapter,
    IngestBackend,
    MdAdapter,
    PhononAdapter,
    XrdAdapter,
)
from materials_discovery.backends.validation_real_fixtures import (
    FixtureBackedCommitteeAdapter,
    FixtureBackedMdAdapter,
    FixtureBackedPhononAdapter,
    FixtureBackedXrdAdapter,
)

_INGEST_BACKENDS: dict[tuple[str, str], IngestBackend] = {
    ("mock", "hypodx_fixture"): MockFixtureIngestBackend(),
    ("real", "hypodx_pinned_v2026_03_09"): RealHypodxPinnedIngestBackend(),
}

_DEFAULT_ADAPTERS: dict[str, str] = {
    "mock": "hypodx_fixture",
    "real": "hypodx_pinned_v2026_03_09",
}

_COMMITTEE_ADAPTERS: dict[tuple[str, str], CommitteeAdapter] = {
    ("real", "committee_fixture_fallback_v2026_03_09"): FixtureBackedCommitteeAdapter(),
}

_PHONON_ADAPTERS: dict[tuple[str, str], PhononAdapter] = {
    ("real", "phonon_fixture_fallback_v2026_03_09"): FixtureBackedPhononAdapter(),
}

_MD_ADAPTERS: dict[tuple[str, str], MdAdapter] = {
    ("real", "md_fixture_fallback_v2026_03_09"): FixtureBackedMdAdapter(),
}

_XRD_ADAPTERS: dict[tuple[str, str], XrdAdapter] = {
    ("real", "xrd_fixture_fallback_v2026_03_09"): FixtureBackedXrdAdapter(),
}

_DEFAULT_COMMITTEE_ADAPTERS: dict[str, str] = {
    "real": "committee_fixture_fallback_v2026_03_09",
}

_DEFAULT_PHONON_ADAPTERS: dict[str, str] = {
    "real": "phonon_fixture_fallback_v2026_03_09",
}

_DEFAULT_MD_ADAPTERS: dict[str, str] = {
    "real": "md_fixture_fallback_v2026_03_09",
}

_DEFAULT_XRD_ADAPTERS: dict[str, str] = {
    "real": "xrd_fixture_fallback_v2026_03_09",
}

AdapterType = TypeVar("AdapterType")


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


def _resolve_adapter(
    registry: dict[tuple[str, str], AdapterType],
    defaults: dict[str, str],
    mode: str,
    adapter: str | None,
    label: str,
) -> AdapterType:
    chosen_adapter = adapter or defaults.get(mode)
    if chosen_adapter is None:
        known_modes = ", ".join(sorted(defaults.keys()))
        raise ValueError(
            f"Unknown backend mode '{mode}' for {label}. Expected one of: {known_modes}"
        )
    try:
        return registry[(mode, chosen_adapter)]
    except KeyError as exc:
        known = ", ".join(
            f"{entry_mode}:{entry_adapter}"
            for entry_mode, entry_adapter in sorted(registry)
        )
        raise ValueError(
            f"Unknown {label} backend combination '{mode}:{chosen_adapter}'. "
            f"Expected one of: {known}"
        ) from exc


def resolve_committee_adapter(mode: str, adapter: str | None = None) -> CommitteeAdapter:
    return _resolve_adapter(
        _COMMITTEE_ADAPTERS,
        _DEFAULT_COMMITTEE_ADAPTERS,
        mode,
        adapter,
        "committee",
    )


def resolve_phonon_adapter(mode: str, adapter: str | None = None) -> PhononAdapter:
    return _resolve_adapter(
        _PHONON_ADAPTERS,
        _DEFAULT_PHONON_ADAPTERS,
        mode,
        adapter,
        "phonon",
    )


def resolve_md_adapter(mode: str, adapter: str | None = None) -> MdAdapter:
    return _resolve_adapter(
        _MD_ADAPTERS,
        _DEFAULT_MD_ADAPTERS,
        mode,
        adapter,
        "md",
    )


def resolve_xrd_adapter(mode: str, adapter: str | None = None) -> XrdAdapter:
    return _resolve_adapter(
        _XRD_ADAPTERS,
        _DEFAULT_XRD_ADAPTERS,
        mode,
        adapter,
        "xrd",
    )
