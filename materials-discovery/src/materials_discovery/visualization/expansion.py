"""Crystal expansion view figures — 2x2x2 supercell tiling of the Sc-Zn motif.

ENRICH-02: expansion_figure() returns a plotly Figure showing how the Sc-Zn
quasicrystal approximant motif tiles into a larger periodic structure.

Central cell sites (offset 0,0,0) have marker opacity 1.0; surrounding 7 cells
have opacity 0.3.  Each orbit is rendered as a single trace (5 total traces)
using orbit-colored markers from ORBIT_COLORS.
"""

from __future__ import annotations

import itertools

# ---------------------------------------------------------------------------
# Optional viz dependency guard — must be at module top so _EXPANSION_AVAILABLE
# is set once at import time (not lazily inside function bodies).
# ---------------------------------------------------------------------------
try:
    import plotly.graph_objects as go

    _EXPANSION_AVAILABLE = True
    _EXPANSION_IMPORT_ERROR: str | None = None
except ImportError as exc:
    _EXPANSION_AVAILABLE = False
    _EXPANSION_IMPORT_ERROR = str(exc)

# Labels module is a leaf with no intra-package imports — always safe to import.
from materials_discovery.visualization.labels import (
    DEFAULT_ORBIT_COLOR,
    ORBIT_COLORS,
    SHELL_NAMES,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _require_expansion() -> None:
    """Raise ImportError with install instructions when plotly is absent."""
    if not _EXPANSION_AVAILABLE:
        raise ImportError(
            "Crystal expansion visualization requires the [viz] extra. "
            "Install with: uv pip install 'materials-discovery[viz]'. "
            f"Missing: {_EXPANSION_IMPORT_ERROR}"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def expansion_figure(
    orbit_lib_data: dict, n_cells: int = 2
) -> "go.Figure":  # type: ignore[name-defined]
    """Return a plotly Figure showing the Sc-Zn motif tiled into a n_cells^3 supercell.

    Creates ONE trace per orbit (5 traces total for the Sc-Zn Tsai bridge),
    not one trace per orbit per cell.  Central cell sites (offset (0,0,0)) have
    marker opacity 1.0; sites in the surrounding 7 cells have opacity 0.3.

    Parameters
    ----------
    orbit_lib_data:
        Dict loaded by :func:`~materials_discovery.visualization.plotly_3d.load_orbit_library`.
    n_cells:
        Number of unit cells along each axis (default 2 → 2x2x2 = 8 cells).

    Returns
    -------
    go.Figure
        Interactive plotly figure with exactly ``len(orbits)`` Scatter3d traces.
        For the default Sc-Zn Tsai bridge this is 5 traces x 8 cells = 800 marker
        points total.
    """
    _require_expansion()

    a: float = orbit_lib_data["base_cell"]["a"]
    mc_frac: list[float] = orbit_lib_data["motif_center"]
    mc_cart = [f * a for f in mc_frac]

    # Generate all cell offsets: (0,0,0) first, then the remaining 7 for n_cells=2.
    offsets = list(itertools.product(range(n_cells), repeat=3))

    fig = go.Figure()

    for orb in orbit_lib_data["orbits"]:
        orbit_name: str = orb["orbit"]
        shell_name: str = SHELL_NAMES.get(orbit_name, orbit_name)
        color: str = ORBIT_COLORS.get(orbit_name, DEFAULT_ORBIT_COLOR)

        xs: list[float] = []
        ys: list[float] = []
        zs: list[float] = []
        opacities: list[float] = []
        texts: list[str] = []

        for n1, n2, n3 in offsets:
            is_central = (n1, n2, n3) == (0, 0, 0)
            opacity_val = 1.0 if is_central else 0.3
            cell_label = "central" if is_central else f"cell ({n1},{n2},{n3})"

            for site in orb["sites"]:
                fp = site["fractional_position"]
                x = (fp[0] + n1) * a - mc_cart[0]
                y = (fp[1] + n2) * a - mc_cart[1]
                z = (fp[2] + n3) * a - mc_cart[2]
                xs.append(x)
                ys.append(y)
                zs.append(z)
                opacities.append(opacity_val)
                texts.append(
                    f"{site['label']} -- {shell_name} -- {cell_label}"
                )

        fig.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="markers",
                marker=dict(size=5, color=color, opacity=opacities),
                name=shell_name,
                text=texts,
                hovertemplate="%{text}<extra></extra>",
            )
        )

    fig.update_layout(
        title=f"Sc-Zn Periodic Approximant -- {n_cells}x{n_cells}x{n_cells} Expansion",
        scene=dict(
            xaxis_title="x (A)",
            yaxis_title="y (A)",
            zaxis_title="z (A)",
            aspectmode="data",
        ),
    )

    return fig
