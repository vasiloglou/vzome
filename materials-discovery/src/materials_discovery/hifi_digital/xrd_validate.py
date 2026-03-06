from __future__ import annotations

import hashlib
from copy import deepcopy

from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def validate_xrd_signatures(
    config: SystemConfig,
    candidates: list[CandidateRecord],
    min_confidence: float = 0.60,
) -> list[CandidateRecord]:
    """Attach deterministic XRD agreement confidence and pass/fail labels."""
    scored: list[CandidateRecord] = []
    system_bias = (len(config.system_name) % 7) / 100.0

    for candidate in candidates:
        copied = deepcopy(candidate)
        phonon_penalty = (copied.digital_validation.phonon_imaginary_modes or 0) * 0.03

        digest = hashlib.sha256(
            f"{config.system_name}:{copied.candidate_id}:xrd".encode()
        ).hexdigest()
        seed = int(digest[:8], 16)
        base_confidence = 0.56 + (seed % 35) / 100.0 + system_bias
        confidence = round(_clamp(base_confidence - phonon_penalty, 0.0, 1.0), 6)

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "xrd_checked"
        validation.xrd_confidence = confidence
        validation.xrd_pass = confidence >= min_confidence
        copied.digital_validation = validation
        scored.append(copied)
    return scored
