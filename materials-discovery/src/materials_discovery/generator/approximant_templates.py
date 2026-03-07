from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from math import cos, pi, sin, sqrt
from pathlib import Path

from materials_discovery.common.coordinates import FractionalCoord
from materials_discovery.common.io import load_json_object, workspace_root
from materials_discovery.common.schema import QPhiCoord

PHI = (1.0 + 5.0**0.5) / 2.0


def _normalize(vector: tuple[float, float, float]) -> FractionalCoord:
    norm = sqrt(sum(component * component for component in vector))
    if norm <= 1e-12:
        raise ValueError("template vectors must have positive norm")
    return tuple(component / norm for component in vector)  # type: ignore[return-value]


def _centered_position(
    vector: tuple[float, float, float],
    radius: float,
) -> FractionalCoord:
    normalized = _normalize(vector)
    return tuple(round(0.5 + radius * component, 6) for component in normalized)  # type: ignore[return-value]


def _icosahedral_shell_positions() -> tuple[FractionalCoord, ...]:
    raw_vertices = (
        (0.0, 1.0, PHI),
        (0.0, 1.0, -PHI),
        (0.0, -1.0, PHI),
        (0.0, -1.0, -PHI),
        (1.0, PHI, 0.0),
        (1.0, -PHI, 0.0),
        (-1.0, PHI, 0.0),
        (-1.0, -PHI, 0.0),
        (PHI, 0.0, 1.0),
        (PHI, 0.0, -1.0),
        (-PHI, 0.0, 1.0),
        (-PHI, 0.0, -1.0),
    )
    return tuple(_centered_position(vertex, radius=0.235) for vertex in raw_vertices)


def _ring_positions(
    count: int,
    *,
    radius: float,
    z: float,
    phase: float = 0.0,
) -> tuple[FractionalCoord, ...]:
    return tuple(
        (
            round(0.5 + radius * cos(2.0 * pi * index / count + phase), 6),
            round(0.5 + radius * sin(2.0 * pi * index / count + phase), 6),
            round(z, 6),
        )
        for index in range(count)
    )


def _cubic_corner_positions() -> tuple[FractionalCoord, ...]:
    corner = 0.29
    return tuple(
        (round(x, 6), round(y, 6), round(z, 6))
        for x in (corner, 1.0 - corner)
        for y in (corner, 1.0 - corner)
        for z in (corner, 1.0 - corner)
    )


def _base_cell(
    a: float,
    *,
    b: float | None = None,
    c: float | None = None,
    alpha: float = 90.0,
    beta: float = 90.0,
    gamma: float = 90.0,
) -> dict[str, float]:
    return {
        "a": a,
        "b": a if b is None else b,
        "c": a if c is None else c,
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
    }


def _position_to_qphi(position: FractionalCoord, site_index: int) -> QPhiCoord:
    centered = tuple(component - 0.5 for component in position)
    return tuple(
        (
            int(round(6.0 * value)),
            int(round(3.0 * value * PHI)) + ((site_index + axis_index) % 3) - 1,
        )
        for axis_index, value in enumerate(centered)
    )  # type: ignore[return-value]


def _coerce_float(value: object, field_name: str) -> float:
    if isinstance(value, (int, float, str)):
        return float(value)
    raise ValueError(f"prototype field {field_name} must be numeric")


@dataclass(frozen=True)
class TemplateSite:
    label: str
    base_qphi: QPhiCoord
    base_fractional_position: FractionalCoord
    orbit: str
    preferred_species: tuple[str, ...] | None = None
    wyckoff: str | None = None


@dataclass(frozen=True)
class ApproximantTemplate:
    name: str
    prototype_key: str
    anchor_system: str | None
    reference: str
    reference_url: str | None
    base_cell: dict[str, float]
    sites: tuple[TemplateSite, ...]
    motif_center: FractionalCoord
    translation_divisor: float
    radial_scale: float
    tangential_scale: float
    reference_axes: tuple[FractionalCoord, FractionalCoord, FractionalCoord]
    minimum_site_separation: float
    space_group: str | None = None
    source_kind: str = "generic"


def _build_sites(
    positions: tuple[FractionalCoord, ...],
    *,
    orbit: str,
    label_prefix: str,
    start_index: int,
) -> tuple[TemplateSite, ...]:
    return tuple(
        TemplateSite(
            label=f"{label_prefix}{index:02d}",
            base_qphi=_position_to_qphi(position, index),
            base_fractional_position=position,
            orbit=orbit,
        )
        for index, position in enumerate(positions, start=start_index)
    )


def _generic_icosahedral_template() -> ApproximantTemplate:
    return ApproximantTemplate(
        name="icosahedral_approximant_1_1",
        prototype_key="generic_icosahedral_1_1",
        anchor_system=None,
        reference="Generic 1/1 icosahedral approximant motif",
        reference_url=None,
        base_cell=_base_cell(14.2),
        sites=_build_sites(
            _icosahedral_shell_positions(),
            orbit="generic_icosa_shell",
            label_prefix="S",
            start_index=1,
        ),
        motif_center=(0.5, 0.5, 0.5),
        translation_divisor=8.0,
        radial_scale=0.028,
        tangential_scale=0.064,
        reference_axes=(
            _normalize((0.0, 1.0, PHI)),
            _normalize((1.0, PHI, 0.0)),
            _normalize((PHI, 0.0, 1.0)),
        ),
        minimum_site_separation=0.15,
    )


def _generic_decagonal_template() -> ApproximantTemplate:
    return ApproximantTemplate(
        name="decagonal_proxy_2_1",
        prototype_key="generic_decagonal_2_1",
        anchor_system=None,
        reference="Generic decagonal approximant motif",
        reference_url=None,
        base_cell=_base_cell(11.8, c=16.0),
        sites=_build_sites(
            _ring_positions(5, radius=0.24, z=0.34)
            + _ring_positions(5, radius=0.24, z=0.66, phase=pi / 5.0),
            orbit="generic_decagonal_ring",
            label_prefix="S",
            start_index=1,
        ),
        motif_center=(0.5, 0.5, 0.5),
        translation_divisor=10.0,
        radial_scale=0.02,
        tangential_scale=0.05,
        reference_axes=(
            _normalize((1.0, 0.0, 0.0)),
            _normalize((cos(pi / 5.0), sin(pi / 5.0), 0.0)),
            _normalize((0.0, 0.0, 1.0)),
        ),
        minimum_site_separation=0.13,
    )


def _generic_cubic_template() -> ApproximantTemplate:
    return ApproximantTemplate(
        name="cubic_proxy_1_0",
        prototype_key="generic_cubic_1_0",
        anchor_system=None,
        reference="Generic cubic approximant motif",
        reference_url=None,
        base_cell=_base_cell(10.0),
        sites=_build_sites(
            _cubic_corner_positions(),
            orbit="generic_cubic_corner",
            label_prefix="S",
            start_index=1,
        ),
        motif_center=(0.5, 0.5, 0.5),
        translation_divisor=6.0,
        radial_scale=0.018,
        tangential_scale=0.04,
        reference_axes=(
            _normalize((1.0, 0.0, 0.0)),
            _normalize((0.0, 1.0, 0.0)),
            _normalize((0.0, 0.0, 1.0)),
        ),
        minimum_site_separation=0.18,
    )


FAMILY_TEMPLATES: dict[str, ApproximantTemplate] = {
    "icosahedral_approximant_1_1": _generic_icosahedral_template(),
    "decagonal_proxy_2_1": _generic_decagonal_template(),
    "cubic_proxy_1_0": _generic_cubic_template(),
}

SYSTEM_TEMPLATE_PATHS: dict[tuple[str, str], Path] = {
    ("Al-Cu-Fe", "icosahedral_approximant_1_1"): workspace_root()
    / "data"
    / "prototypes"
    / "al_cu_fe_mackay_1_1.json",
    ("Al-Pd-Mn", "decagonal_proxy_2_1"): workspace_root()
    / "data"
    / "prototypes"
    / "al_pd_mn_xi_prime.json",
    ("Sc-Zn", "cubic_proxy_1_0"): workspace_root()
    / "data"
    / "prototypes"
    / "sc_zn_tsai_sczn6.json",
}


def _template_from_orbit_library(data: dict[str, object]) -> ApproximantTemplate:
    raw_orbits = data["orbits"]
    if not isinstance(raw_orbits, list):
        raise ValueError("prototype orbit library must contain an 'orbits' list")

    sites: list[TemplateSite] = []
    for orbit in raw_orbits:
        if not isinstance(orbit, dict):
            raise ValueError("prototype orbit records must be JSON objects")
        preferred = orbit.get("preferred_species")
        preferred_species = None
        if isinstance(preferred, list):
            preferred_species = tuple(str(value) for value in preferred)
        wyckoff = orbit.get("wyckoff")
        orbit_name = str(orbit["orbit"])
        raw_sites = orbit.get("sites")
        if not isinstance(raw_sites, list):
            raise ValueError("prototype orbit records must contain a 'sites' list")

        for raw_site in raw_sites:
            if not isinstance(raw_site, dict):
                raise ValueError("prototype site records must be JSON objects")
            position = raw_site["fractional_position"]
            if (
                not isinstance(position, list)
                or len(position) != 3
                or not all(isinstance(value, (int, float)) for value in position)
            ):
                raise ValueError("prototype sites must define 3D fractional positions")
            fractional_position = (
                round(float(position[0]), 6),
                round(float(position[1]), 6),
                round(float(position[2]), 6),
            )
            site_index = len(sites) + 1
            sites.append(
                TemplateSite(
                    label=str(raw_site["label"]),
                    base_qphi=_position_to_qphi(fractional_position, site_index),
                    base_fractional_position=fractional_position,
                    orbit=orbit_name,
                    preferred_species=preferred_species,
                    wyckoff=None if wyckoff is None else str(wyckoff),
                )
            )

    raw_cell = data["base_cell"]
    if not isinstance(raw_cell, dict):
        raise ValueError("prototype orbit library must contain a 'base_cell' mapping")
    raw_center = data["motif_center"]
    raw_axes = data["reference_axes"]
    if not isinstance(raw_center, list) or len(raw_center) != 3:
        raise ValueError("prototype orbit library must contain a 3D motif_center")
    if not isinstance(raw_axes, list) or len(raw_axes) != 3:
        raise ValueError("prototype orbit library must contain 3 reference axes")

    raw_reference_axes = tuple(
        (
            float(axis[0]),
            float(axis[1]),
            float(axis[2]),
        )
        for axis in raw_axes
        if isinstance(axis, list) and len(axis) == 3
    )
    if len(raw_reference_axes) != 3:
        raise ValueError("prototype reference axes must all be 3D vectors")
    reference_axes: tuple[FractionalCoord, FractionalCoord, FractionalCoord] = (
        raw_reference_axes[0],
        raw_reference_axes[1],
        raw_reference_axes[2],
    )

    return ApproximantTemplate(
        name=str(data["template_family"]),
        prototype_key=str(data["prototype_key"]),
        anchor_system=None if data.get("system_name") is None else str(data["system_name"]),
        reference=str(data["reference"]),
        reference_url=None if data.get("reference_url") is None else str(data["reference_url"]),
        base_cell={
            key: _coerce_float(value, f"base_cell.{key}")
            for key, value in raw_cell.items()
        },
        sites=tuple(sites),
        motif_center=(
            _coerce_float(raw_center[0], "motif_center[0]"),
            _coerce_float(raw_center[1], "motif_center[1]"),
            _coerce_float(raw_center[2], "motif_center[2]"),
        ),
        translation_divisor=_coerce_float(data["translation_divisor"], "translation_divisor"),
        radial_scale=_coerce_float(data["radial_scale"], "radial_scale"),
        tangential_scale=_coerce_float(data["tangential_scale"], "tangential_scale"),
        reference_axes=reference_axes,
        minimum_site_separation=_coerce_float(
            data["minimum_site_separation"],
            "minimum_site_separation",
        ),
        space_group=None if data.get("space_group") is None else str(data["space_group"]),
        source_kind=str(data.get("source_kind", "orbit_library")),
    )


@cache
def _load_orbit_library_template(path_str: str) -> ApproximantTemplate:
    return _template_from_orbit_library(load_json_object(Path(path_str)))


def get_template(template_family: str) -> ApproximantTemplate:
    try:
        return FAMILY_TEMPLATES[template_family]
    except KeyError as exc:
        raise ValueError(f"Unknown template_family: {template_family}") from exc


def resolve_template(system_name: str, template_family: str) -> ApproximantTemplate:
    path = SYSTEM_TEMPLATE_PATHS.get((system_name, template_family))
    if path is not None and path.exists():
        return _load_orbit_library_template(str(path))
    return get_template(template_family)
