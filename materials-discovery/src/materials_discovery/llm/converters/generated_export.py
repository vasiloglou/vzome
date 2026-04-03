from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import load_json_object
from materials_discovery.generator.zomic_bridge import _infer_orbit_name
from materials_discovery.llm.schema import (
    CorpusExample,
    CorpusProvenance,
    CorpusValidationState,
)


def _generated_record_id(path: Path) -> str:
    return path.name[: -len(".raw.json")] if path.name.endswith(".raw.json") else path.stem


def generated_export_to_corpus_examples(path: Path) -> list[CorpusExample]:
    payload = load_json_object(path)
    labels = [
        str(point.get("source_label") or point.get("label"))
        for point in payload.get("labeled_points", [])
        if isinstance(point, dict)
    ]
    orbit_names: list[str] = []
    for label in labels:
        orbit = _infer_orbit_name(label)
        if orbit not in orbit_names:
            orbit_names.append(orbit)

    record_id = _generated_record_id(path)
    zomic_file = payload.get("zomic_file")
    zomic_path = Path(zomic_file) if isinstance(zomic_file, str) else None
    if zomic_path is not None and zomic_path.exists():
        zomic_text = zomic_path.read_text(encoding="utf-8")
        fidelity_tier = "exact"
    else:
        lines = [f"// generated_export={record_id}", "branch {"]
        for index, label in enumerate(labels, start=1):
            lines.append(f"  branch {{ size {index} blue +0")
            lines.append(f"    label {label}")
            lines.append("  }")
        lines.append("}")
        zomic_text = "\n".join(lines) + "\n"
        fidelity_tier = "anchored"

    example = CorpusExample(
        provenance=CorpusProvenance(
            example_id=f"generated_export:{record_id}",
            source_family="generated_export",
            source_path=str(path),
            source_record_id=record_id,
            system=None,
            fidelity_tier=fidelity_tier,
        ),
        zomic_text=zomic_text,
        labels=labels,
        orbit_names=orbit_names,
        properties={
            "loader_hint": "generated_export",
            "parser": payload.get("parser"),
            "symmetry": payload.get("symmetry"),
            "zomic_design": zomic_file,
        },
        validation=CorpusValidationState(
            parse_status="pending",
            compile_status="pending",
            site_count=len(labels),
        ),
    )
    return [example]
