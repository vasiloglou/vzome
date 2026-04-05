from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import UTC, datetime
from pathlib import Path

import typer
from pydantic import ValidationError

from materials_discovery.active_learning.select_next_batch import select_next_candidate_batch
from materials_discovery.active_learning.train_surrogate import (
    candidate_feature_map,
    train_surrogate_model,
)
from materials_discovery.backends.capabilities import load_capabilities_matrix
from materials_discovery.backends.registry import (
    is_source_runtime_ingest_adapter,
    resolve_ingest_backend,
)
from materials_discovery.common.io import (
    append_jsonl,
    ensure_parent,
    load_json_object,
    load_jsonl,
    load_yaml,
    workspace_root,
    write_json_object,
    write_jsonl,
)
from materials_discovery.common.benchmarking import (
    BenchmarkRunContext,
    build_benchmark_run_context,
    write_benchmark_pack,
)
from materials_discovery.common.manifest import build_manifest, config_sha256, write_manifest
from materials_discovery.common.pipeline_manifest import (
    build_pipeline_manifest,
    write_pipeline_manifest,
)
from materials_discovery.common.schema import (
    ActiveLearnSummary,
    CandidateRecord,
    HifiRankSummary,
    HifiValidateSummary,
    IngestSummary,
    LlmEvaluateSummary,
    LlmModelLaneConfig,
    ReportSummary,
    ScreenSummary,
    SystemConfig,
    ZomicExportSummary,
)
from materials_discovery.common.stage_metrics import (
    generation_metrics,
    llm_generation_metrics,
    ranking_calibration,
    report_calibration,
    screening_calibration,
    validation_calibration,
)
from materials_discovery.data.ingest_hypodx import ingest_rows
from materials_discovery.data_sources.projection import (
    project_canonical_records,
    project_snapshot_to_ingest_records,
)
from materials_discovery.data_sources.reference_packs import assemble_reference_pack_from_config
from materials_discovery.data_sources.registry import (
    SOURCE_RUNTIME_BRIDGE_ADAPTER_KEY,
    register_builtin_source_adapters,
    resolve_source_adapter,
)
from materials_discovery.data_sources.runtime import (
    load_cached_source_stage_summary,
    stage_registered_source_snapshot,
)
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord
from materials_discovery.common.io import load_jsonl as _load_jsonl_for_pack
from materials_discovery.diffraction.compare_patterns import compile_experiment_report
from materials_discovery.diffraction.simulate_powder_xrd import simulate_powder_xrd_patterns
from materials_discovery.generator.candidate_factory import generate_candidates
from materials_discovery.generator.zomic_bridge import export_zomic_design
from materials_discovery.hifi_digital.committee_relax import run_committee_relaxation
from materials_discovery.hifi_digital.geometry_prefilter import run_geometry_prefilter
from materials_discovery.hifi_digital.hull_proxy import compute_proxy_hull
from materials_discovery.hifi_digital.md_stability import run_short_md_stability
from materials_discovery.hifi_digital.phonon_mlip import run_mlip_phonon_checks
from materials_discovery.hifi_digital.rank_candidates import rank_validated_candidates
from materials_discovery.hifi_digital.uncertainty import compute_committee_uncertainty
from materials_discovery.hifi_digital.xrd_validate import validate_xrd_signatures
from materials_discovery.screen.filter_thresholds import (
    DEFAULT_MAX_ENERGY_PROXY,
    DEFAULT_MIN_DISTANCE_PROXY,
    apply_screen_thresholds,
)
from materials_discovery.screen.rank_shortlist import rank_screen_shortlist
from materials_discovery.screen.relax_fast import run_fast_relaxation

from materials_discovery.lake.index import (
    build_lake_index,
    lake_stats,
    write_lake_index,
)
from materials_discovery.llm.corpus_builder import build_llm_corpus
from materials_discovery.llm.campaigns import (
    create_campaign_approval,
    materialize_campaign_spec,
)
from materials_discovery.llm.evaluate import evaluate_llm_candidates
from materials_discovery.llm.generate import generate_llm_candidates
from materials_discovery.llm.launch import resolve_campaign_launch, resolve_serving_lane
from materials_discovery.llm.compare import (
    build_campaign_comparison,
    build_campaign_outcome_snapshot,
)
from materials_discovery.llm.replay import (
    build_replay_campaign_metadata,
    build_replay_config,
    load_campaign_launch_bundle,
)
from materials_discovery.llm.schema import (
    CorpusBuildConfig,
    LlmAcceptancePack,
    LlmCampaignLaunchSummary,
    LlmCampaignProposal,
    LlmCampaignSpec,
    LlmServingIdentity,
)
from materials_discovery.llm.storage import (
    llm_acceptance_approval_path,
    llm_artifact_root_from_acceptance_pack_path,
    llm_campaign_comparison_path,
    llm_campaign_launch_summary_path,
    llm_campaign_outcome_snapshot_path,
    llm_campaign_resolved_launch_path,
    llm_campaign_spec_path,
)
from materials_discovery.llm.suggest import write_llm_suggestions
from materials_discovery.llm.runtime import resolve_llm_adapter, validate_llm_adapter_ready

app = typer.Typer(add_completion=False, help="No-DFT materials discovery CLI scaffold")

# --- Lake sub-application (D-10: lake catalog and analysis commands) ---
lake_app = typer.Typer(help="Data lake catalog and analysis commands")
app.add_typer(lake_app, name="lake")

# --- LLM corpus preparation sub-application ---
llm_corpus_app = typer.Typer(help="LLM corpus preparation commands")
app.add_typer(llm_corpus_app, name="llm-corpus")


def _emit_error(message: str) -> None:
    typer.echo(message, err=True)


def _load_system_config(path: Path) -> SystemConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    data = load_yaml(path)
    return SystemConfig.model_validate(data)


def _backend_versions_for_stage(config: SystemConfig, stage: str) -> dict[str, str]:
    versions = dict(config.backend.versions)
    capabilities = load_capabilities_matrix()
    mode_map = capabilities.get("modes", {}).get(config.backend.mode, {})
    if isinstance(mode_map, dict):
        adapter_key = f"{stage}_adapter"
        adapter = mode_map.get(adapter_key)
        if isinstance(adapter, str):
            versions[adapter] = versions.get(adapter, "builtin")
    if config.backend.ingest_adapter is not None:
        versions[config.backend.ingest_adapter] = versions.get(
            config.backend.ingest_adapter,
            "builtin",
        )
    for adapter_name in (
        config.backend.committee_adapter,
        config.backend.phonon_adapter,
        config.backend.md_adapter,
        config.backend.xrd_adapter,
    ):
        if adapter_name is not None:
            versions[adapter_name] = versions.get(adapter_name, "builtin")
    if config.backend.benchmark_corpus is not None:
        versions["benchmark_corpus"] = versions.get("benchmark_corpus", "pinned")
    return versions


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _batch_slug(batch: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", batch.strip().lower()).strip("_")
    return slug or "batch"


def _baseline_llm_runtime_tuple(config: SystemConfig) -> tuple[str, str, str, str | None]:
    if config.backend.mode == "mock":
        return (
            config.backend.llm_adapter or "llm_fixture_v1",
            config.backend.llm_provider or "mock",
            config.backend.llm_model or "fixture",
            config.backend.llm_api_base,
        )
    return (
        config.backend.llm_adapter or "anthropic_api_v1",
        config.backend.llm_provider or "anthropic",
        config.backend.llm_model or "fixture",
        config.backend.llm_api_base,
    )


def _build_serving_identity(
    config: SystemConfig,
    *,
    requested_lane: str | None,
    resolved_lane: str,
    lane_source: str,
    lane_config: LlmModelLaneConfig | None,
) -> LlmServingIdentity:
    adapter, provider, model, api_base = _baseline_llm_runtime_tuple(config)
    checkpoint_id = None
    model_revision = None
    local_model_path = None
    if lane_config is not None:
        adapter = lane_config.adapter
        provider = lane_config.provider
        model = lane_config.model
        api_base = lane_config.api_base
        checkpoint_id = lane_config.checkpoint_id
        model_revision = lane_config.model_revision
        local_model_path = lane_config.local_model_path
    return LlmServingIdentity(
        requested_model_lane=requested_lane,
        resolved_model_lane=resolved_lane,
        resolved_model_lane_source=lane_source,
        adapter=adapter,
        provider=provider,
        model=model,
        effective_api_base=api_base,
        checkpoint_id=checkpoint_id,
        model_revision=model_revision,
        local_model_path=local_model_path,
    )


def _resolve_llm_serving_config(
    config: SystemConfig,
    *,
    requested_lane: str | None,
) -> tuple[SystemConfig, LlmServingIdentity]:
    resolved_lane, lane_config, lane_source = resolve_serving_lane(
        requested_lane,
        config.llm_generate,
        config.backend,
    )
    serving_identity = _build_serving_identity(
        config,
        requested_lane=requested_lane,
        resolved_lane=resolved_lane,
        lane_source=lane_source,
        lane_config=lane_config,
    )
    resolved_config = config.model_copy(deep=True)
    resolved_config.backend.llm_adapter = serving_identity.adapter
    resolved_config.backend.llm_provider = serving_identity.provider
    resolved_config.backend.llm_model = serving_identity.model
    resolved_config.backend.llm_api_base = serving_identity.effective_api_base
    return resolved_config, serving_identity


def _shortlist_rank(candidate: CandidateRecord) -> int:
    rank = (candidate.screen or {}).get("shortlist_rank")
    if isinstance(rank, int):
        return rank
    if isinstance(rank, float) and rank.is_integer():
        return int(rank)
    return 10**9


def _quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("cannot compute quantile for empty values")
    if q <= 0.0:
        return min(values)
    if q >= 1.0:
        return max(values)

    ordered = sorted(values)
    location = (len(ordered) - 1) * q
    lower = math.floor(location)
    upper = math.ceil(location)
    if lower == upper:
        return ordered[lower]
    fraction = location - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _select_hifi_batch(candidates: list[CandidateRecord], batch: str) -> list[CandidateRecord]:
    ordered = sorted(
        candidates,
        key=lambda candidate: (_shortlist_rank(candidate), candidate.candidate_id),
    )
    token = batch.strip().lower()

    if token == "all":
        selected = ordered
    elif token.startswith("top"):
        suffix = token[3:]
        if not suffix or not suffix.isdigit() or int(suffix) < 1:
            raise ValueError("batch must be 'all' or 'top<N>' with N >= 1, e.g. top500")
        selected = ordered[: int(suffix)]
    else:
        raise ValueError("batch must be 'all' or 'top<N>' with N >= 1, e.g. top500")

    if not selected:
        raise ValueError(
            "no screened candidates available; run 'mdisc screen' with more candidates"
        )

    return selected


def _finalize_validation(candidates: list[CandidateRecord]) -> tuple[list[CandidateRecord], int]:
    finalized: list[CandidateRecord] = []
    passed_count = 0

    for candidate in candidates:
        copied = candidate.model_copy(deep=True)
        validation = copied.digital_validation.model_copy(deep=True)

        uncertainty = validation.uncertainty_ev_per_atom
        delta_hull = validation.delta_e_proxy_hull_ev_per_atom
        passed_checks = (
            uncertainty is not None
            and uncertainty <= 0.04
            and delta_hull is not None
            and delta_hull <= 0.08
            and validation.phonon_pass is True
            and validation.md_pass is True
            and validation.xrd_pass is True
        )

        validation.passed_checks = passed_checks
        validation.status = "passed" if passed_checks else "failed"
        copied.digital_validation = validation

        if passed_checks:
            passed_count += 1
        finalized.append(copied)

    return finalized, passed_count


def _load_validated_candidates(system_slug: str) -> list[CandidateRecord]:
    validated_dir = workspace_root() / "data" / "hifi_validated"
    validated_paths = sorted(validated_dir.glob(f"{system_slug}_*_validated.jsonl"))
    if not validated_paths:
        raise FileNotFoundError(
            "active-learn validated inputs not found; run 'mdisc hifi-validate' first: "
            f"{validated_dir / (system_slug + '_*_validated.jsonl')}"
        )

    deduped: dict[str, CandidateRecord] = {}
    for path in validated_paths:
        for row in load_jsonl(path):
            candidate = CandidateRecord.model_validate(row)
            if candidate.candidate_id not in deduped:
                deduped[candidate.candidate_id] = candidate

    if not deduped:
        raise ValueError("validated candidate files were found but contained no records")

    return [deduped[candidate_id] for candidate_id in sorted(deduped)]


def _load_ranked_candidates(system_slug: str) -> list[CandidateRecord]:
    ranked_path = workspace_root() / "data" / "ranked" / f"{system_slug}_ranked.jsonl"
    if not ranked_path.exists():
        raise FileNotFoundError(
            "report input ranked file not found; run 'mdisc hifi-rank' first: "
            f"{ranked_path}"
        )

    ranked = [CandidateRecord.model_validate(row) for row in load_jsonl(ranked_path)]
    if not ranked:
        raise ValueError("ranked candidate file was found but contained no records")
    return ranked


def _load_report_candidates(system_slug: str) -> tuple[list[CandidateRecord], Path]:
    llm_evaluated_path = (
        workspace_root() / "data" / "llm_evaluated" / f"{system_slug}_all_llm_evaluated.jsonl"
    )
    if llm_evaluated_path.exists():
        evaluated = [
            CandidateRecord.model_validate(row) for row in load_jsonl(llm_evaluated_path)
        ]
        if evaluated:
            return evaluated, llm_evaluated_path

    ranked_path = workspace_root() / "data" / "ranked" / f"{system_slug}_ranked.jsonl"
    return _load_ranked_candidates(system_slug), ranked_path


def _enrich_validated_with_ranked(
    system_slug: str,
    validated: list[CandidateRecord],
) -> list[CandidateRecord]:
    ranked_path = workspace_root() / "data" / "ranked" / f"{system_slug}_ranked.jsonl"
    if not ranked_path.exists():
        return validated

    ranked = {
        candidate.candidate_id: candidate
        for candidate in _load_ranked_candidates(system_slug)
    }
    enriched: list[CandidateRecord] = []
    for candidate in validated:
        enriched.append(ranked.get(candidate.candidate_id, candidate))
    return enriched


def _load_active_learning_pool(
    system_slug: str,
    validated_ids: set[str],
) -> list[CandidateRecord]:
    screened_path = workspace_root() / "data" / "screened" / f"{system_slug}_screened.jsonl"
    if screened_path.exists():
        screened_pool = [CandidateRecord.model_validate(row) for row in load_jsonl(screened_path)]
        if any(candidate.candidate_id not in validated_ids for candidate in screened_pool):
            return screened_pool

    candidates_path = workspace_root() / "data" / "candidates" / f"{system_slug}_candidates.jsonl"
    return [CandidateRecord.model_validate(row) for row in load_jsonl(candidates_path)]


def _workspace_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return workspace_root() / path


def _new_launch_id() -> str:
    return f"launch_{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}"


def _ingest_via_reference_pack(
    config: SystemConfig,
    out_path: Path,
) -> tuple[IngestSummary, dict[str, object]]:
    """Assemble a multi-source reference pack and project into processed IngestRecords.

    Called when ``ingestion.reference_pack`` is set in the system config.
    This is a no-DFT path: it assembles, deduplicates, and projects canonical
    source records into processed reference phases without invoking any
    high-fidelity validation adapters.
    """
    pack_manifest = assemble_reference_pack_from_config(config)

    canonical_records_path = _workspace_path(pack_manifest.canonical_records_path)
    raw_rows = _load_jsonl_for_pack(canonical_records_path)
    records = [CanonicalRawSourceRecord.model_validate(row) for row in raw_rows]
    projected, projection_summary = project_canonical_records(records, config)

    if not projected:
        raise ValueError("reference-pack projection produced zero usable records")

    write_jsonl([row.model_dump(mode="json") for row in projected], out_path)

    summary = IngestSummary(
        raw_count=pack_manifest.total_canonical_records,
        matched_count=projection_summary.matched_system_count,
        deduped_count=projection_summary.deduped_count,
        output_path=str(out_path),
        invalid_count=projection_summary.skipped_missing_composition_count,
        backend_mode=config.backend.mode,
        backend_adapter=SOURCE_RUNTIME_BRIDGE_ADAPTER_KEY,
        qa_metrics={
            "passed": projection_summary.deduped_count > 0,
            "input_count": projection_summary.input_count,
            "matched_system_count": projection_summary.matched_system_count,
            "projected_count": projection_summary.projected_count,
            "deduped_count": projection_summary.deduped_count,
            "skipped_system_mismatch_count": projection_summary.skipped_system_mismatch_count,
            "skipped_missing_composition_count": projection_summary.skipped_missing_composition_count,
            "duplicate_dropped_count": projection_summary.duplicate_dropped_count,
        },
    )
    source_lineage: dict[str, object] = {
        "pack_id": pack_manifest.pack_id,
        "system_slug": pack_manifest.system_slug,
        "pack_fingerprint": pack_manifest.pack_fingerprint,
        "canonical_records_path": pack_manifest.canonical_records_path,
        "total_canonical_records": pack_manifest.total_canonical_records,
        "member_sources": [
            {"source_key": m.source_key, "snapshot_id": m.snapshot_id}
            for m in pack_manifest.members
        ],
        "priority_order": pack_manifest.priority_order,
        "projection_summary": projection_summary.model_dump(mode="json"),
    }
    return summary, source_lineage


def _source_registry_snapshot_id(config: SystemConfig) -> tuple[str, str, str | None]:
    ingestion = config.ingestion
    if ingestion is None:
        raise ValueError("source_registry_v1 ingest requires an ingestion block")

    register_builtin_source_adapters()
    adapter = resolve_source_adapter(ingestion.source_key, ingestion.adapter_key)
    snapshot_id = ingestion.snapshot_id or adapter.default_snapshot_id(config)
    return ingestion.source_key, snapshot_id, ingestion.adapter_key


def _ingest_via_source_registry(
    config: SystemConfig,
    fixture: Path | None,
    out_path: Path,
) -> tuple[IngestSummary, dict[str, object]]:
    ingestion = config.ingestion
    if ingestion is None:
        raise ValueError("source_registry_v1 ingest requires an ingestion block")

    source_key, snapshot_id, adapter_key = _source_registry_snapshot_id(config)
    if ingestion.use_cached_snapshot:
        stage_summary = load_cached_source_stage_summary(config, source_key, snapshot_id)
        if stage_summary is None:
            stage_summary = stage_registered_source_snapshot(
                config,
                source_key,
                adapter_key=adapter_key,
                snapshot_path=fixture,
            )
    else:
        stage_summary = stage_registered_source_snapshot(
            config,
            source_key,
            adapter_key=adapter_key,
            snapshot_path=fixture,
        )

    projected, projection_summary = project_snapshot_to_ingest_records(
        _workspace_path(stage_summary.canonical_records_path),
        config,
    )
    if not projected:
        raise ValueError("source projection produced zero usable records")

    write_jsonl([row.model_dump(mode="json") for row in projected], out_path)
    snapshot_manifest = load_json_object(_workspace_path(stage_summary.snapshot_manifest_path))
    summary = IngestSummary(
        raw_count=stage_summary.raw_count,
        matched_count=projection_summary.matched_system_count,
        deduped_count=projection_summary.deduped_count,
        output_path=str(out_path),
        invalid_count=projection_summary.skipped_missing_composition_count,
        backend_mode=config.backend.mode,
        backend_adapter=SOURCE_RUNTIME_BRIDGE_ADAPTER_KEY,
        qa_metrics={
            "passed": projection_summary.deduped_count > 0,
            "input_count": projection_summary.input_count,
            "matched_system_count": projection_summary.matched_system_count,
            "projected_count": projection_summary.projected_count,
            "deduped_count": projection_summary.deduped_count,
            "skipped_system_mismatch_count": projection_summary.skipped_system_mismatch_count,
            "skipped_missing_composition_count": projection_summary.skipped_missing_composition_count,
            "duplicate_dropped_count": projection_summary.duplicate_dropped_count,
        },
    )
    source_lineage: dict[str, object] = {
        "source_key": source_key,
        "snapshot_id": snapshot_id,
        "adapter_key": snapshot_manifest.get("adapter_key"),
        "adapter_version": snapshot_manifest.get("adapter_version"),
        "snapshot_manifest_path": stage_summary.snapshot_manifest_path,
        "canonical_records_path": stage_summary.canonical_records_path,
        "qa_report_path": stage_summary.qa_report_path,
        "projection_summary": projection_summary.model_dump(mode="json"),
    }
    return summary, source_lineage


def _load_benchmark_context(
    config: SystemConfig,
    system_slug: str,
) -> BenchmarkRunContext:
    """Load and assemble the benchmark run context for downstream stage commands.

    Reads the previously written ingest manifest (if present) to recover the
    source lineage, then delegates to :func:`build_benchmark_run_context`.
    Falls back gracefully to a config-only context when the manifest is absent.
    """
    ingest_manifest_path = (
        workspace_root() / "data" / "manifests" / f"{system_slug}_ingest_manifest.json"
    )
    source_lineage: dict[str, object] | None = None
    if ingest_manifest_path.exists():
        try:
            raw_manifest = load_json_object(ingest_manifest_path)
            lineage = raw_manifest.get("source_lineage")
            if isinstance(lineage, dict):
                source_lineage = lineage
        except Exception:  # noqa: BLE001
            pass
    return build_benchmark_run_context(config, source_lineage)


_CAMPAIGN_LINEAGE_KEYS = (
    "campaign_id",
    "launch_id",
    "proposal_id",
    "approval_id",
    "campaign_spec_path",
    "launch_summary_path",
    "resolved_launch_path",
    "replay_of_launch_id",
    "replay_of_launch_summary_path",
    "requested_model_lanes",
    "resolved_model_lane",
    "resolved_model_lane_source",
)


def _normalize_campaign_lineage(
    lineage: dict[str, object] | None,
) -> dict[str, object] | None:
    if not isinstance(lineage, dict):
        return None

    raw_campaign = lineage.get("llm_campaign")
    if isinstance(raw_campaign, dict):
        payload = raw_campaign
    else:
        payload = lineage

    campaign_id = payload.get("campaign_id")
    launch_id = payload.get("launch_id")
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        return None
    if not isinstance(launch_id, str) or not launch_id.strip():
        return None

    normalized: dict[str, object] = {
        "campaign_id": campaign_id.strip(),
        "launch_id": launch_id.strip(),
    }
    for key in _CAMPAIGN_LINEAGE_KEYS:
        if key in {"campaign_id", "launch_id"}:
            continue
        value = payload.get(key)
        if value is None:
            continue
        if key == "requested_model_lanes":
            if isinstance(value, list):
                cleaned = [
                    item.strip()
                    for item in value
                    if isinstance(item, str) and item.strip()
                ]
                if cleaned:
                    normalized[key] = cleaned
            continue
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                normalized[key] = stripped

    return {"llm_campaign": normalized}


def _candidate_campaign_lineage(
    candidates: list[CandidateRecord],
) -> dict[str, object] | None:
    for candidate in sorted(candidates, key=lambda item: item.candidate_id):
        raw = candidate.provenance.get("llm_campaign")
        if isinstance(raw, dict):
            normalized = _normalize_campaign_lineage({"llm_campaign": raw})
            if normalized is not None:
                return normalized
    return None


def _load_llm_generate_campaign_lineage(system_slug: str) -> dict[str, object] | None:
    manifest_path = (
        workspace_root() / "data" / "manifests" / f"{system_slug}_llm_generate_manifest.json"
    )
    if not manifest_path.exists():
        return None
    try:
        raw_manifest = load_json_object(manifest_path)
    except Exception:  # noqa: BLE001
        return None
    lineage = raw_manifest.get("source_lineage")
    if isinstance(lineage, dict):
        return _normalize_campaign_lineage(lineage)
    return None


def _merge_campaign_lineage(
    primary: dict[str, object] | None,
    fallback: dict[str, object] | None,
) -> dict[str, object] | None:
    if primary is None:
        return fallback
    if fallback is None:
        return primary

    primary_payload = primary["llm_campaign"]
    fallback_payload = fallback["llm_campaign"]
    if (
        primary_payload.get("campaign_id") != fallback_payload.get("campaign_id")
        or primary_payload.get("launch_id") != fallback_payload.get("launch_id")
    ):
        return primary

    merged = dict(fallback_payload)
    merged.update(primary_payload)
    return {"llm_campaign": merged}


def _resolve_campaign_lineage(
    system_slug: str,
    candidates: list[CandidateRecord],
) -> dict[str, object] | None:
    candidate_lineage = _candidate_campaign_lineage(candidates)
    manifest_lineage = _load_llm_generate_campaign_lineage(system_slug)
    return _merge_campaign_lineage(candidate_lineage, manifest_lineage)


@app.command("ingest")
def ingest_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
    fixture: Path | None = typer.Option(None, "--fixture", exists=False, dir_okay=False),
    out: Path | None = typer.Option(None, "--out", exists=False, dir_okay=False),
) -> None:
    """Ingest and normalize fixture metadata into processed JSONL."""
    try:
        system_config = _load_system_config(config)
        default_out = (
            workspace_root()
            / "data"
            / "processed"
            / f"{_system_slug(system_config.system_name)}_reference_phases.jsonl"
        )
        out_path = out or default_out
        source_lineage: dict[str, object] | None = None
        _has_reference_pack = (
            system_config.ingestion is not None
            and system_config.ingestion.reference_pack is not None
        )
        if is_source_runtime_ingest_adapter(system_config.backend.ingest_adapter) and _has_reference_pack:
            summary, source_lineage = _ingest_via_reference_pack(system_config, out_path)
        elif is_source_runtime_ingest_adapter(system_config.backend.ingest_adapter):
            summary, source_lineage = _ingest_via_source_registry(system_config, fixture, out_path)
        else:
            backend = resolve_ingest_backend(
                system_config.backend.mode,
                system_config.backend.ingest_adapter,
            )
            backend_info = backend.info()
            raw_rows = backend.load_rows(system_config, fixture)
            summary = ingest_rows(
                system_config,
                raw_rows,
                out_path,
                backend_mode=system_config.backend.mode,
                backend_adapter=backend_info.name,
            )

        system_slug = _system_slug(system_config.system_name)
        manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_ingest_manifest.json"
        )
        backend_versions = _backend_versions_for_stage(system_config, "ingest")
        if source_lineage is None:
            backend_versions[summary.backend_adapter] = backend_versions.get(
                summary.backend_adapter,
                "builtin",
            )
        else:
            adapter_key = source_lineage.get("adapter_key")
            adapter_version = source_lineage.get("adapter_version")
            if isinstance(adapter_key, str) and adapter_key:
                backend_versions[adapter_key] = (
                    str(adapter_version) if adapter_version is not None else "staged"
                )
        manifest = build_manifest(
            stage="ingest",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=backend_versions,
            output_paths={"processed_jsonl": out_path},
            source_lineage=source_lineage,
        )
        write_manifest(manifest, manifest_path)
        summary.manifest_path = str(manifest_path)

        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"ingest failed: {exc}")
        raise typer.Exit(code=2)


@app.command("generate")
def generate_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
    count: int = typer.Option(..., "--count", min=1),
    seed: int | None = typer.Option(None, "--seed"),
    out: Path | None = typer.Option(None, "--out", exists=False, dir_okay=False),
) -> None:
    """Generate deterministic candidate structures into JSONL."""
    try:
        system_config = _load_system_config(config)
        system_slug = _system_slug(system_config.system_name)

        default_out = (
            workspace_root()
            / "data"
            / "candidates"
            / f"{system_slug}_candidates.jsonl"
        )
        out_path = out or default_out

        summary = generate_candidates(
            system_config,
            out_path,
            count=count,
            seed=seed,
            config_path=config,
        )
        generated_rows = load_jsonl(out_path)
        unique_count = len({row["candidate_id"] for row in generated_rows})
        metrics = generation_metrics(
            requested_count=summary.requested_count,
            generated_count=summary.generated_count,
            invalid_filtered_count=summary.invalid_filtered_count,
            unique_count=unique_count,
        )
        summary.qa_metrics = metrics

        calibration_path = (
            workspace_root() / "data" / "calibration" / f"{system_slug}_generation_metrics.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(metrics, sort_keys=True), encoding="utf-8")
        summary.calibration_path = str(calibration_path)

        manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_generate_manifest.json"
        )
        manifest = build_manifest(
            stage="generate",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=_backend_versions_for_stage(system_config, "generate"),
            output_paths={
                "candidates_jsonl": out_path,
                "generation_metrics_json": calibration_path,
            },
        )
        write_manifest(manifest, manifest_path)
        summary.manifest_path = str(manifest_path)
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"generate failed: {exc}")
        raise typer.Exit(code=2)


@app.command("llm-generate")
def llm_generate_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
    count: int = typer.Option(..., "--count", min=1),
    seed_zomic: Path | None = typer.Option(None, "--seed-zomic", exists=False, dir_okay=False),
    temperature: float | None = typer.Option(None, "--temperature"),
    model_lane: str | None = typer.Option(None, "--model-lane"),
    out: Path | None = typer.Option(None, "--out", exists=False, dir_okay=False),
) -> None:
    """Generate candidate structures from LLM-produced Zomic text."""
    try:
        system_config = _load_system_config(config)
        resolved_config, serving_identity = _resolve_llm_serving_config(
            system_config,
            requested_lane=model_lane,
        )
        adapter = resolve_llm_adapter(
            resolved_config.backend.mode,
            backend=resolved_config.backend,
            llm_generate=resolved_config.llm_generate,
        )
        validate_llm_adapter_ready(
            adapter,
            adapter_key=resolved_config.backend.llm_adapter or "llm_fixture_v1",
            requested_lane=model_lane,
            resolved_lane=serving_identity.resolved_model_lane,
        )
        system_slug = _system_slug(resolved_config.system_name)

        default_out = workspace_root() / "data" / "candidates" / f"{system_slug}_candidates.jsonl"
        out_path = out or default_out
        resolved_seed = None if seed_zomic is None else _workspace_path(str(seed_zomic))

        summary = generate_llm_candidates(
            resolved_config,
            out_path,
            count=count,
            config_path=config,
            seed_zomic_path=resolved_seed,
            temperature_override=temperature,
            serving_identity=serving_identity,
        )
        metrics = llm_generation_metrics(
            requested_count=summary.requested_count,
            generated_count=summary.generated_count,
            attempt_count=summary.attempt_count,
            parse_pass_count=summary.parse_pass_count,
            compile_pass_count=summary.compile_pass_count,
        )

        calibration_path = (
            workspace_root() / "data" / "calibration" / f"{system_slug}_llm_generation_metrics.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(metrics, sort_keys=True), encoding="utf-8")
        summary.calibration_path = str(calibration_path)

        manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_llm_generate_manifest.json"
        )
        output_paths = {
            "candidates_jsonl": out_path,
            "llm_generation_metrics_json": calibration_path,
        }
        if summary.run_manifest_path is not None:
            output_paths["llm_run_manifest_json"] = Path(summary.run_manifest_path)
        manifest = build_manifest(
            stage="llm_generate",
            config=resolved_config,
            backend_mode=resolved_config.backend.mode,
            backend_versions=_backend_versions_for_stage(resolved_config, "generate"),
            output_paths=output_paths,
        )
        write_manifest(manifest, manifest_path)
        summary.manifest_path = str(manifest_path)
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError, RuntimeError) as exc:
        _emit_error(f"llm-generate failed: {exc}")
        raise typer.Exit(code=2)


@app.command("llm-evaluate")
def llm_evaluate_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
    batch: str = typer.Option("all", "--batch"),
    out: Path | None = typer.Option(None, "--out", exists=False, dir_okay=False),
) -> None:
    """Assess ranked candidates with the LLM provider seam and write additive artifacts."""
    try:
        system_config = _load_system_config(config)
        system_slug = _system_slug(system_config.system_name)
        out_path = (
            out
            or workspace_root()
            / "data"
            / "llm_evaluated"
            / f"{system_slug}_{_batch_slug(batch)}_llm_evaluated.jsonl"
        )

        summary: LlmEvaluateSummary = evaluate_llm_candidates(
            system_config,
            out_path,
            batch=batch,
        )
        metrics = {
            "input_count": summary.input_count,
            "assessed_count": summary.assessed_count,
            "failed_count": summary.failed_count,
            "assessment_success_rate": (
                0.0 if summary.input_count == 0 else summary.assessed_count / summary.input_count
            ),
            "passed": summary.assessed_count > 0,
        }
        calibration_path = (
            workspace_root()
            / "data"
            / "calibration"
            / f"{system_slug}_{_batch_slug(batch)}_llm_evaluation_metrics.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(metrics, sort_keys=True), encoding="utf-8")
        summary.calibration_path = str(calibration_path)

        manifest_path = (
            workspace_root()
            / "data"
            / "manifests"
            / f"{system_slug}_{_batch_slug(batch)}_llm_evaluate_manifest.json"
        )
        output_paths = {
            "llm_evaluated_jsonl": out_path,
            "llm_evaluation_metrics_json": calibration_path,
        }
        if summary.run_manifest_path is not None:
            output_paths["llm_evaluation_run_manifest_json"] = Path(summary.run_manifest_path)
        manifest = build_manifest(
            stage="llm_evaluate",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=_backend_versions_for_stage(system_config, "generate"),
            output_paths=output_paths,
        )
        write_manifest(manifest, manifest_path)
        summary.manifest_path = str(manifest_path)
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError, RuntimeError) as exc:
        _emit_error(f"llm-evaluate failed: {exc}")
        raise typer.Exit(code=2)


@app.command("llm-suggest")
def llm_suggest_command(
    acceptance_pack: Path = typer.Option(..., "--acceptance-pack", exists=True, dir_okay=False),
    out: Path | None = typer.Option(None, "--out", dir_okay=False),
) -> None:
    """Emit a dry-run suggestion set from a typed acceptance pack."""
    try:
        pack = LlmAcceptancePack.model_validate(load_json_object(acceptance_pack))
        written_path = write_llm_suggestions(
            pack,
            acceptance_pack_path=acceptance_pack,
            out_path=out,
        )
        typer.echo(json.dumps(load_json_object(written_path)))
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"llm-suggest failed: {exc}")
        raise typer.Exit(code=2)


@app.command("llm-approve")
def llm_approve_command(
    proposal: Path = typer.Option(..., "--proposal", exists=False, dir_okay=False),
    decision: str = typer.Option(..., "--decision"),
    operator: str = typer.Option(..., "--operator"),
    config: Path | None = typer.Option(None, "--config", exists=False, dir_okay=False),
    notes: str | None = typer.Option(None, "--notes"),
) -> None:
    """Write approval artifacts and an optional self-contained campaign spec."""
    try:
        proposal_payload = load_json_object(proposal)
        typed_proposal = LlmCampaignProposal.model_validate(proposal_payload)
        approval = create_campaign_approval(
            typed_proposal,
            proposal_path=proposal,
            decision=decision,
            operator=operator,
            notes=notes,
        )

        acceptance_pack_path = Path(typed_proposal.acceptance_pack_path).resolve()
        artifact_root = llm_artifact_root_from_acceptance_pack_path(acceptance_pack_path)
        approval_path = llm_acceptance_approval_path(
            typed_proposal.pack_id,
            approval.approval_id,
            root=artifact_root,
        )
        ensure_parent(approval_path)
        approval_path.write_text(approval.model_dump_json(indent=2), encoding="utf-8")

        campaign_spec_path: Path | None = None
        if approval.decision == "approved":
            if config is None:
                raise ValueError("approved decisions require --config")
            system_config = _load_system_config(config)
            campaign_spec = materialize_campaign_spec(
                typed_proposal,
                approval,
                approval_path=approval_path,
                system_config=system_config,
                system_config_path=config,
            )
            campaign_spec_path = llm_campaign_spec_path(
                campaign_spec.campaign_id,
                root=artifact_root,
            )
            ensure_parent(campaign_spec_path)
            campaign_spec_path.write_text(
                campaign_spec.model_dump_json(indent=2),
                encoding="utf-8",
            )

        typer.echo(
            json.dumps(
                {
                    "proposal_id": typed_proposal.proposal_id,
                    "decision": approval.decision,
                    "approval_id": approval.approval_id,
                    "approval_path": str(approval_path),
                    "campaign_id": approval.campaign_id,
                    "campaign_spec_path": (
                        str(campaign_spec_path) if campaign_spec_path is not None else None
                    ),
                }
            )
        )
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"llm-approve failed: {exc}")
        raise typer.Exit(code=2)


@app.command("llm-launch")
def llm_launch_command(
    campaign_spec: Path = typer.Option(..., "--campaign-spec", exists=False, dir_okay=False),
    out: Path | None = typer.Option(None, "--out", exists=False, dir_okay=False),
) -> None:
    """Launch an approved campaign spec through the existing llm-generate runtime."""
    try:
        typed_spec = LlmCampaignSpec.model_validate(load_json_object(campaign_spec))
        config_path = _workspace_path(typed_spec.launch_baseline.system_config_path)
        system_config = _load_system_config(config_path)
        current_hash = config_sha256(system_config)
        if current_hash != typed_spec.launch_baseline.system_config_hash:
            raise ValueError(
                "campaign spec config hash does not match current config: "
                f"{config_path} changed since approval; "
                f"pinned={typed_spec.launch_baseline.system_config_hash}; "
                f"current={current_hash}; re-approval may be required"
            )

        launch_id = _new_launch_id()
        _emit_error(f"llm-launch starting: {launch_id}")

        system_slug = _system_slug(system_config.system_name)
        out_path = out or (
            workspace_root() / "data" / "candidates" / f"{system_slug}_candidates.jsonl"
        )

        resolved_config, resolved_launch = resolve_campaign_launch(
            typed_spec,
            system_config,
            campaign_spec_path=campaign_spec,
            launch_id=launch_id,
            artifact_root=workspace_root(),
        )
        adapter = resolve_llm_adapter(
            resolved_config.backend.mode,
            backend=resolved_config.backend,
            llm_generate=resolved_config.llm_generate,
        )
        validate_llm_adapter_ready(
            adapter,
            adapter_key=resolved_config.backend.llm_adapter or "llm_fixture_v1",
            requested_lane=next(iter(resolved_launch.requested_model_lanes), None),
            resolved_lane=resolved_launch.resolved_model_lane,
        )
        resolved_launch.effective_candidates_path = str(out_path)
        resolved_launch.output_override_used = out is not None

        resolved_launch_path = llm_campaign_resolved_launch_path(
            typed_spec.campaign_id,
            launch_id,
            root=workspace_root(),
        )
        write_json_object(resolved_launch.model_dump(mode="json"), resolved_launch_path)

        launch_summary_path = llm_campaign_launch_summary_path(
            typed_spec.campaign_id,
            launch_id,
            root=workspace_root(),
        )
        campaign_metadata = {
            "campaign_id": typed_spec.campaign_id,
            "launch_id": launch_id,
            "campaign_spec_path": str(campaign_spec),
            "proposal_id": typed_spec.proposal_id,
            "approval_id": typed_spec.approval_id,
            "requested_model_lanes": resolved_launch.requested_model_lanes,
            "resolved_model_lane": resolved_launch.resolved_model_lane,
            "resolved_model_lane_source": resolved_launch.resolved_model_lane_source,
            "launch_summary_path": str(launch_summary_path),
        }
        launch_source_lineage = _normalize_campaign_lineage(
            {
                "llm_campaign": {
                    **campaign_metadata,
                    "resolved_launch_path": str(resolved_launch_path),
                }
            }
        )

        summary = generate_llm_candidates(
            resolved_config,
            out_path,
            count=typed_spec.launch_baseline.default_count,
            config_path=config_path,
            prompt_instruction_deltas=resolved_launch.prompt_instruction_deltas,
            campaign_metadata=campaign_metadata,
            serving_identity=resolved_launch.serving_identity,
        )

        metrics = llm_generation_metrics(
            requested_count=summary.requested_count,
            generated_count=summary.generated_count,
            attempt_count=summary.attempt_count,
            parse_pass_count=summary.parse_pass_count,
            compile_pass_count=summary.compile_pass_count,
        )
        calibration_path = (
            workspace_root() / "data" / "calibration" / f"{system_slug}_llm_generation_metrics.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(metrics, sort_keys=True), encoding="utf-8")

        llm_generate_manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_llm_generate_manifest.json"
        )
        output_paths = {
            "candidates_jsonl": out_path,
            "llm_generation_metrics_json": calibration_path,
        }
        if summary.run_manifest_path is not None:
            output_paths["llm_run_manifest_json"] = Path(summary.run_manifest_path)
        manifest = build_manifest(
            stage="llm_generate",
            config=resolved_config,
            backend_mode=resolved_config.backend.mode,
            backend_versions=_backend_versions_for_stage(resolved_config, "generate"),
            output_paths=output_paths,
            source_lineage=launch_source_lineage,
        )
        write_manifest(manifest, llm_generate_manifest_path)

        launch_summary = LlmCampaignLaunchSummary(
            launch_id=launch_id,
            campaign_id=typed_spec.campaign_id,
            campaign_spec_path=str(campaign_spec),
            proposal_id=typed_spec.proposal_id,
            approval_id=typed_spec.approval_id,
            system=typed_spec.system,
            status="succeeded",
            created_at_utc=datetime.now(UTC).isoformat(),
            requested_count=typed_spec.launch_baseline.default_count,
            requested_model_lanes=resolved_launch.requested_model_lanes,
            resolved_model_lane=resolved_launch.resolved_model_lane,
            resolved_model_lane_source=resolved_launch.resolved_model_lane_source,
            resolved_launch_path=str(resolved_launch_path),
            run_manifest_path=summary.run_manifest_path,
            llm_generate_manifest_path=str(llm_generate_manifest_path),
            candidates_path=str(out_path),
        )
        write_json_object(launch_summary.model_dump(mode="json"), launch_summary_path)
        typer.echo(launch_summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError, RuntimeError) as exc:
        if "typed_spec" in locals() and "launch_id" in locals():
            resolved_launch_path = llm_campaign_resolved_launch_path(
                typed_spec.campaign_id,
                launch_id,
                root=workspace_root(),
            )
            failed_summary = LlmCampaignLaunchSummary(
                launch_id=launch_id,
                campaign_id=typed_spec.campaign_id,
                campaign_spec_path=str(campaign_spec),
                proposal_id=typed_spec.proposal_id,
                approval_id=typed_spec.approval_id,
                system=typed_spec.system,
                status="failed",
                created_at_utc=datetime.now(UTC).isoformat(),
                requested_count=typed_spec.launch_baseline.default_count,
                requested_model_lanes=(
                    [] if "resolved_launch" not in locals() else resolved_launch.requested_model_lanes
                ),
                resolved_model_lane=(
                    "general_purpose"
                    if "resolved_launch" not in locals()
                    else resolved_launch.resolved_model_lane
                ),
                resolved_model_lane_source=(
                    "backend_default"
                    if "resolved_launch" not in locals()
                    else resolved_launch.resolved_model_lane_source
                ),
                resolved_launch_path=str(resolved_launch_path),
                run_manifest_path=(
                    None if "summary" not in locals() else summary.run_manifest_path
                ),
                llm_generate_manifest_path=(
                    None
                    if "llm_generate_manifest_path" not in locals()
                    else str(llm_generate_manifest_path)
                ),
                candidates_path=(
                    str(out_path)
                    if "out_path" in locals() and Path(out_path).exists()
                    else None
                ),
                error_kind=type(exc).__name__,
                error_message=str(exc),
            )
            write_json_object(
                failed_summary.model_dump(mode="json"),
                llm_campaign_launch_summary_path(
                    typed_spec.campaign_id,
                    launch_id,
                    root=workspace_root(),
                ),
            )
        _emit_error(f"llm-launch failed: {exc}")
        raise typer.Exit(code=2)


@app.command("llm-replay")
def llm_replay_command(
    launch_summary: Path = typer.Option(..., "--launch-summary", exists=False, dir_okay=False),
) -> None:
    """Replay a saved LLM campaign launch strictly from its recorded launch bundle."""
    try:
        source_bundle = load_campaign_launch_bundle(launch_summary, root=workspace_root())
        config_path = _workspace_path(source_bundle.campaign_spec.launch_baseline.system_config_path)
        current_config = _load_system_config(config_path)
        current_hash = config_sha256(current_config)
        replay_config = build_replay_config(source_bundle, current_config)

        launch_id = _new_launch_id()
        _emit_error(f"llm-replay starting: {launch_id}")

        system_slug = _system_slug(replay_config.system_name)
        out_path = (
            workspace_root() / "data" / "candidates" / f"{system_slug}_replay_{launch_id}.jsonl"
        )

        resolved_launch = source_bundle.resolved_launch.model_copy(deep=True)
        resolved_launch.launch_id = launch_id
        resolved_launch.campaign_spec_path = str(source_bundle.campaign_spec_path)
        resolved_launch.system_config_path = str(config_path)
        resolved_launch.system_config_hash = source_bundle.campaign_spec.launch_baseline.system_config_hash
        resolved_launch.requested_model_lanes = list(source_bundle.launch_summary.requested_model_lanes)
        resolved_launch.resolved_model_lane = source_bundle.launch_summary.resolved_model_lane
        resolved_launch.resolved_model_lane_source = (
            source_bundle.launch_summary.resolved_model_lane_source
        )
        resolved_launch.resolved_adapter = replay_config.backend.llm_adapter or ""
        resolved_launch.resolved_provider = replay_config.backend.llm_provider or ""
        resolved_launch.resolved_model = replay_config.backend.llm_model or ""
        resolved_launch.prompt_instruction_deltas = list(
            source_bundle.run_manifest.prompt_instruction_deltas
        )
        resolved_launch.resolved_composition_bounds = {
            species: bound.model_copy(deep=True)
            for species, bound in replay_config.composition_bounds.items()
        }
        resolved_launch.resolved_example_pack_path = replay_config.llm_generate.example_pack_path
        resolved_launch.resolved_seed_zomic_path = replay_config.llm_generate.seed_zomic
        resolved_launch.effective_candidates_path = str(out_path)
        resolved_launch.output_override_used = False
        resolved_launch.replay_of_launch_id = source_bundle.launch_summary.launch_id
        resolved_launch.replay_of_launch_summary_path = str(source_bundle.launch_summary_path)
        resolved_launch.current_system_config_hash = current_hash

        resolved_launch_path = llm_campaign_resolved_launch_path(
            source_bundle.campaign_spec.campaign_id,
            launch_id,
            root=workspace_root(),
        )
        write_json_object(resolved_launch.model_dump(mode="json"), resolved_launch_path)

        replay_launch_summary_path = llm_campaign_launch_summary_path(
            source_bundle.campaign_spec.campaign_id,
            launch_id,
            root=workspace_root(),
        )
        campaign_metadata = build_replay_campaign_metadata(source_bundle)
        campaign_metadata.update(
            {
                "launch_id": launch_id,
                "launch_summary_path": str(replay_launch_summary_path),
            }
        )
        replay_source_lineage = _normalize_campaign_lineage(
            {
                "llm_campaign": {
                    **campaign_metadata,
                    "resolved_launch_path": str(resolved_launch_path),
                }
            }
        )

        summary = generate_llm_candidates(
            replay_config,
            out_path,
            count=source_bundle.launch_summary.requested_count,
            config_path=config_path,
            prompt_instruction_deltas=list(source_bundle.run_manifest.prompt_instruction_deltas),
            campaign_metadata=campaign_metadata,
        )

        metrics = llm_generation_metrics(
            requested_count=summary.requested_count,
            generated_count=summary.generated_count,
            attempt_count=summary.attempt_count,
            parse_pass_count=summary.parse_pass_count,
            compile_pass_count=summary.compile_pass_count,
        )
        calibration_path = (
            workspace_root() / "data" / "calibration" / f"{system_slug}_llm_generation_metrics.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(metrics, sort_keys=True), encoding="utf-8")

        llm_generate_manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_llm_generate_manifest.json"
        )
        output_paths = {
            "candidates_jsonl": out_path,
            "llm_generation_metrics_json": calibration_path,
        }
        if summary.run_manifest_path is not None:
            output_paths["llm_run_manifest_json"] = Path(summary.run_manifest_path)
        manifest = build_manifest(
            stage="llm_generate",
            config=replay_config,
            backend_mode=replay_config.backend.mode,
            backend_versions=_backend_versions_for_stage(replay_config, "generate"),
            output_paths=output_paths,
            source_lineage=replay_source_lineage,
        )
        write_manifest(manifest, llm_generate_manifest_path)

        replay_summary = LlmCampaignLaunchSummary(
            launch_id=launch_id,
            campaign_id=source_bundle.campaign_spec.campaign_id,
            campaign_spec_path=str(source_bundle.campaign_spec_path),
            proposal_id=source_bundle.campaign_spec.proposal_id,
            approval_id=source_bundle.campaign_spec.approval_id,
            system=source_bundle.campaign_spec.system,
            status="succeeded",
            created_at_utc=datetime.now(UTC).isoformat(),
            requested_count=source_bundle.launch_summary.requested_count,
            requested_model_lanes=list(source_bundle.launch_summary.requested_model_lanes),
            resolved_model_lane=source_bundle.launch_summary.resolved_model_lane,
            resolved_model_lane_source=source_bundle.launch_summary.resolved_model_lane_source,
            resolved_launch_path=str(resolved_launch_path),
            run_manifest_path=summary.run_manifest_path,
            llm_generate_manifest_path=str(llm_generate_manifest_path),
            candidates_path=str(out_path),
            replay_of_launch_id=source_bundle.launch_summary.launch_id,
            replay_of_launch_summary_path=str(source_bundle.launch_summary_path),
            current_system_config_hash=current_hash,
        )
        write_json_object(replay_summary.model_dump(mode="json"), replay_launch_summary_path)
        typer.echo(replay_summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError, RuntimeError) as exc:
        if "source_bundle" in locals() and "launch_id" in locals():
            resolved_launch_path = llm_campaign_resolved_launch_path(
                source_bundle.campaign_spec.campaign_id,
                launch_id,
                root=workspace_root(),
            )
            failed_summary = LlmCampaignLaunchSummary(
                launch_id=launch_id,
                campaign_id=source_bundle.campaign_spec.campaign_id,
                campaign_spec_path=str(source_bundle.campaign_spec_path),
                proposal_id=source_bundle.campaign_spec.proposal_id,
                approval_id=source_bundle.campaign_spec.approval_id,
                system=source_bundle.campaign_spec.system,
                status="failed",
                created_at_utc=datetime.now(UTC).isoformat(),
                requested_count=source_bundle.launch_summary.requested_count,
                requested_model_lanes=list(source_bundle.launch_summary.requested_model_lanes),
                resolved_model_lane=source_bundle.launch_summary.resolved_model_lane,
                resolved_model_lane_source=source_bundle.launch_summary.resolved_model_lane_source,
                resolved_launch_path=str(resolved_launch_path),
                run_manifest_path=(None if "summary" not in locals() else summary.run_manifest_path),
                llm_generate_manifest_path=(
                    None
                    if "llm_generate_manifest_path" not in locals()
                    else str(llm_generate_manifest_path)
                ),
                candidates_path=(str(out_path) if "out_path" in locals() else None),
                error_kind=type(exc).__name__,
                error_message=str(exc),
                replay_of_launch_id=source_bundle.launch_summary.launch_id,
                replay_of_launch_summary_path=str(source_bundle.launch_summary_path),
                current_system_config_hash=(
                    None if "current_hash" not in locals() else current_hash
                ),
            )
            write_json_object(
                failed_summary.model_dump(mode="json"),
                llm_campaign_launch_summary_path(
                    source_bundle.campaign_spec.campaign_id,
                    launch_id,
                    root=workspace_root(),
                ),
            )
        _emit_error(f"llm-replay failed: {exc}")
        raise typer.Exit(code=2)


@app.command("llm-compare")
def llm_compare_command(
    launch_summary: Path = typer.Option(..., "--launch-summary", exists=False, dir_okay=False),
) -> None:
    """Compare a launch against its acceptance-pack baseline and prior launch when available."""
    try:
        bundle = load_campaign_launch_bundle(launch_summary, root=workspace_root())
        current_outcome = build_campaign_outcome_snapshot(bundle, root=workspace_root())
        comparison = build_campaign_comparison(
            bundle,
            current_outcome=current_outcome,
            root=workspace_root(),
        )
        comparison_path = llm_campaign_comparison_path(
            comparison.campaign_id,
            comparison.comparison_id,
            root=workspace_root(),
        )
        outcome_snapshot_path = llm_campaign_outcome_snapshot_path(
            comparison.campaign_id,
            comparison.launch_id,
            root=workspace_root(),
        )
        for line in comparison.summary_lines:
            typer.echo(line)
        typer.echo(f"Outcome snapshot: {outcome_snapshot_path}")
        typer.echo(f"Comparison artifact: {comparison_path}")
    except (FileNotFoundError, ValidationError, ValueError, RuntimeError) as exc:
        _emit_error(f"llm-compare failed: {exc}")
        raise typer.Exit(code=2)


@app.command("export-zomic")
def export_zomic_command(
    design: Path = typer.Option(..., "--design", exists=False, dir_okay=False),
    out: Path | None = typer.Option(None, "--out", exists=False, dir_okay=False),
    force: bool = typer.Option(False, "--force"),
) -> None:
    """Compile a Zomic design into an orbit-library prototype JSON file."""
    try:
        summary: ZomicExportSummary = export_zomic_design(design, output_path=out, force=force)
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError, RuntimeError) as exc:
        _emit_error(f"export-zomic failed: {exc}")
        raise typer.Exit(code=2)


@app.command("screen")
def screen_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
) -> None:
    """Run M3 fast-screening: proxy relax, threshold filter, and shortlist ranking."""
    try:
        system_config = _load_system_config(config)
        system_slug = _system_slug(system_config.system_name)

        input_path = workspace_root() / "data" / "candidates" / f"{system_slug}_candidates.jsonl"
        if not input_path.exists():
            raise FileNotFoundError(
                "screen input candidates file not found; run 'mdisc generate' first: "
                f"{input_path}"
            )

        output_path = workspace_root() / "data" / "screened" / f"{system_slug}_screened.jsonl"

        raw_candidates = load_jsonl(input_path)
        candidates = [CandidateRecord.model_validate(row) for row in raw_candidates]
        campaign_lineage = _resolve_campaign_lineage(system_slug, candidates)
        relaxed = run_fast_relaxation(system_config, candidates)

        min_distance = DEFAULT_MIN_DISTANCE_PROXY
        max_energy = DEFAULT_MAX_ENERGY_PROXY
        if system_config.backend.mode == "real":
            energy_values = [
                float((candidate.screen or {})["energy_proxy_ev_per_atom"]) for candidate in relaxed
            ]
            distance_values = [
                float((candidate.screen or {})["min_distance_proxy"]) for candidate in relaxed
            ]
            max_energy = round(_quantile(energy_values, 0.65), 6)
            min_distance = round(_quantile(distance_values, 0.30), 6)

        passing, _ = apply_screen_thresholds(
            relaxed,
            min_distance_proxy=min_distance,
            max_energy_proxy=max_energy,
        )
        shortlisted = rank_screen_shortlist(passing)
        write_jsonl([candidate.model_dump() for candidate in shortlisted], output_path)

        calibration = screening_calibration(
            input_count=len(candidates),
            relaxed_count=len(relaxed),
            passed_count=len(passing),
            shortlisted_count=len(shortlisted),
            min_distance_proxy=min_distance,
            max_energy_proxy=max_energy,
        )
        calibration_path = (
            workspace_root() / "data" / "calibration" / f"{system_slug}_screen_calibration.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(calibration, sort_keys=True), encoding="utf-8")

        manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_screen_manifest.json"
        )
        manifest = build_manifest(
            stage="screen",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=_backend_versions_for_stage(system_config, "screen"),
            output_paths={
                "screened_jsonl": output_path,
                "screen_calibration_json": calibration_path,
            },
            source_lineage=campaign_lineage,
        )
        write_manifest(manifest, manifest_path)

        summary = ScreenSummary(
            input_count=len(candidates),
            relaxed_count=len(relaxed),
            passed_count=len(passing),
            shortlisted_count=len(shortlisted),
            output_path=str(output_path),
            calibration_path=str(calibration_path),
            manifest_path=str(manifest_path),
        )
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"screen failed: {exc}")
        raise typer.Exit(code=2)


@app.command("hifi-validate")
def hifi_validate_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
    batch: str = typer.Option(..., "--batch"),
) -> None:
    """Run M4 no-DFT high-fidelity digital validation on shortlisted candidates."""
    try:
        system_config = _load_system_config(config)
        system_slug = _system_slug(system_config.system_name)

        input_path = workspace_root() / "data" / "screened" / f"{system_slug}_screened.jsonl"
        if not input_path.exists():
            raise FileNotFoundError(
                "hifi-validate input screened file not found; run 'mdisc screen' first: "
                f"{input_path}"
            )

        output_path = (
            workspace_root()
            / "data"
            / "hifi_validated"
            / f"{system_slug}_{_batch_slug(batch)}_validated.jsonl"
        )

        raw_candidates = load_jsonl(input_path)
        candidates = [CandidateRecord.model_validate(row) for row in raw_candidates]
        selected = _select_hifi_batch(candidates, batch)
        campaign_lineage = _resolve_campaign_lineage(system_slug, selected)

        validated = run_committee_relaxation(system_config, selected, batch)
        validated = compute_committee_uncertainty(validated)
        validated = compute_proxy_hull(validated, config=system_config)
        validated = run_geometry_prefilter(validated, config=system_config)
        validated = run_mlip_phonon_checks(validated, config=system_config)
        validated = run_short_md_stability(validated, config=system_config)
        validated = validate_xrd_signatures(system_config, validated)
        validated, passed_count = _finalize_validation(validated)

        write_jsonl([candidate.model_dump() for candidate in validated], output_path)

        calibration = validation_calibration(validated)
        calibration_path = (
            workspace_root()
            / "data"
            / "calibration"
            / f"{system_slug}_{_batch_slug(batch)}_validation_calibration.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(calibration, sort_keys=True), encoding="utf-8")

        manifest_path = (
            workspace_root()
            / "data"
            / "manifests"
            / f"{system_slug}_{_batch_slug(batch)}_hifi_validate_manifest.json"
        )
        manifest = build_manifest(
            stage="hifi_validate",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=_backend_versions_for_stage(system_config, "validate"),
            output_paths={
                "hifi_validated_jsonl": output_path,
                "validation_calibration_json": calibration_path,
            },
            source_lineage=campaign_lineage,
        )
        write_manifest(manifest, manifest_path)

        summary = HifiValidateSummary(
            batch=batch,
            input_count=len(candidates),
            validated_count=len(validated),
            passed_count=passed_count,
            output_path=str(output_path),
            calibration_path=str(calibration_path),
            manifest_path=str(manifest_path),
        )
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"hifi-validate failed: {exc}")
        raise typer.Exit(code=2)


@app.command("hifi-rank")
def hifi_rank_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
) -> None:
    """Run M6 ranking over validated candidates with deterministic uncertainty-aware scoring."""
    try:
        system_config = _load_system_config(config)
        system_slug = _system_slug(system_config.system_name)

        benchmark_ctx = _load_benchmark_context(system_config, system_slug)
        bm_ctx_dict = benchmark_ctx.as_dict()

        validated = _load_validated_candidates(system_slug)
        campaign_lineage = _resolve_campaign_lineage(system_slug, validated)
        # Pass benchmark context so it is embedded in every ranked candidate's provenance.
        enriched_ranked = rank_validated_candidates(
            system_config, validated, benchmark_context=bm_ctx_dict
        )

        output_path = workspace_root() / "data" / "ranked" / f"{system_slug}_ranked.jsonl"
        write_jsonl([candidate.model_dump() for candidate in enriched_ranked], output_path)

        calibration = ranking_calibration(enriched_ranked)
        calibration_path = (
            workspace_root() / "data" / "calibration" / f"{system_slug}_ranking_calibration.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(calibration, sort_keys=True), encoding="utf-8")

        manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_hifi_rank_manifest.json"
        )
        manifest = build_manifest(
            stage="hifi_rank",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=_backend_versions_for_stage(system_config, "rank"),
            output_paths={
                "ranked_jsonl": output_path,
                "ranking_calibration_json": calibration_path,
            },
            source_lineage=campaign_lineage,
            benchmark_context=bm_ctx_dict,
        )
        write_manifest(manifest, manifest_path)

        summary = HifiRankSummary(
            input_count=len(validated),
            ranked_count=len(enriched_ranked),
            passed_count=sum(
                candidate.digital_validation.passed_checks is True for candidate in enriched_ranked
            ),
            output_path=str(output_path),
            calibration_path=str(calibration_path),
            manifest_path=str(manifest_path),
        )
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"hifi-rank failed: {exc}")
        raise typer.Exit(code=2)


@app.command("active-learn")
def active_learn_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
) -> None:
    """Run M5 active learning over validated candidates and propose next candidate batch."""
    try:
        system_config = _load_system_config(config)
        system_slug = _system_slug(system_config.system_name)

        candidates_path = (
            workspace_root() / "data" / "candidates" / f"{system_slug}_candidates.jsonl"
        )
        if not candidates_path.exists():
            raise FileNotFoundError(
                "active-learn candidate pool not found; run 'mdisc generate' first: "
                f"{candidates_path}"
            )

        validated = _load_validated_candidates(system_slug)
        validated = _enrich_validated_with_ranked(system_slug, validated)
        campaign_lineage = _resolve_campaign_lineage(system_slug, validated)
        validated_ids = {candidate.candidate_id for candidate in validated}
        candidate_pool = _load_active_learning_pool(system_slug, validated_ids)

        remaining = sum(candidate.candidate_id not in validated_ids for candidate in candidate_pool)
        if remaining <= 0:
            raise ValueError(
                "no unvalidated candidates remain in the pool; generate additional candidates first"
            )

        surrogate = train_surrogate_model(system_config, validated)
        batch_size = min(system_config.default_count, remaining)
        selected = select_next_candidate_batch(
            system_config,
            candidate_pool,
            validated_ids,
            surrogate,
            batch_size=batch_size,
        )

        surrogate_path = (
            workspace_root() / "data" / "active_learning" / f"{system_slug}_surrogate.json"
        )
        batch_path = (
            workspace_root() / "data" / "active_learning" / f"{system_slug}_next_batch.jsonl"
        )
        feature_store_path = (
            workspace_root()
            / "data"
            / "registry"
            / "features"
            / f"{system_slug}_validated_features.jsonl"
        )
        model_registry_path = (
            workspace_root() / "data" / "registry" / "models" / f"{system_slug}_models.jsonl"
        )

        ensure_parent(surrogate_path)
        surrogate_path.write_text(
            json.dumps(surrogate.model_dump(), sort_keys=True),
            encoding="utf-8",
        )
        write_jsonl([candidate.model_dump() for candidate in selected], batch_path)
        feature_rows = []
        for candidate in validated:
            rank_info = candidate.provenance.get("hifi_rank") or {}
            features = candidate_feature_map(system_config, candidate)
            feature_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "system": system_config.system_name,
                    "composition": candidate.composition,
                    "features": features,
                    "uncertainty_ev_per_atom": candidate.digital_validation.uncertainty_ev_per_atom,
                    "delta_e_proxy_hull_ev_per_atom": (
                        candidate.digital_validation.delta_e_proxy_hull_ev_per_atom
                    ),
                    "proxy_hull_reference_distance": (
                        candidate.digital_validation.proxy_hull_reference_distance
                    ),
                    "hifi_rank_score": rank_info.get("score"),
                    "stability_probability": rank_info.get("stability_probability"),
                    "ood_score": rank_info.get("ood_score"),
                    "passed_checks": candidate.digital_validation.passed_checks,
                }
            )
        write_jsonl(feature_rows, feature_store_path)

        digest = hashlib.sha256(
            json.dumps(surrogate.model_dump(), sort_keys=True).encode()
        ).hexdigest()
        model_id = f"surrogate_{digest[:12]}"
        append_jsonl(
            {
                "model_id": model_id,
                "system": system_config.system_name,
                "created_at_utc": datetime.now(UTC).isoformat(),
                "training_rows": surrogate.training_rows,
                "positive_count": surrogate.positive_count,
                "negative_count": surrogate.negative_count,
                "pass_rate": surrogate.pass_rate,
                "decision_threshold": surrogate.decision_threshold,
                "separation_margin": surrogate.separation_margin,
                "training_radius": surrogate.training_radius,
                "top_k_precision": surrogate.top_k_precision,
                "mean_predicted_success": surrogate.mean_predicted_success,
                "surrogate_path": str(surrogate_path),
            },
            model_registry_path,
        )

        manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_active_learn_manifest.json"
        )
        manifest = build_manifest(
            stage="active_learn",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=_backend_versions_for_stage(system_config, "active_learning"),
            output_paths={
                "surrogate_json": surrogate_path,
                "next_batch_jsonl": batch_path,
                "feature_store_jsonl": feature_store_path,
                "model_registry_jsonl": model_registry_path,
            },
            source_lineage=campaign_lineage,
        )
        write_manifest(manifest, manifest_path)

        summary = ActiveLearnSummary(
            validated_count=len(validated),
            selected_count=len(selected),
            pass_rate=surrogate.pass_rate,
            surrogate_path=str(surrogate_path),
            batch_path=str(batch_path),
            feature_store_path=str(feature_store_path),
            model_registry_path=str(model_registry_path),
            model_id=model_id,
            manifest_path=str(manifest_path),
        )
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"active-learn failed: {exc}")
        raise typer.Exit(code=2)


@app.command("report")
def report_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
) -> None:
    """Build an experiment-facing report with ranked candidates and synthetic XRD signatures."""
    try:
        system_config = _load_system_config(config)
        system_slug = _system_slug(system_config.system_name)

        benchmark_ctx = _load_benchmark_context(system_config, system_slug)
        bm_ctx_dict = benchmark_ctx.as_dict()

        ranked, ranked_source_path = _load_report_candidates(system_slug)
        campaign_lineage = _resolve_campaign_lineage(system_slug, ranked)
        xrd_patterns = simulate_powder_xrd_patterns(ranked)
        report = compile_experiment_report(system_config, ranked, xrd_patterns)

        # Inject benchmark/reference context into the report payload
        report["benchmark_context"] = bm_ctx_dict

        report_dir = workspace_root() / "data" / "reports"
        xrd_path = report_dir / f"{system_slug}_xrd_patterns.jsonl"
        report_path = report_dir / f"{system_slug}_report.json"

        write_jsonl(xrd_patterns, xrd_path)
        ensure_parent(report_path)
        report_path.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")

        calibration = report_calibration(report)
        calibration_path = (
            workspace_root() / "data" / "calibration" / f"{system_slug}_report_calibration.json"
        )
        ensure_parent(calibration_path)
        calibration_path.write_text(json.dumps(calibration, sort_keys=True), encoding="utf-8")

        manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_report_manifest.json"
        )
        report_manifest = build_manifest(
            stage="report",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=_backend_versions_for_stage(system_config, "report"),
            output_paths={
                "report_json": report_path,
                "xrd_patterns_jsonl": xrd_path,
                "report_calibration_json": calibration_path,
            },
            source_lineage=campaign_lineage,
            benchmark_context=bm_ctx_dict,
        )
        write_manifest(report_manifest, manifest_path)

        pipeline_manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_pipeline_manifest.json"
        )
        stage_paths: dict[str, Path] = {
            "report_json": report_path,
            "xrd_patterns_jsonl": xrd_path,
            "ranked_jsonl": workspace_root() / "data" / "ranked" / f"{system_slug}_ranked.jsonl",
            "candidates_jsonl": workspace_root()
            / "data"
            / "candidates"
            / f"{system_slug}_candidates.jsonl",
            "screened_jsonl": workspace_root()
            / "data"
            / "screened"
            / f"{system_slug}_screened.jsonl",
        }
        if ranked_source_path.name.endswith("_llm_evaluated.jsonl"):
            stage_paths["llm_evaluated_jsonl"] = ranked_source_path
        validated_paths = sorted(
            (workspace_root() / "data" / "hifi_validated").glob(f"{system_slug}_*_validated.jsonl")
        )
        if validated_paths:
            stage_paths["hifi_validated_jsonl"] = validated_paths[0]

        existing_stage_paths = {name: path for name, path in stage_paths.items() if path.exists()}
        pipeline_manifest = build_pipeline_manifest(
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=_backend_versions_for_stage(system_config, "pipeline"),
            stage_paths=existing_stage_paths,
            source_lineage=campaign_lineage,
        )
        write_pipeline_manifest(pipeline_manifest, pipeline_manifest_path)

        # Write dedicated benchmark-pack artifact
        benchmark_pack_path = (
            workspace_root() / "data" / "reports" / f"{system_slug}_benchmark_pack.json"
        )
        stage_manifest_refs: dict[str, str] = {
            "report_manifest": str(manifest_path),
            "pipeline_manifest": str(pipeline_manifest_path),
            "report_calibration": str(calibration_path),
        }
        hifi_rank_manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_hifi_rank_manifest.json"
        )
        if hifi_rank_manifest_path.exists():
            stage_manifest_refs["hifi_rank_manifest"] = str(hifi_rank_manifest_path)
        ingest_manifest_path = (
            workspace_root() / "data" / "manifests" / f"{system_slug}_ingest_manifest.json"
        )
        if ingest_manifest_path.exists():
            stage_manifest_refs["ingest_manifest"] = str(ingest_manifest_path)

        report_gate = report.get("release_gate", {})
        report_summary_slice = {
            k: v
            for k, v in (report.get("summary") or {}).items()
            if k
            in {
                "synthesize_count",
                "high_priority_count",
                "medium_priority_count",
                "stability_probability_mean",
                "xrd_confidence_mean",
            }
        }
        top_report_metrics = {
            "report_fingerprint": report.get("report_fingerprint", ""),
            "ranked_count": report.get("ranked_count", 0),
            "reported_count": report.get("reported_count", 0),
            "release_gate": report_gate,
            "summary": report_summary_slice,
        }
        write_benchmark_pack(
            config=system_config,
            benchmark_context=benchmark_ctx,
            stage_manifest_paths=stage_manifest_refs,
            report_metrics=top_report_metrics,
            output_path=benchmark_pack_path,
        )

        summary = ReportSummary(
            ranked_count=len(ranked),
            reported_count=int(report["reported_count"]),
            report_path=str(report_path),
            xrd_patterns_path=str(xrd_path),
            calibration_path=str(calibration_path),
            report_fingerprint=str(report.get("report_fingerprint", "")),
            manifest_path=str(manifest_path),
            pipeline_manifest_path=str(pipeline_manifest_path),
        )
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"report failed: {exc}")
        raise typer.Exit(code=2)


@lake_app.command("index")
def lake_index_cmd(
    root: Path = typer.Option(None, "--root", help="Workspace root override"),
) -> None:
    """Scan all artifact directories and write data/lake_index.json."""
    index = build_lake_index(root=root)
    output_path = write_lake_index(index, output_path=(root / "data" / "lake_index.json") if root else None)
    typer.echo(f"Lake index written to: {output_path}")
    typer.echo(f"  Artifact directories scanned: {index.artifact_directories}")
    typer.echo(f"  Total entries: {index.total_entries}")
    typer.echo(f"  Stale entries: {index.stale_count}")


@lake_app.command("stats")
def lake_stats_cmd(
    root: Path = typer.Option(None, "--root", help="Workspace root override"),
) -> None:
    """Print a summary table of the current lake index (rebuilds if missing)."""
    from materials_discovery.common.io import workspace_root as _ws_root
    ws = root or _ws_root()
    index_path = ws / "data" / "lake_index.json"
    if index_path.exists():
        import json as _json
        from materials_discovery.lake.index import LakeIndex
        data = _json.loads(index_path.read_text(encoding="utf-8"))
        index = LakeIndex.model_validate(data)
    else:
        typer.echo("lake_index.json not found — rebuilding...")
        index = build_lake_index(root=root)
        write_lake_index(index, output_path=index_path)

    stats = lake_stats(index)
    typer.echo("=== Lake Stats ===")
    typer.echo(f"  Workspace:            {stats['workspace_root']}")
    typer.echo(f"  Artifact directories: {stats['artifact_directories']}")
    typer.echo(f"  Total entries:        {stats['total_entries']}")
    typer.echo(f"  Stale entries:        {stats['stale_count']}")
    typer.echo(f"  Latest run:           {stats.get('latest_run_utc', 'n/a')}")
    typer.echo(f"  Generated at:         {stats['generated_at_utc']}")


@lake_app.command("compare")
def lake_compare_cmd(
    pack_a: Path = typer.Argument(..., help="Path to the first benchmark_pack.json"),
    pack_b: Path = typer.Argument(..., help="Path to the second benchmark_pack.json"),
    output_dir: Path = typer.Option(None, "--output-dir", help="Override comparison output directory"),
    json_only: bool = typer.Option(False, "--json-only", help="Write JSON only, suppress CLI table"),
) -> None:
    """Compare two benchmark packs and produce gate-level deltas and metric summaries.

    Accepts explicit benchmark-pack paths (D-08) and produces dual-format output:
    a JSON file in data/comparisons/ and a human-readable terminal table (D-06).
    """
    from materials_discovery.lake.compare import (
        compare_benchmark_packs,
        format_comparison_table,
        write_comparison,
    )

    if not pack_a.exists():
        _emit_error(f"Pack A not found: {pack_a}")
        raise typer.Exit(code=1)
    if not pack_b.exists():
        _emit_error(f"Pack B not found: {pack_b}")
        raise typer.Exit(code=1)

    result = compare_benchmark_packs(pack_a, pack_b)
    out_path = write_comparison(result, output_dir=output_dir)

    if not json_only:
        typer.echo(format_comparison_table(result))
    typer.echo(f"\nComparison JSON written to: {out_path}")


@llm_corpus_app.command("build")
def llm_corpus_build_cmd(
    config: Path = typer.Option(..., "--config", exists=True, dir_okay=False),
) -> None:
    try:
        raw = load_yaml(config)
        build_config = CorpusBuildConfig.model_validate(raw)
        summary = build_llm_corpus(build_config)
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(str(exc))
        raise typer.Exit(code=2) from exc

    typer.echo(summary.model_dump_json())


if __name__ == "__main__":
    app()
