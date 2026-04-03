---
phase: 05-candidate-reference-data-lake-and-analysis-layer
plan: 03
subsystem: materials-discovery/notebooks, materials-discovery/RUNBOOK.md, materials-discovery/tests
tags: [notebooks, analytics, runbook, documentation, smoke-tests]
dependency_graph:
  requires: ["05-01", "05-02"]
  provides: ["analytics-notebooks", "operator-runbook", "notebook-smoke-tests"]
  affects: ["materials-discovery/notebooks", "materials-discovery/RUNBOOK.md", "materials-discovery/tests"]
tech_stack:
  added: [nbformat, nbconvert (optional), matplotlib, numpy]
  patterns:
    - Jupyter notebooks with configurable top cell and graceful missing-data degradation
    - pytest.mark.skipif for optional-dependency tests rather than module-level importorskip
    - workspace_root() as canonical data path root in all notebooks
    - Smoke test workspace injection via unittest.mock.patch for isolated notebook execution
key_files:
  created:
    - materials-discovery/notebooks/source_contribution_analysis.ipynb
    - materials-discovery/notebooks/cross_run_drift_detection.ipynb
    - materials-discovery/notebooks/metric_distribution_deep_dive.ipynb
    - materials-discovery/RUNBOOK.md
    - materials-discovery/tests/test_notebooks.py
  modified:
    - materials-discovery/Progress.md
decisions:
  - "Static notebook tests (JSON validity, imports, workspace_root) separated from execution tests so they always run even without nbformat/nbconvert installed"
  - "Notebook execution smoke tests use pytest.mark.skipif rather than module-level importorskip to allow static tests to run in any environment"
  - "workspace_root() override injected as a synthetic first cell via nbformat.v4.new_code_cell() rather than patching at the OS level"
  - "RUNBOOK.md placed at materials-discovery root (per D-13 high visibility); does not duplicate developer-docs content but references it for deep-dive context"
metrics:
  duration: "~8 minutes"
  completed_date: "2026-04-03"
  tasks: 2 (+ 1 checkpoint)
  files: 6
---

# Phase 05 Plan 03: Starter Analytics Notebooks and Operator RUNBOOK Summary

Three analytics notebooks, a unified operator runbook, and notebook smoke tests for the materials discovery platform.

## What Was Built

### Task 1: Three Starter Analytics Notebooks + Smoke Test

**Notebooks** (`materials-discovery/notebooks/`):

1. **source_contribution_analysis.ipynb** — loads a report JSON, groups candidates by
   ingestion source (via `benchmark_context.source_keys` or `evidence.calibration_provenance`),
   renders a priority-breakdown bar chart (high/medium/watch), a top-N candidate table with
   hifi_score and xrd_confidence, and a text summary. Addresses D-11.

2. **cross_run_drift_detection.ipynb** — loads two `benchmark_pack.json` files as
   `LaneSnapshot` objects using `lake.compare`, runs `compare_benchmark_packs()`, renders
   a gate pass/fail comparison bar chart with regression/improvement annotations, side-by-side
   metric distribution bars with error bars, and a delta interpretation table. Addresses D-11.

3. **metric_distribution_deep_dive.ipynb** — loads one or more report JSONs (overlay mode),
   renders histograms for hifi_score/stability_probability/ood_score, a scatter plot of
   xrd_confidence vs xrd_distinctiveness, and a summary statistics table. Supports multi-report
   overlay for cross-run comparison. Addresses D-11.

All three notebooks:
- Use `workspace_root()` for data path construction (CLI-consistent, per D-09)
- Have a dedicated **CONFIGURATION** cell at the top with all editable parameters
- Degrade gracefully when data files are missing (print informative message, skip plots)
- Import from `materials_discovery.lake` and `materials_discovery.common.io`

**Smoke test** (`materials-discovery/tests/test_notebooks.py`):
- 6 tests total: 3 static (always run) + 3 execution (skip when nbformat/nbconvert absent)
- Static tests: valid .ipynb JSON, `from materials_discovery` import present, `workspace_root` used
- Execution tests: inject synthetic workspace override cell, run via `ExecutePreprocessor`,
  verify no `CellExecutionError`
- Addresses review concern #4 (notebook maintainability)

### Task 2: Unified Operator RUNBOOK.md

**`materials-discovery/RUNBOOK.md`** (at workspace root per D-13):

8 major sections:
1. Prerequisites (Python env, API keys, Java for Sc-Zn)
2. Ingestion (single source + reference-pack)
3. Reference Pack Assembly (when to assemble vs. reuse, config structure)
4. Pipeline Execution (all 6 stages with exact commands)
5. Benchmarking (full suite runner + artifact structure)
6. Data Lake Operations (lake index, stats, compare with examples)
7. Analytics Notebooks (launch instructions + parameter guide for each notebook)
8. Quick Reference (command table, key file paths, config locations, see-also links)

Metrics: 53 code blocks, 38 `mdisc` occurrences, 5 troubleshooting sub-sections.

Each troubleshooting entry: Symptom + Cause + Resolution with commands (D-15).
Every section has copy-pasteable command blocks (D-14).
RUNBOOK is the single operator source of truth (addresses review suggestion from 05-CONTEXT).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Separated static tests from execution tests**
- **Found during:** Task 1 verification
- **Issue:** Original implementation used module-level `pytest.importorskip("nbformat")` which
  caused the entire module to be skipped when nbformat was absent — including the 3 structural
  tests that don't need nbformat at all.
- **Fix:** Replaced module-level importorskip with a try/except import block and
  `pytest.mark.skipif` applied only to the execution tests. Static tests now always run.
- **Files modified:** `materials-discovery/tests/test_notebooks.py`
- **Commit:** included in 8e11121b

## Known Stubs

None. All notebooks load real pipeline data via `workspace_root()` and provide
informative messages when data is absent rather than rendering placeholder values.

## Test Results

| Suite | Result |
|---|---|
| Full test suite (197 tests, excluding notebook execution) | PASSED |
| Notebook static tests (3 tests) | PASSED |
| Notebook execution smoke tests | SKIPPED (nbformat/nbconvert not installed in CI) |

## Self-Check: PASSED

All created files verified present on disk. Task commits verified in git log:
- `8e11121b` — feat(05-03): three analytics notebooks and smoke tests
- `663dfacc` — feat(05-03): unified operator RUNBOOK.md
