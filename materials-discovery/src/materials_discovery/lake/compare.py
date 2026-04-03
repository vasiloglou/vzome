"""Cross-lane comparison engine for benchmark packs.

Lane-centric model: A "lane" is any benchmark run uniquely identified by its
(reference_pack_id, backend_mode, source_keys) combination.  System-vs-system
comparison is just a preset view where two lanes happen to carry different
system names.  The same model supports future source-vs-source or
backend-vs-backend comparisons.

Addresses:
- PIPE-04: source-aware reference-phase enrichment comparison
- D-06: dual-format output (JSON file + CLI table)
- D-07: metric distributions (mean, min, max, std for 8 key metrics)
- D-08: explicit benchmark-pack path inputs (no auto-discovery)
- Review concern #2: dereference benchmark-pack pointers to read deeper report
- Review concern #6: lane-centric model
"""
from __future__ import annotations

import json
import logging
import re
import statistics
import warnings
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from materials_discovery.common.io import workspace_root
from materials_discovery.data_sources.storage import workspace_relative

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Metric names extracted from report entries
# ---------------------------------------------------------------------------

_ENTRY_METRICS: list[str] = [
    "hifi_score",
    "stability_probability",
    "ood_score",
    "xrd_confidence",
    "xrd_distinctiveness",
]

_EVIDENCE_METRICS: list[str] = [
    "delta_e_proxy_hull_ev_per_atom",
    "uncertainty_ev_per_atom",
    "md_stability_score",
]


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class MetricDistribution(BaseModel):
    """Aggregate distribution for a single metric across report entries."""

    mean: float
    min: float
    max: float
    std: float
    count: int


class LaneSnapshot(BaseModel):
    """Snapshot of one benchmark lane, with gate results and metric distributions.

    Loaded from a benchmark-pack JSON.  The report path is dereferenced to
    compute per-entry metric distributions.  If the report file is missing the
    model falls back to the summary metrics embedded in the pack itself.
    """

    system: str
    lane_id: str
    backend_mode: str
    source_keys: list[str]
    reference_pack_id: str | None
    gate_results: dict[str, bool]
    summary_metrics: dict[str, float]
    metric_distributions: dict[str, MetricDistribution]
    pack_path: str  # workspace-relative
    report_path: str | None  # workspace-relative, resolved from stage_manifest_paths

    @classmethod
    def from_benchmark_pack(cls, pack_path: Path, workspace: Path | None = None) -> "LaneSnapshot":
        """Load a LaneSnapshot from a benchmark_pack.json file.

        Parameters
        ----------
        pack_path:
            Path to the benchmark_pack.json file.
        workspace:
            Workspace root for computing workspace-relative paths.  Defaults
            to the project workspace root detected via workspace_root().
        """
        ws = workspace or workspace_root()

        data: dict[str, Any] = json.loads(pack_path.read_text(encoding="utf-8"))

        system: str = data.get("system", "unknown")
        backend_mode: str = data.get("backend_mode", "unknown")

        # Lane identity from benchmark_context
        ctx: dict[str, Any] = data.get("benchmark_context", {})
        lane_id: str = ctx.get("lane_id", f"{system.lower().replace('-', '_')}:{backend_mode}")
        reference_pack_id: str | None = ctx.get("reference_pack_id")
        source_keys: list[str] = ctx.get("source_keys", [])

        # Gate results and summary from report_metrics in pack
        report_metrics: dict[str, Any] = data.get("report_metrics", {})
        gate_results: dict[str, bool] = {
            k: bool(v)
            for k, v in report_metrics.get("release_gate", {}).items()
        }
        summary_raw: dict[str, Any] = report_metrics.get("summary", {})
        summary_metrics: dict[str, float] = {
            k: float(v)
            for k, v in summary_raw.items()
            if isinstance(v, (int, float))
        }

        # Dereference report path from stage_manifest_paths
        stage_paths: dict[str, str] = data.get("stage_manifest_paths", {})
        raw_report_path: str | None = stage_paths.get("report")

        metric_distributions: dict[str, MetricDistribution] = {}
        resolved_report_path: str | None = None

        if raw_report_path is not None:
            report_file = Path(raw_report_path)
            if not report_file.is_absolute():
                report_file = ws / report_file

            if report_file.exists():
                resolved_report_path = workspace_relative(report_file)
                report_data = json.loads(report_file.read_text(encoding="utf-8"))
                entries: list[dict[str, Any]] = report_data.get("entries", [])
                metric_distributions = _compute_distributions(entries)

                # Also update gate_results and summary from actual report if present
                rg = report_data.get("release_gate")
                if isinstance(rg, dict):
                    gate_results = {k: bool(v) for k, v in rg.items()}
                rs = report_data.get("summary")
                if isinstance(rs, dict):
                    summary_metrics = {
                        k: float(v)
                        for k, v in rs.items()
                        if isinstance(v, (int, float))
                    }
            else:
                warnings.warn(
                    f"Report file not found: {report_file}. "
                    f"Falling back to report_metrics from pack for {system}.",
                    stacklevel=2,
                )

        return cls(
            system=system,
            lane_id=lane_id,
            backend_mode=backend_mode,
            source_keys=source_keys,
            reference_pack_id=reference_pack_id,
            gate_results=gate_results,
            summary_metrics=summary_metrics,
            metric_distributions=metric_distributions,
            pack_path=workspace_relative(pack_path),
            report_path=resolved_report_path,
        )


class GateDelta(BaseModel):
    """Pass/fail comparison for one release gate across two lanes."""

    gate_name: str
    lane_a: bool
    lane_b: bool
    status: str  # "both_pass" | "both_fail" | "regression" | "improvement"


class MetricDelta(BaseModel):
    """Distribution comparison for one metric across two lanes."""

    metric_name: str
    lane_a: MetricDistribution | None
    lane_b: MetricDistribution | None
    delta_mean: float | None  # lane_b.mean - lane_a.mean


class ComparisonResult(BaseModel):
    """Full comparison result between two benchmark lanes.

    Serializes to JSON for D-06 dual-format output.
    """

    schema_version: str = "comparison/v1"
    generated_at_utc: str
    lane_a: LaneSnapshot
    lane_b: LaneSnapshot
    gate_deltas: list[GateDelta]
    metric_deltas: list[MetricDelta]


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def compare_benchmark_packs(
    pack_a: Path,
    pack_b: Path,
    workspace: Path | None = None,
) -> ComparisonResult:
    """Compare two benchmark packs and produce a ComparisonResult.

    Parameters
    ----------
    pack_a:
        Path to the first benchmark_pack.json.
    pack_b:
        Path to the second benchmark_pack.json.
    workspace:
        Workspace root for workspace-relative path resolution.
    """
    ws = workspace or workspace_root()

    snap_a = LaneSnapshot.from_benchmark_pack(pack_a, workspace=ws)
    snap_b = LaneSnapshot.from_benchmark_pack(pack_b, workspace=ws)

    gate_deltas = _compute_gate_deltas(snap_a, snap_b)
    metric_deltas = _compute_metric_deltas(snap_a, snap_b)

    return ComparisonResult(
        generated_at_utc=datetime.now(UTC).isoformat(),
        lane_a=snap_a,
        lane_b=snap_b,
        gate_deltas=gate_deltas,
        metric_deltas=metric_deltas,
    )


def write_comparison(
    result: ComparisonResult,
    output_dir: Path | None = None,
) -> Path:
    """Write a ComparisonResult as JSON to output_dir.

    Default output directory: workspace_root() / "data" / "comparisons".
    Filename: ``{lane_a.system}_vs_{lane_b.system}.json`` (slugified).

    Parameters
    ----------
    result:
        The comparison result to write.
    output_dir:
        Override the default output directory.

    Returns
    -------
    Path to the written file.
    """
    if output_dir is None:
        output_dir = workspace_root() / "data" / "comparisons"

    output_dir.mkdir(parents=True, exist_ok=True)

    slug_a = _slugify(result.lane_a.system)
    slug_b = _slugify(result.lane_b.system)
    filename = f"{slug_a}_vs_{slug_b}.json"
    out_path = output_dir / filename

    out_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return out_path


def format_comparison_table(result: ComparisonResult) -> str:
    """Format a ComparisonResult as a human-readable terminal table.

    Produces:
    - Header with both lane system names and lane IDs
    - Gate section with pass/fail status
    - Metric section with mean, delta, and std for each metric

    Parameters
    ----------
    result:
        The comparison result to format.

    Returns
    -------
    Multi-line string suitable for terminal output.
    """
    lines: list[str] = []

    # --- Header ---
    lines.append("=" * 72)
    lines.append(
        f"Lane A: {result.lane_a.system} ({result.lane_a.lane_id})"
    )
    lines.append(
        f"Lane B: {result.lane_b.system} ({result.lane_b.lane_id})"
    )
    lines.append(f"Generated: {result.generated_at_utc}")
    lines.append("=" * 72)

    # --- Gate section ---
    lines.append("")
    lines.append("GATE RESULTS")
    lines.append("-" * 72)
    lines.append(f"{'Gate':<40} {'Lane A':<10} {'Lane B':<10} {'Status'}")
    lines.append("-" * 72)
    for gd in result.gate_deltas:
        a_str = "PASS" if gd.lane_a else "FAIL"
        b_str = "PASS" if gd.lane_b else "FAIL"
        status_map = {
            "both_pass": "ok",
            "both_fail": "fail",
            "regression": "REGRESSION",
            "improvement": "IMPROVEMENT",
        }
        status_display = status_map.get(gd.status, gd.status)
        lines.append(f"{gd.gate_name:<40} {a_str:<10} {b_str:<10} {status_display}")

    # --- Metric section ---
    lines.append("")
    lines.append("METRIC DISTRIBUTIONS")
    lines.append("-" * 72)
    lines.append(
        f"{'Metric':<40} {'Mean A':>8} {'Mean B':>8} {'Delta':>8} {'Std A':>8} {'Std B':>8}"
    )
    lines.append("-" * 72)
    for md in result.metric_deltas:
        mean_a = f"{md.lane_a.mean:.4f}" if md.lane_a is not None else "N/A"
        mean_b = f"{md.lane_b.mean:.4f}" if md.lane_b is not None else "N/A"
        delta = f"{md.delta_mean:+.4f}" if md.delta_mean is not None else "N/A"
        std_a = f"{md.lane_a.std:.4f}" if md.lane_a is not None else "N/A"
        std_b = f"{md.lane_b.std:.4f}" if md.lane_b is not None else "N/A"
        lines.append(
            f"{md.metric_name:<40} {mean_a:>8} {mean_b:>8} {delta:>8} {std_a:>8} {std_b:>8}"
        )

    lines.append("=" * 72)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _compute_distributions(entries: list[dict[str, Any]]) -> dict[str, MetricDistribution]:
    """Compute MetricDistribution for each metric across report entries."""
    buckets: dict[str, list[float]] = {m: [] for m in _ENTRY_METRICS + _EVIDENCE_METRICS}

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for metric in _ENTRY_METRICS:
            val = entry.get(metric)
            if isinstance(val, (int, float)):
                buckets[metric].append(float(val))

        evidence = entry.get("evidence", {})
        if isinstance(evidence, dict):
            for metric in _EVIDENCE_METRICS:
                val = evidence.get(metric)
                if isinstance(val, (int, float)):
                    buckets[metric].append(float(val))

    distributions: dict[str, MetricDistribution] = {}
    for metric, values in buckets.items():
        if not values:
            continue
        distributions[metric] = MetricDistribution(
            mean=statistics.mean(values),
            min=min(values),
            max=max(values),
            std=statistics.stdev(values) if len(values) > 1 else 0.0,
            count=len(values),
        )
    return distributions


def _compute_gate_deltas(snap_a: LaneSnapshot, snap_b: LaneSnapshot) -> list[GateDelta]:
    """Compute gate deltas between two lane snapshots."""
    all_gates = sorted(
        set(snap_a.gate_results.keys()) | set(snap_b.gate_results.keys())
    )
    deltas: list[GateDelta] = []
    for gate in all_gates:
        a_val = snap_a.gate_results.get(gate, False)
        b_val = snap_b.gate_results.get(gate, False)
        if a_val and b_val:
            status = "both_pass"
        elif not a_val and not b_val:
            status = "both_fail"
        elif a_val and not b_val:
            status = "regression"
        else:
            status = "improvement"
        deltas.append(
            GateDelta(gate_name=gate, lane_a=a_val, lane_b=b_val, status=status)
        )
    return deltas


def _compute_metric_deltas(snap_a: LaneSnapshot, snap_b: LaneSnapshot) -> list[MetricDelta]:
    """Compute metric distribution deltas between two lane snapshots."""
    all_metrics = sorted(
        set(snap_a.metric_distributions.keys()) | set(snap_b.metric_distributions.keys())
    )
    deltas: list[MetricDelta] = []
    for metric in all_metrics:
        dist_a = snap_a.metric_distributions.get(metric)
        dist_b = snap_b.metric_distributions.get(metric)
        delta_mean: float | None = None
        if dist_a is not None and dist_b is not None:
            delta_mean = dist_b.mean - dist_a.mean
        deltas.append(
            MetricDelta(
                metric_name=metric,
                lane_a=dist_a,
                lane_b=dist_b,
                delta_mean=delta_mean,
            )
        )
    return deltas


def _slugify(text: str) -> str:
    """Convert a system name to a URL/filename-safe slug."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
