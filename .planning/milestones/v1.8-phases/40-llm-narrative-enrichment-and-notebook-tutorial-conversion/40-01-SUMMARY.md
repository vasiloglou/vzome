---
phase: 40-llm-narrative-enrichment-and-notebook-tutorial-conversion
plan: 01
subsystem: documentation
tags: [docs, notebook, llm, materials-discovery, tutorial, sc-zn]

requires:
  - phase: 38
    provides: refreshed workflow-family deep dive and current cross-links
  - phase: 39
    provides: checked Sc-Zn guided tutorial baseline
provides:
  - LLM-aware guided tutorial framing across the docs stack
  - Guided design notebook with deterministic and additive LLM companion lanes
  - Updated docs hub discovery, progress logging, and refreshed PDF export
affects: [materials-discovery-docs, onboarding, milestone-v1.8]

tech-stack:
  added: []
  patterns:
    - markdown-and-notebook paired tutorial publishing
    - deterministic-spine plus additive-llm-companion framing
    - same-change materials-discovery progress logging

key-files:
  created:
    - .planning/phases/40-llm-narrative-enrichment-and-notebook-tutorial-conversion/40-01-SUMMARY.md
    - materials-discovery/notebooks/guided_design_tutorial.ipynb
  modified:
    - materials-discovery/developers-docs/guided-design-tutorial.md
    - materials-discovery/developers-docs/index.md
    - materials-discovery/developers-docs/podcast-deep-dive-source.md
    - materials-discovery/developers-docs/podcast-deep-dive-source.pdf
    - materials-discovery/Progress.md
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
    - .planning/STATE.md

key-decisions:
  - "Keep one checked Sc-Zn deterministic path and explain the LLM surface as a companion lane instead of widening chemistry scope."
  - "Teach the shipped LLM command families at workflow-family level and cross-link to runbooks rather than duplicating every operator detail in one page."
  - "Publish the notebook as a detailed companion to the Markdown tutorial rather than replacing the shorter checked walkthrough."

patterns-established:
  - "Tutorial pairs can split a short checked Markdown path and a detailed notebook path while sharing one example system."
  - "Docs should distinguish deterministic geometry authority from additive LLM operations explicitly."

requirements-completed: [DOC-04, DOC-05, OPS-22, OPS-23, OPS-24]

duration: 12min
completed: 2026-04-15
---

# Phase 40 Plan 01: LLM Narrative Enrichment and Notebook Tutorial Conversion Summary

**LLM-aware docs refresh and notebook companion for the checked Sc-Zn walkthrough**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-15T04:53:15Z
- **Completed:** 2026-04-15T05:05:01Z
- **Tasks:** 3
- **Files modified:** 5 materials-discovery docs/artifacts, 1 new notebook, plus planning metadata after completion

## Accomplishments

- Extended `materials-discovery/developers-docs/guided-design-tutorial.md` with a dedicated section that shows where the shipped LLM workflow families fit relative to the deterministic Sc-Zn design -> evaluate spine.
- Added `materials-discovery/notebooks/guided_design_tutorial.ipynb` as a fuller companion walkthrough with setup notes, shell-driven execution cells, artifact inspection, and an LLM companion lane.
- Updated `materials-discovery/developers-docs/index.md` so readers can choose between the shorter Markdown tutorial and the more detailed notebook.
- Added tutorial/notebook cross-links back into `materials-discovery/developers-docs/podcast-deep-dive-source.md` and refreshed the sibling PDF export in the same change set.
- Recorded the required `materials-discovery/Progress.md` changelog row and same-day diary entry for the docs/notebook work.

## Task Commits

The implementation for Tasks 1-3 landed together in one atomic phase commit:

1. **Task 1-3: Publish the LLM-aware tutorial companion, notebook, and planning closeout** - `9b1dc9de` (`docs(40): add llm-aware tutorial notebook`)

## Files Created/Modified

- `materials-discovery/developers-docs/guided-design-tutorial.md` - now frames the deterministic path as the checked spine and maps the shipped LLM families onto it.
- `materials-discovery/notebooks/guided_design_tutorial.ipynb` - new detailed notebook companion for the same Sc-Zn example.
- `materials-discovery/developers-docs/index.md` - explains when to open the Markdown tutorial versus the notebook.
- `materials-discovery/developers-docs/podcast-deep-dive-source.md` - adds hands-on cross-links back into the tutorial/notebook stack.
- `materials-discovery/developers-docs/podcast-deep-dive-source.pdf` - refreshed after the deep-dive source changed.
- `materials-discovery/Progress.md` - changelog row and diary entry for Phase 40.
- `.planning/phases/40-llm-narrative-enrichment-and-notebook-tutorial-conversion/40-01-SUMMARY.md` - execution summary and closeout for Plan 40-01.
- `.planning/phases/40-llm-narrative-enrichment-and-notebook-tutorial-conversion/40-VERIFICATION.md` - verification record for DOC-04, DOC-05, OPS-22, OPS-23, and OPS-24.
- `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md` - marked Phase 40 complete and set the milestone up for audit.

## Decisions Made

- Keep the tutorial centered on the same checked Sc-Zn path instead of adding a second chemistry or alternate deterministic example.
- Explain the shipped LLM surfaces as additive workflow families with runbook links rather than turning the tutorial into an exhaustive operator manual.
- Use the notebook to hold the extra execution detail and environment notes while preserving the Markdown page as the shortest checked path.

## Deviations from Plan

No material deviations. The docs, notebook, PDF refresh, and required
`Progress.md` update landed together so the documentation surface stayed
coherent in one change set.

## Issues Encountered

None.

## Auth Gates

None.

## Known Stubs

None. This phase documents the shipped surface without adding new workflow
mechanics.

## User Setup Required

The notebook assumes the same repo-local environment as the Markdown tutorial:
`uv` for CLI execution, the checked `materials-discovery` workspace layout, and
Java/vZome tooling when readers follow the Zomic visualization handoff.

## Verification

- `test -f materials-discovery/notebooks/guided_design_tutorial.ipynb`
- `python3 - <<'PY' ... json.load(...) ... PY` to confirm notebook metadata and cell count
- `rg -n "Where the LLM workflows fit|llm-integration\\.md|guided_design_tutorial\\.ipynb|Markdown tutorial|notebook" materials-discovery/developers-docs/guided-design-tutorial.md materials-discovery/developers-docs/index.md materials-discovery/developers-docs/podcast-deep-dive-source.md`
- `rg -n "llm-generate|llm-evaluate|llm-suggest|llm-serving-benchmark|llm-register-checkpoint|llm-translate|llm-external-benchmark" materials-discovery/developers-docs/guided-design-tutorial.md materials-discovery/notebooks/guided_design_tutorial.ipynb`
- `rg -n "Phase 40 LLM docs and notebook tutorial" materials-discovery/Progress.md`
- `git diff --check`
- `cd materials-discovery && uv run pytest tests/test_cli.py -q` -> `18 passed`

## Next Phase Readiness

All planned `v1.8` phases are complete. The milestone is ready for audit and
archival.

## Self-Check: PASSED

- Found `40-01-SUMMARY.md`.
- Found the new notebook, docs-hub link, and tutorial/deep-dive cross-links.
- Verified all five `v1.8` requirements are now marked complete in `.planning/REQUIREMENTS.md`.
- Verified the required `materials-discovery/Progress.md` entry is present in the same docs change set.

---
*Phase: 40-llm-narrative-enrichment-and-notebook-tutorial-conversion*
*Completed: 2026-04-15*
