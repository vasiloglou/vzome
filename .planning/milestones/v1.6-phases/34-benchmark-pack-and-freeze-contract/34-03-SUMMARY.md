---
phase: 34-benchmark-pack-and-freeze-contract
plan: 03
subsystem: llm
tags: [benchmark-pack, cli, docs, translation, operator-workflow]
requires:
  - phase: 34-02-plan
    provides: translated benchmark freeze engine, persisted manifest contract, and included/excluded inventories
provides:
  - translated benchmark freeze and inspect CLI commands for operators
  - committed YAML freeze spec plus repo-backed demo translation bundles
  - translated benchmark runbook and docs discoverability updates with explicit phase boundaries
affects: [35-external-target-registration-and-reproducible-execution, 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards]
tech-stack:
  added: []
  patterns:
    - translated benchmark freeze mirrors the repo's CLI pattern: JSON summary for write commands and human-readable traces for inspect commands
    - example benchmark-pack specs live under configs/llm as YAML and point directly at translation-bundle manifests
    - operator-facing sample configs must resolve to real repo-backed bundle manifests rather than placeholder paths
key-files:
  created:
    - materials-discovery/tests/test_llm_translated_benchmark_cli.py
    - materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml
    - materials-discovery/developers-docs/llm-translated-benchmark-runbook.md
    - materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json
    - materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_material_string_v1/manifest.json
  modified:
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/src/materials_discovery/llm/translated_benchmark.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/developers-docs/configuration-reference.md
    - materials-discovery/developers-docs/pipeline-stages.md
    - materials-discovery/developers-docs/index.md
    - materials-discovery/Progress.md
key-decisions:
  - "Used one Al-Cu-Fe CIF demo bundle plus one Al-Cu-Fe material-string demo bundle so the shipped example spec shows both included and excluded rows without inventing a separate cross-system benchmark story."
  - "Kept `llm-translated-benchmark-inspect` human-readable, matching the earlier translation-bundle inspect pattern instead of adding another JSON artifact command."
  - "Accepted YAML freeze specs in the core loader because the committed operator config lives under configs/llm and should run directly without JSON conversion."
patterns-established:
  - "Phase 34 operator docs point from translation bundles to benchmark-pack freeze and explicitly stop before runtime registration or scorecards."
  - "Repo-backed demo translation bundles may be committed when a shipped example spec needs real manifest targets to stay executable."
requirements-completed: [LLM-31]
duration: 15 min
completed: 2026-04-07
---

# Phase 34 Plan 03: Benchmark Pack and Freeze Contract Summary

**Operator CLI freeze/inspect workflow for translated benchmark packs with a runnable YAML example spec, repo-backed demo bundles, and phase-bounded runbook docs**

## Performance

- **Duration:** 15 min
- **Started:** 2026-04-07T06:02:00Z
- **Completed:** 2026-04-07T06:17:17Z
- **Tasks:** 2
- **Files modified:** 16

## Accomplishments

- Added `mdisc llm-translated-benchmark-freeze` and `mdisc llm-translated-benchmark-inspect`, including focused CLI coverage and root-help discoverability.
- Shipped a committed YAML freeze spec plus repo-backed demo translation bundles so operators can run the Phase 34 workflow against real manifests without custom Python.
- Added a dedicated translated benchmark runbook and threaded the new workflow through the docs index, configuration reference, and pipeline command reference with explicit Phase 35/36 scope boundaries.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add CLI freeze and inspect commands for translated benchmark packs** - `35e9a9ad` (test, RED), `f017fd16` (feat, GREEN)
2. **Task 2: Add an example freeze spec and operator documentation for the Phase 34 workflow** - `c98c77dd` (feat)

## Files Created/Modified

- `materials-discovery/src/materials_discovery/cli.py` - Added freeze and inspect commands for translated benchmark packs plus shared inventory loading for the inspect surface.
- `materials-discovery/tests/test_llm_translated_benchmark_cli.py` - Locked the new CLI contract for JSON freeze summaries, human-readable inspect output, filtering, and exit-code-2 failures.
- `materials-discovery/tests/test_cli.py` - Extended root help discoverability to the translated benchmark commands.
- `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` - Taught the freeze-spec loader to accept YAML so the committed operator config runs directly.
- `materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml` - Added the repo-backed sample freeze spec for the Phase 34 workflow.
- `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/*` - Committed a demo CIF translation bundle manifest, inventory, and payload for the shipped example spec.
- `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_material_string_v1/*` - Committed a demo material-string translation bundle manifest, inventory, and payload so the example spec yields a typed exclusion.
- `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md` - Added the operator runbook for freeze, inspect, artifact layout, and scope boundaries.
- `materials-discovery/developers-docs/configuration-reference.md` - Documented the new freeze-spec contract under `configs/llm/`.
- `materials-discovery/developers-docs/pipeline-stages.md` - Documented both new CLI commands, their inputs, artifacts, and failure rules.
- `materials-discovery/developers-docs/index.md` - Added the new commands and runbook to the docs map and quickstart examples.
- `materials-discovery/Progress.md` - Logged both Task 1 and Task 2 changes per repo policy.

## Decisions Made

- Shipped the example freeze spec as YAML under `configs/llm/` to match the repo's operator-config conventions instead of introducing a JSON-only exception.
- Used two repo-backed Al-Cu-Fe demo bundles with different target families so one sample spec demonstrates both inclusion and exclusion under the persisted contract.
- Kept the benchmark inspect surface human-readable, which matches the established operator pattern from `llm-translate-inspect` and makes docs-driven tracing easier.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added repo-backed demo translation bundles for the sample freeze spec**
- **Found during:** Task 2 (Add an example freeze spec and operator documentation for the Phase 34 workflow)
- **Issue:** The repo had no checked-in translation-bundle manifests, so the committed example freeze spec would have pointed at nonexistent inputs and the docs workflow would not have been executable.
- **Fix:** Generated and committed two minimal Al-Cu-Fe translation bundles under `data/llm_translation_exports/` and pointed the sample freeze spec at those real manifests.
- **Files modified:** `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json`, `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/inventory.jsonl`, `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/payloads/al_cu_fe_fixture_periodic_001.cif`, `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_material_string_v1/manifest.json`, `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_material_string_v1/inventory.jsonl`, `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_material_string_v1/payloads/al_cu_fe_fixture_periodic_001.material_string.txt`, `materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml`
- **Verification:** `uv run mdisc llm-translated-benchmark-freeze --spec configs/llm/al_cu_fe_translated_benchmark_freeze.yaml`
- **Committed in:** `c98c77dd`

**2. [Rule 2 - Missing Critical] Added YAML support to the benchmark freeze spec loader**
- **Found during:** Task 2 (Add an example freeze spec and operator documentation for the Phase 34 workflow)
- **Issue:** `load_translated_benchmark_spec(...)` only accepted JSON objects, but the shipped operator config for this phase lives under `configs/llm/*.yaml`; the documented example would have failed immediately.
- **Fix:** Switched the loader to `load_yaml(...)`, which keeps existing JSON compatibility while allowing the committed YAML spec to run directly through the freeze CLI.
- **Files modified:** `materials-discovery/src/materials_discovery/llm/translated_benchmark.py`
- **Verification:** `uv run mdisc llm-translated-benchmark-freeze --spec configs/llm/al_cu_fe_translated_benchmark_freeze.yaml`
- **Committed in:** `c98c77dd`

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical)
**Impact on plan:** Both deviations were necessary to keep the shipped operator workflow runnable. Scope stayed inside the Phase 34 freeze/inspect boundary.

## Issues Encountered

- The first manual inspect verification raced cleanup of the generated benchmark-pack directory, so the manifest disappeared before the inspect command ran. Re-running the freeze and inspect commands sequentially resolved it and confirmed the human-readable trace output.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 35 can register external targets against a stable translated benchmark-pack manifest, included inventory, excluded inventory, and persisted rule contract.
- The repo now has one documented operator path from translation bundles into a frozen benchmark pack, plus a small repo-backed demo spec for walkthroughs.
- Real benchmark work should replace the demo `bundle_manifest_paths` with manifests from operator-produced `llm-translate` runs, but there are no blockers for Phase 35 planning or implementation.

## Self-Check

PASSED

- Summary file exists: `.planning/phases/34-benchmark-pack-and-freeze-contract/34-03-SUMMARY.md`
- Key files verified: `materials-discovery/src/materials_discovery/cli.py`, `materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml`, `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md`, `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json`, `materials-discovery/data/llm_translation_exports/phase34_demo_al_cu_fe_material_string_v1/manifest.json`
- Task commits verified: `35e9a9ad`, `f017fd16`, `c98c77dd`
