from __future__ import annotations

import re

from materials_discovery.llm.schema import TranslatedStructureArtifact

_CELL_FIELD_ORDER = (
    ("a", "_cell_length_a"),
    ("b", "_cell_length_b"),
    ("c", "_cell_length_c"),
    ("alpha", "_cell_angle_alpha"),
    ("beta", "_cell_angle_beta"),
    ("gamma", "_cell_angle_gamma"),
)
_ATOM_SITE_HEADERS = (
    "_atom_site_label",
    "_atom_site_type_symbol",
    "_atom_site_fract_x",
    "_atom_site_fract_y",
    "_atom_site_fract_z",
    "_atom_site_occupancy",
)


def validate_translated_structure_for_export(artifact: TranslatedStructureArtifact) -> None:
    if artifact.target.requires_periodic_cell:
        if artifact.cell is None:
            raise ValueError("translated structure export requires cell data")
        missing_cell_keys = [key for key, _ in _CELL_FIELD_ORDER if key not in artifact.cell]
        if missing_cell_keys:
            missing_keys = ", ".join(missing_cell_keys)
            raise ValueError(f"translated structure export requires cell keys: {missing_keys}")

    if not artifact.sites:
        raise ValueError("translated structure export requires at least one site")

    if artifact.target.requires_fractional_coordinates:
        for site in artifact.sites:
            if site.fractional_position is None:
                raise ValueError(
                    "translated structure export requires fractional_position "
                    f"for site {site.label}"
                )


def emit_translated_structure(
    artifact: TranslatedStructureArtifact,
) -> TranslatedStructureArtifact:
    validate_translated_structure_for_export(artifact)

    if artifact.target.family == "cif":
        emitted_text = emit_cif_text(artifact)
    elif artifact.target.family == "material_string":
        raise NotImplementedError("material_string export not implemented yet")
    else:  # pragma: no cover - schema registry should prevent this branch
        raise ValueError(f"unsupported translation export target family: {artifact.target.family}")

    return artifact.model_copy(update={"emitted_text": emitted_text})


def emit_cif_text(artifact: TranslatedStructureArtifact) -> str:
    validate_translated_structure_for_export(artifact)
    assert artifact.cell is not None

    lines = [f"data_{_sanitize_data_block_name(artifact.source.candidate_id)}"]
    for cell_key, cif_key in _CELL_FIELD_ORDER:
        lines.append(f"{cif_key} {_format_float(artifact.cell[cell_key])}")

    lines.append("loop_")
    lines.extend(_ATOM_SITE_HEADERS)
    for site in artifact.sites:
        assert site.fractional_position is not None
        fract_x, fract_y, fract_z = site.fractional_position
        lines.append(
            " ".join(
                (
                    _format_cif_token(site.label),
                    _format_cif_token(site.species),
                    _format_float(fract_x),
                    _format_float(fract_y),
                    _format_float(fract_z),
                    _format_float(site.occupancy),
                )
            )
        )

    return "\n".join(lines) + "\n"


def _format_float(value: float) -> str:
    rounded = float(f"{float(value):.6f}")
    if rounded == 0.0:
        rounded = 0.0
    rendered = f"{rounded:.6f}".rstrip("0")
    if rendered.endswith("."):
        rendered += "0"
    return rendered


def _sanitize_data_block_name(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return sanitized or "translated_structure"


def _format_cif_token(value: str) -> str:
    if re.search(r"\s", value) is None and "'" not in value:
        return value
    escaped = value.replace("'", "''")
    return f"'{escaped}'"
