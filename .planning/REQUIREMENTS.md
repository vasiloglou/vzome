# Requirements: Materials Design Program

**Defined:** 2026-04-07
**Core Value:** Build one reproducible system where trusted materials data, physically grounded no-DFT validation, and LLM-guided structure generation reinforce each other instead of living in separate prototypes.

## v1.6 Requirements

### External Benchmark Sets

- [x] **LLM-31**: Operator can freeze a translated benchmark set from one or more shipped translation bundles with explicit inclusion and exclusion rules by system, target family, fidelity tier, and representational-loss posture.

### External Benchmark Operations

- [x] **OPS-17**: Operator can register each curated downloaded external materials LLM as an immutable benchmark target with pinned revision or snapshot identity, compatible translation families, runtime settings, smoke checks, and reproducibility-grade environment lineage before benchmark execution.
- [x] **OPS-18**: Operator can inspect translated benchmark sets, external model registrations, and benchmark summaries through CLI and documentation surfaces that expose fidelity posture, control-arm identity, exclusions, and environment capture without reverse-engineering raw artifacts.

### Comparative Benchmarking

- [x] **LLM-32**: Operator can run one typed benchmark workflow that executes curated downloaded external materials LLMs and current promoted or explicitly pinned internal controls against the same translated benchmark cases and records per-target run artifacts.
- [x] **LLM-33**: Benchmark summaries are target-family-aware and fidelity-aware, report eligible and excluded counts plus internal-control deltas, and emit decision-grade recommendation lines about whether deeper external-model investment is justified.

## v2 Requirements

### LLM Expansion

- **LLM-12**: Add optional autonomous campaign execution only after multi-checkpoint selection and rollback remain reliable with promoted checkpoints in the workflow.
- **LLM-18**: Add controlled training and fine-tuning automation only after the checkpoint lifecycle surface is stable enough to support automated adaptation jobs, checkpoint promotion, retirement, and multi-checkpoint management responsibly.

### Platform Expansion

- **PIPE-06**: Add more target chemistries beyond the current QC-centered systems.
- **PIPE-07**: Add automated release gates and benchmark dashboards for every source/backend/serving/checkpoint combination.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full training or fine-tuning automation for external models in v1.6 | This milestone is supposed to decide whether deeper investment is warranted, not assume it upfront. |
| Autonomous campaign execution based on benchmark winners | External-model value still needs operator-reviewed evidence before the workflow expands its autonomy. |
| Broad model-zoo or generic external serving platform support | A generic external-model platform would absorb the milestone and delay the actual benchmark question. |
| Broad chemistry or source expansion as the milestone headline | Dataset breadth would blur whether results changed because of model quality or benchmark movement. |
| One blended leaderboard across incompatible artifact families and fidelity tiers | A single headline score would hide representational mismatch and make the results scientifically misleading. |
| UI-first benchmark dashboards or services | The repo remains CLI-first, file-backed, and operator-governed for this milestone. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| LLM-31 | Phase 34 | Complete |
| OPS-17 | Phase 35 | Complete |
| LLM-32 | Phase 36 | Complete |
| LLM-33 | Phase 36 | Complete |
| OPS-18 | Phase 36 | Complete |

**Coverage:**
- v1.6 requirements: 5 total
- Mapped to phases: 5
- Unmapped: 0

---
*Requirements defined: 2026-04-07*
*Last updated: 2026-04-07 after completing Phase 36 and verifying v1.6 requirements*
