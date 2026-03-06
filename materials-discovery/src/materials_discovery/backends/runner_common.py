from __future__ import annotations

import argparse
import json
from pathlib import Path

from materials_discovery.common.schema import CandidateRecord, SystemConfig


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def load_runner_inputs(input_path: Path) -> tuple[SystemConfig, CandidateRecord]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"runner input must be a JSON object: {input_path}")

    config_payload = payload.get("config")
    candidate_payload = payload.get("candidate")
    if not isinstance(config_payload, dict):
        raise ValueError(f"runner input missing config payload: {input_path}")
    if not isinstance(candidate_payload, dict):
        raise ValueError(f"runner input missing candidate payload: {input_path}")

    config = SystemConfig.model_validate(config_payload)
    candidate = CandidateRecord.model_validate(candidate_payload)
    return config, candidate


def write_runner_output(output_path: Path, payload: dict[str, object]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
