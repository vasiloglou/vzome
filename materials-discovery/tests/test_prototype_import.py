from __future__ import annotations

from pathlib import Path

from materials_discovery.generator.prototype_import import (
    expand_cif_orbits,
    export_orbit_library_from_cif,
)

PHI = (1.0 + 5.0**0.5) / 2.0


def _normalize(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    norm = sum(component * component for component in vector) ** 0.5
    return (
        vector[0] / norm,
        vector[1] / norm,
        vector[2] / norm,
    )


def test_expand_cif_orbits_extracts_space_group_and_multiplicities() -> None:
    workspace = Path(__file__).resolve().parents[1]
    cif_path = workspace / "data" / "prototypes" / "raw" / "sc_zn_cod_4344182.cif"

    expanded = expand_cif_orbits(cif_path)

    assert expanded["space_group"] == "I m -3"
    assert len(expanded["orbits"]) == 9
    multiplicities = {orbit["label"]: len(orbit["sites"]) for orbit in expanded["orbits"]}
    assert multiplicities["Sc1"] == 24
    assert multiplicities["Zn3"] == 48


def test_export_orbit_library_from_cif_maps_species_preferences() -> None:
    workspace = Path(__file__).resolve().parents[1]
    cif_path = workspace / "data" / "prototypes" / "raw" / "sc_zn_cod_4344182.cif"

    exported = export_orbit_library_from_cif(
        cif_path,
        prototype_key="sc_zn_tsai_sczn6",
        system_name="Sc-Zn",
        template_family="cubic_proxy_1_0",
        reference="test export",
        reference_url=None,
        motif_center=(0.5, 0.5, 0.5),
        translation_divisor=10.0,
        radial_scale=0.012,
        tangential_scale=0.026,
        reference_axes=(
            _normalize((0.0, 1.0, PHI)),
            _normalize((1.0, PHI, 0.0)),
            _normalize((PHI, 0.0, 1.0)),
        ),
        minimum_site_separation=0.08,
        preferred_species_by_symbol={"Sc": ("Sc",), "Zn": ("Zn",), "Cu": ("Zn",)},
        occupancy_cutoff=0.2,
    )

    assert exported["source_kind"] == "cif_export"
    assert exported["space_group"] == "I m -3"
    sc_orbit = next(orbit for orbit in exported["orbits"] if orbit["orbit"] == "sc1")
    assert sc_orbit["preferred_species"] == ["Sc"]
