from __future__ import annotations

import hashlib
import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

AdapterFamily = Literal[
    "direct",
    "optimade",
    "cif_conversion",
    "curated_manual",
    "archive_repository",
]
RecordKind = Literal[
    "structure",
    "material_entry",
    "phase_entry",
    "dataset_member",
    "repository_asset",
]
AccessLevel = Literal["open", "restricted", "subscription", "manual"]
RedistributionPosture = Literal[
    "allowed",
    "allowed_with_attribution",
    "unknown",
    "not_allowed",
]
LicenseCategory = Literal["open", "restricted", "subscription", "custom", "unknown"]
RetrievalMode = Literal["api", "optimade", "bulk", "manual", "fixture", "mixed"]
StructureStatus = Literal["valid", "missing", "malformed", "unsupported"]
CompositionStatus = Literal["valid", "missing", "malformed", "partial"]

_LOCAL_RECORD_ID_PATTERN = re.compile(r"^src_[a-z0-9_]+_[0-9a-f]{16}$")


def derive_local_record_id(source_key: str, snapshot_id: str, source_record_id: str) -> str:
    stable_source_key = source_key.strip().lower().replace("-", "_")
    payload = f"{stable_source_key}|{snapshot_id}|{source_record_id}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:16]
    return f"src_{stable_source_key}_{digest}"


class SourceIdentity(BaseModel):
    source_key: str
    source_name: str
    source_record_id: str
    source_record_url: str | None = None
    source_namespace: str | None = None
    record_title: str | None = None


class AccessInfo(BaseModel):
    access_level: AccessLevel
    auth_required: bool
    access_surface: str
    terms_url: str | None = None
    redistribution_posture: RedistributionPosture


class LicenseInfo(BaseModel):
    license_expression: str
    license_url: str | None = None
    license_category: LicenseCategory
    attribution_required: bool
    commercial_use_allowed: bool | None = None
    notes: str | None = None


class SnapshotInfo(BaseModel):
    snapshot_id: str
    source_version: str | None = None
    source_release_date: str | None = None
    retrieved_at_utc: str
    retrieval_mode: RetrievalMode
    snapshot_manifest_path: str


class RawPayloadInfo(BaseModel):
    payload_path: str
    payload_format: str
    payload_encoding: str | None = None
    content_hash: str
    raw_excerpt: dict[str, Any] | None = None


class StructureRepresentation(BaseModel):
    representation_kind: str
    payload_path: str | None = None
    payload_format: str | None = None
    content_hash: str | None = None
    structure_summary: dict[str, Any] = Field(default_factory=dict)


class CanonicalCommonFields(BaseModel):
    chemical_system: str | None = None
    elements: list[str] = Field(default_factory=list)
    formula_raw: str | None = None
    formula_reduced: str | None = None
    composition: dict[str, float] | None = None
    structure_representations: list[StructureRepresentation] = Field(default_factory=list)
    space_group: str | None = None
    dimension_class: str | None = None
    reported_properties: dict[str, Any] = Field(default_factory=dict)
    citations: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)

    @field_validator("elements")
    @classmethod
    def normalize_elements(cls, value: list[str]) -> list[str]:
        normalized = sorted({element.strip() for element in value if element.strip()})
        return normalized

    @model_validator(mode="after")
    def normalize_composition(self) -> CanonicalCommonFields:
        if self.composition is None:
            return self
        total = sum(self.composition.values())
        if total <= 0.0:
            raise ValueError("composition must have positive total")
        self.composition = {
            key: value / total for key, value in sorted(self.composition.items())
        }
        if not self.elements:
            self.elements = sorted(self.composition)
        return self


class CanonicalQaState(BaseModel):
    schema_valid: bool = True
    required_field_gaps: list[str] = Field(default_factory=list)
    normalization_warnings: list[str] = Field(default_factory=list)
    duplicate_keys: list[str] = Field(default_factory=list)
    structure_status: StructureStatus = "missing"
    composition_status: CompositionStatus = "missing"
    schema_drift_flags: list[str] = Field(default_factory=list)
    needs_manual_review: bool = False


class LineageInfo(BaseModel):
    adapter_key: str
    adapter_family: AdapterFamily
    adapter_version: str
    fetch_manifest_id: str
    normalize_manifest_id: str
    parent_snapshot_ids: list[str] = Field(default_factory=list)
    projection_status: str | None = None


class CanonicalRawSourceRecord(BaseModel):
    schema_version: str = "raw-source-record/v1"
    local_record_id: str
    record_kind: RecordKind
    source: SourceIdentity
    access: AccessInfo
    license: LicenseInfo
    snapshot: SnapshotInfo
    raw_payload: RawPayloadInfo
    common: CanonicalCommonFields
    qa: CanonicalQaState = Field(default_factory=CanonicalQaState)
    lineage: LineageInfo
    source_metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("local_record_id")
    @classmethod
    def validate_local_record_id(cls, value: str) -> str:
        if not _LOCAL_RECORD_ID_PATTERN.fullmatch(value):
            raise ValueError("local_record_id must match src_<source_key>_<16 hex chars>")
        return value

    @model_validator(mode="after")
    def validate_identity(self) -> CanonicalRawSourceRecord:
        expected_prefix = f"src_{self.source.source_key.strip().lower().replace('-', '_')}_"
        if not self.local_record_id.startswith(expected_prefix):
            raise ValueError("local_record_id must encode the source_key prefix")
        return self


class SourceSnapshotManifest(BaseModel):
    manifest_id: str
    stage: str
    source_key: str
    snapshot_id: str
    adapter_key: str
    adapter_version: str
    created_at_utc: str
    output_hashes: dict[str, str]
    record_counts: dict[str, int]
    license_summary: dict[str, int]
    qa_summary: dict[str, int | bool]
    parent_manifest_id: str | None = None


class SourceQaReport(BaseModel):
    source_key: str
    snapshot_id: str
    raw_count: int
    canonical_count: int
    valid_count: int
    duplicate_collision_count: int
    missing_required_core_field_count: int
    invalid_composition_count: int
    malformed_structure_count: int
    schema_drift_count: int
    needs_manual_review_count: int
    passed: bool


class SourceStageSummary(BaseModel):
    source_key: str
    snapshot_id: str
    raw_count: int
    canonical_count: int
    output_dir: str
    raw_rows_path: str
    canonical_records_path: str
    qa_report_path: str
    snapshot_manifest_path: str


class ProjectionSummary(BaseModel):
    input_count: int = 0
    matched_system_count: int = 0
    projected_count: int = 0
    deduped_count: int = 0
    skipped_system_mismatch_count: int = 0
    skipped_missing_composition_count: int = 0
    duplicate_dropped_count: int = 0


# ---------------------------------------------------------------------------
# Reference-pack manifest and assembly summary (written to disk, Phase 4)
# Config-layer models (ReferencePackConfig, ReferencePackMemberConfig) live
# in materials_discovery.common.schema to avoid circular imports.
# ---------------------------------------------------------------------------


class ReferencePackMemberResult(BaseModel):
    """Per-member assembly outcome recorded in pack_manifest.json."""

    source_key: str
    snapshot_id: str
    canonical_records_path: str
    snapshot_manifest_path: str | None = None
    canonical_record_count: int
    priority_rank: int


class ReferencePackManifest(BaseModel):
    """Written as ``pack_manifest.json`` inside the reference-pack directory."""

    schema_version: str = "reference-pack-manifest/v1"
    pack_id: str
    system_slug: str
    created_at_utc: str
    pack_fingerprint: str
    members: list[ReferencePackMemberResult]
    priority_order: list[str]
    total_canonical_records: int
    duplicate_dropped_count: int
    overlap_count: int
    canonical_records_path: str
