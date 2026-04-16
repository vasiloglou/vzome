"""Interactive 3D plotly figures for orbit-colored Tsai cluster visualization."""

from __future__ import annotations

import json
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional viz dependency guard — must be at module top so _VIZ_AVAILABLE
# is set once at import time (not lazily inside function bodies).
# ---------------------------------------------------------------------------
try:
    import plotly.graph_objects as go
    import numpy as np
    from scipy.spatial import ConvexHull

    _VIZ_AVAILABLE = True
    _VIZ_IMPORT_ERROR: str | None = None
except ImportError as exc:
    _VIZ_AVAILABLE = False
    _VIZ_IMPORT_ERROR = str(exc)

# Labels module is a leaf with no intra-package imports — always safe to import.
from materials_discovery.visualization.labels import (
    DEFAULT_ORBIT_COLOR,
    ORBIT_COLORS,
    SHELL_NAMES,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _require_viz() -> None:
    """Raise ImportError with install instructions when plotly/scipy are absent."""
    if not _VIZ_AVAILABLE:
        raise ImportError(
            "Interactive 3D visualization requires the [viz] extra. "
            "Install with: uv pip install 'materials-discovery[viz]'. "
            f"Missing: {_VIZ_IMPORT_ERROR}"
        )


def _frac_to_centered_cart(
    frac: list[float], a: float, mc_cart: list[float]
) -> list[float]:
    """Convert a fractional position to centered Cartesian coordinates (Angstrom).

    Assumes a cubic, axis-aligned cell (a = b = c, all angles 90 deg).
    """
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


def _hull_edge_lines(
    pts: "np.ndarray",  # type: ignore[name-defined]
    hull: "ConvexHull",  # type: ignore[name-defined]
) -> "tuple[list, list, list]":
    """Return flat x/y/z arrays for a Scatter3d wireframe with None separators."""
    edges: set[tuple[int, int]] = set()
    for simplex in hull.simplices:
        for e in range(3):
            edge = tuple(sorted([int(simplex[e]), int(simplex[(e + 1) % 3])]))
            edges.add(edge)  # type: ignore[arg-type]
    ex: list = []
    ey: list = []
    ez: list = []
    for v1, v2 in edges:
        ex += [pts[v1, 0], pts[v2, 0], None]
        ey += [pts[v1, 1], pts[v2, 1], None]
        ez += [pts[v1, 2], pts[v2, 2], None]
    return ex, ey, ez


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_orbit_library(path: Path) -> dict:
    """Load the orbit library JSON produced by ``mdisc export-zomic``.

    Parameters
    ----------
    path:
        Path to the orbit library JSON (e.g. ``sc_zn_tsai_bridge.json``).

    Returns
    -------
    dict
        Parsed orbit library dict with keys ``base_cell``, ``motif_center``,
        ``orbits``, and ``anchor_orbit_summary``.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the resolved path.
    """
    resolved = path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"orbit library not found: {resolved}")
    return json.loads(resolved.read_text(encoding="utf-8"))


def orbit_figure(orbit_lib_data: dict) -> "go.Figure":  # type: ignore[name-defined]
    """Return a plotly Figure with one Scatter3d trace per anchor orbit (VIZ-01).

    Each trace uses the colorblind-safe palette from ``labels.ORBIT_COLORS``.
    Hover text shows: ``"{label} ({orbit}) - {species} - {shell_name}"``.
    Marker size is uniform at 8 for all sites.

    Parameters
    ----------
    orbit_lib_data:
        Dict loaded by :func:`load_orbit_library`.

    Returns
    -------
    go.Figure
        Interactive plotly figure with exactly 5 Scatter3d traces for the
        Sc-Zn Tsai anchor orbits.
    """
    _require_viz()

    a: float = orbit_lib_data["base_cell"]["a"]
    mc_frac: list[float] = orbit_lib_data["motif_center"]
    mc_cart = [f * a for f in mc_frac]

    fig = go.Figure()

    for orb in orbit_lib_data["orbits"]:
        orbit_name: str = orb["orbit"]
        species: str = orb["preferred_species"][0] if orb["preferred_species"] else "?"
        shell_name: str = SHELL_NAMES.get(orbit_name, orbit_name)
        color: str = ORBIT_COLORS.get(orbit_name, DEFAULT_ORBIT_COLOR)

        xs: list[float] = []
        ys: list[float] = []
        zs: list[float] = []
        texts: list[str] = []

        for site in orb["sites"]:
            fp = site["fractional_position"]
            x, y, z = _frac_to_centered_cart(fp, a, mc_cart)
            xs.append(x)
            ys.append(y)
            zs.append(z)
            texts.append(
                f"{site['label']} ({orbit_name}) - {species} - {shell_name}"
            )

        fig.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="markers",
                marker=dict(size=8, color=color),
                name=shell_name,
                text=texts,
                hovertemplate="%{text}<extra></extra>",
            )
        )

    fig.update_layout(
        title="Sc-Zn Tsai Cluster — Orbit-Colored Sites",
        scene=dict(
            xaxis_title="x (A)",
            yaxis_title="y (A)",
            zaxis_title="z (A)",
            aspectmode="data",
        ),
    )

    return fig


def shell_figure(orbit_lib_data: dict) -> "go.Figure":  # type: ignore[name-defined]
    """Return a plotly Figure with shells sorted by mean radial distance (VIZ-02).

    Each shell is rendered as:
    - A ``go.Scatter3d`` markers trace
    - A ``go.Mesh3d`` convex-hull cage (opacity=0.15) if >= 4 sites
    - A ``go.Scatter3d`` edge wireframe in ``mode="lines"``

    All three traces share a ``legendgroup`` so toggling in the legend shows/hides
    the full shell.

    Parameters
    ----------
    orbit_lib_data:
        Dict loaded by :func:`load_orbit_library`.

    Returns
    -------
    go.Figure
        Interactive plotly figure with shells in ascending radial-distance order.
    """
    _require_viz()

    a: float = orbit_lib_data["base_cell"]["a"]
    mc_frac: list[float] = orbit_lib_data["motif_center"]
    mc_cart = [f * a for f in mc_frac]

    # Sort orbits by mean radial distance; orbit name as tiebreaker for stability.
    orbits_sorted = sorted(
        orbit_lib_data["orbits"],
        key=lambda orb: (
            _compute_mean_radius(orb["sites"], a, mc_cart),
            orb["orbit"],
        ),
    )

    fig = go.Figure()

    for shell_idx, orb in enumerate(orbits_sorted, start=1):
        orbit_name: str = orb["orbit"]
        species: str = orb["preferred_species"][0] if orb["preferred_species"] else "?"
        shell_name: str = SHELL_NAMES.get(orbit_name, orbit_name)
        color: str = ORBIT_COLORS.get(orbit_name, DEFAULT_ORBIT_COLOR)
        group = f"shell_{shell_idx}"

        pts_list: list[list[float]] = []
        texts: list[str] = []

        for site in orb["sites"]:
            fp = site["fractional_position"]
            x, y, z = _frac_to_centered_cart(fp, a, mc_cart)
            pts_list.append([x, y, z])
            texts.append(
                f"{site['label']} ({orbit_name}) - {species} - {shell_name}"
            )

        pts = np.array(pts_list)
        xs, ys, zs = pts[:, 0], pts[:, 1], pts[:, 2]

        # Marker trace
        fig.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="markers",
                marker=dict(size=8, color=color),
                name=f"Shell {shell_idx}: {shell_name}",
                text=texts,
                hovertemplate="%{text}<extra></extra>",
                legendgroup=group,
            )
        )

        # ConvexHull cage + wireframe (only when enough non-coplanar sites exist)
        if len(pts_list) >= 4:
            try:
                hull = ConvexHull(pts)

                # Mesh3d faces
                fig.add_trace(
                    go.Mesh3d(
                        x=xs,
                        y=ys,
                        z=zs,
                        i=hull.simplices[:, 0],
                        j=hull.simplices[:, 1],
                        k=hull.simplices[:, 2],
                        opacity=0.15,
                        color=color,
                        name=f"Shell {shell_idx} cage",
                        showlegend=False,
                        legendgroup=group,
                    )
                )

                # Edge wireframe
                ex, ey, ez = _hull_edge_lines(pts, hull)
                fig.add_trace(
                    go.Scatter3d(
                        x=ex,
                        y=ey,
                        z=ez,
                        mode="lines",
                        line=dict(color=color, width=2),
                        name=f"Shell {shell_idx} edges",
                        showlegend=False,
                        legendgroup=group,
                    )
                )

            except Exception:
                # Degenerate hull (coplanar points) — skip cage, keep markers.
                pass

    fig.update_layout(
        title="Sc-Zn Tsai Cluster — Shell Decomposition",
        scene=dict(
            xaxis_title="x (A)",
            yaxis_title="y (A)",
            zaxis_title="z (A)",
            aspectmode="data",
        ),
    )

    return fig
