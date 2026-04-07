# Roadmap: Materials Design Program

## Overview

`v1.6` is now implemented end to end and ready for milestone archival. The
milestone goal was to decide whether a small curated set of downloaded external
materials LLMs deserves deeper workflow investment by benchmarking them on
shipped translation artifacts against current promoted or explicitly pinned
internal controls in one reproducible, fidelity-aware workflow.

## Milestones

- ✅ **v1.5 External Materials-LLM Translation Bridge MVP** - Phases 31-33
  (shipped 2026-04-07)
- ✅ **v1.6 Translator-Backed External Materials-LLM Benchmark MVP** - Phases
  34-36 (shipped 2026-04-07; archival pending)

## Phases

**Phase Numbering:**
- Integer phases continue from the previous milestone.
- `v1.6` starts at Phase 34 because `v1.5` ended at Phase 33.

- [x] **Phase 34: Benchmark Pack and Freeze Contract** - Freeze a (completed 2026-04-07)
  fidelity-aware translated benchmark set from shipped bundles.
- [x] **Phase 35: External Target Registration and Reproducible Execution** - (completed 2026-04-07)
  Register curated downloaded external models as immutable, smoke-tested
  benchmark targets.
- [x] **Phase 36: Comparative Benchmark Workflow and Fidelity-Aware
  Scorecards** - (completed 2026-04-07) Run shared external-vs-internal
  benchmarks and emit decision-grade scorecards.

## Phase Details

### Phase 34: Benchmark Pack and Freeze Contract
**Goal**: Operators can freeze one trustworthy translated benchmark pack from
shipped translation bundles so later external-versus-internal comparisons run
on an explicit, fidelity-aware case slice.
**Depends on**: Phase 33
**Requirements**: LLM-31
**Success Criteria** (what must be TRUE):
  1. Operator can freeze a benchmark set from one or more shipped translation
     bundles using explicit rules for system, target family, fidelity tier, and
     representational-loss posture.
  2. Operator can inspect the frozen benchmark set and see which translated
     cases were included or excluded under those rules.
  3. The frozen benchmark set records its source translation bundles and filter
     contract as file-backed lineage that can be reused unchanged in later
     benchmark runs.
**Plans**: 3 plans

Plans:
- [x] `34-01-PLAN.md` - Define the translated benchmark-pack contract, exclusion vocabulary, and storage layout.
- [x] `34-02-PLAN.md` - Freeze included and excluded benchmark rows from shipped translation bundles with reusable lineage.
- [x] `34-03-PLAN.md` - Add CLI freeze and inspect commands, an example freeze spec, and operator docs.

### Phase 35: External Target Registration and Reproducible Execution
**Goal**: Operators can register each curated downloaded external materials LLM
as an immutable benchmark target with reproducible execution metadata before
milestone-grade comparison begins.
**Depends on**: Phase 34
**Requirements**: OPS-17
**Success Criteria** (what must be TRUE):
  1. Operator can register a curated external model with pinned revision or
     snapshot identity, compatible translation families, runtime settings, and
     smoke-check status.
  2. Operator can resolve the registered target back to the same local snapshot
     and runtime contract on repeated benchmark attempts.
  3. Each registered target exposes reproducibility-grade environment lineage
     before benchmark execution, so operators can tell what model bits and
     runtime context were actually used.
**Plans**: 3 plans

Plans:
- [x] `35-01-PLAN.md` - Define the external-target registration, smoke, and environment contract plus storage layout.
- [x] `35-02-PLAN.md` - Implement immutable registration, environment capture, and smoke persistence for curated external targets.
- [x] `35-03-PLAN.md` - Add CLI register/inspect/smoke commands, example specs, and operator docs.

### Phase 36: Comparative Benchmark Workflow and Fidelity-Aware Scorecards
**Goal**: Operators can run one comparative benchmark workflow across curated
external models and current promoted or explicitly pinned internal controls,
then inspect fidelity-aware scorecards that support an evidence-based
next-milestone decision.
**Depends on**: Phase 35
**Requirements**: LLM-32, LLM-33, OPS-18
**Success Criteria** (what must be TRUE):
  1. Operator can run one typed benchmark workflow that executes curated
     external models and current promoted or explicitly pinned internal
     controls against the same frozen translated benchmark cases.
  2. Each benchmark run writes per-target artifacts and summaries that expose
     the control-arm identity, fidelity posture, eligible counts, excluded
     counts, and captured environment lineage through CLI and documentation
     surfaces.
  3. Benchmark scorecards are target-family-aware and fidelity-aware rather
     than one blended leaderboard, and they report internal-control deltas on
     the shared eligible slice.
  4. Scorecards emit clear recommendation lines about whether each external
     model warrants deeper investment, more targeted follow-up, or no further
     milestone expansion.
**Plans**: 3 plans

Plans:
- [x] `36-01-PLAN.md` - Define the comparative benchmark contract, scorecard schema, and artifact layout.
- [x] `36-02-PLAN.md` - Implement benchmark execution, per-target artifact writing, and fidelity-aware scorecard aggregation.
- [x] `36-03-PLAN.md` - Add benchmark execute/inspect CLI commands, an example spec, and operator docs.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 34. Benchmark Pack and Freeze Contract | 3/3 | Complete | 2026-04-07 |
| 35. External Target Registration and Reproducible Execution | 3/3 | Complete | 2026-04-07 |
| 36. Comparative Benchmark Workflow and Fidelity-Aware Scorecards | 3/3 | Complete | 2026-04-07 |
