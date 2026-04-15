---
phase: 06-zomic-training-corpus-pipeline
plan: 02
subsystem: materials-discovery
tags: [llm, inventory, qa, dedupe, corpus, materials-discovery]
requires: [06-01]
provides:
  - deterministic inventory coverage for all required Phase 6 source families
  - typed gold/silver/reject grading with explainable duplicate handling
  - offline tests for inventory discovery, grading, and issue tallies
affects: [06-03, 06-04, LLM-01]
tech-stack:
  added: []
  patterns: [record-addressable inventory rows, loader-hint dispatch, pending-to-tier promotion, duplicate precedence]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/inventory.py
    - materials-discovery/src/materials_discovery/llm/qa.py
    - materials-discovery/tests/fixtures/pyqcstrc_projection_sample.json
    - materials-discovery/tests/test_llm_corpus_inventory.py
    - materials-discovery/tests/test_llm_corpus_qa.py
    - .planning/phases/06-zomic-training-corpus-pipeline/06-02-SUMMARY.md
  modified:
    - materials-discovery/src/materials_discovery/llm/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Keep inventory rows record-addressable with explicit loader hints so the builder can reopen exact source artifacts without re-globbing."
  - "Use pending -> gold/silver/reject promotion as a separate QA step instead of mixing release decisions into the converters."
  - "Make duplicate handling explainable by storing dropped-count metadata on the surviving example."
patterns-established:
  - "Inventory defaults to repo-root scanning while corpus artifacts continue to live under the materials-discovery workspace."
  - "QA precedence is deterministic: gold > silver > reject, then exact > anchored > approximate > heuristic."
requirements-completed: []
duration: 32min
completed: 2026-04-03
---

# Phase 6 Plan 02: Inventory And QA Layer Summary

**Deterministic source inventory, gold/silver/reject grading, and explainable dedupe for the Zomic corpus pipeline**

## Performance

- **Duration:** 32 min
- **Completed:** 2026-04-03
- **Tasks:** 2
- **Task commits:** 2

## Accomplishments

- Added `llm/inventory.py` covering repo regression scripts, part scripts,
  materials-design `.zomic` files, candidate JSONL rows, generated raw
  exports, canonical source rows, reference-pack rows, and the committed
  PyQCstrc projection payload.
- Added `llm/qa.py` with typed release-tier grading, orbit-label validation,
  duplicate precedence, and QA summary aggregation.
- Added focused tests proving the inventory stays offline and deterministic and
  that grading/dedupe logic remains explainable.

## Task Commits

1. **Task 1: Build source inventory for all required Phase 6 source families** - `9f6d8711` (`feat`)
2. **Task 2: Implement gold/silver/reject QA grading and dedupe** - `b2a4aaaa` (`feat`)

## Verification

- `cd materials-discovery && uv run pytest tests/test_llm_corpus_inventory.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_corpus_qa.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_corpus_inventory.py tests/test_llm_corpus_qa.py -x -v`

All verification commands passed before the next plan started.

## Deviations from Plan

### Auto-fixed Issues

**1. Materials-design system inference initially over-included descriptive filename tokens**

- **Found during:** `tests/test_llm_corpus_inventory.py`
- **Issue:** `sc_zn_tsai_bridge.zomic` initially inferred the system as `Sc-Zn-Tsai`, which caused the design row to be filtered out when the build config requested `Sc-Zn`.
- **Fix:** Tightened filename-based system inference to only consume leading element-like tokens.
- **Files modified:** `materials-discovery/src/materials_discovery/llm/inventory.py`, `materials-discovery/tests/test_llm_corpus_inventory.py`
- **Verification:** `cd materials-discovery && uv run pytest tests/test_llm_corpus_inventory.py -x -v`

---

**Total deviations:** 1 auto-fixed
**Impact on plan:** The fix aligned the inventory filter with the intended system-scoping contract and did not expand scope.

## Next Phase Readiness

- The converter layer can now trust the inventory contract instead of scanning
  the repo directly.
- The builder can later dispatch purely on `loader_hint` and `source_family`
  rather than re-inferring source type from paths or payloads.

## Self-Check: PASSED

- Verified commits `9f6d8711` and `b2a4aaaa` exist in git history.
- Verified focused inventory/QA test slices pass together.
