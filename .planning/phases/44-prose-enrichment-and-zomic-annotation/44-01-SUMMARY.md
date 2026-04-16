---
phase: 44-prose-enrichment-and-zomic-annotation
plan: "01"
subsystem: visualization
tags: [labels, orbit-colors, wong-palette, leaf-module, tdd]
dependency_graph:
  requires: []
  provides: [visualization/labels.py, ORBIT_LABELS, ORBIT_COLORS, SHELL_NAMES, PREFERRED_SPECIES, DEFAULT_ORBIT_COLOR]
  affects: [Phase 45 plotly_3d.py, Phase 46 matplotlib_pub.py]
tech_stack:
  added: []
  patterns: [leaf-module, TDD, Wong-2011-colorblind-safe-palette]
key_files:
  created:
    - materials-discovery/src/materials_discovery/visualization/labels.py
    - materials-discovery/tests/test_labels.py
  modified:
    - materials-discovery/src/materials_discovery/visualization/__init__.py
    - materials-discovery/Progress.md
decisions:
  - "Used Wong (2011) 5-color subset (sky blue, orange, bluish green, vermilion, blue) keyed by anchor-library orbit names — black omitted for contrast per Wong 2011 guidance"
  - "labels.py is a pure leaf module with no intra-package imports, eliminating circular import risk for Phase 45/46 importers"
  - "PREFERRED_SPECIES mirrors sc_zn_tsai_bridge.yaml exactly to provide a single source of truth for orbit-to-species mapping"
metrics:
  duration: "~2 minutes"
  completed: "2026-04-15"
  tasks_completed: 2
  tasks_total: 2
  files_created: 2
  files_modified: 2
---

# Phase 44 Plan 01: Orbit Label Module (labels.py) Summary

**One-liner:** Colorblind-safe Wong (2011) orbit palette and human-readable label mappings in a leaf visualization module for Phase 45/46 downstream use.

## What Was Built

Created `materials-discovery/src/materials_discovery/visualization/labels.py` — a leaf module that provides five canonical symbols for all downstream visualization code:

- `ORBIT_LABELS`: Design-time orbit names (`pent`, `frustum`, `joint`) mapped to human-readable descriptions
- `SHELL_NAMES`: Anchor-library orbit names (`tsai_zn7`, `tsai_sc1`, `tsai_zn6`, `tsai_zn5`, `tsai_zn4`) mapped to physical shell descriptions
- `ORBIT_COLORS`: Wong (2011) colorblind-safe hex values keyed by anchor-library orbit names (black excluded per contrast rules)
- `PREFERRED_SPECIES`: Design-time orbit-to-species mapping mirroring `sc_zn_tsai_bridge.yaml`
- `DEFAULT_ORBIT_COLOR`: Fallback hex color for unlabeled orbits

Updated `visualization/__init__.py` to re-export all 5 symbols. Added 10 unit tests in `tests/test_labels.py` covering key sets, hex validity, no-black constraint, species consistency, init exports, and leaf-module enforcement.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create labels.py and test_labels.py with TDD | 11db1d6f | labels.py, test_labels.py |
| 2 | Update __init__.py exports and run full suite | f2f7664f | __init__.py, Progress.md |

## Verification Results

- `uv run pytest tests/test_labels.py -x -q` — 10 passed
- `uv run pytest tests/ -q --ignore=tests/test_llm_replay_core.py` — 595 passed, 3 skipped
- `python -c "from materials_discovery.visualization import ORBIT_COLORS, ORBIT_LABELS, SHELL_NAMES, PREFERRED_SPECIES, DEFAULT_ORBIT_COLOR; print('OK')"` — OK

## Deviations from Plan

### Pre-existing Test Failure (Out of Scope)

**Found during:** Task 2 full suite run
**Issue:** `test_build_replay_config_keeps_retired_checkpoint_replayable_by_fingerprint` in `test_llm_replay_core.py` fails with `ValueError: checkpoint_family 'adapted-al-cu-fe' has no promoted checkpoint for new execution`. This failure was confirmed pre-existing before any changes in this plan (verified via git stash).
**Action:** Logged here; not fixed. Out of scope per deviation rules (pre-existing failure in unrelated module).
**Deferred:** To `deferred-items.md` for future investigation.

No other deviations — plan executed as written.

## Known Stubs

None. All 5 exported symbols contain real data derived from sc_zn_tsai_bridge.yaml and the anchor-library JSON. No placeholder values.

## Self-Check: PASSED

- `materials-discovery/src/materials_discovery/visualization/labels.py` — FOUND
- `materials-discovery/tests/test_labels.py` — FOUND
- `materials-discovery/src/materials_discovery/visualization/__init__.py` — verified contains "from materials_discovery.visualization.labels import"
- Commit 11db1d6f — FOUND
- Commit f2f7664f — FOUND
