from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from materials_discovery.common.schema import SystemConfig
from materials_discovery.data_sources.registry import (
    clear_source_adapters_for_tests,
    list_source_adapters,
    register_source_adapter,
    resolve_source_adapter,
)
from materials_discovery.data_sources.types import SourceAdapterInfo


@dataclass
class _DummyAdapter:
    adapter_info: SourceAdapterInfo

    def info(self) -> SourceAdapterInfo:
        return self.adapter_info

    def default_snapshot_id(self, config: SystemConfig) -> str:
        return "snapshot-001"

    def load_rows(
        self,
        config: SystemConfig,
        snapshot_path: Path | None,
    ) -> list[dict[str, object]]:
        return []

    def canonicalize_rows(
        self,
        config: SystemConfig,
        raw_rows: list[dict[str, object]],
        snapshot_id: str,
        raw_payload_path: Path,
    ) -> list[object]:
        return []


@pytest.fixture(autouse=True)
def _clear_registry() -> None:
    clear_source_adapters_for_tests()
    yield
    clear_source_adapters_for_tests()


def _adapter(source_key: str, adapter_key: str, adapter_family: str) -> _DummyAdapter:
    return _DummyAdapter(
        SourceAdapterInfo(
            adapter_key=adapter_key,
            source_key=source_key,
            adapter_family=adapter_family,
            version="v1",
            description=f"{source_key}:{adapter_key}",
        )
    )


def test_source_registry_registers_and_resolves_defaults() -> None:
    hypodx = _adapter("hypodx", "fixture_direct", "direct")
    cod = _adapter("cod", "cif_archive_v1", "cif_conversion")
    jarvis = _adapter("jarvis", "optimade_v1", "optimade")

    register_source_adapter(hypodx, make_default=True)
    register_source_adapter(cod, make_default=True)
    register_source_adapter(jarvis, make_default=True)

    assert resolve_source_adapter("hypodx") is hypodx
    assert resolve_source_adapter("cod") is cod
    assert resolve_source_adapter("jarvis") is jarvis


def test_source_registry_resolves_explicit_source_adapter_variants() -> None:
    direct = _adapter("materials_project", "rest_api_v1", "direct")
    optimade = _adapter("materials_project", "optimade_v1", "optimade")

    register_source_adapter(direct, make_default=True)
    register_source_adapter(optimade)

    assert resolve_source_adapter("materials_project") is direct
    assert resolve_source_adapter("materials_project", "optimade_v1") is optimade

    listed = {
        (entry.source_key, entry.adapter_key, entry.adapter_family)
        for entry in list_source_adapters()
    }
    assert ("materials_project", "rest_api_v1", "direct") in listed
    assert ("materials_project", "optimade_v1", "optimade") in listed


def test_source_registry_raises_for_unknown_source_or_adapter() -> None:
    register_source_adapter(_adapter("oqmd", "rest_api_v1", "direct"), make_default=True)

    with pytest.raises(ValueError, match="Unknown source 'cod'"):
        resolve_source_adapter("cod")

    with pytest.raises(ValueError, match="Unknown source adapter combination 'oqmd:optimade_v1'"):
        resolve_source_adapter("oqmd", "optimade_v1")
