"""Publication-quality 2D matplotlib figures for the Sc-Zn Tsai cluster pipeline.

Provides three figure functions for the VIZ-03, VIZ-04, and VIZ-05 requirements:
  - screening_scatter: shortlisted candidate scatter with threshold boundary lines
  - rdf_plot: pairwise-distance histogram with shell-peak annotations
  - diffraction_plot: simulated powder XRD stem plot

Module is importable without the [viz] extra installed.  Calling any figure
function raises ImportError with install instructions when matplotlib or numpy
is unavailable.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional viz dependency guard — set once at module import time.
# ---------------------------------------------------------------------------
try:
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np

    _PUB_AVAILABLE = True
    _PUB_IMPORT_ERROR: str | None = None
except ImportError as exc:
    _PUB_AVAILABLE = False
    _PUB_IMPORT_ERROR = str(exc)

# Labels module is a leaf with no intra-package imports — always safe to import.
from materials_discovery.visualization.labels import (
    DEFAULT_ORBIT_COLOR,
    ORBIT_COLORS,
    SHELL_NAMES,
)

# ---------------------------------------------------------------------------
# Publication style defaults
# ---------------------------------------------------------------------------

PUB_STYLE: dict = {
    "font.family": "sans-serif",
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "axes.spines.top": False,
    "axes.spines.right": False,
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _require_pub() -> None:
    """Raise ImportError with install instructions when matplotlib/numpy are absent."""
    if not _PUB_AVAILABLE:
        raise ImportError(
            "Publication-quality 2D figures require the [viz] extra. "
            "Install with: uv pip install 'materials-discovery[viz]'. "
            f"Missing: {_PUB_IMPORT_ERROR}"
        )


def _frac_to_centered_cart(
    frac: list[float], a: float, mc_cart: list[float]
) -> list[float]:
    """Convert a fractional position to centered Cartesian coordinates (Angstrom)."""
    return [frac[i] * a - mc_cart[i] for i in range(3)]


def _compute_mean_radius(
    sites: list[dict], a: float, mc_cart: list[float]
) -> float:
    """Return mean radial distance of orbit sites from the motif centre."""
    dists = []
    for s in sites:
        fp = s["fractional_position"]
        dx = fp[0] * a - mc_cart[0]
        dy = fp[1] * a - mc_cart[1]
        dz = fp[2] * a - mc_cart[2]
        dists.append(math.sqrt(dx**2 + dy**2 + dz**2))
    return sum(dists) / len(dists) if dists else 0.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def screening_scatter(
    screened_path: Path,
    calibration_path: Path,
) -> "matplotlib.figure.Figure":  # type: ignore[name-defined]
    """Return a publication-quality screening scatter figure (VIZ-03).

    Plots all shortlisted candidates from the screened JSONL against two
    threshold boundary lines loaded from the calibration JSON.

    Parameters
    ----------
    screened_path:
        Path to the screened candidates JSONL file (e.g. sc_zn_screened.jsonl).
        Only records with a non-None ``shortlist_rank`` are plotted.
    calibration_path:
        Path to the screen calibration JSON file (e.g. sc_zn_screen_calibration.json).
        Provides ``max_energy_threshold``, ``min_distance_threshold``,
        ``shortlisted_count``, ``passed_count``, and ``input_count``.

    Returns
    -------
    matplotlib.figure.Figure
        Figure instance (caller must call ``fig.savefig()`` or ``plt.show()``).
    """
    _require_pub()

    # Load calibration thresholds
    cal = json.loads(Path(calibration_path).resolve().read_text(encoding="utf-8"))

    # Load screened records — collect shortlisted ones
    energies: list[float] = []
    distances: list[float] = []
    with open(Path(screened_path).resolve(), encoding="utf-8") as fh:
        for line in fh:
            record = json.loads(line)
            screen = record.get("screen") or {}
            if screen.get("shortlist_rank") is not None:
                energies.append(float(screen["energy_proxy_ev_per_atom"]))
                distances.append(float(screen["min_distance_proxy"]))

    with plt.rc_context(PUB_STYLE):
        fig, ax = plt.subplots(figsize=(6, 4))

        # Scatter shortlisted candidates
        ax.scatter(
            distances,
            energies,
            color=ORBIT_COLORS.get("tsai_zn4", "#0072B2"),
            s=60,
            zorder=3,
            label="Shortlisted candidates",
        )

        # Threshold boundary lines
        ax.axvline(
            cal["min_distance_threshold"],
            color="#888",
            linestyle="--",
            label="Min distance threshold",
        )
        ax.axhline(
            cal["max_energy_threshold"],
            color="#555",
            linestyle=":",
            label="Max energy threshold",
        )

        ax.set_xlabel("min_distance_proxy")
        ax.set_ylabel("energy_proxy_ev_per_atom (eV/atom)")
        ax.set_title(
            f"Screening: {cal['shortlisted_count']} shortlisted"
            f" / {cal['passed_count']} passed"
            f" / {cal['input_count']} total"
        )
        ax.legend()

    return fig


def rdf_plot(orbit_lib_path: Path) -> "matplotlib.figure.Figure":  # type: ignore[name-defined]
    """Return a publication-quality radial distribution function figure (VIZ-04).

    Computes all pairwise distances from the 100-site orbit library (NOT the
    raw.json with duplicate points) and plots a histogram together with 5
    vertical shell-peak annotation lines.

    Parameters
    ----------
    orbit_lib_path:
        Path to the orbit library JSON (e.g. sc_zn_tsai_bridge.json).
        Must contain ``base_cell``, ``motif_center``, and ``orbits`` keys.

    Returns
    -------
    matplotlib.figure.Figure
        Figure instance with a bar-chart histogram and 5 axvline annotations.
    """
    _require_pub()

    lib = json.loads(Path(orbit_lib_path).resolve().read_text(encoding="utf-8"))
    a: float = lib["base_cell"]["a"]
    mc_frac: list[float] = lib["motif_center"]
    mc_cart = [f * a for f in mc_frac]

    # Collect all site Cartesian positions (100 unique sites from orbit library)
    coords_list: list[list[float]] = []
    for orb in lib["orbits"]:
        for site in orb["sites"]:
            coords_list.append(
                _frac_to_centered_cart(site["fractional_position"], a, mc_cart)
            )

    coords = np.array(coords_list)  # shape (N, 3)
    N = len(coords)

    # Vectorised pairwise distances — upper triangle only (k=1 excludes diagonal)
    diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]  # (N, N, 3)
    dists_full = np.sqrt((diff**2).sum(axis=-1))  # (N, N)
    upper = dists_full[np.triu_indices(N, k=1)]  # 4950 values for N=100

    # Histogram with 0.1 Angstrom bins
    bin_width = 0.1
    bins = np.arange(0.0, upper.max() + bin_width, bin_width)
    counts, bin_edges = np.histogram(upper, bins=bins)

    with plt.rc_context(PUB_STYLE):
        fig, ax = plt.subplots(figsize=(7, 4))

        # Bar-chart of pair counts vs distance
        ax.bar(
            bin_edges[:-1],
            counts,
            width=bin_width,
            align="edge",
            color="#0072B2",
            alpha=0.7,
            label="Pair count",
        )

        # Per-orbit shell-peak annotations (5 lines, one per orbit)
        for orb in lib["orbits"]:
            orbit_name: str = orb["orbit"]
            mean_r = _compute_mean_radius(orb["sites"], a, mc_cart)
            shell_label = SHELL_NAMES.get(orbit_name, orbit_name)
            color = ORBIT_COLORS.get(orbit_name, DEFAULT_ORBIT_COLOR)
            ax.axvline(mean_r, color=color, linestyle="--", linewidth=1.2, label=shell_label)

        ax.set_xlabel("Distance (Angstrom)")
        ax.set_ylabel("Pair count")
        ax.set_title("Pairwise Distance Distribution")
        ax.legend(fontsize=7)

    return fig


def diffraction_plot(
    peaks: list[dict],
) -> "matplotlib.figure.Figure":  # type: ignore[name-defined]
    """Return a publication-quality simulated powder XRD figure (VIZ-05).

    Renders each peak as a vertical line (stem plot) using ``ax.vlines``.

    Parameters
    ----------
    peaks:
        Pre-computed peaks list.  Each dict must have keys ``"two_theta"``
        (float, degrees) and ``"intensity"`` (float, relative 0-100).
        Typically produced by
        ``simulate_powder_xrd_patterns([candidate])[0]["peaks"]``.

    Returns
    -------
    matplotlib.figure.Figure
        Figure instance with one vlines call covering all peaks.
    """
    _require_pub()

    two_thetas = [float(p["two_theta"]) for p in peaks]
    intensities = [float(p["intensity"]) for p in peaks]

    with plt.rc_context(PUB_STYLE):
        fig, ax = plt.subplots(figsize=(7, 4))

        ax.vlines(two_thetas, 0, intensities, colors="#2563eb", linewidth=1.5)

        ax.set_xlabel("2theta (degrees)")
        ax.set_ylabel("Relative intensity")
        ax.set_title("Simulated Powder XRD Pattern")
        ax.set_ylim(bottom=0)

    return fig
