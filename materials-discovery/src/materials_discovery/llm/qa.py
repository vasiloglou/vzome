from __future__ import annotations

import hashlib

from materials_discovery.generator.zomic_bridge import _infer_orbit_name
from materials_discovery.llm.schema import (
    CorpusBuildConfig,
    CorpusExample,
    CorpusProvenance,
    CorpusQaSummary,
    CorpusValidationState,
)

_RELEASE_RANK = {"gold": 3, "silver": 2, "pending": 1, "reject": 0}
_FIDELITY_RANK = {"exact": 3, "anchored": 2, "approximate": 1, "heuristic": 0}


def _labels_are_valid(example: CorpusExample) -> bool:
    if not example.labels:
        return False
    allowed_orbits = set(example.orbit_names)
    for label in example.labels:
        orbit_name = _infer_orbit_name(label).strip()
        if not orbit_name:
            return False
        if allowed_orbits and orbit_name not in allowed_orbits:
            return False
    return True


def _site_count(example: CorpusExample) -> int:
    if example.validation.site_count is not None:
        return example.validation.site_count
    return len(example.labels)


def _graded_release_tier(
    example: CorpusExample,
    *,
    labels_valid: bool,
    collision_free: bool,
    site_count: int,
    config: CorpusBuildConfig,
) -> str:
    parse_ok = example.validation.parse_status == "passed"
    compile_ok = example.validation.compile_status == "passed"
    fidelity_tier = example.provenance.fidelity_tier
    if (
        parse_ok
        and compile_ok
        and labels_valid
        and collision_free
        and config.gold_min_sites <= site_count <= config.gold_max_sites
        and fidelity_tier in {"exact", "anchored"}
    ):
        return "gold"
    if (
        parse_ok
        and compile_ok
        and labels_valid
        and collision_free
        and config.gold_min_sites <= site_count <= config.silver_max_sites
        and (
            fidelity_tier == "approximate"
            or site_count > config.gold_max_sites
            or (
                fidelity_tier in {"exact", "anchored"}
                and site_count > config.gold_max_sites
            )
        )
    ):
        return "silver"
    return "reject"


def grade_corpus_example(example: CorpusExample, config: CorpusBuildConfig) -> CorpusExample:
    labels_valid = _labels_are_valid(example)
    collision_free = bool(example.validation.collision_free)
    site_count = _site_count(example)
    release_tier = _graded_release_tier(
        example,
        labels_valid=labels_valid,
        collision_free=collision_free,
        site_count=site_count,
        config=config,
    )
    validation = example.validation.model_copy(
        update={
            "labels_valid": labels_valid,
            "site_count": site_count,
        }
    )
    provenance = example.provenance.model_copy(update={"release_tier": release_tier})
    return example.model_copy(update={"provenance": provenance, "validation": validation})


def _precedence_key(example: CorpusExample) -> tuple[int, int, str, str]:
    return (
        _RELEASE_RANK[example.provenance.release_tier],
        _FIDELITY_RANK[example.provenance.fidelity_tier],
        example.provenance.source_family,
        example.provenance.example_id,
    )


def _zomic_text_hash(example: CorpusExample) -> str:
    return hashlib.sha256(example.zomic_text.encode("utf-8")).hexdigest()


def dedupe_corpus_examples(examples: list[CorpusExample]) -> list[CorpusExample]:
    kept: list[CorpusExample] = []
    kept_dropped_counts: dict[int, int] = {}
    owners_by_example_id: dict[str, int] = {}
    owners_by_hash: dict[str, int] = {}
    ordered_examples = sorted(examples, key=_precedence_key, reverse=True)

    for example in ordered_examples:
        example_id = example.provenance.example_id
        zomic_hash = _zomic_text_hash(example)
        owner_index = owners_by_example_id.get(example_id)
        if owner_index is None:
            owner_index = owners_by_hash.get(zomic_hash)
        if owner_index is not None:
            kept_dropped_counts[owner_index] = kept_dropped_counts.get(owner_index, 0) + 1
            continue

        owner_index = len(kept)
        kept.append(example)
        owners_by_example_id[example_id] = owner_index
        owners_by_hash[zomic_hash] = owner_index
        kept_dropped_counts[owner_index] = kept_dropped_counts.get(owner_index, 0)

    deduped: list[CorpusExample] = []
    for index, example in enumerate(kept):
        properties = dict(example.properties)
        properties["dedupe_dropped_count"] = kept_dropped_counts.get(index, 0)
        deduped.append(example.model_copy(update={"properties": properties}))
    return deduped


def summarize_corpus_quality(examples: list[CorpusExample]) -> CorpusQaSummary:
    summary = CorpusQaSummary()
    for example in examples:
        release_tier = example.provenance.release_tier
        if release_tier == "gold":
            summary.gold_count += 1
        elif release_tier == "silver":
            summary.silver_count += 1
        elif release_tier == "reject":
            summary.reject_count += 1

        summary.duplicate_dropped_count += int(example.properties.get("dedupe_dropped_count", 0))
        if example.validation.parse_status != "passed":
            summary.parse_fail_count += 1
        if example.validation.compile_status != "passed":
            summary.compile_fail_count += 1
        if example.validation.collision_free is False:
            summary.collision_fail_count += 1
        if example.validation.labels_valid is False:
            summary.label_fail_count += 1
    return summary
