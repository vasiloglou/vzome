# Architecture Research: v1.81 Extensive LLM Tutorial and Programmatic vZome Visualization MVP

**Milestone:** `v1.81`
**Researched:** 2026-04-15
**Confidence:** HIGH for the tutorial-first raw-geometry viewer path, MEDIUM
for a richer adapter that fully reuses the existing online viewer stack.

## Executive Position

v1.81 should be built as two linked additions:

1. a small programmatic visualization surface for the checked exported Zomic
   geometry
2. a deeper tutorial and notebook pass that uses that surface instead of
   requiring desktop vZome

The safest architecture is tutorial-first and artifact-first:

- keep `.zomic` as the editable geometry authority
- keep `mdisc export-zomic` as the compiler from design source to checked raw
  geometry
- make the raw geometry export the MVP viewer input
- package one thin renderer or wrapper around that artifact
- wire the docs and notebook to the new surface

The richer `vzome-viewer` / `.shapes.json` path is valuable existing
infrastructure, but it should be treated as optional leverage for v1.81 rather
than a new hard dependency the milestone must solve before the tutorial can
improve.

## Integration Points

- `materials-discovery/developers-docs/guided-design-tutorial.md`
- `materials-discovery/notebooks/guided_design_tutorial.ipynb`
- `materials-discovery/developers-docs/index.md`
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.zomic`
- `materials-discovery/designs/zomic/sc_zn_tsai_bridge.yaml`
- `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json`
- `materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.json`
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
- `core/src/main/java/com/vzome/core/apps/ExportZomicLabeledGeometry.java`
- `core/src/main/java/com/vzome/core/exporters/ShapesJsonExporter.java`
- `online/src/wc/vzome-viewer.js`
- `online/src/viewer/context/viewer.jsx`

## Recommended Architecture

```text
checked .zomic source
  -> mdisc export-zomic
  -> raw labeled geometry JSON + orbit-library JSON
  -> viewer asset helper
  -> standalone visualization library
  -> tutorial markdown + notebook render path

optional richer path:
  existing vZome / .shapes.json preview infrastructure
  -> compatible adapter or future enhancement
```

## New vs Modified Components

### New Components

| Component | Why it should exist | Responsibility |
|-----------|---------------------|----------------|
| Standalone tutorial visualization library | The user explicitly asked for a programmatic function-call or library path | Load checked geometry artifacts and render them predictably outside desktop vZome |
| Viewer asset helper | The tutorial needs one stable way to find or refresh the geometry artifact | Resolve or refresh the checked export and pass it to the library in a predictable form |
| Notebook embed helper | Notebook users need a smooth render path | Inline or launch the viewer without manual desktop steps |

### Modified Components

| Component | Modification | Why |
|-----------|-------------|-----|
| Guided tutorial Markdown | Expand narrative depth and replace the desktop-only visualization step | This is the main user-facing milestone outcome. |
| Guided tutorial notebook | Add programmatic rendering cells and deeper LLM branch guidance | The notebook is where the extensive, executable version should live. |
| Docs index or cross-links | Explain when to use the Markdown tutorial, notebook, and visualization library | Readers need one discoverable path into the new surface. |
| Existing visualization docs | Clarify how the tutorial-first viewer relates to full vZome capabilities | Avoid overclaiming parity. |

## Architectural Seams

### 1. Keep visualization separate from authoring

Do not make v1.81 responsible for browser-side `.zomic` authoring or full
desktop parity.

Reason:

- the milestone is about eliminating the tutorial handoff, not replacing the
  authoring tool
- the checked tutorial already has a trusted export artifact
- full editing parity would turn a tutorial milestone into a product rewrite

Recommendation:

- author in `.zomic`
- export with `mdisc export-zomic`
- render the resulting checked artifact programmatically

### 2. Prefer a library surface over a service surface

The user allowed a service if it is easier, but the repo context points the
other way.

Reason:

- the tutorial is file-backed and local-first
- the browser viewer stack already exists
- a server would add lifecycle, availability, and port-management complexity

Recommendation:

- publish a scriptable library surface first
- allow a tiny local static host helper only when browser rendering needs URLs
- defer any long-running service until there is real non-tutorial demand

### 3. Keep the artifact chain explicit

The tutorial already relies on a specific authority chain:

`.zomic -> raw export -> orbit library -> downstream candidates`

Do not hide that by rendering downstream candidate artifacts as if they were
the geometry source, or by inventing a new "viewer model" that severs the link
back to the checked design export.

Recommendation:

- the viewer should make it obvious which raw export it is rendering
- the docs should say what the viewer is showing and what it is not showing

### 4. Treat `vzome-viewer` as leverage, not as a forced dependency

The repo's online viewer gives useful patterns:

- component packaging
- programmatic methods (`loadFromText()`, `captureImage()`, `exportText()`)
- preview-first loading

But the tutorial's checked design path does not currently hand us `.vZome`
share files for free.

Recommendation:

- use the online viewer stack when it lowers implementation cost
- do not block the milestone on deriving `.vZome` / `.shapes.json` from the
  current tutorial inputs if the raw export contract is already enough

## Recommended Build Shape

Plan v1.81 as three phases:

### Phase 41: Programmatic Visualization Artifact and Library Surface

Freeze the tutorial-facing geometry contract and stand up the standalone viewer
library around the checked export.

### Phase 42: Extensive Guided Tutorial Expansion

Rewrite the Markdown tutorial into a deeper operator walkthrough of the shipped
LLM surfaces, using the new visualization path instead of a desktop-only step.

### Phase 43: Notebook Visualization and LLM Walkthrough Integration

Add executable or previewable notebook helpers for programmatic rendering and
expand the notebook's LLM workflow coverage so it becomes the most detailed
walkthrough surface in the repo.

## Architecture Recommendation

Build v1.81 on the checked raw export path first. Reuse the online viewer code
where it meaningfully reduces work, but keep the milestone contract simple:
one exported geometry artifact, one standalone programmatic viewer surface, and
one extensive tutorial/notebook path that proves the workflow end to end.

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/ARCHITECTURE.md`
