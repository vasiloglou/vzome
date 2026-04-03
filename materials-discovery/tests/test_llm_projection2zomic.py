from __future__ import annotations

from pathlib import Path

import yaml

from materials_discovery.common.io import load_json_object
from materials_discovery.common.schema import QPhiCoord
from materials_discovery.common.schema import ZomicExportSummary
from materials_discovery.llm.compiler import compile_zomic_script
from materials_discovery.llm.converters.projection2zomic import projection_payload_to_zomic


def _fixture_payload() -> dict[str, object]:
    fixture_path = (
        Path(__file__).resolve().parent / "fixtures" / "pyqcstrc_projection_sample.json"
    )
    return load_json_object(fixture_path)


def test_compile_zomic_script_writes_temp_inputs_and_uses_bridge_authority(monkeypatch) -> None:
    observed: dict[str, object] = {}

    def _fake_export(design_path: Path, *, force: bool = False) -> ZomicExportSummary:
        observed["force"] = force
        observed["design_path"] = design_path
        design_payload = yaml.safe_load(design_path.read_text(encoding="utf-8"))
        observed["zomic_exists"] = Path(design_payload["zomic_file"]).exists()
        observed["design_payload"] = design_payload
        raw_export = Path(design_payload["raw_export_path"])
        raw_export.write_text("{}", encoding="utf-8")
        orbit_library = Path(design_payload["export_path"])
        orbit_library.write_text("{}", encoding="utf-8")
        return ZomicExportSummary(
            design_path=str(design_path),
            zomic_file=str(design_payload["zomic_file"]),
            raw_export_path=str(raw_export),
            orbit_library_path=str(orbit_library),
            labeled_site_count=2,
            orbit_count=1,
        )

    monkeypatch.setattr("materials_discovery.llm.compiler.export_zomic_design", _fake_export)

    result = compile_zomic_script(
        "label shell.01\nbranch { label shell.02 }\n",
        prototype_key="demo_prototype",
        system_name="Sc-Zn",
        template_family="icosahedral_approximant_1_1",
    )

    assert observed["force"] is True
    assert observed["zomic_exists"] is True
    assert result["parse_status"] == "passed"
    assert result["compile_status"] == "passed"
    assert result["raw_export_path"]


def test_projection_payload_to_zomic_accepts_committed_fixture_payload() -> None:
    example = projection_payload_to_zomic(_fixture_payload())

    assert example.zomic_text
    assert example.labels == ["shell.01", "shell.02"]


def test_projection_conversion_uses_pyqcstrc_source_family() -> None:
    example = projection_payload_to_zomic(_fixture_payload())

    assert example.provenance.source_family == "pyqcstrc_projection"
    assert example.provenance.source_record_id == "ico_demo_v1"


def test_projection_conversion_preserves_composition_metadata_and_source_model_id() -> None:
    example = projection_payload_to_zomic(_fixture_payload())

    assert example.composition == {"Al": 0.7, "Cu": 0.2, "Fe": 0.1}
    assert example.properties["source_model_id"] == "ico_demo_v1"
    assert example.properties["coordinate_system"] == "qphi"


def test_compile_failures_surface_in_validation_metadata(monkeypatch) -> None:
    def _failing_export(design_path: Path, *, force: bool = False) -> ZomicExportSummary:
        del design_path, force
        raise RuntimeError("synthetic compile failure")

    monkeypatch.setattr("materials_discovery.llm.compiler.export_zomic_design", _failing_export)

    result = compile_zomic_script(
        "label shell.01\n",
        prototype_key="demo_prototype",
        system_name="Sc-Zn",
        template_family="icosahedral_approximant_1_1",
    )

    assert result["parse_status"] == "failed"
    assert result["compile_status"] == "failed"
    assert result["error_message"] == "synthetic compile failure"


def test_large_qphi_magnitudes_scale_temporary_cell_deterministically(monkeypatch) -> None:
    observed_scales: list[float] = []

    def _fake_export(design_path: Path, *, force: bool = False) -> ZomicExportSummary:
        del force
        design_payload = yaml.safe_load(design_path.read_text(encoding="utf-8"))
        observed_scales.append(float(design_payload["base_cell"]["a"]))
        raw_export = Path(design_payload["raw_export_path"])
        raw_export.write_text("{}", encoding="utf-8")
        orbit_library = Path(design_payload["export_path"])
        orbit_library.write_text("{}", encoding="utf-8")
        return ZomicExportSummary(
            design_path=str(design_path),
            zomic_file=str(design_payload["zomic_file"]),
            raw_export_path=str(raw_export),
            orbit_library_path=str(orbit_library),
            labeled_site_count=0,
            orbit_count=0,
        )

    monkeypatch.setattr("materials_discovery.llm.compiler.export_zomic_design", _fake_export)
    bounds: list[QPhiCoord] = [((10, 0), (8, 0), (6, 0))]

    first = compile_zomic_script(
        "label shell.01\n",
        prototype_key="scaled_demo",
        system_name="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        source_qphi_bounds=bounds,
    )
    second = compile_zomic_script(
        "label shell.01\n",
        prototype_key="scaled_demo",
        system_name="Al-Cu-Fe",
        template_family="icosahedral_approximant_1_1",
        source_qphi_bounds=bounds,
    )

    assert observed_scales[0] == observed_scales[1]
    assert first["cell_scale_used"] == second["cell_scale_used"]
    assert first["cell_scale_used"] > 10.0
