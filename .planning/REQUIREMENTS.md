# Requirements: Materials Design Program

**Defined:** 2026-04-02
**Core Value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.

## v1 Requirements

### Data Ingestion

- [ ] **DATA-01**: The platform can ingest at least one QC-specific open source
  dataset and at least three general materials databases into a canonical raw
  staging format.
- [ ] **DATA-02**: Every ingested record carries source provenance, source
  version/snapshot metadata, license metadata, and an immutable local record ID.
- [ ] **DATA-03**: The ingestion layer supports both direct source-specific
  adapters and an OPTIMADE-based adapter path for compatible databases.
- [ ] **DATA-04**: The ingestion layer emits QA metrics for duplicates, missing
  fields, invalid compositions, malformed structures, and schema drift.
- [x] **DATA-05**: The ingestion layer can normalize periodic crystal sources
  and QC/approximant sources into pipeline-compatible reference-phase artifacts.

### Reference-Aware No-DFT Materials Discovery

- [x] **PIPE-01**: The current `ingest -> generate -> screen -> hifi-validate -> hifi-rank -> active-learn -> report`
  discovery workflow remains green while ingesting richer external data.
- [x] **PIPE-02**: The reference-aware no-DFT discovery workflow can run a
  benchmarked end-to-end flow on at least two target systems using non-mock
  data inputs.
- [x] **PIPE-03**: The platform produces comparable manifests, calibration
  outputs, and benchmark packs across source adapters and backend modes.
- [x] **PIPE-04**: The system supports source-aware reference-phase enrichment
  for proxy hull, XRD matching, and report generation.
- [x] **PIPE-05**: The platform exposes one operator-facing runbook for
  ingestion, execution, benchmarking, and result inspection.

### LLM Training and Inference

- [ ] **LLM-01**: The project can build a Zomic-centered training corpus from
  existing Zomic scripts plus converted external structures.
- [ ] **LLM-02**: The project provides a constrained inference path that
  generates Zomic, validates syntax/compileability, and converts valid outputs
  into standard `CandidateRecord` artifacts.
- [ ] **LLM-03**: The project supports an `llm-evaluate` path for
  synthesizability, precursor hints, anomaly checks, or literature-style
  contextual assessment.
- [ ] **LLM-04**: The LLM path is benchmarked against the existing generator and
  uses the same downstream screen/validate/rank/report pipeline.
- [ ] **LLM-05**: The project defines acceptance metrics for validity,
  novelty, synthesizability quality, and downstream pass-through rate.

### Operations and Governance

- [x] **OPS-01**: The roadmap explicitly distinguishes open-access, restricted,
  and subscription-only data sources.
- [x] **OPS-02**: Source adapters are prioritized by implementation cost,
  scientific value, and licensing friction.
- [x] **OPS-03**: The system keeps the no-DFT boundary explicit in required
  execution paths.
- [ ] **OPS-04**: The roadmap preserves compatibility with the current
  `materials-discovery` CLI and schema unless a deliberate version change is
  approved.

## v2 Requirements

### Data Platform Expansion

- **DATA-06**: Add support for licensed or partner-only sources such as ICSD or
  subscription-backed platforms when access is available.
- **DATA-07**: Add a federated query UI or notebook layer for comparing sources
  and extracted subsets interactively.

### Pipeline Expansion

- **PIPE-06**: Add more target chemistries beyond the current QC-centered
  systems.
- **PIPE-07**: Add automated release gates and benchmark dashboards for every
  source/backend combination.

### LLM Expansion

- **LLM-06**: Add `llm-suggest` for closed-loop active learning over composition
  regions and Zomic motif edits.
- **LLM-07**: Add fine-tuned local inference serving for Zomic generation and/or
  materials-synthesis assessment.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full DFT workflow integration for v1 | Violates the current program boundary and slows iteration |
| General-purpose chat assistant for chemistry | Not core to the platform's main value |
| Immediate support for all materials databases on day one | Better to ship a prioritized adapter set first |
| Large-scale autonomous lab execution | Requires a different operational surface than the current pipeline |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 2 | Pending |
| DATA-04 | Phase 2 | Pending |
| DATA-05 | Phase 3 | Complete |
| PIPE-01 | Phase 3 | Complete |
| PIPE-02 | Phase 4 | Complete |
| PIPE-03 | Phase 4 | Complete |
| PIPE-04 | Phase 5 | Complete |
| PIPE-05 | Phase 5 | Complete |
| LLM-01 | Phase 6 | Pending |
| LLM-02 | Phase 7 | Pending |
| LLM-03 | Phase 8 | Pending |
| LLM-04 | Phase 8 | Pending |
| LLM-05 | Phase 9 | Pending |
| OPS-01 | Phase 1 | Complete |
| OPS-02 | Phase 1 | Complete |
| OPS-03 | Phase 3 | Complete |
| OPS-04 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0

---
*Requirements defined: 2026-04-02*
*Last updated: 2026-04-03 after Phase 03 execution completed DATA-05, PIPE-01, and OPS-03*
