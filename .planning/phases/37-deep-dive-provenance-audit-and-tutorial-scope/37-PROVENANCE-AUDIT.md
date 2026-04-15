---
phase: 37-deep-dive-provenance-audit-and-tutorial-scope
requirement: DOC-01
status: evidence-packet
created: 2026-04-15
---

# Phase 37 Provenance Audit and Tutorial Scope

## Scope Boundary

- Phase 37 does not rewrite materials-discovery/developers-docs/podcast-deep-dive-source.md.
- Phase 37 does not author the guided tutorial.
- Phase 37 does not edit materials-discovery/, so materials-discovery/Progress.md is intentionally unchanged.
- Refresh claims must be backed by git history, shipped milestone audits, current docs, or current source code.

## Source Document Provenance

`materials-discovery/developers-docs/podcast-deep-dive-source.md` was created before the current `materials-discovery/` documentation layout and moved twice before landing at its current path. The ledger below is backed by `git log --follow --date=iso-strict --format='%H%x09%ad%x09%an%x09%s' --name-status -- materials-discovery/developers-docs/podcast-deep-dive-source.md`.

| Event | Commit | Date | Evidence |
|-------|--------|------|----------|
| Created | `359cef57777479fb15652f1f4c702c43a25c4bc6` | `2026-03-06T19:53:04-05:00` | `A developer-docs/podcast-deep-dive-source.md` |
| First move | `9d7e7bc8189b067155a147ce2dd1e180688ef96f` | `2026-03-06T20:01:04-05:00` | `R099 developer-docs/podcast-deep-dive-source.md -> developer-docs/materials_discovery/podcast-deep-dive-source.md` |
| Current move | `f21c17e3c1a246349d0d0171cfa0b9390bcc8c1d` | `2026-04-02T20:48:12-04:00` | `R098 developer-docs/materials_discovery/podcast-deep-dive-source.md -> materials-discovery/developers-docs/podcast-deep-dive-source.md` |

## Post-Draft Shipped Workflow Deltas

The first source draft landed on 2026-03-06. The shipped milestone audits below show the workflow surface that Phase 38 must consider when refreshing the narrative.

| Milestone | Milestone audit path | Shipped-surface summary |
|-----------|----------------------|-------------------------|
| `v1.0` | `.planning/milestones/v1.0-MILESTONE-AUDIT.md` | Multi-source ingestion, reference-aware workflow, LLM corpus/generate/evaluate/suggest surfaces. |
| `v1.1` | `.planning/milestones/v1.1-MILESTONE-AUDIT.md` | Proposal, approval, launch, replay, and compare campaign workflow. |
| `v1.2` | `.planning/milestones/v1.2-MILESTONE-AUDIT.md` | Hosted/local/specialized serving lanes and serving benchmark workflow. |
| `v1.3` | `.planning/milestones/v1.3-MILESTONE-AUDIT.md` | Adapted checkpoint registration, strict lane resolution, adapted-vs-baseline benchmarks, rollback guidance. |
| `v1.4` | `.planning/milestones/v1.4-MILESTONE-AUDIT.md` | Checkpoint-family lifecycle, promoted default, explicit pin, promotion, and retirement. |
| `v1.5` | `.planning/v1.5-MILESTONE-AUDIT.md` | CIF/material-string translation bundles with fidelity/loss semantics. |
| `v1.6` | `.planning/v1.6-MILESTONE-AUDIT.md` | Translated benchmark freeze, external target registration, comparative external benchmark, and fidelity-aware scorecards. |
