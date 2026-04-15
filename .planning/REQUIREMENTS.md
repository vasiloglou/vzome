# Requirements: Materials Design Program

**Defined:** 2026-04-15
**Core Value:** Build one reproducible system where trusted materials data,
physically grounded no-DFT validation, and LLM-guided structure generation
reinforce each other instead of living in separate prototypes.

## v1.81 Requirements

### Visualization Runtime

- [x] **VIS-01**: Operator can generate or refresh a checked visualization
  artifact for the Sc-Zn Zomic design from repo commands or documented helpers
  without manually opening desktop vZome.
- [x] **VIS-02**: Operator can render that checked visualization artifact
  programmatically through a standalone library or thin wrapper with a stable
  usage path.

### Extensive Tutorial

- [x] **DOC-06**: Reader can follow one extensive guided tutorial that keeps
  the deterministic Sc-Zn workflow spine visible while also explaining where
  each shipped LLM workflow family branches from that spine.
- [x] **DOC-07**: Reader can understand the programmatic visualization path,
  the geometry artifact chain, and what desktop vZome remains useful for
  without the docs implying full browser or service parity.

### Notebook Workflow

- [x] **OPS-25**: Operator can use the guided tutorial notebook to render or
  launch the checked design programmatically with documented preview or execute
  behavior.
- [x] **OPS-26**: Operator can use the notebook as the most detailed walkthrough
  for the shipped LLM surfaces, with richer command, artifact, and branch
  guidance than the Markdown tutorial alone.

## v2 Requirements

### Visualization Expansion

- **VIS-03**: Add richer `.vZome` / `.shapes.json` share compatibility or scene
  features once the tutorial-first visualization library is stable.
- **VIS-04**: Add browser-side editing or deeper vZome authoring parity only
  after the tutorial visualization surface is stable and there is demand beyond
  documentation.

### Product Expansion

- **LLM-12**: Add optional autonomous campaign execution only after
  multi-checkpoint selection and rollback remain reliable with promoted
  checkpoints in the workflow.
- **LLM-18**: Add controlled training and fine-tuning automation only after the
  checkpoint lifecycle surface is stable enough to support automated adaptation
  jobs, checkpoint promotion, retirement, and multi-checkpoint management
  responsibly.
- **PIPE-06**: Add more target chemistries beyond the current QC-centered
  systems.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full browser or service parity with desktop vZome in v1.81 | The milestone needs one reproducible tutorial visualization path, not a full authoring-platform replacement. |
| A long-running visualization backend as the default path | The repo is file-backed and local-first; a service would add operational surface without solving the core tutorial problem better. |
| New LLM algorithms, training flows, checkpoint mechanics, or campaign automation as part of the tutorial expansion | The user asked to demonstrate shipped functionality extensively, not to add new product surface. |
| Broad chemistry expansion beyond the checked Sc-Zn tutorial anchor | The milestone should deepen one trustworthy example rather than dilute the walkthrough with new examples. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VIS-01 | Phase 41 | Complete |
| VIS-02 | Phase 41 | Complete |
| DOC-06 | Phase 42 | Complete |
| DOC-07 | Phase 42 | Complete |
| OPS-25 | Phase 43 | Complete |
| OPS-26 | Phase 43 | Complete |

**Coverage:**
- v1.81 requirements: 6 total
- Mapped to phases: 6
- Unmapped: 0

---
*Requirements defined: 2026-04-15*
*Last updated: 2026-04-15 after roadmap creation*
