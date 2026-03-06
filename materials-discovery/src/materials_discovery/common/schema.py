from __future__ import annotations

from collections.abc import Sequence
from typing import Any

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


class SystemConfig(BaseModel):
    system_name: str
    template_family: str
    species: list[str]
    composition_bounds: dict[str, CompositionBound]
    coeff_bounds: CoeffBounds
    seed: int
    default_count: int

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


class GenerateSummary(BaseModel):
    requested_count: int
    generated_count: int
    invalid_filtered_count: int
    output_path: str


class ScreenSummary(BaseModel):
    input_count: int
    relaxed_count: int
    passed_count: int
    shortlisted_count: int
    output_path: str


class HifiValidateSummary(BaseModel):
    batch: str
    input_count: int
    validated_count: int
    passed_count: int
    output_path: str


def validate_unique_candidate_ids(candidates: Sequence[CandidateRecord]) -> None:
    ids = [candidate.candidate_id for candidate in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("candidate IDs must be unique")
