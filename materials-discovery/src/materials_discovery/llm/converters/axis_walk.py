from __future__ import annotations

from math import sqrt
from typing import Any

from materials_discovery.common.coordinates import qphi_coord_to_float
from materials_discovery.common.schema import QPhiCoord

_AXIS_VOCAB = (
    ("blue", 0),
    ("green", 0),
    ("red", 1),
    ("orange", 1),
    ("yellow", 2),
    ("purple", 2),
)


def _command_for_component(color: str, axis_index: int, coefficient: int) -> str:
    polarity = "+" if coefficient >= 0 else "-"
    magnitude = max(1, abs(coefficient))
    return f"size {magnitude} {color} {polarity}{axis_index}"


def decompose_qphi_to_axis_walk(qphi: QPhiCoord, *, max_steps: int = 12) -> dict[str, Any]:
    components = [
        (qphi[0][0], _AXIS_VOCAB[0]),
        (qphi[0][1], _AXIS_VOCAB[1]),
        (qphi[1][0], _AXIS_VOCAB[2]),
        (qphi[1][1], _AXIS_VOCAB[3]),
        (qphi[2][0], _AXIS_VOCAB[4]),
        (qphi[2][1], _AXIS_VOCAB[5]),
    ]
    commands = [
        _command_for_component(color, axis_index, coefficient)
        for coefficient, (color, axis_index) in components
        if coefficient != 0
    ]
    total_components = len(commands)
    unresolved_axes: list[str] = []

    if total_components == 0:
        return {
            "strategy": "direct_basis",
            "commands": [],
            "step_count": 0,
            "unresolved_axes": [],
        }

    nonzero_pairs = sum(1 for pair in qphi if pair != (0, 0))
    if nonzero_pairs == 1 and all(pair[1] == 0 for pair in qphi):
        return {
            "strategy": "direct_basis",
            "commands": commands,
            "step_count": total_components,
            "unresolved_axes": [],
        }

    if total_components <= max_steps:
        return {
            "strategy": "bounded_search",
            "commands": commands,
            "step_count": total_components,
            "unresolved_axes": [],
        }

    if total_components <= (2 * max_steps):
        truncated = commands[:max_steps]
        for coefficient, (color, axis_index) in components[max_steps:]:
            if coefficient != 0:
                unresolved_axes.append(f"{color}:{axis_index}")
        return {
            "strategy": "anchored_fallback",
            "commands": truncated,
            "step_count": len(truncated),
            "unresolved_axes": unresolved_axes,
        }

    return {
        "strategy": "heuristic_fallback",
        "commands": ["move"],
        "step_count": 1,
        "unresolved_axes": [color for _, (color, _) in components if _ != 0],
    }


def assess_geometry_equivalence(
    source_qphi: QPhiCoord,
    exported_qphi: QPhiCoord,
    *,
    tolerance: float = 1e-6,
) -> dict[str, Any]:
    source = qphi_coord_to_float(source_qphi)
    exported = qphi_coord_to_float(exported_qphi)
    error = sqrt(
        sum((src - dst) ** 2 for src, dst in zip(source, exported, strict=True))
    )
    return {
        "equivalent": error <= tolerance,
        "error": round(float(error), 8),
        "tolerance": tolerance,
    }
