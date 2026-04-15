---
gsd_state_version: 1.0
milestone: v1.81
milestone_name: Extensive LLM Tutorial and Programmatic vZome Visualization MVP
current_phase: "42"
current_phase_name: Extensive Guided Tutorial Expansion
current_plan: Not started
status: ready for planning
stopped_at: phase 41 complete; phase 42 ready for planning
last_updated: "2026-04-15T16:14:42.900Z"
last_activity: 2026-04-15
progress:
  total_phases: 3
  completed_phases: 1
  total_plans: 1
  completed_plans: 1
  percent: 33
---

# Project State

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-04-15)

**Core value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.
**Current focus:** Phase 42 — extensive-guided-tutorial-expansion. Expand the
checked tutorial around the new repo-owned preview seam and make the shipped LLM
workflow families legible inside one deeper walkthrough.

## Current Position

Phase: 42 (extensive guided tutorial expansion) — READY FOR PLANNING
Plan: Not started
Current Milestone: v1.81
Most Recent Milestone: v1.8
Current Phase: 42
Current Phase Name: Extensive Guided Tutorial Expansion
Total Phases in Current Milestone: 3
Current Plan: Not started
Status: Phase 41 complete; Phase 42 ready for planning
Last activity: 2026-04-15
Last Activity Description: Phase 41 complete, transitioned to Phase 42

Progress: [###-------] 33%

## Performance Metrics

**Velocity:**

- Total plans completed: 110
- Average duration: archived across prior milestones
- Total execution time: archived across prior milestones

**By Milestone:**

| Milestone | Phases | Plans | Outcome |
|-----------|--------|-------|---------|
| v1.0 | 1-9 | 26 | Shipped |
| v1.1 | 10-18 | 27 | Shipped |
| v1.2 | 19-24 | 18 | Shipped |
| v1.3 | 25-27 | 9 | Shipped |
| v1.4 | 28-30 | 9 | Shipped |
| v1.5 | 31-33 | 9 | Shipped |
| v1.6 | 34-36 | 9 | Shipped |
| v1.7 | 37-39 | 3 | Shipped |
| v1.8 | 40 | 1 | Shipped |
| Phase 37 P01 | 537 | 3 tasks | 2 files |
| Phase 38 P01 | 289 | 3 tasks | 2 files |
| Phase 39 P01 | 0b8 | 3 tasks | 3 files |
| Phase 40 P01 | 9b1 | 3 tasks | 6 files |

## Accumulated Context

### Decisions

Decisions are logged in `PROJECT.md`. Recent decisions affecting future work:

- Use a documentation-first `v1.7` milestone to align the external-facing
  narrative and onboarding docs with the shipped workflow before expanding
  automation again.

- [Phase 37]: Keep the deep-dive refresh as an evidence-backed narrative with
  cross-links rather than turning it into a standalone operator manual.

- [Phase 37]: Use one Sc-Zn Zomic-backed worked example as the tutorial anchor
  so design, evaluation, and visualization stay in one coherent path.

- [Phase 37]: Require shipped-only claims and explicit future-work labeling in
  the refreshed narrative and tutorial.

- Keep the platform CLI-first, file-backed, and operator-governed until
  stronger evidence justifies broader automation.

- Use `v1.6` benchmark scorecards to decide whether the next milestone should
  prioritize training automation, campaign automation, or benchmark-driven
  source QA.

- [Phase 37]: Phase 37 stays planning-only; materials-discovery/Progress.md remains intentionally unchanged because no materials-discovery files changed.
- [Phase 37]: Phase 39 tutorial anchor is one Sc-Zn Zomic-backed path using checked config and design artifacts.
- [Phase 37]: Phase 38 should soften or date volatile counts and describe the shipped surface through v1.6.
- [Phase 38]: Refresh the deep-dive as a workflow-family narrative through v1.6 rather than a frozen seven-command story.
- [Phase 38]: Remove or soften volatile counts and make future-work labels explicit for campaigns, checkpoints, visualization, and chemistry expansion.
- [Phase 38]: Build Phase 39 from the locked Sc-Zn path and the refreshed deep-dive cross-links instead of inventing a second example.
- [Phase 39]: Publish the guided tutorial as its own doc page and wire it into the docs index instead of overloading RUNBOOK.md or the deep-dive narrative.
- [Phase 39]: Keep the geometry authority chain explicit: `.zomic` source first, then raw export, then orbit-library JSON, then downstream candidate artifacts.
- [Phase 39]: Use the checked Sc-Zn snapshot to teach interpretation, even when the correct conclusion is "hold" rather than "promote".
- [Milestone v1.7]: Archive the documentation refresh milestone now that the refreshed deep dive and guided tutorial are shipped and audited, and use them as the baseline for next-milestone scoping.
- [Milestone v1.8]: Use the next docs milestone to make the shipped LLM surface legible in the docs stack and to convert the guided tutorial into a notebook before expanding the product surface again.
- [Milestone v1.8]: Treat notebook conversion as a documentation deliverable, not as a new workflow engine or UI surface.
- [Phase 40]: Keep the checked Sc-Zn deterministic path as the tutorial spine and explain the LLM surface as additive companion workflows instead of widening chemistry scope.
- [Phase 40]: Publish the notebook as a detailed companion artifact, not as a replacement for the shorter Markdown walkthrough.
- [Phase 40]: Cross-link the deep dive, docs index, Markdown tutorial, notebook, and LLM runbooks so readers can move between narrative, checked walkthrough, and operator references without ambiguity.
- [Milestone v1.8]: Archive the LLM-aware docs-and-notebook milestone now that the tutorial, notebook, deep-dive cross-links, and PDF refresh are verified and shipped.
- [Milestone v1.81]: Extend the guided tutorial and notebook from one bounded companion lane into an extensive walkthrough of the shipped LLM functionality.
- [Milestone v1.81]: Replace the manual desktop vZome visualization handoff with a programmatic repo-owned visualization path, preferably by packaging the existing viewer/export surfaces rather than inventing a brand-new service.
- [Phase 41]: Use the checked `*.raw.json` labeled-geometry export as the
  official v1.81 visualization input; defer richer `.vZome` and
  `.shapes.json` compatibility to later work.

- [Phase 41]: Make the public usage path Python-first for docs and notebooks,
  backed by a small JavaScript rendering layer rather than a default service.

- [Phase 41]: Optimize the MVP for clear tutorial geometry rather than desktop
  vZome visual parity.

- [Phase 41]: Reuse `mdisc export-zomic` as the official artifact refresh path
  unless a paper-thin helper is needed solely for tutorial ergonomics.

- [Phase 41]: Implement the first programmatic preview path inside
  `materials_discovery.visualization` and keep `online/` as reference material
  rather than a required runtime dependency for the tutorial MVP.

- [Phase 41]: Expose the viewer through one thin `preview-zomic` CLI wrapper
  over the Python library instead of building a service or a second render
  stack.

- [Phase 41 review]: Replan execution so malformed segment coordinates raise
  `ValueError`, simultaneous `--design` and `--raw` inputs are rejected, and
  the checked Sc-Zn raw export gets a smoke-test expectation when present.
- [Phase 41]: Ship `materials_discovery.visualization`,
  `mdisc preview-zomic`, and a standalone HTML viewer so the checked Sc-Zn
  design can be previewed programmatically without a mandatory desktop-vZome
  handoff.

### Pending Todos

None yet.

### Blockers/Concerns

No active blockers. The next execution risk is keeping Phase 42 tutorial work
tied to the shipped visualization seam instead of letting the walkthrough drift
back into a manual desktop-only path or a shallow LLM catalog.

## Session Continuity

Last session: 2026-04-15T15:06:49Z
Stopped at: phase 41 complete; phase 42 ready for planning
Resume file: .planning/ROADMAP.md
