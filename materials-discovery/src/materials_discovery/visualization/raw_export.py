from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from materials_discovery.common.io import load_json_object
from materials_discovery.generator.zomic_bridge import _infer_orbit_name

_ORBIT_PALETTE = (
    "#2563eb",
    "#ca8a04",
    "#dc2626",
    "#16a34a",
    "#ea580c",
    "#7c3aed",
    "#0f766e",
    "#db2777",
)
_DEFAULT_SEGMENT_COLOR = "#6b7280"
_PRECISION = 6


class ZomicRawCoordinateComponent(BaseModel):
    expression: str | None = None
    zomic_expression: str | None = None
    trailing_divisor: tuple[str, str, str] | None = None
    evaluate: float


class ZomicRawSegmentEndpoint(BaseModel):
    expression: str | None = None
    zomic_expression: str | None = None
    components: list[ZomicRawCoordinateComponent] = Field(default_factory=list)


class ZomicRawPoint(BaseModel):
    label: str
    source_label: str | None = None
    occurrence: int | None = None
    cartesian: tuple[float, float, float]


class ZomicRawSegment(BaseModel):
    signature: str | None = None
    start: ZomicRawSegmentEndpoint
    end: ZomicRawSegmentEndpoint


class ZomicRawExport(BaseModel):
    zomic_file: str | None = None
    parser: str | None = None
    symmetry: str | None = None
    labeled_points: list[ZomicRawPoint] = Field(default_factory=list)
    segments: list[ZomicRawSegment] = Field(default_factory=list)


class ZomicViewPoint(BaseModel):
    label: str
    source_label: str
    orbit: str
    color: str
    coordinates: tuple[float, float, float]


class ZomicViewSegment(BaseModel):
    signature: str | None = None
    orbit: str | None = None
    color: str
    start: tuple[float, float, float]
    end: tuple[float, float, float]


class RawExportViewModel(BaseModel):
    source_zomic: str | None = None
    symmetry: str | None = None
    parser: str | None = None
    labeled_point_count: int
    segment_count: int
    orbit_count: int
    bounds_radius: float
    centroid: tuple[float, float, float]
    points: list[ZomicViewPoint] = Field(default_factory=list)
    segments: list[ZomicViewSegment] = Field(default_factory=list)


def load_raw_export(path: Path) -> ZomicRawExport:
    resolved_path = path.resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"raw export file not found: {resolved_path}")
    return ZomicRawExport.model_validate(load_json_object(resolved_path))


def _round_scalar(value: float) -> float:
    return round(float(value), _PRECISION)


def _round_coordinates(values: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(_round_scalar(value) for value in values)  # type: ignore[return-value]


def _coordinate_key(values: tuple[float, float, float]) -> tuple[float, float, float]:
    return _round_coordinates(values)


def _extract_endpoint_coordinates(
    endpoint: ZomicRawSegmentEndpoint,
    *,
    signature: str | None,
) -> tuple[float, float, float]:
    if len(endpoint.components) != 3:
        raise ValueError(
            f"segment {signature or '<unknown>'!r} must define exactly three endpoint coordinates"
        )
    values: list[float] = []
    for component in endpoint.components:
        value = component.evaluate
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"segment {signature or '<unknown>'!r} must define numeric endpoint coordinates"
            )
        values.append(float(value))
    return (values[0], values[1], values[2])


def _centroid(points: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    if not points:
        return (0.0, 0.0, 0.0)
    count = float(len(points))
    return (
        sum(point[0] for point in points) / count,
        sum(point[1] for point in points) / count,
        sum(point[2] for point in points) / count,
    )


def _normalize_coordinates(
    values: tuple[float, float, float],
    centroid: tuple[float, float, float],
) -> tuple[float, float, float]:
    return _round_coordinates(
        (
            values[0] - centroid[0],
            values[1] - centroid[1],
            values[2] - centroid[2],
        )
    )


def _segment_orbit(
    start_key: tuple[float, float, float],
    end_key: tuple[float, float, float],
    point_orbits_by_coordinate: dict[tuple[float, float, float], str],
) -> str | None:
    start_orbit = point_orbits_by_coordinate.get(start_key)
    end_orbit = point_orbits_by_coordinate.get(end_key)
    if start_orbit and end_orbit and start_orbit == end_orbit:
        return start_orbit
    return start_orbit or end_orbit


def _segment_dedupe_key(
    signature: str | None,
    start_key: tuple[float, float, float],
    end_key: tuple[float, float, float],
) -> Any:
    if signature:
        return signature
    return tuple(sorted((start_key, end_key)))


def build_view_model(path_or_export: Path | ZomicRawExport) -> RawExportViewModel:
    raw_export = (
        load_raw_export(path_or_export)
        if isinstance(path_or_export, Path)
        else path_or_export
    )

    raw_point_coordinates = [
        tuple(float(component) for component in point.cartesian)
        for point in raw_export.labeled_points
    ]
    raw_segment_coordinates: list[tuple[tuple[float, float, float], tuple[float, float, float], str | None]] = []
    for segment in raw_export.segments:
        start = _extract_endpoint_coordinates(segment.start, signature=segment.signature)
        end = _extract_endpoint_coordinates(segment.end, signature=segment.signature)
        raw_segment_coordinates.append((start, end, segment.signature))

    centroid_source = raw_point_coordinates or [
        coordinate
        for start, end, _ in raw_segment_coordinates
        for coordinate in (start, end)
    ]
    centroid = _centroid(centroid_source)

    orbit_colors: dict[str, str] = {}
    point_orbits_by_coordinate: dict[tuple[float, float, float], str] = {}
    points: list[ZomicViewPoint] = []
    for point, raw_coordinates in zip(raw_export.labeled_points, raw_point_coordinates, strict=True):
        source_label = point.source_label or point.label
        orbit = _infer_orbit_name(source_label)
        if orbit not in orbit_colors:
            orbit_colors[orbit] = _ORBIT_PALETTE[len(orbit_colors) % len(_ORBIT_PALETTE)]
        point_orbits_by_coordinate[_coordinate_key(raw_coordinates)] = orbit
        points.append(
            ZomicViewPoint(
                label=point.label,
                source_label=source_label,
                orbit=orbit,
                color=orbit_colors[orbit],
                coordinates=_normalize_coordinates(raw_coordinates, centroid),
            )
        )

    segments: list[ZomicViewSegment] = []
    seen_segments: set[Any] = set()
    for start, end, signature in raw_segment_coordinates:
        start_key = _coordinate_key(start)
        end_key = _coordinate_key(end)
        dedupe_key = _segment_dedupe_key(signature, start_key, end_key)
        if dedupe_key in seen_segments:
            continue
        seen_segments.add(dedupe_key)
        orbit = _segment_orbit(start_key, end_key, point_orbits_by_coordinate)
        color = orbit_colors.get(orbit, _DEFAULT_SEGMENT_COLOR)
        segments.append(
            ZomicViewSegment(
                signature=signature,
                orbit=orbit,
                color=color,
                start=_normalize_coordinates(start, centroid),
                end=_normalize_coordinates(end, centroid),
            )
        )

    geometry_points = [point.coordinates for point in points]
    geometry_points.extend(segment.start for segment in segments)
    geometry_points.extend(segment.end for segment in segments)
    bounds_radius = max(
        (
            math.sqrt(
                (coordinates[0] ** 2)
                + (coordinates[1] ** 2)
                + (coordinates[2] ** 2)
            )
            for coordinates in geometry_points
        ),
        default=0.0,
    )
    if bounds_radius <= 0.0:
        bounds_radius = 1.0

    return RawExportViewModel(
        source_zomic=raw_export.zomic_file,
        symmetry=raw_export.symmetry,
        parser=raw_export.parser,
        labeled_point_count=len(points),
        segment_count=len(segments),
        orbit_count=len(orbit_colors),
        bounds_radius=_round_scalar(bounds_radius),
        centroid=_round_coordinates(centroid),
        points=points,
        segments=segments,
    )
