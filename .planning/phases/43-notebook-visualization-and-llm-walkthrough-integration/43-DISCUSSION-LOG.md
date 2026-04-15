# Phase 43: Notebook Visualization and LLM Walkthrough Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or
> execution agents. Decisions are captured in `43-CONTEXT.md`.

**Date:** 2026-04-15  
**Phase:** 43-notebook-visualization-and-llm-walkthrough-integration  
**Areas discussed:** notebook role, preview-vs-execute behavior, LLM branch
depth, docs cross-links

---

## Notebook Role and Reader Path

| Option | Description | Selected |
|--------|-------------|----------|
| Keep the notebook as a lighter companion to the Markdown page | Leave most of the new branch detail in prose and only mirror a subset in cells. | |
| Make the notebook the richest runnable companion while preserving the Markdown tutorial as the shortest operator story | Deepen the notebook with inline preview helpers, richer branch walkthroughs, and execution controls. | ✓ |
| Replace the Markdown tutorial with the notebook as the primary docs surface | Treat the notebook as the new canonical tutorial and de-emphasize the docs page. | |

**Notes:** Auto-accepted in autonomous mode based on the Phase 43 roadmap goal,
the Phase 40 decision that the notebook is a companion artifact, and the Phase
42 decision that the Markdown tutorial should remain the operator story.

---

## Preview vs Execute Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Force the notebook to rerun the export and render path on every execution | Make the inline preview depend on a fresh pipeline step every time. | |
| Default to safe preview mode over checked artifacts, then document an explicit refresh/execute switch | Keep the notebook runnable without surprise costs while still exposing the programmatic preview seam. | ✓ |
| Reintroduce desktop vZome as the notebook visualization handoff | Leave inline preview as future work and keep the last mile manual. | |

**Notes:** Auto-accepted in autonomous mode. This keeps the notebook useful in
read-only mode, matches the existing `RUN_PIPELINE = False` guardrail, and uses
the Phase 41 visualization helper as intended.

---

## LLM Branch Depth and Chemistry Handoff

| Option | Description | Selected |
|--------|-------------|----------|
| Keep only the same-system Sc-Zn LLM lane in the notebook | Leave translation/external benchmarking to runbooks and prose. | |
| Expand both the same-system lane and the translation/external benchmark branch with explicit command cells and artifact guidance | Make the notebook the densest practical walkthrough of the shipped LLM surface. | ✓ |
| Turn every workflow family into a fully executable notebook path | Try to run campaign, serving, checkpoint, translation, and external benchmark flows end to end in one notebook. | |

**Notes:** Auto-accepted in autonomous mode. The notebook should show the full
shipped command family, but it must stay honest that the Al-Cu-Fe external
branch is fixture-backed and that external target registration still depends on
real downloaded snapshots.

---

## Docs Cross-Links and Visualization References

| Option | Description | Selected |
|--------|-------------|----------|
| Change only the notebook | Leave the docs hub and visualization reference untouched. | |
| Update the notebook plus the discovery docs that explain when to use the tutorial, notebook, and standalone visualization reference | Make the three entry points legible together. | ✓ |
| Fold the standalone visualization reference into the notebook and remove the separate doc | Collapse everything into one notebook-centric explanation. | |

**Notes:** Auto-accepted in autonomous mode. Phase 43 should make the notebook
and the standalone visualization doc point at each other, and the docs index
should explain the roles of all three surfaces.

---

## the agent's Discretion

- The exact notebook section ordering as long as the deterministic Sc-Zn spine
  stays primary
- Whether external-branch artifacts are shown through graceful path checks,
  config inspection, or committed example files when a full runtime is not
  available
- The exact helper names and preview flags used inside the notebook
