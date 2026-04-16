"""Tests for materials_discovery.visualization.expansion — expansion_figure."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import plotly.graph_objects as go

import materials_discovery.visualization.expansion as expansion_mod
from materials_discovery.visualization.expansion import (
    expansion_figure,
    _EXPANSION_AVAILABLE,
)
from materials_discovery.visualization.labels import SHELL_NAMES

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
def fig_expansion(orbit_lib_data: dict) -> go.Figure:
    """Pre-built expansion figure (module-scoped for performance)."""
    return expansion_figure(orbit_lib_data)


# ---------------------------------------------------------------------------
# expansion_figure tests (ENRICH-02)
# ---------------------------------------------------------------------------


def test_expansion_figure_returns_go_figure(fig_expansion: go.Figure) -> None:
    """expansion_figure() returns a plotly go.Figure instance."""
    assert isinstance(fig_expansion, go.Figure), (
        f"Expected go.Figure, got {type(fig_expansion)}"
    )


def test_expansion_figure_has_five_traces(fig_expansion: go.Figure) -> None:
    """expansion_figure() returns exactly 5 Scatter3d traces, one per orbit."""
    assert len(fig_expansion.data) == 5, (
        f"Expected 5 traces, got {len(fig_expansion.data)}"
    )
    for trace in fig_expansion.data:
        assert isinstance(trace, go.Scatter3d), (
            f"Expected Scatter3d, got {type(trace)}"
        )


def test_expansion_figure_800_sites(fig_expansion: go.Figure) -> None:
    """Total marker points across all traces equals 800 (100 sites x 8 cells)."""
    total = sum(len(trace.x) for trace in fig_expansion.data)
    assert total == 800, (
        f"Expected 800 total marker points (100 sites x 8 cells), got {total}"
    )


def test_expansion_figure_central_cell_opacity(
    orbit_lib_data: dict, fig_expansion: go.Figure
) -> None:
    """Central cell sites have opacity 1.0; surrounding cell sites have opacity 0.3.

    Per-point opacity is encoded via RGBA color strings (plotly Scatter3d
    marker.opacity is scalar-only).  The numeric opacity value (1.0 or 0.3) is
    stored in trace.customdata for straightforward test verification.

    For each trace, count of opacity==1.0 must match the single-cell site count
    for that orbit.  Count of opacity==0.3 entries must be 7x that.
    """
    # Build a map: orbit_name -> site count from the library
    orbit_site_counts: dict[str, int] = {}
    orbit_shell_names: dict[str, str] = {}
    for orb in orbit_lib_data["orbits"]:
        orbit_name = orb["orbit"]
        orbit_site_counts[orbit_name] = len(orb["sites"])
        orbit_shell_names[orbit_name] = SHELL_NAMES.get(orbit_name, orbit_name)

    # Build a map: shell_name -> site count for lookup by trace.name
    shell_site_counts: dict[str, int] = {
        shell_name: orbit_site_counts[orbit_name]
        for orbit_name, shell_name in orbit_shell_names.items()
    }

    for trace in fig_expansion.data:
        trace_name = trace.name
        assert trace_name in shell_site_counts, (
            f"Trace name '{trace_name}' not found in expected shell names"
        )
        expected_central_count = shell_site_counts[trace_name]
        expected_surrounding_count = expected_central_count * 7

        # Opacity values are stored in customdata (marker.opacity is scalar-only
        # in plotly Scatter3d; per-point opacity is encoded via RGBA colors).
        assert trace.customdata is not None, (
            f"Trace '{trace_name}' has no customdata — opacity values not stored"
        )
        opacities = list(trace.customdata)
        central_count = sum(1 for op in opacities if op == 1.0)
        surrounding_count = sum(1 for op in opacities if op == 0.3)

        assert central_count == expected_central_count, (
            f"Trace '{trace_name}': expected {expected_central_count} central-cell "
            f"(opacity=1.0) sites, got {central_count}"
        )
        assert surrounding_count == expected_surrounding_count, (
            f"Trace '{trace_name}': expected {expected_surrounding_count} surrounding "
            f"(opacity=0.3) sites, got {surrounding_count}"
        )


def test_expansion_figure_trace_names(fig_expansion: go.Figure) -> None:
    """Each trace.name is a value from SHELL_NAMES."""
    shell_name_values = set(SHELL_NAMES.values())
    for trace in fig_expansion.data:
        assert trace.name in shell_name_values, (
            f"Trace name '{trace.name}' not in SHELL_NAMES.values(): {shell_name_values!r}"
        )


def test_expansion_figure_title(fig_expansion: go.Figure) -> None:
    """Figure layout title contains 'Periodic Approximant'."""
    title_text = fig_expansion.layout.title.text
    assert title_text is not None, "Figure has no title"
    assert "Periodic Approximant" in title_text, (
        f"Expected 'Periodic Approximant' in title, got: {title_text!r}"
    )


def test_expansion_figure_hover_text(fig_expansion: go.Figure) -> None:
    """At least one trace text entry contains 'central'; at least one contains 'cell ('."""
    all_texts: list[str] = []
    for trace in fig_expansion.data:
        if trace.text:
            all_texts.extend(trace.text)

    assert any("central" in t for t in all_texts), (
        "No hover text found containing 'central'"
    )
    assert any("cell (" in t for t in all_texts), (
        "No hover text found containing 'cell ('"
    )


def test_import_guard(
    monkeypatch: pytest.MonkeyPatch, orbit_lib_data: dict
) -> None:
    """When _EXPANSION_AVAILABLE is False, expansion_figure raises ImportError matching 'materials-discovery[viz]'."""
    monkeypatch.setattr(expansion_mod, "_EXPANSION_AVAILABLE", False)
    monkeypatch.setattr(
        expansion_mod, "_EXPANSION_IMPORT_ERROR", "No module named 'plotly'"
    )

    with pytest.raises(ImportError, match=r"materials-discovery\[viz\]"):
        expansion_figure(orbit_lib_data)
