from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import yaml

from materials_discovery.common.coordinates import qphi_coord_to_float
from materials_discovery.common.schema import QPhiCoord
from materials_discovery.generator.zomic_bridge import export_zomic_design


def _cell_scale_from_bounds(source_qphi_bounds: list[QPhiCoord] | None) -> float:
    if not source_qphi_bounds:
        return 10.0
    max_abs = max(
        abs(component)
        for coord in source_qphi_bounds
        for component in qphi_coord_to_float(coord)
    )
    return round(max(10.0, 2.0 * max_abs + 2.0), 6)


def compile_zomic_script(
    zomic_text: str,
    *,
    prototype_key: str,
    system_name: str,
    template_family: str,
    source_qphi_bounds: list[QPhiCoord] | None = None,
) -> dict[str, Any]:
    cell_scale = _cell_scale_from_bounds(source_qphi_bounds)
    with TemporaryDirectory(prefix="mdisc-llm-compile-") as temp_dir:
        temp_root = Path(temp_dir)
        zomic_path = temp_root / f"{prototype_key}.zomic"
        design_path = temp_root / f"{prototype_key}.yaml"
        raw_export_path = temp_root / f"{prototype_key}.raw.json"
        orbit_library_path = temp_root / f"{prototype_key}.json"
        zomic_path.write_text(zomic_text, encoding="utf-8")

        design_payload = {
            "zomic_file": str(zomic_path),
            "prototype_key": prototype_key,
            "system_name": system_name,
            "template_family": template_family,
            "base_cell": {
                "a": cell_scale,
                "b": cell_scale,
                "c": cell_scale,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            "reference": "Phase 6 temporary compile validation",
            "motif_center": [0.5, 0.5, 0.5],
            "translation_divisor": 10.0,
            "radial_scale": 0.01,
            "tangential_scale": 0.02,
            "reference_axes": [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            "minimum_site_separation": 0.1,
            "raw_export_path": str(raw_export_path),
            "export_path": str(orbit_library_path),
        }
        design_path.write_text(yaml.safe_dump(design_payload, sort_keys=True), encoding="utf-8")

        try:
            summary = export_zomic_design(design_path, force=True)
        except Exception as exc:  # pragma: no cover - exercised via monkeypatching
            return {
                "parse_status": "failed",
                "compile_status": "failed",
                "raw_export_path": None,
                "cell_scale_used": cell_scale,
                "geometry_equivalence": None,
                "geometry_error": None,
                "error_message": str(exc),
            }

        return {
            "parse_status": "passed",
            "compile_status": "passed",
            "raw_export_path": str(summary.raw_export_path),
            "cell_scale_used": cell_scale,
            "geometry_equivalence": None,
            "geometry_error": None,
            "error_message": None,
        }
