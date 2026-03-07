from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

QPhiPair = tuple[int, int]
QPhiCoord = tuple[QPhiPair, QPhiPair, QPhiPair]
Position3D = tuple[float, float, float]


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
    fractional_position: Position3D | None = None
    cartesian_position: Position3D | None = None

    @field_validator("occ")
    @classmethod
    def validate_occupancy(cls, value: float) -> float:
        if value < 0.0 or value > 1.0:
            raise ValueError("site occupancy must be in [0, 1]")
        return value

    @field_validator("fractional_position")
    @classmethod
    def validate_fractional_position(
        cls,
        value: Position3D | None,
    ) -> Position3D | None:
        if value is None:
            return value
        for coord in value:
            if coord < 0.0 or coord >= 1.0:
                raise ValueError("fractional positions must be in [0, 1)")
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
    geometry_prefilter_pass: bool | None = None
    geometry_prefilter_reason: str | None = None
    minimum_cartesian_distance_angstrom: float | None = None
    close_contact_pairs: int | None = None
    volume_per_atom_ang3: float | None = None
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
    committee_provider: str | None = None
    phonon_provider: str | None = None
    md_provider: str | None = None
    xrd_provider: str | None = None
    pinned_snapshot: str | None = None
    validation_snapshot: str | None = None
    validation_cache_dir: str | None = None
    committee_command: list[str] | None = None
    phonon_command: list[str] | None = None
    md_command: list[str] | None = None
    xrd_command: list[str] | None = None
    committee_device: str | None = None
    md_temperature_k: float = 600.0
    md_timestep_fs: float = 0.5
    md_steps: int = 50
    xrd_wavelength: str = "CuKa"
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
            if self.committee_provider is None:
                self.committee_provider = "pinned"
            if self.phonon_provider is None:
                self.phonon_provider = "pinned"
            if self.md_provider is None:
                self.md_provider = "pinned"
            if self.xrd_provider is None:
                self.xrd_provider = "pinned"
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

    @model_validator(mode="after")
    def validate_runtime_settings(self) -> BackendConfig:
        if self.md_temperature_k <= 0.0:
            raise ValueError("backend.md_temperature_k must be > 0")
        if self.md_timestep_fs <= 0.0:
            raise ValueError("backend.md_timestep_fs must be > 0")
        if self.md_steps <= 0:
            raise ValueError("backend.md_steps must be > 0")
        return self


class ZomicOrbitConfig(BaseModel):
    preferred_species: list[str] | None = None
    wyckoff: str | None = None


class ZomicDesignConfig(BaseModel):
    zomic_file: str
    prototype_key: str
    system_name: str
    template_family: str
    base_cell: dict[str, float]
    reference: str
    reference_url: str | None = None
    motif_center: Position3D = (0.5, 0.5, 0.5)
    translation_divisor: float
    radial_scale: float
    tangential_scale: float
    reference_axes: tuple[Position3D, Position3D, Position3D]
    minimum_site_separation: float
    preferred_species_by_orbit: dict[str, list[str]] = Field(default_factory=dict)
    orbit_config: dict[str, ZomicOrbitConfig] = Field(default_factory=dict)
    cartesian_scale: float | None = None
    embedding_fraction: float = 0.72
    anchor_prototype: str | None = None
    anchor_orbit_strategy: Literal["snap_only", "seed_orbit_expand"] = "snap_only"
    anchor_site_target: int | None = None
    anchor_orbit_min_votes: int = 1
    export_path: str | None = None
    raw_export_path: str | None = None
    space_group: str | None = None

    @field_validator("motif_center")
    @classmethod
    def validate_motif_center(cls, value: Position3D) -> Position3D:
        for coord in value:
            if coord <= 0.0 or coord >= 1.0:
                raise ValueError("motif_center coordinates must be strictly within (0, 1)")
        return value

    @field_validator("base_cell")
    @classmethod
    def validate_base_cell(cls, value: dict[str, float]) -> dict[str, float]:
        required = {"a", "b", "c", "alpha", "beta", "gamma"}
        missing = sorted(required - set(value))
        if missing:
            raise ValueError(f"base_cell missing required keys: {missing}")
        for key in ("a", "b", "c"):
            if value[key] <= 0.0:
                raise ValueError(f"base_cell.{key} must be > 0")
        for key in ("alpha", "beta", "gamma"):
            if value[key] <= 0.0 or value[key] >= 180.0:
                raise ValueError(f"base_cell.{key} must be in (0, 180)")
        return value

    @model_validator(mode="after")
    def validate_embedding(self) -> ZomicDesignConfig:
        if self.translation_divisor <= 0.0:
            raise ValueError("translation_divisor must be > 0")
        if self.radial_scale <= 0.0:
            raise ValueError("radial_scale must be > 0")
        if self.tangential_scale <= 0.0:
            raise ValueError("tangential_scale must be > 0")
        if self.minimum_site_separation <= 0.0:
            raise ValueError("minimum_site_separation must be > 0")
        if self.cartesian_scale is not None and self.cartesian_scale <= 0.0:
            raise ValueError("cartesian_scale must be > 0 when provided")
        if self.embedding_fraction <= 0.0 or self.embedding_fraction >= 1.0:
            raise ValueError("embedding_fraction must be in (0, 1)")
        if self.anchor_prototype is None:
            if self.anchor_orbit_strategy != "snap_only":
                raise ValueError("anchor_orbit_strategy requires anchor_prototype")
            if self.anchor_site_target is not None:
                raise ValueError("anchor_site_target requires anchor_prototype")
            if self.anchor_orbit_min_votes != 1:
                raise ValueError("anchor_orbit_min_votes requires anchor_prototype")
        if self.anchor_site_target is not None and self.anchor_site_target <= 0:
            raise ValueError("anchor_site_target must be > 0 when provided")
        if self.anchor_orbit_min_votes <= 0:
            raise ValueError("anchor_orbit_min_votes must be > 0")
        return self


class SystemConfig(BaseModel):
    system_name: str
    template_family: str
    species: list[str]
    composition_bounds: dict[str, CompositionBound]
    coeff_bounds: CoeffBounds
    seed: int
    default_count: int
    prototype_library: str | None = None
    zomic_design: str | None = None
    backend: BackendConfig = Field(default_factory=BackendConfig)

    @model_validator(mode="after")
    def validate_species(self) -> SystemConfig:
        missing = [s for s in self.species if s not in self.composition_bounds]
        if missing:
            raise ValueError(f"composition_bounds missing species entries: {missing}")
        if self.prototype_library and self.zomic_design:
            raise ValueError("prototype_library and zomic_design are mutually exclusive")
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


class ZomicExportSummary(BaseModel):
    design_path: str
    zomic_file: str
    raw_export_path: str
    orbit_library_path: str
    labeled_site_count: int
    orbit_count: int


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
