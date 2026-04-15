# Materials Design Program

## Current State

`v1.0`, `v1.1`, `v1.2`, `v1.3`, `v1.4`, `v1.5`, and `v1.6` are shipped.

The translator-backed benchmark milestone is now archived. Phases 37 and 38 of
`v1.7` are complete, so the milestone now has both a git-backed provenance
audit for the deep-dive refresh and a refreshed long-form source document that
matches the shipped workflow through `v1.6`. Phase 39 is next.

The shipped milestones delivered all three linked workstreams and the current
LLM operating surface:
- multi-source materials ingestion
- reference-aware no-DFT materials discovery
- the complete Zomic-centered LLM ladder from corpus through acceptance
- the proposal -> approval -> launch -> replay -> compare campaign workflow
- local and specialized serving lanes with benchmarkable operator workflow
- checkpoint-family lifecycle management with benchmark-backed promotion,
  rollback, and retirement guidance
- the groundwork for a new interoperability layer between Zomic-native
  candidates and external downloadable materials LLM formats

## Current Milestone: v1.7 Documentation Refresh and Guided Design Tutorial MVP

**Goal:** Refresh the long-form external narrative and publish one
evidence-backed operator tutorial that shows how to design candidate materials,
evaluate them with the current pipeline, and visualize the geometry in the
existing vZome/Zomic toolchain.

**Target features:**
- trace the origin of `podcast-deep-dive-source.md`, audit what shipped after
  it, and use that evidence to refresh stale capability claims
- update the deep-dive source so it accurately reflects the current CLI
  surface, milestone history, and shipped translation and benchmark workflow
- create a step-by-step tutorial with example commands, expected artifacts, and
  interpretation notes for designing and evaluating candidate materials with
  the current tool
- show how the same example flows into the vZome/Zomic visualization path so
  geometry and materials artifacts stay connected

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
- `.planning/milestones/v1.3-ROADMAP.md`
- `.planning/milestones/v1.3-REQUIREMENTS.md`
- `.planning/milestones/v1.3-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.4-ROADMAP.md`
- `.planning/milestones/v1.4-REQUIREMENTS.md`
- `.planning/milestones/v1.4-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.5-ROADMAP.md`
- `.planning/milestones/v1.5-REQUIREMENTS.md`
- `.planning/v1.5-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.6-ROADMAP.md`
- `.planning/milestones/v1.6-REQUIREMENTS.md`
- `.planning/v1.6-MILESTONE-AUDIT.md`

## Current Milestone Status

**Current Milestone:** `v1.7` — Documentation Refresh and Guided Design
Tutorial MVP

**Status:** Phases 37 and 38 completed on 2026-04-15. Phase 39, guided design,
evaluation, and visualization tutorial, is next.

**Current focus:**
- produce one checked, end-to-end tutorial that starts from the locked Sc-Zn
  Zomic-backed path and runs the current design, evaluation, and report stages
- show how the same worked example flows through the existing vZome/Zomic
  visualization path and which artifact remains the geometry authority
- keep the milestone CLI-first, file-backed, and documentation-centric now
  that the deep-dive narrative has been refreshed for the shipped `v1.6`
  surface

**Most Recent Shipped Milestone:** `v1.6` — Translator-Backed External
Materials-LLM Benchmark MVP

**Delivered in `v1.6`:**
- frozen translated benchmark packs with explicit inclusion, exclusion, and
  lineage semantics
- immutable external-target registration with reproducibility-grade smoke and
  environment capture
- comparative external-vs-internal benchmark execution on the same translated
  case slice
- fidelity-aware scorecards and operator inspect surfaces for next-step
  decisions

## Later Milestone Candidates

- add controlled checkpoint training automation only after lifecycle,
  promotion, rollback, and translator-backed benchmarking remain reliable across
  multiple checkpoints
- expand campaign automation only after promoted-checkpoint selection is stable
  in operator hands
- broaden source coverage or deepen source QA after the checkpoint lifecycle
  workflow and translation bridge are stable

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
- Validated in v1.3: adapted local checkpoints are now first-class, audited
  workflow lanes with file-backed registration, replay-safe fingerprinting,
  adapted-vs-baseline benchmarks, and operator rollback guidance.
- Validated in v1.4: adapted checkpoint families now have file-backed
  lifecycle state, promoted-default and explicit-pin execution through the
  shipped workflow, benchmark-backed candidate promotion guidance, and a
  documented rollback/retirement procedure.
- Validated in Phase 31: the translation bridge now has a typed additive
  translated-structure artifact contract, registry-backed downstream target
  families, deterministic normalization from `CandidateRecord`, explicit
  exact/anchored/approximate/lossy semantics, fixture-backed regression
  coverage, and a developer handoff note for Phase 32 exporters.
- Validated in v1.5: the external materials-LLM translation bridge is now
  shipped end to end, including deterministic CIF/material-string exporters, a
  file-backed translation bundle CLI, operator tracing commands, and explicit
  runbook guidance for representational-loss boundaries.
- Validated in Phase 34: translated benchmark packs can now be frozen from
  shipped translation bundles with explicit inclusion/exclusion rules,
  persisted lineage, and operator-facing inspect commands.
- Validated in Phase 35: curated external materials LLM targets can now be
  registered as immutable benchmark runtimes with pinned snapshot identity,
  reproducibility-grade environment capture, typed smoke artifacts, CLI
  inspect flows, and committed example specs/runbook guidance.
- Validated in v1.6: the translator-backed benchmark workflow is now shipped
  end to end, including frozen translated benchmark packs, immutable
  external-target registration, comparative benchmark execution, fidelity-aware
  scorecards, bounded recommendation lines, and operator execute/inspect
  surfaces.
- Validated in Phase 37: the repo now has a git-backed provenance audit for
  `podcast-deep-dive-source.md`, a stale-claim and shipped-surface correction
  checklist for the refresh, and a locked Sc-Zn Zomic-backed tutorial path for
  later tutorial authoring.

### Active

- Refresh `materials-discovery/developers-docs/podcast-deep-dive-source.md`
  from the Phase 37 provenance audit so it no longer under- or over-states the
  system.
- Publish a guided design -> evaluate -> visualize tutorial with runnable
  examples, expected artifacts, and interpretation notes for the current
  operator workflow.
- Keep the milestone documentation-first and CLI-first: improve explainability
  and onboarding without broadening the scientific or automation surface.

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
- The repo now ships additive translation and benchmark tooling from
  QC-native candidates into CIF/material-string bundles, translated benchmark
  packs, and external-vs-internal scorecards.
- `podcast-deep-dive-source.md` was first added on 2026-03-06 and then moved
  during later docs reorganizations, so it predates the shipped `v1.5`/`v1.6`
  workflow surface.
- The repo already has strong reference docs (`RUNBOOK.md`,
  `zomic-design-workflow.md`, `pipeline-stages.md`,
  `vzome-geometry-tutorial.md`), but no single checked tutorial currently ties
  design authoring, evaluation interpretation, and vZome visualization into
  one example.
- The current runtime can realize `CandidateRecord` data into ASE atoms or a
  pymatgen `Structure`, while the Zomic bridge preserves a vZome-rooted
  geometry path for design authoring and visualization.

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
- **Representational honesty**: Do not silently present translated CIF or
  material-string artifacts as lossless QC-native equivalents — fidelity and
  loss must be explicit in the exported contract.
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
| Start Project 3 v1.3 with Zomic-adapted local checkpoints | The serving surface was stable enough to judge adapted local generation honestly | ✓ Good |
| Archive milestone v1.3 after direct in-phase verification | The checkpoint workflow now ships with its own proof chain instead of requiring later cleanup phases | ✓ Good |
| Start Project 3 v1.4 with checkpoint lifecycle and promotion | One adapted checkpoint is now proven, so the next risk is operational curation rather than another one-off lane | ✓ Good |
| Start Project 3 v1.5 with a Zomic translation bridge before external-model execution | The immediate gap is not another model alias but an auditable representation bridge from Zomic into formats external materials LLMs actually consume | ✓ Good |
| Start Project 3 v1.6 with translator-backed external-model benchmarking | The translation bridge was shipped, so the next dependency-breaking question was which downloaded materials LLMs are worth deeper automation or training investment | ✓ Good |
| Keep `v1.6` benchmark-first and advisory rather than auto-promoting winners | Benchmark evidence needed to guide the next milestone, not silently become automation policy | ✓ Good |
| Start Project 3 v1.7 with documentation refresh and one guided workflow tutorial | The shipped tool surface now exceeds the accuracy and usability of the long-form narrative docs, and a checked tutorial lowers onboarding risk before more automation work | ✓ Good |

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
*Last updated: 2026-04-15 after completing Phase 37 and advancing to Phase 38*
