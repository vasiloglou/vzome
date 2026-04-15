# Roadmap: Materials Design Program

## Overview

`v1.8` is a docs-and-notebook follow-up to `v1.7`. The goal is to make the
shipped LLM surface legible in the narrative/tutorial stack and to publish a
detailed notebook version of the checked guided workflow.

This milestone does not add new model, serving, or benchmark mechanics. It
improves explanation, executable documentation, and onboarding fidelity for the
surface that already ships today.

## Milestones

- ✅ **v1.6 Translator-Backed External Materials-LLM Benchmark MVP** - Phases
  34-36 (shipped 2026-04-07)
- ✅ **v1.7 Documentation Refresh and Guided Design Tutorial MVP** - Phases
  37-39 (shipped 2026-04-15; archive: `milestones/v1.7-ROADMAP.md`)
- 🚧 **v1.8 LLM Narrative Enrichment and Notebook Tutorial MVP** - Phase 40
  (all phases complete; audit pending)

## Phases

**Phase Numbering:**
- Integer phases continue from the previous milestone.
- `v1.8` starts at Phase 40 because `v1.7` ended at Phase 39.

- [x] **Phase 40: LLM Narrative Enrichment and Notebook Tutorial Conversion** -
  Enrich the docs bundle so it explains the repo's shipped LLM component and
  convert the guided walkthrough into a detailed notebook. (complete
  2026-04-15)

## Phase Details

### Phase 40: LLM Narrative Enrichment and Notebook Tutorial Conversion
**Goal**: Readers and operators can see how the shipped LLM workflows fit into
the current materials-discovery system and can follow the worked example in a
notebook with full detail.
**Depends on**: Phase 39
**Requirements**: DOC-04, DOC-05, OPS-22, OPS-23, OPS-24
**Success Criteria** (what must be TRUE):
  1. The docs set makes the shipped LLM surfaces explicit, including
     generation/evaluation, campaign governance, serving comparison,
     checkpoint lifecycle, translation, and external benchmarking, while
     still labeling future work clearly.
  2. The guided tutorial or its companion narrative shows how the
     deterministic Sc-Zn path relates to the repo's additive LLM workflows
     instead of leaving the LLM component implicit.
  3. A notebook version of the tutorial exists with runnable cells or clearly
     marked shell cells, setup assumptions, artifact inspection steps, and
     fuller interpretation notes than the Markdown page alone.
  4. The docs index and related pages tell readers when to use the notebook
     versus the Markdown tutorial and what environment each path assumes.
**Plans**: 1 plan

Plans:
- [x] 40-01-PLAN.md - Enrich the docs with explicit LLM workflow framing and
  publish a detailed notebook conversion of the guided tutorial.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 40. LLM Narrative Enrichment and Notebook Tutorial Conversion | 1/1 | Complete | 2026-04-15 |

## Archive Pointers

- `.planning/milestones/v1.7-ROADMAP.md`
- `.planning/milestones/v1.7-REQUIREMENTS.md`
- `.planning/milestones/v1.7-phases/`
- `.planning/v1.7-MILESTONE-AUDIT.md`
