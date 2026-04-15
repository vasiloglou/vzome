# Phase 38: Narrative Refresh and Cross-Linked Deep Dive - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 38 refreshes
`materials-discovery/developers-docs/podcast-deep-dive-source.md` so it
accurately describes the shipped `materials-discovery` system through `v1.6`
without blending future work into present capability claims.

This phase should deliver:

- a rewritten long-form deep-dive source that reflects the shipped design,
  evaluation, serving/checkpoint, translation, and external benchmark surfaces
- refreshed or removed quantitative, path, and version claims so the document
  no longer repeats stale numbers as timeless facts
- explicit cross-links to the current runbooks and reference docs so the deep
  dive stays high-level and externally readable without becoming the only
  technical source of truth

This phase does not author the worked tutorial itself. It prepares the narrative
handoff that Phase 39 will complement with the operator walkthrough.

</domain>

<decisions>
## Implementation Decisions

### Narrative shape
- **D-01:** Preserve roughly half of the existing history/math-heavy story and
  reshape the other half around the current shipped workflow. The refresh
  should feel like a balanced rewrite, not a total replacement and not a light
  touch polish pass.
- **D-02:** Keep the deep dive as a high-level external narrative rather than
  turning it into a standalone operator manual.
- **D-03:** The narrative should cross-link the current runbooks and reference
  docs instead of duplicating their procedural detail inline.

### Shipped-surface emphasis
- **D-04:** Post-`v1.0` shipped surfaces should be folded in prominently, with
  somewhat more emphasis than the legacy seven-stage framing. A good target is
  roughly a 60/40 split in favor of the current shipped workflow surface over
  the older origin-story-only framing.
- **D-05:** The refresh must explicitly cover the shipped workflow surface
  through `v1.6`, including campaigns, serving, checkpoint lifecycle,
  translation, and external benchmarking.
- **D-06:** Planned or future capabilities must be labeled explicitly as future
  work rather than blended into current-state prose.

### Quantitative claims and freshness
- **D-07:** Try refreshed numeric snapshots rather than dropping all numbers,
  but only keep numbers that are regenerated from current repo commands and are
  clearly time-bound rather than presented as timeless facts.
- **D-08:** If a number does not materially help the reader understand the
  system, soften or remove it instead of preserving it just because it can be
  counted.

### Documentation workflow
- **D-09:** Phase 38 will edit files under `materials-discovery/`, so it must
  update `materials-discovery/Progress.md` in the same change set with both a
  Changelog row and a Diary entry.

### the agent's Discretion
- Exact heading structure and paragraph flow of the refreshed deep dive
- Exact placement and phrasing of cross-links inside the document
- Which refreshed command-derived numeric snapshots are worth keeping after the
  rewrite
- Whether to add a compact summary table or callout block if it helps the
  document stay readable without turning it into a runbook

</decisions>

<specifics>
## Specific Ideas

- The refreshed piece should keep the geometric/vZome origin story, but the
  shipped materials-discovery system should now carry at least equal narrative
  weight.
- The later workflow surfaces should be described as substantial parts of the
  current system, not tacked on as an afterthought or buried in a final
  appendix.
- Fresh numbers are acceptable if they are regenerated now and written as
  dated snapshots rather than evergreen claims.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` — `v1.7` milestone framing, current state, and the
  validated outcome of Phase 37
- `.planning/REQUIREMENTS.md` — `DOC-02` and `DOC-03` as the governing
  requirements for the refresh
- `.planning/ROADMAP.md` — Phase 38 scope, dependencies, and success criteria
- `.planning/STATE.md` — current milestone state and handoff from Phase 37

### Phase 37 evidence packet
- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md` —
  source-of-truth stale-claim inventory, shipped-surface audit, and Phase 38
  correction checklist
- `.planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-VERIFICATION.md` —
  proof that the provenance audit, stale-surface inventory, and Sc-Zn scope
  lock were completed and source-checked

### Current narrative and reference docs
- `materials-discovery/developers-docs/podcast-deep-dive-source.md` — the
  document being refreshed in this phase
- `materials-discovery/developers-docs/index.md` — current docs map and shipped
  command surface
- `materials-discovery/RUNBOOK.md` — operator source of truth for current
  workflow, artifact paths, and command examples
- `materials-discovery/developers-docs/pipeline-stages.md` — per-command stage
  behavior and output contracts
- `materials-discovery/developers-docs/backend-system.md` — current backend
  mode/adaptor vocabulary needed to replace stale layering language

### Geometry and design context
- `materials-discovery/developers-docs/zomic-design-workflow.md` — current
  Zomic-authored design/export path that the deep dive can cite without
  re-explaining every procedural step
- `materials-discovery/developers-docs/vzome-geometry-tutorial.md` — geometry
  and vZome background for the preserved math/story sections

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/developers-docs/index.md` already provides a concise
  shipped command table and documentation hub that the refreshed narrative can
  cite instead of restating every command.
- `materials-discovery/RUNBOOK.md` already holds the operator workflow and
  artifact locations that should be linked rather than duplicated.
- `materials-discovery/developers-docs/pipeline-stages.md` already provides
  the current command-by-command behavior needed to validate every shipped
  surface mentioned in the narrative.
- `materials-discovery/developers-docs/backend-system.md` already defines the
  correct `mock` / `real` vocabulary and the fixture/exec/native layering that
  replaces the stale "four execution layers" framing.
- `materials-discovery/developers-docs/zomic-design-workflow.md` and
  `materials-discovery/developers-docs/vzome-geometry-tutorial.md` already
  carry the deeper geometry/design explanations that can be cross-linked from
  the refreshed story.

### Established Patterns
- The documentation surface is CLI-first, file-backed, and artifact-oriented.
- Narrative docs are allowed to stay broad and story-driven, but operational
  details should point readers to the runbook and reference docs instead of
  duplicating the full command workflow.
- Shipped claims should be backed by git history, current docs, milestone
  audits, or current source code rather than memory.
- Time-sensitive numbers should either be explicitly refreshed from commands or
  softened so they do not go stale immediately again.

### Integration Points
- `materials-discovery/developers-docs/podcast-deep-dive-source.md` is the
  primary edit target for this phase.
- `materials-discovery/Progress.md` must be updated when this phase edits the
  deep-dive source or any other file under `materials-discovery/`.
- Phase 39 will consume the refreshed narrative alongside the Sc-Zn tutorial
  scope lock, so this phase should avoid drifting into tutorial-writing.

</code_context>

<deferred>
## Deferred Ideas

- Authoring the full worked tutorial itself — Phase 39
- Additional worked examples beyond the checked Sc-Zn path
- Broader website, podcast packaging, or marketing refresh outside the repo
  documentation set

</deferred>

---

*Phase: 38-narrative-refresh-and-cross-linked-deep-dive*
*Context gathered: 2026-04-14*
