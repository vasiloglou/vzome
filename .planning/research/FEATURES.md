# Feature Landscape: v1.81 Extensive LLM Tutorial and Programmatic vZome Visualization MVP

**Domain:** Extensive tutorial expansion plus programmatic visualization for the
checked Sc-Zn Zomic workflow
**Researched:** 2026-04-15

## Scope Frame

- This document covers only the net-new features needed for v1.81.
- Already shipped and reused: the deterministic Sc-Zn walkthrough, the notebook
  companion, the shipped LLM command families, the Zomic export bridge, and the
  broader online vZome codebase.
- The milestone question is narrow: how do we make the checked tutorial truly
  extensive and keep visualization inside a programmatic repo-owned path?
- The milestone stays CLI-first, file-backed, tutorial-first, and scoped to the
  checked design path instead of broad product expansion.

## Suggested Requirement Categories

| Candidate REQ ID | Theme | Why It Exists In v1.81 |
|------------------|-------|------------------------|
| `VIS-01` | Viewer-ready geometry contract | Make the tutorial's checked Zomic export directly consumable by a programmatic viewer. |
| `VIS-02` | Standalone programmatic visualization library | Give users a function-call or small library path instead of a desktop-only handoff. |
| `DOC-06` | Extensive guided tutorial narrative | Turn the current concise walkthrough into a deeper explanation of the shipped LLM workflow families. |
| `DOC-07` | Visualization and workflow boundary docs | Explain the new programmatic visualization path, the artifact chain, and what remains optional or future work. |
| `OPS-25` | Notebook visualization cells | Let notebook users render the checked design programmatically inside the walkthrough. |
| `OPS-26` | Notebook LLM workflow branches | Show where the shipped LLM command families fit through richer command and artifact guidance, not a brief companion note. |

## Table Stakes

Features the milestone needs in order to feel complete for the stated goal.

| Category | Candidate REQ IDs | Feature | Why Expected | Milestone-Scoping Notes |
|----------|-------------------|---------|--------------|-------------------------|
| Visualization input contract | `VIS-01` | One checked geometry artifact can drive programmatic visualization without manual desktop work. | Without this, the tutorial still breaks its own reproducibility promise at the visualization step. | Prefer the existing raw export artifact over inventing a second primary geometry source. |
| Standalone visualization surface | `VIS-02` | A scriptable library or wrapper can load the checked geometry and render it programmatically. | The user explicitly asked for a function-call or service alternative. | Prefer a small library over a service; keep server use optional. |
| Extensive tutorial coverage | `DOC-06` | The Markdown tutorial explains the deterministic spine plus the shipped LLM workflow families in one coherent operator story. | The current tutorial is useful, but still bounded and too light for "demonstrate all the LLM based functionality." | Keep the Sc-Zn spine; do not turn this into a second unrelated example. |
| Visualization documentation | `DOC-07` | The docs explain how programmatic visualization fits into the `.zomic -> raw export -> orbit library -> candidates` chain, and what desktop vZome is still good for. | Users need to know what the new path replaces and what it does not. | Desktop vZome can remain a reference path, but no longer the required tutorial step. |
| Notebook programmatic rendering | `OPS-25` | The notebook can render or launch the checked design programmatically using the new viewer surface. | The notebook is the best place to prove the new path works in practice. | Avoid turning the notebook into a GUI shell or controller. |
| Notebook LLM walkthrough depth | `OPS-26` | The notebook deepens the shipped LLM command coverage with command cells, artifact references, and bounded branch guidance. | The user's ask was explicitly to demonstrate all the LLM-based functionality in an extensive tutorial. | Stay grounded in shipped workflows and checked artifacts. |

## Differentiators

High-value additions that make the milestone more decisive, but should not
expand it into a larger platform build.

| Category | Candidate REQ IDs | Feature | Value Proposition | Milestone-Scoping Notes |
|----------|-------------------|---------|-------------------|-------------------------|
| Viewer capture helpers | `OPS-25` | Allow notebook or script users to capture still images or stable embeds from the programmatic viewer. | This makes the tutorial and notebook easier to share and verify. | Useful, but secondary to basic rendering. |
| Library packaging clarity | `VIS-02`, `DOC-07` | Publish one obvious import or usage path instead of burying the viewer inside the existing online app. | This makes the "standalone library" ask true in practice, not just in architecture notes. | Keep the packaging minimal; do not create a new product site. |
| Branch-routing guidance | `DOC-06`, `OPS-26` | Tell readers when to branch from the deterministic spine into generation/evaluation, campaign governance, serving/checkpoints, and translation/external benchmarking. | This is the difference between an extensive tutorial and a long list of commands. | The routing can stay document-based; it does not need automation. |

## Anti-Features

Features to explicitly avoid in v1.81.

| Anti-Feature | Why Avoid It In v1.81 | What To Do Instead |
|--------------|-----------------------|--------------------|
| Full vZome editing parity in the browser | Too much scope and not required to solve the tutorial handoff problem. | Render the checked geometry and keep authoring on the existing `.zomic` path. |
| A permanent visualization backend or orchestration service | Too much operational weight for a tutorial-first milestone. | Use a library-first path, with a tiny local host helper only if browser embedding needs it. |
| New chemistry examples as the headline | The tutorial already has one checked Sc-Zn anchor; broadening chemistry would dilute the milestone. | Keep the checked anchor and deepen explanation around it. |
| New model-training, checkpoint, or campaign automation features | These are real future milestones, but not the one the user asked for here. | Demonstrate the shipped surfaces honestly instead of sneaking in new product work. |
| Replacing the deterministic spine with an LLM-first story | The deterministic path remains the evidence chain that grounds the tutorial. | Keep the deterministic spine and explain LLM workflows as additive branches. |

## Minimum Credible v1.81 Feature Set

Prioritize:

1. `VIS-01`: the checked Sc-Zn export path produces a stable visualization
   artifact for programmatic rendering.
2. `VIS-02`: a standalone viewer surface can load that artifact from a script,
   notebook, or simple page.
3. `DOC-06`: the Markdown tutorial becomes an extensive walkthrough of the
   shipped LLM workflow families without abandoning the deterministic spine.
4. `OPS-25`: the notebook renders the checked geometry programmatically.
5. `OPS-26`: the notebook deepens command and artifact coverage for the shipped
   LLM surfaces.

Defer browser editing parity, server-backed visualization infrastructure,
broader chemistry, and new workflow automation. The minimum credible milestone
is a tutorial that stays inside the repo workflow from `.zomic` authoring to
programmatic visualization and clear LLM-branch guidance.

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/FEATURES.md`
