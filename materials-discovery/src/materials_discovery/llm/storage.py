from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import workspace_root


def _artifact_root(root: Path | None = None) -> Path:
    return workspace_root() if root is None else root


def _require_artifact_id(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be blank")
    return normalized


def _require_revision(value: int) -> int:
    if value < 0:
        raise ValueError("revision must be >= 0")
    return value


def corpus_build_dir(build_id: str, root: Path | None = None) -> Path:
    return _artifact_root(root) / "data" / "llm_corpus" / build_id


def syntax_corpus_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "syntax_corpus.jsonl"


def materials_corpus_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "materials_corpus.jsonl"


def corpus_rejects_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "rejects.jsonl"


def corpus_inventory_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "inventory.json"


def corpus_qa_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "qa.json"


def corpus_manifest_path(build_id: str, root: Path | None = None) -> Path:
    return corpus_build_dir(build_id, root) / "manifest.json"


def llm_eval_set_dir(export_id: str, root: Path | None = None) -> Path:
    return _artifact_root(root) / "data" / "llm_eval_sets" / export_id


def llm_eval_set_path(export_id: str, root: Path | None = None) -> Path:
    return llm_eval_set_dir(export_id, root) / "eval_set.jsonl"


def llm_eval_set_manifest_path(export_id: str, root: Path | None = None) -> Path:
    return llm_eval_set_dir(export_id, root) / "manifest.json"


def llm_translation_export_dir(export_id: str, root: Path | None = None) -> Path:
    normalized_export_id = _require_artifact_id(export_id, "export_id")
    return _artifact_root(root) / "data" / "llm_translation_exports" / normalized_export_id


def llm_translation_manifest_path(export_id: str, root: Path | None = None) -> Path:
    return llm_translation_export_dir(export_id, root) / "manifest.json"


def llm_translation_inventory_path(export_id: str, root: Path | None = None) -> Path:
    return llm_translation_export_dir(export_id, root) / "inventory.jsonl"


def llm_translation_payload_dir(export_id: str, root: Path | None = None) -> Path:
    return llm_translation_export_dir(export_id, root) / "payloads"


def llm_translate_stage_manifest_path(
    system_slug: str,
    export_id: str,
    root: Path | None = None,
) -> Path:
    normalized_system_slug = _require_artifact_id(system_slug, "system_slug")
    normalized_export_id = _require_artifact_id(export_id, "export_id")
    return (
        _artifact_root(root)
        / "data"
        / "manifests"
        / f"{normalized_system_slug}_{normalized_export_id}_llm_translate_manifest.json"
    )


def llm_acceptance_dir(pack_id: str, root: Path | None = None) -> Path:
    normalized_pack_id = _require_artifact_id(pack_id, "pack_id")
    return _artifact_root(root) / "data" / "benchmarks" / "llm_acceptance" / normalized_pack_id


def llm_acceptance_pack_path(pack_id: str, root: Path | None = None) -> Path:
    return llm_acceptance_dir(pack_id, root) / "acceptance_pack.json"


def llm_artifact_root_from_acceptance_pack_path(acceptance_pack_path: Path) -> Path:
    parts = acceptance_pack_path.parts
    marker = ("data", "benchmarks", "llm_acceptance")
    for idx in range(len(parts) - len(marker) + 1):
        if parts[idx : idx + len(marker)] == marker:
            return Path(*parts[:idx]) if idx > 0 else Path(".")
    raise ValueError(
        "acceptance pack path must live under data/benchmarks/llm_acceptance/{pack_id}/"
    )


def llm_acceptance_suggestion_path(pack_id: str, root: Path | None = None) -> Path:
    return llm_acceptance_dir(pack_id, root) / "suggestions.json"


def llm_acceptance_proposals_dir(pack_id: str, root: Path | None = None) -> Path:
    return llm_acceptance_dir(pack_id, root) / "proposals"


def llm_acceptance_proposal_path(
    pack_id: str,
    proposal_id: str,
    root: Path | None = None,
) -> Path:
    normalized_proposal_id = _require_artifact_id(proposal_id, "proposal_id")
    return llm_acceptance_proposals_dir(pack_id, root) / f"{normalized_proposal_id}.json"


def llm_acceptance_approvals_dir(pack_id: str, root: Path | None = None) -> Path:
    return llm_acceptance_dir(pack_id, root) / "approvals"


def llm_acceptance_approval_path(
    pack_id: str,
    approval_id: str,
    root: Path | None = None,
) -> Path:
    normalized_approval_id = _require_artifact_id(approval_id, "approval_id")
    return llm_acceptance_approvals_dir(pack_id, root) / f"{normalized_approval_id}.json"


def llm_checkpoint_dir(checkpoint_id: str, root: Path | None = None) -> Path:
    normalized_checkpoint_id = _require_artifact_id(checkpoint_id, "checkpoint_id")
    return _artifact_root(root) / "data" / "llm_checkpoints" / normalized_checkpoint_id


def llm_checkpoint_registration_path(
    checkpoint_id: str,
    root: Path | None = None,
) -> Path:
    return llm_checkpoint_dir(checkpoint_id, root) / "registration.json"


def llm_external_target_dir(model_id: str, root: Path | None = None) -> Path:
    normalized_model_id = _require_artifact_id(model_id, "model_id")
    return _artifact_root(root) / "data" / "llm_external_models" / normalized_model_id


def llm_external_target_registration_path(
    model_id: str,
    root: Path | None = None,
) -> Path:
    return llm_external_target_dir(model_id, root) / "registration.json"


def llm_external_target_environment_path(
    model_id: str,
    root: Path | None = None,
) -> Path:
    return llm_external_target_dir(model_id, root) / "environment.json"


def llm_external_target_smoke_path(
    model_id: str,
    root: Path | None = None,
) -> Path:
    return llm_external_target_dir(model_id, root) / "smoke_check.json"


def llm_checkpoint_family_dir(
    checkpoint_family: str,
    root: Path | None = None,
) -> Path:
    normalized_checkpoint_family = _require_artifact_id(checkpoint_family, "checkpoint_family")
    return _artifact_root(root) / "data" / "llm_checkpoints" / "families" / normalized_checkpoint_family


def llm_checkpoint_lifecycle_index_path(
    checkpoint_family: str,
    root: Path | None = None,
) -> Path:
    return llm_checkpoint_family_dir(checkpoint_family, root) / "lifecycle.json"


def llm_checkpoint_action_dir(
    checkpoint_family: str,
    root: Path | None = None,
) -> Path:
    return llm_checkpoint_family_dir(checkpoint_family, root) / "actions"


def _llm_checkpoint_revision_action_path(
    checkpoint_family: str,
    checkpoint_id: str,
    *,
    revision: int,
    action_prefix: str,
    root: Path | None = None,
) -> Path:
    normalized_action_prefix = _require_artifact_id(action_prefix, "action_prefix")
    normalized_checkpoint_id = _require_artifact_id(checkpoint_id, "checkpoint_id")
    normalized_revision = _require_revision(revision)
    return (
        llm_checkpoint_action_dir(checkpoint_family, root)
        / f"{normalized_action_prefix}-r{normalized_revision}-{normalized_checkpoint_id}.json"
    )


def llm_checkpoint_promotion_action_path(
    checkpoint_family: str,
    checkpoint_id: str,
    *,
    revision: int,
    root: Path | None = None,
) -> Path:
    return _llm_checkpoint_revision_action_path(
        checkpoint_family,
        checkpoint_id,
        revision=revision,
        action_prefix="promotion",
        root=root,
    )


def llm_checkpoint_retirement_action_path(
    checkpoint_family: str,
    checkpoint_id: str,
    *,
    revision: int,
    root: Path | None = None,
) -> Path:
    return _llm_checkpoint_revision_action_path(
        checkpoint_family,
        checkpoint_id,
        revision=revision,
        action_prefix="retirement",
        root=root,
    )


def llm_serving_benchmark_dir(benchmark_id: str, root: Path | None = None) -> Path:
    normalized_benchmark_id = _require_artifact_id(benchmark_id, "benchmark_id")
    return _artifact_root(root) / "data" / "benchmarks" / "llm_serving" / normalized_benchmark_id


def llm_serving_benchmark_smoke_path(
    benchmark_id: str, root: Path | None = None
) -> Path:
    return llm_serving_benchmark_dir(benchmark_id, root) / "smoke_checks.json"


def llm_serving_benchmark_summary_path(
    benchmark_id: str, root: Path | None = None
) -> Path:
    return llm_serving_benchmark_dir(benchmark_id, root) / "benchmark_summary.json"


def translated_benchmark_set_dir(
    benchmark_set_id: str, root: Path | None = None
) -> Path:
    normalized_benchmark_set_id = _require_artifact_id(benchmark_set_id, "benchmark_set_id")
    return _artifact_root(root) / "data" / "benchmarks" / "llm_external_sets" / normalized_benchmark_set_id


def translated_benchmark_contract_path(
    benchmark_set_id: str, root: Path | None = None
) -> Path:
    return translated_benchmark_set_dir(benchmark_set_id, root) / "freeze_contract.json"


def translated_benchmark_manifest_path(
    benchmark_set_id: str, root: Path | None = None
) -> Path:
    return translated_benchmark_set_dir(benchmark_set_id, root) / "manifest.json"


def translated_benchmark_included_path(
    benchmark_set_id: str, root: Path | None = None
) -> Path:
    return translated_benchmark_set_dir(benchmark_set_id, root) / "included.jsonl"


def translated_benchmark_excluded_path(
    benchmark_set_id: str, root: Path | None = None
) -> Path:
    return translated_benchmark_set_dir(benchmark_set_id, root) / "excluded.jsonl"


def llm_campaign_dir(campaign_id: str, root: Path | None = None) -> Path:
    normalized_campaign_id = _require_artifact_id(campaign_id, "campaign_id")
    return _artifact_root(root) / "data" / "llm_campaigns" / normalized_campaign_id


def llm_campaign_spec_path(campaign_id: str, root: Path | None = None) -> Path:
    return llm_campaign_dir(campaign_id, root) / "campaign_spec.json"


def llm_campaign_launches_dir(campaign_id: str, root: Path | None = None) -> Path:
    return llm_campaign_dir(campaign_id, root) / "launches"


def llm_campaign_launch_dir(
    campaign_id: str,
    launch_id: str,
    root: Path | None = None,
) -> Path:
    normalized_launch_id = _require_artifact_id(launch_id, "launch_id")
    return llm_campaign_launches_dir(campaign_id, root) / normalized_launch_id


def llm_campaign_launch_summary_path(
    campaign_id: str,
    launch_id: str,
    root: Path | None = None,
) -> Path:
    return llm_campaign_launch_dir(campaign_id, launch_id, root) / "launch_summary.json"


def llm_campaign_resolved_launch_path(
    campaign_id: str,
    launch_id: str,
    root: Path | None = None,
) -> Path:
    return llm_campaign_launch_dir(campaign_id, launch_id, root) / "resolved_launch.json"


def llm_campaign_outcome_snapshot_path(
    campaign_id: str,
    launch_id: str,
    root: Path | None = None,
) -> Path:
    return llm_campaign_launch_dir(campaign_id, launch_id, root) / "outcome_snapshot.json"


def llm_campaign_comparisons_dir(campaign_id: str, root: Path | None = None) -> Path:
    return llm_campaign_dir(campaign_id, root) / "comparisons"


def llm_campaign_comparison_path(
    campaign_id: str,
    comparison_id: str,
    root: Path | None = None,
) -> Path:
    normalized_comparison_id = _require_artifact_id(comparison_id, "comparison_id")
    return llm_campaign_comparisons_dir(campaign_id, root) / f"{normalized_comparison_id}.json"


def llm_campaign_materialized_seed_path(
    campaign_id: str,
    launch_id: str,
    root: Path | None = None,
) -> Path:
    return llm_campaign_launch_dir(campaign_id, launch_id, root) / "seed_from_evalset.zomic"
