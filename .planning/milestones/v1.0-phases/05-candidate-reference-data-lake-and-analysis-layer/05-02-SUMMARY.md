---
phase: 05-candidate-reference-data-lake-and-analysis-layer
plan: 02
subsystem: materials-discovery/lake
tags: [comparison, lake, benchmark, metrics, cli]
dependency_graph:
  requires:
    - 05-01  # lake catalog/index layer
    - 04-02  # benchmark-pack artifacts and write_benchmark_pack
  provides:
    - cross-lane comparison engine (compare_benchmark_packs, ComparisonResult)
    - mdisc lake compare CLI command
  affects:
    - cli.py (lake_app extended with compare command)
tech_stack:
  added:
    - statistics stdlib for distribution computation
  patterns:
    - Lane-centric comparison model (LaneSnapshot)
    - Pydantic v2 model serialization for dual-format output (D-06)
    - Benchmark-pack dereferencing via stage_manifest_paths
key_files:
  created:
    - materials-discovery/src/materials_discovery/lake/compare.py
    - materials-discovery/tests/test_lake_compare.py
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/Progress.md
decisions:
  - Lane-centric model: system-vs-system is a preset view; same model supports source-vs-source and backend-vs-backend comparisons (review concern #6)
  - Dereference benchmark-pack stage_manifest_paths["report"] to read deeper entry-level metrics for aggregate distributions (review concern #2)
  - Graceful fallback: missing report file emits UserWarning and falls back to report_metrics embedded in pack — no crash
  - Gate status uses four-value vocabulary (both_pass, both_fail, regression, improvement) for unambiguous operator reading
  - Comparison JSON written with model_dump_json for deterministic Pydantic v2 serialization
metrics:
  duration_minutes: 5
  completed_date: "2026-04-03"
  tasks_completed: 2
  files_created: 2
  files_modified: 2
  tests_added: 10
  tests_total: 197
---

# Phase 05 Plan 02: Cross-Lane Comparison Engine Summary

**One-liner:** Lane-centric comparison engine using LaneSnapshot that dereferences benchmark-pack report paths for 8-metric aggregate distributions, gate deltas, and dual-format CLI output via `mdisc lake compare`.

## What Was Built

### Task 1: Comparison engine with lane-centric model (TDD)

Created `materials-discovery/src/materials_discovery/lake/compare.py` with:

- `MetricDistribution` — Pydantic model for mean/min/max/std/count aggregate over report entries
- `LaneSnapshot` — Pydantic model loaded from a benchmark_pack.json; dereferences `stage_manifest_paths["report"]` to compute per-candidate distributions for 8 key metrics (hifi_score, stability_probability, ood_score, xrd_confidence, xrd_distinctiveness, delta_e_proxy_hull_ev_per_atom, uncertainty_ev_per_atom, md_stability_score); falls back to pack-embedded report_metrics if report file is missing
- `GateDelta` — gate pass/fail comparison with status vocabulary (both_pass, both_fail, regression, improvement)
- `MetricDelta` — distribution comparison with delta_mean = lane_b.mean - lane_a.mean
- `ComparisonResult` — full result with schema_version "comparison/v1" and generated_at_utc
- `compare_benchmark_packs(pack_a, pack_b, workspace)` — builds LaneSnapshot for each, computes gate and metric deltas
- `write_comparison(result, output_dir)` — writes JSON to data/comparisons/ with slugified filename (D-06)
- `format_comparison_table(result)` — multi-line terminal table with header, gate section, metric section (D-06)

### Task 2: Wire mdisc lake compare CLI command

Extended `materials-discovery/src/materials_discovery/cli.py`:

- Added `@lake_app.command("compare")` with:
  - `pack_a: Path` and `pack_b: Path` positional arguments (D-08)
  - `--output-dir` optional override for comparison output directory
  - `--json-only` flag to suppress CLI table output
- Validates both paths exist before running
- Produces dual-format output: JSON artifact + CLI table (D-06)

## Requirements Satisfied

- PIPE-04: Source-aware reference-phase enrichment comparison via lane_id, source_keys, and reference_pack_id in LaneSnapshot
- D-06: Dual-format output — JSON file in data/comparisons/ + terminal table
- D-07: Metric distributions for 8 key metrics across report entries
- D-08: Explicit benchmark-pack path inputs (no auto-discovery)
- Review concern #2: Comparison dereferences benchmark-pack pointers to read deeper report artifacts (entry-level metrics)
- Review concern #6: Lane-centric internal model — system-vs-system is just a preset view

## Test Coverage

Created `materials-discovery/tests/test_lake_compare.py` with 10 test functions:

| Class | Test | Behavior |
|-------|------|----------|
| TestLaneSnapshot | test_loads_from_benchmark_pack | Test 1: loads from benchmark-pack, dereferences report |
| TestLaneSnapshot | test_computes_metric_distributions | Test 2: aggregate distributions for 8 metrics |
| TestComparisonResult | test_gate_deltas | Test 3: gate delta status (regression, both_pass) |
| TestComparisonResult | test_metric_distribution_diffs | Test 4: delta_mean computation |
| TestComparisonResult | test_format_comparison_table | Test 5: readable multi-line table with system names |
| TestComparisonResult | test_comparison_result_serializes_to_json | Test 6: JSON serialization matches D-06 |
| TestComparisonResult | test_missing_report_falls_back_to_pack_metrics | Test 7: graceful fallback |
| TestWriteComparison | test_write_comparison_creates_file | write_comparison produces valid JSON file |
| TestCLIIntegration | test_cli_compare_command | CLI exits 0, output contains system names |
| TestCLIIntegration | test_cli_compare_json_only | --json-only writes JSON file |

All 10 new tests pass. Full suite: 197 tests passing (was 187).

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| RED  | 5dc5d0e0 | test(05-02): add failing tests for lake comparison engine |
| Task 1 GREEN | 591acd22 | feat(05-02): build lake comparison engine with lane-centric model |
| Task 2 | c123e9eb | feat(05-02): wire mdisc lake compare CLI command |

## Deviations from Plan

**1. [Rule 1 - Bug] Fixed test fixture directory creation**
- **Found during:** Task 1 GREEN phase
- **Issue:** `_write_pack(tmp_path / "a", ...)` failed with FileNotFoundError because the subdirectory `tmp_path / "a"` was not created before writing files.
- **Fix:** Added `tmp_path.mkdir(parents=True, exist_ok=True)` at the start of `_write_pack()`.
- **Files modified:** `materials-discovery/tests/test_lake_compare.py`
- **Commit:** 591acd22 (included in Task 1 GREEN commit)

No other deviations — plan executed as written.

## Known Stubs

None. All modeled data flows from real benchmark-pack and report JSON inputs. CLI produces complete output for any valid pack pair.

## Self-Check: PASSED

- `materials-discovery/src/materials_discovery/lake/compare.py` exists: FOUND
- `materials-discovery/tests/test_lake_compare.py` exists: FOUND
- Commits 5dc5d0e0, 591acd22, c123e9eb exist in git log: FOUND
- 197 tests pass: CONFIRMED
