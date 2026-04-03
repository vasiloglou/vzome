from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from materials_discovery.common.io import load_json_array, workspace_root
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data.connectors.hypodx_pinned import load_hypodx_pinned_snapshot
from materials_discovery.data.normalize import normalize_raw_record
from materials_discovery.data_sources.schema import (
    CanonicalCommonFields,
    CanonicalRawSourceRecord,
    LineageInfo,
    RawPayloadInfo,
    SnapshotInfo,
    SourceIdentity,
    AccessInfo,
    LicenseInfo,
    derive_local_record_id,
)
from materials_discovery.data_sources.storage import workspace_relative
from materials_discovery.data_sources.types import SourceAdapter, SourceAdapterInfo

_FIXTURE_PATH = workspace_root() / "data" / "external" / "fixtures" / "hypodx_sample.json"
_PINNED_PATH = workspace_root() / "data" / "external" / "pinned" / "hypodx_pinned_2026_03_09.json"
_NORMALIZED_KEYS = {"system", "alloy_system", "alloy", "phase_name", "phase", "composition", "source"}


def _formula_from_composition(composition: dict[str, float]) -> str:
    return "".join(
        f"{element}{round(float(amount), 6):g}" for element, amount in sorted(composition.items())
    )


def _source_record_id(system: str, phase_name: str, composition: dict[str, float]) -> str:
    composition_signature = ",".join(
        f"{element}:{round(float(amount), 8):g}" for element, amount in sorted(composition.items())
    )
    return f"{system.strip().lower()}|{phase_name.strip().lower()}|{composition_signature}"


def _row_hash(raw_row: dict[str, Any]) -> str:
    payload = json.dumps(raw_row, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class HypodxSourceAdapter(SourceAdapter):
    adapter_key: str
    version: str
    access_surface: str
    retrieval_mode: str
    snapshot_id: str
    default_path: Path
    retrieved_at_utc: str

    def info(self) -> SourceAdapterInfo:
        return SourceAdapterInfo(
            adapter_key=self.adapter_key,
            source_key="hypodx",
            adapter_family="direct",
            version=self.version,
            description=f"HYPOD-X {self.access_surface} source adapter",
        )

    def default_snapshot_id(self, config: SystemConfig) -> str:
        return self.snapshot_id

    def load_rows(
        self,
        config: SystemConfig,
        snapshot_path: Path | None,
    ) -> list[dict[str, Any]]:
        if self.access_surface == "fixture":
            chosen_path = snapshot_path or self.default_path
            return load_json_array(chosen_path)

        pinned_from_config = config.backend.pinned_snapshot
        if snapshot_path is not None:
            chosen_path = snapshot_path
        elif pinned_from_config is not None:
            chosen_path = Path(pinned_from_config)
            if not chosen_path.is_absolute():
                chosen_path = workspace_root() / chosen_path
        else:
            chosen_path = self.default_path
        return load_hypodx_pinned_snapshot(chosen_path)

    def canonicalize_rows(
        self,
        config: SystemConfig,
        raw_rows: list[dict[str, Any]],
        snapshot_id: str,
        raw_payload_path: Path,
    ) -> list[CanonicalRawSourceRecord]:
        adapter_info = self.info()
        canonical_records: list[CanonicalRawSourceRecord] = []
        for raw_row in raw_rows:
            try:
                normalized = normalize_raw_record(raw_row)
            except ValueError:
                continue

            source_record_id = _source_record_id(
                normalized.system,
                normalized.phase_name,
                normalized.composition,
            )
            local_record_id = derive_local_record_id("hypodx", snapshot_id, source_record_id)
            extra_metadata = {
                key: value for key, value in raw_row.items() if key not in _NORMALIZED_KEYS
            }
            extra_metadata["phase_name"] = normalized.phase_name
            extra_metadata["raw_keys"] = sorted(raw_row)
            extra_metadata["provider_source"] = normalized.source

            canonical_records.append(
                CanonicalRawSourceRecord(
                    local_record_id=local_record_id,
                    record_kind="phase_entry",
                    source=SourceIdentity(
                        source_key="hypodx",
                        source_name="HYPOD-X",
                        source_record_id=source_record_id,
                        record_title=normalized.phase_name,
                    ),
                    access=AccessInfo(
                        access_level="open",
                        auth_required=False,
                        access_surface=self.access_surface,
                        redistribution_posture="allowed_with_attribution",
                    ),
                    license=LicenseInfo(
                        license_expression="CC-BY-4.0",
                        license_category="open",
                        attribution_required=True,
                        commercial_use_allowed=True,
                    ),
                    snapshot=SnapshotInfo(
                        snapshot_id=snapshot_id,
                        source_version=self.version,
                        source_release_date=None,
                        retrieved_at_utc=self.retrieved_at_utc,
                        retrieval_mode=self.retrieval_mode,
                        snapshot_manifest_path="",
                    ),
                    raw_payload=RawPayloadInfo(
                        payload_path=workspace_relative(raw_payload_path),
                        payload_format="jsonl",
                        content_hash=_row_hash(raw_row),
                    ),
                    common=CanonicalCommonFields(
                        chemical_system=normalized.system,
                        elements=sorted(normalized.composition),
                        formula_raw=_formula_from_composition(normalized.composition),
                        formula_reduced=_formula_from_composition(normalized.composition),
                        composition=normalized.composition,
                        reported_properties={"phase_name": normalized.phase_name},
                        keywords=[normalized.phase_name],
                    ),
                    lineage=LineageInfo(
                        adapter_key=adapter_info.adapter_key,
                        adapter_family=adapter_info.adapter_family,
                        adapter_version=adapter_info.version,
                        fetch_manifest_id=f"{adapter_info.adapter_key}:fetch:{snapshot_id}",
                        normalize_manifest_id=f"{adapter_info.adapter_key}:normalize:{snapshot_id}",
                    ),
                    source_metadata=extra_metadata,
                )
            )
        return canonical_records


def build_hypodx_source_adapters() -> list[SourceAdapter]:
    return [
        HypodxSourceAdapter(
            adapter_key="fixture_json_v1",
            version="fixture.2026-04-03",
            access_surface="fixture",
            retrieval_mode="fixture",
            snapshot_id="hypodx_fixture_sample_v1",
            default_path=_FIXTURE_PATH,
            retrieved_at_utc="2026-04-03T00:00:00Z",
        ),
        HypodxSourceAdapter(
            adapter_key="pinned_snapshot_v2026_03_09",
            version="2026.03.09",
            access_surface="pinned_snapshot",
            retrieval_mode="bulk",
            snapshot_id="hypodx_pinned_2026_03_09",
            default_path=_PINNED_PATH,
            retrieved_at_utc="2026-03-09T00:00:00Z",
        ),
    ]
