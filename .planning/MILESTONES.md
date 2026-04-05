# Milestones

## v1.2 — Local and Specialized LLM Serving MVP

**Status:** Shipped on 2026-04-05
**Phases:** 19-24
**Plans:** 18

### Highlights

- Landed an additive local-serving runtime and deterministic serving-lane
  contract for `llm-generate`, campaign launch, and replay.
- Added a real `specialized_materials` workflow lane with evaluation-primary
  behavior, auditable serving lineage, and compatibility through compare,
  replay, and report surfaces.
- Shipped hosted vs local vs specialized serving benchmarks, smoke-first
  operator workflow docs, and committed example configs for the serving
  comparison path.
- Closed the full v1.2 proof chain with formal verification for Phases 19-21
  and self-verifying audit-closure phases 22-24.

### Archives

- `.planning/milestones/v1.2-ROADMAP.md`
- `.planning/milestones/v1.2-REQUIREMENTS.md`
- `.planning/milestones/v1.2-MILESTONE-AUDIT.md`

## v1.1 — Closed-Loop LLM Campaign MVP

**Status:** Shipped on 2026-04-05
**Phases:** 10-18
**Plans:** 27

### Highlights

- Turned the dry-run `llm-suggest` surface into typed campaign proposals,
  approval artifacts, and self-contained campaign specs.
- Launched approved campaigns through the existing `llm-generate` path while
  preserving downstream manifests and campaign lineage.
- Added `llm-replay`, `llm-compare`, and the operator runbook for the full
  safe closed-loop workflow.
- Closed the full milestone proof chain with verification for Phases 10-15 and
  self-verifying cleanup phases 16-18.

### Archives

- `.planning/milestones/v1.1-ROADMAP.md`
- `.planning/milestones/v1.1-REQUIREMENTS.md`
- `.planning/milestones/v1.1-MILESTONE-AUDIT.md`

## v1.0 — Materials Design Program

**Status:** Shipped on 2026-04-03
**Phases:** 1-9
**Plans:** 26

### Highlights

- Built the multi-source ingestion platform with HYPOD-X, COD, Materials
  Project, OQMD, JARVIS, and OPTIMADE support.
- Integrated staged source records back into the existing no-DFT discovery
  workflow without breaking `mdisc ingest`.
- Landed the reference-aware benchmark, data lake, analytics, and runbook
  surfaces for `Al-Cu-Fe` and `Sc-Zn`.
- Built the Zomic corpus pipeline, constrained `llm-generate`, additive
  `llm-evaluate`, and downstream LLM-vs-deterministic benchmarks.
- Closed the v1 LLM loop with acceptance packs and the dry-run
  `mdisc llm-suggest` workflow.

### Archives

- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`
