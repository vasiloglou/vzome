from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from materials_discovery.cli import (
    _resolve_campaign_lineage,
    app,
)
from materials_discovery.common.io import load_yaml, write_json_object, write_jsonl
from materials_discovery.common.pipeline_manifest import build_pipeline_manifest
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _workspace() -> Path:
    return Path(__file__).resolve().parents[1]


def _launched_candidate(candidate_id: str = "cand-001") -> CandidateRecord:
    return CandidateRecord.model_validate(
        {
            "candidate_id": candidate_id,
            "system": "Al-Cu-Fe",
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
                    "label": "S1",
                    "qphi": [[1, 0], [0, 1], [-1, 1]],
                    "species": "Al",
                    "occ": 1.0,
                }
            ],
            "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
            "screen": {
                "energy_proxy_ev_per_atom": -2.9,
                "min_distance_proxy": 2.4,
            },
            "digital_validation": {"status": "generated"},
            "provenance": {
                "source": "llm",
                "llm_campaign": {
                    "campaign_id": "campaign-001",
                    "launch_id": "launch-001",
                    "proposal_id": "proposal-001",
                    "approval_id": "approval-001",
                    "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
                },
            },
        }
    )


def test_resolve_campaign_lineage_prefers_candidate_provenance_and_enriches_from_manifest(
    monkeypatch,
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    system_slug = "al_cu_fe"
    manifest_path = workspace / "data" / "manifests" / f"{system_slug}_llm_generate_manifest.json"
    write_json_object(
        {
            "source_lineage": {
                "llm_campaign": {
                    "campaign_id": "campaign-001",
                    "launch_id": "launch-001",
                    "proposal_id": "proposal-001",
                    "approval_id": "approval-001",
                    "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
                    "launch_summary_path": (
                        "data/llm_campaigns/campaign-001/launches/launch-001/launch_summary.json"
                    ),
                    "resolved_launch_path": (
                        "data/llm_campaigns/campaign-001/launches/launch-001/resolved_launch.json"
                    ),
                    "resolved_model_lane": "general_purpose",
                    "resolved_model_lane_source": "configured_lane",
                }
            }
        },
        manifest_path,
    )
    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: workspace)

    lineage = _resolve_campaign_lineage(system_slug, [_launched_candidate()])

    assert lineage == {
        "llm_campaign": {
            "campaign_id": "campaign-001",
            "launch_id": "launch-001",
            "proposal_id": "proposal-001",
            "approval_id": "approval-001",
            "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
            "launch_summary_path": (
                "data/llm_campaigns/campaign-001/launches/launch-001/launch_summary.json"
            ),
            "resolved_launch_path": (
                "data/llm_campaigns/campaign-001/launches/launch-001/resolved_launch.json"
            ),
            "resolved_model_lane": "general_purpose",
            "resolved_model_lane_source": "configured_lane",
        }
    }
    assert "llm_campaign" not in lineage["llm_campaign"]


def test_screen_manifest_carries_normalized_campaign_lineage(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    workspace = tmp_path / "workspace"
    config_path = _workspace() / "configs" / "systems" / "al_cu_fe_llm_mock.yaml"
    config = SystemConfig.model_validate(load_yaml(config_path))
    system_slug = config.system_name.lower().replace("-", "_")

    candidates_path = workspace / "data" / "candidates" / f"{system_slug}_candidates.jsonl"
    write_jsonl([_launched_candidate().model_dump(mode="json")], candidates_path)
    write_json_object(
        {
            "source_lineage": {
                "llm_campaign": {
                    "campaign_id": "campaign-001",
                    "launch_id": "launch-001",
                    "proposal_id": "proposal-001",
                    "approval_id": "approval-001",
                    "campaign_spec_path": "data/llm_campaigns/campaign-001/campaign_spec.json",
                    "launch_summary_path": (
                        "data/llm_campaigns/campaign-001/launches/launch-001/launch_summary.json"
                    ),
                }
            }
        },
        workspace / "data" / "manifests" / f"{system_slug}_llm_generate_manifest.json",
    )

    monkeypatch.setattr("materials_discovery.cli.workspace_root", lambda: workspace)
    monkeypatch.setattr("materials_discovery.cli.run_fast_relaxation", lambda config, candidates: candidates)
    monkeypatch.setattr(
        "materials_discovery.cli.apply_screen_thresholds",
        lambda candidates, **kwargs: (candidates, []),
    )
    monkeypatch.setattr("materials_discovery.cli.rank_screen_shortlist", lambda candidates: candidates)

    result = runner.invoke(app, ["screen", "--config", str(config_path)])

    assert result.exit_code == 0
    summary = json.loads(result.stdout)
    manifest = json.loads(Path(summary["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["source_lineage"]["llm_campaign"]["campaign_id"] == "campaign-001"
    assert (
        manifest["source_lineage"]["llm_campaign"]["launch_summary_path"]
        == "data/llm_campaigns/campaign-001/launches/launch-001/launch_summary.json"
    )
    assert "llm_campaign" not in manifest["source_lineage"]["llm_campaign"]


def test_build_pipeline_manifest_accepts_campaign_source_lineage(tmp_path: Path) -> None:
    stage_path = tmp_path / "report.json"
    stage_path.write_text("{}", encoding="utf-8")
    config = SystemConfig.model_validate(load_yaml(_workspace() / "configs" / "systems" / "al_cu_fe.yaml"))

    manifest = build_pipeline_manifest(
        config=config,
        backend_mode=config.backend.mode,
        backend_versions={"pipeline": "builtin"},
        stage_paths={"report_json": stage_path},
        source_lineage={
            "llm_campaign": {
                "campaign_id": "campaign-001",
                "launch_id": "launch-001",
            }
        },
    )

    assert manifest.source_lineage == {
        "llm_campaign": {
            "campaign_id": "campaign-001",
            "launch_id": "launch-001",
        }
    }
