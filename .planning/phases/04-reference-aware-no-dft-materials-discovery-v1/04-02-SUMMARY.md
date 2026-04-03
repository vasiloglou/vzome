---
phase: 04-reference-aware-no-dft-materials-discovery-v1
plan: 02
subsystem: materials-discovery
tags:
  - benchmarking
  - provenance
  - comparability
  - pipeline-outputs
  - reference-packs
dependency_graph:
  requires:
    - 04-01
  provides:
    - benchmark_run_context
    - benchmark_pack_artifact
    - rank_provenance_with_context
    - report_provenance_with_context
  affects:
    - hifi_rank_manifests
    - report_manifests
    - artifact_manifests
tech_stack:
  added:
    - BenchmarkRunContext dataclass (common/benchmarking.py)
    - build_benchmark_run_context() assembly function
    - write_benchmark_pack() artifact writer
    - _load_benchmark_context() CLI helper
    - benchmark_context additive field on ArtifactManifest
  patterns:
    - Additive context threading (config + lineage -> context -> manifests + artifacts)
    - Single-owner context assembly in CLI, passed forward to downstream stages
    - Nullable/optional fields for backward-compatibility
key_files:
  created: []
  modified:
    - materials-discovery/src/materials_discovery/common/schema.py
    - materials-discovery/src/materials_discovery/common/benchmarking.py
    - materials-discovery/src/materials_discovery/common/manifest.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/src/materials_discovery/hifi_digital/rank_candidates.py
    - materials-discovery/src/materials_discovery/diffraction/compare_patterns.py
    - materials-discovery/tests/test_benchmarking.py
    - materials-discovery/tests/test_hifi_rank.py
    - materials-discovery/tests/test_report.py
decisions:
  - CLI assembles BenchmarkRunContext once from config + ingest manifest lineage and passes it forward; downstream stages do not reconstruct context independently
  - benchmark_context field on ArtifactManifest is nullable so existing manifest readers remain valid when context is absent
  - benchmark_pack.json is a high-level index referencing stage manifests/calibration JSONs rather than duplicating their content
  - calibration_provenance (source, benchmark_corpus, backend_mode) embedded in hifi_rank block unconditionally; benchmark_context embedded only when supplied
  - _extract_benchmark_context() reads context from ranked candidates so compare_patterns.py does not need direct config access
metrics:
  duration: 18 min
  completed: 2026-04-03
  tasks: 3
  files: 9
---

# Phase 4 Plan 02: Make Calibration, Ranking, And Report Outputs Comparable — Summary

## One-Liner

Additive benchmark/reference context threading from config+lineage through manifests, ranked-candidate provenance, and report payloads, plus a dedicated `benchmark_pack.json` artifact for cross-lane operator comparison.

## What Was Built

### Task 1 — Benchmark/Reference Context Model and Benchmark-Pack Artifact

**`common/benchmarking.py`**
- Added `BenchmarkRunContext` dataclass with fields: `reference_pack_id`, `reference_pack_fingerprint`, `source_keys`, `benchmark_corpus`, `backend_mode`, `lane_id` plus `as_dict()` serializer.
- Added `build_benchmark_run_context(config, source_lineage)` — assembles context from config (reference pack block, backend mode, benchmark corpus) enriched by optional ingest manifest source lineage (pack_id, pack_fingerprint, member_sources).
- Added `write_benchmark_pack(config, benchmark_context, stage_manifest_paths, report_metrics, output_path)` — writes `benchmark_pack.json` with schema_version, system, backend_mode, context dict, stage manifest references, and top-level report metrics.

**`common/schema.py`**
- Added `benchmark_context: dict[str, Any] | None = None` to `ArtifactManifest` — fully additive, backward-compatible.

**`common/manifest.py`**
- Added `benchmark_context` optional parameter to `build_manifest()`, threaded into the returned `ArtifactManifest`.

**`cli.py`**
- Added `_load_benchmark_context(config, system_slug)` — reads ingest manifest from disk (if present) to recover source lineage, then delegates to `build_benchmark_run_context`.
- `hifi-rank` command: assembles context, passes it to `rank_validated_candidates()`, threads it into the stage manifest.
- `report` command: assembles context, injects into report JSON payload, threads into report manifest, writes `benchmark_pack.json` with stage manifest references and top report metrics.

### Task 2 — Rank and Report Provenance

**`hifi_digital/rank_candidates.py`**
- `rank_validated_candidates()` now accepts optional `benchmark_context: dict | None = None`.
- Embeds `calibration_provenance` (source, benchmark_corpus, backend_mode) into every ranked candidate's `hifi_rank` provenance block unconditionally.
- Embeds `benchmark_context` when supplied.

**`diffraction/compare_patterns.py`**
- Added `_extract_benchmark_context(candidates)` — extracts benchmark_context from the first ranked candidate that carries one.
- `compile_experiment_report()` surfaces `calibration_provenance` and `benchmark_context` in each entry's `evidence` block.
- Adds top-level `benchmark_context` key to the report dict when candidates carry one.

### Task 3 — Regression Coverage

**`tests/test_benchmarking.py`** — `TestBuildBenchmarkRunContext` (8 new tests):
- Both Phase 4 benchmark systems (Al-Cu-Fe, Sc-Zn) produce valid contexts from config alone.
- Context dict contains all required keys.
- Pack lineage enriches fingerprint and source_keys.
- Cross-lane key alignment test: Al-Cu-Fe and Sc-Zn context dicts have identical key sets with distinct lane_ids.
- Benchmark corpus is recorded when configured.

**`tests/test_hifi_rank.py`** (3 new tests):
- `calibration_provenance` is always present in `hifi_rank` block.
- `benchmark_context` is embedded when supplied to `rank_validated_candidates()`.
- `benchmark_context` key is absent when not supplied.

**`tests/test_report.py`** (3 new tests):
- `compile_experiment_report()` surfaces `benchmark_context` and per-entry `calibration_provenance` when candidates carry context.
- `report` CLI command writes `benchmark_pack.json` with correct schema version, system, context, stage refs, and report metrics.
- Cross-lane comparison: Al-Cu-Fe baseline vs. real configs produce contexts with identical key sets.

## Verification

All four plan success criteria are met:

1. Manifests and summaries expose additive benchmark/reference context — `ArtifactManifest.benchmark_context` threaded into `hifi-rank` and `report` stage manifests.
2. A dedicated benchmark-pack output artifact exists — `{system_slug}_benchmark_pack.json` written by the `report` command.
3. Rank/report outputs expose pack/corpus/mode provenance — `calibration_provenance` in every ranked candidate's `hifi_rank` block; `benchmark_context` in report entries' evidence and at report top level.
4. Tests compare outputs across lanes — `test_cross_lane_benchmark_context_keys_match` and `TestBuildBenchmarkRunContext.test_cross_lane_context_keys_are_structurally_comparable` both pass.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. All context fields are wired from real config + lineage; no placeholder values flow to UI/report outputs.

## Self-Check: PASSED
- All 3 task commits exist: 2e2ca020, e2c895c5, 7e13f778
- 164 tests pass (`uv run pytest -x -q` in `materials-discovery/`)
- `benchmark_pack.json` is written by the report command (verified by `test_benchmark_pack_written_by_report_command`)
- Progress.md updated per CLAUDE.md requirement
