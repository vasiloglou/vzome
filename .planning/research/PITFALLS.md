# Domain Pitfalls

**Domain:** `v1.81` Extensive LLM Tutorial and Programmatic vZome Visualization
MVP
**Researched:** 2026-04-15
**Confidence:** HIGH for repo-specific tutorial and scope risks, MEDIUM for the
exact packaging edge cases of the standalone viewer.

## Milestone Phase Assumptions

To keep the warnings actionable, this file assumes `v1.81` is split into three
phases:

| Proposed Phase | Purpose |
|---|---|
| Phase 41: Programmatic Visualization Artifact and Library Surface | Freeze the checked geometry artifact and provide a standalone render path. |
| Phase 42: Extensive Guided Tutorial Expansion | Deepen the Markdown tutorial and wire it to the new visualization path. |
| Phase 43: Notebook Visualization and LLM Walkthrough Integration | Make the notebook executable or previewable for rendering and richer LLM branches. |

## Critical Pitfalls

### Pitfall 1: The new visualization path still hides a manual desktop step

**What goes wrong:**  
The milestone claims "programmatic visualization," but the actual workflow
still depends on a human opening desktop vZome to export a file, refresh a
preview, or rescue a broken render.

**Why it happens here:**  
The current tutorial already uses desktop vZome for the final visualization
handoff. It is easy to move that step around rather than remove it.

**Consequences:**  
The tutorial remains irreproducible in practice. Readers still leave the repo
workflow at the last step, which means the main user pain is unsolved.

**Prevention:**  

- Define one checked artifact that the programmatic viewer consumes directly.
- Ensure that artifact can be refreshed from repo commands.
- Refuse milestone "done" if the documented happy path still requires opening
  desktop vZome by hand.

**Address in milestone:**  
Phase 41 must solve this directly.

### Pitfall 2: Scope creep into a general-purpose visualization platform

**What goes wrong:**  
The milestone grows from "show the checked design programmatically" into
browser editing, scene authoring, multi-design management, persistent hosting,
or a generic vZome web service.

**Why it happens here:**  
The repo already contains a substantial online vZome stack, so it is tempting
to broaden the ambition once that code is in view.

**Consequences:**  
The tutorial does not improve quickly, and the milestone turns into a platform
project that is much harder to verify.

**Prevention:**  

- Keep the user-facing requirement on the checked tutorial path only.
- Treat service hosting and editing parity as explicitly out of scope.
- Prefer one thin library surface and one checked example over a general app.

**Address in milestone:**  
Phase 41 architecture and Phase 42 docs scope boundaries.

### Pitfall 3: Rendering the wrong artifact and confusing the authority chain

**What goes wrong:**  
The viewer renders downstream candidate artifacts, orbit-library outputs, or
ad hoc transformed geometry, and the docs blur that with the original Zomic
design intent.

**Why it happens here:**  
The repo has several related artifacts: raw labeled geometry, orbit-library
JSON, candidate JSONL, and report outputs. They are connected, but not
interchangeable.

**Consequences:**  
Readers lose track of what the visualization proves. The tutorial becomes
harder to trust and to extend.

**Prevention:**  

- Name the rendered artifact explicitly in the viewer and docs.
- Keep `.zomic -> raw export -> orbit library -> candidates` visible.
- Only use downstream artifacts for the questions they actually answer.

**Address in milestone:**  
Phase 41 asset contract plus Phase 42 documentation.

### Pitfall 4: The extensive tutorial becomes a catalog instead of a story

**What goes wrong:**  
The docs try to "cover everything" by listing commands, but they lose the
single coherent operator narrative that made the original tutorial useful.

**Why it happens here:**  
The user's ask is to demonstrate all the LLM functionality, which can easily
turn into a disconnected checklist.

**Consequences:**  
Readers see more words but understand less. The tutorial becomes longer without
becoming more teachable.

**Prevention:**  

- Keep one deterministic Sc-Zn spine.
- Introduce each shipped LLM family at the moment it naturally branches from
  that spine.
- Keep command examples tied to artifact questions, not just coverage goals.

**Address in milestone:**  
Phase 42 first, then Phase 43 notebook depth.

### Pitfall 5: Notebook rendering becomes brittle or environment-specific

**What goes wrong:**  
The notebook viewer only works in one browser, only from one working
directory, or only when a hidden local server is already running.

**Why it happens here:**  
Browser-based rendering surfaces often have asset-loading constraints, and the
existing notebook currently assumes a mostly shell-and-artifact workflow.

**Consequences:**  
The notebook becomes harder to trust than the Markdown tutorial. Users fall
back to screenshots or skip the visualization cells entirely.

**Prevention:**  

- Keep the integration surface small and explicit.
- If a local host is needed, launch it with one documented helper rather than
  an implied background prerequisite.
- Provide preview-only and execute modes just as the current notebook does.

**Address in milestone:**  
Phase 43.

## Cross-Cutting Warning

Do not quietly turn the tutorial expansion into a new LLM milestone. The work
should demonstrate shipped generation/evaluation, campaign governance,
serving/checkpoints, and translation/external benchmarking honestly, but it
should not add new training, automation, or chemistry scope in order to make
the tutorial look more ambitious.

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/PITFALLS.md`
