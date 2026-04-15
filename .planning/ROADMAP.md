# Roadmap: Materials Design Program

## Overview

`v1.7` is a documentation-first milestone. The goal is to bring the long-form
deep-dive source back into sync with the shipped workflow through `v1.6` and
to publish one guided operator tutorial that shows a real design -> evaluate ->
visualize path using the current toolchain.

This milestone does not add new scientific or automation capabilities. It makes
the current ones more legible, evidence-backed, and teachable.

## Milestones

- ✅ **v1.6 Translator-Backed External Materials-LLM Benchmark MVP** - Phases
  34-36 (shipped 2026-04-07)
- 🚧 **v1.7 Documentation Refresh and Guided Design Tutorial MVP** - Phases
  37-39 (active)

## Phases

**Phase Numbering:**
- Integer phases continue from the previous milestone.
- `v1.7` starts at Phase 37 because `v1.6` ended at Phase 36.

- [x] **Phase 37: Deep-Dive Provenance Audit and Tutorial Scope** - Trace the (completed 2026-04-15)
  podcast source doc, audit stale claims, and lock the worked-example scope for
  the tutorial.
- [x] **Phase 38: Narrative Refresh and Cross-Linked Deep Dive** - Refresh the
  long-form source document so it accurately reflects the shipped system and
  points at the current docs surface. (completed 2026-04-15)
- [x] **Phase 39: Guided Design, Evaluation, and Visualization Tutorial** -
  Publish a step-by-step example for using the current tool to design,
  evaluate, and visualize candidate materials. (completed 2026-04-15)

## Phase Details

### Phase 37: Deep-Dive Provenance Audit and Tutorial Scope
**Goal**: Operators can see exactly when the podcast deep-dive source was
written, what shipped after it, and what example/tutorial path will anchor the
refresh.
**Depends on**: Phase 36
**Requirements**: DOC-01
**Success Criteria** (what must be TRUE):
  1. Git-backed provenance exists for
     `materials-discovery/developers-docs/podcast-deep-dive-source.md`,
     including its creation commit, path moves, and major shipped workflow
     changes that landed after its first draft.
  2. The audit identifies outdated quantitative claims, stale capability
     descriptions, and missing shipped surfaces that must be reflected in the
     refreshed narrative.
  3. One worked example path and artifact set are chosen for the tutorial so
     later phases do not drift across too many systems or modes.
**Plans**: 1 plan

Plans:
- [x] 37-01-PLAN.md - Create the planning-side provenance audit and Sc-Zn tutorial scope lock.

### Phase 38: Narrative Refresh and Cross-Linked Deep Dive
**Goal**: The long-form deep-dive source accurately describes the shipped
materials-discovery system through `v1.6` without blurring future work into
present capabilities.
**Depends on**: Phase 37
**Requirements**: DOC-02, DOC-03
**Success Criteria** (what must be TRUE):
  1. The refreshed deep-dive source accurately describes the shipped design,
     evaluation, serving/checkpoint, translation, and external benchmarking
     surfaces at the right level of fidelity.
  2. Quantitative, path, and version claims in the document are refreshed or
     removed, and planned versus shipped language is explicit throughout.
  3. The deep-dive source cross-links the current runbook and reference docs so
     it can serve as an external narrative without becoming the only technical
     source of truth.
**Plans**: 1 plan

Plans:
- [x] 38-01-PLAN.md - Refresh the deep-dive narrative, source links, future-work labels, and required Progress.md entry.

### Phase 39: Guided Design, Evaluation, and Visualization Tutorial
**Goal**: Operators can follow one reproducible example that uses the current
toolchain to design candidate materials, inspect evaluation results, and view
the geometry through the existing vZome/Zomic path.
**Depends on**: Phase 38
**Requirements**: OPS-19, OPS-20, OPS-21
**Success Criteria** (what must be TRUE):
  1. The tutorial walks through one reproducible example from Zomic-backed
     design export or system selection through generate, screen, validate,
     rank, and report with runnable commands.
  2. The tutorial shows where the key artifacts land and how to interpret the
     current evidence surface for candidate properties, validation gates,
     ranking signals, and report outputs.
  3. The tutorial includes explicit visualization steps using the existing
     vZome/Zomic toolchain for the same example and makes clear which artifact
     is the geometry authority at each step.
**Plans**: 1 plan

Plans:
- [x] 39-01-PLAN.md - Publish the Sc-Zn Zomic-backed guided tutorial, docs index link, and required Progress.md update.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 37. Deep-Dive Provenance Audit and Tutorial Scope | 1/1 | Complete    | 2026-04-15 |
| 38. Narrative Refresh and Cross-Linked Deep Dive | 1/1 | Complete    | 2026-04-15 |
| 39. Guided Design, Evaluation, and Visualization Tutorial | 1/1 | Complete    | 2026-04-15 |
