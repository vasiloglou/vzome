"""Shared orbit label mappings and colorblind-safe palette.

This module is a **leaf** — it imports nothing from the rest of
``materials_discovery``.  Phase 45's ``plotly_3d.py`` and Phase 46's
``matplotlib_pub.py`` import from here.

Palette: Wong (2011) https://www.nature.com/articles/nmeth.1618
Design source: designs/zomic/sc_zn_tsai_bridge.yaml preferred_species_by_orbit
Orbit source: data/prototypes/generated/sc_zn_tsai_bridge.json selected_orbits
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Design-time orbit labels (from .zomic label prefixes)
# ---------------------------------------------------------------------------
ORBIT_LABELS: dict[str, str] = {
    "pent": "Pentagonal ring",
    "frustum": "Frustum connectors",
    "joint": "Joint sites",
}

# ---------------------------------------------------------------------------
# Anchor-library shell names (from sc_zn_tsai_bridge.json selected_orbits)
# ---------------------------------------------------------------------------
SHELL_NAMES: dict[str, str] = {
    "tsai_zn7": "Zn inner shell",
    "tsai_sc1": "Sc icosahedron shell",
    "tsai_zn6": "Zn middle shell",
    "tsai_zn5": "Zn pentagonal shell",
    "tsai_zn4": "Zn outer shell",
}

# ---------------------------------------------------------------------------
# Colorblind-safe palette — Wong (2011), skip black for contrast
# ---------------------------------------------------------------------------
ORBIT_COLORS: dict[str, str] = {
    "tsai_zn7": "#56B4E9",  # sky blue
    "tsai_sc1": "#E69F00",  # orange
    "tsai_zn6": "#009E73",  # bluish green
    "tsai_zn5": "#D55E00",  # vermilion
    "tsai_zn4": "#0072B2",  # blue
}

DEFAULT_ORBIT_COLOR: str = "#6b7280"

# ---------------------------------------------------------------------------
# Preferred species by design-time orbit (mirrors sc_zn_tsai_bridge.yaml)
# ---------------------------------------------------------------------------
PREFERRED_SPECIES: dict[str, list[str]] = {
    "pent": ["Sc", "Zn"],
    "frustum": ["Zn", "Sc"],
    "joint": ["Zn"],
}
