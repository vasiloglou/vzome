from __future__ import annotations

from materials_discovery.common.schema import SystemConfig


def train_surrogate_model(config: SystemConfig) -> None:
    """Train or refresh the surrogate model from available labels."""
    raise NotImplementedError(
        "Stage 'active-learn' is interface-complete but not implemented; "
        "target function: materials_discovery.active_learning.train_surrogate.train_surrogate_model"
    )
