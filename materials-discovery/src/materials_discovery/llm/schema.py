from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from materials_discovery.common.schema import CompositionBound

SourceFamily = Literal[
    "repo_regression",
    "repo_parts",
    "materials_design",
    "candidate_record",
    "generated_export",
    "canonical_source",
    "reference_pack",
    "pyqcstrc_projection",
]
FidelityTier = Literal["exact", "anchored", "approximate", "heuristic"]
ReleaseTier = Literal["pending", "gold", "silver", "reject"]
ValidationStatus = Literal["pending", "passed", "failed"]

DEFAULT_CORPUS_SCHEMA_VERSION = "llm-corpus-example/v1"
DEFAULT_CORPUS_MANIFEST_VERSION = "llm-corpus-manifest/v1"
DEFAULT_BUILDER_VERSION = "phase6_v1"
DEFAULT_LLM_ATTEMPT_SCHEMA_VERSION = "llm-generation-attempt/v1"
DEFAULT_LLM_RESULT_SCHEMA_VERSION = "llm-generation-result/v1"
DEFAULT_LLM_RUN_MANIFEST_VERSION = "llm-run-manifest/v1"
DEFAULT_LLM_ASSESSMENT_SCHEMA_VERSION = "llm-assessment/v1"
DEFAULT_LLM_EVALUATION_REQUEST_SCHEMA_VERSION = "llm-evaluation-request/v1"
DEFAULT_LLM_EVALUATION_RUN_MANIFEST_VERSION = "llm-evaluation-run-manifest/v1"


def _normalize_string_list(values: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        stripped = value.strip()
        if stripped and stripped not in normalized:
            normalized.append(stripped)
    return normalized


class CorpusBuildConfig(BaseModel):
    build_id: str
    systems: list[str] = Field(default_factory=list)
    include_repo_regression: bool = True
    include_repo_parts: bool = True
    include_materials_designs: bool = True
    include_candidate_records: bool = True
    include_generated_exports: bool = True
    include_canonical_sources: bool = True
    include_reference_packs: bool = True
    include_pyqcstrc_projection: bool = True
    gold_min_sites: int
    gold_max_sites: int
    silver_max_sites: int
    collision_threshold_angstrom: float
    source_keys: list[str] = Field(default_factory=list)
    reference_pack_ids: list[str] = Field(default_factory=list)

    @field_validator("build_id")
    @classmethod
    def validate_build_id(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("build_id must not be blank")
        return stripped

    @field_validator("systems", "source_keys", "reference_pack_ids")
    @classmethod
    def normalize_string_lists(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @model_validator(mode="after")
    def validate_thresholds(self) -> CorpusBuildConfig:
        if self.gold_min_sites < 1:
            raise ValueError("gold_min_sites must be >= 1")
        if self.gold_max_sites < self.gold_min_sites:
            raise ValueError("gold_max_sites must be >= gold_min_sites")
        if self.silver_max_sites < self.gold_max_sites:
            raise ValueError("silver_max_sites must be >= gold_max_sites")
        if self.collision_threshold_angstrom <= 0.0:
            raise ValueError("collision_threshold_angstrom must be > 0")
        return self


class CorpusInventoryRow(BaseModel):
    source_family: SourceFamily
    source_path: str
    system: str | None = None
    source_record_id: str
    input_kind: str
    record_locator: dict[str, Any]
    loader_hint: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_path", "source_record_id", "input_kind", "loader_hint")
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("system")
    @classmethod
    def normalize_system(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("record_locator")
    @classmethod
    def validate_record_locator(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("record_locator must not be empty")
        return value


class CorpusProvenance(BaseModel):
    example_id: str
    source_family: SourceFamily
    source_path: str
    source_record_id: str
    system: str | None = None
    fidelity_tier: FidelityTier
    release_tier: ReleaseTier = "pending"
    builder_version: str = DEFAULT_BUILDER_VERSION

    @field_validator("example_id", "source_path", "source_record_id", "builder_version")
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("system")
    @classmethod
    def normalize_system(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def validate_release_fidelity_pair(self) -> CorpusProvenance:
        if self.release_tier == "pending":
            return self
        if self.release_tier == "gold" and self.fidelity_tier not in {"exact", "anchored"}:
            raise ValueError("gold examples must be exact or anchored")
        if self.release_tier == "silver" and self.fidelity_tier == "heuristic":
            raise ValueError("silver examples cannot be heuristic")
        return self


class CorpusValidationState(BaseModel):
    parse_status: ValidationStatus = "pending"
    compile_status: ValidationStatus = "pending"
    labels_valid: bool | None = None
    collision_free: bool | None = None
    site_count: int | None = None
    geometry_equivalence: bool | None = None
    geometry_error: float | None = None
    raw_export_path: str | None = None
    error_message: str | None = None

    @field_validator("site_count")
    @classmethod
    def validate_site_count(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 0:
            raise ValueError("site_count must be >= 0")
        return value

    @field_validator("geometry_error")
    @classmethod
    def validate_geometry_error(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if value < 0.0:
            raise ValueError("geometry_error must be >= 0")
        return value

    @field_validator("raw_export_path", "error_message")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class CorpusConversionTrace(BaseModel):
    strategy: str
    step_count: int
    fidelity_reason: str
    source_signature: str
    unresolved_axes: list[str] = Field(default_factory=list)

    @field_validator("strategy", "fidelity_reason", "source_signature")
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("step_count")
    @classmethod
    def validate_step_count(cls, value: int) -> int:
        if value < 0:
            raise ValueError("step_count must be >= 0")
        return value

    @field_validator("unresolved_axes")
    @classmethod
    def normalize_axes(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)


class CorpusExample(BaseModel):
    schema_version: str = DEFAULT_CORPUS_SCHEMA_VERSION
    provenance: CorpusProvenance
    zomic_text: str
    labels: list[str] = Field(default_factory=list)
    orbit_names: list[str] = Field(default_factory=list)
    composition: dict[str, float] | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    validation: CorpusValidationState = Field(default_factory=CorpusValidationState)
    conversion_trace: CorpusConversionTrace | None = None

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("schema_version must not be blank")
        return stripped

    @field_validator("zomic_text")
    @classmethod
    def validate_zomic_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("zomic_text must not be blank")
        return value

    @field_validator("labels", "orbit_names")
    @classmethod
    def normalize_named_lists(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @model_validator(mode="after")
    def validate_composition(self) -> CorpusExample:
        if self.composition is None:
            return self
        total = sum(self.composition.values())
        if total <= 0.0:
            raise ValueError("composition must have a positive total")
        self.composition = {
            key: value / total for key, value in sorted(self.composition.items())
        }
        return self


class CorpusQaSummary(BaseModel):
    schema_version: str = "llm-corpus-qa-summary/v1"
    gold_count: int = 0
    silver_count: int = 0
    reject_count: int = 0
    duplicate_dropped_count: int = 0
    parse_fail_count: int = 0
    compile_fail_count: int = 0
    collision_fail_count: int = 0
    label_fail_count: int = 0


class CorpusManifest(BaseModel):
    schema_version: str = DEFAULT_CORPUS_MANIFEST_VERSION
    build_id: str
    builder_version: str = DEFAULT_BUILDER_VERSION
    build_fingerprint: str
    created_at_utc: str
    config_path: str
    syntax_count: int
    materials_count: int
    reject_count: int
    inventory_count: int
    syntax_corpus_path: str
    materials_corpus_path: str
    rejects_path: str
    inventory_path: str
    qa_path: str
    output_hashes: dict[str, str] = Field(default_factory=dict)

    @field_validator(
        "build_id",
        "build_fingerprint",
        "created_at_utc",
        "config_path",
        "syntax_corpus_path",
        "materials_corpus_path",
        "rejects_path",
        "inventory_path",
        "qa_path",
    )
    @classmethod
    def validate_non_empty_path_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped


class CorpusBuildSummary(BaseModel):
    build_id: str
    syntax_count: int
    materials_count: int
    reject_count: int
    inventory_count: int
    syntax_corpus_path: str
    materials_corpus_path: str
    rejects_path: str
    inventory_path: str
    qa_path: str
    manifest_path: str

    @field_validator(
        "build_id",
        "syntax_corpus_path",
        "materials_corpus_path",
        "rejects_path",
        "inventory_path",
        "qa_path",
        "manifest_path",
    )
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @model_validator(mode="after")
    def validate_counts(self) -> CorpusBuildSummary:
        for name in ("syntax_count", "materials_count", "reject_count", "inventory_count"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be >= 0")
        return self


class LlmGenerationRequest(BaseModel):
    system: str
    template_family: str
    composition_bounds: dict[str, CompositionBound]
    prompt_text: str
    temperature: float
    max_tokens: int
    seed_zomic_path: str | None = None

    @field_validator("system", "template_family", "prompt_text")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("seed_zomic_path")
    @classmethod
    def normalize_seed_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def validate_runtime_settings(self) -> LlmGenerationRequest:
        if not self.composition_bounds:
            raise ValueError("composition_bounds must not be empty")
        if self.temperature < 0.0:
            raise ValueError("temperature must be >= 0")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be > 0")
        return self


class LlmGenerationAttempt(BaseModel):
    schema_version: str = DEFAULT_LLM_ATTEMPT_SCHEMA_VERSION
    attempt_id: str
    adapter_key: str
    provider: str
    model: str
    temperature: float
    prompt_path: str
    raw_completion_path: str
    parse_status: ValidationStatus
    compile_status: ValidationStatus
    error_kind: str | None = None
    error_message: str | None = None

    @field_validator(
        "schema_version",
        "attempt_id",
        "adapter_key",
        "provider",
        "model",
        "prompt_path",
        "raw_completion_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("error_kind", "error_message")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, value: float) -> float:
        if value < 0.0:
            raise ValueError("temperature must be >= 0")
        return value


class LlmGenerationResult(BaseModel):
    schema_version: str = DEFAULT_LLM_RESULT_SCHEMA_VERSION
    attempt_id: str
    candidate_id: str | None = None
    orbit_library_path: str | None = None
    raw_export_path: str | None = None
    parse_status: ValidationStatus
    compile_status: ValidationStatus
    passed: bool

    @field_validator("schema_version", "attempt_id")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("candidate_id", "orbit_library_path", "raw_export_path")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class LlmRunManifest(BaseModel):
    schema_version: str = DEFAULT_LLM_RUN_MANIFEST_VERSION
    run_id: str
    system: str
    adapter_key: str
    provider: str
    model: str
    prompt_template: str
    attempt_count: int
    requested_count: int
    generated_count: int
    prompt_path: str
    attempts_path: str
    compile_results_path: str
    created_at_utc: str

    @field_validator(
        "schema_version",
        "run_id",
        "system",
        "adapter_key",
        "provider",
        "model",
        "prompt_template",
        "prompt_path",
        "attempts_path",
        "compile_results_path",
        "created_at_utc",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @model_validator(mode="after")
    def validate_counts(self) -> LlmRunManifest:
        for field_name in ("attempt_count", "requested_count", "generated_count"):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        return self


class LlmEvaluationRequest(BaseModel):
    schema_version: str = DEFAULT_LLM_EVALUATION_REQUEST_SCHEMA_VERSION
    candidate_id: str
    system: str
    template_family: str
    composition: dict[str, float]
    digital_validation: dict[str, Any]
    prompt_text: str
    temperature: float
    max_tokens: int

    @field_validator("schema_version", "candidate_id", "system", "template_family", "prompt_text")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @model_validator(mode="after")
    def validate_runtime_settings(self) -> LlmEvaluationRequest:
        if not self.composition:
            raise ValueError("composition must not be empty")
        if self.temperature < 0.0:
            raise ValueError("temperature must be >= 0")
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be > 0")
        return self


class LlmAssessment(BaseModel):
    schema_version: str = DEFAULT_LLM_ASSESSMENT_SCHEMA_VERSION
    candidate_id: str
    adapter_key: str
    provider: str
    model: str
    status: ValidationStatus
    raw_response_path: str
    synthesizability_score: float | None = None
    precursor_hints: list[str] = Field(default_factory=list)
    anomaly_flags: list[str] = Field(default_factory=list)
    literature_context: str | None = None
    rationale: str | None = None
    error_kind: str | None = None
    error_message: str | None = None

    @field_validator(
        "schema_version",
        "candidate_id",
        "adapter_key",
        "provider",
        "model",
        "raw_response_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("precursor_hints", "anomaly_flags")
    @classmethod
    def normalize_lists(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("literature_context", "rationale", "error_kind", "error_message")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("synthesizability_score")
    @classmethod
    def validate_score(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if value < 0.0 or value > 1.0:
            raise ValueError("synthesizability_score must be in [0, 1]")
        return value


class LlmEvaluationRunManifest(BaseModel):
    schema_version: str = DEFAULT_LLM_EVALUATION_RUN_MANIFEST_VERSION
    run_id: str
    system: str
    adapter_key: str
    provider: str
    model: str
    prompt_template: str
    input_path: str
    output_path: str
    requests_path: str
    assessments_path: str
    requested_count: int
    assessed_count: int
    failed_count: int
    created_at_utc: str

    @field_validator(
        "schema_version",
        "run_id",
        "system",
        "adapter_key",
        "provider",
        "model",
        "prompt_template",
        "input_path",
        "output_path",
        "requests_path",
        "assessments_path",
        "created_at_utc",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @model_validator(mode="after")
    def validate_counts(self) -> LlmEvaluationRunManifest:
        for field_name in ("requested_count", "assessed_count", "failed_count"):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        return self
