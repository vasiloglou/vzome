# Phase 42: Extensive Guided Tutorial Expansion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or
> execution agents. Decisions are captured in `42-CONTEXT.md`.

**Date:** 2026-04-15  
**Phase:** 42-extensive-guided-tutorial-expansion  
**Areas discussed:** tutorial structure, LLM branch depth, programmatic
visualization handoff, artifact interpretation pattern

---

## Tutorial Structure and Reader Path

| Option | Description | Selected |
|--------|-------------|----------|
| Fully interleave LLM notes into every deterministic section | Turn the whole tutorial into one blended narrative step-by-step. | |
| Keep the deterministic spine, then expand with explicit branch sections | Preserve the Sc-Zn operator walkthrough and explain where LLM families branch from it. | ✓ |
| Leave the current short LLM appendix mostly intact | Keep the LLM coverage as a brief catalog and rely on links for detail. | |

**Notes:** Recommended and accepted by user with "use your recommendation."
This preserves the checked deterministic path as the tutorial's authority chain
while allowing the LLM surfaces to become genuinely legible.

---

## LLM Branch Depth and Order

| Option | Description | Selected |
|--------|-------------|----------|
| Deeply expand only the same-system LLM lane | Keep translation, benchmarking, and external targets as short references. | |
| Deeply expand the same-system lane and the translation or external benchmark lane | Make both branches concrete, while keeping campaigns and serving lighter. | ✓ |
| Give every LLM workflow family a fully worked example | Turn the tutorial into an all-families operator manual. | |

**Notes:** Recommended structure accepted by user, with one explicit addition:
the tutorial must demonstrate `llm-translate`, `llm-translate-inspect`,
`llm-translated-benchmark-freeze`, `llm-translated-benchmark-inspect`,
`llm-register-external-target`, `llm-inspect-external-target`,
`llm-smoke-external-target`, `llm-external-benchmark`, and
`llm-inspect-external-benchmark` rather than leaving that branch as a short
table entry.

---

## Programmatic Visualization Handoff

| Option | Description | Selected |
|--------|-------------|----------|
| Keep desktop vZome as the tutorial happy path | Mention the preview seam only as optional follow-on tooling. | |
| Use the CLI preview path plus a brief Python helper example | Make repo-owned preview the normal path and show the reusable library surface. | ✓ |
| Replace the tutorial with a service-backed viewer workflow | Center the docs on a new server or browser product surface. | |

**Notes:** Recommended and accepted by user. Desktop vZome remains useful for
authoring and deeper inspection, but it should no longer be the mandatory
tutorial step.

---

## Artifact Interpretation Pattern

| Option | Description | Selected |
|--------|-------------|----------|
| Keep everything high level | Favor narrative summary and links over artifact inspection. | |
| Use full artifact interpretation on the core branches and lighter summaries for the rest | Preserve the tutorial's "run, inspect, interpret" style without overloading every branch. | ✓ |
| Give every workflow family the same full artifact walkthrough depth | Treat campaigns, serving, translation, and benchmarking as equally long worked examples. | |

**Notes:** Recommended and accepted by user. The deterministic lane, same-system
LLM lane, and translation/external benchmark lane should all stay concrete and
artifact-backed, while campaign and serving or checkpoint flows remain explicit
but shorter.

---

## the agent's Discretion

- Exact section titles and section order inside the rewritten tutorial
- Whether campaign and serving summaries live inline or in an appendix-style
  section
- How much of the Python helper usage to show inline before deferring to the
  Phase 41 visualization doc
