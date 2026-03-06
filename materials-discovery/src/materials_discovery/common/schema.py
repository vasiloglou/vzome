from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

QPhiPair = tuple[int, int]
QPhiCoord = tuple[QPhiPair, QPhiPair, QPhiPair]


class CompositionBound(BaseModel):
    min: float
    max: float

    @model_validator(mode="after")
    def validate_bounds(self) -> CompositionBound:
        if self.min > self.max:
            raise ValueError("composition bound min must be <= max")
        if self.min < 0.0 or self.max > 1.0:
            raise ValueError("composition bounds must be in [0, 1]")
        return self


class CoeffBounds(BaseModel):
    min: int
    max: int

    @model_validator(mode="after")
    def validate_bounds(self) -> CoeffBounds:
        if self.min > self.max:
            raise ValueError("coeff_bounds.min must be <= coeff_bounds.max")
        return self


class SiteRecord(BaseModel):
    label: str
    qphi: QPhiCoord
    species: str
    occ: float

    @field_validator("occ")
    @classmethod
    def validate_occupancy(cls, value: float) -> float:
        if value < 0.0 or value > 1.0:
            raise ValueError("site occupancy must be in [0, 1]")
        return value


class DigitalValidationRecord(BaseModel):
    status: str = "pending"
    committee: list[str] = Field(default_factory=lambda: ["MACE", "CHGNet", "MatterSim"])
    uncertainty_ev_per_atom: float | None = None
    committee_energy_ev_per_atom: dict[str, float] | None = None
    committee_std_ev_per_atom: float | None = None
    delta_e_proxy_hull_ev_per_atom: float | None = None
    proxy_hull_baseline_ev_per_atom: float | None = None
    proxy_hull_reference_distance: float | None = None
    proxy_hull_reference_phases: list[str] | None = None
    phonon_imaginary_modes: int | None = None
    phonon_pass: bool | None = None
    md_stability_score: float | None = None
    md_pass: bool | None = None
    xrd_confidence: float | None = None
    xrd_pass: bool | None = None
    passed_checks: bool | None = None
    batch: str | None = None


class CandidateRecord(BaseModel):
    candidate_id: str
    system: str
    template_family: str
    cell: dict[str, float]
    sites: list[SiteRecord]
    composition: dict[str, float]
    screen: dict[str, Any] | None = None
    digital_validation: DigitalValidationRecord = Field(default_factory=DigitalValidationRecord)
    provenance: dict[str, Any]

    @model_validator(mode="after")
    def validate_composition(self) -> CandidateRecord:
        if not self.composition:
            raise ValueError("composition cannot be empty")
        total = sum(self.composition.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError("composition fractions must sum to 1.0 +/- 1e-6")
        return self


class BackendConfig(BaseModel):
    mode: Literal["mock", "real"] = "mock"
    ingest_adapter: str | None = None
    committee_adapter: str | None = None
    phonon_adapter: str | None = None
    md_adapter: str | None = None
    xrd_adapter: str | None = None
    pinned_snapshot: str | None = None
    validation_snapshot: str | None = None
    validation_cache_dir: str | None = None
    committee_command: list[str] | None = None
    phonon_command: list[str] | None = None
    md_command: list[str] | None = None
    xrd_command: list[str] | None = None
    benchmark_corpus: str | None = None
    versions: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def default_adapter(self) -> BackendConfig:
        if self.ingest_adapter is None:
            self.ingest_adapter = (
                "hypodx_fixture" if self.mode == "mock" else "hypodx_pinned_v2026_03_09"
            )
        if self.mode == "real":
            if self.committee_adapter is None:
                self.committee_adapter = "committee_fixture_fallback_v2026_03_09"
            if self.phonon_adapter is None:
                self.phonon_adapter = "phonon_fixture_fallback_v2026_03_09"
            if self.md_adapter is None:
                self.md_adapter = "md_fixture_fallback_v2026_03_09"
            if self.xrd_adapter is None:
                self.xrd_adapter = "xrd_fixture_fallback_v2026_03_09"
        return self

    @field_validator(
        "committee_command",
        "phonon_command",
        "md_command",
        "xrd_command",
    )
    @classmethod
    def validate_command_list(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        if not value:
            raise ValueError("backend command lists must be non-empty when configured")
        return value


class SystemConfig(BaseModel):
    system_name: str
    template_family: str
    species: list[str]
    composition_bounds: dict[str, CompositionBound]
    coeff_bounds: CoeffBounds
    seed: int
    default_count: int
    backend: BackendConfig = Field(default_factory=BackendConfig)

    @model_validator(mode="after")
    def validate_species(self) -> SystemConfig:
        missing = [s for s in self.species if s not in self.composition_bounds]
        if missing:
            raise ValueError(f"composition_bounds missing species entries: {missing}")
        return self


class IngestRecord(BaseModel):
    system: str
    phase_name: str
    composition: dict[str, float]
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_composition(self) -> IngestRecord:
        total = sum(self.composition.values())
        if total <= 0:
            raise ValueError("composition must have positive total")
        normed = {k: v / total for k, v in self.composition.items()}
        self.composition = normed
        return self


class IngestSummary(BaseModel):
    raw_count: int
    matched_count: int
    deduped_count: int
    output_path: str
    invalid_count: int = 0
    backend_mode: Literal["mock", "real"] = "mock"
    backend_adapter: str = "hypodx_fixture"
    qa_metrics: dict[str, float | int | bool] = Field(default_factory=dict)
    manifest_path: str | None = None


class GenerateSummary(BaseModel):
    requested_count: int
    generated_count: int
    invalid_filtered_count: int
    output_path: str
    qa_metrics: dict[str, float | int | bool] = Field(default_factory=dict)
    calibration_path: str | None = None
    manifest_path: str | None = None


class ScreenSummary(BaseModel):
    input_count: int
    relaxed_count: int
    passed_count: int
    shortlisted_count: int
    output_path: str
    calibration_path: str | None = None
    manifest_path: str | None = None


class HifiValidateSummary(BaseModel):
    batch: str
    input_count: int
    validated_count: int
    passed_count: int
    output_path: str
    calibration_path: str | None = None
    manifest_path: str | None = None


class ActiveLearnSummary(BaseModel):
    validated_count: int
    selected_count: int
    pass_rate: float
    surrogate_path: str
    batch_path: str
    feature_store_path: str | None = None
    model_registry_path: str | None = None
    model_id: str | None = None
    manifest_path: str | None = None


class HifiRankSummary(BaseModel):
    input_count: int
    ranked_count: int
    passed_count: int
    output_path: str
    calibration_path: str | None = None
    manifest_path: str | None = None


class ReportSummary(BaseModel):
    ranked_count: int
    reported_count: int
    report_path: str
    xrd_patterns_path: str
    calibration_path: str | None = None
    report_fingerprint: str | None = None
    manifest_path: str | None = None
    pipeline_manifest_path: str | None = None


class ArtifactManifest(BaseModel):
    run_id: str
    stage: str
    system: str
    config_hash: str
    backend_mode: Literal["mock", "real"]
    backend_versions: dict[str, str]
    output_hashes: dict[str, str]
    created_at_utc: str


def validate_unique_candidate_ids(candidates: Sequence[CandidateRecord]) -> None:
    ids = [candidate.candidate_id for candidate in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("candidate IDs must be unique")
