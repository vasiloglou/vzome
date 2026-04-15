# Phase 41: Programmatic Visualization Artifact and Library Surface - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution
> agents. Decisions are captured in `41-CONTEXT.md`.

**Date:** 2026-04-15  
**Phase:** 41-programmatic-visualization-artifact-and-library-surface  
**Areas discussed:** official viewer input, library surface, visual fidelity,
artifact refresh UX

---

## Official Viewer Input

| Option | Description | Selected |
|--------|-------------|----------|
| `.vZome` or `.shapes.json` first | Make existing vZome web-viewer compatibility the official MVP target. | |
| `raw.json` first | Use the checked labeled-geometry export as the stable MVP input. | ✓ |
| Support both equally in Phase 41 | Expand the MVP so all viewer inputs are first-class immediately. | |

**Notes:** Recommended and accepted by user with "use your recommendation."
This keeps the MVP anchored to the export contract the tutorial already checks
into the repo.

---

## Library Surface

| Option | Description | Selected |
|--------|-------------|----------|
| Python helper only | Expose a notebook/doc-facing API entirely from Python. | |
| Python-first helper over a thin JS layer | Make Python the official call surface while using a small browser renderer underneath. | ✓ |
| Standalone JS package first | Make the web layer the primary API and wrap it later for Python. | |

**Notes:** Recommended and accepted by user. The notebook and tutorial are the
main consumers, so the primary surface should feel direct there.

---

## Visual Fidelity

| Option | Description | Selected |
|--------|-------------|----------|
| Tutorial-readable geometry | Prioritize clear points, segments, and orbit or label cues over desktop parity. | ✓ |
| vZome-like styling now | Spend Phase 41 effort chasing closer desktop visual fidelity. | |
| Full browser parity | Treat the MVP as a desktop-vZome replacement target. | |

**Notes:** Recommended and accepted by user. Phase 41 is scoped as a tutorial
visualization surface, not a parity project.

---

## Artifact Refresh UX

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse `mdisc export-zomic` | Bless the existing command as the official refresh path. | ✓ |
| Add a thin checked-example helper | Wrap the existing export in a narrower tutorial helper immediately. | |
| Introduce a service-backed refresh path | Move artifact generation behind a viewer or server workflow. | |

**Notes:** Recommended and accepted by user. A thinner helper is still allowed
later if it measurably improves the tutorial ergonomics without changing the
underlying contract.

---

## the agent's Discretion

- Exact package names and file layout
- Whether the thin JavaScript layer borrows narrowly from `online/` or is
  implemented entirely inside `materials-discovery/`
- Minor styling choices that improve readability without implying desktop
  parity
