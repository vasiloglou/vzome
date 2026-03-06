from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from materials_discovery.backends.execution_cache import (
    candidate_input_digest,
    load_cached_result,
    write_cached_result,
)
from materials_discovery.backends.types import (
    AdapterInfo,
    CommitteeEvaluation,
    MdEvaluation,
    PhononEvaluation,
    XrdEvaluation,
)
from materials_discovery.common.io import workspace_root
from materials_discovery.common.schema import CandidateRecord, SystemConfig


@dataclass(frozen=True)
class ExecAdapterSpec:
    stage: str
    adapter_name: str
    command_field: str


def _input_payload(
    *,
    stage: str,
    adapter_name: str,
    config: SystemConfig,
    candidate: CandidateRecord,
) -> dict[str, Any]:
    return {
        "stage": stage,
        "adapter_name": adapter_name,
        "system": config.system_name,
        "template_family": config.template_family,
        "backend_mode": config.backend.mode,
        "config": config.model_dump(mode="json"),
        "candidate": candidate.model_dump(mode="json"),
    }


def _render_command(command: list[str], context: dict[str, str]) -> list[str]:
    rendered: list[str] = []
    for token in command:
        rendered.append(token.format_map(context))
    return rendered


def _command_for_spec(config: SystemConfig, spec: ExecAdapterSpec) -> list[str] | None:
    command = getattr(config.backend, spec.command_field)
    if command is None:
        return None
    if not command:
        raise ValueError(
            f"backend.{spec.command_field} must be a non-empty command list when configured"
        )
    return list(command)


def _run_external_command(
    *,
    config: SystemConfig,
    candidate: CandidateRecord,
    spec: ExecAdapterSpec,
    command: list[str],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"mdisc_{spec.stage}_") as temp_dir:
        input_path = Path(temp_dir) / "input.json"
        output_path = Path(temp_dir) / "output.json"
        payload = _input_payload(
            stage=spec.stage,
            adapter_name=spec.adapter_name,
            config=config,
            candidate=candidate,
        )
        input_path.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")

        rendered_command = _render_command(
            command,
            {
                "input": str(input_path),
                "output": str(output_path),
                "stage": spec.stage,
                "system": config.system_name,
                "candidate_id": candidate.candidate_id,
                "python": sys.executable,
                "workspace_root": str(workspace_root()),
            },
        )
        completed = subprocess.run(
            rendered_command,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip()
            stdout = completed.stdout.strip()
            details = stderr or stdout or "no stderr/stdout captured"
            raise ValueError(
                f"{spec.stage} adapter command failed for {candidate.candidate_id} "
                f"(exit {completed.returncode}): {details}"
            )
        if not output_path.exists():
            raise FileNotFoundError(
                f"{spec.stage} adapter command did not create output JSON for "
                f"{candidate.candidate_id}: {output_path}"
            )
        with output_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"{spec.stage} adapter output must be a JSON object: {output_path}")
        return payload


def _execute_with_cache(
    *,
    config: SystemConfig,
    candidate: CandidateRecord,
    spec: ExecAdapterSpec,
) -> dict[str, Any]:
    command = _command_for_spec(config, spec)
    input_digest = candidate_input_digest(
        stage=spec.stage,
        adapter_name=spec.adapter_name,
        config=config,
        candidate=candidate,
        command=command,
    )
    cached = load_cached_result(
        config,
        stage=spec.stage,
        candidate_id=candidate.candidate_id,
        input_digest=input_digest,
    )
    if cached is not None:
        return cached

    if command is None:
        raise FileNotFoundError(
            f"real-mode {spec.stage} adapter '{spec.adapter_name}' has no cache hit for "
            f"{candidate.candidate_id} and backend.{spec.command_field} is not configured"
        )

    payload = _run_external_command(config=config, candidate=candidate, spec=spec, command=command)
    write_cached_result(
        config,
        stage=spec.stage,
        candidate_id=candidate.candidate_id,
        input_digest=input_digest,
        adapter_name=spec.adapter_name,
        command=command,
        result=payload,
    )
    return payload


def _parse_committee_result(payload: dict[str, Any]) -> CommitteeEvaluation:
    energies_raw = payload.get("energies", payload.get("committee_energy_ev_per_atom"))
    if not isinstance(energies_raw, dict):
        raise ValueError("committee adapter output must define 'energies'")

    energies: dict[str, float] = {}
    for model, value in energies_raw.items():
        if not isinstance(model, str) or not isinstance(value, int | float):
            raise ValueError(
                "committee adapter output must use string model names and numeric values"
            )
        energies[model] = round(float(value), 6)
    if len(energies) < 2:
        raise ValueError("committee adapter output must contain at least two model energies")
    return CommitteeEvaluation(energies=energies)


def _parse_phonon_result(payload: dict[str, Any]) -> PhononEvaluation:
    value = payload.get("imaginary_modes", payload.get("phonon_imaginary_modes"))
    if not isinstance(value, int):
        raise ValueError("phonon adapter output must define integer 'imaginary_modes'")
    return PhononEvaluation(imaginary_modes=int(value))


def _parse_md_result(payload: dict[str, Any]) -> MdEvaluation:
    value = payload.get("stability_score", payload.get("md_stability_score"))
    if not isinstance(value, int | float):
        raise ValueError("md adapter output must define numeric 'stability_score'")
    return MdEvaluation(stability_score=round(float(value), 6))


def _parse_xrd_result(payload: dict[str, Any]) -> XrdEvaluation:
    value = payload.get("confidence", payload.get("xrd_confidence"))
    if not isinstance(value, int | float):
        raise ValueError("xrd adapter output must define numeric 'confidence'")
    return XrdEvaluation(confidence=round(float(value), 6))


class ExecCommitteeAdapter:
    _spec = ExecAdapterSpec(
        stage="committee",
        adapter_name="committee_exec_cache_v1",
        command_field="committee_command",
    )

    def info(self) -> AdapterInfo:
        return AdapterInfo(name=self._spec.adapter_name, version="2026.03.06+exec-cache-v1")

    def evaluate_candidate(
        self,
        config: SystemConfig,
        candidate: CandidateRecord,
    ) -> CommitteeEvaluation:
        payload = _execute_with_cache(config=config, candidate=candidate, spec=self._spec)
        return _parse_committee_result(payload)


class ExecPhononAdapter:
    _spec = ExecAdapterSpec(
        stage="phonon",
        adapter_name="phonon_exec_cache_v1",
        command_field="phonon_command",
    )

    def info(self) -> AdapterInfo:
        return AdapterInfo(name=self._spec.adapter_name, version="2026.03.06+exec-cache-v1")

    def evaluate_candidate(
        self,
        config: SystemConfig,
        candidate: CandidateRecord,
    ) -> PhononEvaluation:
        payload = _execute_with_cache(config=config, candidate=candidate, spec=self._spec)
        return _parse_phonon_result(payload)


class ExecMdAdapter:
    _spec = ExecAdapterSpec(
        stage="md",
        adapter_name="md_exec_cache_v1",
        command_field="md_command",
    )

    def info(self) -> AdapterInfo:
        return AdapterInfo(name=self._spec.adapter_name, version="2026.03.06+exec-cache-v1")

    def evaluate_candidate(self, config: SystemConfig, candidate: CandidateRecord) -> MdEvaluation:
        payload = _execute_with_cache(config=config, candidate=candidate, spec=self._spec)
        return _parse_md_result(payload)


class ExecXrdAdapter:
    _spec = ExecAdapterSpec(
        stage="xrd",
        adapter_name="xrd_exec_cache_v1",
        command_field="xrd_command",
    )

    def info(self) -> AdapterInfo:
        return AdapterInfo(name=self._spec.adapter_name, version="2026.03.06+exec-cache-v1")

    def evaluate_candidate(self, config: SystemConfig, candidate: CandidateRecord) -> XrdEvaluation:
        payload = _execute_with_cache(config=config, candidate=candidate, spec=self._spec)
        return _parse_xrd_result(payload)
