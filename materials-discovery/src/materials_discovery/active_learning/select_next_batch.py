from __future__ import annotations


def select_next_candidate_batch() -> None:
    """Select the next candidate batch with uncertainty-aware sampling."""
    raise NotImplementedError(
        "Stage 'active-learn' is interface-complete but not implemented; "
        "target function: "
        "materials_discovery.active_learning.select_next_batch.select_next_candidate_batch"
    )
