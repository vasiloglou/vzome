from __future__ import annotations

from statistics import mean
from typing import Any

from materials_discovery.common.chemistry import describe_candidate
from materials_discovery.common.schema import CandidateRecord

PHI = (1.0 + 5.0**0.5) / 2.0


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def _qphi_complexity(candidate: CandidateRecord) -> float:
    coeffs: list[int] = []
    for site in candidate.sites:
        for pair in site.qphi:
            coeffs.extend(pair)
    return mean(abs(v) for v in coeffs)


def _dominant_fraction(candidate: CandidateRecord) -> float:
    return max(candidate.composition.values())


def _cell_scale(candidate: CandidateRecord) -> float:
    axes = [float(candidate.cell.get(axis, 0.0)) for axis in ("a", "b", "c")]
    positive_axes = [axis for axis in axes if axis > 0.0]
    return mean(positive_axes) if positive_axes else 10.0


def _site_signature(candidate: CandidateRecord) -> list[float]:
    signatures: list[float] = []
    for site in candidate.sites:
        coeffs = [abs(first) + PHI * abs(second) for first, second in site.qphi]
        if not coeffs:
            continue
        signatures.append(round(float(site.occ) * mean(coeffs), 6))
    return signatures or [max(0.5, _qphi_complexity(candidate))]


def simulate_powder_xrd_patterns(
    candidates: list[CandidateRecord],
    n_peaks: int = 12,
) -> list[dict[str, Any]]:
    """Create deterministic chemistry-aware powder-XRD proxy peak sets for ranked candidates."""
    patterns: list[dict[str, Any]] = []

    for candidate in candidates:
        descriptor = describe_candidate(candidate, strict_pairs=False)
        complexity = descriptor.qphi_complexity
        dominant_fraction = _dominant_fraction(candidate)
        cell_scale = _cell_scale(candidate)
        site_signatures = _site_signature(candidate)
        scattering_power = descriptor.avg_atomic_number / 30.0
        mixing_preference = _clamp((-descriptor.pair_mixing_enthalpy_ev_per_atom) / 0.35, 0.0, 1.0)
        radius_penalty = _clamp(descriptor.radius_mismatch / 0.15, 0.0, 1.0)
        base_angle = (
            10.8
            + 0.18 * complexity
            + 0.05 * descriptor.avg_atomic_number
            + 0.02 * descriptor.vec
            + 12.0 / max(cell_scale, 6.0)
        )
        spacing = 4.1 - 0.02 * descriptor.avg_atomic_number + 0.08 * complexity

        raw_peaks: list[tuple[float, float]] = []
        for idx in range(n_peaks):
            family = idx + 1
            signature = site_signatures[idx % len(site_signatures)] + 0.14 * (
                idx // len(site_signatures)
            )
            two_theta = (
                base_angle
                + spacing * idx
                + 0.42 * signature
                + 0.08 * descriptor.electronegativity_spread * 10.0
                + 0.05 * dominant_fraction * family
            )

            intensity = (
                34.0
                + 24.0 * scattering_power
                + 16.0 * mixing_preference
                + 12.0 * dominant_fraction
                + 10.0 * signature
                + 4.0 * abs(((family + 1) % 5) - 2)
                - 10.0 * radius_penalty
                - 2.2 * idx
            )
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
                "fingerprint": "-".join(
                    f"{peak['two_theta']:.2f}:{peak['intensity']:.1f}" for peak in peaks[:4]
                ),
            }
        )

    return patterns
