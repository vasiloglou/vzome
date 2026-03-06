from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from pydantic import ValidationError

from materials_discovery.active_learning.train_surrogate import train_surrogate_model
from materials_discovery.common.io import load_yaml, workspace_root
from materials_discovery.common.schema import SystemConfig
from materials_discovery.data.ingest_hypodx import ingest_fixture
from materials_discovery.diffraction.compare_patterns import compile_experiment_report
from materials_discovery.generator.candidate_factory import generate_candidates
from materials_discovery.hifi_digital.committee_relax import run_committee_relaxation
from materials_discovery.hifi_digital.rank_candidates import rank_validated_candidates
from materials_discovery.screen.relax_fast import run_fast_relaxation

app = typer.Typer(add_completion=False, help="No-DFT materials discovery CLI scaffold")


def _emit_error(message: str) -> None:
    typer.echo(message, err=True)


def _load_system_config(path: Path) -> SystemConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    data = load_yaml(path)
    return SystemConfig.model_validate(data)


def _not_implemented(stage: str, target: str, err: NotImplementedError) -> None:
    payload: dict[str, Any] = {
        "stage": stage,
        "status": "not_implemented",
        "target": target,
        "message": str(err),
    }
    typer.echo(json.dumps(payload, sort_keys=True))
    raise typer.Exit(code=3)


@app.command("ingest")
def ingest_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
    fixture: Path | None = typer.Option(None, "--fixture", exists=False, dir_okay=False),
    out: Path | None = typer.Option(None, "--out", exists=False, dir_okay=False),
) -> None:
    """Ingest and normalize fixture metadata into processed JSONL."""
    try:
        system_config = _load_system_config(config)
        default_fixture = workspace_root() / "data" / "external" / "fixtures" / "hypodx_sample.json"
        fixture_path = fixture or default_fixture
        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

        default_out = (
            workspace_root()
            / "data"
            / "processed"
            / f"{system_config.system_name.lower().replace('-', '_')}_reference_phases.jsonl"
        )
        out_path = out or default_out

        summary = ingest_fixture(system_config, fixture_path, out_path)
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
            / f"{system_config.system_name.lower().replace('-', '_')}_candidates.jsonl"
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
    """Screen-stage placeholder command with explicit not-implemented contract."""
    try:
        system_config = _load_system_config(config)
        run_fast_relaxation(system_config)
    except NotImplementedError as exc:
        _not_implemented(
            "screen",
            "materials_discovery.screen.relax_fast.run_fast_relaxation",
            exc,
        )
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"screen failed: {exc}")
        raise typer.Exit(code=2)


@app.command("hifi-validate")
def hifi_validate_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
    batch: str = typer.Option(..., "--batch"),
) -> None:
    """Hifi validation placeholder command with explicit not-implemented contract."""
    try:
        system_config = _load_system_config(config)
        run_committee_relaxation(system_config, batch)
    except NotImplementedError as exc:
        _not_implemented(
            "hifi-validate",
            "materials_discovery.hifi_digital.committee_relax.run_committee_relaxation",
            exc,
        )
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"hifi-validate failed: {exc}")
        raise typer.Exit(code=2)


@app.command("hifi-rank")
def hifi_rank_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
) -> None:
    """Hifi ranking placeholder command with explicit not-implemented contract."""
    try:
        system_config = _load_system_config(config)
        rank_validated_candidates(system_config)
    except NotImplementedError as exc:
        _not_implemented(
            "hifi-rank",
            "materials_discovery.hifi_digital.rank_candidates.rank_validated_candidates",
            exc,
        )
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"hifi-rank failed: {exc}")
        raise typer.Exit(code=2)


@app.command("active-learn")
def active_learn_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
) -> None:
    """Active-learning placeholder command with explicit not-implemented contract."""
    try:
        system_config = _load_system_config(config)
        train_surrogate_model(system_config)
    except NotImplementedError as exc:
        _not_implemented(
            "active-learn",
            "materials_discovery.active_learning.train_surrogate.train_surrogate_model",
            exc,
        )
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"active-learn failed: {exc}")
        raise typer.Exit(code=2)


@app.command("report")
def report_command(
    config: Path = typer.Option(..., "--config", exists=False, dir_okay=False),
) -> None:
    """Report placeholder command with explicit not-implemented contract."""
    try:
        system_config = _load_system_config(config)
        compile_experiment_report(system_config)
    except NotImplementedError as exc:
        _not_implemented(
            "report",
            "materials_discovery.diffraction.compare_patterns.compile_experiment_report",
            exc,
        )
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        _emit_error(f"report failed: {exc}")
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
