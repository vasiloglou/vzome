# Project Research Summary

**Project:** Materials Design Program
**Domain:** Extensive tutorial expansion plus programmatic visualization for the
checked Zomic workflow
**Milestone:** `v1.81`
**Researched:** 2026-04-15
**Confidence:** MEDIUM-HIGH

## Executive Summary

`v1.81` should stay tightly focused on one user-visible improvement: the guided
tutorial and notebook need to become the extensive, practical entry point for
the repo's shipped LLM workflow families, and they need to stop ejecting the
reader into desktop vZome at the visualization step.

The most credible path is not a new service and not a full browser rewrite of
vZome authoring. It is a tutorial-first visualization surface built on the
artifacts the checked workflow already produces. The key insight is that the
current tutorial already trusts `mdisc export-zomic`, and that command already
emits raw labeled geometry with segments and labeled points. That artifact is a
clean MVP input for a standalone renderer.

The repo's existing online vZome code is still important. It proves that the
repo already has browser rendering, packaging, and programmatic viewer patterns
worth reusing. But the milestone should not depend on inventing a new
`.zomic -> .vZome` share pipeline before the tutorial can improve. Start from
the checked raw export path, package one small viewer around it, then wire the
docs and notebook to that surface.

## Key Findings

### Recommended Stack

The current stack is already sufficient:

- keep `materials-discovery/` on the existing Python + `uv` workflow
- keep `mdisc export-zomic` and `ExportZomicLabeledGeometry` as the checked
  geometry compiler
- use the raw labeled geometry JSON as the first tutorial visualization input
- reuse the repo's browser-side patterns from `online/`
- package one standalone library or thin wrapper rather than a new service

The richer `vzome-viewer` and `.shapes.json` preview path should be treated as
valuable infrastructure and future compatibility, not as the first blocker for
the milestone.

### Expected Features

The minimum credible feature set is:

- one stable visualization artifact contract for the checked Sc-Zn design
- one standalone programmatic viewer surface for that artifact
- one extensive Markdown tutorial that explains the shipped LLM families in the
  same operator story
- one notebook that renders the checked design programmatically and deepens the
  command and artifact coverage for the shipped LLM surfaces

### Architecture Approach

The architecture should stay artifact-first:

`.zomic -> export-zomic raw geometry -> standalone viewer -> docs/notebook`

Do not force the milestone to solve general `.vZome` authoring, general sharing
infrastructure, or a persistent visualization service. Those are valid future
extensions, but they are not necessary to meet the user's ask here.

### Critical Pitfalls

The main risks are tutorial credibility risks, not rendering-performance risks:

1. the "programmatic" path still hides a manual desktop step
2. the milestone grows into a general visualization platform
3. the docs blur raw geometry, orbit libraries, and downstream candidates
4. the extensive tutorial becomes a long command catalog instead of a coherent
   story
5. the notebook rendering path becomes brittle or underdocumented

## Implications for Roadmap

Based on the combined research, the milestone should be planned as three
phases. That order matches the real dependency chain: artifact and viewer
surface first, narrative second, notebook integration third.

### Phase 41: Programmatic Visualization Artifact and Library Surface

**Rationale:** The tutorial cannot stop depending on desktop vZome until there
is one checked artifact and one standalone viewer path that render
programmatically.
**Delivers:** tutorial-facing geometry contract, standalone viewer packaging,
and one stable asset-refresh path for the checked Sc-Zn design.
**Addresses:** `VIS-01`, `VIS-02`.

### Phase 42: Extensive Guided Tutorial Expansion

**Rationale:** Once the programmatic visualization path exists, the Markdown
tutorial can become the coherent long-form operator story the user requested.
**Delivers:** deeper walkthrough of the deterministic spine plus shipped LLM
workflow branches, explicit visualization artifact chain, and honest scope
boundaries.
**Addresses:** `DOC-06`, `DOC-07`.

### Phase 43: Notebook Visualization and LLM Walkthrough Integration

**Rationale:** The notebook should become the executable, most-detailed version
of the same story after the viewer and narrative contracts are stable.
**Delivers:** programmatic rendering cells or helpers, richer LLM command
coverage, and clearer notebook-vs-Markdown guidance.
**Addresses:** `OPS-25`, `OPS-26`.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | The repo already has almost everything needed; the main decision is packaging, not capability discovery. |
| Features | HIGH | The user ask translates cleanly into one visualization track and one tutorial-depth track. |
| Architecture | MEDIUM-HIGH | The tutorial-first raw export path is clear; richer integration with the existing online viewer can stay optional. |
| Pitfalls | HIGH | The failure modes are concrete and strongly grounded in the current docs and codebase. |

**Overall confidence:** MEDIUM-HIGH

## Sources

### Primary

- local repo: `materials-discovery/developers-docs/guided-design-tutorial.md`
- local repo: `materials-discovery/notebooks/guided_design_tutorial.ipynb`
- local repo: `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
- local repo: `core/src/main/java/com/vzome/core/apps/ExportZomicLabeledGeometry.java`
- local repo: `core/src/main/java/com/vzome/core/exporters/ShapesJsonExporter.java`
- local repo: `online/src/wc/vzome-viewer.js`
- local repo: `online/src/viewer/context/viewer.jsx`
- local repo: `online/README.md`
- local repo: `online/developer-docs/architecture.md`
- official vZome docs: https://www.vzome.com/docs/web-component/

## Milestone Recommendation

Plan `v1.81` as a three-phase tutorial-and-visualization milestone. Success is
not a full vZome web product. Success is a checked Sc-Zn walkthrough that
stays inside the repo workflow from `.zomic` authoring to programmatic
visualization, and that finally gives the shipped LLM workflow families the
extensive tutorial coverage the user asked for.

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/SUMMARY.md`
