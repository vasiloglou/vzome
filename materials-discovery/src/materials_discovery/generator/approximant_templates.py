from __future__ import annotations

from dataclasses import dataclass

from materials_discovery.common.schema import QPhiCoord


@dataclass(frozen=True)
class TemplateSite:
    label: str
    base_qphi: QPhiCoord


@dataclass(frozen=True)
class ApproximantTemplate:
    name: str
    cell_scale: float
    sites: tuple[TemplateSite, ...]


TEMPLATES: dict[str, ApproximantTemplate] = {
    "icosahedral_approximant_1_1": ApproximantTemplate(
        name="icosahedral_approximant_1_1",
        cell_scale=14.2,
        sites=(
            TemplateSite("S1", ((1, 0), (0, 1), (-1, 1))),
            TemplateSite("S2", ((0, 1), (1, 0), (1, 1))),
            TemplateSite("S3", ((-1, 1), (1, 0), (0, 1))),
            TemplateSite("S4", ((1, 1), (-1, 0), (0, 1))),
            TemplateSite("S5", ((0, -1), (1, 1), (1, 0))),
            TemplateSite("S6", ((1, 0), (1, -1), (0, 1))),
            TemplateSite("S7", ((-1, 0), (0, 1), (1, 1))),
            TemplateSite("S8", ((0, 1), (-1, 1), (1, 0))),
            TemplateSite("S9", ((1, -1), (1, 0), (0, 1))),
            TemplateSite("S10", ((0, 1), (1, 1), (-1, 0))),
            TemplateSite("S11", ((1, 0), (0, -1), (1, 1))),
            TemplateSite("S12", ((-1, 1), (0, 1), (1, 0))),
        ),
    ),
    "decagonal_proxy_2_1": ApproximantTemplate(
        name="decagonal_proxy_2_1",
        cell_scale=11.8,
        sites=(
            TemplateSite("S1", ((1, 0), (0, 1), (0, 0))),
            TemplateSite("S2", ((0, 1), (1, 0), (0, 0))),
            TemplateSite("S3", ((1, -1), (0, 1), (0, 0))),
            TemplateSite("S4", ((0, 1), (1, -1), (0, 0))),
            TemplateSite("S5", ((-1, 1), (1, 0), (0, 0))),
            TemplateSite("S6", ((1, 0), (-1, 1), (0, 0))),
            TemplateSite("S7", ((0, -1), (1, 1), (0, 0))),
            TemplateSite("S8", ((1, 1), (0, -1), (0, 0))),
            TemplateSite("S9", ((-1, 0), (0, 1), (0, 0))),
            TemplateSite("S10", ((0, 1), (-1, 0), (0, 0))),
        ),
    ),
    "cubic_proxy_1_0": ApproximantTemplate(
        name="cubic_proxy_1_0",
        cell_scale=10.0,
        sites=(
            TemplateSite("S1", ((1, 0), (0, 0), (0, 0))),
            TemplateSite("S2", ((0, 0), (1, 0), (0, 0))),
            TemplateSite("S3", ((0, 0), (0, 0), (1, 0))),
            TemplateSite("S4", ((-1, 0), (0, 0), (0, 0))),
            TemplateSite("S5", ((0, 0), (-1, 0), (0, 0))),
            TemplateSite("S6", ((0, 0), (0, 0), (-1, 0))),
            TemplateSite("S7", ((1, 0), (1, 0), (0, 0))),
            TemplateSite("S8", ((0, 0), (1, 0), (1, 0))),
        ),
    ),
}


def get_template(template_family: str) -> ApproximantTemplate:
    try:
        return TEMPLATES[template_family]
    except KeyError as exc:
        raise ValueError(f"Unknown template_family: {template_family}") from exc
