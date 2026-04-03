# Materials Design Program

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
  configs for Al-Cu-Fe and Sc-Zn, output-side comparability (BenchmarkRunContext,
  provenance in rank/report), operator-facing benchmark runner and runbook,
  172 tests passing.

### Active

- [ ] Build a multi-source ingestion layer for open materials datasets relevant
  to quasicrystals, approximants, and materials design.
- [ ] Turn the current pipeline into a robust reference-aware no-DFT materials
  discovery product with better source coverage, provenance, analytics, and
  benchmarked execution paths.
- [ ] Add an LLM training and inference path that uses Zomic as the native
  generation representation and integrates with the existing pipeline.

### Out of Scope

- Full DFT-based generation/validation in the required path — the project is
  explicitly no-DFT by design.
- Lab automation and robotic synthesis integration in v1 — useful later, but
  not necessary to prove the software platform.
- Broad periodic-crystal discovery outside the quasicrystal/approximant focus —
  valuable, but it would dilute the current design advantage built around
  Z[phi], Zomic, and QC-specific data.
- Training a giant foundation model from scratch as the first LLM milestone —
  too expensive and unnecessary before corpus tooling and constrained inference
  exist.

## Context

- The current implementation already covers `ingest`, `generate`, `screen`,
  `hifi-validate`, `hifi-rank`, `active-learn`, `report`, and `export-zomic`
  under `materials-discovery/src/materials_discovery/cli.py`.
- The architecture is file-backed and schema-driven. The key contracts are
  `SystemConfig`, `CandidateRecord`, manifests, calibration outputs, and stage
  JSON/JSONL artifacts.
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

---
*Last updated: 2026-04-03 after Phase 4 reference-aware no-DFT materials discovery execution*
