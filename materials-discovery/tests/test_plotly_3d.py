"""Tests for materials_discovery.visualization.plotly_3d — orbit and shell figures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import plotly.graph_objects as go

import materials_discovery.visualization.plotly_3d as plotly_3d_mod
from materials_discovery.visualization.plotly_3d import (
    load_orbit_library,
    orbit_figure,
    shell_figure,
    _VIZ_AVAILABLE,
)
from materials_discovery.visualization.labels import ORBIT_COLORS, SHELL_NAMES

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ORBIT_LIB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "prototypes"
    / "generated"
    / "sc_zn_tsai_bridge.json"
)


@pytest.fixture(scope="module")
def orbit_lib_data() -> dict:
    """Load the real sc_zn_tsai_bridge orbit library for integration-style tests."""
    return json.loads(ORBIT_LIB_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fig_orbit(orbit_lib_data: dict) -> go.Figure:
    """Pre-built orbit figure (module-scoped for performance)."""
    return orbit_figure(orbit_lib_data)


@pytest.fixture(scope="module")
def fig_shell(orbit_lib_data: dict) -> go.Figure:
    """Pre-built shell figure (module-scoped for performance)."""
    return shell_figure(orbit_lib_data)


# ---------------------------------------------------------------------------
# orbit_figure tests (VIZ-01)
# ---------------------------------------------------------------------------


def test_orbit_figure_has_five_traces(fig_orbit: go.Figure) -> None:
    """orbit_figure() returns exactly 5 Scatter3d traces, one per anchor orbit."""
    assert len(fig_orbit.data) == 5
    for trace in fig_orbit.data:
        assert isinstance(trace, go.Scatter3d), f"Expected Scatter3d, got {type(trace)}"


def test_orbit_figure_trace_colors(fig_orbit: go.Figure) -> None:
    """Each trace's marker.color matches ORBIT_COLORS for the corresponding anchor orbit."""
    trace_colors = {trace.marker.color for trace in fig_orbit.data}
    expected_colors = set(ORBIT_COLORS.values())
    assert trace_colors == expected_colors, (
        f"Color mismatch: got {trace_colors!r}, expected {expected_colors!r}"
    )


def test_orbit_figure_hover_text(fig_orbit: go.Figure) -> None:
    """Every trace text matches hover format; at least one entry for tsai_zn7 + shell name."""
    all_texts: list[str] = []
    for trace in fig_orbit.data:
        all_texts.extend(trace.text)

    # Check overall format: each text must contain '(' and ')' and ' - '
    for text in all_texts:
        assert "(" in text and ")" in text and " - " in text, (
            f"Hover text has wrong format: {text!r}"
        )

    # Verify at least one entry for the inner Zn7 orbit
    assert any("(tsai_zn7)" in t for t in all_texts), (
        "No hover text found containing '(tsai_zn7)'"
    )
    assert any("Zn inner shell" in t for t in all_texts), (
        "No hover text found containing 'Zn inner shell'"
    )


def test_orbit_figure_marker_size(fig_orbit: go.Figure) -> None:
    """All 5 traces have marker.size == 8."""
    for trace in fig_orbit.data:
        assert trace.marker.size == 8, (
            f"Trace '{trace.name}' has marker.size={trace.marker.size}, expected 8"
        )


def test_orbit_figure_total_points(fig_orbit: go.Figure) -> None:
    """Sum of site counts across all 5 traces equals 100."""
    total = sum(len(trace.x) for trace in fig_orbit.data)
    assert total == 100, f"Expected 100 total sites, got {total}"


# ---------------------------------------------------------------------------
# shell_figure tests (VIZ-02)
# ---------------------------------------------------------------------------


def test_shell_figure_shell_ordering(fig_shell: go.Figure) -> None:
    """Scatter3d marker traces are ordered by mean radial distance, innermost first.

    Expected order (from RESEARCH.md):
        tsai_zn6 (5.97 A) < tsai_zn7 (6.13 A) < tsai_zn5 (6.57 A)
        < tsai_sc1 (6.73 A) < tsai_zn4 (7.73 A)

    The first marker trace name should contain 'Zn middle shell' (tsai_zn6)
    and the last marker trace name should contain 'Zn outer shell' (tsai_zn4).
    """
    marker_traces = [
        t
        for t in fig_shell.data
        if isinstance(t, go.Scatter3d) and t.mode == "markers"
    ]
    assert len(marker_traces) == 5, (
        f"Expected 5 marker traces, got {len(marker_traces)}"
    )

    first_name = marker_traces[0].name
    last_name = marker_traces[-1].name

    assert "Zn middle shell" in first_name, (
        f"First shell (innermost) should be 'Zn middle shell' (tsai_zn6), got: {first_name!r}"
    )
    assert "Zn outer shell" in last_name, (
        f"Last shell (outermost) should be 'Zn outer shell' (tsai_zn4), got: {last_name!r}"
    )


def test_shell_figure_has_mesh3d_traces(fig_shell: go.Figure) -> None:
    """shell_figure() contains at least 5 Mesh3d traces (one cage per shell)."""
    mesh_count = sum(1 for t in fig_shell.data if isinstance(t, go.Mesh3d))
    assert mesh_count >= 5, (
        f"Expected at least 5 Mesh3d traces, got {mesh_count}"
    )


def test_shell_figure_legendgroup(fig_shell: go.Figure) -> None:
    """For each shell legendgroup, there exists at least one Scatter3d markers and one Mesh3d."""
    groups: dict[str, dict[str, bool]] = {}
    for trace in fig_shell.data:
        group = trace.legendgroup
        if group is None:
            continue
        if group not in groups:
            groups[group] = {"has_scatter_markers": False, "has_mesh3d": False}
        if isinstance(trace, go.Scatter3d) and trace.mode == "markers":
            groups[group]["has_scatter_markers"] = True
        if isinstance(trace, go.Mesh3d):
            groups[group]["has_mesh3d"] = True

    # Should have at least 5 legendgroups (one per shell)
    assert len(groups) >= 5, f"Expected at least 5 legendgroups, got {len(groups)}"

    for group, flags in groups.items():
        assert flags["has_scatter_markers"], (
            f"legendgroup '{group}' has no Scatter3d markers trace"
        )
        assert flags["has_mesh3d"], (
            f"legendgroup '{group}' has no Mesh3d cage trace"
        )


def test_shell_figure_mesh3d_opacity(fig_shell: go.Figure) -> None:
    """All Mesh3d cage traces have opacity == 0.15."""
    mesh_traces = [t for t in fig_shell.data if isinstance(t, go.Mesh3d)]
    assert mesh_traces, "No Mesh3d traces found"
    for trace in mesh_traces:
        assert trace.opacity == 0.15, (
            f"Mesh3d trace '{trace.name}' has opacity={trace.opacity}, expected 0.15"
        )


def test_shell_figure_edge_wireframe(fig_shell: go.Figure) -> None:
    """shell_figure() contains Scatter3d traces in mode='lines' for edge wireframes."""
    line_traces = [
        t
        for t in fig_shell.data
        if isinstance(t, go.Scatter3d) and t.mode == "lines"
    ]
    assert len(line_traces) >= 1, (
        "Expected at least 1 Scatter3d lines trace for hull edge wireframe"
    )


# ---------------------------------------------------------------------------
# Import error guard test (ENRICH-03)
# ---------------------------------------------------------------------------


def test_import_error_message(monkeypatch: pytest.MonkeyPatch, orbit_lib_data: dict) -> None:
    """When _VIZ_AVAILABLE is False, orbit_figure raises ImportError with install hint."""
    monkeypatch.setattr(plotly_3d_mod, "_VIZ_AVAILABLE", False)
    monkeypatch.setattr(plotly_3d_mod, "_VIZ_IMPORT_ERROR", "No module named 'plotly'")

    with pytest.raises(ImportError, match=r"materials-discovery\[viz\]"):
        orbit_figure(orbit_lib_data)


# ---------------------------------------------------------------------------
# Stub importability tests (ENRICH-03)
# ---------------------------------------------------------------------------


def test_matplotlib_pub_importable() -> None:
    """import materials_discovery.visualization.matplotlib_pub succeeds without error."""
    import materials_discovery.visualization.matplotlib_pub  # noqa: F401


def test_expansion_importable() -> None:
    """import materials_discovery.visualization.expansion succeeds without error."""
    import materials_discovery.visualization.expansion  # noqa: F401


# ---------------------------------------------------------------------------
# [viz] extra declaration test (ENRICH-03)
# ---------------------------------------------------------------------------


def test_viz_extra_declared() -> None:
    """pyproject.toml [project.optional-dependencies] has [viz] with all required packages."""
    import tomllib

    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with open(pyproject, "rb") as f:
        config = tomllib.load(f)

    viz_deps: list[str] = config["project"]["optional-dependencies"]["viz"]

    required_prefixes = ("plotly", "matplotlib", "kaleido", "scipy", "nbformat")
    for prefix in required_prefixes:
        matching = [dep for dep in viz_deps if dep.startswith(prefix)]
        assert matching, (
            f"[viz] extra is missing a '{prefix}' dependency. Found: {viz_deps!r}"
        )


# ---------------------------------------------------------------------------
# load_orbit_library tests (ENRICH-03)
# ---------------------------------------------------------------------------


def test_load_orbit_library(orbit_lib_data: dict) -> None:
    """load_orbit_library() with real path returns dict with expected top-level keys."""
    result = load_orbit_library(ORBIT_LIB_PATH)
    assert isinstance(result, dict)
    assert "base_cell" in result, "Missing 'base_cell' key"
    assert "motif_center" in result, "Missing 'motif_center' key"
    assert "orbits" in result, "Missing 'orbits' key"
    assert len(result["orbits"]) == 5, (
        f"Expected 5 orbits, got {len(result['orbits'])}"
    )


def test_load_orbit_library_missing_file() -> None:
    """load_orbit_library() raises FileNotFoundError for a nonexistent path."""
    with pytest.raises(FileNotFoundError, match="orbit library not found"):
        load_orbit_library(Path("/nonexistent/path/that/does/not/exist.json"))
