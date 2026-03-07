from __future__ import annotations

import shlex
from fractions import Fraction
from pathlib import Path
from typing import Any, cast


def _tokenize(line: str) -> list[str]:
    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _parse_scalar(value: str) -> str | float:
    cleaned = value.strip()
    if not cleaned:
        return ""
    try:
        return float(cleaned)
    except ValueError:
        return cleaned.strip("'").strip('"')


def parse_cif(path: Path) -> dict[str, Any]:
    values: dict[str, Any] = {}
    loops: list[dict[str, Any]] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        idx += 1
        if not line or line.startswith("#") or line.startswith("data_"):
            continue

        if line == "loop_":
            headers: list[str] = []
            while idx < len(lines) and lines[idx].strip().startswith("_"):
                headers.append(lines[idx].strip())
                idx += 1

            rows: list[dict[str, Any]] = []
            while idx < len(lines):
                raw = lines[idx].strip()
                if not raw or raw.startswith("#"):
                    idx += 1
                    continue
                if raw == "loop_" or raw.startswith("data_") or raw.startswith("_"):
                    break

                tokens = _tokenize(raw)
                idx += 1
                while len(tokens) < len(headers) and idx < len(lines):
                    extra = lines[idx].strip()
                    if not extra or extra.startswith("#"):
                        idx += 1
                        continue
                    if extra == "loop_" or extra.startswith("data_") or extra.startswith("_"):
                        break
                    tokens.extend(_tokenize(extra))
                    idx += 1

                if len(tokens) < len(headers):
                    raise ValueError(f"Incomplete CIF loop row in {path}")

                row = {
                    header: _parse_scalar(token)
                    for header, token in zip(headers, tokens[: len(headers)], strict=True)
                }
                rows.append(row)

            loops.append({"headers": headers, "rows": rows})
            continue

        if line.startswith("_"):
            tokens = _tokenize(line)
            if len(tokens) >= 2:
                values[tokens[0]] = _parse_scalar(tokens[1])
            continue

    return {"values": values, "loops": loops}


def _parse_constant(term: str) -> float:
    if "/" in term:
        return float(Fraction(term))
    return float(term)


def _eval_axis_expression(expression: str, coords: dict[str, float]) -> float:
    expr = expression.replace(" ", "")
    if not expr:
        raise ValueError("empty symmetry expression")
    if expr[0] not in "+-":
        expr = f"+{expr}"

    total = 0.0
    idx = 0
    while idx < len(expr):
        sign = 1.0 if expr[idx] == "+" else -1.0
        idx += 1
        start = idx
        while idx < len(expr) and expr[idx] not in "+-":
            idx += 1
        token = expr[start:idx]
        if token in {"x", "y", "z"}:
            total += sign * coords[token]
        else:
            total += sign * _parse_constant(token)
    return total % 1.0


def _parse_symmetry_operation(operation: str) -> tuple[str, str, str]:
    parts = [part.strip() for part in operation.split(",")]
    if len(parts) != 3:
        raise ValueError(f"invalid symmetry operation: {operation}")
    return parts[0], parts[1], parts[2]


def _symmetry_operations(cif: dict[str, Any]) -> list[tuple[str, str, str]]:
    for loop in cif["loops"]:
        headers = loop["headers"]
        if "_symmetry_equiv_pos_as_xyz" in headers:
            return [
                _parse_symmetry_operation(str(row["_symmetry_equiv_pos_as_xyz"]))
                for row in loop["rows"]
            ]
        if "_space_group_symop_operation_xyz" in headers:
            return [
                _parse_symmetry_operation(str(row["_space_group_symop_operation_xyz"]))
                for row in loop["rows"]
            ]
    raise ValueError("CIF does not contain symmetry operation loop")


def _atom_sites(cif: dict[str, Any]) -> list[dict[str, Any]]:
    for loop in cif["loops"]:
        headers = set(loop["headers"])
        required = {
            "_atom_site_label",
            "_atom_site_type_symbol",
            "_atom_site_fract_x",
            "_atom_site_fract_y",
            "_atom_site_fract_z",
        }
        if required.issubset(headers):
            return cast(list[dict[str, Any]], loop["rows"])
    raise ValueError("CIF does not contain atom site loop")


def expand_cif_orbits(cif_path: Path) -> dict[str, Any]:
    cif = parse_cif(cif_path)
    values = cif["values"]
    operations = _symmetry_operations(cif)
    atom_sites = _atom_sites(cif)

    orbits: list[dict[str, Any]] = []
    for site in atom_sites:
        coords = {
            "x": float(site["_atom_site_fract_x"]),
            "y": float(site["_atom_site_fract_y"]),
            "z": float(site["_atom_site_fract_z"]),
        }
        positions: set[tuple[float, float, float]] = set()
        for op_x, op_y, op_z in operations:
            positions.add(
                (
                    round(_eval_axis_expression(op_x, coords), 6),
                    round(_eval_axis_expression(op_y, coords), 6),
                    round(_eval_axis_expression(op_z, coords), 6),
                )
            )

        sorted_positions = sorted(positions)
        label = str(site["_atom_site_label"])
        symbol = str(site["_atom_site_type_symbol"])
        orbit = {
            "orbit": label.lower(),
            "label": label,
            "symbol": symbol,
            "wyckoff": site.get("_atom_site_Wyckoff_symbol"),
            "occupancy": float(site.get("_atom_site_occupancy", 1.0)),
            "sites": [
                {
                    "label": f"{label}_{index + 1:02d}",
                    "fractional_position": [x, y, z],
                }
                for index, (x, y, z) in enumerate(sorted_positions)
            ],
        }
        orbits.append(orbit)

    return {
        "space_group": values.get("_symmetry_space_group_name_H-M"),
        "space_group_number": values.get("_space_group_IT_number"),
        "base_cell": {
            "a": float(values["_cell_length_a"]),
            "b": float(values["_cell_length_b"]),
            "c": float(values["_cell_length_c"]),
            "alpha": float(values["_cell_angle_alpha"]),
            "beta": float(values["_cell_angle_beta"]),
            "gamma": float(values["_cell_angle_gamma"]),
        },
        "orbits": orbits,
    }


def export_orbit_library_from_cif(
    cif_path: Path,
    *,
    prototype_key: str,
    system_name: str,
    template_family: str,
    reference: str,
    reference_url: str | None,
    motif_center: tuple[float, float, float],
    translation_divisor: float,
    radial_scale: float,
    tangential_scale: float,
    reference_axes: tuple[tuple[float, float, float], ...],
    minimum_site_separation: float,
    preferred_species_by_symbol: dict[str, tuple[str, ...]],
    orbit_name_overrides: dict[str, str] | None = None,
    occupancy_cutoff: float = 0.0,
) -> dict[str, Any]:
    expanded = expand_cif_orbits(cif_path)
    orbits: list[dict[str, Any]] = []
    for orbit in expanded["orbits"]:
        if float(orbit["occupancy"]) < occupancy_cutoff:
            continue
        label = str(orbit["label"])
        if orbit_name_overrides is None:
            orbit_name = label.lower()
        else:
            orbit_name = orbit_name_overrides.get(label, label.lower())
        symbol = str(orbit["symbol"])
        preferred_species = preferred_species_by_symbol.get(symbol)
        orbits.append(
            {
                "orbit": orbit_name,
                "wyckoff": orbit["wyckoff"],
                "preferred_species": list(preferred_species) if preferred_species else None,
                "sites": orbit["sites"],
            }
        )

    return {
        "prototype_key": prototype_key,
        "system_name": system_name,
        "template_family": template_family,
        "source_kind": "cif_export",
        "source_cif": str(cif_path),
        "reference": reference,
        "reference_url": reference_url,
        "space_group": expanded["space_group"],
        "space_group_number": expanded["space_group_number"],
        "base_cell": expanded["base_cell"],
        "motif_center": list(motif_center),
        "translation_divisor": translation_divisor,
        "radial_scale": radial_scale,
        "tangential_scale": tangential_scale,
        "reference_axes": [list(axis) for axis in reference_axes],
        "minimum_site_separation": minimum_site_separation,
        "orbits": orbits,
    }
