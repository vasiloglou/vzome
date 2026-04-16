"""Tests for materials_discovery.visualization.matplotlib_pub — 2D publication figures.

Covers VIZ-03 (screening_scatter), VIZ-04 (rdf_plot), VIZ-05 (diffraction_plot),
PUB_STYLE dict keys, and the import guard.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib
import matplotlib.figure
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg")  # non-interactive backend for tests

import materials_discovery.visualization.matplotlib_pub as matplotlib_pub_mod
from materials_discovery.visualization.matplotlib_pub import (
    PUB_STYLE,
    _PUB_AVAILABLE,
    diffraction_plot,
    rdf_plot,
    screening_scatter,
)

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
SCREENED_PATH = DATA_ROOT / "screened" / "sc_zn_screened.jsonl"
CALIBRATION_PATH = DATA_ROOT / "calibration" / "sc_zn_screen_calibration.json"
ORBIT_LIB_PATH = DATA_ROOT / "prototypes" / "generated" / "sc_zn_tsai_bridge.json"
CANDIDATES_PATH = DATA_ROOT / "candidates" / "sc_zn_candidates.jsonl"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def screened_path() -> Path:
    return SCREENED_PATH


@pytest.fixture(scope="module")
def calibration_path() -> Path:
    return CALIBRATION_PATH


@pytest.fixture(scope="module")
def orbit_lib_path() -> Path:
    return ORBIT_LIB_PATH


@pytest.fixture(scope="module")
def candidate_peaks() -> list[dict]:
    """Load first candidate and return its simulated XRD peaks (12 peaks)."""
    from materials_discovery.common.schema import CandidateRecord
    from materials_discovery.diffraction.simulate_powder_xrd import (
        simulate_powder_xrd_patterns,
    )

    with open(CANDIDATES_PATH, encoding="utf-8") as fh:
        first_line = fh.readline()
    candidate = CandidateRecord.model_validate(json.loads(first_line))
    result = simulate_powder_xrd_patterns([candidate])
    return result[0]["peaks"]


@pytest.fixture(scope="module")
def fig_scatter(screened_path: Path, calibration_path: Path) -> matplotlib.figure.Figure:
    return screening_scatter(screened_path, calibration_path)


@pytest.fixture(scope="module")
def fig_rdf(orbit_lib_path: Path) -> matplotlib.figure.Figure:
    return rdf_plot(orbit_lib_path)


@pytest.fixture(scope="module")
def fig_xrd(candidate_peaks: list[dict]) -> matplotlib.figure.Figure:
    return diffraction_plot(candidate_peaks)


# ---------------------------------------------------------------------------
# Test 1: PUB_STYLE keys
# ---------------------------------------------------------------------------


def test_pub_style_keys() -> None:
    """PUB_STYLE dict contains all required publication-quality keys."""
    required_keys = {
        "font.family",
        "figure.dpi",
        "savefig.dpi",
        "pdf.fonttype",
        "axes.spines.top",
        "axes.spines.right",
    }
    missing = required_keys - set(PUB_STYLE.keys())
    assert not missing, f"PUB_STYLE is missing keys: {missing!r}"


# ---------------------------------------------------------------------------
# Test 2: screening_scatter returns Figure
# ---------------------------------------------------------------------------


def test_screening_scatter_returns_figure(
    fig_scatter: matplotlib.figure.Figure,
) -> None:
    """screening_scatter() returns a matplotlib Figure instance."""
    assert isinstance(fig_scatter, matplotlib.figure.Figure), (
        f"Expected matplotlib.figure.Figure, got {type(fig_scatter)}"
    )


# ---------------------------------------------------------------------------
# Test 3: screening_scatter has threshold lines
# ---------------------------------------------------------------------------


def test_screening_scatter_has_threshold_lines(
    fig_scatter: matplotlib.figure.Figure,
) -> None:
    """screening_scatter axes has at least 2 Line2D objects from axhline/axvline."""
    ax = fig_scatter.axes[0]
    # axhline/axvline produce Line2D with dashed ('--') or dotted (':') linestyles.
    # matplotlib normalises linestyles in various ways; check using get_linestyle()
    # against both short-form strings and long-form tuple representations.
    threshold_lines = []
    for line in ax.get_lines():
        ls = line.get_linestyle()
        # matplotlib may return "--", ":", "dashed", "dotted", or a tuple
        if ls in ("--", ":", "dashed", "dotted") or (
            isinstance(ls, tuple) and len(ls) == 2 and ls[1] is not None
        ):
            threshold_lines.append(line)

    assert len(threshold_lines) >= 2, (
        f"Expected at least 2 threshold lines, found {len(threshold_lines)}. "
        f"All linestyles: {[l.get_linestyle() for l in ax.get_lines()]!r}"
    )


# ---------------------------------------------------------------------------
# Test 4: screening_scatter title contains count numbers
# ---------------------------------------------------------------------------


def test_screening_scatter_title_has_counts(
    fig_scatter: matplotlib.figure.Figure,
) -> None:
    """screening_scatter title contains shortlisted (4), passed (20), total (30) counts."""
    ax = fig_scatter.axes[0]
    title = ax.get_title()
    assert "4" in title, f"Expected '4' (shortlisted count) in title: {title!r}"
    assert "20" in title, f"Expected '20' (passed count) in title: {title!r}"
    assert "30" in title, f"Expected '30' (total count) in title: {title!r}"


# ---------------------------------------------------------------------------
# Test 5: rdf_plot returns Figure
# ---------------------------------------------------------------------------


def test_rdf_plot_returns_figure(fig_rdf: matplotlib.figure.Figure) -> None:
    """rdf_plot() returns a matplotlib Figure instance."""
    assert isinstance(fig_rdf, matplotlib.figure.Figure), (
        f"Expected matplotlib.figure.Figure, got {type(fig_rdf)}"
    )


# ---------------------------------------------------------------------------
# Test 6: rdf_plot has shell annotation lines
# ---------------------------------------------------------------------------


def test_rdf_plot_has_shell_annotations(fig_rdf: matplotlib.figure.Figure) -> None:
    """rdf_plot axes has exactly 5 vertical annotation lines (one per orbit shell)."""
    ax = fig_rdf.axes[0]
    # axvline creates Line2D objects with x-data of length 2 (ymin, ymax) in axes
    # coordinates.  We count lines whose xdata is constant (both x-values equal),
    # which is the matplotlib representation of axvline.
    vlines = []
    for line in ax.get_lines():
        xdata = line.get_xdata()
        if len(xdata) == 2 and xdata[0] == xdata[1]:
            vlines.append(line)

    assert len(vlines) == 5, (
        f"Expected exactly 5 shell annotation vlines, found {len(vlines)}"
    )


# ---------------------------------------------------------------------------
# Test 7: rdf_plot no zero-distance spike (orbit library, not raw.json)
# ---------------------------------------------------------------------------


def test_rdf_plot_no_zero_distance_spike(fig_rdf: matplotlib.figure.Figure) -> None:
    """rdf_plot histogram first bins (0-1.0 A) have zero counts — confirms orbit library used.

    If raw.json (with duplicated fractional positions) were used, there would be
    zero-distance pairs creating a spike in the first bin.
    """
    ax = fig_rdf.axes[0]
    # Bar containers give us access to the bar heights
    containers = ax.containers
    assert containers, "Expected bar containers in rdf_plot axes"

    bar_container = containers[0]
    # Collect heights of bars whose left edge is in [0.0, 1.0)
    zero_range_counts = []
    for bar in bar_container:
        x_left = bar.get_x()
        height = bar.get_height()
        if 0.0 <= x_left < 1.0:
            zero_range_counts.append(height)

    # None of the sub-1 Angstrom bins should have non-zero counts
    nonzero = [h for h in zero_range_counts if h > 0]
    assert not nonzero, (
        f"Found non-zero counts in 0-1 Angstrom bins: {nonzero!r}. "
        "This suggests raw.json (with duplicate/zero-distance pairs) was used instead of "
        "the orbit library."
    )


# ---------------------------------------------------------------------------
# Test 8: diffraction_plot returns Figure
# ---------------------------------------------------------------------------


def test_diffraction_plot_returns_figure(fig_xrd: matplotlib.figure.Figure) -> None:
    """diffraction_plot() returns a matplotlib Figure instance."""
    assert isinstance(fig_xrd, matplotlib.figure.Figure), (
        f"Expected matplotlib.figure.Figure, got {type(fig_xrd)}"
    )


# ---------------------------------------------------------------------------
# Test 9: diffraction_plot has 12 peak lines
# ---------------------------------------------------------------------------


def test_diffraction_plot_has_12_peaks(fig_xrd: matplotlib.figure.Figure) -> None:
    """diffraction_plot figure has Line2D or LineCollection artists representing 12 peaks.

    ax.vlines() produces a LineCollection; each segment is one peak line.
    """
    from matplotlib.collections import LineCollection

    ax = fig_xrd.axes[0]

    # Count segments in LineCollection objects (produced by ax.vlines)
    total_peak_lines = 0
    for coll in ax.collections:
        if isinstance(coll, LineCollection):
            total_peak_lines += len(coll.get_segments())

    # Also count any standalone Line2D objects that look like peaks (non-threshold)
    for line in ax.get_lines():
        xdata = line.get_xdata()
        if len(xdata) == 2 and xdata[0] == xdata[1]:
            total_peak_lines += 1

    assert total_peak_lines == 12, (
        f"Expected 12 peak lines in diffraction_plot, found {total_peak_lines}"
    )


# ---------------------------------------------------------------------------
# Test 10: import guard — _PUB_AVAILABLE=False raises ImportError
# ---------------------------------------------------------------------------


def test_import_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    """When _PUB_AVAILABLE is monkeypatched to False, screening_scatter raises ImportError
    with install hint matching 'materials-discovery[viz]'.
    """
    monkeypatch.setattr(matplotlib_pub_mod, "_PUB_AVAILABLE", False)
    monkeypatch.setattr(
        matplotlib_pub_mod, "_PUB_IMPORT_ERROR", "No module named 'matplotlib'"
    )

    with pytest.raises(ImportError, match=r"materials-discovery\[viz\]"):
        screening_scatter(SCREENED_PATH, CALIBRATION_PATH)
