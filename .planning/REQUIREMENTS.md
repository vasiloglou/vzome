# Requirements: Materials Design Program

**Defined:** 2026-04-05
**Core Value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.

## v1.2 Requirements

### LLM Serving

- [ ] **LLM-13**: An operator can run `mdisc llm-generate` against a configured
  local serving lane for Zomic generation without changing standard
  `CandidateRecord` or `llm_generate` manifest contracts.
- [ ] **LLM-14**: Manual generation and approved campaigns can target
  configured `general_purpose` and `specialized_materials` lanes with
  deterministic resolution and recorded lane-selection provenance.
- [ ] **LLM-15**: The platform can use at least one specialized materials model
  path for a real workflow role, such as synthesis-aware evaluation or
  QC-conditioned generation, while remaining additive to the existing LLM
  workflow. This does not assume off-the-shelf specialized models are already
  Zomic-native.

### Workflow Integration

- [ ] **LLM-16**: `llm-launch`, `llm-replay`, and `llm-compare` remain
  compatible when the originating run used a local or specialized lane.
- [ ] **LLM-17**: The platform can benchmark hosted, local, and specialized
  lanes against the same acceptance-pack or benchmark context so operators can
  judge quality, cost, and workflow tradeoffs.

### Operations and Governance

- [ ] **OPS-08**: Local and specialized serving configs fail early with clear
  diagnostics for missing model files, missing endpoints, incompatible lane
  selections, or unavailable runtime dependencies.
- [ ] **OPS-09**: Every local or specialized run records auditable serving
  lineage including adapter type, provider/model lane, model identifier or
  checkpoint, runtime endpoint or path, and launch/replay provenance.
- [ ] **OPS-10**: The workflow ships with an operator runbook for setup, smoke
  tests, lane fallback, and reproducible benchmark comparison across hosted and
  local/specialized serving paths.

## v2+ Requirements

### LLM Expansion

- **LLM-12**: Add optional autonomous campaign execution only after the
  operator-governed workflow remains reliable with the broader serving surface.
- **LLM-18**: Add training/fine-tuning automation only after local serving and
  comparative benchmark workflows are stable enough to judge new checkpoints
  responsibly, including Zomic-native local generation adaptation and
  checkpoint management.

### Platform Expansion

- **PIPE-06**: Add more target chemistries beyond the current QC-centered
  systems.
- **PIPE-07**: Add automated release gates and benchmark dashboards for every
  source/backend/serving combination.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fully autonomous campaign execution in v1.2 | Operator approval and manual continuation are still the safety boundary |
| Foundation-model training from scratch | Too expensive and premature before serving and comparison workflows mature |
| New chemistry breadth as the headline | The milestone focus is Project 3 serving depth, not expanding system coverage |
| UI-first orchestration surface | The existing CLI and file-backed artifacts remain the right control surface |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LLM-13 | Phase 22 | Pending |
| LLM-14 | Phase 22 | Pending |
| OPS-08 | Phase 22 | Pending |
| LLM-15 | Phase 23 | Pending |
| LLM-16 | Phase 23 | Pending |
| OPS-09 | Phase 23 | Pending |
| LLM-17 | Phase 24 | Pending |
| OPS-10 | Phase 24 | Pending |

**Coverage:**
- v1.2 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0

---
*Requirements defined: 2026-04-05*
*Last updated: 2026-04-05 after planning v1.2 audit-closure phases*
