from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from shlex import split as shlex_split
from typing import Any

from materials_discovery.common.manifest import file_sha256
from materials_discovery.data_sources.schema import (
    CanonicalCommonFields,
    CanonicalRawSourceRecord,
    LineageInfo,
    RawPayloadInfo,
    SnapshotInfo,
    SourceIdentity,
    AccessInfo,
    LicenseInfo,
    StructureRepresentation,
    derive_local_record_id,
)
from materials_discovery.data_sources.storage import workspace_relative
from materials_discovery.data_sources.types import SourceAdapterInfo

_CELL_KEYS = {
    "_cell_length_a": "a",
    "_cell_length_b": "b",
    "_cell_length_c": "c",
    "_cell_angle_alpha": "alpha",
    "_cell_angle_beta": "beta",
    "_cell_angle_gamma": "gamma",
}
_SPACE_GROUP_KEYS = (
    "_space_group_name_h-m_alt",
    "_symmetry_space_group_name_h-m",
)


def _clean_lines(text: str) -> list[str]:
    cleaned: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        cleaned.append(stripped)
    return cleaned


def _parse_scalar_tokens(line: str) -> tuple[str, str]:
    tokens = shlex_split(line, comments=False, posix=True)
    if len(tokens) < 2:
        raise ValueError(f"invalid CIF scalar line: {line}")
    return tokens[0], tokens[1]


def _parse_cif(path: Path) -> dict[str, Any]:
    lines = _clean_lines(path.read_text(encoding="utf-8"))
    scalars: dict[str, str] = {}
    loops: list[tuple[list[str], list[list[str]]]] = []

    index = 0
    while index < len(lines):
        line = lines[index]
        lower_line = line.lower()

        if lower_line == "loop_":
            index += 1
            headers: list[str] = []
            while index < len(lines) and lines[index].startswith("_"):
                headers.append(shlex_split(lines[index], comments=False, posix=True)[0].lower())
                index += 1

            rows: list[list[str]] = []
            while index < len(lines):
                candidate = lines[index]
                lowered = candidate.lower()
                if lowered == "loop_" or candidate.startswith("_") or lowered.startswith("data_"):
                    break
                rows.append(shlex_split(candidate, comments=False, posix=True))
                index += 1
            loops.append((headers, rows))
            continue

        if line.startswith("_"):
            key, value = _parse_scalar_tokens(line)
            scalars[key.lower()] = value

        index += 1

    cell = {
        field_name: float(scalars[cif_key.lower()])
        for cif_key, field_name in _CELL_KEYS.items()
        if cif_key.lower() in scalars
    }
    if len(cell) != len(_CELL_KEYS):
        missing = sorted(field for field in _CELL_KEYS if field.lower() not in scalars)
        raise ValueError(f"CIF missing required cell keys: {missing}")

    space_group = None
    for key in _SPACE_GROUP_KEYS:
        if key in scalars:
            space_group = scalars[key]
            break

    atom_headers: list[str] | None = None
    atom_rows: list[list[str]] | None = None
    required_headers = {
        "_atom_site_label",
        "_atom_site_type_symbol",
        "_atom_site_fract_x",
        "_atom_site_fract_y",
        "_atom_site_fract_z",
    }
    for headers, rows in loops:
        if required_headers.issubset(set(headers)):
            atom_headers = headers
            atom_rows = rows
            break

    if atom_headers is None or atom_rows is None:
        raise ValueError("CIF missing atom site loop")

    header_index = {header: idx for idx, header in enumerate(atom_headers)}
    sites: list[dict[str, Any]] = []
    composition_counts: OrderedDict[str, float] = OrderedDict()
    for row in atom_rows:
        label = row[header_index["_atom_site_label"]]
        species = row[header_index["_atom_site_type_symbol"]]
        fract_x = float(row[header_index["_atom_site_fract_x"]])
        fract_y = float(row[header_index["_atom_site_fract_y"]])
        fract_z = float(row[header_index["_atom_site_fract_z"]])
        occupancy = (
            float(row[header_index["_atom_site_occupancy"]])
            if "_atom_site_occupancy" in header_index
            else 1.0
        )
        sites.append(
            {
                "label": label,
                "species": species,
                "fractional_position": [fract_x, fract_y, fract_z],
                "occupancy": occupancy,
            }
        )
        composition_counts[species] = composition_counts.get(species, 0.0) + occupancy

    formula = "".join(
        f"{element}{count:g}" if abs(count - 1.0) > 1e-8 else element
        for element, count in composition_counts.items()
    )
    return {
        "cell": cell,
        "space_group": space_group,
        "sites": sites,
        "site_count": len(sites),
        "composition": dict(composition_counts),
        "formula": formula,
    }


def cif_to_canonical_record(
    raw_row: dict[str, Any],
    snapshot_id: str,
    raw_payload_path: Path,
    adapter_info: SourceAdapterInfo,
) -> CanonicalRawSourceRecord:
    cif_path = Path(str(raw_row["cif_path"]))
    cod_id = str(raw_row.get("cod_id") or cif_path.stem)
    parsed = _parse_cif(cif_path)
    local_record_id = derive_local_record_id("cod", snapshot_id, cod_id)
    structure_summary = {
        "cell": parsed["cell"],
        "space_group": parsed["space_group"],
        "site_count": parsed["site_count"],
        "sites": parsed["sites"],
        "formula_reduced": parsed["formula"],
    }

    return CanonicalRawSourceRecord(
        local_record_id=local_record_id,
        record_kind="structure",
        source=SourceIdentity(
            source_key="cod",
            source_name="Crystallography Open Database",
            source_record_id=cod_id,
            source_record_url=str(raw_row.get("source_record_url")) if raw_row.get("source_record_url") else None,
            record_title=parsed["formula"],
        ),
        access=AccessInfo(
            access_level="open",
            auth_required=False,
            access_surface="manual",
            redistribution_posture="allowed",
        ),
        license=LicenseInfo(
            license_expression="CC0-1.0",
            license_category="open",
            attribution_required=False,
            commercial_use_allowed=True,
        ),
        snapshot=SnapshotInfo(
            snapshot_id=snapshot_id,
            source_version=adapter_info.version,
            source_release_date=None,
            retrieved_at_utc=str(raw_row.get("retrieved_at_utc") or "2026-04-03T00:00:00Z"),
            retrieval_mode="manual",
            snapshot_manifest_path="",
        ),
        raw_payload=RawPayloadInfo(
            payload_path=workspace_relative(raw_payload_path),
            payload_format="jsonl",
            content_hash=file_sha256(cif_path),
            raw_excerpt={"cif_path": workspace_relative(cif_path)},
        ),
        common=CanonicalCommonFields(
            chemical_system="-".join(sorted(parsed["composition"])),
            elements=sorted(parsed["composition"]),
            formula_raw=parsed["formula"],
            formula_reduced=parsed["formula"],
            composition=parsed["composition"],
            structure_representations=[
                StructureRepresentation(
                    representation_kind="cif",
                    payload_path=workspace_relative(cif_path),
                    payload_format="cif",
                    content_hash=file_sha256(cif_path),
                    structure_summary=structure_summary,
                )
            ],
            space_group=parsed["space_group"],
            reported_properties={"site_count": parsed["site_count"]},
        ),
        lineage=LineageInfo(
            adapter_key=adapter_info.adapter_key,
            adapter_family=adapter_info.adapter_family,
            adapter_version=adapter_info.version,
            fetch_manifest_id=f"{adapter_info.adapter_key}:fetch:{snapshot_id}",
            normalize_manifest_id=f"{adapter_info.adapter_key}:normalize:{snapshot_id}",
        ),
        source_metadata={
            "raw_keys": sorted(raw_row),
            "cif_path": workspace_relative(cif_path),
            "cell_source": "cif",
        },
    )
