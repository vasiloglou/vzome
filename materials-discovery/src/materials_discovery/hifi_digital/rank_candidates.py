from __future__ import annotations

from materials_discovery.common.schema import SystemConfig


def rank_validated_candidates(config: SystemConfig) -> None:
    """Rank candidates after hifi validation with uncertainty-aware scoring."""
    raise NotImplementedError(
        "Stage 'hifi-rank' is interface-complete but not implemented; "
        "target function: "
        "materials_discovery.hifi_digital.rank_candidates.rank_validated_candidates"
    )
