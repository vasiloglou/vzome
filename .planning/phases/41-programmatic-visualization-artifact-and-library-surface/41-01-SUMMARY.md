---
phase: 41-programmatic-visualization-artifact-and-library-surface
plan: 01
subsystem: ui
tags: [zomic, visualization, typer, canvas, docs]
requires:
  - phase: 40
    provides: checked Sc-Zn tutorial and notebook baseline
provides:
  - checked raw-export visualization library
  - preview-zomic CLI wrapper
  - programmatic visualization reference doc
affects: [guided-tutorial, notebook, docs]
tech-stack:
  added: [standalone-html-canvas]
  patterns: [raw-export-view-model, thin-cli-wrapper]
key-files:
  created:
    - materials-discovery/src/materials_discovery/visualization/raw_export.py
    - materials-discovery/src/materials_discovery/visualization/viewer.py
    - materials-discovery/tests/test_zomic_visualization.py
    - materials-discovery/developers-docs/programmatic-zomic-visualization.md
  modified:
    - materials-discovery/src/materials_discovery/visualization/__init__.py
    - materials-discovery/src/materials_discovery/common/schema.py
    - materials-discovery/src/materials_discovery/cli.py
    - materials-discovery/tests/test_cli.py
    - materials-discovery/developers-docs/zomic-design-workflow.md
    - materials-discovery/Progress.md
key-decisions:
  - "Use the checked `*.raw.json` export as the programmatic preview input and keep `export-zomic` as the refresh path."
  - "Keep the viewer self-contained with inline canvas JavaScript instead of adding Node or service dependencies."
  - "Reject simultaneous `--design` and `--raw` inputs so the preview command stays unambiguous."
patterns-established:
  - "Visualization helpers live under `materials_discovery.visualization` and expose both raw-export and design-first entrypoints."
  - "Programmatic preview surfaces preserve repo-standard CLI JSON summaries and exit-code-2 failures."
requirements-completed: [VIS-01, VIS-02]
duration: 8 min
completed: 2026-04-15
---

# Phase 41 Plan 01: Programmatic Visualization Artifact and Library Surface Summary

**Checked raw-export visualization library with standalone HTML canvas rendering and a `preview-zomic` CLI wrapper**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-15T16:08:26Z
- **Completed:** 2026-04-15T16:12:39Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Added a typed raw-export loader plus normalized view-model builder that reads the checked `*.raw.json` artifact directly and preserves source metadata for downstream preview surfaces.
- Shipped a self-contained HTML canvas renderer and `mdisc preview-zomic` CLI wrapper with explicit failure handling for malformed segment data and ambiguous `--design` / `--raw` invocation.
- Documented the repo-owned preview path and updated `materials-discovery/Progress.md` so the programmatic visualization surface is discoverable from the existing Zomic workflow docs.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the raw export contract and self-contained renderer core** - `031261dc` (`feat`)
2. **Task 2: Add the public helper surface and thin `preview-zomic` CLI wrapper** - `8194c5f9` (`feat`)
3. **Task 3: Publish the narrow reference doc and update required progress tracking** - `e817b495` (`docs`)

Plan metadata is recorded in the completion commit that adds this summary and the phase verification artifacts.

## Files Created/Modified

- `materials-discovery/src/materials_discovery/visualization/raw_export.py` - Typed raw-export models, metadata preservation, orbit color mapping, segment dedupe, and view-model normalization.
- `materials-discovery/src/materials_discovery/visualization/viewer.py` - Standalone HTML renderer, viewer writer, and preview helpers for design-first or raw-export-first usage.
- `materials-discovery/src/materials_discovery/visualization/__init__.py` - Public visualization helper exports.
- `materials-discovery/src/materials_discovery/common/schema.py` - Added the typed `ZomicPreviewSummary` CLI contract.
- `materials-discovery/src/materials_discovery/cli.py` - Added `preview-zomic` with repo-standard JSON success output and exit-code-2 failures.
- `materials-discovery/tests/test_zomic_visualization.py` - Focused coverage for raw export loading, malformed segment rejection, HTML rendering, and the checked Sc-Zn smoke test.
- `materials-discovery/tests/test_cli.py` - Preview CLI coverage including `--show-labels`, browser monkeypatching, and mutual-exclusion failures.
- `materials-discovery/developers-docs/programmatic-zomic-visualization.md` - Narrow operator reference for refresh, preview, and Python helper usage.
- `materials-discovery/developers-docs/zomic-design-workflow.md` - Cross-link to the new programmatic preview reference.
- `materials-discovery/Progress.md` - Required changelog row and diary entry for the materials-discovery changes.

## Decisions Made

- Used the checked raw export rather than `.vZome` or `.shapes.json` as the first stable preview input.
- Kept the render path Python-first and file-backed, with inline JavaScript only inside the generated HTML viewer artifact.
- Treated malformed segment endpoint payloads and dual-input CLI invocations as explicit failures instead of silently degrading behavior.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

One transient `.git/index.lock` blocked the first docs commit attempt. The lock had already cleared by the time it was rechecked, and the retry succeeded without any repo cleanup.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 42 can now replace the Markdown tutorial's manual desktop preview handoff with the repo-owned viewer path and build the deeper LLM walkthrough on top of that stable visualization seam.

---
*Phase: 41-programmatic-visualization-artifact-and-library-surface*
*Completed: 2026-04-15*
