# Requirements: Materials Design Program

**Defined:** 2026-04-14
**Core Value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.

## v1.7 Requirements

### Documentation Provenance

- [x] **DOC-01**: Operator can see when
  `materials-discovery/developers-docs/podcast-deep-dive-source.md` was
  created, how it moved in the repo, and which shipped milestones and workflow
  capabilities landed after its first draft so refresh work has a concrete
  evidence base.

### Narrative Refresh

- [ ] **DOC-02**: The refreshed
  `materials-discovery/developers-docs/podcast-deep-dive-source.md` accurately
  describes the currently shipped `materials-discovery/` workflow through
  `v1.6`, including the design, evaluation, serving/checkpoint, translation,
  and comparative benchmarking surfaces at the right level of fidelity.
- [ ] **DOC-03**: The refreshed narrative clearly distinguishes shipped
  capabilities from planned or future work and points readers to the current
  source-of-truth runbooks and references for deeper technical detail.

### Guided Workflow Tutorial

- [ ] **OPS-19**: Operator can follow one end-to-end example that starts from a
  current Zomic-backed or built-in system config, runs the design/generate/
  evaluate/report workflow, and records the key artifact paths produced at each
  stage.
- [ ] **OPS-20**: The tutorial explains how to interpret the current screening,
  validation, ranking, and report artifacts for the worked example so a reader
  can understand what properties, evidence, and risk signals the tool exposes
  today.
- [ ] **OPS-21**: The tutorial shows how to take the same example into the
  vZome/Zomic visualization path, including the exact design/export artifacts
  or commands needed to inspect the geometry with the existing toolchain.

## v2 Requirements

### Product Expansion

- **LLM-12**: Add optional autonomous campaign execution only after
  multi-checkpoint selection and rollback remain reliable with promoted
  checkpoints in the workflow.
- **LLM-18**: Add controlled training and fine-tuning automation only after the
  checkpoint lifecycle surface is stable enough to support automated
  adaptation jobs, checkpoint promotion, retirement, and multi-checkpoint
  management responsibly.
- **PIPE-06**: Add more target chemistries beyond the current QC-centered
  systems.

## Out of Scope

| Feature | Reason |
|---------|--------|
| New discovery algorithms, serving lanes, checkpoint lifecycle features, or external benchmark mechanics in v1.7 | This milestone is about documentation and onboarding alignment for the shipped surface, not another tooling expansion. |
| Automated reverse import, new visualization exporters, or new vZome bridge code purely for tutorial polish | The tutorial should teach the current toolchain rather than quietly expand it. |
| Broad website or marketing refresh outside the `materials-discovery/` documentation set | The immediate gap is accuracy and usability in the repo docs, not a larger publishing project. |
| Autonomous campaign automation or checkpoint training work | Those remain future product milestones and would dilute the documentation/tutorial goal. |
| New benchmark datasets or chemistry expansion solely to make examples look broader | One honest, checked example is more valuable here than wider but less verified coverage. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DOC-01 | Phase 37 | Complete |
| DOC-02 | Phase 38 | Pending |
| DOC-03 | Phase 38 | Pending |
| OPS-19 | Phase 39 | Pending |
| OPS-20 | Phase 39 | Pending |
| OPS-21 | Phase 39 | Pending |

**Coverage:**
- v1.7 requirements: 6 total
- Mapped to phases: 6
- Unmapped: 0

---
*Requirements defined: 2026-04-14*
*Last updated: 2026-04-14 after creating milestone v1.7 roadmap*
