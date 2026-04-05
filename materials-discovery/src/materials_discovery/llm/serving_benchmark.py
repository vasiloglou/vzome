from __future__ import annotations

from pathlib import Path

from materials_discovery.common.io import load_json_object, load_yaml
from materials_discovery.common.schema import SystemConfig
from materials_discovery.llm.schema import LlmAcceptancePack, LlmServingBenchmarkSpec


def _resolve_spec_relative_path(spec_path: Path, candidate: str) -> Path:
    path = Path(candidate)
    if path.is_absolute():
        return path
    return (spec_path.parent / path).resolve()


def load_serving_benchmark_spec(spec_path: Path) -> LlmServingBenchmarkSpec:
    raw_spec = load_yaml(spec_path)
    spec = LlmServingBenchmarkSpec.model_validate(raw_spec)

    acceptance_pack_file = _resolve_spec_relative_path(spec_path, spec.acceptance_pack_path)
    acceptance_pack = LlmAcceptancePack.model_validate(load_json_object(acceptance_pack_file))
    acceptance_systems = {system_metrics.system for system_metrics in acceptance_pack.systems}
    if not acceptance_systems:
        raise ValueError("shared acceptance-pack context must include at least one system")

    for target in spec.targets:
        system_config_file = _resolve_spec_relative_path(spec_path, target.system_config_path)
        system_config = SystemConfig.model_validate(load_yaml(system_config_file))
        if system_config.system_name not in acceptance_systems:
            raise ValueError(
                "benchmark targets must stay within the shared acceptance-pack context"
            )

    return spec.model_copy(
        update={
            "acceptance_pack_path": str(acceptance_pack_file),
            "targets": [
                target.model_copy(
                    update={
                        "system_config_path": str(
                            _resolve_spec_relative_path(spec_path, target.system_config_path)
                        ),
                        "campaign_spec_path": (
                            str(_resolve_spec_relative_path(spec_path, target.campaign_spec_path))
                            if target.campaign_spec_path is not None
                            else None
                        ),
                    }
                )
                for target in spec.targets
            ],
        }
    )
