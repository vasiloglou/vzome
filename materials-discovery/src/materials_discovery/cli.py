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
from materials_discovery.backends.registry import resolve_ingest_backend
from materials_discovery.common.io import (
    append_jsonl,
    ensure_parent,
    load_jsonl,
    load_yaml,
    workspace_root,
    write_jsonl,
)
from materials_discovery.common.manifest import build_manifest, write_manifest
from materials_discovery.common.pipeline_manifest import (
    build_pipeline_manifest,
    write_pipeline_manifest,
)
from materials_discovery.common.schema import (
    ActiveLearnSummary,
    CandidateRecord,
    HifiRankSummary,
    HifiValidateSummary,
    ReportSummary,
    ScreenSummary,
    SystemConfig,
    ZomicExportSummary,
)
from materials_discovery.common.stage_metrics import (
    generation_metrics,
    ranking_calibration,
    report_calibration,
    screening_calibration,
    validation_calibration,
)
from materials_discovery.data.ingest_hypodx import ingest_rows
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

app = typer.Typer(add_completion=False, help="No-DFT materials discovery CLI scaffold")


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


@app.command("ingest")
def ingest_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
    fixture: Path | None = typer.Option(None, "--fixture", exists=False, dir_okay=False),
    out: Path | None = typer.Option(None, "--out", exists=False, dir_okay=False),
) -> None:
    """Ingest and normalize fixture metadata into processed JSONL."""
    try:
        system_config = _load_system_config(config)
        backend = resolve_ingest_backend(
            system_config.backend.mode,
            system_config.backend.ingest_adapter,
        )
        backend_info = backend.info()
        raw_rows = backend.load_rows(system_config, fixture)

        default_out = (
            workspace_root()
            / "data"
            / "processed"
            / f"{_system_slug(system_config.system_name)}_reference_phases.jsonl"
        )
        out_path = out or default_out

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
        backend_versions[backend_info.name] = backend_info.version
        manifest = build_manifest(
            stage="ingest",
            config=system_config,
            backend_mode=system_config.backend.mode,
            backend_versions=backend_versions,
            output_paths={"processed_jsonl": out_path},
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

        validated = _load_validated_candidates(system_slug)
        ranked = rank_validated_candidates(system_config, validated)

        output_path = workspace_root() / "data" / "ranked" / f"{system_slug}_ranked.jsonl"
        write_jsonl([candidate.model_dump() for candidate in ranked], output_path)

        calibration = ranking_calibration(ranked)
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
        )
        write_manifest(manifest, manifest_path)

        summary = HifiRankSummary(
            input_count=len(validated),
            ranked_count=len(ranked),
            passed_count=sum(
                candidate.digital_validation.passed_checks is True for candidate in ranked
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

        ranked = _load_ranked_candidates(system_slug)
        xrd_patterns = simulate_powder_xrd_patterns(ranked)
        report = compile_experiment_report(system_config, ranked, xrd_patterns)

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
        )
        write_pipeline_manifest(pipeline_manifest, pipeline_manifest_path)

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


if __name__ == "__main__":
    app()
