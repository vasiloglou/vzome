# Phase 39: Guided Design, Evaluation, and Visualization Tutorial - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution
> agents. Decisions are captured in `39-CONTEXT.md`.

**Date:** 2026-04-15  
**Phase:** 39-guided-design-evaluation-and-visualization-tutorial  
**Areas discussed:** example scope, doc target, visualization surface, checked
snapshot usage

---

## Example Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Multiple example systems | Teach Sc-Zn plus one second chemistry for contrast. | |
| One locked Sc-Zn path | Keep the tutorial on one checked Zomic-backed example from start to finish. | ✓ |
| Purely abstract operator flow | Avoid a worked example and only describe the stages generically. | |

**Notes:** Phase 37 already locked the tutorial to one Sc-Zn Zomic-backed path.

---

## Tutorial Placement

| Option | Description | Selected |
|--------|-------------|----------|
| Fold into `RUNBOOK.md` | Extend the main operator runbook with one long walkthrough. | |
| New developer-docs tutorial page | Publish a dedicated tutorial and link it from the docs index. | ✓ |
| Add it only to the deep-dive source | Keep the tutorial inside the long-form narrative document. | |

**Notes:** A dedicated page keeps the runbook and deep-dive from becoming too
crowded.

---

## Visualization Guidance

| Option | Description | Selected |
|--------|-------------|----------|
| Treat generated candidate JSONL as the main geometry authority | Focus visualization on downstream candidate files only. | |
| Keep the Zomic authority chain explicit | Teach `.zomic`, raw export JSON, orbit-library JSON, and vZome workflow as the visualization backbone. | ✓ |
| Add a new exporter or helper just for the tutorial | Improve the path by expanding the toolchain during documentation. | |

**Notes:** The tutorial should teach the existing vZome/Zomic path, not extend it.

---

## Checked Snapshot Values

| Option | Description | Selected |
|--------|-------------|----------|
| Avoid all exact numbers | Use only generic prose for artifact interpretation. | |
| Use dated checked values sparingly | Include a few high-signal values from committed artifacts and date them. | ✓ |
| Reproduce large JSON payloads inline | Copy many current values into the tutorial. | |

**Notes:** Exact values are useful when they anchor interpretation, but they
should be obviously time-bound.

---

## the agent's Discretion

- Exact section ordering in the tutorial
- Which checked values best anchor interpretation
- How much of the desktop vZome workflow to describe without inventing UI paths

