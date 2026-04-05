from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from materials_discovery.common.schema import BackendConfig, LlmModelLaneConfig
from materials_discovery.llm.checkpoints import (
    load_checkpoint_lifecycle,
    load_registered_checkpoint,
    list_checkpoint_family_members,
    promote_checkpoint,
    register_llm_checkpoint,
    retire_checkpoint,
    resolve_checkpoint_lane,
)
from materials_discovery.llm.launch import build_serving_identity
from materials_discovery.llm.storage import (
    llm_checkpoint_action_dir,
    llm_checkpoint_family_dir,
    llm_checkpoint_lifecycle_index_path,
    llm_checkpoint_promotion_action_path,
    llm_checkpoint_registration_path,
    llm_checkpoint_retirement_action_path,
)


def _write_required_lineage_files(root: Path) -> None:
    (root / "lineage").mkdir(parents=True, exist_ok=True)
    (root / "lineage" / "adapter_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "corpus_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "eval_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "acceptance_pack.json").write_text("{}", encoding="utf-8")


def _write_registration_spec(
    root: Path,
    *,
    checkpoint_id: str = "ckpt-al-cu-fe-zomic-adapted",
    checkpoint_family: str | None = None,
    model: str = "zomic-adapted-local-v1",
) -> Path:
    spec = {
        "checkpoint_id": checkpoint_id,
        "system": "Al-Cu-Fe",
        "template_family": "icosahedral_approximant_1_1",
        "adapter": "openai_compat_v1",
        "provider": "openai_compat",
        "model": model,
        "local_model_path": "/opt/models/zomic-adapted-local-v1",
        "model_revision": "adapted-dev-2026-04-05",
        "base_model": "zomic-general-local-v1",
        "base_model_revision": "local-dev-2026-04-05",
        "adaptation_method": "lora",
        "adaptation_artifact_path": "lineage/adapter_manifest.json",
        "corpus_manifest_path": "lineage/corpus_manifest.json",
        "eval_set_manifest_path": "lineage/eval_manifest.json",
        "acceptance_pack_path": "lineage/acceptance_pack.json",
    }
    if checkpoint_family is not None:
        spec["checkpoint_family"] = checkpoint_family
    spec_path = root / f"{checkpoint_id}.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def _write_evidence_files(root: Path) -> list[str]:
    relative_paths = [
        "reports/serving_benchmark.json",
        "reports/acceptance_eval.json",
    ]
    for relative_path in relative_paths:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")
    return relative_paths


def _write_promotion_spec(
    root: Path,
    *,
    checkpoint_family: str,
    checkpoint_id: str,
    expected_revision: int | None,
    expected_promoted_checkpoint_id: str | None = None,
    evidence_paths: list[str] | None = None,
) -> Path:
    spec = {
        "checkpoint_family": checkpoint_family,
        "checkpoint_id": checkpoint_id,
        "evidence_paths": evidence_paths or _write_evidence_files(root),
    }
    if expected_revision is not None:
        spec["expected_revision"] = expected_revision
    if expected_promoted_checkpoint_id is not None:
        spec["expected_promoted_checkpoint_id"] = expected_promoted_checkpoint_id
    spec_path = root / f"{checkpoint_id}-promotion.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def _write_retirement_spec(
    root: Path,
    *,
    checkpoint_family: str,
    checkpoint_id: str,
    expected_revision: int | None,
    reason: str = "superseded",
    expected_promoted_checkpoint_id: str | None = None,
    replacement_checkpoint_id: str | None = None,
) -> Path:
    spec = {
        "checkpoint_family": checkpoint_family,
        "checkpoint_id": checkpoint_id,
        "reason": reason,
    }
    if expected_revision is not None:
        spec["expected_revision"] = expected_revision
    if expected_promoted_checkpoint_id is not None:
        spec["expected_promoted_checkpoint_id"] = expected_promoted_checkpoint_id
    if replacement_checkpoint_id is not None:
        spec["replacement_checkpoint_id"] = replacement_checkpoint_id
    spec_path = root / f"{checkpoint_id}-retirement.yaml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def test_register_checkpoint_writes_registration_and_fingerprint(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    spec_path = _write_registration_spec(tmp_path)

    summary = register_llm_checkpoint(spec_path, root=tmp_path)
    registration, registration_path = load_registered_checkpoint(
        "ckpt-al-cu-fe-zomic-adapted",
        root=tmp_path,
    )

    assert summary.checkpoint_id == "ckpt-al-cu-fe-zomic-adapted"
    assert summary.fingerprint == registration.fingerprint
    assert registration_path == tmp_path / "data" / "llm_checkpoints" / "ckpt-al-cu-fe-zomic-adapted" / "registration.json"
    assert registration.corpus_manifest_path == "lineage/corpus_manifest.json"
    assert registration.eval_set_manifest_path == "lineage/eval_manifest.json"
    assert registration.acceptance_pack_path == "lineage/acceptance_pack.json"


def test_register_checkpoint_rejects_missing_lineage_inputs(tmp_path: Path) -> None:
    spec_path = _write_registration_spec(tmp_path)

    with pytest.raises(FileNotFoundError, match="adaptation artifact"):
        register_llm_checkpoint(spec_path, root=tmp_path)


def test_checkpoint_family_storage_paths_are_deterministic(tmp_path: Path) -> None:
    family_dir = llm_checkpoint_family_dir(" adapted-al-cu-fe ", root=tmp_path)
    lifecycle_path = llm_checkpoint_lifecycle_index_path("adapted-al-cu-fe", root=tmp_path)
    action_dir = llm_checkpoint_action_dir("adapted-al-cu-fe", root=tmp_path)

    assert family_dir == tmp_path / "data" / "llm_checkpoints" / "families" / "adapted-al-cu-fe"
    assert lifecycle_path == family_dir / "lifecycle.json"
    assert action_dir == family_dir / "actions"


def test_checkpoint_lifecycle_action_paths_use_revision_filenames(tmp_path: Path) -> None:
    promotion_path = llm_checkpoint_promotion_action_path(
        "adapted-al-cu-fe",
        "ckpt-al-cu-fe-zomic-adapted",
        revision=3,
        root=tmp_path,
    )
    retirement_path = llm_checkpoint_retirement_action_path(
        "adapted-al-cu-fe",
        "ckpt-al-cu-fe-zomic-adapted",
        revision=4,
        root=tmp_path,
    )

    assert promotion_path == (
        tmp_path
        / "data"
        / "llm_checkpoints"
        / "families"
        / "adapted-al-cu-fe"
        / "actions"
        / "promotion-r3-ckpt-al-cu-fe-zomic-adapted.json"
    )
    assert retirement_path == (
        tmp_path
        / "data"
        / "llm_checkpoints"
        / "families"
        / "adapted-al-cu-fe"
        / "actions"
        / "retirement-r4-ckpt-al-cu-fe-zomic-adapted.json"
    )


def test_checkpoint_family_storage_keeps_registration_path_unchanged(tmp_path: Path) -> None:
    registration_path = llm_checkpoint_registration_path(
        "ckpt-al-cu-fe-zomic-adapted",
        root=tmp_path,
    )

    assert registration_path == (
        tmp_path
        / "data"
        / "llm_checkpoints"
        / "ckpt-al-cu-fe-zomic-adapted"
        / "registration.json"
    )


def test_register_checkpoint_with_family_auto_enrolls_candidate_member(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    spec_path = _write_registration_spec(
        tmp_path,
        checkpoint_family="adapted-al-cu-fe",
    )

    summary = register_llm_checkpoint(spec_path, root=tmp_path)
    lifecycle, lifecycle_path = load_checkpoint_lifecycle("adapted-al-cu-fe", root=tmp_path)
    members = list_checkpoint_family_members("adapted-al-cu-fe", root=tmp_path)

    assert summary.checkpoint_family == "adapted-al-cu-fe"
    assert lifecycle_path == (
        tmp_path / "data" / "llm_checkpoints" / "families" / "adapted-al-cu-fe" / "lifecycle.json"
    )
    assert lifecycle.revision == 1
    assert lifecycle.promoted_checkpoint_id is None
    assert len(members) == 1
    assert members[0].checkpoint_id == "ckpt-al-cu-fe-zomic-adapted"
    assert members[0].lifecycle_state == "candidate"
    assert members[0].registration_path == (
        "data/llm_checkpoints/ckpt-al-cu-fe-zomic-adapted/registration.json"
    )


def test_register_checkpoint_without_family_keeps_legacy_behavior(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    spec_path = _write_registration_spec(tmp_path)

    summary = register_llm_checkpoint(spec_path, root=tmp_path)

    assert summary.checkpoint_family is None
    assert not llm_checkpoint_lifecycle_index_path("adapted-al-cu-fe", root=tmp_path).exists()


def test_promote_checkpoint_updates_lifecycle_and_writes_action_artifact(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    first_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        checkpoint_family="adapted-al-cu-fe",
    )
    second_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-b",
        checkpoint_family="adapted-al-cu-fe",
    )
    register_llm_checkpoint(first_spec, root=tmp_path)
    register_llm_checkpoint(second_spec, root=tmp_path)

    promotion_spec = _write_promotion_spec(
        tmp_path,
        checkpoint_family="adapted-al-cu-fe",
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        expected_revision=2,
    )

    lifecycle = promote_checkpoint(promotion_spec, root=tmp_path)
    action_path = llm_checkpoint_promotion_action_path(
        "adapted-al-cu-fe",
        "ckpt-al-cu-fe-zomic-a",
        revision=3,
        root=tmp_path,
    )

    assert lifecycle.revision == 3
    assert lifecycle.promoted_checkpoint_id == "ckpt-al-cu-fe-zomic-a"
    assert action_path.exists()
    payload = yaml.safe_load(action_path.read_text(encoding="utf-8"))
    assert payload["checkpoint_family"] == "adapted-al-cu-fe"
    assert payload["checkpoint_id"] == "ckpt-al-cu-fe-zomic-a"
    assert payload["evidence_paths"] == [
        "reports/serving_benchmark.json",
        "reports/acceptance_eval.json",
    ]
    member_states = {
        member.checkpoint_id: member.lifecycle_state
        for member in lifecycle.members
    }
    assert member_states == {
        "ckpt-al-cu-fe-zomic-a": "promoted",
        "ckpt-al-cu-fe-zomic-b": "candidate",
    }


def test_promote_checkpoint_is_idempotent_for_current_member(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    first_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        checkpoint_family="adapted-al-cu-fe",
    )
    second_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-b",
        checkpoint_family="adapted-al-cu-fe",
    )
    register_llm_checkpoint(first_spec, root=tmp_path)
    register_llm_checkpoint(second_spec, root=tmp_path)
    first_promotion = _write_promotion_spec(
        tmp_path,
        checkpoint_family="adapted-al-cu-fe",
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        expected_revision=2,
    )
    lifecycle = promote_checkpoint(first_promotion, root=tmp_path)
    repeat_promotion = _write_promotion_spec(
        tmp_path,
        checkpoint_family="adapted-al-cu-fe",
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        expected_revision=lifecycle.revision,
        expected_promoted_checkpoint_id="ckpt-al-cu-fe-zomic-a",
    )

    repeated = promote_checkpoint(repeat_promotion, root=tmp_path)

    assert repeated.revision == lifecycle.revision
    assert repeated.promoted_checkpoint_id == "ckpt-al-cu-fe-zomic-a"
    assert repeated.action_history_paths == lifecycle.action_history_paths


def test_promote_checkpoint_rejects_stale_revision_with_retry_guidance(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    first_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        checkpoint_family="adapted-al-cu-fe",
    )
    second_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-b",
        checkpoint_family="adapted-al-cu-fe",
    )
    register_llm_checkpoint(first_spec, root=tmp_path)
    register_llm_checkpoint(second_spec, root=tmp_path)
    promote_checkpoint(
        _write_promotion_spec(
            tmp_path,
            checkpoint_family="adapted-al-cu-fe",
            checkpoint_id="ckpt-al-cu-fe-zomic-a",
            expected_revision=2,
        ),
        root=tmp_path,
    )

    with pytest.raises(ValueError, match="reload the current lifecycle revision and retry"):
        promote_checkpoint(
            _write_promotion_spec(
                tmp_path,
                checkpoint_family="adapted-al-cu-fe",
                checkpoint_id="ckpt-al-cu-fe-zomic-b",
                expected_revision=2,
            ),
            root=tmp_path,
        )


def test_retire_promoted_checkpoint_requires_promoting_a_different_member_first(
    tmp_path: Path,
) -> None:
    _write_required_lineage_files(tmp_path)
    first_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        checkpoint_family="adapted-al-cu-fe",
    )
    second_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-b",
        checkpoint_family="adapted-al-cu-fe",
    )
    register_llm_checkpoint(first_spec, root=tmp_path)
    register_llm_checkpoint(second_spec, root=tmp_path)
    lifecycle = promote_checkpoint(
        _write_promotion_spec(
            tmp_path,
            checkpoint_family="adapted-al-cu-fe",
            checkpoint_id="ckpt-al-cu-fe-zomic-a",
            expected_revision=2,
        ),
        root=tmp_path,
    )

    with pytest.raises(ValueError, match="promote a different checkpoint first"):
        retire_checkpoint(
            _write_retirement_spec(
                tmp_path,
                checkpoint_family="adapted-al-cu-fe",
                checkpoint_id="ckpt-al-cu-fe-zomic-a",
                expected_revision=lifecycle.revision,
            ),
            root=tmp_path,
        )


def test_retired_checkpoint_remains_auditable_and_replay_safe(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    first_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-a",
        checkpoint_family="adapted-al-cu-fe",
    )
    second_spec = _write_registration_spec(
        tmp_path,
        checkpoint_id="ckpt-al-cu-fe-zomic-b",
        checkpoint_family="adapted-al-cu-fe",
    )
    register_llm_checkpoint(first_spec, root=tmp_path)
    register_llm_checkpoint(second_spec, root=tmp_path)
    lifecycle = promote_checkpoint(
        _write_promotion_spec(
            tmp_path,
            checkpoint_family="adapted-al-cu-fe",
            checkpoint_id="ckpt-al-cu-fe-zomic-a",
            expected_revision=2,
        ),
        root=tmp_path,
    )

    retired = retire_checkpoint(
        _write_retirement_spec(
            tmp_path,
            checkpoint_family="adapted-al-cu-fe",
            checkpoint_id="ckpt-al-cu-fe-zomic-b",
            expected_revision=lifecycle.revision,
            expected_promoted_checkpoint_id="ckpt-al-cu-fe-zomic-a",
        ),
        root=tmp_path,
    )
    registration, registration_path = load_registered_checkpoint(
        "ckpt-al-cu-fe-zomic-b",
        root=tmp_path,
    )
    action_path = llm_checkpoint_retirement_action_path(
        "adapted-al-cu-fe",
        "ckpt-al-cu-fe-zomic-b",
        revision=4,
        root=tmp_path,
    )

    assert registration.checkpoint_family == "adapted-al-cu-fe"
    assert registration_path.exists()
    assert action_path.exists()
    retired_member = next(
        member
        for member in retired.members
        if member.checkpoint_id == "ckpt-al-cu-fe-zomic-b"
    )
    assert retired.revision == 4
    assert retired_member.lifecycle_state == "retired"
    assert retired_member.retirement_reason == "superseded"


def test_resolve_checkpoint_lane_fills_identity_from_registration(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    spec_path = _write_registration_spec(tmp_path)
    register_llm_checkpoint(spec_path, root=tmp_path)

    lane = LlmModelLaneConfig(
        adapter="openai_compat_v1",
        provider="openai_compat",
        model="zomic-adapted-local-v1",
        api_base="http://localhost:8000",
        checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
    )

    resolved_lane, checkpoint_lineage = resolve_checkpoint_lane(lane, root=tmp_path)

    assert resolved_lane.model_revision == "adapted-dev-2026-04-05"
    assert resolved_lane.local_model_path == "/opt/models/zomic-adapted-local-v1"
    assert checkpoint_lineage is not None
    assert checkpoint_lineage.base_model == "zomic-general-local-v1"
    assert checkpoint_lineage.adaptation_method == "lora"
    assert checkpoint_lineage.registration_path == (
        "data/llm_checkpoints/ckpt-al-cu-fe-zomic-adapted/registration.json"
    )


def test_resolve_checkpoint_lane_rejects_checkpoint_family_mismatch(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    spec_path = _write_registration_spec(
        tmp_path,
        checkpoint_family="adapted-al-cu-fe",
    )
    register_llm_checkpoint(spec_path, root=tmp_path)

    lane = LlmModelLaneConfig(
        adapter="openai_compat_v1",
        provider="openai_compat",
        model="zomic-adapted-local-v1",
        api_base="http://localhost:8000",
        checkpoint_family="different-family",
        checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
    )

    with pytest.raises(ValueError, match="does not belong to checkpoint_family"):
        resolve_checkpoint_lane(lane, root=tmp_path)


def test_resolve_checkpoint_lane_rejects_model_mismatch(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    spec_path = _write_registration_spec(tmp_path)
    register_llm_checkpoint(spec_path, root=tmp_path)

    lane = LlmModelLaneConfig(
        adapter="openai_compat_v1",
        provider="openai_compat",
        model="wrong-model-name",
        api_base="http://localhost:8000",
        checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
    )

    with pytest.raises(ValueError, match="model mismatch"):
        resolve_checkpoint_lane(lane, root=tmp_path)


def test_build_serving_identity_embeds_checkpoint_lineage(tmp_path: Path) -> None:
    _write_required_lineage_files(tmp_path)
    spec_path = _write_registration_spec(tmp_path)
    register_llm_checkpoint(spec_path, root=tmp_path)

    lane = LlmModelLaneConfig(
        adapter="openai_compat_v1",
        provider="openai_compat",
        model="zomic-adapted-local-v1",
        api_base="http://localhost:8000",
        checkpoint_id="ckpt-al-cu-fe-zomic-adapted",
    )

    identity = build_serving_identity(
        requested_lane="general_purpose",
        resolved_lane="general_purpose",
        lane_source="configured_lane",
        backend=BackendConfig(mode="real"),
        lane_config=lane,
        root=tmp_path,
    )

    assert identity.checkpoint_id == "ckpt-al-cu-fe-zomic-adapted"
    assert identity.model_revision == "adapted-dev-2026-04-05"
    assert identity.checkpoint_lineage is not None
    assert identity.checkpoint_lineage.fingerprint
