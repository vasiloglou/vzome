"""Smoke tests for analytics notebooks.

Static tests (structure, imports, workspace_root usage) always run.
Execution tests require nbformat and nbconvert and are skipped when those
packages are not installed.

Addresses review concern #4 (notebook maintainability).
"""
from __future__ import annotations

import json
import textwrap
import warnings
from pathlib import Path
from typing import Any

import pytest

NOTEBOOK_DIR = Path(__file__).resolve().parents[1] / "notebooks"

# ---------------------------------------------------------------------------
# Lazy nbformat/nbconvert availability check
# ---------------------------------------------------------------------------

try:
    import nbformat as _nbformat
    from nbconvert.preprocessors import ExecutePreprocessor as _ExecutePreprocessor
    _HAS_NBCONVERT = True
except ImportError:
    _HAS_NBCONVERT = False

_requires_nbconvert = pytest.mark.skipif(
    not _HAS_NBCONVERT,
    reason="nbformat/nbconvert not installed — skipping notebook execution smoke tests",
)

NOTEBOOK_TIMEOUT = 120  # seconds per notebook

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_fixture_report(directory: Path, system_slug: str) -> Path:
    """Write a minimal report JSON with two synthetic entries."""
    entries = [
        {
            "candidate_id": f"{system_slug}_cand_001",
            "hifi_score": 0.25,
            "stability_probability": 0.82,
            "ood_score": 0.15,
            "xrd_confidence": 0.77,
            "xrd_distinctiveness": 0.65,
            "evidence": {
                "delta_e_proxy_hull_ev_per_atom": -0.12,
                "uncertainty_ev_per_atom": 0.03,
                "md_stability_score": 0.91,
            },
            "benchmark_context": {"source_keys": ["hypodx"]},
        },
        {
            "candidate_id": f"{system_slug}_cand_002",
            "hifi_score": 0.45,
            "stability_probability": 0.60,
            "ood_score": 0.28,
            "xrd_confidence": 0.55,
            "xrd_distinctiveness": 0.42,
            "evidence": {
                "delta_e_proxy_hull_ev_per_atom": -0.07,
                "uncertainty_ev_per_atom": 0.05,
                "md_stability_score": 0.78,
            },
            "benchmark_context": {"source_keys": ["materials_project"]},
        },
    ]
    report_data = {"schema_version": "report/v1", "entries": entries}
    reports_dir = directory / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{system_slug}_report.json"
    report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    return report_path


def _write_fixture_benchmark_pack(directory: Path, system: str, lane_id: str) -> Path:
    """Write a minimal benchmark_pack.json."""
    pack = {
        "schema_version": "benchmark-pack/v1",
        "system": system,
        "backend_mode": "mock",
        "benchmark_context": {
            "lane_id": lane_id,
            "reference_pack_id": "test_ref_v1",
            "source_keys": ["hypodx"],
        },
        "report_metrics": {
            "release_gate": {"min_hifi_candidates": True, "min_xrd_confidence": False},
            "summary": {"hifi_score_mean": 0.35, "candidate_count": 2},
        },
        "stage_manifest_paths": {},  # no dereferenced report in fixture
    }
    benchmarks_dir = directory / "data" / "benchmarks"
    benchmarks_dir.mkdir(parents=True, exist_ok=True)
    slug = system.lower().replace("-", "_")
    pack_path = benchmarks_dir / f"{slug}_benchmark.json"
    pack_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return pack_path


@pytest.fixture()
def fixture_workspace(tmp_path: Path) -> Path:
    """Create a minimal workspace with fixture data for all three notebooks."""
    _write_fixture_report(tmp_path, "al_cu_fe")
    _write_fixture_benchmark_pack(tmp_path, "Al-Cu-Fe", "al_cu_fe:mock")
    _write_fixture_benchmark_pack(tmp_path, "Sc-Zn", "sc_zn:mock")
    return tmp_path


# ---------------------------------------------------------------------------
# Execution helpers (require nbformat/nbconvert)
# ---------------------------------------------------------------------------


def _load_notebook(path: Path) -> Any:
    """Load a notebook from disk using nbformat."""
    return _nbformat.read(str(path), as_version=4)


def _prepend_workspace_override(nb: Any, workspace_path: Path) -> Any:
    """Inject a cell at position 0 that overrides workspace_root() for the smoke test."""
    override_source = textwrap.dedent(f"""\
        # Injected by test_notebooks.py — override workspace_root for smoke test
        import unittest.mock as _mock
        from pathlib import Path as _Path
        _fixture_workspace = _Path(r"{workspace_path}")
        _patcher = _mock.patch(
            "materials_discovery.common.io.workspace_root",
            return_value=_fixture_workspace,
        )
        _patcher.start()
        # Also patch the copy that lake/compare and lake/index import
        for _mod_name in [
            "materials_discovery.lake.compare",
            "materials_discovery.lake.index",
            "materials_discovery.data_sources.storage",
        ]:
            import importlib as _importlib
            try:
                _m = _importlib.import_module(_mod_name)
                if hasattr(_m, "workspace_root"):
                    _mock.patch.object(_m, "workspace_root", return_value=_fixture_workspace).start()
            except ImportError:
                pass
    """)
    override_cell = _nbformat.v4.new_code_cell(source=override_source)
    nb.cells.insert(0, override_cell)
    return nb


def _execute_notebook(nb: Any, notebook_path: Path) -> None:
    """Execute a notebook in place, raising on cell errors."""
    ep = _ExecutePreprocessor(timeout=NOTEBOOK_TIMEOUT, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": str(notebook_path.parent)}})


# ---------------------------------------------------------------------------
# Static tests (always run — no nbformat/nbconvert needed)
# ---------------------------------------------------------------------------


def test_all_notebooks_are_valid_json() -> None:
    """Verify all three notebooks are valid .ipynb JSON files."""
    notebooks = [
        "source_contribution_analysis.ipynb",
        "cross_run_drift_detection.ipynb",
        "metric_distribution_deep_dive.ipynb",
    ]
    for name in notebooks:
        path = NOTEBOOK_DIR / name
        assert path.exists(), f"Missing notebook: {name}"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "cells" in data, f"Notebook {name} has no 'cells' key"
        assert "nbformat" in data, f"Notebook {name} has no 'nbformat' key"


def test_notebooks_import_from_materials_discovery() -> None:
    """Verify each notebook contains at least one import from materials_discovery."""
    notebooks = [
        "source_contribution_analysis.ipynb",
        "cross_run_drift_detection.ipynb",
        "metric_distribution_deep_dive.ipynb",
    ]
    for name in notebooks:
        path = NOTEBOOK_DIR / name
        assert path.exists(), f"Missing notebook: {name}"
        content = path.read_text(encoding="utf-8")
        assert "from materials_discovery" in content, (
            f"Notebook {name} does not import from materials_discovery"
        )


def test_notebooks_use_workspace_root() -> None:
    """Verify each notebook uses workspace_root for data path construction."""
    notebooks = [
        "source_contribution_analysis.ipynb",
        "cross_run_drift_detection.ipynb",
        "metric_distribution_deep_dive.ipynb",
    ]
    for name in notebooks:
        path = NOTEBOOK_DIR / name
        assert path.exists(), f"Missing notebook: {name}"
        content = path.read_text(encoding="utf-8")
        assert "workspace_root" in content, (
            f"Notebook {name} does not use workspace_root"
        )


# ---------------------------------------------------------------------------
# Execution smoke tests (require nbformat + nbconvert)
# ---------------------------------------------------------------------------


@_requires_nbconvert
def test_source_contribution_analysis_notebook(fixture_workspace: Path) -> None:
    """Smoke test: source_contribution_analysis.ipynb runs without CellExecutionError."""
    path = NOTEBOOK_DIR / "source_contribution_analysis.ipynb"
    assert path.exists(), f"Notebook not found: {path}"
    nb = _load_notebook(path)
    nb = _prepend_workspace_override(nb, fixture_workspace)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _execute_notebook(nb, path)


@_requires_nbconvert
def test_cross_run_drift_detection_notebook(fixture_workspace: Path) -> None:
    """Smoke test: cross_run_drift_detection.ipynb runs without CellExecutionError."""
    path = NOTEBOOK_DIR / "cross_run_drift_detection.ipynb"
    assert path.exists(), f"Notebook not found: {path}"
    nb = _load_notebook(path)
    nb = _prepend_workspace_override(nb, fixture_workspace)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _execute_notebook(nb, path)


@_requires_nbconvert
def test_metric_distribution_deep_dive_notebook(fixture_workspace: Path) -> None:
    """Smoke test: metric_distribution_deep_dive.ipynb runs without CellExecutionError."""
    path = NOTEBOOK_DIR / "metric_distribution_deep_dive.ipynb"
    assert path.exists(), f"Notebook not found: {path}"
    nb = _load_notebook(path)
    nb = _prepend_workspace_override(nb, fixture_workspace)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _execute_notebook(nb, path)
