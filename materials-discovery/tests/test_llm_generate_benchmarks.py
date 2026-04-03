from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from materials_discovery.cli import app
from materials_discovery.common.io import load_json_object
from materials_discovery.llm.benchmark import (
    build_llm_generate_comparison,
    write_llm_generate_comparison,
)


def _repo_workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _copy_sc_zn_seed(tmp_workspace: Path) -> None:
    seed_source = _repo_workspace() / "designs" / "zomic" / "sc_zn_tsai_bridge.zomic"
    seed_target = tmp_workspace / "designs" / "zomic" / "sc_zn_tsai_bridge.zomic"
    seed_target.parent.mkdir(parents=True, exist_ok=True)
    seed_target.write_text(seed_source.read_text(encoding="utf-8"), encoding="utf-8")


def _fake_compile_factory(fixture_name: str):
    def _fake_compile(
        zomic_text: str,
        *,
        artifact_root: Path | None = None,
        **_: object,
    ) -> dict[str, object]:
        del zomic_text
        prototype_path = _repo_workspace() / "data" / "prototypes" / fixture_name
        if artifact_root is None:
            orbit_library_path = prototype_path
            raw_export_path = prototype_path.with_suffix(".raw.json")
        else:
            artifact_root.mkdir(parents=True, exist_ok=True)
            orbit_library_path = artifact_root / "compiled.json"
            orbit_library_path.write_text(
                prototype_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            raw_export_path = artifact_root / "compiled.raw.json"
            raw_export_path.write_text("{}", encoding="utf-8")
        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "error_kind": None,
            "error_message": None,
            "raw_export_path": str(raw_export_path),
            "orbit_library_path": str(orbit_library_path),
            "cell_scale_used": 10.0,
            "geometry_equivalence": None,
            "geometry_error": None,
        }

    return _fake_compile


@pytest.mark.llm_lane
@pytest.mark.parametrize(
    ("system_name", "deterministic_config", "llm_config", "fixture_name"),
    [
        (
            "Al-Cu-Fe",
            "configs/systems/al_cu_fe.yaml",
            "configs/systems/al_cu_fe_llm_mock.yaml",
            "al_cu_fe_mackay_1_1.json",
        ),
        (
            "Sc-Zn",
            "configs/systems/sc_zn.yaml",
            "configs/systems/sc_zn_llm_mock.yaml",
            "sc_zn_tsai_sczn6.json",
        ),
    ],
)
def test_offline_llm_generate_benchmark_lane(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    system_name: str,
    deterministic_config: str,
    llm_config: str,
    fixture_name: str,
) -> None:
    repo_workspace = _repo_workspace()
    tmp_workspace = tmp_path / "workspace"
    tmp_workspace.mkdir(parents=True, exist_ok=True)
    _copy_sc_zn_seed(tmp_workspace)

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: tmp_workspace)
    monkeypatch.setattr("materials_discovery.llm.generate.workspace_root", lambda: tmp_workspace)
    monkeypatch.setattr(
        "materials_discovery.llm.generate.compile_zomic_script",
        _fake_compile_factory(fixture_name),
    )

    runner = CliRunner()
    deterministic_result = runner.invoke(
        app,
        [
            "generate",
            "--config",
            str(repo_workspace / deterministic_config),
            "--count",
            "3",
        ],
    )
    assert deterministic_result.exit_code == 0, deterministic_result.stdout
    deterministic_screen = runner.invoke(
        app,
        [
            "screen",
            "--config",
            str(repo_workspace / deterministic_config),
        ],
    )
    assert deterministic_screen.exit_code == 0, deterministic_screen.stdout

    llm_result = runner.invoke(
        app,
        [
            "llm-generate",
            "--config",
            str(repo_workspace / llm_config),
            "--count",
            "3",
        ],
    )
    assert llm_result.exit_code == 0, llm_result.stdout
    llm_screen = runner.invoke(
        app,
        [
            "screen",
            "--config",
            str(repo_workspace / llm_config),
        ],
    )
    assert llm_screen.exit_code == 0, llm_screen.stdout

    deterministic_summary = json.loads(deterministic_result.stdout)
    deterministic_screen_summary = json.loads(deterministic_screen.stdout)
    llm_summary = json.loads(llm_result.stdout)
    llm_screen_summary = json.loads(llm_screen.stdout)

    comparison = build_llm_generate_comparison(
        system_name,
        load_json_object(Path(deterministic_summary["calibration_path"])),
        load_json_object(Path(deterministic_screen_summary["calibration_path"])),
        load_json_object(Path(llm_summary["calibration_path"])),
        load_json_object(Path(llm_screen_summary["calibration_path"])),
    )
    out_path = write_llm_generate_comparison(
        comparison,
        tmp_workspace
        / "data"
        / "benchmarks"
        / "llm_generate"
        / f"{system_name.lower().replace('-', '_')}_comparison.json",
    )

    assert out_path.exists()
    assert comparison["system"] == system_name
    assert "deterministic_generation" in comparison
    assert "deterministic_screen" in comparison
    assert "llm_generation" in comparison
    assert "llm_screen" in comparison
    assert "comparison" in comparison

    metrics = comparison["comparison"]
    assert "parse_pass_rate_delta" in metrics
    assert "compile_pass_rate_delta" in metrics
    assert "conversion_rate_delta" in metrics
    assert "screen_pass_rate_delta" in metrics
    assert comparison["llm_generation"]["generated_count"] >= 1
    assert comparison["llm_screen"]["pass_rate"] >= 0.0
