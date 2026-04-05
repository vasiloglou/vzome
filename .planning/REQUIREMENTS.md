# Requirements: Materials Design Program

**Defined:** 2026-04-05
**Core Value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.

## v1.3 Requirements

### Checkpoint Lifecycle

- [ ] **LLM-19**: An operator can register a Zomic-adapted local checkpoint
  with pinned base-model, adaptation-artifact, corpus, and evaluation lineage
  so it can be selected as a configured serving lane.
- [ ] **LLM-20**: The platform can run `mdisc llm-generate` and approved
  campaign launches through at least one Zomic-adapted local checkpoint lane
  without changing standard `CandidateRecord` or manifest contracts.

### Workflow Integration

- [ ] **LLM-21**: Adapted checkpoints remain compatible with `llm-launch`,
  `llm-replay`, `llm-compare`, and `llm-serving-benchmark` so adapted-vs-
  baseline evaluation reuses the shipped workflow.
- [ ] **LLM-22**: At least one adapted checkpoint shows a measurable
  improvement in Zomic validity or parse/compile/conversion outcomes against an
  unadapted local baseline on a shared benchmark context.

### Operations and Governance

- [ ] **OPS-11**: Every adapted checkpoint records auditable lineage for base
  model, adaptation method, corpus build, eval set, revision/hash, and serving
  configuration, and fails early on incompatible registration or load attempts.
- [ ] **OPS-12**: The workflow ships with operator docs for checkpoint
  registration, smoke testing, rollback to baseline lanes, and adapted-vs-
  baseline comparison.

## v2+ Requirements

### LLM Expansion

- **LLM-12**: Add optional autonomous campaign execution only after the
  operator-governed workflow remains reliable with adapted checkpoints in the
  broader serving surface.
- **LLM-18**: Add broader training/fine-tuning automation only after the first
  adapted checkpoint workflow is stable enough to support automated checkpoint
  promotion, retirement, and multi-checkpoint management responsibly.

### Platform Expansion

- **PIPE-06**: Add more target chemistries beyond the current QC-centered
  systems.
- **PIPE-07**: Add automated release gates and benchmark dashboards for every
  source/backend/serving/checkpoint combination.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fully autonomous campaign execution in v1.3 | Operator approval and manual continuation remain the safety boundary |
| Large-scale training orchestration or checkpoint farming | The milestone focus is one credible adapted checkpoint path, not automation at scale |
| Foundation-model training from scratch | Too expensive and premature before adapted-checkpoint usefulness is proven |
| New chemistry breadth as the headline | The milestone focus is Project 3 checkpoint depth, not expanding system coverage |
| UI-first checkpoint management surface | The existing CLI and file-backed artifacts remain the right control surface |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LLM-19 | Phase 25 | Pending |
| OPS-11 | Phase 25 | Pending |
| LLM-20 | Phase 26 | Pending |
| LLM-21 | Phase 26 | Pending |
| LLM-22 | Phase 27 | Pending |
| OPS-12 | Phase 27 | Pending |

**Coverage:**
- v1.3 requirements: 6 total
- Mapped to phases: 6
- Unmapped: 0

---
*Requirements defined: 2026-04-05*
*Last updated: 2026-04-05 after starting milestone v1.3*
