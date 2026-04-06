from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from materials_discovery.common.schema import CompositionBound, Position3D

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
TranslationFidelityTier = Literal["exact", "anchored", "approximate", "lossy"]
TranslationTargetFamily = Literal["cif", "material_string"]
TranslationTargetFormat = Literal["cif_text", "crystaltextllm_material_string"]
TranslationEmissionKind = Literal["file", "line_oriented"]
TranslationLossReason = Literal[
    "aperiodic_to_periodic_proxy",
    "coordinate_derivation_required",
    "qc_semantics_dropped",
    "unsupported_exactness_claim",
]
TranslationDiagnosticCode = Literal[
    "coordinate_derivation_required",
    "periodic_proxy_required",
    "qc_semantics_dropped",
    "unsupported_exactness_claim",
]
TranslationDiagnosticSeverity = Literal["info", "warning", "error"]
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
DEFAULT_LLM_CHECKPOINT_REGISTRATION_VERSION = "llm-checkpoint-registration/v1"
DEFAULT_LLM_CHECKPOINT_LIFECYCLE_INDEX_VERSION = "llm-checkpoint-lifecycle-index/v1"
DEFAULT_LLM_CHECKPOINT_PROMOTION_SPEC_VERSION = "llm-checkpoint-promotion/v1"
DEFAULT_LLM_CHECKPOINT_RETIREMENT_SPEC_VERSION = "llm-checkpoint-retirement/v1"
DEFAULT_LLM_CHECKPOINT_PIN_SELECTION_VERSION = "llm-checkpoint-pin-selection/v1"
DEFAULT_LLM_SUGGESTION_SCHEMA_VERSION = "llm-suggestion/v1"
DEFAULT_LLM_CAMPAIGN_SUGGESTION_VERSION = "llm-campaign-suggestion/v1"
DEFAULT_LLM_CAMPAIGN_PROPOSAL_VERSION = "llm-campaign-proposal/v1"
DEFAULT_LLM_CAMPAIGN_APPROVAL_VERSION = "llm-campaign-approval/v1"
DEFAULT_LLM_CAMPAIGN_SPEC_VERSION = "llm-campaign-spec/v1"
DEFAULT_LLM_OUTCOME_SNAPSHOT_VERSION = "llm-campaign-outcome-snapshot/v1"
DEFAULT_LLM_CAMPAIGN_COMPARISON_VERSION = "llm-campaign-comparison/v1"
DEFAULT_TRANSLATED_STRUCTURE_SCHEMA_VERSION = "translated-structure-artifact/v1"

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
CheckpointAdaptationMethod = Literal["lora", "qlora", "merge", "full_finetune", "manual"]
CheckpointLifecycleState = Literal["candidate", "promoted", "retired"]
CheckpointBenchmarkRole = Literal[
    "baseline_local",
    "promoted_default",
    "candidate_checkpoint",
]
CheckpointPinSource = Literal["manual", "campaign"]
CheckpointRetirementReason = Literal["superseded", "invalidated", "operator_request", "obsolete"]
CheckpointSelectionSource = Literal[
    "legacy_checkpoint_id",
    "family_explicit_pin",
    "family_promoted_default",
]
ResolvedModelLaneSource = Literal[
    "configured_lane",
    "default_lane",
    "configured_fallback",
    "backend_default",
    "baseline_fallback",
]

OUTCOME_METRIC_KEYS = (
    "parse_success_rate",
    "compile_success_rate",
    "generation_success_rate",
    "shortlist_pass_rate",
    "validation_pass_rate",
    "novelty_score_mean",
    "synthesizability_mean",
    "report_release_gate_ready",
)


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


class TranslatedStructureSourceReference(BaseModel):
    source_kind: Literal["candidate_record"] = "candidate_record"
    candidate_id: str
    system: str | None = None
    template_family: str | None = None
    provenance_hints: dict[str, Any] = Field(default_factory=dict)

    @field_validator("candidate_id")
    @classmethod
    def validate_candidate_id(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("system", "template_family")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("provenance_hints")
    @classmethod
    def validate_provenance_hints(cls, value: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, hint_value in value.items():
            normalized[_require_non_blank_string(key)] = hint_value
        return normalized


class TranslationTargetDescriptor(BaseModel):
    family: TranslationTargetFamily
    target_format: TranslationTargetFormat
    requires_periodic_cell: bool
    requires_fractional_coordinates: bool = True
    preserves_qc_native_semantics: bool
    emission_kind: TranslationEmissionKind
    description: str | None = None

    @field_validator("description")
    @classmethod
    def normalize_optional_description(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)


class TranslatedStructureSite(BaseModel):
    label: str
    species: str
    occupancy: float
    fractional_position: Position3D | None = None
    cartesian_position: Position3D | None = None

    @field_validator("label", "species")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("occupancy")
    @classmethod
    def validate_occupancy(cls, value: float) -> float:
        if value < 0.0 or value > 1.0:
            raise ValueError("occupancy must be in [0, 1]")
        return value


class TranslatedStructureDiagnostic(BaseModel):
    code: TranslationDiagnosticCode
    severity: TranslationDiagnosticSeverity = "warning"
    message: str
    site_label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("message", "site_label")
    @classmethod
    def normalize_string_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _require_non_blank_string(value)

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            normalized[_require_non_blank_string(key)] = item
        return normalized


class TranslatedStructureArtifact(BaseModel):
    schema_version: str = DEFAULT_TRANSLATED_STRUCTURE_SCHEMA_VERSION
    source: TranslatedStructureSourceReference
    target: TranslationTargetDescriptor
    fidelity_tier: TranslationFidelityTier
    loss_reasons: list[TranslationLossReason] = Field(default_factory=list)
    composition: dict[str, float] = Field(default_factory=dict)
    cell: dict[str, float] | None = None
    sites: list[TranslatedStructureSite] = Field(default_factory=list)
    diagnostics: list[TranslatedStructureDiagnostic] = Field(default_factory=list)
    emitted_text: str | None = None

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("emitted_text")
    @classmethod
    def normalize_emitted_text(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("composition")
    @classmethod
    def validate_composition(cls, value: dict[str, float]) -> dict[str, float]:
        if not value:
            return value
        total = sum(value.values())
        if total <= 0.0:
            raise ValueError("composition must have positive total")
        return {key: amount / total for key, amount in sorted(value.items())}

    @field_validator("cell")
    @classmethod
    def validate_cell(cls, value: dict[str, float] | None) -> dict[str, float] | None:
        if value is None:
            return None
        normalized: dict[str, float] = {}
        for key, amount in value.items():
            normalized[_require_non_blank_string(key)] = float(amount)
        return normalized

    @model_validator(mode="after")
    def validate_loss_semantics(self) -> TranslatedStructureArtifact:
        if self.fidelity_tier == "lossy" and not self.loss_reasons:
            raise ValueError("loss_reasons are required when fidelity_tier is lossy")
        return self


BUILTIN_TRANSLATION_TARGETS: tuple[TranslationTargetDescriptor, ...] = (
    TranslationTargetDescriptor(
        family="cif",
        target_format="cif_text",
        requires_periodic_cell=True,
        requires_fractional_coordinates=True,
        preserves_qc_native_semantics=False,
        emission_kind="file",
        description="Periodic CIF export for downstream crystal-LLM workflows.",
    ),
    TranslationTargetDescriptor(
        family="material_string",
        target_format="crystaltextllm_material_string",
        requires_periodic_cell=True,
        requires_fractional_coordinates=True,
        preserves_qc_native_semantics=False,
        emission_kind="line_oriented",
        description="Line-oriented material-string export for CrystalTextLLM-style workflows.",
    ),
)

_BUILTIN_TRANSLATION_TARGETS_BY_FAMILY = {
    descriptor.family: descriptor for descriptor in BUILTIN_TRANSLATION_TARGETS
}


def list_translation_targets() -> tuple[TranslationTargetDescriptor, ...]:
    return BUILTIN_TRANSLATION_TARGETS


def resolve_translation_target(target_family: str) -> TranslationTargetDescriptor:
    normalized_family = _require_non_blank_string(target_family)
    descriptor = _BUILTIN_TRANSLATION_TARGETS_BY_FAMILY.get(normalized_family)
    if descriptor is None:
        raise KeyError(f"unknown translation target family: {normalized_family}")
    return descriptor


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


class LlmCheckpointLineage(BaseModel):
    checkpoint_id: str
    checkpoint_family: str | None = None
    registration_path: str
    fingerprint: str
    base_model: str
    base_model_revision: str | None = None
    adaptation_method: CheckpointAdaptationMethod
    adaptation_artifact_path: str
    corpus_manifest_path: str
    eval_set_manifest_path: str
    acceptance_pack_path: str | None = None

    @field_validator(
        "checkpoint_id",
        "registration_path",
        "fingerprint",
        "base_model",
        "adaptation_artifact_path",
        "corpus_manifest_path",
        "eval_set_manifest_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = _require_non_blank_string(value)
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized

    @field_validator("checkpoint_family", "base_model_revision", "acceptance_pack_path")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_string(value)
        if normalized is None:
            return None
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized


class LlmCheckpointRegistrationSpec(BaseModel):
    checkpoint_id: str
    checkpoint_family: str | None = None
    system: str
    template_family: str
    adapter: str
    provider: str
    model: str
    local_model_path: str
    model_revision: str | None = None
    base_model: str
    base_model_revision: str | None = None
    adaptation_method: CheckpointAdaptationMethod
    adaptation_artifact_path: str
    corpus_manifest_path: str
    eval_set_manifest_path: str
    acceptance_pack_path: str | None = None
    notes: str | None = None

    @field_validator(
        "checkpoint_id",
        "system",
        "template_family",
        "adapter",
        "provider",
        "model",
        "local_model_path",
        "base_model",
        "adaptation_artifact_path",
        "corpus_manifest_path",
        "eval_set_manifest_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = _require_non_blank_string(value)
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized

    @field_validator(
        "checkpoint_family",
        "model_revision",
        "base_model_revision",
        "acceptance_pack_path",
        "notes",
    )
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_string(value)
        if normalized is None:
            return None
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized


class LlmCheckpointRegistration(BaseModel):
    schema_version: str = DEFAULT_LLM_CHECKPOINT_REGISTRATION_VERSION
    checkpoint_id: str
    checkpoint_family: str | None = None
    system: str
    template_family: str
    created_at_utc: str
    adapter: str
    provider: str
    model: str
    local_model_path: str
    model_revision: str | None = None
    fingerprint: str
    base_model: str
    base_model_revision: str | None = None
    adaptation_method: CheckpointAdaptationMethod
    adaptation_artifact_path: str
    corpus_manifest_path: str
    eval_set_manifest_path: str
    acceptance_pack_path: str | None = None
    notes: str | None = None

    @field_validator(
        "schema_version",
        "checkpoint_id",
        "system",
        "template_family",
        "created_at_utc",
        "adapter",
        "provider",
        "model",
        "local_model_path",
        "fingerprint",
        "base_model",
        "adaptation_artifact_path",
        "corpus_manifest_path",
        "eval_set_manifest_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = _require_non_blank_string(value)
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized

    @field_validator(
        "checkpoint_family",
        "model_revision",
        "base_model_revision",
        "acceptance_pack_path",
        "notes",
    )
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_string(value)
        if normalized is None:
            return None
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized


class LlmCheckpointRegistrationSummary(BaseModel):
    checkpoint_id: str
    checkpoint_family: str | None = None
    fingerprint: str
    registration_path: str

    @field_validator("checkpoint_id", "fingerprint", "registration_path")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = _require_non_blank_string(value)
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized

    @field_validator("checkpoint_family")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)


class LlmCheckpointLifecycleMemberSummary(BaseModel):
    checkpoint_id: str
    fingerprint: str
    registration_path: str
    lifecycle_state: CheckpointLifecycleState = "candidate"
    registered_at_utc: str | None = None
    promoted_at_utc: str | None = None
    retired_at_utc: str | None = None
    retirement_reason: CheckpointRetirementReason | None = None
    last_action_path: str | None = None

    @field_validator("checkpoint_id", "fingerprint", "registration_path")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = _require_non_blank_string(value)
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized

    @field_validator(
        "registered_at_utc",
        "promoted_at_utc",
        "retired_at_utc",
        "last_action_path",
    )
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_string(value)
        if normalized is None:
            return None
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized

    @model_validator(mode="after")
    def validate_retirement_state(self) -> LlmCheckpointLifecycleMemberSummary:
        if self.lifecycle_state == "retired":
            if self.retirement_reason is None:
                raise ValueError("retired members must record retirement_reason")
            return self
        if self.retired_at_utc is not None or self.retirement_reason is not None:
            raise ValueError("only retired members may record retirement metadata")
        return self


class LlmCheckpointLifecycleIndex(BaseModel):
    schema_version: str = DEFAULT_LLM_CHECKPOINT_LIFECYCLE_INDEX_VERSION
    checkpoint_family: str
    revision: int = 0
    promoted_checkpoint_id: str | None = None
    members: list[LlmCheckpointLifecycleMemberSummary] = Field(default_factory=list)
    action_history_paths: list[str] = Field(default_factory=list)

    @field_validator("schema_version", "checkpoint_family")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("promoted_checkpoint_id")
    @classmethod
    def normalize_optional_checkpoint_id(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("revision")
    @classmethod
    def validate_revision(cls, value: int) -> int:
        if value < 0:
            raise ValueError("revision must be >= 0")
        return value

    @field_validator("action_history_paths")
    @classmethod
    def normalize_action_history_paths(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @model_validator(mode="after")
    def validate_member_state(self) -> LlmCheckpointLifecycleIndex:
        member_ids = [member.checkpoint_id for member in self.members]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("members must be unique by checkpoint_id")

        promoted_members = [
            member.checkpoint_id
            for member in self.members
            if member.lifecycle_state == "promoted"
        ]
        if len(promoted_members) > 1:
            raise ValueError("only one member may be promoted per checkpoint family")
        if self.promoted_checkpoint_id is None and promoted_members:
            raise ValueError("promoted_checkpoint_id must be set when a promoted member exists")
        if self.promoted_checkpoint_id is not None:
            if self.promoted_checkpoint_id not in member_ids:
                raise ValueError("promoted_checkpoint_id must reference a known family member")
            if promoted_members != [self.promoted_checkpoint_id]:
                raise ValueError(
                    "promoted member lifecycle_state must match promoted_checkpoint_id"
                )
        return self


class LlmCheckpointPromotionSpec(BaseModel):
    schema_version: str = DEFAULT_LLM_CHECKPOINT_PROMOTION_SPEC_VERSION
    checkpoint_family: str
    checkpoint_id: str
    evidence_paths: list[str] = Field(default_factory=list)
    expected_revision: int | None = None
    expected_promoted_checkpoint_id: str | None = None
    note: str | None = None

    @field_validator("schema_version", "checkpoint_family", "checkpoint_id")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        normalized = _require_non_blank_string(value)
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized

    @field_validator("evidence_paths")
    @classmethod
    def validate_evidence_paths(cls, values: Sequence[str]) -> list[str]:
        normalized = _normalize_string_list(values)
        if not normalized:
            raise ValueError("evidence_paths must contain at least one repo-relative path")
        return normalized

    @field_validator("expected_revision")
    @classmethod
    def validate_expected_revision(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("expected_revision must be >= 0")
        return value

    @field_validator("expected_promoted_checkpoint_id", "note")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)


class LlmCheckpointRetirementSpec(BaseModel):
    schema_version: str = DEFAULT_LLM_CHECKPOINT_RETIREMENT_SPEC_VERSION
    checkpoint_family: str
    checkpoint_id: str
    reason: CheckpointRetirementReason
    expected_revision: int | None = None
    expected_promoted_checkpoint_id: str | None = None
    replacement_checkpoint_id: str | None = None
    note: str | None = None

    @field_validator("schema_version", "checkpoint_family", "checkpoint_id")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("expected_revision")
    @classmethod
    def validate_expected_revision(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("expected_revision must be >= 0")
        return value

    @field_validator("expected_promoted_checkpoint_id", "replacement_checkpoint_id", "note")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @model_validator(mode="after")
    def validate_replacement_checkpoint(self) -> LlmCheckpointRetirementSpec:
        if self.replacement_checkpoint_id == self.checkpoint_id:
            raise ValueError("replacement_checkpoint_id must differ from checkpoint_id")
        return self


class LlmCheckpointPinSelectionSpec(BaseModel):
    schema_version: str = DEFAULT_LLM_CHECKPOINT_PIN_SELECTION_VERSION
    checkpoint_family: str
    checkpoint_id: str
    selection_source: CheckpointPinSource
    campaign_id: str | None = None
    note: str | None = None

    @field_validator("schema_version", "checkpoint_family", "checkpoint_id")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("campaign_id", "note")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @model_validator(mode="after")
    def validate_selection_source(self) -> LlmCheckpointPinSelectionSpec:
        if self.selection_source == "campaign" and self.campaign_id is None:
            raise ValueError("campaign pin selections must include campaign_id")
        if self.selection_source == "manual" and self.campaign_id is not None:
            raise ValueError("manual pin selections cannot include campaign_id")
        return self


class LlmServingIdentity(BaseModel):
    requested_model_lane: str | None = None
    resolved_model_lane: str
    resolved_model_lane_source: ResolvedModelLaneSource
    adapter: str
    provider: str
    model: str
    effective_api_base: str | None = None
    checkpoint_id: str | None = None
    model_revision: str | None = None
    local_model_path: str | None = None
    checkpoint_lineage: LlmCheckpointLineage | None = None
    checkpoint_selection_source: CheckpointSelectionSource | None = None
    checkpoint_lifecycle_path: str | None = None
    checkpoint_lifecycle_revision: int | None = None

    @field_validator(
        "resolved_model_lane",
        "adapter",
        "provider",
        "model",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator(
        "requested_model_lane",
        "effective_api_base",
        "checkpoint_id",
        "model_revision",
        "local_model_path",
        "checkpoint_lifecycle_path",
    )
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_string(value)
        if normalized is None:
            return None
        if normalized.startswith("http://") or normalized.startswith("https://"):
            return normalized.rstrip("/")
        return normalized

    @field_validator("checkpoint_lifecycle_revision")
    @classmethod
    def validate_checkpoint_lifecycle_revision(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("checkpoint_lifecycle_revision must be >= 0")
        return value

    @model_validator(mode="after")
    def validate_checkpoint_selection_contract(self) -> LlmServingIdentity:
        if self.checkpoint_selection_source is None:
            if (
                self.checkpoint_lifecycle_path is not None
                or self.checkpoint_lifecycle_revision is not None
            ):
                raise ValueError(
                    "checkpoint lifecycle metadata requires checkpoint_selection_source"
                )
            return self

        if self.checkpoint_id is None:
            raise ValueError("checkpoint_selection_source requires checkpoint_id")

        if self.checkpoint_selection_source == "legacy_checkpoint_id":
            if (
                self.checkpoint_lifecycle_path is not None
                or self.checkpoint_lifecycle_revision is not None
            ):
                raise ValueError(
                    "legacy checkpoint selection cannot record lifecycle metadata"
                )
            return self

        if self.checkpoint_lineage is None or self.checkpoint_lineage.checkpoint_family is None:
            raise ValueError(
                "family checkpoint selection requires checkpoint_lineage with checkpoint_family"
            )
        if (
            self.checkpoint_lifecycle_path is None
            or self.checkpoint_lifecycle_revision is None
        ):
            raise ValueError("family checkpoint selection requires lifecycle path and revision")
        return self


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
    resolved_model_lane_source: ResolvedModelLaneSource | None = None
    serving_identity: LlmServingIdentity | None = None
    launch_summary_path: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    max_attempts: int | None = None
    seed_zomic_path: str | None = None
    replay_of_launch_id: str | None = None
    replay_of_launch_summary_path: str | None = None

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
        "launch_summary_path",
        "seed_zomic_path",
        "replay_of_launch_id",
        "replay_of_launch_summary_path",
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
        if self.temperature is not None and self.temperature < 0.0:
            raise ValueError("temperature must be >= 0")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens must be > 0")
        if self.max_attempts is not None and self.max_attempts <= 0:
            raise ValueError("max_attempts must be > 0")
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
    requested_model_lanes: list[str] = Field(default_factory=list)
    resolved_model_lane: str | None = None
    resolved_model_lane_source: ResolvedModelLaneSource | None = None
    serving_identity: LlmServingIdentity | None = None
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

    @field_validator("precursor_hints", "anomaly_flags", "requested_model_lanes")
    @classmethod
    def normalize_lists(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator(
        "resolved_model_lane",
        "literature_context",
        "rationale",
        "error_kind",
        "error_message",
    )
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
    requested_model_lanes: list[str] = Field(default_factory=list)
    resolved_model_lane: str | None = None
    resolved_model_lane_source: ResolvedModelLaneSource | None = None
    serving_identity: LlmServingIdentity | None = None

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

    @field_validator("requested_model_lanes")
    @classmethod
    def normalize_requested_model_lanes(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("resolved_model_lane")
    @classmethod
    def normalize_optional_lane(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

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
    resolved_model_lane_source: ResolvedModelLaneSource
    resolved_adapter: str
    resolved_provider: str
    resolved_model: str
    serving_identity: LlmServingIdentity | None = None
    prompt_instruction_deltas: list[str] = Field(default_factory=list)
    resolved_composition_bounds: dict[str, CompositionBound]
    resolved_example_pack_path: str | None = None
    resolved_seed_zomic_path: str | None = None
    effective_candidates_path: str | None = None
    output_override_used: bool = False
    replay_of_launch_id: str | None = None
    replay_of_launch_summary_path: str | None = None
    current_system_config_hash: str | None = None

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

    @field_validator(
        "resolved_example_pack_path",
        "resolved_seed_zomic_path",
        "effective_candidates_path",
        "replay_of_launch_summary_path",
        "current_system_config_hash",
    )
    @classmethod
    def normalize_optional_paths(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("replay_of_launch_id")
    @classmethod
    def normalize_optional_replay_launch_id(cls, value: str | None) -> str | None:
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
    resolved_model_lane_source: ResolvedModelLaneSource
    serving_identity: LlmServingIdentity | None = None
    resolved_launch_path: str
    run_manifest_path: str | None = None
    llm_generate_manifest_path: str | None = None
    candidates_path: str | None = None
    error_kind: str | None = None
    error_message: str | None = None
    replay_of_launch_id: str | None = None
    replay_of_launch_summary_path: str | None = None
    current_system_config_hash: str | None = None

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
        "replay_of_launch_id",
        "replay_of_launch_summary_path",
        "current_system_config_hash",
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


class LlmCampaignOutcomeSnapshot(BaseModel):
    schema_version: str = DEFAULT_LLM_OUTCOME_SNAPSHOT_VERSION
    campaign_id: str
    launch_id: str
    system: str
    launch_summary_path: str
    campaign_spec_path: str
    acceptance_pack_path: str
    requested_model_lanes: list[str] = Field(default_factory=list)
    resolved_model_lane: str
    resolved_model_lane_source: str
    evaluation_requested_model_lanes: list[str] = Field(default_factory=list)
    evaluation_resolved_model_lane: str | None = None
    evaluation_resolved_model_lane_source: ResolvedModelLaneSource | None = None
    evaluation_serving_identity: LlmServingIdentity | None = None
    parse_success_rate: float
    compile_success_rate: float
    generation_success_rate: float
    shortlist_pass_rate: float | None = None
    validation_pass_rate: float | None = None
    novelty_score_mean: float | None = None
    synthesizability_mean: float | None = None
    report_release_gate_ready: bool | None = None
    missing_metrics: list[str] = Field(default_factory=list)
    stage_manifest_paths: dict[str, str] = Field(default_factory=dict)

    @field_validator(
        "schema_version",
        "campaign_id",
        "launch_id",
        "system",
        "launch_summary_path",
        "campaign_spec_path",
        "acceptance_pack_path",
        "resolved_model_lane",
        "resolved_model_lane_source",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("requested_model_lanes", "evaluation_requested_model_lanes")
    @classmethod
    def normalize_requested_model_lanes(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("evaluation_resolved_model_lane")
    @classmethod
    def normalize_optional_evaluation_lane(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("missing_metrics")
    @classmethod
    def normalize_missing_metrics(cls, values: Sequence[str]) -> list[str]:
        normalized = _normalize_string_list(values)
        invalid = [value for value in normalized if value not in OUTCOME_METRIC_KEYS]
        if invalid:
            raise ValueError(f"unsupported missing_metrics keys: {', '.join(invalid)}")
        return normalized

    @field_validator("stage_manifest_paths")
    @classmethod
    def validate_stage_manifest_paths(cls, value: dict[str, str]) -> dict[str, str]:
        out: dict[str, str] = {}
        for key, path in value.items():
            normalized_key = _require_non_blank_string(key)
            normalized_path = _require_non_blank_string(path)
            out[normalized_key] = normalized_path
        return out

    @model_validator(mode="after")
    def validate_metrics(self) -> LlmCampaignOutcomeSnapshot:
        for field_name in (
            "parse_success_rate",
            "compile_success_rate",
            "generation_success_rate",
            "shortlist_pass_rate",
            "validation_pass_rate",
            "novelty_score_mean",
            "synthesizability_mean",
        ):
            value = getattr(self, field_name)
            if value is not None and value < 0.0:
                raise ValueError(f"{field_name} must be >= 0")
        return self


class LlmCampaignComparisonResult(BaseModel):
    schema_version: str = DEFAULT_LLM_CAMPAIGN_COMPARISON_VERSION
    comparison_id: str
    campaign_id: str
    launch_id: str
    system: str
    generated_at_utc: str
    current_outcome: LlmCampaignOutcomeSnapshot
    acceptance_baseline: LlmAcceptanceSystemMetrics
    prior_outcome: LlmCampaignOutcomeSnapshot | None = None
    delta_vs_acceptance: dict[str, float] = Field(default_factory=dict)
    delta_vs_prior: dict[str, float] = Field(default_factory=dict)
    summary_lines: list[str] = Field(default_factory=list)

    @field_validator(
        "schema_version",
        "comparison_id",
        "campaign_id",
        "launch_id",
        "system",
        "generated_at_utc",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("summary_lines")
    @classmethod
    def normalize_summary_lines(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("delta_vs_acceptance", "delta_vs_prior")
    @classmethod
    def validate_delta_maps(cls, value: dict[str, float]) -> dict[str, float]:
        out: dict[str, float] = {}
        for key, metric in value.items():
            normalized_key = _require_non_blank_string(key)
            if normalized_key not in OUTCOME_METRIC_KEYS:
                raise ValueError(f"unsupported delta metric key: {normalized_key}")
            out[normalized_key] = float(metric)
        return out

    @model_validator(mode="after")
    def validate_system_alignment(self) -> LlmCampaignComparisonResult:
        if self.current_outcome.system != self.system:
            raise ValueError("current_outcome system must match comparison system")
        if self.acceptance_baseline.system != self.system:
            raise ValueError("acceptance_baseline system must match comparison system")
        if self.prior_outcome is not None and self.prior_outcome.system != self.system:
            raise ValueError("prior_outcome system must match comparison system")
        return self


class LlmServingBenchmarkTarget(BaseModel):
    target_id: str
    label: str
    workflow_role: Literal["campaign_launch", "llm_evaluate"]
    checkpoint_benchmark_role: CheckpointBenchmarkRole | None = None
    system_config_path: str
    campaign_spec_path: str | None = None
    batch: str | None = None
    generation_model_lane: CampaignModelLane | None = None
    evaluation_model_lane: CampaignModelLane | None = None
    estimated_cost_usd: float
    operator_friction_tier: Literal["low", "medium", "high"]
    allow_fallback: bool = False
    notes: str | None = None

    @field_validator(
        "target_id",
        "label",
        "system_config_path",
    )
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("campaign_spec_path", "batch", "notes")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @model_validator(mode="after")
    def validate_target_configuration(self) -> LlmServingBenchmarkTarget:
        if self.estimated_cost_usd < 0.0:
            raise ValueError("estimated_cost_usd must be >= 0")
        if self.workflow_role == "campaign_launch" and self.campaign_spec_path is None:
            raise ValueError("campaign_spec_path is required for campaign_launch targets")
        if self.workflow_role == "llm_evaluate" and self.batch is None:
            raise ValueError("batch is required for llm_evaluate targets")
        if self.generation_model_lane is None and self.evaluation_model_lane is None:
            raise ValueError(
                "at least one of generation_model_lane or evaluation_model_lane must be set"
            )
        if (
            self.checkpoint_benchmark_role is not None
            and self.workflow_role != "campaign_launch"
        ):
            raise ValueError(
                "checkpoint_benchmark_role is only valid for campaign_launch targets"
            )
        return self


class LlmServingSmokeCheck(BaseModel):
    target_id: str
    role: Literal["generation", "evaluation"]
    status: Literal["passed", "failed"]
    requested_model_lane: CampaignModelLane | None = None
    resolved_model_lane: CampaignModelLane | None = None
    resolved_model_lane_source: ResolvedModelLaneSource | None = None
    serving_identity: LlmServingIdentity | None = None
    latency_s: float
    detail: str | None = None

    @field_validator("target_id")
    @classmethod
    def validate_target_id(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("detail")
    @classmethod
    def normalize_optional_detail(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @model_validator(mode="after")
    def validate_latency(self) -> LlmServingSmokeCheck:
        if self.latency_s < 0.0:
            raise ValueError("latency_s must be >= 0")
        return self


class LlmServingBenchmarkTargetResult(BaseModel):
    target_id: str
    label: str
    workflow_role: Literal["campaign_launch", "llm_evaluate"]
    estimated_cost_usd: float
    operator_friction_tier: Literal["low", "medium", "high"]
    smoke_checks: list[LlmServingSmokeCheck] = Field(default_factory=list)
    quality_metrics: dict[str, float | bool | None] = Field(default_factory=dict)
    execution_latency_s: float | None = None
    launch_summary_path: str | None = None
    comparison_path: str | None = None
    evaluate_summary_path: str | None = None
    summary_lines: list[str] = Field(default_factory=list)

    @field_validator("target_id", "label")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator(
        "launch_summary_path",
        "comparison_path",
        "evaluate_summary_path",
    )
    @classmethod
    def normalize_optional_paths(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("summary_lines")
    @classmethod
    def normalize_summary_lines(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)

    @field_validator("quality_metrics")
    @classmethod
    def validate_quality_metrics(
        cls, value: dict[str, float | bool | None]
    ) -> dict[str, float | bool | None]:
        out: dict[str, float | bool | None] = {}
        for key, metric in value.items():
            normalized_key = _require_non_blank_string(key)
            if normalized_key not in OUTCOME_METRIC_KEYS:
                raise ValueError(f"unsupported quality metric key: {normalized_key}")
            if metric is not None and not isinstance(metric, (bool, float, int)):
                raise ValueError("quality_metrics values must be float, bool, or None")
            if isinstance(metric, int) and not isinstance(metric, bool):
                out[normalized_key] = float(metric)
            else:
                out[normalized_key] = metric
        return out

    @model_validator(mode="after")
    def validate_result_metrics(self) -> LlmServingBenchmarkTargetResult:
        if self.estimated_cost_usd < 0.0:
            raise ValueError("estimated_cost_usd must be >= 0")
        if self.execution_latency_s is not None and self.execution_latency_s < 0.0:
            raise ValueError("execution_latency_s must be >= 0")
        return self


class LlmServingBenchmarkSummary(BaseModel):
    benchmark_id: str
    acceptance_pack_path: str
    generated_at_utc: str
    targets: list[LlmServingBenchmarkTargetResult] = Field(default_factory=list)
    recommendation_lines: list[str] = Field(default_factory=list)
    failed_targets: list[str] = Field(default_factory=list)

    @field_validator("benchmark_id", "acceptance_pack_path", "generated_at_utc")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @field_validator("recommendation_lines", "failed_targets")
    @classmethod
    def normalize_string_fields(cls, values: Sequence[str]) -> list[str]:
        return _normalize_string_list(values)


class LlmServingBenchmarkSpec(BaseModel):
    benchmark_id: str
    acceptance_pack_path: str
    targets: list[LlmServingBenchmarkTarget] = Field(default_factory=list)

    @field_validator("benchmark_id", "acceptance_pack_path")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        return _require_non_blank_string(value)

    @model_validator(mode="after")
    def validate_targets(self) -> LlmServingBenchmarkSpec:
        if len(self.targets) < 2:
            raise ValueError("serving benchmark spec must include at least two targets")
        target_ids = [target.target_id for target in self.targets]
        if len(set(target_ids)) != len(target_ids):
            raise ValueError("serving benchmark spec must use unique target_id values")
        lifecycle_roles = [
            target.checkpoint_benchmark_role
            for target in self.targets
            if target.checkpoint_benchmark_role is not None
        ]
        if len(set(lifecycle_roles)) != len(lifecycle_roles):
            raise ValueError("checkpoint_benchmark_role values must be unique within one benchmark")
        return self


from materials_discovery.common.schema import LlmEvaluateSummary

LlmEvaluateSummary.model_rebuild(
    _types_namespace={
        "LlmServingIdentity": LlmServingIdentity,
        "ResolvedModelLaneSource": ResolvedModelLaneSource,
    }
)
