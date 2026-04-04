from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from materials_discovery.common.io import (
    load_json_object,
    load_jsonl,
    write_json_object,
    workspace_root,
)
from materials_discovery.llm.replay import CampaignLaunchBundle, load_campaign_launch_bundle
from materials_discovery.llm.schema import (
    LlmAcceptancePack,
    LlmAcceptanceSystemMetrics,
    LlmCampaignComparisonResult,
    LlmCampaignLaunchSummary,
    LlmCampaignOutcomeSnapshot,
    OUTCOME_METRIC_KEYS,
)
from materials_discovery.llm.storage import (
    llm_campaign_comparison_path,
    llm_campaign_launches_dir,
    llm_campaign_outcome_snapshot_path,
)


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root


def _resolve_artifact_path(path_str: str, *, root: Path | None = None) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (_artifact_root(root) / path).resolve()


def _system_slug(system: str) -> str:
    return system.lower().replace("-", "_")


def _metric_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(int(value))
    if isinstance(value, int | float):
        return float(value)
    return None


def _metric_value_from_outcome(
    outcome: LlmCampaignOutcomeSnapshot,
    metric_name: str,
) -> float | None:
    return _metric_float(getattr(outcome, metric_name))


def _metric_value_from_acceptance(
    acceptance: LlmAcceptanceSystemMetrics,
    metric_name: str,
) -> float | None:
    return _metric_float(getattr(acceptance, metric_name))


def find_prior_campaign_launch(
    current_launch_summary: LlmCampaignLaunchSummary,
    root: Path | None = None,
) -> Path | None:
    launches_dir = llm_campaign_launches_dir(current_launch_summary.campaign_id, root=root)
    if not launches_dir.exists():
        return None

    current_key = (current_launch_summary.created_at_utc, current_launch_summary.launch_id)
    candidates: list[tuple[str, str, Path]] = []
    for summary_path in sorted(launches_dir.glob("*/launch_summary.json")):
        if summary_path == Path(current_launch_summary.resolved_launch_path).parent / "launch_summary.json":
            continue
        payload = LlmCampaignLaunchSummary.model_validate(load_json_object(summary_path))
        if payload.system != current_launch_summary.system:
            continue
        candidate_key = (payload.created_at_utc, payload.launch_id)
        if candidate_key >= current_key:
            continue
        candidates.append((payload.created_at_utc, payload.launch_id, summary_path))

    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][2]


def _matching_manifest(path: Path, launch_id: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = load_json_object(path)
    source_lineage = payload.get("source_lineage")
    if not isinstance(source_lineage, dict):
        return None
    llm_campaign = source_lineage.get("llm_campaign")
    if not isinstance(llm_campaign, dict):
        return None
    if llm_campaign.get("launch_id") != launch_id:
        return None
    return payload


def _validation_manifest_path(root: Path, system_slug: str, launch_id: str) -> Path | None:
    candidates: list[tuple[str, Path]] = []
    manifests_dir = root / "data" / "manifests"
    for manifest_path in sorted(manifests_dir.glob(f"{system_slug}_*_hifi_validate_manifest.json")):
        payload = _matching_manifest(manifest_path, launch_id)
        if payload is not None:
            created_at = payload.get("created_at_utc")
            candidates.append((str(created_at or ""), manifest_path))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]


def _load_calibration(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json_object(path)


def build_campaign_outcome_snapshot(
    bundle: CampaignLaunchBundle,
    root: Path | None = None,
) -> LlmCampaignOutcomeSnapshot:
    outcome_path = llm_campaign_outcome_snapshot_path(
        bundle.launch_summary.campaign_id,
        bundle.launch_summary.launch_id,
        root=root,
    )
    if outcome_path.exists():
        return LlmCampaignOutcomeSnapshot.model_validate(load_json_object(outcome_path))

    compile_results = load_jsonl(
        _resolve_artifact_path(bundle.run_manifest.compile_results_path, root=root)
    )
    attempt_count = bundle.run_manifest.attempt_count or len(compile_results)
    parse_pass_count = sum(row.get("parse_status") == "passed" for row in compile_results)
    compile_pass_count = sum(row.get("compile_status") == "passed" for row in compile_results)
    parse_success_rate = 0.0 if attempt_count <= 0 else parse_pass_count / attempt_count
    compile_success_rate = 0.0 if attempt_count <= 0 else compile_pass_count / attempt_count
    generation_success_rate = (
        0.0
        if bundle.run_manifest.requested_count <= 0
        else bundle.run_manifest.generated_count / bundle.run_manifest.requested_count
    )

    root_path = _artifact_root(root)
    system_slug = _system_slug(bundle.launch_summary.system)
    launch_id = bundle.launch_summary.launch_id
    missing_metrics: list[str] = []
    stage_manifest_paths: dict[str, str] = {}
    shortlist_pass_rate: float | None = None
    validation_pass_rate: float | None = None
    novelty_score_mean: float | None = None
    synthesizability_mean: float | None = None
    report_release_gate_ready: bool | None = None

    screen_manifest_path = root_path / "data" / "manifests" / f"{system_slug}_screen_manifest.json"
    if _matching_manifest(screen_manifest_path, launch_id) is not None:
        screen_calibration = _load_calibration(
            root_path / "data" / "calibration" / f"{system_slug}_screen_calibration.json"
        )
        if screen_calibration is not None:
            shortlist_pass_rate = _metric_float(screen_calibration.get("pass_rate"))
            stage_manifest_paths["screen"] = str(screen_manifest_path)
    if shortlist_pass_rate is None:
        missing_metrics.append("shortlist_pass_rate")

    validation_manifest_path = _validation_manifest_path(root_path, system_slug, launch_id)
    if validation_manifest_path is not None:
        calibration_name = validation_manifest_path.name.replace(
            "_hifi_validate_manifest.json",
            "_validation_calibration.json",
        )
        validation_calibration = _load_calibration(
            root_path / "data" / "calibration" / calibration_name
        )
        if validation_calibration is not None:
            validation_pass_rate = _metric_float(validation_calibration.get("pass_rate"))
            stage_manifest_paths["hifi_validate"] = str(validation_manifest_path)
    if validation_pass_rate is None:
        missing_metrics.append("validation_pass_rate")

    rank_manifest_path = root_path / "data" / "manifests" / f"{system_slug}_hifi_rank_manifest.json"
    if _matching_manifest(rank_manifest_path, launch_id) is not None:
        rank_calibration = _load_calibration(
            root_path / "data" / "calibration" / f"{system_slug}_ranking_calibration.json"
        )
        if rank_calibration is not None:
            novelty_score_mean = _metric_float(rank_calibration.get("novelty_score_mean"))
            stage_manifest_paths["hifi_rank"] = str(rank_manifest_path)
    if novelty_score_mean is None:
        missing_metrics.append("novelty_score_mean")

    report_manifest_path = root_path / "data" / "manifests" / f"{system_slug}_report_manifest.json"
    if _matching_manifest(report_manifest_path, launch_id) is not None:
        report_calibration = _load_calibration(
            root_path / "data" / "calibration" / f"{system_slug}_report_calibration.json"
        )
        if report_calibration is not None:
            synthesizability_mean = _metric_float(
                report_calibration.get("llm_synthesizability_mean")
            )
            report_release_gate_ready = bool(report_calibration.get("release_gate_ready"))
            stage_manifest_paths["report"] = str(report_manifest_path)
        pipeline_manifest_path = root_path / "data" / "manifests" / f"{system_slug}_pipeline_manifest.json"
        if _matching_manifest(pipeline_manifest_path, launch_id) is not None:
            stage_manifest_paths["pipeline"] = str(pipeline_manifest_path)
    if synthesizability_mean is None:
        missing_metrics.append("synthesizability_mean")
    if report_release_gate_ready is None:
        missing_metrics.append("report_release_gate_ready")

    snapshot = LlmCampaignOutcomeSnapshot(
        campaign_id=bundle.launch_summary.campaign_id,
        launch_id=bundle.launch_summary.launch_id,
        system=bundle.launch_summary.system,
        launch_summary_path=str(bundle.launch_summary_path),
        campaign_spec_path=str(bundle.campaign_spec_path),
        acceptance_pack_path=bundle.campaign_spec.lineage.acceptance_pack_path,
        requested_model_lanes=list(bundle.launch_summary.requested_model_lanes),
        resolved_model_lane=bundle.launch_summary.resolved_model_lane,
        resolved_model_lane_source=bundle.launch_summary.resolved_model_lane_source,
        parse_success_rate=round(parse_success_rate, 6),
        compile_success_rate=round(compile_success_rate, 6),
        generation_success_rate=round(generation_success_rate, 6),
        shortlist_pass_rate=None if shortlist_pass_rate is None else round(shortlist_pass_rate, 6),
        validation_pass_rate=None if validation_pass_rate is None else round(validation_pass_rate, 6),
        novelty_score_mean=None if novelty_score_mean is None else round(novelty_score_mean, 6),
        synthesizability_mean=(
            None if synthesizability_mean is None else round(synthesizability_mean, 6)
        ),
        report_release_gate_ready=report_release_gate_ready,
        missing_metrics=missing_metrics,
        stage_manifest_paths=stage_manifest_paths,
    )
    write_json_object(snapshot.model_dump(mode="json"), outcome_path)
    return snapshot


def _acceptance_baseline_for_bundle(
    bundle: CampaignLaunchBundle,
    *,
    root: Path | None = None,
) -> LlmAcceptanceSystemMetrics:
    acceptance_pack_path = _resolve_artifact_path(
        bundle.campaign_spec.lineage.acceptance_pack_path,
        root=root,
    )
    acceptance_pack = LlmAcceptancePack.model_validate(load_json_object(acceptance_pack_path))
    for system_metrics in acceptance_pack.systems:
        if system_metrics.system == bundle.campaign_spec.system:
            return system_metrics
    raise ValueError("acceptance pack does not contain metrics for the campaign system")


def _delta_map(
    current_outcome: LlmCampaignOutcomeSnapshot,
    baseline: LlmAcceptanceSystemMetrics | LlmCampaignOutcomeSnapshot,
) -> dict[str, float]:
    deltas: dict[str, float] = {}
    for metric_name in OUTCOME_METRIC_KEYS:
        current_value = _metric_value_from_outcome(current_outcome, metric_name)
        if isinstance(baseline, LlmAcceptanceSystemMetrics):
            baseline_value = _metric_value_from_acceptance(baseline, metric_name)
        else:
            baseline_value = _metric_value_from_outcome(baseline, metric_name)
        if current_value is None or baseline_value is None:
            continue
        deltas[metric_name] = round(current_value - baseline_value, 6)
    return deltas


def _summary_lines(
    comparison_id: str,
    current_outcome: LlmCampaignOutcomeSnapshot,
    acceptance_baseline: LlmAcceptanceSystemMetrics,
    prior_outcome: LlmCampaignOutcomeSnapshot | None,
    delta_vs_acceptance: dict[str, float],
    delta_vs_prior: dict[str, float],
) -> list[str]:
    lines = [
        (
            f"{current_outcome.system} campaign {current_outcome.campaign_id} "
            f"launch {current_outcome.launch_id} ({comparison_id})"
        ),
        f"Acceptance baseline loaded for {acceptance_baseline.system}.",
        (
            f"Prior launch baseline: {prior_outcome.launch_id}"
            if prior_outcome is not None
            else "Prior launch baseline: none"
        ),
    ]
    for metric_name in OUTCOME_METRIC_KEYS:
        if metric_name in delta_vs_acceptance:
            lines.append(
                f"vs acceptance {metric_name}: {delta_vs_acceptance[metric_name]:+0.6f}"
            )
        if metric_name in delta_vs_prior:
            lines.append(f"vs prior {metric_name}: {delta_vs_prior[metric_name]:+0.6f}")
    if current_outcome.missing_metrics:
        lines.append(
            "Current outcome missing metrics: "
            + ", ".join(current_outcome.missing_metrics)
        )
    if prior_outcome is not None and prior_outcome.missing_metrics:
        lines.append("Prior outcome missing metrics: " + ", ".join(prior_outcome.missing_metrics))
    return lines


def build_campaign_comparison(
    bundle: CampaignLaunchBundle,
    *,
    current_outcome: LlmCampaignOutcomeSnapshot | None = None,
    prior_outcome: LlmCampaignOutcomeSnapshot | None = None,
    root: Path | None = None,
) -> LlmCampaignComparisonResult:
    effective_current = current_outcome or build_campaign_outcome_snapshot(bundle, root=root)
    acceptance_baseline = _acceptance_baseline_for_bundle(bundle, root=root)

    effective_prior = prior_outcome
    if effective_prior is None:
        prior_launch_summary_path = find_prior_campaign_launch(bundle.launch_summary, root=root)
        if prior_launch_summary_path is not None:
            prior_summary = LlmCampaignLaunchSummary.model_validate(
                load_json_object(prior_launch_summary_path)
            )
            prior_snapshot_path = llm_campaign_outcome_snapshot_path(
                prior_summary.campaign_id,
                prior_summary.launch_id,
                root=root,
            )
            if prior_snapshot_path.exists():
                effective_prior = LlmCampaignOutcomeSnapshot.model_validate(
                    load_json_object(prior_snapshot_path)
                )
            else:
                prior_bundle = load_campaign_launch_bundle(prior_launch_summary_path, root=root)
                effective_prior = build_campaign_outcome_snapshot(prior_bundle, root=root)

    delta_vs_acceptance = _delta_map(effective_current, acceptance_baseline)
    delta_vs_prior = (
        {}
        if effective_prior is None
        else _delta_map(effective_current, effective_prior)
    )
    comparison_id = f"comparison_{effective_current.launch_id}"
    summary_lines = _summary_lines(
        comparison_id,
        effective_current,
        acceptance_baseline,
        effective_prior,
        delta_vs_acceptance,
        delta_vs_prior,
    )
    comparison = LlmCampaignComparisonResult(
        comparison_id=comparison_id,
        campaign_id=effective_current.campaign_id,
        launch_id=effective_current.launch_id,
        system=effective_current.system,
        generated_at_utc=datetime.now(UTC).isoformat(),
        current_outcome=effective_current,
        acceptance_baseline=acceptance_baseline,
        prior_outcome=effective_prior,
        delta_vs_acceptance=delta_vs_acceptance,
        delta_vs_prior=delta_vs_prior,
        summary_lines=summary_lines,
    )
    comparison_path = llm_campaign_comparison_path(
        comparison.campaign_id,
        comparison.comparison_id,
        root=root,
    )
    write_json_object(comparison.model_dump(mode="json"), comparison_path)
    return comparison
