from __future__ import annotations

from materials_discovery.common.schema import SystemConfig


def run_fast_relaxation(config: SystemConfig) -> None:
    """Run fast model-based relaxation for shortlisted candidates."""
    raise NotImplementedError(
        "Stage 'screen' is interface-complete but not implemented; "
        "target function: materials_discovery.screen.relax_fast.run_fast_relaxation"
    )
