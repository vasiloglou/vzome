from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

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


def _orbit_library_from_export(
    export_data: dict[str, Any],
    design: ZomicDesignConfig,
    *,
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
    grouped: dict[str, list[dict[str, Any]]] = {}
    labeled_positions = zip(labels, source_labels, occurrences, fractional_positions, strict=True)
    for label, source_label, occurrence, fractional in sorted(
        labeled_positions,
        key=lambda item: (item[1], item[0]),
    ):
        orbit_name = _infer_orbit_name(source_label)
        grouped.setdefault(orbit_name, []).append(
            {
                "label": label,
                "source_label": source_label,
                "occurrence": occurrence,
                "fractional_position": [fractional[0], fractional[1], fractional[2]],
            }
        )

    orbits: list[dict[str, Any]] = []
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
        "source_kind": "zomic_export",
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
        raw_export_path=raw_export_path,
        zomic_file=zomic_file,
    )
    if force or _needs_refresh(
        orbit_library_path,
        [resolved_design_path, zomic_file, raw_export_path],
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
