# Technology Stack: v1.81 Extensive LLM Tutorial and Programmatic vZome Visualization MVP

**Project:** Materials Design Program
**Milestone:** v1.81
**Researched:** 2026-04-15
**Scope:** Only the stack additions or reuse decisions needed to turn the guided
tutorial and notebook into an extensive LLM-aware walkthrough while replacing
the manual desktop visualization handoff with a programmatic path.
**Overall confidence:** HIGH for the tutorial-stack reuse path, MEDIUM for the
exact packaging boundary of the standalone visualization library.

## Recommended Stack

### Core Runtime

| Technology | Version or Source | Purpose | Why |
|------------|-------------------|---------|-----|
| Python + `uv` | existing `materials-discovery/` baseline | Keep tutorial helpers, notebook cells, and CLI examples inside the current repo workflow | The tutorial already assumes this toolchain; v1.81 should deepen it, not fork it. |
| Existing Gradle + Java export path | existing repo build surface | Compile Zomic into checked raw geometry for visualization | `mdisc export-zomic` and `ExportZomicLabeledGeometry` already produce the geometry artifact the tutorial trusts. |
| Raw labeled geometry JSON | `data/prototypes/generated/*.raw.json` | First-class tutorial visualization artifact | This is already generated from the checked `.zomic` source without any desktop-only step. |
| Repo-owned web stack | `online/` with `esbuild`, `solid-js`, `three` | Source of truth for browser-side rendering and packaging patterns | The repo already contains browser rendering infrastructure; reuse it before inventing a second visualization stack. |
| Standalone visualization library | new thin package or wrapper built from repo code | Programmatic render surface for tutorial/notebook users | The user asked for a function-call or service path; the lowest-risk answer is a small library surface, not a general server. |
| Optional static hosting helper | simple local static file serving only when needed | Notebook or docs preview convenience | Some browser embedding flows need URL-based assets, but that does not justify an always-on backend. |

### Reuse Instead of Replacing

| Existing Stack | v1.81 Change | Why |
|----------------|--------------|-----|
| `mdisc export-zomic` | Treat its raw output as tutorial-viewer input, not just an intermediate artifact | The checked design path already passes through this command. |
| `ExportZomicLabeledGeometry` | Keep using it as the geometry compiler for the checked `.zomic` source | It already emits labeled points plus segments, which are enough for a tutorial-first renderer. |
| `online/src/wc/vzome-viewer.js` | Reuse its packaging and browser API ideas where helpful | The repo already solved programmatic viewer controls like `loadFromText()`, `captureImage()`, and export hooks. |
| `ShapesJsonExporter` and `.shapes.json` previews | Keep as a compatible richer preview path, not a v1.81 prerequisite | The guided tutorial currently starts from `.zomic`, not `.vZome`, so forcing a new preview-export pipeline would add risk. |
| Notebook HTML output | Use it for inline browser rendering when practical | This keeps programmatic visualization inside the notebook instead of bouncing to desktop. |

## Recommended Default Path

Use the checked `export-zomic` raw geometry as the MVP visualization contract.
Build the standalone library around labeled points and segments first.

Why this is the best default:

- it starts from the artifact the tutorial already produces
- it avoids inventing a `.zomic -> .vZome` conversion story just to satisfy the
  viewer
- it keeps the geometry authority chain explicit:
  `.zomic -> raw export -> orbit library -> candidates`
- it still leaves room to reuse `vzome-viewer` or `.shapes.json` later for
  richer scenes or share flows

## Required Additions

### 1. Standalone Visualization Package

Add one small, scriptable visualization surface that can:

- load a checked raw Zomic export JSON file
- render segments and labeled points programmatically
- expose a stable API for notebook or docs use
- optionally capture still images or serialize a small embed state

This package can live as:

- a thin extracted browser package under `online/`, or
- a milestone-local package that reuses `three` and repo conventions

The key is the public API, not the folder name.

### 2. Viewer Asset Staging Helpers

Add one helper path that turns the checked tutorial artifacts into something the
standalone viewer can consume predictably.

Minimum expectation:

- resolve the checked Sc-Zn raw export path
- optionally refresh it from `mdisc export-zomic`
- stage or reference the artifact in a stable tutorial location

Avoid a heavyweight asset pipeline. The tutorial needs a reliable helper, not a
new asset-management subsystem.

### 3. Notebook and Docs Embedding Surface

Add a lightweight integration path for:

- inline rendering inside the notebook, or
- opening a local viewer page from notebook or docs helpers

If a local static server is needed for browser URL loading, keep it thin and
ephemeral. Do not make service orchestration the milestone centerpiece.

## Avoid

| Avoid | Why |
|-------|-----|
| Mandatory desktop-app automation | The whole point of the milestone is to remove the desktop-only handoff from the tutorial path. |
| A new always-on visualization server | Too much operational surface for a tutorial-first milestone. |
| A brand-new geometry format | The repo already has raw labeled geometry and preview/export formats. |
| Replacing vZome authoring or editing workflows entirely | The milestone only needs a reproducible tutorial visualization path, not full authoring parity. |
| New LLM model, training, campaign, or chemistry expansion work as part of the visualization effort | That would blur the milestone and slow the real tutorial problem. |

## Stack Recommendation

Ship v1.81 on the current repo stack:

1. keep the checked design source in `.zomic`
2. keep `mdisc export-zomic` as the geometry compiler
3. use raw export JSON as the MVP visualization input
4. package one small programmatic renderer for that artifact
5. wire the tutorial and notebook to that renderer

Treat `.vZome` / `.shapes.json` viewer compatibility as a valuable extension,
not as the first dependency the milestone must solve.

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/STACK.md`
