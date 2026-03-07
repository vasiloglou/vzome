from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, TypedDict

from materials_discovery.common.coordinates import (
    cartesian_to_fractional,
    cell_matrix_from_cell,
)
from materials_discovery.common.io import (
    load_json_object,
    load_yaml,
    workspace_root,
    write_json_object,
)
from materials_discovery.common.schema import (
    SystemConfig,
    ZomicDesignConfig,
    ZomicExportSummary,
)


def repo_root() -> Path:
    return workspace_root().parent


def _detect_java_home() -> str | None:
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        return java_home

    candidates = [
        Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"),
        Path("/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _resolve_workspace_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return workspace_root() / path


def _resolve_relative_path(path_str: str, base_dir: Path) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def load_zomic_design(path: Path) -> ZomicDesignConfig:
    data = load_yaml(path)
    return ZomicDesignConfig.model_validate(data)


def _default_raw_export_path(design: ZomicDesignConfig) -> Path:
    return (
        workspace_root()
        / "data"
        / "prototypes"
        / "generated"
        / f"{design.prototype_key}.raw.json"
    )


def _default_orbit_library_path(design: ZomicDesignConfig) -> Path:
    return workspace_root() / "data" / "prototypes" / "generated" / f"{design.prototype_key}.json"


def _needs_refresh(output_path: Path, inputs: list[Path]) -> bool:
    if not output_path.exists():
        return True
    output_mtime = output_path.stat().st_mtime
    return any(path.stat().st_mtime > output_mtime for path in inputs if path.exists())


def _run_zomic_export(zomic_file: Path, output_path: Path) -> None:
    gradlew = repo_root() / "gradlew"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    java_home = _detect_java_home()
    if java_home is not None:
        env["JAVA_HOME"] = java_home
        env["PATH"] = f"{java_home}/bin:{env.get('PATH', '')}"
    command = [
        str(gradlew),
        "-q",
        ":core:zomicExport",
        f"-PzomicFile={zomic_file}",
        f"-PzomicOut={output_path}",
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root(),
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        detail = stderr or stdout or "unknown error"
        raise RuntimeError(f"Zomic export failed for {zomic_file}: {detail}")


def _infer_orbit_name(label: str) -> str:
    if "." in label:
        prefix, _ = label.split(".", 1)
        return prefix
    if "_" in label:
        prefix, suffix = label.rsplit("_", 1)
        if suffix.isdigit():
            return prefix
    return label


def _cartesian_position(record: dict[str, Any]) -> tuple[float, float, float]:
    raw = record.get("cartesian")
    if not isinstance(raw, list) or len(raw) != 3:
        raise ValueError("zomic export labeled_points entries must define a 3D cartesian list")
    if not all(isinstance(value, (int, float)) for value in raw):
        raise ValueError("zomic export cartesian coordinates must be numeric")
    return (float(raw[0]), float(raw[1]), float(raw[2]))


def _center_cartesian_positions(
    positions: list[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:
    centroid = tuple(
        sum(position[index] for position in positions) / len(positions)
        for index in range(3)
    )
    return [
        (
            position[0] - centroid[0],
            position[1] - centroid[1],
            position[2] - centroid[2],
        )
        for position in positions
    ]


def _embedding_scale(
    raw_fractional_offsets: list[tuple[float, float, float]],
    design: ZomicDesignConfig,
) -> float:
    if design.cartesian_scale is not None:
        return design.cartesian_scale

    max_abs = max(
        max(abs(component) for component in offset)
        for offset in raw_fractional_offsets
    )
    if max_abs <= 1e-9:
        return 1.0

    available = min(
        min(design.motif_center),
        min(1.0 - component for component in design.motif_center),
    )
    if available <= 0.0:
        raise ValueError("motif_center must leave positive space inside the unit cell")
    return round((design.embedding_fraction * available) / max_abs, 6)


def _fractional_positions(
    cartesian_positions: list[tuple[float, float, float]],
    design: ZomicDesignConfig,
) -> tuple[list[tuple[float, float, float]], float]:
    cell_matrix = cell_matrix_from_cell(design.base_cell)
    centered = _center_cartesian_positions(cartesian_positions)
    raw_fractional_offsets = [
        cartesian_to_fractional(position, cell_matrix, wrap=False)
        for position in centered
    ]
    scale = _embedding_scale(raw_fractional_offsets, design)

    positions: list[tuple[float, float, float]] = []
    for offset in raw_fractional_offsets:
        fractional = (
            round(design.motif_center[0] + scale * offset[0], 6),
            round(design.motif_center[1] + scale * offset[1], 6),
            round(design.motif_center[2] + scale * offset[2], 6),
        )
        if any(component < 0.0 or component >= 1.0 for component in fractional):
            raise ValueError(
                "embedded Zomic coordinates fall outside the unit cell; "
                "increase the cell size or reduce embedding_fraction/cartesian_scale"
            )
        positions.append(fractional)
    return positions, scale


def _periodic_axis_delta(first: float, second: float) -> float:
    delta = abs(first - second)
    return min(delta, 1.0 - delta)


def _periodic_distance(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> float:
    dx = _periodic_axis_delta(first[0], second[0])
    dy = _periodic_axis_delta(first[1], second[1])
    dz = _periodic_axis_delta(first[2], second[2])
    return float((dx * dx + dy * dy + dz * dz) ** 0.5)


class _AnchorSite(TypedDict):
    label: str
    orbit: str
    fractional: tuple[float, float, float]


class _AnchorMatch(TypedDict):
    label: str
    orbit: str
    fractional: tuple[float, float, float]
    distance: float


def _anchor_sites(anchor_data: dict[str, Any]) -> list[_AnchorSite]:
    raw_orbits = anchor_data.get("orbits")
    if not isinstance(raw_orbits, list) or not raw_orbits:
        raise ValueError("anchor prototype must contain a non-empty 'orbits' list")

    sites: list[_AnchorSite] = []
    for orbit in raw_orbits:
        if not isinstance(orbit, dict):
            raise ValueError("anchor prototype orbit entries must be objects")
        orbit_name = str(orbit["orbit"])
        raw_sites = orbit.get("sites")
        if not isinstance(raw_sites, list):
            raise ValueError("anchor prototype orbits must define a 'sites' list")
        for site in raw_sites:
            if not isinstance(site, dict):
                raise ValueError("anchor prototype site entries must be objects")
            position = site.get("fractional_position")
            if (
                not isinstance(position, list)
                or len(position) != 3
                or not all(isinstance(value, (int, float)) for value in position)
            ):
                raise ValueError(
                    "anchor prototype sites must define numeric 3D fractional positions"
                )
            sites.append(
                {
                    "label": str(site["label"]),
                    "orbit": orbit_name,
                    "fractional": (
                        round(float(position[0]), 6),
                        round(float(position[1]), 6),
                        round(float(position[2]), 6),
                    ),
                }
            )
    return sites


def _snap_to_anchor_sites(
    fractional_positions: list[tuple[float, float, float]],
    anchor_data: dict[str, Any],
) -> tuple[list[tuple[float, float, float]], list[_AnchorMatch], dict[str, float | int]]:
    anchors = _anchor_sites(anchor_data)
    if len(fractional_positions) > len(anchors):
        raise ValueError("anchor prototype does not contain enough sites for the Zomic export")

    remaining = anchors.copy()
    snapped: list[tuple[float, float, float]] = []
    matches: list[_AnchorMatch] = []
    distances: list[float] = []
    for position in fractional_positions:
        best_index = min(
            range(len(remaining)),
            key=lambda index: (
                _periodic_distance(position, remaining[index]["fractional"]),
                remaining[index]["orbit"],
                remaining[index]["label"],
            ),
        )
        best_site = remaining.pop(best_index)
        distance = _periodic_distance(position, best_site["fractional"])
        distances.append(distance)
        snapped.append(best_site["fractional"])
        matches.append(
            {
                "label": best_site["label"],
                "orbit": best_site["orbit"],
                "fractional": best_site["fractional"],
                "distance": round(distance, 6),
            }
        )

    summary = {
        "assigned_sites": len(matches),
        "mean_distance": round(sum(distances) / len(distances), 6),
        "max_distance": round(max(distances), 6),
    }
    return snapped, matches, summary


class _AnchorOrbitRecord(TypedDict):
    orbit: str
    preferred_species: list[str] | None
    wyckoff: str | None
    sites: list[dict[str, Any]]


class _AnchorOrbitEvidence(TypedDict):
    orbit: str
    votes: int
    size: int
    preferred_species: list[str] | None
    design_votes: dict[str, int]
    wyckoff: str | None


def _anchor_orbit_records(anchor_data: dict[str, Any]) -> dict[str, _AnchorOrbitRecord]:
    raw_orbits = anchor_data.get("orbits")
    if not isinstance(raw_orbits, list) or not raw_orbits:
        raise ValueError("anchor prototype must contain a non-empty 'orbits' list")

    records: dict[str, _AnchorOrbitRecord] = {}
    for orbit in raw_orbits:
        if not isinstance(orbit, dict):
            raise ValueError("anchor prototype orbit entries must be objects")
        orbit_name = str(orbit["orbit"])
        raw_sites = orbit.get("sites")
        if not isinstance(raw_sites, list) or not raw_sites:
            raise ValueError("anchor prototype orbits must define a non-empty 'sites' list")
        preferred_species = orbit.get("preferred_species")
        if preferred_species is not None and not isinstance(preferred_species, list):
            raise ValueError("anchor prototype preferred_species must be a list when provided")
        records[orbit_name] = {
            "orbit": orbit_name,
            "preferred_species": (
                None
                if preferred_species is None
                else [str(species) for species in preferred_species]
            ),
            "wyckoff": None if orbit.get("wyckoff") is None else str(orbit["wyckoff"]),
            "sites": [dict(site) for site in raw_sites if isinstance(site, dict)],
        }
    return records


def _anchor_orbit_evidence(
    unique_sites: list[tuple[str, str, int | None, tuple[float, float, float], list[str]]],
    *,
    anchor_match_by_position: dict[tuple[float, float, float], _AnchorMatch],
    anchor_records: dict[str, _AnchorOrbitRecord],
) -> dict[str, _AnchorOrbitEvidence]:
    evidence: dict[str, _AnchorOrbitEvidence] = {}
    for _, source_label, _, fractional, _ in unique_sites:
        anchor_match = anchor_match_by_position.get(fractional)
        if anchor_match is None:
            continue
        orbit_name = anchor_match["orbit"]
        record = anchor_records[orbit_name]
        entry = evidence.setdefault(
            orbit_name,
            {
                "orbit": orbit_name,
                "votes": 0,
                "size": len(record["sites"]),
                "preferred_species": record["preferred_species"],
                "design_votes": {},
                "wyckoff": record["wyckoff"],
            },
        )
        design_orbit = _infer_orbit_name(source_label)
        entry["votes"] += 1
        entry["design_votes"][design_orbit] = entry["design_votes"].get(design_orbit, 0) + 1
    return evidence


def _select_anchor_orbits(
    evidence_by_orbit: dict[str, _AnchorOrbitEvidence],
    *,
    target: int | None,
    min_votes: int,
) -> list[str]:
    candidates = [
        evidence
        for evidence in evidence_by_orbit.values()
        if evidence["votes"] >= min_votes
    ]
    if not candidates:
        return []

    if target is None:
        ordered = sorted(
            candidates,
            key=lambda item: (-item["votes"], item["size"], item["orbit"]),
        )
        return [item["orbit"] for item in ordered]

    selected: list[str] = []
    covered_species: set[str] = set()
    total_sites = 0
    remaining = candidates.copy()
    while remaining and total_sites < target:
        fit_candidates = [
            item
            for item in remaining
            if total_sites + item["size"] <= target
        ]
        if fit_candidates:
            chosen = max(
                fit_candidates,
                key=lambda item: (
                    int(
                        item["preferred_species"] is not None
                        and any(
                            species not in covered_species
                            for species in item["preferred_species"]
                        )
                    ),
                    item["votes"],
                    -item["size"],
                    item["orbit"],
                ),
            )
        else:
            chosen = min(
                remaining,
                key=lambda item: (
                    total_sites + item["size"] - target,
                    -int(
                        item["preferred_species"] is not None
                        and any(
                            species not in covered_species
                            for species in item["preferred_species"]
                        )
                    ),
                    -item["votes"],
                    item["size"],
                    item["orbit"],
                ),
            )
        selected.append(chosen["orbit"])
        if chosen["preferred_species"] is not None:
            covered_species.update(chosen["preferred_species"])
        total_sites += chosen["size"]
        remaining = [item for item in remaining if item["orbit"] != chosen["orbit"]]
    return selected


def _expanded_anchor_orbits(
    *,
    selected_anchor_orbits: list[str],
    anchor_records: dict[str, _AnchorOrbitRecord],
    evidence_by_orbit: dict[str, _AnchorOrbitEvidence],
    design: ZomicDesignConfig,
) -> list[dict[str, Any]]:
    orbits: list[dict[str, Any]] = []
    for orbit_name in selected_anchor_orbits:
        record = anchor_records[orbit_name]
        evidence = evidence_by_orbit[orbit_name]
        sites: list[dict[str, Any]] = []
        for site in record["sites"]:
            position = site.get("fractional_position")
            if (
                not isinstance(position, list)
                or len(position) != 3
                or not all(isinstance(value, (int, float)) for value in position)
            ):
                raise ValueError("anchor orbit sites must contain numeric fractional_position")
            sites.append(
                {
                    "label": str(site["label"]),
                    "fractional_position": [
                        round(float(position[0]), 6),
                        round(float(position[1]), 6),
                        round(float(position[2]), 6),
                    ],
                }
            )

        dominant_design_orbit = None
        if evidence["design_votes"]:
            dominant_design_orbit = max(
                evidence["design_votes"].items(),
                key=lambda item: (item[1], item[0]),
            )[0]

        preferred_species = record["preferred_species"]
        if preferred_species is None and dominant_design_orbit is not None:
            preferred_species = design.preferred_species_by_orbit.get(dominant_design_orbit)

        orbits.append(
            {
                "orbit": orbit_name,
                "wyckoff": record["wyckoff"],
                "preferred_species": preferred_species,
                "source_design_orbit": dominant_design_orbit,
                "seed_votes": evidence["votes"],
                "seed_design_votes": evidence["design_votes"],
                "sites": sites,
            }
        )
    return orbits


class _DedupedSite(TypedDict):
    label: str
    source_label: str
    occurrence: int | None
    fractional: tuple[float, float, float]
    aliases: list[str]


def _dedupe_fractional_sites(
    labels: list[str],
    source_labels: list[str],
    occurrences: list[int | None],
    fractional_positions: list[tuple[float, float, float]],
) -> list[tuple[str, str, int | None, tuple[float, float, float], list[str]]]:
    unique_by_position: dict[tuple[float, float, float], _DedupedSite] = {}
    for label, source_label, occurrence, fractional in zip(
        labels,
        source_labels,
        occurrences,
        fractional_positions,
        strict=True,
    ):
        key = (
            round(fractional[0], 6),
            round(fractional[1], 6),
            round(fractional[2], 6),
        )
        existing = unique_by_position.get(key)
        if existing is not None:
            aliases = existing["aliases"]
            assert isinstance(aliases, list)
            aliases.append(label)
            continue
        unique_by_position[key] = {
            "label": label,
            "source_label": source_label,
            "occurrence": occurrence,
            "fractional": fractional,
            "aliases": [],
        }
    deduped = []
    for item in unique_by_position.values():
        deduped.append(
            (
                item["label"],
                item["source_label"],
                item["occurrence"],
                item["fractional"],
                item["aliases"],
            )
        )
    return sorted(deduped, key=lambda item: (item[1], item[0]))


def _orbit_library_from_export(
    export_data: dict[str, Any],
    design: ZomicDesignConfig,
    *,
    design_dir: Path,
    raw_export_path: Path,
    zomic_file: Path,
) -> dict[str, Any]:
    raw_points = export_data.get("labeled_points")
    if not isinstance(raw_points, list) or not raw_points:
        raise ValueError("zomic export must contain a non-empty labeled_points list")

    labels: list[str] = []
    source_labels: list[str] = []
    cartesian_positions: list[tuple[float, float, float]] = []
    occurrences: list[int | None] = []
    for point in raw_points:
        if not isinstance(point, dict):
            raise ValueError("zomic export labeled_points entries must be objects")
        label = point.get("label")
        if not isinstance(label, str) or not label:
            raise ValueError("zomic export labeled_points entries must define a label")
        source_label = point.get("source_label")
        if source_label is None:
            source_label = label
        if not isinstance(source_label, str) or not source_label:
            raise ValueError("zomic export labeled_points source_label must be a non-empty string")
        occurrence = point.get("occurrence")
        if occurrence is not None and not isinstance(occurrence, int):
            raise ValueError(
                "zomic export labeled_points occurrence must be an integer when provided"
            )
        labels.append(label)
        source_labels.append(source_label)
        occurrences.append(occurrence)
        cartesian_positions.append(_cartesian_position(point))

    fractional_positions, scale = _fractional_positions(cartesian_positions, design)
    anchor_matches: list[_AnchorMatch] | None = None
    anchor_path: Path | None = None
    anchor_data: dict[str, Any] | None = None
    anchor_alignment: dict[str, float | int] | None = None
    if design.anchor_prototype is not None:
        anchor_path = _resolve_relative_path(design.anchor_prototype, design_dir)
        anchor_data = load_json_object(anchor_path)
        fractional_positions, anchor_matches, anchor_alignment = _snap_to_anchor_sites(
            fractional_positions,
            anchor_data,
        )
    grouped: dict[str, list[dict[str, Any]]] = {}
    unique_sites = _dedupe_fractional_sites(
        labels,
        source_labels,
        occurrences,
        fractional_positions,
    )
    anchor_match_by_position: dict[tuple[float, float, float], _AnchorMatch] = {}
    if anchor_matches is not None:
        for match in anchor_matches:
            anchor_match_by_position[match["fractional"]] = match

    for label, source_label, occurrence, fractional, aliases in unique_sites:
        orbit_name = _infer_orbit_name(source_label)
        site_payload: dict[str, Any] = {
            "label": label,
            "source_label": source_label,
            "occurrence": occurrence,
            "fractional_position": [fractional[0], fractional[1], fractional[2]],
        }
        anchor_match = anchor_match_by_position.get(fractional)
        if anchor_match is not None:
            site_payload["anchor_label"] = anchor_match["label"]
            site_payload["anchor_orbit"] = anchor_match["orbit"]
            site_payload["anchor_distance"] = anchor_match["distance"]
        if aliases:
            site_payload["aliases"] = aliases
        grouped.setdefault(orbit_name, []).append(site_payload)

    orbits: list[dict[str, Any]] = []
    anchor_orbit_summary: dict[str, Any] | None = None
    if (
        anchor_data is not None
        and design.anchor_orbit_strategy == "seed_orbit_expand"
    ):
        anchor_records = _anchor_orbit_records(anchor_data)
        evidence_by_orbit = _anchor_orbit_evidence(
            unique_sites,
            anchor_match_by_position=anchor_match_by_position,
            anchor_records=anchor_records,
        )
        selected_anchor_orbits = _select_anchor_orbits(
            evidence_by_orbit,
            target=design.anchor_site_target,
            min_votes=design.anchor_orbit_min_votes,
        )
        orbits = _expanded_anchor_orbits(
            selected_anchor_orbits=selected_anchor_orbits,
            anchor_records=anchor_records,
            evidence_by_orbit=evidence_by_orbit,
            design=design,
        )
        anchor_orbit_summary = {
            "strategy": design.anchor_orbit_strategy,
            "site_target": design.anchor_site_target,
            "min_votes": design.anchor_orbit_min_votes,
            "selected_orbits": selected_anchor_orbits,
            "selected_site_count": sum(len(orbit["sites"]) for orbit in orbits),
        }
    else:
        for orbit_name in sorted(grouped):
            config = design.orbit_config.get(orbit_name)
            preferred_species = None
            if config is not None and config.preferred_species is not None:
                preferred_species = config.preferred_species
            elif orbit_name in design.preferred_species_by_orbit:
                preferred_species = design.preferred_species_by_orbit[orbit_name]
            orbits.append(
                {
                    "orbit": orbit_name,
                    "wyckoff": None if config is None else config.wyckoff,
                    "preferred_species": preferred_species,
                    "sites": grouped[orbit_name],
                }
            )

    return {
        "prototype_key": design.prototype_key,
        "system_name": design.system_name,
        "template_family": design.template_family,
        "source_kind": (
            "zomic_export_anchor_expanded"
            if anchor_path is not None and design.anchor_orbit_strategy == "seed_orbit_expand"
            else (
                "zomic_export_anchor_fitted"
                if anchor_path is not None
                else "zomic_export"
            )
        ),
        "source_zomic": str(zomic_file),
        "source_raw_export": str(raw_export_path),
        "reference": design.reference,
        "reference_url": design.reference_url,
        "space_group": design.space_group,
        "base_cell": design.base_cell,
        "motif_center": list(design.motif_center),
        "translation_divisor": design.translation_divisor,
        "radial_scale": design.radial_scale,
        "tangential_scale": design.tangential_scale,
        "reference_axes": [list(axis) for axis in design.reference_axes],
        "minimum_site_separation": design.minimum_site_separation,
        "embedding_scale": scale,
        "anchor_prototype": None if anchor_path is None else str(anchor_path),
        "anchor_alignment": anchor_alignment,
        "anchor_orbit_summary": anchor_orbit_summary,
        "anchor_space_group": None if anchor_data is None else anchor_data.get("space_group"),
        "orbits": orbits,
    }


def export_zomic_design(
    design_path: Path,
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> ZomicExportSummary:
    resolved_design_path = design_path.resolve()
    design = load_zomic_design(resolved_design_path)
    design_dir = resolved_design_path.parent

    zomic_file = _resolve_relative_path(design.zomic_file, design_dir)
    raw_export_path = (
        _resolve_relative_path(design.raw_export_path, design_dir)
        if design.raw_export_path
        else _default_raw_export_path(design)
    )
    orbit_library_path = (
        output_path.resolve()
        if output_path is not None
        else (
            _resolve_relative_path(design.export_path, design_dir)
            if design.export_path
            else _default_orbit_library_path(design)
        )
    )

    if force or _needs_refresh(raw_export_path, [resolved_design_path, zomic_file]):
        _run_zomic_export(zomic_file, raw_export_path)

    export_data = load_json_object(raw_export_path)
    orbit_library = _orbit_library_from_export(
        export_data,
        design,
        design_dir=design_dir,
        raw_export_path=raw_export_path,
        zomic_file=zomic_file,
    )
    orbit_inputs = [resolved_design_path, zomic_file, raw_export_path]
    if design.anchor_prototype is not None:
        orbit_inputs.append(_resolve_relative_path(design.anchor_prototype, design_dir))
    if force or _needs_refresh(
        orbit_library_path,
        orbit_inputs,
    ):
        write_json_object(orbit_library, orbit_library_path)

    return ZomicExportSummary(
        design_path=str(resolved_design_path),
        zomic_file=str(zomic_file),
        raw_export_path=str(raw_export_path),
        orbit_library_path=str(orbit_library_path),
        labeled_site_count=sum(len(orbit["sites"]) for orbit in orbit_library["orbits"]),
        orbit_count=len(orbit_library["orbits"]),
    )


def prototype_library_for_config(
    config: SystemConfig,
    *,
    config_path: Path | None = None,
) -> Path | None:
    del config_path
    if config.prototype_library is not None:
        return _resolve_workspace_path(config.prototype_library)

    if config.zomic_design is None:
        return None

    design_path = _resolve_workspace_path(config.zomic_design)
    summary = export_zomic_design(design_path)
    return Path(summary.orbit_library_path)
