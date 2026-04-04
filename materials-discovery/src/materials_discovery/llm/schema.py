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
DEFAULT_LLM_EVAL_SET_SCHEMA_VERSION = "llm-eval-set-example/v1"
DEFAULT_LLM_EVAL_SET_MANIFEST_VERSION = "llm-eval-set-manifest/v1"
DEFAULT_LLM_ACCEPTANCE_PACK_VERSION = "llm-acceptance-pack/v1"
DEFAULT_LLM_SUGGESTION_SCHEMA_VERSION = "llm-suggestion/v1"
DEFAULT_LLM_CAMPAIGN_SUGGESTION_VERSION = "llm-campaign-suggestion/v1"
DEFAULT_LLM_CAMPAIGN_PROPOSAL_VERSION = "llm-campaign-proposal/v1"
DEFAULT_LLM_CAMPAIGN_APPROVAL_VERSION = "llm-campaign-approval/v1"
DEFAULT_LLM_CAMPAIGN_SPEC_VERSION = "llm-campaign-spec/v1"

CampaignActionFamily = Literal[
    "prompt_conditioning",
    "composition_window",
    "seed_motif_variation",
]
CampaignModelLane = Literal["general_purpose", "specialized_materials"]
CampaignDecision = Literal["approved", "rejected"]
CampaignPriority = Literal["high", "medium", "low"]
CampaignOverallStatus = Literal["ready", "needs_improvement"]
CampaignLaunchStatus = Literal["running", "succeeded", "failed"]


def _normalize_string_list(values: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        stripped = value.strip()
        if stripped and stripped not in normalized:
            normalized.append(stripped)
    return normalized


def _require_non_blank_string(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("field must not be blank")
    return stripped


def _normalize_optional_string(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


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
    example_pack_path: str | None = None
    prompt_instruction_deltas: list[str] = Field(default_factory=list)
    conditioning_example_ids: list[str] = Field(default_factory=list)

    @field_validator("system", "template_family", "prompt_text")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("seed_zomic_path", "example_pack_path")
    @classmethod
    def normalize_seed_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("conditioning_example_ids", "prompt_instruction_deltas")
    @classmethod
    def normalize_conditioning_ids(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

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
    example_pack_path: str | None = None
    prompt_instruction_deltas: list[str] = Field(default_factory=list)
    conditioning_example_ids: list[str] = Field(default_factory=list)
    campaign_id: str | None = None
    launch_id: str | None = None
    campaign_spec_path: str | None = None
    proposal_id: str | None = None
    approval_id: str | None = None
    requested_model_lanes: list[str] = Field(default_factory=list)
    resolved_model_lane: str | None = None
    resolved_model_lane_source: str | None = None
    launch_summary_path: str | None = None

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

    @field_validator(
        "example_pack_path",
        "campaign_id",
        "launch_id",
        "campaign_spec_path",
        "proposal_id",
        "approval_id",
        "resolved_model_lane",
        "resolved_model_lane_source",
        "launch_summary_path",
    )
    @classmethod
    def normalize_example_pack_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator(
        "conditioning_example_ids",
        "requested_model_lanes",
        "prompt_instruction_deltas",
    )
    @classmethod
    def normalize_conditioning_ids(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

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


class LlmEvalSetExample(BaseModel):
    schema_version: str = DEFAULT_LLM_EVAL_SET_SCHEMA_VERSION
    example_id: str
    system: str
    release_tier: ReleaseTier
    fidelity_tier: FidelityTier
    source_family: SourceFamily
    source_record_id: str
    composition: dict[str, float]
    labels: list[str] = Field(default_factory=list)
    orbit_names: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)
    zomic_text: str

    @field_validator(
        "schema_version",
        "example_id",
        "system",
        "source_record_id",
        "zomic_text",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("labels", "orbit_names", "tags")
    @classmethod
    def normalize_lists(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @model_validator(mode="after")
    def validate_composition(self) -> LlmEvalSetExample:
        if not self.composition:
            raise ValueError("composition must not be empty")
        total = sum(self.composition.values())
        if total <= 0.0:
            raise ValueError("composition must have a positive total")
        self.composition = {
            key: value / total for key, value in sorted(self.composition.items())
        }
        return self


class LlmEvalSetManifest(BaseModel):
    schema_version: str = DEFAULT_LLM_EVAL_SET_MANIFEST_VERSION
    export_id: str
    build_id: str
    created_at_utc: str
    corpus_manifest_path: str
    eval_set_path: str
    systems: list[str] = Field(default_factory=list)
    release_tiers: list[ReleaseTier] = Field(default_factory=list)
    example_count: int
    max_examples_per_system: int | None = None
    output_hashes: dict[str, str] = Field(default_factory=dict)

    @field_validator(
        "schema_version",
        "export_id",
        "build_id",
        "created_at_utc",
        "corpus_manifest_path",
        "eval_set_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("systems")
    @classmethod
    def normalize_systems(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("example_count", "max_examples_per_system")
    @classmethod
    def validate_non_negative_counts(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 0:
            raise ValueError("count fields must be >= 0")
        return value


class LlmEvalSetSummary(BaseModel):
    export_id: str
    example_count: int
    eval_set_path: str
    manifest_path: str

    @field_validator("export_id", "eval_set_path", "manifest_path")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("example_count")
    @classmethod
    def validate_example_count(cls, value: int) -> int:
        if value < 0:
            raise ValueError("example_count must be >= 0")
        return value


class LlmAcceptanceThresholds(BaseModel):
    min_parse_success_rate: float = 0.8
    min_compile_success_rate: float = 0.8
    min_generation_success_rate: float = 0.3
    min_shortlist_pass_rate: float = 0.05
    min_validation_pass_rate: float = 0.02
    min_novelty_score_mean: float = 0.0
    min_synthesizability_mean: float = 0.5

    @field_validator(
        "min_parse_success_rate",
        "min_compile_success_rate",
        "min_generation_success_rate",
        "min_shortlist_pass_rate",
        "min_validation_pass_rate",
        "min_synthesizability_mean",
    )
    @classmethod
    def validate_rate(cls, value: float) -> float:
        if value < 0.0 or value > 1.0:
            raise ValueError("rate thresholds must be in [0, 1]")
        return value

    @field_validator("min_novelty_score_mean")
    @classmethod
    def validate_novelty(cls, value: float) -> float:
        if value < 0.0:
            raise ValueError("min_novelty_score_mean must be >= 0")
        return value


class LlmAcceptanceBenchmarkInput(BaseModel):
    system: str
    generate_comparison_path: str
    pipeline_comparison_path: str
    generate_comparison: dict[str, Any]
    pipeline_comparison: dict[str, Any]

    @field_validator("system", "generate_comparison_path", "pipeline_comparison_path")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped


class LlmAcceptanceSystemMetrics(BaseModel):
    system: str
    generate_comparison_path: str
    pipeline_comparison_path: str
    parse_success_rate: float
    compile_success_rate: float
    generation_success_rate: float
    shortlist_pass_rate: float
    validation_pass_rate: float
    novelty_score_mean: float
    synthesizability_mean: float
    report_release_gate_ready: bool
    failing_metrics: list[str] = Field(default_factory=list)
    passed: bool

    @field_validator("system", "generate_comparison_path", "pipeline_comparison_path")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("failing_metrics")
    @classmethod
    def normalize_failing_metrics(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator(
        "parse_success_rate",
        "compile_success_rate",
        "generation_success_rate",
        "shortlist_pass_rate",
        "validation_pass_rate",
        "synthesizability_mean",
    )
    @classmethod
    def validate_unit_interval(cls, value: float) -> float:
        if value < 0.0 or value > 1.0:
            raise ValueError("rate metrics must be in [0, 1]")
        return value

    @field_validator("novelty_score_mean")
    @classmethod
    def validate_novelty_score(cls, value: float) -> float:
        if value < 0.0:
            raise ValueError("novelty_score_mean must be >= 0")
        return value


class LlmAcceptancePack(BaseModel):
    schema_version: str = DEFAULT_LLM_ACCEPTANCE_PACK_VERSION
    pack_id: str
    created_at_utc: str
    eval_set_manifest_path: str | None = None
    thresholds: LlmAcceptanceThresholds = Field(default_factory=LlmAcceptanceThresholds)
    systems: list[LlmAcceptanceSystemMetrics] = Field(default_factory=list)
    overall_passed: bool

    @field_validator("schema_version", "pack_id", "created_at_utc")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped

    @field_validator("eval_set_manifest_path")
    @classmethod
    def normalize_eval_set_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class LlmSuggestionItem(BaseModel):
    system: str
    priority: Literal["high", "medium", "low"]
    action: str
    rationale: str

    @field_validator("system", "action", "rationale")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped


class LlmSuggestion(BaseModel):
    schema_version: str = DEFAULT_LLM_SUGGESTION_SCHEMA_VERSION
    pack_id: str
    overall_status: Literal["ready", "needs_improvement"]
    generated_at_utc: str
    items: list[LlmSuggestionItem] = Field(default_factory=list)

    @field_validator("schema_version", "pack_id", "generated_at_utc")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field must not be blank")
        return stripped


class LlmPromptConditioningActionData(BaseModel):
    instruction_delta: str
    conditioning_strategy: str
    target_example_family: str | None = None
    preferred_max_conditioning_examples: int | None = None

    @field_validator("instruction_delta", "conditioning_strategy")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("target_example_family")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("preferred_max_conditioning_examples")
    @classmethod
    def validate_optional_count(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 1:
            raise ValueError("preferred_max_conditioning_examples must be >= 1")
        return value


class LlmCompositionWindowActionData(BaseModel):
    window_strategy: str
    focus_species: list[str]
    target_bounds: dict[str, CompositionBound] | None = None

    @field_validator("window_strategy")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("focus_species")
    @classmethod
    def normalize_focus_species(cls, values: Sequence[str]) -> list[str]:
        normalized = _normalize_string_list(values)
        if not normalized:
            raise ValueError("focus_species must not be empty")
        return normalized


class LlmSeedMotifVariationActionData(BaseModel):
    variation_strategy: str
    seed_source_hint: str | None = None
    motif_tags: list[str] = Field(default_factory=list)

    @field_validator("variation_strategy")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("seed_source_hint")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("motif_tags")
    @classmethod
    def normalize_motif_tags(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)


class LlmCampaignAction(BaseModel):
    action_id: str
    family: CampaignActionFamily
    title: str
    rationale: str
    priority: CampaignPriority
    evidence_metrics: list[str] = Field(default_factory=list)
    preferred_model_lane: CampaignModelLane
    preferred_provider: str | None = None
    preferred_model: str | None = None
    specialized_model_family: str | None = None
    prompt_conditioning: LlmPromptConditioningActionData | None = None
    composition_window: LlmCompositionWindowActionData | None = None
    seed_motif_variation: LlmSeedMotifVariationActionData | None = None

    @field_validator("action_id", "title", "rationale")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("evidence_metrics")
    @classmethod
    def normalize_metrics(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("preferred_provider", "preferred_model", "specialized_model_family")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @model_validator(mode="after")
    def validate_family_payload(self) -> LlmCampaignAction:
        payload_by_family = {
            "prompt_conditioning": self.prompt_conditioning,
            "composition_window": self.composition_window,
            "seed_motif_variation": self.seed_motif_variation,
        }
        if payload_by_family[self.family] is None:
            raise ValueError(f"{self.family} payload is required")
        for family, payload in payload_by_family.items():
            if family != self.family and payload is not None:
                raise ValueError(f"{family} payload must be omitted for {self.family} actions")
        return self


class LlmCampaignProposal(BaseModel):
    schema_version: str = DEFAULT_LLM_CAMPAIGN_PROPOSAL_VERSION
    proposal_id: str
    pack_id: str
    system: str
    generated_at_utc: str
    acceptance_pack_path: str
    eval_set_manifest_path: str | None = None
    generate_comparison_path: str
    pipeline_comparison_path: str
    overall_status: CampaignOverallStatus
    priority: CampaignPriority
    failing_metrics: list[str] = Field(default_factory=list)
    actions: list[LlmCampaignAction] = Field(default_factory=list)

    @field_validator(
        "schema_version",
        "proposal_id",
        "pack_id",
        "system",
        "generated_at_utc",
        "acceptance_pack_path",
        "generate_comparison_path",
        "pipeline_comparison_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("eval_set_manifest_path")
    @classmethod
    def normalize_optional_path(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("failing_metrics")
    @classmethod
    def normalize_failing_metrics(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @model_validator(mode="after")
    def validate_actions(self) -> LlmCampaignProposal:
        if not self.actions:
            raise ValueError("campaign proposals must contain at least one action")
        return self


class LlmCampaignProposalSummary(BaseModel):
    proposal_id: str
    system: str
    priority: CampaignPriority
    failing_metrics: list[str] = Field(default_factory=list)
    action_families: list[CampaignActionFamily] = Field(default_factory=list)
    proposal_path: str

    @field_validator("proposal_id", "system", "proposal_path")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("failing_metrics")
    @classmethod
    def normalize_failing_metrics(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("action_families")
    @classmethod
    def normalize_action_families(
        cls,
        values: Sequence[CampaignActionFamily],
    ) -> list[CampaignActionFamily]:
        normalized: list[CampaignActionFamily] = []
        for value in values:
            if value not in normalized:
                normalized.append(value)
        return normalized


class LlmCampaignSuggestion(BaseModel):
    schema_version: str = DEFAULT_LLM_CAMPAIGN_SUGGESTION_VERSION
    pack_id: str
    overall_status: CampaignOverallStatus
    generated_at_utc: str
    proposal_count: int
    proposals: list[LlmCampaignProposalSummary] = Field(default_factory=list)

    @field_validator("schema_version", "pack_id", "generated_at_utc")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("proposal_count")
    @classmethod
    def validate_proposal_count(cls, value: int) -> int:
        if value < 0:
            raise ValueError("proposal_count must be >= 0")
        return value

    @model_validator(mode="after")
    def validate_summary_count(self) -> LlmCampaignSuggestion:
        if self.proposal_count != len(self.proposals):
            raise ValueError("proposal_count must equal the number of proposals")
        return self


class LlmCampaignApproval(BaseModel):
    schema_version: str = DEFAULT_LLM_CAMPAIGN_APPROVAL_VERSION
    approval_id: str
    proposal_id: str
    proposal_path: str
    decision: CampaignDecision
    operator: str
    decided_at_utc: str
    notes: str | None = None
    campaign_id: str | None = None

    @field_validator(
        "schema_version",
        "approval_id",
        "proposal_id",
        "proposal_path",
        "operator",
        "decided_at_utc",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("notes", "campaign_id")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @model_validator(mode="after")
    def validate_campaign_decision(self) -> LlmCampaignApproval:
        if self.decision == "approved" and self.campaign_id is None:
            raise ValueError("approved decisions require a campaign_id")
        if self.decision == "rejected" and self.campaign_id is not None:
            raise ValueError("rejected decisions must not set campaign_id")
        return self


class LlmCampaignLaunchBaseline(BaseModel):
    system_config_path: str
    system_config_hash: str
    system: str
    template_family: str
    default_count: int
    composition_bounds: dict[str, CompositionBound]
    prompt_template: str | None = None
    example_pack_path: str | None = None
    max_conditioning_examples: int | None = None
    seed_zomic_path: str | None = None

    @field_validator("system_config_path", "system_config_hash", "system", "template_family")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("prompt_template", "example_pack_path", "seed_zomic_path")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("default_count")
    @classmethod
    def validate_default_count(cls, value: int) -> int:
        if value < 1:
            raise ValueError("default_count must be >= 1")
        return value

    @field_validator("max_conditioning_examples")
    @classmethod
    def validate_max_conditioning_examples(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 1:
            raise ValueError("max_conditioning_examples must be >= 1")
        return value

    @model_validator(mode="after")
    def validate_composition_bounds(self) -> LlmCampaignLaunchBaseline:
        if not self.composition_bounds:
            raise ValueError("composition_bounds must not be empty")
        return self


class LlmCampaignLineage(BaseModel):
    acceptance_pack_path: str
    eval_set_manifest_path: str | None = None
    proposal_path: str
    approval_path: str
    source_system_config_path: str
    source_system_config_hash: str

    @field_validator(
        "acceptance_pack_path",
        "proposal_path",
        "approval_path",
        "source_system_config_path",
        "source_system_config_hash",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("eval_set_manifest_path")
    @classmethod
    def normalize_optional_path(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)


class LlmCampaignSpec(BaseModel):
    schema_version: str = DEFAULT_LLM_CAMPAIGN_SPEC_VERSION
    campaign_id: str
    proposal_id: str
    approval_id: str
    system: str
    created_at_utc: str
    actions: list[LlmCampaignAction] = Field(default_factory=list)
    launch_baseline: LlmCampaignLaunchBaseline
    lineage: LlmCampaignLineage

    @field_validator(
        "schema_version",
        "campaign_id",
        "proposal_id",
        "approval_id",
        "system",
        "created_at_utc",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @model_validator(mode="after")
    def validate_spec(self) -> LlmCampaignSpec:
        if not self.actions:
            raise ValueError("campaign specs must contain at least one action")
        if self.system != self.launch_baseline.system:
            raise ValueError("campaign spec system must match launch baseline system")
        return self


class LlmCampaignResolvedLaunch(BaseModel):
    launch_id: str
    campaign_id: str
    campaign_spec_path: str
    system_config_path: str
    system_config_hash: str
    requested_model_lanes: list[str] = Field(default_factory=list)
    resolved_model_lane: str
    resolved_model_lane_source: Literal["configured_lane", "baseline_fallback"]
    resolved_adapter: str
    resolved_provider: str
    resolved_model: str
    prompt_instruction_deltas: list[str] = Field(default_factory=list)
    resolved_composition_bounds: dict[str, CompositionBound]
    resolved_example_pack_path: str | None = None
    resolved_seed_zomic_path: str | None = None

    @field_validator(
        "launch_id",
        "campaign_id",
        "campaign_spec_path",
        "system_config_path",
        "system_config_hash",
        "resolved_model_lane",
        "resolved_adapter",
        "resolved_provider",
        "resolved_model",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("requested_model_lanes", "prompt_instruction_deltas")
    @classmethod
    def normalize_string_lists(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("resolved_example_pack_path", "resolved_seed_zomic_path")
    @classmethod
    def normalize_optional_paths(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @model_validator(mode="after")
    def validate_composition_bounds(self) -> LlmCampaignResolvedLaunch:
        if not self.resolved_composition_bounds:
            raise ValueError("resolved_composition_bounds must not be empty")
        return self


class LlmCampaignLaunchSummary(BaseModel):
    launch_id: str
    campaign_id: str
    campaign_spec_path: str
    proposal_id: str
    approval_id: str
    system: str
    status: CampaignLaunchStatus
    created_at_utc: str
    requested_count: int
    requested_model_lanes: list[str] = Field(default_factory=list)
    resolved_model_lane: str
    resolved_model_lane_source: Literal["configured_lane", "baseline_fallback"]
    resolved_launch_path: str
    run_manifest_path: str | None = None
    llm_generate_manifest_path: str | None = None
    candidates_path: str | None = None
    error_kind: str | None = None
    error_message: str | None = None

    @field_validator(
        "launch_id",
        "campaign_id",
        "campaign_spec_path",
        "proposal_id",
        "approval_id",
        "system",
        "created_at_utc",
        "resolved_model_lane",
        "resolved_launch_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("requested_model_lanes")
    @classmethod
    def normalize_requested_model_lanes(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator(
        "run_manifest_path",
        "llm_generate_manifest_path",
        "candidates_path",
        "error_kind",
        "error_message",
    )
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("requested_count")
    @classmethod
    def validate_requested_count(cls, value: int) -> int:
        if value < 0:
            raise ValueError("requested_count must be >= 0")
        return value
