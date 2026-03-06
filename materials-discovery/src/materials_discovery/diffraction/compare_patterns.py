from __future__ import annotations

from materials_discovery.common.schema import SystemConfig


def compile_experiment_report(config: SystemConfig) -> None:
    """Compile report bundle with simulated signatures and ranking outputs."""
    raise NotImplementedError(
        "Stage 'report' is interface-complete but not implemented; "
        "target function: "
        "materials_discovery.diffraction.compare_patterns.compile_experiment_report"
    )
