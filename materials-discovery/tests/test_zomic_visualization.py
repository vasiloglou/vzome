from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from materials_discovery.visualization import (
    build_view_model,
    load_raw_export,
    render_raw_export_html,
    write_raw_export_viewer,
)


def _endpoint(x: float, y: float, z: float) -> dict[str, object]:
    return {
        "components": [
            {"evaluate": x},
            {"evaluate": y},
            {"evaluate": z},
        ]
    }


def _demo_raw_export_payload() -> dict[str, object]:
    return {
        "zomic_file": "designs/zomic/demo.zomic",
        "parser": "antlr4",
        "symmetry": "icosahedral",
        "labeled_points": [
            {
                "label": "core.01",
                "source_label": "core.01",
                "occurrence": 1,
                "cartesian": [0.0, 0.0, 0.0],
            },
            {
                "label": "shell_1",
                "source_label": "shell_1",
                "occurrence": 1,
                "cartesian": [2.0, 0.0, 0.0],
            },
            {
                "label": "shell_2",
                "source_label": "shell_2",
                "occurrence": 2,
                "cartesian": [-2.0, 0.0, 0.0],
            },
        ],
        "segments": [
            {
                "signature": "origin-shell",
                "start": _endpoint(0.0, 0.0, 0.0),
                "end": _endpoint(2.0, 0.0, 0.0),
            }
        ],
    }


def _write_raw_export(
    tmp_path: Path,
    payload: dict[str, object],
    *,
    name: str = "demo.raw.json",
) -> Path:
    raw_export_path = tmp_path / name
    raw_export_path.write_text(json.dumps(payload), encoding="utf-8")
    return raw_export_path


def test_load_raw_export_reads_labeled_points_and_segments(tmp_path: Path) -> None:
    raw_export_path = _write_raw_export(tmp_path, _demo_raw_export_payload())

    raw_export = load_raw_export(raw_export_path)

    assert raw_export.zomic_file == "designs/zomic/demo.zomic"
    assert len(raw_export.labeled_points) == 3
    assert len(raw_export.segments) == 1
    assert raw_export.labeled_points[1].source_label == "shell_1"


def test_build_view_model_preserves_metadata_and_orbit_names(tmp_path: Path) -> None:
    raw_export_path = _write_raw_export(tmp_path, _demo_raw_export_payload())

    view_model = build_view_model(raw_export_path)

    assert view_model.source_zomic == "designs/zomic/demo.zomic"
    assert view_model.symmetry == "icosahedral"
    assert view_model.labeled_point_count == 3
    assert view_model.orbit_count == 2
    assert [point.orbit for point in view_model.points] == ["core", "shell", "shell"]
    assert view_model.points[0].color != view_model.points[1].color


def test_build_view_model_recenters_points_only_geometry(tmp_path: Path) -> None:
    payload = _demo_raw_export_payload()
    payload["segments"] = []
    raw_export_path = _write_raw_export(tmp_path, payload)

    view_model = build_view_model(raw_export_path)
    x_coordinates = [point.coordinates[0] for point in view_model.points]

    assert math.isclose(sum(x_coordinates), 0.0, abs_tol=1e-6)
    assert view_model.segment_count == 0
    assert view_model.bounds_radius > 0.0


def test_build_view_model_dedupes_duplicate_segments(tmp_path: Path) -> None:
    payload = _demo_raw_export_payload()
    payload["segments"] = [
        {
            "signature": "dup",
            "start": _endpoint(0.0, 0.0, 0.0),
            "end": _endpoint(2.0, 0.0, 0.0),
        },
        {
            "signature": "dup",
            "start": _endpoint(0.0, 0.0, 0.0),
            "end": _endpoint(2.0, 0.0, 0.0),
        },
        {
            "start": _endpoint(-2.0, 0.0, 0.0),
            "end": _endpoint(0.0, 0.0, 0.0),
        },
        {
            "start": _endpoint(0.0, 0.0, 0.0),
            "end": _endpoint(-2.0, 0.0, 0.0),
        },
    ]
    raw_export_path = _write_raw_export(tmp_path, payload)

    view_model = build_view_model(raw_export_path)

    assert view_model.segment_count == 2


def test_build_view_model_rejects_malformed_segment_coordinates(tmp_path: Path) -> None:
    payload = _demo_raw_export_payload()
    payload["segments"] = [
        {
            "signature": "broken-segment",
            "start": _endpoint(0.0, 0.0, 0.0),
            "end": {"components": [{"evaluate": 1.0}, {"evaluate": 2.0}]},
        }
    ]
    raw_export_path = _write_raw_export(tmp_path, payload)

    with pytest.raises(ValueError, match="broken-segment"):
        build_view_model(raw_export_path)


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[1] / "data/prototypes/generated/sc_zn_tsai_bridge.raw.json").exists(),
    reason="checked Sc-Zn raw export not present",
)
def test_build_view_model_smoke_tests_checked_sc_zn_raw_export() -> None:
    raw_export_path = (
        Path(__file__).resolve().parents[1]
        / "data/prototypes/generated/sc_zn_tsai_bridge.raw.json"
    )

    view_model = build_view_model(raw_export_path)

    assert view_model.labeled_point_count == 52
    assert view_model.segment_count == 52
    assert view_model.bounds_radius > 0.0


def test_render_raw_export_html_contains_canvas_and_metadata(tmp_path: Path) -> None:
    raw_export_path = _write_raw_export(tmp_path, _demo_raw_export_payload())
    view_model = build_view_model(raw_export_path)

    html_text = render_raw_export_html(view_model, show_labels=True)

    assert 'canvas id="zomic-viewer"' in html_text
    assert "const VIEW_MODEL =" in html_text
    assert 'button id="toggle-labels"' in html_text
    assert 'button id="reset-view"' in html_text
    assert "designs/zomic/demo.zomic" in html_text
    assert "demo.zomic" in html_text
    assert "icosahedral" in html_text
    assert "true" in html_text


def test_write_raw_export_viewer_writes_html_file(tmp_path: Path) -> None:
    raw_export_path = _write_raw_export(tmp_path, _demo_raw_export_payload())

    viewer_path = write_raw_export_viewer(raw_export_path)

    assert viewer_path.exists()
    assert viewer_path.name == "demo.viewer.html"
    assert "demo.zomic" in viewer_path.read_text(encoding="utf-8")
