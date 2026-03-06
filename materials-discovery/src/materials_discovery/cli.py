from __future__ import annotations

import json
import re
from pathlib import Path

import typer
from pydantic import ValidationError

from materials_discovery.active_learning.select_next_batch import select_next_candidate_batch
from materials_discovery.active_learning.train_surrogate import train_surrogate_model
from materials_discovery.backends.registry import resolve_ingest_backend
from materials_discovery.common.io import (
    ensure_parent,
    load_jsonl,
    load_yaml,
    workspace_root,
    write_jsonl,
)
from materials_discovery.common.manifest import build_manifest, write_manifest
from materials_discovery.common.schema import (
    ActiveLearnSummary,
    CandidateRecord,
    HifiRankSummary,
    HifiValidateSummary,
    ReportSummary,
    ScreenSummary,
    SystemConfig,
)
from materials_discovery.data.ingest_hypodx import ingest_rows
from materials_discovery.diffraction.compare_patterns import compile_experiment_report
from materials_discovery.diffraction.simulate_powder_xrd import simulate_powder_xrd_patterns
from materials_discovery.generator.candidate_factory import generate_candidates
from materials_discovery.hifi_digital.committee_relax import run_committee_relaxation
from materials_discovery.hifi_digital.hull_proxy import compute_proxy_hull
from materials_discovery.hifi_digital.md_stability import run_short_md_stability
from materials_discovery.hifi_digital.phonon_mlip import run_mlip_phonon_checks
from materials_discovery.hifi_digital.rank_candidates import rank_validated_candidates
from materials_discovery.hifi_digital.uncertainty import compute_committee_uncertainty
from materials_discovery.hifi_digital.xrd_validate import validate_xrd_signatures
from materials_discovery.screen.filter_thresholds import apply_screen_thresholds
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
        backend_versions = dict(system_config.backend.versions)
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

        default_out = (
            workspace_root()
            / "data"
            / "candidates"
            / f"{_system_slug(system_config.system_name)}_candidates.jsonl"
        )
        out_path = out or default_out

        summary = generate_candidates(system_config, out_path, count=count, seed=seed)
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"generate failed: {exc}")
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
        passing, _ = apply_screen_thresholds(relaxed)
        shortlisted = rank_screen_shortlist(passing)
        write_jsonl([candidate.model_dump() for candidate in shortlisted], output_path)

        summary = ScreenSummary(
            input_count=len(candidates),
            relaxed_count=len(relaxed),
            passed_count=len(passing),
            shortlisted_count=len(shortlisted),
            output_path=str(output_path),
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
        validated = compute_proxy_hull(validated)
        validated = run_mlip_phonon_checks(validated)
        validated = run_short_md_stability(validated)
        validated = validate_xrd_signatures(system_config, validated)
        validated, passed_count = _finalize_validation(validated)

        write_jsonl([candidate.model_dump() for candidate in validated], output_path)

        summary = HifiValidateSummary(
            batch=batch,
            input_count=len(candidates),
            validated_count=len(validated),
            passed_count=passed_count,
            output_path=str(output_path),
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

        summary = HifiRankSummary(
            input_count=len(validated),
            ranked_count=len(ranked),
            passed_count=sum(
                candidate.digital_validation.passed_checks is True for candidate in ranked
            ),
            output_path=str(output_path),
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

        candidate_pool = [
            CandidateRecord.model_validate(row) for row in load_jsonl(candidates_path)
        ]
        validated = _load_validated_candidates(system_slug)
        validated_ids = {candidate.candidate_id for candidate in validated}

        remaining = len(candidate_pool) - len(validated_ids)
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

        ensure_parent(surrogate_path)
        surrogate_path.write_text(
            json.dumps(surrogate.model_dump(), sort_keys=True),
            encoding="utf-8",
        )
        write_jsonl([candidate.model_dump() for candidate in selected], batch_path)

        summary = ActiveLearnSummary(
            validated_count=len(validated),
            selected_count=len(selected),
            pass_rate=surrogate.pass_rate,
            surrogate_path=str(surrogate_path),
            batch_path=str(batch_path),
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

        summary = ReportSummary(
            ranked_count=len(ranked),
            reported_count=int(report["reported_count"]),
            report_path=str(report_path),
            xrd_patterns_path=str(xrd_path),
        )
        typer.echo(summary.model_dump_json())
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"report failed: {exc}")
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
