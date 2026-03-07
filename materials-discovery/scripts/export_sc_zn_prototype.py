#!/usr/bin/env python3

from __future__ import annotations

import json
from math import sqrt
from pathlib import Path

from materials_discovery.generator.prototype_import import export_orbit_library_from_cif

PHI = (1.0 + 5.0**0.5) / 2.0


def _normalize(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    norm = sqrt(sum(component * component for component in vector))
    if norm <= 1e-12:
        raise ValueError("reference axes must have positive norm")
    return tuple(component / norm for component in vector)  # type: ignore[return-value]


def main() -> None:
    workspace = Path(__file__).resolve().parents[1]
    cif_path = workspace / "data" / "prototypes" / "raw" / "sc_zn_cod_4344182.cif"
    output_path = workspace / "data" / "prototypes" / "sc_zn_tsai_sczn6.json"

    payload = export_orbit_library_from_cif(
        cif_path,
        prototype_key="sc_zn_tsai_sczn6",
        system_name="Sc-Zn",
        template_family="cubic_proxy_1_0",
        reference=(
            "Tsai-cluster 1/1 cubic approximant exported from COD entry 4344182 "
            "(Cu0.66Sc3Zn17.34, Im-3), mapped onto the Sc-Zn anchor with Cu-bearing orbits "
            "treated as Zn-like for no-DFT generation."
        ),
        reference_url="https://www.crystallography.net/cod/4344182.html",
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
        preferred_species_by_symbol={
            "Sc": ("Sc",),
            "Zn": ("Zn",),
            "Cu": ("Zn", "Sc"),
        },
        orbit_name_overrides={
            "Sc1": "tsai_sc1",
            "Cu1": "tsai_cu1",
            "Zn1": "tsai_zn1",
            "Zn2": "tsai_zn2",
            "Zn3": "tsai_zn3",
            "Zn4": "tsai_zn4",
            "Zn5": "tsai_zn5",
            "Zn6": "tsai_zn6",
            "Zn7": "tsai_zn7",
        },
        occupancy_cutoff=0.2,
    )

    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
