from __future__ import annotations

from materials_discovery.llm.qa import (
    dedupe_corpus_examples,
    grade_corpus_example,
    summarize_corpus_quality,
)
from materials_discovery.llm.schema import (
    CorpusBuildConfig,
    CorpusExample,
)


def _config() -> CorpusBuildConfig:
    return CorpusBuildConfig.model_validate(
        {
            "build_id": "qa-demo",
            "systems": ["Sc-Zn"],
            "gold_min_sites": 2,
            "gold_max_sites": 8,
            "silver_max_sites": 12,
            "collision_threshold_angstrom": 0.1,
        }
    )


def _example(
    *,
    example_id: str = "example-001",
    zomic_text: str = "label shell.01\nbranch { label shell.02 }\n",
    labels: list[str] | None = None,
    orbit_names: list[str] | None = None,
    fidelity_tier: str = "anchored",
    parse_status: str = "passed",
    compile_status: str = "passed",
    collision_free: bool | None = True,
    site_count: int | None = 2,
) -> CorpusExample:
    return CorpusExample.model_validate(
        {
            "provenance": {
                "example_id": example_id,
                "source_family": "candidate_record",
                "source_path": "data/candidates/sc_zn_batch.jsonl",
                "source_record_id": "candidate-001",
                "system": "Sc-Zn",
                "fidelity_tier": fidelity_tier,
                "release_tier": "pending",
            },
            "zomic_text": zomic_text,
            "labels": labels if labels is not None else ["shell.01", "shell.02"],
            "orbit_names": orbit_names if orbit_names is not None else ["shell"],
            "composition": {"Sc": 0.3, "Zn": 0.7},
            "validation": {
                "parse_status": parse_status,
                "compile_status": compile_status,
                "collision_free": collision_free,
                "site_count": site_count,
            },
        }
    )


def test_grade_corpus_example_returns_gold_for_exact_or_anchored_examples() -> None:
    graded = grade_corpus_example(_example(fidelity_tier="exact"), _config())

    assert graded.provenance.release_tier == "gold"
    assert graded.validation.labels_valid is True
    assert graded.validation.site_count == 2


def test_grade_corpus_example_downgrades_approximate_examples_to_silver() -> None:
    graded = grade_corpus_example(_example(fidelity_tier="approximate"), _config())

    assert graded.provenance.release_tier == "silver"


def test_grade_corpus_example_rejects_failed_compile_collision_or_site_count() -> None:
    too_small = grade_corpus_example(_example(site_count=1), _config())
    failed_compile = grade_corpus_example(_example(compile_status="failed"), _config())
    collided = grade_corpus_example(_example(collision_free=False), _config())
    bad_labels = grade_corpus_example(_example(orbit_names=["other"]), _config())

    assert too_small.provenance.release_tier == "reject"
    assert failed_compile.provenance.release_tier == "reject"
    assert collided.provenance.release_tier == "reject"
    assert bad_labels.validation.labels_valid is False


def test_dedupe_corpus_examples_keeps_best_example_by_release_and_fidelity() -> None:
    gold = grade_corpus_example(_example(example_id="dup-001", fidelity_tier="exact"), _config())
    silver = grade_corpus_example(
        _example(example_id="dup-001", fidelity_tier="approximate"),
        _config(),
    )
    text_duplicate = grade_corpus_example(
        _example(example_id="dup-002", fidelity_tier="anchored", zomic_text=gold.zomic_text),
        _config(),
    )

    deduped = dedupe_corpus_examples([silver, text_duplicate, gold])

    assert len(deduped) == 1
    assert deduped[0].provenance.example_id == "dup-001"
    assert deduped[0].properties["dedupe_dropped_count"] == 2


def test_summarize_corpus_quality_reports_counts_and_issue_tallies() -> None:
    gold = grade_corpus_example(
        _example(
            example_id="gold-001",
            fidelity_tier="exact",
            zomic_text="label gold.01\nbranch { label gold.02 }\n",
            labels=["gold.01", "gold.02"],
            orbit_names=["gold"],
        ),
        _config(),
    )
    silver = grade_corpus_example(
        _example(
            example_id="silver-001",
            fidelity_tier="approximate",
            zomic_text="label silver.01\nbranch { label silver.02 }\n",
            labels=["silver.01", "silver.02"],
            orbit_names=["silver"],
        ),
        _config(),
    )
    reject = grade_corpus_example(
        _example(
            example_id="reject-001",
            fidelity_tier="heuristic",
            parse_status="failed",
            compile_status="failed",
            collision_free=False,
            zomic_text="label reject.01\nbranch { label reject.02 }\n",
            labels=["reject.01", "reject.02"],
            orbit_names=["other"],
        ),
        _config(),
    )

    deduped = dedupe_corpus_examples([gold, silver, reject, silver])
    summary = summarize_corpus_quality(deduped)

    assert summary.gold_count == 1
    assert summary.silver_count == 1
    assert summary.reject_count == 1
    assert summary.duplicate_dropped_count == 1
    assert summary.parse_fail_count == 1
    assert summary.compile_fail_count == 1
    assert summary.collision_fail_count == 1
    assert summary.label_fail_count == 1
