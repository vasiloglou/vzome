# Phase 37: Deep-Dive Provenance Audit and Tutorial Scope - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-14
**Phase:** 37-deep-dive-provenance-audit-and-tutorial-scope
**Areas discussed:** narrative boundary, evidence and freshness policy, tutorial
anchor example, tutorial walkthrough shape

---

## Narrative Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Narrative + cross-links | Keep the deep dive as a high-level external story and point readers to current runbooks and docs for operational detail. | ✓ |
| Standalone manual | Expand the deep dive into one exhaustive tutorial and reference document. | |
| Light-touch refresh | Update a few stale passages but leave the overall structure and scope largely untouched. | |

**User's choice:** Narrative + cross-links
**Notes:** Resolved from the user's request to refresh a possibly stale source
document while also creating a separate nice tutorial with examples and
step-by-step instructions.

---

## Evidence and Freshness Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Git-backed shipped-only audit | Refresh claims from current docs, planning artifacts, and git history; label future work explicitly. | ✓ |
| Code-scan-only refresh | Use current source tree behavior as the only truth source and do not anchor narrative claims in milestone history. | |
| Story-first blended update | Optimize for narrative smoothness even if shipped and planned capabilities are discussed together. | |

**User's choice:** Git-backed shipped-only audit
**Notes:** Chosen because the user explicitly asked to trace when the source
document was created and what happened since then before using that as the
basis for a new milestone.

---

## Tutorial Anchor Example

| Option | Description | Selected |
|--------|-------------|----------|
| Sc-Zn Zomic-backed example | Use the checked Sc-Zn Zomic design path so one tutorial covers design authoring, evaluation flow, and vZome/Zomic visualization. | ✓ |
| Al-Cu-Fe reference-aware example | Use the Al-Cu-Fe reference-aware pipeline as the primary worked example. | |
| Dual-example tutorial | Cover both a Zomic-backed example and a separate reference-aware or benchmark example in the first tutorial. | |

**User's choice:** Sc-Zn Zomic-backed example
**Notes:** This is the most direct fit for the user's request to design new
materials, evaluate them, and visualize them with the vZome/Zomic toolchain in
one coherent example.

---

## Tutorial Walkthrough Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Operator walkthrough | Step-by-step commands, artifact paths, and interpretation checkpoints after each major stage. | ✓ |
| Quickstart only | Minimal runnable commands with little explanation of outputs. | |
| Architecture deep dive | Focus on internal system design rather than operator workflow. | |

**User's choice:** Operator walkthrough
**Notes:** The user asked for a nice tutorial with examples and step-by-step
instructions, so the tutorial needs to explain both execution and interpretation.

---

## the agent's Discretion

- Exact tutorial file name and placement under `materials-discovery/developers-docs/`
- Whether supporting diagrams, tables, or screenshots are worth adding
- Exact prose density and callout style

## Deferred Ideas

- Additional worked examples for other chemistries or the external benchmark flow
- Broader podcast or website packaging beyond repo docs
- Multi-example tutorial expansion after the first checked workflow lands
