from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from materials_discovery.common.schema import BackendConfig, LlmModelLaneConfig
from materials_discovery.llm.checkpoints import (
    load_registered_checkpoint,
    register_llm_checkpoint,
    resolve_checkpoint_lane,
)
from materials_discovery.llm.launch import build_serving_identity


def _write_required_lineage_files(root: Path) -> None:
    (root / "lineage").mkdir(parents=True, exist_ok=True)
    (root / "lineage" / "adapter_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "corpus_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "eval_manifest.json").write_text("{}", encoding="utf-8")
    (root / "lineage" / "acceptance_pack.json").write_text("{}", encoding="utf-8")


def _write_registration_spec(root: Path, *, model: str = "zomic-adapted-local-v1") -> Path:
    spec = {
        "checkpoint_id": "ckpt-al-cu-fe-zomic-adapted",
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
    spec_path = root / "checkpoint.yaml"
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
