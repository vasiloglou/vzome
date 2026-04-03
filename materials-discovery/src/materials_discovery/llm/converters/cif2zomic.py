from __future__ import annotations

from collections import Counter
from pathlib import Path

from materials_discovery.common.io import workspace_root
from materials_discovery.data_sources.schema import CanonicalRawSourceRecord
from materials_discovery.generator.prototype_import import expand_cif_orbits, parse_cif
from materials_discovery.generator.zomic_bridge import _infer_orbit_name
from materials_discovery.llm.schema import (
    CorpusExample,
    CorpusProvenance,
    CorpusValidationState,
)


def _normalize_cif_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(workspace_root()))
    except ValueError:
        return str(path.resolve())


def _cif_orbit_script(expanded: dict[str, object]) -> tuple[str, list[str], list[str], dict[str, float]]:
    orbit_names: list[str] = []
    labels: list[str] = []
    composition_counts: Counter[str] = Counter()
    lines = [
        "// source=cif",
        f"// space_group={expanded.get('space_group')}",
        "",
    ]
    orbits = expanded.get("orbits", [])
    for orbit_index, orbit in enumerate(orbits):
        if not isinstance(orbit, dict):
            continue
        orbit_name = _infer_orbit_name(str(orbit.get("label", orbit["orbit"])))
        orbit_names.append(orbit_name)
        symbol = str(orbit.get("symbol", "X"))
        lines.append(f"// orbit={orbit_name}")
        lines.append("branch {")
        for site_index, site in enumerate(orbit.get("sites", []), start=1):
            if not isinstance(site, dict):
                continue
            label = str(site["label"])
            labels.append(label)
            composition_counts[symbol] += float(orbit.get("occupancy", 1.0))
            lines.append("  branch {")
            lines.append(f"    size {orbit_index + site_index} blue +0")
            lines.append(f"    label {label}")
            lines.append("  }")
        lines.append("}")
        lines.append("")
    return ("\n".join(lines).strip() + "\n", labels, orbit_names, dict(composition_counts))


def _expand_without_symmetry(cif_path: Path) -> dict[str, object]:
    parsed = parse_cif(cif_path)
    values = parsed["values"]
    atom_loop = next(
        loop
        for loop in parsed["loops"]
        if {
            "_atom_site_label",
            "_atom_site_type_symbol",
            "_atom_site_fract_x",
            "_atom_site_fract_y",
            "_atom_site_fract_z",
        }.issubset(set(loop["headers"]))
    )
    orbits: list[dict[str, object]] = []
    for row in atom_loop["rows"]:
        label = str(row["_atom_site_label"])
        symbol = str(row["_atom_site_type_symbol"])
        orbits.append(
            {
                "orbit": label.lower(),
                "label": label,
                "symbol": symbol,
                "occupancy": float(row.get("_atom_site_occupancy", 1.0)),
                "sites": [
                    {
                        "label": f"{label}_01",
                        "fractional_position": [
                            float(row["_atom_site_fract_x"]),
                            float(row["_atom_site_fract_y"]),
                            float(row["_atom_site_fract_z"]),
                        ],
                    }
                ],
            }
        )
    return {
        "space_group": values.get("_symmetry_space_group_name_h-m"),
        "orbits": orbits,
    }


def cif_path_to_zomic(
    cif_path: Path,
    *,
    source_family: str,
    source_record_id: str,
    system: str | None = None,
) -> CorpusExample:
    try:
        expanded = expand_cif_orbits(cif_path)
    except ValueError as exc:
        if "symmetry operation loop" not in str(exc):
            raise
        expanded = _expand_without_symmetry(cif_path)
    zomic_text, labels, orbit_names, composition = _cif_orbit_script(expanded)
    return CorpusExample(
        provenance=CorpusProvenance(
            example_id=f"{source_family}:{source_record_id}",
            source_family=source_family,
            source_path=_normalize_cif_path(cif_path),
            source_record_id=source_record_id,
            system=system,
            fidelity_tier="approximate",
        ),
        zomic_text=zomic_text,
        labels=labels,
        orbit_names=orbit_names,
        composition=composition or None,
        properties={
            "source_name": source_family,
            "space_group": expanded.get("space_group"),
            "loader_hint": "cif_conversion",
        },
        validation=CorpusValidationState(
            parse_status="pending",
            compile_status="pending",
            site_count=len(labels),
        ),
    )


def _resolve_representation_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return workspace_root() / path


def _fallback_canonical_example(record: CanonicalRawSourceRecord) -> CorpusExample:
    labels = [f"phase.{element.lower()}" for element in record.common.elements or record.common.composition or {}]
    lines = [
        f"// source={record.source.source_name}",
        f"// record_id={record.local_record_id}",
        "branch {",
    ]
    for label in labels:
        lines.append(f"  label {label}")
    lines.append("}")
    return CorpusExample(
        provenance=CorpusProvenance(
            example_id=f"canonical_source:{record.local_record_id}",
            source_family="canonical_source",
            source_path=record.raw_payload.payload_path,
            source_record_id=record.local_record_id,
            system=record.common.chemical_system,
            fidelity_tier="approximate",
        ),
        zomic_text="\n".join(lines) + "\n",
        labels=labels,
        orbit_names=["phase"],
        composition=record.common.composition,
        properties={
            "source_name": record.source.source_name,
            "space_group": record.common.space_group,
            "source_key": record.source.source_key,
            "loader_hint": "cif_conversion",
        },
        validation=CorpusValidationState(
            parse_status="pending",
            compile_status="pending",
            site_count=len(labels),
        ),
    )


def canonical_record_to_zomic(record: CanonicalRawSourceRecord) -> CorpusExample:
    cif_representation = next(
        (
            representation
            for representation in record.common.structure_representations
            if representation.representation_kind == "cif" and representation.payload_path
        ),
        None,
    )
    if cif_representation is None:
        return _fallback_canonical_example(record)

    example = cif_path_to_zomic(
        _resolve_representation_path(cif_representation.payload_path),
        source_family="canonical_source",
        source_record_id=record.local_record_id,
        system=record.common.chemical_system,
    )
    properties = dict(example.properties)
    properties["source_name"] = record.source.source_name
    properties["space_group"] = record.common.space_group or properties.get("space_group")
    properties["source_key"] = record.source.source_key
    provenance = example.provenance.model_copy(
        update={"source_path": cif_representation.payload_path}
    )
    return example.model_copy(update={"provenance": provenance, "properties": properties})
