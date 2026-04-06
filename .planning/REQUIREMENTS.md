# Requirements: Materials Design Program

**Defined:** 2026-04-06
**Core Value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.

## v1.5 Requirements

### Representation Interoperability

- [x] **LLM-27**: The platform can translate a compiled Zomic candidate into a
  deterministic structure-interoperability artifact with explicit cell, species,
  positions, provenance, and representation metadata that downstream
  crystal/material LLM workflows can reuse.
- [ ] **LLM-28**: The platform can export supported translated candidates as CIF
  artifacts for CIF-oriented external materials LLM workflows without requiring
  ad hoc notebook conversion.
- [ ] **LLM-29**: The platform can export at least one model-oriented
  crystal/material string encoding from the same translated candidate for
  CrystalTextLLM- or CSLLM-style downstream workflows.
- [x] **LLM-30**: Every translation artifact records whether it is exact,
  anchored, approximate, or lossy relative to the source Zomic candidate, plus
  the reason when the QC-native structure cannot be represented exactly in the
  target format.

### Operations and Governance

- [ ] **OPS-15**: Operators can create, inspect, and trace translation artifacts
  through a file-backed CLI/documented workflow instead of hand-written export
  scripts.
- [ ] **OPS-16**: Developer and runbook docs explain the intended downstream
  target formats, where representational loss occurs, and when CIF/material
  string exports are appropriate versus when Zomic must remain the source of
  truth.

## v2+ Requirements

### LLM Expansion

- **LLM-12**: Add optional autonomous campaign execution only after
  multi-checkpoint selection and rollback remain reliable with promoted
  checkpoints in the workflow.
- **LLM-18**: Add controlled training and fine-tuning automation only after the
  checkpoint lifecycle surface is stable enough to support automated adaptation
  jobs, checkpoint promotion, retirement, and multi-checkpoint management
  responsibly.
- **LLM-31**: Run translator-backed comparative experiments against downloaded
  external materials LLMs only after the exported CIF/material-string artifacts
  are stable and auditable.

### Platform Expansion

- **PIPE-06**: Add more target chemistries beyond the current QC-centered
  systems.
- **PIPE-07**: Add automated release gates and benchmark dashboards for every
  source/backend/serving/checkpoint combination.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Lossless CIF export for every QC-native Zomic structure in v1.5 | CIF is not a faithful native representation for true quasicrystal geometry; the milestone must keep lossy boundaries explicit |
| Running external downloadable materials LLMs end to end in the milestone headline | The immediate gap is translation/export interoperability, not another serving stack |
| Automatic best-model selection across CrystaLLM, CrystalTextLLM, CSLLM, and generic instruct models | Too broad before the exported representations are stable and benchmarkable |
| Replacing Zomic as the core generation representation | Zomic remains the QC-native source of truth; the new layer is additive interoperability |
| UI-first translation management | The existing CLI and file-backed artifacts remain the right control surface |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LLM-27 | Phase 31 | Completed |
| LLM-30 | Phase 31 | Completed |
| LLM-28 | Phase 32 | Planned |
| LLM-29 | Phase 32 | Planned |
| OPS-15 | Phase 33 | Planned |
| OPS-16 | Phase 33 | Planned |

**Coverage:**
- v1.5 requirements: 6 total
- Mapped to phases: 6
- Unmapped: 0

---
*Requirements defined: 2026-04-06*
*Last updated: 2026-04-06 after completing Phase 31 Plan 01*
