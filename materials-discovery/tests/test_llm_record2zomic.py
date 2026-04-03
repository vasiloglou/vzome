from __future__ import annotations

from materials_discovery.common.schema import CandidateRecord
from materials_discovery.llm.converters.record2zomic import (
    build_record_conversion_trace,
    candidate_to_zomic,
)


def _candidate(*, duplicate_labels: bool = False) -> CandidateRecord:
    labels = [
        "pent.top.center",
        "pent.top.left",
        "joint.top.right",
    ]
    if duplicate_labels:
        labels[2] = "pent.top.left"
    return CandidateRecord.model_validate(
        {
            "candidate_id": "sc_zn_demo_001",
            "system": "Sc-Zn",
            "template_family": "icosahedral_approximant_1_1",
            "cell": {
                "a": 14.2,
                "b": 14.2,
                "c": 14.2,
                "alpha": 90.0,
                "beta": 90.0,
                "gamma": 90.0,
            },
            "sites": [
                {
                    "label": labels[0],
                    "qphi": [[0, 0], [1, 0], [0, 0]],
                    "species": "Zn",
                    "occ": 1.0,
                },
                {
                    "label": labels[1],
                    "qphi": [[1, 0], [0, 1], [0, 0]],
                    "species": "Sc",
                    "occ": 1.0,
                },
                {
                    "label": labels[2],
                    "qphi": [[1, 1], [0, 0], [0, 0]],
                    "species": "Zn",
                    "occ": 1.0,
                },
            ],
            "composition": {"Sc": 0.3333333333, "Zn": 0.6666666667},
            "provenance": {
                "prototype_key": "sc_zn_tsai_bridge",
                "zomic_design": "designs/zomic/sc_zn_tsai_bridge.zomic",
            },
        }
    )


def test_candidate_to_zomic_returns_deterministic_output() -> None:
    first = candidate_to_zomic(_candidate())
    second = candidate_to_zomic(_candidate())

    assert first.zomic_text == second.zomic_text
    assert first.conversion_trace == second.conversion_trace


def test_output_ordering_groups_labels_by_orbit_and_stable_intra_orbit_order() -> None:
    example = candidate_to_zomic(_candidate())

    assert example.orbit_names == ["joint", "pent"]
    assert example.labels == ["joint.top.right", "pent.top.center", "pent.top.left"]


def test_build_record_conversion_trace_records_strategy_fidelity_and_source_signature() -> None:
    trace = build_record_conversion_trace(_candidate())

    assert trace["strategy"] in {"direct_basis", "bounded_search"}
    assert trace["fidelity_tier"] == "anchored"
    assert trace["source_signature"].startswith("sc_zn_demo_001:")


def test_generated_zomic_contains_label_statements_for_every_input_site() -> None:
    example = candidate_to_zomic(_candidate())

    assert example.zomic_text.count("label ") == 3
    assert example.properties["source_label_map"]["pent.top.center"] == "pent.top.center"


def test_duplicate_labels_are_disambiguated_deterministically() -> None:
    example = candidate_to_zomic(_candidate(duplicate_labels=True))

    assert "pent.top.left" in example.labels
    assert "pent.top.left_02" in example.labels
    assert example.properties["source_label_map"]["pent.top.left_02"] == "pent.top.left"


def test_sc_zn_like_qphi_fixture_yields_non_heuristic_trace_with_step_count() -> None:
    example = candidate_to_zomic(_candidate())

    assert example.provenance.fidelity_tier in {"anchored", "approximate"}
    assert example.conversion_trace is not None
    assert example.conversion_trace.step_count >= 1
    assert isinstance(example.conversion_trace.unresolved_axes, list)
