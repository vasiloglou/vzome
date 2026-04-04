from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from materials_discovery.common.io import write_json_object
from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmSuggestion,
    LlmSuggestionItem,
)


def build_llm_suggestions(pack: LlmAcceptancePack) -> LlmSuggestion:
    items: list[LlmSuggestionItem] = []

    for system in pack.systems:
        if "parse_success_rate" in system.failing_metrics or "compile_success_rate" in system.failing_metrics:
            items.append(
                LlmSuggestionItem(
                    system=system.system,
                    priority="high",
                    action="Tighten prompt constraints and expand exact system-matched examples.",
                    rationale="Validity metrics are below acceptance thresholds, so the next iteration should improve parse and compile reliability before widening search.",
                )
            )
            continue

        if "validation_pass_rate" in system.failing_metrics or "shortlist_pass_rate" in system.failing_metrics:
            items.append(
                LlmSuggestionItem(
                    system=system.system,
                    priority="high",
                    action="Bias conditioning toward higher-quality accepted examples near the target composition window.",
                    rationale="The lane is generating candidates, but too few survive screening or digital validation for this system.",
                )
            )
            continue

        if "synthesizability_mean" in system.failing_metrics:
            items.append(
                LlmSuggestionItem(
                    system=system.system,
                    priority="medium",
                    action="Expand the materials-conditioned eval set and refine evaluation prompts for precursor realism.",
                    rationale="The candidates are structurally valid, but the LLM assessment still sees weak synthesis readiness.",
                )
            )
            continue

        if not system.report_release_gate_ready:
            items.append(
                LlmSuggestionItem(
                    system=system.system,
                    priority="medium",
                    action="Keep the LLM lane in audit mode and collect one more benchmark pack before promotion.",
                    rationale="Core metrics look acceptable, but the report release gate is not yet ready for this system.",
                )
            )
            continue

        items.append(
            LlmSuggestionItem(
                system=system.system,
                priority="low",
                action="Promote this system to broader provider comparisons or a hosted-model bakeoff.",
                rationale="Acceptance metrics and release-gate posture look strong enough for the next evaluation round.",
            )
        )

    return LlmSuggestion(
        pack_id=pack.pack_id,
        overall_status="ready" if pack.overall_passed else "needs_improvement",
        generated_at_utc=datetime.now(UTC).isoformat(),
        items=items,
    )


def write_llm_suggestions(suggestions: LlmSuggestion, path: Path) -> Path:
    write_json_object(suggestions.model_dump(mode="json"), path)
    return path
