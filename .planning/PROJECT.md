# Materials Design Program

## Current State

`v1.0`, `v1.1`, and `v1.2` are shipped.

The shipped milestones delivered all three linked workstreams and the current
LLM operating surface:
- multi-source materials ingestion
- reference-aware no-DFT materials discovery
- the complete Zomic-centered LLM ladder from corpus through acceptance
- the proposal -> approval -> launch -> replay -> compare campaign workflow
- local and specialized serving lanes with benchmarkable operator workflow

Archive references:
- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.1-ROADMAP.md`
- `.planning/milestones/v1.1-REQUIREMENTS.md`
- `.planning/milestones/v1.1-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.2-ROADMAP.md`
- `.planning/milestones/v1.2-REQUIREMENTS.md`
- `.planning/milestones/v1.2-MILESTONE-AUDIT.md`

## Current Milestone

`v1.3` — Zomic-Native Local Checkpoint MVP

**Goal:** make at least one Zomic-adapted local checkpoint a real, auditable,
benchmarkable execution target inside the shipped operator-governed workflow.

**Target features:**
- checkpoint registration and lineage for adapted local model lanes
- adapted-checkpoint execution through `llm-generate`, `llm-launch`, and replay
- adapted-vs-baseline benchmark workflow and operator rollback guidance

## Later Milestone Candidates

- broaden source coverage or deepen source QA after the LLM serving surface is
  stable
- expand campaign automation only after hosted/local/specialized serving paths
  are proven reliable in operator hands
- add larger training and checkpoint-management automation only after serving
  comparison workflows and the first adapted checkpoint lane are credible

## What This Is

This is a three-track program built on top of `materials-discovery/` in the
`vzome` repo. It expands the current no-DFT quasicrystal pipeline into
1) a multi-source materials data ingestion platform,
2) a production-quality reference-aware no-DFT materials discovery workflow,
and
3) an LLM-enabled materials design layer for Zomic generation, evaluation, and
closed-loop search.

The immediate audience is the internal research/development team working on
quasicrystal-compatible materials discovery. The longer-term audience is anyone
who needs a reproducible workflow for ingesting materials data, generating
candidates, screening them with MLIPs, and eventually using language models to
propose or assess structures.

## Core Value

Build one reproducible system where trusted materials data, physically grounded
no-DFT validation, and LLM-guided structure generation reinforce each other
instead of living in separate prototypes.

## Requirements

### Validated

- The existing `materials-discovery/` pipeline already ingests, generates,
  screens, validates, ranks, and reports on candidates.
- The current codebase already supports `mock`, pinned `real`, `exec`, and
  `native` backend modes.
- The docs already define a planned LLM path centered on Zomic rather than CIF
  text generation.
- Phase 1 planning now defines the canonical raw-source contract, source
  registry, and integration boundary for the Material Design Data Ingestion
  project.
- Validated in Phase 4: Reference-aware no-DFT discovery workflow is
  operationally credible — deterministic reference-pack assembly, benchmark
  configs for Al-Cu-Fe and Sc-Zn, output-side comparability
  (`BenchmarkRunContext`, provenance in rank/report), operator-facing benchmark
  runner and runbook, 172 tests passing.
- Validated in Phase 5: Platform is analytically useful — canonical data lake
  with per-directory catalogs and hash-based staleness detection, lane-centric
  cross-system comparison engine with benchmark-pack dereferencing, three
  analytics notebooks, unified operator `RUNBOOK.md`, 200 tests passing.
- Validated in Phases 6-9: The LLM ladder is now complete through corpus
  building, constrained generation, additive evaluation, acceptance packs, and
  a dry-run `llm-suggest` advisory surface.
- Validated in v1.1: the dry-run suggestion surface now extends through
  proposal, approval, launch, replay, compare, and operator documentation with
  a complete verification chain.
- Validated in v1.2: local serving, specialized workflow lanes, and
  comparative serving benchmarks are now first-class, audited parts of the
  operator-governed LLM workflow.

### Active

- Add the first Zomic-adapted local checkpoint lane as a reproducible,
  file-backed serving target rather than leaving adaptation as an external
  experiment.
- Preserve the shipped campaign, replay, compare, and serving-benchmark
  workflow when adapted checkpoints are introduced.
- Give operators clear checkpoint registration, smoke-test, rollback, and
  adapted-vs-baseline comparison guidance before any broader training
  automation milestone.

### Out of Scope

- Full DFT-based generation/validation in the required path — the project is
  explicitly no-DFT by design.
- Lab automation and robotic synthesis integration in v1 — useful later, but
  not necessary to prove the software platform.
- Broad periodic-crystal discovery outside the quasicrystal/approximant focus —
  valuable, but it would dilute the current design advantage built around
  Z[phi], Zomic, and QC-specific data.
- Training a giant foundation model from scratch as the first LLM milestone —
  too expensive and unnecessary before corpus tooling, serving baselines, and
  constrained inference exist.

## Context

- The current implementation already covers `ingest`, `generate`, `screen`,
  `hifi-validate`, `hifi-rank`, `active-learn`, `report`, and `export-zomic`
  under `materials-discovery/src/materials_discovery/cli.py`.
- The architecture is file-backed and schema-driven. The key contracts are
  `SystemConfig`, `CandidateRecord`, manifests, calibration outputs, stage
  JSON/JSONL artifacts, and the newer serving/campaign lineage models.
- The docs already identify external sources such as HYPOD-X, COD, Materials
  Project, OQMD, NOMAD, JARVIS, Alexandria, B-IncStrDB, and NIMS MDR as relevant
  landscape inputs.
- The LLM design already assumes Zomic is the right generative representation
  because CIF-native crystal LLMs do not naturally model aperiodic quasicrystal
  geometry.

## Constraints

- **Tech stack**: Build on the existing Python 3.11 `materials-discovery/`
  subsystem — avoids splitting the platform across incompatible toolchains.
- **Architecture**: Preserve the current CLI/schema contract where practical —
  the current pipeline already works and is documented.
- **Scientific boundary**: Keep the no-DFT path explicit — this is core to the
  project's speed and reproducibility goals.
- **Data governance**: Prefer open or clearly licensable sources first —
  avoids roadmaps that depend on restricted ICSD/paid datasets to get started.
- **Representation**: Use Zomic/Z[phi] for QC-native LLM generation — this is
  the differentiated path relative to CIF-based materials LLMs.
- **Execution order**: Ingestion must mature before the reference-aware no-DFT
  materials discovery product, and that product must mature before aggressive
  LLM automation — otherwise later tracks are trained or judged on weak
  foundations.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use `materials-discovery/` as the program base | Existing pipeline and docs are already aligned around this subtree | ✓ Good |
| Sequence the work as Data -> Reference-Aware No-DFT Discovery -> LLM | Better data and provenance reduce risk in both the discovery workflow and the LLM path | ✓ Good |
| Prioritize open-access data sources first | Fastest route to a working ingestion platform | ✓ Good |
| Use OPTIMADE where possible | Reduces custom connector work across multiple materials databases | ✓ Good |
| Treat Zomic as the core LLM generation format | Best fit for quasicrystal-compatible structure generation | ✓ Good |
| Defer large-model training until corpus + evaluation are ready | Prevents premature spending and noisy benchmarks | ✓ Good |
| Start Project 3 v1.1 with closed-loop campaign execution instead of local serving | The dry-run suggestion surface is already shipped, and a governed execution loop is the next leverage point | ✓ Good |
| Keep the next milestone operator-governed and file-backed | Approval, replay, and provenance matter more right now than additional infrastructure | ✓ Good |
| Start Project 3 v1.2 with local and specialized serving rather than autonomy | The closed-loop campaign workflow is now stable enough to expand execution depth safely | ✓ Good |
| Archive milestone v1.2 after the proof-chain closure phases | The serving expansion is now shipped, benchmarked, and fully audited | ✓ Good |
| Start Project 3 v1.3 with Zomic-adapted local checkpoints | The serving surface is now stable enough to judge adapted local generation honestly | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-05 after starting milestone v1.3*
