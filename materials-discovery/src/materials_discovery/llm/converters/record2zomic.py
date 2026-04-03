from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Any

from materials_discovery.common.schema import CandidateRecord, QPhiCoord, SiteRecord
from materials_discovery.generator.zomic_bridge import _infer_orbit_name
from materials_discovery.llm.converters.axis_walk import decompose_qphi_to_axis_walk
from materials_discovery.llm.schema import (
    CorpusConversionTrace,
    CorpusExample,
    CorpusProvenance,
    CorpusValidationState,
)

_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_label(label: str) -> str:
    cleaned = _SANITIZE_RE.sub("_", label.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "site"


def _qphi_sort_key(coord: QPhiCoord) -> tuple[int, ...]:
    return tuple(value for pair in coord for value in pair)


def _source_signature(record: CandidateRecord) -> str:
    payload = "|".join(
        f"{site.label}:{','.join(str(value) for value in _qphi_sort_key(site.qphi))}"
        for site in sorted(record.sites, key=lambda site: (site.label, _qphi_sort_key(site.qphi)))
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{record.candidate_id}:{digest}"


def _summarize_strategy(strategies: list[str]) -> str:
    if "heuristic_fallback" in strategies:
        return "heuristic_fallback"
    if "anchored_fallback" in strategies:
        return "anchored_fallback"
    if "bounded_search" in strategies:
        return "bounded_search"
    return "direct_basis"


def _fidelity_from_strategy(strategy: str) -> tuple[str, str]:
    if strategy == "heuristic_fallback":
        return ("heuristic", "bounded walk failed; heuristic fallback used")
    if strategy == "anchored_fallback":
        return ("approximate", "bounded walk truncated; anchored approximation retained")
    return ("anchored", "deterministic bounded walk preserved orbit and label semantics")


def build_record_conversion_trace(record: CandidateRecord) -> dict[str, Any]:
    decompositions = [decompose_qphi_to_axis_walk(site.qphi) for site in record.sites]
    strategy = _summarize_strategy([entry["strategy"] for entry in decompositions])
    fidelity_tier, fidelity_reason = _fidelity_from_strategy(strategy)
    unresolved_axes: list[str] = []
    for entry in decompositions:
        for axis in entry["unresolved_axes"]:
            if axis not in unresolved_axes:
                unresolved_axes.append(axis)
    return {
        "strategy": strategy,
        "step_count": sum(int(entry["step_count"]) for entry in decompositions),
        "fidelity_reason": fidelity_reason,
        "source_signature": _source_signature(record),
        "unresolved_axes": unresolved_axes,
        "fidelity_tier": fidelity_tier,
    }


def _ordered_sites(record: CandidateRecord) -> list[tuple[SiteRecord, str]]:
    sites = [(site, _infer_orbit_name(site.label)) for site in record.sites]
    return sorted(
        sites,
        key=lambda item: (
            item[1],
            item[0].label,
            _qphi_sort_key(item[0].qphi),
        ),
    )


def _unique_labels(sites: list[tuple[SiteRecord, str]]) -> tuple[list[tuple[SiteRecord, str, str]], dict[str, str]]:
    counts: Counter[str] = Counter()
    rows: list[tuple[SiteRecord, str, str]] = []
    source_label_map: dict[str, str] = {}
    for site, orbit_name in sites:
        base_label = _sanitize_label(site.label)
        counts[base_label] += 1
        label = base_label if counts[base_label] == 1 else f"{base_label}_{counts[base_label]:02d}"
        rows.append((site, orbit_name, label))
        source_label_map[label] = site.label
    return rows, source_label_map


def candidate_to_zomic(record: CandidateRecord) -> CorpusExample:
    trace_payload = build_record_conversion_trace(record)
    fidelity_tier = trace_payload.pop("fidelity_tier")
    ordered_sites = _ordered_sites(record)
    unique_sites, source_label_map = _unique_labels(ordered_sites)

    lines = [
        f"// candidate_id={record.candidate_id}",
        f"// system={record.system}",
        f"// fidelity_tier={fidelity_tier}",
        "",
    ]
    labels: list[str] = []
    orbit_names: list[str] = []
    grouped: dict[str, list[tuple[SiteRecord, str]]] = {}
    for site, orbit_name, label in unique_sites:
        grouped.setdefault(orbit_name, []).append((site, label))

    for orbit_name in sorted(grouped):
        orbit_names.append(orbit_name)
        lines.append(f"// orbit={orbit_name}")
        lines.append("branch {")
        for site, label in grouped[orbit_name]:
            labels.append(label)
            walk = decompose_qphi_to_axis_walk(site.qphi)
            if walk["commands"]:
                lines.append("  branch {")
                for command in walk["commands"]:
                    lines.append(f"    {command}")
                lines.append(f"    label {label}")
                lines.append("  }")
            else:
                lines.append(f"  label {label}")
        lines.append("}")
        lines.append("")

    properties: dict[str, Any] = {
        "template_family": record.template_family,
        "source_label_map": source_label_map,
    }
    if "prototype_key" in record.provenance:
        properties["prototype_key"] = record.provenance["prototype_key"]
    if "zomic_design" in record.provenance:
        properties["zomic_design"] = record.provenance["zomic_design"]

    provenance = CorpusProvenance(
        example_id=record.candidate_id,
        source_family="candidate_record",
        source_path=str(record.provenance.get("source_path", f"candidate_record:{record.candidate_id}")),
        source_record_id=record.candidate_id,
        system=record.system,
        fidelity_tier=fidelity_tier,
    )
    validation = CorpusValidationState(
        parse_status="pending",
        compile_status="pending",
        site_count=len(unique_sites),
    )
    return CorpusExample(
        provenance=provenance,
        zomic_text="\n".join(lines).strip() + "\n",
        labels=labels,
        orbit_names=orbit_names,
        composition=record.composition,
        properties=properties,
        validation=validation,
        conversion_trace=CorpusConversionTrace.model_validate(trace_payload),
    )
