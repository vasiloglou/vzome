from __future__ import annotations

import hashlib
from copy import deepcopy

from materials_discovery.backends.registry import resolve_xrd_adapter
from materials_discovery.common.io import load_jsonl, workspace_root
from materials_discovery.common.schema import CandidateRecord, SystemConfig


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _system_slug(system_name: str) -> str:
    return system_name.lower().replace("-", "_")


def _load_reference_compositions(config: SystemConfig) -> list[dict[str, float]]:
    processed_path = (
        workspace_root()
        / "data"
        / "processed"
        / f"{_system_slug(config.system_name)}_reference_phases.jsonl"
    )
    if not processed_path.exists():
        raise FileNotFoundError(
            "real-mode XRD validation requires ingested reference phases; "
            f"run 'mdisc ingest' first: {processed_path}"
        )
    rows = load_jsonl(processed_path)
    compositions: list[dict[str, float]] = []
    for row in rows:
        composition = row.get("composition")
        if not isinstance(composition, dict):
            continue
        parsed: dict[str, float] = {}
        for symbol, frac in composition.items():
            if not isinstance(symbol, str) or not isinstance(frac, int | float):
                parsed = {}
                break
            parsed[symbol] = float(frac)
        if parsed:
            compositions.append(parsed)
    if not compositions:
        raise ValueError(
            "real-mode XRD validation found no usable reference compositions in "
            f"{processed_path}"
        )
    return compositions


def _validate_xrd_signatures_mock(
    config: SystemConfig,
    candidates: list[CandidateRecord],
    min_confidence: float,
) -> list[CandidateRecord]:
    """Legacy deterministic XRD confidence check for mock mode."""
    scored: list[CandidateRecord] = []
    system_bias = (len(config.system_name) % 7) / 100.0

    for candidate in candidates:
        copied = deepcopy(candidate)
        if copied.digital_validation.geometry_prefilter_pass is False:
            scored.append(copied)
            continue
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


def _validate_xrd_signatures_real(
    config: SystemConfig,
    candidates: list[CandidateRecord],
    min_confidence: float,
) -> list[CandidateRecord]:
    """Fixture-backed XRD confidence adapter for no-DFT real mode."""
    adapter = None
    scored: list[CandidateRecord] = []

    for candidate in candidates:
        copied = deepcopy(candidate)
        if copied.digital_validation.geometry_prefilter_pass is False:
            scored.append(copied)
            continue
        if adapter is None:
            adapter = resolve_xrd_adapter(config.backend.mode, config.backend.xrd_adapter)
        confidence = adapter.evaluate_candidate(config, copied).confidence

        validation = copied.digital_validation.model_copy(deep=True)
        validation.status = "xrd_checked"
        validation.xrd_confidence = confidence
        validation.xrd_pass = confidence >= min_confidence
        copied.digital_validation = validation
        scored.append(copied)

    return scored


def validate_xrd_signatures(
    config: SystemConfig,
    candidates: list[CandidateRecord],
    min_confidence: float = 0.60,
) -> list[CandidateRecord]:
    """Attach XRD agreement confidence and pass/fail labels."""
    if config.backend.mode == "real":
        return _validate_xrd_signatures_real(
            config=config,
            candidates=candidates,
            min_confidence=min_confidence,
        )
    return _validate_xrd_signatures_mock(
        config=config,
        candidates=candidates,
        min_confidence=min_confidence,
    )
