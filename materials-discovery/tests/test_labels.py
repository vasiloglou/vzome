from __future__ import annotations

import re
from pathlib import Path

import pytest

from materials_discovery.visualization import (
    DEFAULT_ORBIT_COLOR,
    ORBIT_COLORS,
    ORBIT_LABELS,
    PREFERRED_SPECIES,
    SHELL_NAMES,
)

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def test_orbit_labels_keys():
    assert set(ORBIT_LABELS.keys()) == {"pent", "frustum", "joint"}
    assert all(isinstance(v, str) and len(v) > 0 for v in ORBIT_LABELS.values())


def test_shell_names_keys():
    expected = {"tsai_zn7", "tsai_sc1", "tsai_zn6", "tsai_zn5", "tsai_zn4"}
    assert set(SHELL_NAMES.keys()) == expected
    assert all(isinstance(v, str) and len(v) > 0 for v in SHELL_NAMES.values())


def test_orbit_colors_keys_match_shell_names():
    assert set(ORBIT_COLORS.keys()) == set(SHELL_NAMES.keys())


def test_orbit_colors_are_valid_hex():
    for name, color in ORBIT_COLORS.items():
        assert _HEX_RE.match(color), f"{name}: {color} is not valid hex"


def test_orbit_colors_no_black():
    for name, color in ORBIT_COLORS.items():
        assert color.upper() != "#000000", f"{name} is black — skip black per Wong 2011"


def test_preferred_species_keys_match_orbit_labels():
    assert set(PREFERRED_SPECIES.keys()) == set(ORBIT_LABELS.keys())


def test_preferred_species_values_are_nonempty_lists():
    for name, species in PREFERRED_SPECIES.items():
        assert isinstance(species, list) and len(species) > 0, f"{name} has invalid species"
        assert all(isinstance(s, str) for s in species)


def test_default_orbit_color_is_valid_hex():
    assert _HEX_RE.match(DEFAULT_ORBIT_COLOR)


def test_init_exports():
    import materials_discovery.visualization as viz
    for sym in ("ORBIT_COLORS", "ORBIT_LABELS", "SHELL_NAMES", "PREFERRED_SPECIES", "DEFAULT_ORBIT_COLOR"):
        assert hasattr(viz, sym), f"missing export: {sym}"


def test_labels_no_intra_package_imports():
    labels_path = Path(__file__).resolve().parent.parent / "src" / "materials_discovery" / "visualization" / "labels.py"
    source = labels_path.read_text()
    assert "from materials_discovery" not in source, "labels.py must be a leaf module"
    assert "import materials_discovery" not in source, "labels.py must be a leaf module"
