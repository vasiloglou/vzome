# Materials Design Program

## Current State

`v1.0`, `v1.1`, `v1.2`, `v1.3`, `v1.4`, `v1.5`, `v1.6`, `v1.7`, `v1.8`, and
`v1.81` are shipped.

The documentation refresh milestone is now archived. It delivered a git-backed
provenance audit for `podcast-deep-dive-source.md`, a refreshed long-form
deep-dive aligned with the shipped workflow through `v1.6`, and a checked
Sc-Zn tutorial that teaches the current design, evaluation, and visualization
path.

The `v1.8` docs-and-notebook follow-up milestone is now archived. It made the
shipped LLM workflow families legible across the deep dive and guided tutorial,
added a detailed notebook companion for the checked Sc-Zn walkthrough, and
refreshed the shareable PDF/docs-hub cross-links for that documentation stack.

The `v1.81` tutorial-and-visualization follow-up milestone is now archived. It
added a repo-owned programmatic preview surface for the checked Sc-Zn design,
expanded the guided tutorial into the extensive operator walkthrough for the
shipped LLM branches, and turned the notebook into the richest runnable
companion for that same preview-first workflow.

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
- an extensive docs/tutorial layer that connects the deterministic Sc-Zn
  walkthrough to repo-owned preview, same-system LLM generation, translation
  and external benchmarking, campaigns, serving, and checkpoints without
  overstating future automation

## Current Milestone Status

**Current Milestone:** None active

**Status:** `v1.81` — Extensive LLM Tutorial and Programmatic vZome
Visualization MVP — shipped and archived on 2026-04-15.

**Current focus:**
- define the next milestone from the archived `v1.81` tutorial and
  programmatic-preview baseline
- decide whether the next expansion should emphasize checkpoint training,
  campaign automation, source QA, or a broader visualization surface
- keep future scope honest about what is already shipped versus still planned

**Most Recent Shipped Milestone:** `v1.81` — Extensive LLM Tutorial and
Programmatic vZome Visualization MVP

**Delivered in `v1.81`:**
- repo-owned programmatic preview for the checked Sc-Zn design through
  `materials_discovery.visualization` and `mdisc preview-zomic`
- extensive Markdown tutorial coverage for the deterministic Sc-Zn spine, the
  same-system LLM lane, the translation and external benchmark branch, and the
  desktop-vZome boundary
- notebook companion with preview helpers, richer branch guidance, and the
  full translated and external benchmark inspect chain

Archive references:
- `.planning/milestones/v1.81-ROADMAP.md`
- `.planning/milestones/v1.81-REQUIREMENTS.md`
- `.planning/milestones/v1.81-phases/`
- `.planning/v1.81-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.8-ROADMAP.md`
- `.planning/milestones/v1.8-REQUIREMENTS.md`
- `.planning/milestones/v1.8-phases/`
- `.planning/v1.8-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.7-ROADMAP.md`
- `.planning/milestones/v1.7-REQUIREMENTS.md`
- `.planning/milestones/v1.7-phases/`
- `.planning/v1.7-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-phases/`
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
- Validated in v1.7: documentation refresh is now shipped end to end,
  including a git-backed deep-dive provenance audit, a refreshed long-form
  narrative aligned to the shipped workflow through `v1.6`, and a checked
  Sc-Zn tutorial that ties design, evaluation, and visualization together.
- Validated in v1.8: the docs/tutorial stack now explicitly separates the
  deterministic Sc-Zn workflow spine from the additive LLM workflow families,
  includes a detailed notebook companion, and cross-links the deep dive, docs
  hub, and operator runbooks for the shipped LLM surface.
- Validated in `v1.81`: the checked Sc-Zn raw export now has a repo-owned
  programmatic preview surface via `materials_discovery.visualization` and
  `mdisc preview-zomic`, removing the happy-path requirement to open desktop
  vZome just to inspect the current checked geometry.
- Validated in `v1.81`: the checked Markdown tutorial now keeps the Sc-Zn
  deterministic spine visible while demonstrating the repo-owned preview path,
  same-system LLM lane, translation and external benchmark branch, the lighter
  governance or serving follow-ons, and the desktop-vZome boundary in one
  operator story.
- Validated in `v1.81`: the guided tutorial notebook now renders or launches
  the checked design programmatically through the repo-owned preview helper,
  teaches the full translated and external benchmark inspect chain, and sits
  clearly alongside the Markdown tutorial and standalone visualization
  reference.

### Active

- No active milestone requirements. Run `$gsd-new-milestone` to define the
  next milestone-specific requirements.

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
  during later docs reorganizations. `v1.7` refreshed it and aligned the
  narrative with the shipped `v1.6` workflow surface.
- The repo now has strong reference docs (`RUNBOOK.md`,
  `zomic-design-workflow.md`, `pipeline-stages.md`,
  `vzome-geometry-tutorial.md`) plus a checked
  `guided-design-tutorial.md` that ties design authoring, evaluation
  interpretation, and vZome visualization into one example.
- The checked Markdown tutorial now serves as the extensive operator story for
  the deterministic Sc-Zn spine, repo-owned preview handoff, same-system LLM
  lane, translation and external benchmark branch, and follow-on workflow
  families.
- The current runtime can realize `CandidateRecord` data into ASE atoms or a
  pymatgen `Structure`, while the Zomic bridge preserves a vZome-rooted
  geometry path for design authoring and visualization.
- The repo already contains an online visualization surface under `online/`,
  including the `vzome-viewer` web component and checked `.vZome` /
  `.shapes.json` preview assets.
- The Markdown tutorial now uses the repo-owned preview path as the normal
  checked inspection surface, and the notebook now deepens that same path with
  richer preview controls and fuller LLM branch walkthroughs.
- The `core` module already exposes file-backed export machinery such as
  `ExportZomicLabeledGeometry`, `ShapesJsonExporter`, and `GitHubShare`, and
  the shipped programmatic preview path now extends those existing geometry and
  preview contracts instead of inventing a parallel format.

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
- **Visualization delivery**: Prefer repo-owned viewer/library reuse and
  file-backed preview artifacts over a mandatory manual desktop step or a new
  always-on service.
- **Tutorial scope**: Keep the walkthrough tied to shipped commands and checked
  artifacts; do not imply broader chemistry coverage or autonomous workflow
  orchestration than the repo actually supports.

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
| Archive `v1.7` after the documentation refresh and guided tutorial ship | The docs baseline is now trustworthy enough to support the next milestone without carrying active milestone clutter | ✓ Good |
| Start Project 3 v1.8 with LLM-aware docs enrichment and notebook conversion | The current docs now need one follow-up pass that makes the shipped LLM story legible and gives operators a richer executable tutorial format before more product expansion | ✓ Good |
| Archive `v1.8` after the LLM-aware docs refresh and notebook companion ship | The narrative/tutorial stack is now coherent enough to support the next milestone without leaving an active docs-only milestone open | ✓ Good |
| Start Project 3 `v1.81` with extensive LLM tutorial coverage and programmatic vZome visualization | The docs stack is now coherent enough to deepen the tutorial and remove the last manual desktop visualization handoff before broader automation work resumes | ✓ Good |
| Prefer reusing the repo-owned online viewer and preview/export contracts before building a bespoke visualization service | The repo already contains `vzome-viewer`, `.shapes.json` preview handling, and export machinery, so the lowest-risk milestone path is reuse plus packaging | ✓ Good |
| Archive `v1.81` after the preview surface, extensive tutorial, and notebook companion ship | The tutorial-and-visualization baseline is now strong enough to support the next milestone without keeping documentation-only scope open | ✓ Good |

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
*Last updated: 2026-04-15 after v1.81 archival*
