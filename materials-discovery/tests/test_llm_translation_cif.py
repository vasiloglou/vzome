from __future__ import annotations

import json
from pathlib import Path

from materials_discovery.common.schema import CandidateRecord
from materials_discovery.generator.prototype_import import parse_cif
from materials_discovery.llm import emit_cif_text, prepare_translated_structure, resolve_translation_target

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_translation"
_CELL_FIELDS = [
    "_cell_length_a",
    "_cell_length_b",
    "_cell_length_c",
    "_cell_angle_alpha",
    "_cell_angle_beta",
    "_cell_angle_gamma",
]
_ATOM_HEADERS = [
    "_atom_site_label",
    "_atom_site_type_symbol",
    "_atom_site_fract_x",
    "_atom_site_fract_y",
    "_atom_site_fract_z",
    "_atom_site_occupancy",
]


def _load_candidate_fixture(name: str) -> CandidateRecord:
    fixture_path = FIXTURE_DIR / name
    return CandidateRecord.model_validate(json.loads(fixture_path.read_text()))


def _artifact(name: str):
    candidate = _load_candidate_fixture(name)
    return prepare_translated_structure(candidate, resolve_translation_target("cif"))


def _expected_preamble_lines(artifact) -> list[str]:
    loss_reasons = ",".join(artifact.loss_reasons) if artifact.loss_reasons else "none"
    system = artifact.source.system or "none"
    return [
        f"# source_candidate_id={artifact.source.candidate_id}",
        f"# system={system}",
        "# target_family=cif",
        f"# fidelity_tier={artifact.fidelity_tier}",
        f"# loss_reasons={loss_reasons}",
    ]


def _write_comment_stripped_cif(tmp_path: Path, text: str) -> Path:
    cif_path = tmp_path / "emitted.cif"
    stripped = "\n".join(line for line in text.splitlines() if not line.startswith("# "))
    cif_path.write_text(stripped + "\n", encoding="utf-8")
    return cif_path


def test_emit_cif_text_starts_with_deterministic_comment_preamble() -> None:
    artifact = _artifact("al_cu_fe_periodic_candidate.json")

    emitted = emit_cif_text(artifact)

    assert emitted.splitlines()[:5] == _expected_preamble_lines(artifact)


def test_emit_cif_text_has_one_data_block_and_fixed_cell_scalar_order() -> None:
    artifact = _artifact("al_cu_fe_periodic_candidate.json")

    lines = emit_cif_text(artifact).splitlines()

    assert len([line for line in lines if line.startswith("data_")]) == 1
    assert [line.split()[0] for line in lines if line.startswith("_cell_")] == _CELL_FIELDS


def test_emit_cif_text_has_one_atom_site_loop_with_expected_headers() -> None:
    artifact = _artifact("al_cu_fe_periodic_candidate.json")

    lines = emit_cif_text(artifact).splitlines()
    loop_index = lines.index("loop_")

    assert lines[loop_index + 1 : loop_index + 7] == _ATOM_HEADERS


def test_emit_cif_text_preserves_translated_site_order() -> None:
    artifact = _artifact("al_cu_fe_periodic_candidate.json")
    emitted = emit_cif_text(artifact)

    atom_rows = [
        line.split()[0]
        for line in emitted.splitlines()
        if line and not line.startswith("#") and not line.startswith("data_") and not line.startswith("_")
    ]

    assert atom_rows == [site.label for site in artifact.sites]


def test_parse_cif_can_read_emitted_payload_after_comments_are_stripped(tmp_path: Path) -> None:
    artifact = _artifact("al_cu_fe_periodic_candidate.json")

    cif = parse_cif(_write_comment_stripped_cif(tmp_path, emit_cif_text(artifact)))
    atom_loop = next(loop for loop in cif["loops"] if "_atom_site_label" in loop["headers"])

    assert cif["values"]["_cell_length_a"] == artifact.cell["a"]
    assert [row["_atom_site_label"] for row in atom_loop["rows"]] == [
        site.label for site in artifact.sites
    ]


def test_lossy_qc_native_cif_export_keeps_periodic_proxy_metadata_visible() -> None:
    artifact = _artifact("sc_zn_qc_candidate.json")

    emitted = emit_cif_text(artifact)

    assert emitted.splitlines()[:5] == _expected_preamble_lines(artifact)
    assert "# fidelity_tier=lossy" in emitted
    assert "# loss_reasons=aperiodic_to_periodic_proxy,coordinate_derivation_required,qc_semantics_dropped" in emitted
