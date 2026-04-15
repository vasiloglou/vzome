---
phase: 06-zomic-training-corpus-pipeline
plan: 04
subsystem: materials-discovery
tags: [llm, corpus-builder, cif, native-zomic, generated-export, cli, materials-discovery]
requires: [06-02, 06-03]
provides:
  - CIF/open-approximant conversion plus composition-only canonical fallback
  - exact-source loaders for native Zomic files and generated raw exports
  - end-to-end corpus builder writing syntax/materials/reject/audit artifacts
  - operator-facing mdisc llm-corpus build command
affects: [phase-06-completion, phase-07-planning, LLM-01]
tech-stack:
  added: []
  patterns: [inventory-driven loader dispatch, builder-time compile validation, exact-source fast path, JSON CLI summaries]
key-files:
  created:
    - materials-discovery/src/materials_discovery/llm/converters/cif2zomic.py
    - materials-discovery/src/materials_discovery/llm/converters/native_zomic.py
    - materials-discovery/src/materials_discovery/llm/converters/generated_export.py
    - materials-discovery/src/materials_discovery/llm/corpus_builder.py
    - materials-discovery/tests/fixtures/hypodx_approximant_sample.cif
    - materials-discovery/tests/test_llm_cif2zomic.py
    - materials-discovery/tests/test_llm_native_sources.py
    - materials-discovery/tests/test_llm_corpus_builder.py
    - materials-discovery/tests/test_llm_corpus_cli.py
    - .planning/phases/06-zomic-training-corpus-pipeline/06-04-SUMMARY.md
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/src/materials_discovery/llm/converters/__init__.py
    - materials-discovery/Progress.md
key-decisions:
  - "Let canonical CIF conversion fall back to parse_cif when thin offline fixtures omit symmetry loops, instead of requiring richer crystallographic metadata."
  - "Treat native Zomic and direct generated-export sources as exact fast-paths inside the builder while generated candidates and CIF-derived examples go through builder-time compile validation."
  - "Mount the corpus builder as a dedicated llm-corpus Typer sub-application rather than overloading existing pipeline commands."
patterns-established:
  - "The Phase 6 build writes the full audit trail under data/llm_corpus/{build_id}/ with syntax, materials, rejects, inventory, QA, and manifest artifacts."
  - "Builder dispatch is stable and inventory-driven: loader_hint first, source_family second."
requirements-completed: [LLM-01]
duration: 54min
completed: 2026-04-03
---

# Phase 6 Plan 04: Corpus Builder And CLI Summary

**Open-approximant conversion, exact-source loaders, end-to-end corpus assembly, and operator-facing CLI**

## Performance

- **Duration:** 54 min
- **Completed:** 2026-04-03
- **Tasks:** 4
- **Task commits:** 4

## Accomplishments

- Added CIF/open-approximant conversion for COD and HYPOD-X-style fixtures,
  including a deterministic composition-only fallback for canonical records that
  do not carry structure representations.
- Added explicit native-Zomic and generated-export loaders so the builder can
  keep exact source artifacts separate from converted examples.
- Added `llm/corpus_builder.py`, which starts from the Phase 6 inventory,
  validates/grades/dedupes examples, and writes the full artifact family under
  `data/llm_corpus/{build_id}`.
- Added `mdisc llm-corpus build --config ...` and JSON summary output on the
  standard CLI surface.
- Re-ran the full `materials-discovery` suite successfully after all Phase 6
  code landed.

## Task Commits

1. **Task 1: Implement CIF/open-approximant conversion for COD and HYPOD-X-style inputs** - `0f08f9c7` (`feat`)
2. **Task 2: Add dedicated native-Zomic and generated-export source loaders** - `1f98fc34` (`feat`)
3. **Task 3: Build syntax/materials corpora and write inventory, QA, rejects, and manifest outputs** - `a3a8f0e6` (`feat`)
4. **Task 4: Add operator-facing mdisc llm-corpus build command** - `5250265f` (`feat`)

## Verification

- `cd materials-discovery && uv run pytest tests/test_llm_cif2zomic.py tests/test_prototype_import.py tests/test_data_source_cod.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_native_sources.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_corpus_builder.py tests/test_llm_corpus_inventory.py tests/test_llm_corpus_qa.py -x -v`
- `cd materials-discovery && uv run pytest tests/test_llm_corpus_cli.py tests/test_cli.py -x -v`
- `cd materials-discovery && uv run pytest`

The final subsystem verification ended at **254 passed, 3 skipped**.

## Deviations from Plan

### Auto-fixed Issues

**1. CIF-derived orbit names initially failed shared label/orbit validation inside the builder**

- **Found during:** `tests/test_llm_corpus_builder.py`
- **Issue:** The CIF conversion used lowercase orbit names from orbit metadata while label-derived validation inferred mixed-case orbit names from labels like `Sc1_01`, causing canonical-source examples to be rejected.
- **Fix:** Normalized CIF orbit names through `_infer_orbit_name()` so orbit metadata and label-derived validation use the same rule.
- **Files modified:** `materials-discovery/src/materials_discovery/llm/converters/cif2zomic.py`
- **Verification:** `cd materials-discovery && uv run pytest tests/test_llm_corpus_builder.py tests/test_llm_corpus_inventory.py tests/test_llm_corpus_qa.py -x -v`

**2. The new llm-corpus command was inserted with a comparison-command indentation regression**

- **Found during:** `tests/test_llm_corpus_cli.py tests/test_cli.py`
- **Issue:** The `lake compare` output block lost one indentation level and one trailing message line ended up under the new `llm-corpus` command, causing CLI import to fail.
- **Fix:** Restored the `lake compare` indentation and kept the new `llm-corpus` command self-contained.
- **Files modified:** `materials-discovery/src/materials_discovery/cli.py`
- **Verification:** `cd materials-discovery && uv run pytest tests/test_llm_corpus_cli.py tests/test_cli.py -x -v`

---

**Total deviations:** 2 auto-fixed
**Impact on plan:** Both fixes were verification blockers only and tightened the builder/CLI contracts without widening scope.

## Next Phase Readiness

- Phase 6 is complete: the repo now has a reproducible Zomic corpus pipeline,
  committed fixtures, builder outputs, and an operator-facing command.
- Phase 7 can focus on inference-time prompting, ranking, and evaluation
  instead of building the corpus substrate from scratch.

## Self-Check: PASSED

- Verified commits `0f08f9c7`, `1f98fc34`, `a3a8f0e6`, and `5250265f` exist in git history.
- Verified focused Phase 6 wave checks and the full `materials-discovery` suite pass.
