from __future__ import annotations

from materials_discovery.data_sources.adapters import (
    build_cod_source_adapters,
    build_hypodx_source_adapters,
    build_jarvis_source_adapters,
    build_materials_project_source_adapters,
    build_oqmd_source_adapters,
)
from materials_discovery.data_sources.types import SourceAdapter, SourceAdapterInfo

SOURCE_RUNTIME_BRIDGE_ADAPTER_KEY = "source_registry_v1"

_SOURCE_ADAPTERS: dict[tuple[str, str], SourceAdapter] = {}
_DEFAULT_SOURCE_ADAPTERS: dict[str, str] = {}
_BUILTINS_REGISTERED = False


def register_source_adapter(adapter: SourceAdapter, *, make_default: bool = False) -> None:
    info = adapter.info()
    key = (info.source_key, info.adapter_key)
    _SOURCE_ADAPTERS[key] = adapter
    if make_default or info.source_key not in _DEFAULT_SOURCE_ADAPTERS:
        _DEFAULT_SOURCE_ADAPTERS[info.source_key] = info.adapter_key


def resolve_source_adapter(source_key: str, adapter_key: str | None = None) -> SourceAdapter:
    chosen_adapter = adapter_key or _DEFAULT_SOURCE_ADAPTERS.get(source_key)
    if chosen_adapter is None:
        known_sources = ", ".join(sorted(_DEFAULT_SOURCE_ADAPTERS))
        raise ValueError(
            f"Unknown source '{source_key}'. Expected one of: {known_sources or 'none registered'}"
        )
    try:
        return _SOURCE_ADAPTERS[(source_key, chosen_adapter)]
    except KeyError as exc:
        known = ", ".join(
            f"{entry_source}:{entry_adapter}"
            for entry_source, entry_adapter in sorted(_SOURCE_ADAPTERS)
        )
        raise ValueError(
            f"Unknown source adapter combination '{source_key}:{chosen_adapter}'. "
            f"Expected one of: {known or 'none registered'}"
        ) from exc


def list_source_adapters() -> list[SourceAdapterInfo]:
    return [adapter.info() for _, adapter in sorted(_SOURCE_ADAPTERS.items())]


def register_builtin_source_adapters() -> None:
    global _BUILTINS_REGISTERED
    if _BUILTINS_REGISTERED:
        return
    for adapter in [
        *build_hypodx_source_adapters(),
        *build_cod_source_adapters(),
        *build_materials_project_source_adapters(),
        *build_oqmd_source_adapters(),
        *build_jarvis_source_adapters(),
    ]:
        register_source_adapter(adapter, make_default=True)
    _BUILTINS_REGISTERED = True


def clear_source_adapters_for_tests() -> None:
    global _BUILTINS_REGISTERED
    _SOURCE_ADAPTERS.clear()
    _DEFAULT_SOURCE_ADAPTERS.clear()
    _BUILTINS_REGISTERED = False
