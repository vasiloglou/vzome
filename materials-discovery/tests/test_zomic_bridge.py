from __future__ import annotations

import json
from pathlib import Path

import yaml
from pytest import MonkeyPatch

from materials_discovery.common.schema import SystemConfig
from materials_discovery.generator.candidate_factory import generate_candidates
from materials_discovery.generator.zomic_bridge import export_zomic_design


def _write_design(tmp_path: Path, extra_config: dict[str, object] | None = None) -> Path:
    design_dir = tmp_path / "designs"
    design_dir.mkdir()
    zomic_path = design_dir / "demo.zomic"
    zomic_path.write_text("label core.01\nlabel shell.01\nlabel shell.02\n", encoding="utf-8")

    design_path = design_dir / "demo.yaml"
    payload: dict[str, object] = {
        "zomic_file": "demo.zomic",
        "prototype_key": "demo_zomic",
        "system_name": "Sc-Zn",
        "template_family": "cubic_proxy_1_0",
        "reference": "demo",
        "base_cell": {
            "a": 10.0,
            "b": 10.0,
            "c": 10.0,
            "alpha": 90.0,
            "beta": 90.0,
            "gamma": 90.0,
        },
        "motif_center": [0.5, 0.5, 0.5],
        "translation_divisor": 6.0,
        "radial_scale": 0.018,
        "tangential_scale": 0.04,
        "reference_axes": [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        "minimum_site_separation": 0.08,
        "preferred_species_by_orbit": {
            "core": ["Sc"],
            "shell": ["Zn", "Sc"],
        },
        "export_path": "generated/demo_zomic.json",
        "raw_export_path": "generated/demo_zomic.raw.json",
    }
    if extra_config is not None:
        payload.update(extra_config)
    design_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    return design_path


def _fake_export_payload() -> dict[str, object]:
    return {
        "zomic_file": "demo.zomic",
        "parser": "antlr4",
        "symmetry": "icosahedral",
        "labeled_points": [
            {"label": "core.01", "cartesian": [0.0, 0.0, 0.0]},
            {"label": "shell.01", "cartesian": [1.0, 0.0, 0.0]},
            {"label": "shell.02", "cartesian": [-1.0, 0.0, 0.0]},
        ],
        "segments": [],
    }


def _fake_duplicate_label_export_payload() -> dict[str, object]:
    return {
        "zomic_file": "demo.zomic",
        "parser": "antlr4",
        "symmetry": "icosahedral",
        "labeled_points": [
            {
                "label": "shell.outer",
                "source_label": "shell.outer",
                "occurrence": 1,
                "cartesian": [1.0, 0.0, 0.0],
            },
            {
                "label": "shell.outer#2",
                "source_label": "shell.outer",
                "occurrence": 2,
                "cartesian": [-1.0, 0.0, 0.0],
            },
        ],
        "segments": [],
    }


def _fake_coincident_label_export_payload() -> dict[str, object]:
    return {
        "zomic_file": "demo.zomic",
        "parser": "antlr4",
        "symmetry": "icosahedral",
        "labeled_points": [
            {
                "label": "shell.outer",
                "source_label": "shell.outer",
                "occurrence": 1,
                "cartesian": [1.0, 0.0, 0.0],
            },
            {
                "label": "shell.outer#2",
                "source_label": "shell.outer",
                "occurrence": 2,
                "cartesian": [1.0, 0.0, 0.0],
            },
        ],
        "segments": [],
    }


def test_export_zomic_design_groups_labeled_sites_into_orbits(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    design_path = _write_design(tmp_path)

    def fake_run_zomic_export(zomic_file: Path, output_path: Path) -> None:
        del zomic_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(_fake_export_payload()), encoding="utf-8")

    monkeypatch.setattr(
        "materials_discovery.generator.zomic_bridge._run_zomic_export",
        fake_run_zomic_export,
    )

    summary = export_zomic_design(design_path, force=True)
    orbit_library = json.loads(Path(summary.orbit_library_path).read_text(encoding="utf-8"))

    assert summary.labeled_site_count == 3
    assert summary.orbit_count == 2
    assert orbit_library["source_kind"] == "zomic_export"
    assert orbit_library["prototype_key"] == "demo_zomic"
    assert [orbit["orbit"] for orbit in orbit_library["orbits"]] == ["core", "shell"]
    assert orbit_library["orbits"][0]["preferred_species"] == ["Sc"]
    assert len(orbit_library["orbits"][1]["sites"]) == 2


def test_export_zomic_design_accepts_repeated_source_labels(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    design_path = _write_design(tmp_path)

    def fake_run_zomic_export(zomic_file: Path, output_path: Path) -> None:
        del zomic_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(_fake_duplicate_label_export_payload()),
            encoding="utf-8",
        )

    monkeypatch.setattr(
        "materials_discovery.generator.zomic_bridge._run_zomic_export",
        fake_run_zomic_export,
    )

    summary = export_zomic_design(design_path, force=True)
    orbit_library = json.loads(Path(summary.orbit_library_path).read_text(encoding="utf-8"))

    assert summary.labeled_site_count == 2
    assert [orbit["orbit"] for orbit in orbit_library["orbits"]] == ["shell"]
    assert [site["label"] for site in orbit_library["orbits"][0]["sites"]] == [
        "shell.outer",
        "shell.outer#2",
    ]
    assert [site["source_label"] for site in orbit_library["orbits"][0]["sites"]] == [
        "shell.outer",
        "shell.outer",
    ]


def test_export_zomic_design_dedupes_coincident_sites(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    design_path = _write_design(tmp_path)

    def fake_run_zomic_export(zomic_file: Path, output_path: Path) -> None:
        del zomic_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(_fake_coincident_label_export_payload()),
            encoding="utf-8",
        )

    monkeypatch.setattr(
        "materials_discovery.generator.zomic_bridge._run_zomic_export",
        fake_run_zomic_export,
    )

    summary = export_zomic_design(design_path, force=True)
    orbit_library = json.loads(Path(summary.orbit_library_path).read_text(encoding="utf-8"))

    assert summary.labeled_site_count == 1
    sites = orbit_library["orbits"][0]["sites"]
    assert len(sites) == 1
    assert sites[0]["label"] == "shell.outer"
    assert sites[0]["aliases"] == ["shell.outer#2"]


def test_export_zomic_design_can_snap_to_anchor_prototype(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    anchor_path = tmp_path / "anchor.json"
    anchor_path.write_text(
        json.dumps(
            {
                "prototype_key": "anchor_demo",
                "space_group": "I m -3",
                "orbits": [
                    {
                        "orbit": "anchor_shell",
                        "sites": [
                            {"label": "A1", "fractional_position": [0.5, 0.5, 0.5]},
                            {"label": "A2", "fractional_position": [0.6, 0.5, 0.5]},
                            {"label": "A3", "fractional_position": [0.4, 0.5, 0.5]},
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    design_path = _write_design(
        tmp_path,
        extra_config={"anchor_prototype": str(anchor_path)},
    )

    def fake_run_zomic_export(zomic_file: Path, output_path: Path) -> None:
        del zomic_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(_fake_export_payload()), encoding="utf-8")

    monkeypatch.setattr(
        "materials_discovery.generator.zomic_bridge._run_zomic_export",
        fake_run_zomic_export,
    )

    summary = export_zomic_design(design_path, force=True)
    orbit_library = json.loads(Path(summary.orbit_library_path).read_text(encoding="utf-8"))

    positions = []
    anchor_labels = []
    for orbit in orbit_library["orbits"]:
        for site in orbit["sites"]:
            positions.append(site["fractional_position"])
            anchor_labels.append(site["anchor_label"])

    assert orbit_library["source_kind"] == "zomic_export_anchor_fitted"
    assert orbit_library["anchor_prototype"] == str(anchor_path)
    assert orbit_library["anchor_alignment"]["assigned_sites"] == 3
    assert sorted(positions) == [[0.4, 0.5, 0.5], [0.5, 0.5, 0.5], [0.6, 0.5, 0.5]]
    assert sorted(anchor_labels) == ["A1", "A2", "A3"]


def test_generate_candidates_can_use_zomic_design_override(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    design_path = _write_design(tmp_path)

    def fake_run_zomic_export(zomic_file: Path, output_path: Path) -> None:
        del zomic_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(_fake_export_payload()), encoding="utf-8")

    monkeypatch.setattr(
        "materials_discovery.generator.zomic_bridge._run_zomic_export",
        fake_run_zomic_export,
    )

    config = SystemConfig.model_validate(
        {
            "system_name": "Sc-Zn",
            "template_family": "cubic_proxy_1_0",
            "species": ["Sc", "Zn"],
            "composition_bounds": {
                "Sc": {"min": 0.2, "max": 0.4},
                "Zn": {"min": 0.6, "max": 0.8},
            },
            "coeff_bounds": {"min": -2, "max": 2},
            "seed": 11,
            "default_count": 8,
            "zomic_design": str(design_path),
        }
    )

    out_path = tmp_path / "generated.jsonl"
    generate_candidates(config, out_path, count=1, seed=11)
    rows = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines()]

    assert len(rows) == 1
    candidate = rows[0]
    provenance = candidate["provenance"]
    assert provenance["prototype_key"] == "demo_zomic"
    assert provenance["prototype_source_kind"] == "zomic_export"
    assert provenance["zomic_design"] == str(design_path)
    assert provenance["prototype_library_path"].endswith("demo_zomic.json")
    assert len(candidate["sites"]) == 3
