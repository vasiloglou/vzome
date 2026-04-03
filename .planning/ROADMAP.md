# Roadmap: Materials Design Program

**Date:** 2026-04-02  
**Program base:** `materials-discovery/` in the `vzome` repo  
**Roadmap style:** One shared foundation with three linked workstreams

## Program Summary

This roadmap organizes the work into three projects that build on each other:

1. **Material design data ingestion**
   Build a multi-source ingestion platform for quasicrystal, approximant, and
   broader materials-design datasets.
2. **Reference-Aware No-DFT Materials Discovery**
   Turn the existing `materials-discovery` pipeline into a stronger,
   data-rich, benchmarked discovery and prioritization workflow.
3. **LLM training and inference**
   Add a Zomic-centered LLM stack for generation, evaluation, and eventually
   closed-loop suggestions.

The sequencing is intentional:

- richer data improves the current discovery workflow
- a stronger reference-aware no-DFT discovery workflow provides the evaluation harness for LLM outputs
- LLM work should not outrun data quality and downstream validation

## Research Inputs

### Repo-driven inputs

Roadmap assumptions are grounded in:

- `materials-discovery/README.md`
- `materials-discovery/REAL_MODE_EXECUTION_PLAN.md`
- `materials-discovery/developers-docs/index.md`
- `materials-discovery/developers-docs/architecture.md`
- `materials-discovery/developers-docs/backend-system.md`
- `materials-discovery/developers-docs/pipeline-stages.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/zomic-llm-data-plan.md`
- `materials-discovery/developers-docs/llm-quasicrystal-landscape.md`

### External-source inputs

Priority sources confirmed from current official docs/pages:

- **HYPOD-X**: open QC/approximant dataset built specifically to address missing
  open QC data in ML workflows.
- **Materials Project**: official `mp-api` path with API key access and strong
  ecosystem support.
- **OQMD**: open DFT database with REST and OPTIMADE APIs, CC-BY 4.0.
- **NOMAD**: FAIR materials platform with current official docs and OPTIMADE
  presence.
- **JARVIS**: NIST platform with REST and OPTIMADE access for materials design.
- **COD**: CC0 crystallographic database with direct CIF retrieval plus SQL/REST
  query surfaces.
- **Alexandria**: CC-BY 4.0 downloadable JSON + OPTIMADE datasets.
- **Open Materials Database**: public database designed for programmatic access
  via `httk`.
- **B-IncStrDB**: Bilbao incommensurate structures database, useful for
  superspace/incommensurate references.
- **MPDS**: high-value curated source, but API access is subscription-gated,
  so it should not be a v1 dependency.

## Source Prioritization

### Tier 1: Build first

- **HYPOD-X**
  Why: closest fit to the current quasicrystal mission and already referenced by
  the repo.
- **COD**
  Why: open, large, queryable, easy to retrieve CIFs, useful for approximants.
- **Materials Project**
  Why: mature ecosystem, official Python API, standard benchmark source.
- **OQMD**
  Why: open license, REST + OPTIMADE, broad computed materials coverage.
- **JARVIS**
  Why: explicitly built for materials design, includes REST/OPTIMADE surfaces.

### Tier 2: Add after the ingestion core is stable

- **NOMAD**
  Why: broad FAIR platform and strong metadata story, but likely needs more
  careful schema/profile handling.
- **Alexandria**
  Why: excellent downloadable datasets and OPTIMADE support, especially useful
  for large-scale computed data enrichment.
- **Open Materials Database**
  Why: interesting programmatic model via `httk`, but probably lower immediate
  payoff than MP/OQMD/JARVIS.
- **B-IncStrDB**
  Why: highly relevant to superspace/incommensurate structure knowledge, but
  narrower and more specialized.

### Tier 3: Optional or restricted

- **MPDS**
  Why: scientifically valuable but subscription/API access is not fully open.
- **ICSD**
  Why: strong source for approximants but licensed; treat as v2+ or partner path.

## Phase Roadmap

## Phase 1: Program Charter and Canonical Data Model

**Goal:** define the ingestion contract before writing multiple adapters.

**Deliverables**

- expanded source and official-tooling inventory for the relevant materials-data ecosystem
- canonical raw-source schema for external materials records
- source registry with provider metadata, licensing, and snapshot/version fields
- adapter classification: direct, OPTIMADE, CIF-conversion, curated-manual
- source priority matrix and acceptance policy

**Primary requirements**

- `DATA-01`, `DATA-02`, `OPS-01`, `OPS-02`

**Notes**

- This is the point to decide which fields are mandatory for reference-phase
  ingestion versus optional for later enrichment.
- Avoid overfitting the schema to HYPOD-X alone.
- Capture a broader source and client/tooling landscape here so Phase 2 does
  not start from an under-researched source list.

## Phase 2: Ingestion Platform MVP

**Goal:** land the first reusable ingestion framework with a mix of source-specific
and standard-protocol connectors.

**Deliverables**

- `materials_discovery/data_sources/` or equivalent package for external adapters
- shared adapter interface for source listing, fetch, normalize, provenance
- one OPTIMADE adapter path
- first direct adapters:
  - HYPOD-X
  - COD
  - Materials Project
  - OQMD
  - JARVIS
- QA report generation for raw and normalized ingests

**Primary requirements**

- `DATA-03`, `DATA-04`, `OPS-04`

**Notes**

- This is the best first standalone project because it creates reusable leverage
  for everything else.
- COD and HYPOD-X give you open QC/approximant-friendly records early.

## Phase 3: Reference-Phase Integration with Current Pipeline

**Goal:** make the new ingestion layer feed the existing pipeline cleanly.

**Deliverables**

- transform external records into pipeline-compatible processed reference phases
- source-aware normalization rules for compositions, structure tags, and QC family labels
- manifest integration for source provenance and snapshot lineage
- compatibility with existing `mdisc ingest`
- preserved no-DFT execution path and current CLI contracts

**Primary requirements**

- `DATA-05`, `PIPE-01`, `OPS-03`

**Notes**

- This phase should end with the current pipeline behaving better, not just with
  more raw data on disk.

## Phase 4: Reference-Aware No-DFT Materials Discovery v1

**Goal:** turn the current pipeline into an operationally credible
reference-aware no-DFT materials discovery workflow with richer inputs and
stronger benchmarks.

**Deliverables**

- benchmarked end-to-end runs on at least two systems using non-mock inputs
- calibrated reference-phase packs sourced from multiple databases
- improved report and ranking provenance
- reproducible runbooks for source selection and backend selection

**Primary requirements**

- `PIPE-02`, `PIPE-03`

**Notes**

- This is the point where "project 2" becomes real instead of just being the
  existing scaffold.

## Phase 5: Candidate/Reference Data Lake and Analysis Layer

**Goal:** make the platform analytically useful, not just executable.

**Deliverables**

- canonical local lakehouse layout or registry for:
  - raw source records
  - normalized references
  - candidate outputs
  - validation outputs
  - benchmark corpora
- comparison utilities across sources, systems, and backend modes
- operator-facing analytics notebooks or scripts
- one end-to-end runbook for the team

**Primary requirements**

- `PIPE-04`, `PIPE-05`

**Plans:** 3/3 plans complete

Plans:
- [x] 05-01-PLAN.md -- Catalog schema, per-directory catalog generator, staleness detection, mdisc lake index and stats CLI
- [x] 05-02-PLAN.md -- Cross-lane comparison engine and mdisc lake compare CLI
- [x] 05-03-PLAN.md -- Analytics notebooks, RUNBOOK.md, and human verification

**Notes**

- This phase makes it easier to ask "what changed?" and "which source made this
  result stronger?" without manual archaeology.

## Phase 6: Zomic Training Corpus Pipeline

**Goal:** create the data foundation for LLM work.

**Deliverables**

- `record2zomic` converter for pipeline-generated candidates
- `cif2zomic` converter for periodic approximants where feasible
- corpus builder from:
  - existing Zomic scripts
  - generated candidate records
  - HYPOD-X/COD/other open approximant structures
  - vZome exports
- corpus QA: parseability, compilability, label validity, collision checks

**Primary requirements**

- `LLM-01`

**Notes**

- This phase should happen before any serious fine-tuning.
- It is already strongly motivated by `zomic-llm-data-plan.md`.

## Phase 7: LLM Inference MVP

**Goal:** add a useful inference path before full training.

**Deliverables**

- adapter layer for general-purpose or local LLM providers
- constrained `llm-generate` prototype that:
  - prompts for Zomic
  - validates syntax
  - compiles via the existing Zomic bridge
  - emits standard `CandidateRecord` JSONL
- offline evaluation harness comparing generated candidates to the existing
  deterministic generator

**Primary requirements**

- `LLM-02`

**Notes**

- Start with inference and constrained generation before betting on a custom model.
- This lets the existing pipeline serve as the judge.

## Phase 8: LLM Evaluation and Pipeline Integration

**Goal:** connect LLM outputs to the rest of the materials workflow.

**Deliverables**

- `llm-evaluate` prototype for synthesizability, precursor hints, and anomaly checks
- integration of LLM assessments into reports and ranking context
- benchmarking of LLM-generated candidates through `screen -> validate -> rank`
- acceptance metrics for validity, novelty, and downstream pass rate

**Primary requirements**

- `LLM-03`, `LLM-04`

**Notes**

- This is the right time to decide whether external APIs are enough or whether
  fine-tuned local models are justified.

## Phase 9: Fine-Tuned Zomic Model and Closed-Loop Design

**Goal:** move from prototype LLM integration to a differentiated QC-native model.

**Deliverables**

- fine-tuned Zomic generation model and eval set
- stronger `llm-generate` with composition-conditioned prompting
- formal metrics:
  - parse success
  - compile success
  - candidate uniqueness
  - shortlist pass-through
  - validation pass rate
- initial `llm-suggest` design for active-learning integration

**Primary requirements**

- `LLM-05`

**Notes**

- Only do this after the corpus, inference harness, and benchmark criteria are stable.

## Workstream View

### Project A: Material Design Data Ingestion

Owns Phases 1-3.

Success condition:

- the team can ingest, normalize, version, and QA multiple open data sources
  without rewriting logic per source.

### Project B: Reference-Aware No-DFT Materials Discovery

Owns Phases 3-5.

Success condition:

- the current no-DFT pipeline becomes a reliable reference-aware discovery and
  prioritization workflow with stronger reference data, better benchmarks, and
  clearer operator guidance.

### Project C: Material Design Based on LLM Training and Inference

Owns Phases 6-9.

Success condition:

- Zomic-native LLM generation and evaluation become measurable contributors to
  candidate discovery without bypassing the physical validation stack.

## Recommended Immediate Start

If you want the most leverage in the next planning cycle, start here:

1. **Phase 1**
   Lock the source registry, provenance schema, and source priority list.
2. **Phase 2**
   Implement adapters for HYPOD-X, COD, Materials Project, and one OPTIMADE-backed path.
3. **Phase 3**
   Wire those outputs into the existing `mdisc ingest` and reference-phase flow.

That ordering gives you useful progress fast and sets up both the upgraded
reference-aware discovery workflow and the LLM corpus work.

## Primary Sources

- Materials Project API docs:
  https://docs.materialsproject.org/downloading-data/using-the-api/getting-started
- OQMD:
  https://www.oqmd.org/
- OPTIMADE providers dashboard:
  https://www.optimade.org/providers-dashboard/
- NOMAD official docs repo:
  https://github.com/FAIRmat-NFDI/nomad-docs
- JARVIS:
  https://jarvis.nist.gov/
- JARVIS OPTIMADE:
  https://jarvis.nist.gov/optimade/jarvisdft
- COD:
  https://www.crystallography.net/cod/
- COD query docs:
  https://wiki.crystallography.net/howtoquerycod/
- Alexandria:
  https://alexandria.icams.rub.de/
- Open Materials Database:
  https://openmaterialsdb.se/
- MPDS developer docs:
  https://mpds.io/developer/
- HYPOD-X paper:
  https://www.nature.com/articles/s41597-024-04043-z
- B-IncStrDB:
  https://www.cryst.ehu.eus/bincstrdb/
- CSLLM:
  https://www.nature.com/articles/s41467-025-61778-y
- CrystaLLM:
  https://www.nature.com/articles/s41467-024-54639-7
- MatLLMSearch:
  https://arxiv.org/abs/2502.20933

---
*Roadmap created: 2026-04-02 from repo documentation and targeted external source research*
