from __future__ import annotations

import hashlib
from statistics import mean
from typing import Any

from materials_discovery.common.schema import CandidateRecord


def _qphi_complexity(candidate: CandidateRecord) -> float:
    coeffs: list[int] = []
    for site in candidate.sites:
        for pair in site.qphi:
            coeffs.extend(pair)
    return mean(abs(v) for v in coeffs)


def _dominant_fraction(candidate: CandidateRecord) -> float:
    return max(candidate.composition.values())


def simulate_powder_xrd_patterns(
    candidates: list[CandidateRecord],
    n_peaks: int = 12,
) -> list[dict[str, Any]]:
    """Create deterministic synthetic powder-XRD peak sets for ranked candidates."""
    patterns: list[dict[str, Any]] = []

    for candidate in candidates:
        digest = hashlib.sha256(f"{candidate.candidate_id}:xrd_pattern".encode()).hexdigest()
        seed = int(digest[:8], 16)

        complexity = _qphi_complexity(candidate)
        dominant_fraction = _dominant_fraction(candidate)

        raw_peaks: list[tuple[float, float]] = []
        for idx in range(n_peaks):
            angle_shift = ((seed >> (idx % 16)) % 120) / 100.0
            two_theta = 12.0 + idx * 5.6 + 0.35 * complexity + angle_shift

            intensity_base = 28.0 + ((seed >> ((idx + 3) % 16)) % 70)
            intensity = intensity_base + 14.0 * dominant_fraction - 1.8 * idx
            raw_peaks.append((two_theta, max(5.0, intensity)))

        max_intensity = max(intensity for _, intensity in raw_peaks)
        peaks = [
            {
                "two_theta": round(two_theta, 3),
                "intensity": round(100.0 * intensity / max_intensity, 3),
            }
            for two_theta, intensity in raw_peaks
        ]

        patterns.append(
            {
                "candidate_id": candidate.candidate_id,
                "peaks": peaks,
                "fingerprint": "-".join(f"{peak['two_theta']:.2f}" for peak in peaks[:4]),
            }
        )

    return patterns
