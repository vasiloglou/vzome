# Requirements: Materials Design Program

**Defined:** 2026-04-03
**Core Value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.

## v1.1 Requirements

### Closed-Loop Suggestions

- [x] **LLM-06**: The platform can turn an acceptance-pack analysis into a
  structured campaign proposal over composition regions and/or Zomic motif
  edits.
- [x] **LLM-08**: An operator can approve a proposal and materialize it into a
  file-backed campaign spec that `llm-generate` can execute reproducibly.
- [ ] **LLM-09**: The platform can replay a saved campaign and recover the same
  proposal, eval-set, acceptance-pack, and launch inputs for comparison.

### Workflow Integration

- [x] **LLM-10**: Approved campaigns can launch `llm-generate` and emit
  standard `CandidateRecord` artifacts that continue through the existing
  downstream pipeline.
- [ ] **LLM-11**: Campaign outcomes can be compared against the originating
  acceptance pack and prior benchmark lane so operators can judge whether the
  loop improved or regressed.

### Operations and Governance

- [x] **OPS-05**: No suggestion mutates generation inputs, campaign state, or
  active-learning artifacts without an explicit operator approval step.
- [x] **OPS-06**: Every campaign records lineage from acceptance pack and eval
  set through approved suggestion, generation run, downstream artifacts, and
  operator decisions.
- [ ] **OPS-07**: The closed-loop workflow ships with an operator runbook and
  safe defaults for dry-run, approval, execution, and replay.

## v2+ Requirements

### LLM Expansion

- **LLM-07**: Add fine-tuned local inference serving for Zomic generation and/or
  materials-synthesis assessment after the closed-loop workflow is stable.
- **LLM-12**: Add optional autonomous campaign execution only after the
  operator-governed closed-loop path proves reliable.

### Pipeline Expansion

- **PIPE-06**: Add more target chemistries beyond the current QC-centered
  systems.
- **PIPE-07**: Add automated release gates and benchmark dashboards for every
  source/backend combination.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Local or fine-tuned model serving in v1.1 | It would dilute the immediate goal of making the closed-loop workflow operationally credible |
| Fully autonomous loop execution | Operator approval remains mandatory until replay and comparison are stable |
| New chemistry expansion as the headline of this milestone | The milestone focus is Project 3 closed-loop workflow, not breadth |
| New UI-first orchestration surface | The existing CLI and file-backed contracts are sufficient for this milestone |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LLM-06 | Phase 13 | Complete |
| OPS-05 | Phase 13 | Complete |
| LLM-08 | Phase 14 | Complete |
| LLM-10 | Phase 14 | Complete |
| OPS-06 | Phase 14 | Complete |
| LLM-09 | Phase 15 | Pending |
| LLM-11 | Phase 15 | Pending |
| OPS-07 | Phase 15 | Pending |

**Coverage:**
- v1.1 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0

---
*Requirements defined: 2026-04-03*
*Last updated: 2026-04-04 after completing Phase 14 audit-gap closure*
