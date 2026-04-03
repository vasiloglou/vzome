from __future__ import annotations

import re
from pathlib import Path

from materials_discovery.generator.zomic_bridge import _infer_orbit_name
from materials_discovery.llm.schema import (
    CorpusExample,
    CorpusProvenance,
    CorpusValidationState,
)

_LABEL_RE = re.compile(r"^\s*label\s+([^\s{}]+)", re.MULTILINE)


def extract_zomic_labels(zomic_text: str) -> list[str]:
    labels: list[str] = []
    for match in _LABEL_RE.finditer(zomic_text):
        label = match.group(1).strip()
        if label and label not in labels:
            labels.append(label)
    return labels


def zomic_file_to_corpus_example(
    path: Path,
    *,
    source_family: str,
    system: str | None = None,
) -> CorpusExample:
    zomic_text = path.read_text(encoding="utf-8")
    labels = extract_zomic_labels(zomic_text)
    orbit_names: list[str] = []
    for label in labels:
        orbit = _infer_orbit_name(label)
        if orbit not in orbit_names:
            orbit_names.append(orbit)
    return CorpusExample(
        provenance=CorpusProvenance(
            example_id=f"{source_family}:{path.stem}",
            source_family=source_family,
            source_path=str(path),
            source_record_id=path.stem,
            system=system,
            fidelity_tier="exact",
        ),
        zomic_text=zomic_text if zomic_text.endswith("\n") else zomic_text + "\n",
        labels=labels,
        orbit_names=orbit_names,
        properties={
            "loader_hint": "native_zomic",
            "source_kind": "native_zomic",
        },
        validation=CorpusValidationState(
            parse_status="pending",
            compile_status="pending",
            site_count=len(labels),
        ),
    )
