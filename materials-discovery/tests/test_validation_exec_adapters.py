from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from materials_discovery.backends.execution_cache import cache_file_path
from materials_discovery.backends.registry import (
    resolve_committee_adapter,
    resolve_md_adapter,
    resolve_phonon_adapter,
    resolve_xrd_adapter,
)
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _candidate(candidate_id: str = "md_exec_001") -> CandidateRecord:
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
            "screen": {"energy_proxy_ev_per_atom": -2.95, "min_distance_proxy": 0.82},
            "digital_validation": {
                "status": "pending",
                "uncertainty_ev_per_atom": 0.015,
                "delta_e_proxy_hull_ev_per_atom": 0.02,
                "phonon_imaginary_modes": 0,
                "md_stability_score": 0.7,
            },
            "provenance": {"generator_version": "0.1.0"},
        }
    )


def _adapter_script(tmp_path: Path) -> Path:
    script = tmp_path / "validation_adapter.py"
    script.write_text(
        """
import json
import sys
from pathlib import Path

stage = sys.argv[1]
input_path = Path(sys.argv[2])
output_path = Path(sys.argv[3])
payload = json.loads(input_path.read_text(encoding="utf-8"))
candidate_id = payload["candidate"]["candidate_id"]

if stage == "committee":
    result = {"energies": {"MACE": -3.101, "CHGNet": -3.094, "MatterSim": -3.087}}
elif stage == "phonon":
    result = {"imaginary_modes": 1}
elif stage == "md":
    result = {"stability_score": 0.8125}
elif stage == "xrd":
    result = {"confidence": 0.774}
else:
    raise SystemExit(f"unknown stage: {stage}")

result["source_candidate_id"] = candidate_id
output_path.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
""".strip(),
        encoding="utf-8",
    )
    return script


def _exec_config(tmp_path: Path, script: Path) -> SystemConfig:
    return SystemConfig.model_validate(
        {
            "system_name": "Al-Cu-Fe",
            "template_family": "icosahedral_approximant_1_1",
            "species": ["Al", "Cu", "Fe"],
            "composition_bounds": {
                "Al": {"min": 0.60, "max": 0.80},
                "Cu": {"min": 0.10, "max": 0.25},
                "Fe": {"min": 0.05, "max": 0.20},
            },
            "coeff_bounds": {"min": -3, "max": 3},
            "seed": 17,
            "default_count": 100,
            "backend": {
                "mode": "real",
                "validation_cache_dir": str(tmp_path / "cache"),
                "committee_adapter": "committee_exec_cache_v1",
                "phonon_adapter": "phonon_exec_cache_v1",
                "md_adapter": "md_exec_cache_v1",
                "xrd_adapter": "xrd_exec_cache_v1",
                "committee_command": [
                    sys.executable,
                    str(script),
                    "committee",
                    "{input}",
                    "{output}",
                ],
                "phonon_command": [
                    sys.executable,
                    str(script),
                    "phonon",
                    "{input}",
                    "{output}",
                ],
                "md_command": [
                    sys.executable,
                    str(script),
                    "md",
                    "{input}",
                    "{output}",
                ],
                "xrd_command": [
                    sys.executable,
                    str(script),
                    "xrd",
                    "{input}",
                    "{output}",
                ],
                "versions": {"validation_backend": "exec-v1"},
            },
        }
    )


@pytest.mark.parametrize(
    ("stage", "resolver_name", "adapter_name", "command_field", "expected"),
    [
        (
            "committee",
            "committee",
            "committee_exec_cache_v1",
            "committee_command",
            {"energies": {"MACE": -3.101, "CHGNet": -3.094, "MatterSim": -3.087}},
        ),
        (
            "phonon",
            "phonon",
            "phonon_exec_cache_v1",
            "phonon_command",
            {"imaginary_modes": 1},
        ),
        (
            "md",
            "md",
            "md_exec_cache_v1",
            "md_command",
            {"stability_score": 0.8125},
        ),
        (
            "xrd",
            "xrd",
            "xrd_exec_cache_v1",
            "xrd_command",
            {"confidence": 0.774},
        ),
    ],
)
def test_exec_adapters_execute_then_reuse_cache(
    tmp_path: Path,
    stage: str,
    resolver_name: str,
    adapter_name: str,
    command_field: str,
    expected: dict[str, Any],
) -> None:
    script = _adapter_script(tmp_path)
    config = _exec_config(tmp_path, script)
    candidate = _candidate()

    resolver: Callable[[str, str | None], Any] = {
        "committee": resolve_committee_adapter,
        "phonon": resolve_phonon_adapter,
        "md": resolve_md_adapter,
        "xrd": resolve_xrd_adapter,
    }[resolver_name]
    adapter = resolver(config.backend.mode, adapter_name)
    result = adapter.evaluate_candidate(config, candidate)

    if stage == "committee":
        assert result.energies == expected["energies"]
    if stage == "phonon":
        assert result.imaginary_modes == expected["imaginary_modes"]
    if stage == "md":
        assert result.stability_score == expected["stability_score"]
    if stage == "xrd":
        assert result.confidence == expected["confidence"]

    cache_path = cache_file_path(config, stage=stage, candidate_id=candidate.candidate_id)
    assert cache_path.exists()
    cache_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache_payload["result"]["source_candidate_id"] == candidate.candidate_id

    cached_config = config.model_copy(deep=True)
    setattr(cached_config.backend, command_field, None)
    cached_adapter = resolver(cached_config.backend.mode, adapter_name)
    cached_result = cached_adapter.evaluate_candidate(cached_config, candidate)

    if stage == "committee":
        assert cached_result.energies == expected["energies"]
    if stage == "phonon":
        assert cached_result.imaginary_modes == expected["imaginary_modes"]
    if stage == "md":
        assert cached_result.stability_score == expected["stability_score"]
    if stage == "xrd":
        assert cached_result.confidence == expected["confidence"]


def test_exec_adapter_requires_command_or_cache(tmp_path: Path) -> None:
    script = _adapter_script(tmp_path)
    config = _exec_config(tmp_path, script)
    config.backend.committee_command = None

    adapter = resolve_committee_adapter(config.backend.mode, config.backend.committee_adapter)
    with pytest.raises(FileNotFoundError, match="backend.committee_command"):
        adapter.evaluate_candidate(config, _candidate("md_missing_cache"))
