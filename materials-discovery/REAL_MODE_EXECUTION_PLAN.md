# REAL_MODE_EXECUTION_PLAN

This document defines the execution plan to move `materials-discovery/` from scaffold-grade deterministic internals to production-grade no-DFT implementations.

## 0. Current Execution Status (March 6, 2026)

- RM0: completed in code (backend switch + interface freeze guardrails).
- RM1: completed in code (pinned ingest adapter, QA, ingest manifest, integration test).
- RM2-RM6: implemented as runnable no-DFT real-mode software pathways with:
  - stage manifests (`data/manifests/`),
  - calibration artifacts (`data/calibration/`),
  - model/feature registry outputs (`data/registry/models`, `data/registry/features`),
  - pipeline manifest emission from report stage,
  - split fast/integration CI and real-mode run script.
- Phase-1 scientific hardening (started March 6, 2026):
  - descriptor-based real-mode screening and validation scoring (replacing hash-jitter logic),
  - strict real-mode element/pair prior gating for supported systems,
  - real-mode XRD confidence tied to ingested reference-phase compositions.
- Phase-2 scientific hardening (started March 6, 2026):
  - reference-aware proxy hull using ingested competing phases,
  - convex-mixture baseline selection for ternary compositions,
  - validation calibration now tracking reference-match distance,
  - ranking now emits calibrated stability/OOD/novelty decision components.
- RM5 hardening (started March 6, 2026):
  - active-learning surrogate now trains on descriptor + screening features,
  - acquisition now balances predicted success, uncertainty, novelty, and OOD risk,
  - model registry rows now capture surrogate threshold, radius, and top-k precision diagnostics.
- RM6 hardening (started March 6, 2026):
  - report-stage XRD proxies are now descriptor-driven instead of hash-seeded,
  - experiment reports now carry recommendation tiers, evidence blocks, and risk flags,
  - report calibration now emits release-gate and reproducibility diagnostics.
- Phase-3 scientific hardening (started March 6, 2026):
  - validation now resolves fixture-backed committee/phonon/MD/XRD adapters in real mode,
  - ranking, active learning, and report thresholds now load from pinned benchmark corpora,
  - candidate generation now applies Z[phi] geometry transforms instead of pairwise coefficient jitter.

Note: these are production-oriented software pathways; domain-model fidelity can be raised iteratively by swapping adapters and calibrations without changing CLI/schema contracts.

## 1. Program Guardrails

- Preserve existing CLI contract (`mdisc ingest|generate|screen|hifi-validate|hifi-rank|active-learn|report`).
- Preserve JSON schema compatibility for candidate and summary artifacts.
- Keep deterministic `mock` backend available for CI and local reproducibility.
- Implement production logic behind a `real` backend switch.
- Keep no-DFT boundary explicit: no direct DFT dependency in required execution path.

## 2. Program Dates and Milestones

Program start: **March 9, 2026**
Program target completion: **August 7, 2026**

| Milestone | Dates | Scope | Hard Exit Criteria |
|---|---|---|---|
| RM0 Baseline and Interface Freeze | 2026-03-09 to 2026-03-13 | Backend mode switch, artifact naming/versioning contract, config freeze | `mock` path still green; backend interface tests added; docs updated |
| RM1 Real Ingestion | 2026-03-16 to 2026-03-27 | Real data connectors, normalization maps, provenance and data QA | Ingestion reproducible from pinned snapshots; QA report generated |
| RM2 Real Generation | 2026-03-30 to 2026-04-17 | True approximant/template parameterization, geometry validity checks, dedupe at scale | >=10k candidates produced for one ternary system with validity and dedupe metrics |
| RM3 Real Screening | 2026-04-20 to 2026-05-15 | MLIP relax adapters, threshold calibration, shortlist audit | Top 1-5% shortlist reproducible; calibration metrics published |
| RM4 Real Validation | 2026-05-18 to 2026-06-19 | Committee prediction, uncertainty calibration, proxy hull, phonon/MD checks | >=200 validated candidates with complete uncertainty/pass-fail traces |
| RM5 Real Active Learning | 2026-06-22 to 2026-07-10 | Surrogate retraining, model registry, acquisition policy rollout | New model version improves at least one top-k metric on held-out set |
| RM6 Real Rank/Report + Hardening | 2026-07-13 to 2026-08-07 | Ranking calibration, XRD report pack, orchestration hardening | End-to-end runbook complete; release-gate metrics satisfied |

## 3. Acceptance Test Matrix

### RM0 Acceptance Tests

- `uv run pytest` remains green for current suite.
- New backend-interface tests validate parity between `mock` and `real` entry points.
- Config validation rejects missing backend-dependent required fields with exit code `2`.

### RM1 Acceptance Tests

- Ingestion with pinned external snapshot is reproducible (identical output hashes on rerun).
- Duplicate-rate, null-rate, and composition-sum QA checks pass thresholds.
- Provenance fields include source, snapshot version, and normalization version for every record.

### RM2 Acceptance Tests

- Generation emits required count at scale (`>=10k`) without schema violations.
- Duplicate candidate rate below defined cap for baseline systems.
- Geometry validity checks (distance/pathological occupancy rules) produce audit report.

### RM3 Acceptance Tests

- Real relax adapter path executes for selected backend(s) on reference batch.
- Screening threshold calibration artifact generated and versioned.
- Shortlist reproducibility test passes under fixed seed/config/model version.

### RM4 Acceptance Tests

- Committee metrics (`energy`, `uncertainty`, `delta_e_proxy_hull`, `phonon/md/xrd`) populated for all validated candidates.
- Uncertainty calibration report generated (coverage or reliability style metric).
- Validation stage produces pass/fail trace for each candidate and each sub-check.

### RM5 Acceptance Tests

- Surrogate training artifact registered with immutable version ID.
- Acquisition strategy test confirms no re-selection of already validated IDs.
- At least one controlled metric improves over previous model version on held-out data.

### RM6 Acceptance Tests

- Ranking stability test passes on fixed inputs.
- Report bundle contains ranked shortlist, XRD patterns, and provenance links.
- End-to-end orchestration test from ingest->report passes in clean environment.

## 4. Required New Artifacts

- `data/registry/` metadata for dataset snapshots and model versions.
- Backend capability matrix (supported systems, required dependencies, fallback behavior).
- Calibration reports for screening, uncertainty, and ranking.
- End-to-end run manifest containing config hash, backend versions, and output hashes.

## 5. Operationalization Plan

- CI split:
  - Fast path on every push (`schema`, deterministic unit tests, type/lint).
  - Heavy path on schedule/manual dispatch (`real` backend integration tests).
- Orchestration:
  - Add one reproducible workflow definition for full pipeline execution.
  - Persist run manifests and stage outputs with immutable IDs.
- Observability:
  - Stage-level counters and timings.
  - Failure taxonomy by stage and backend.

## 6. Release Gates

A real-mode release is allowed only when all gates below are met:

1. Contract gate: CLI and schema compatibility preserved.
2. Reproducibility gate: fixed-input reruns produce identical ranked/report artifacts.
3. Data gate: ingestion QA thresholds pass on pinned snapshots.
4. Model gate: committee uncertainty and shortlist quality metrics are non-regressing.
5. Operations gate: end-to-end runbook validated on clean checkout.

## 7. First Two-Week Execution Packet (2026-03-09 to 2026-03-20)

1. Add backend mode config (`backend: mock|real`) and pluggable backend registry.
2. Define artifact manifest schema (`run_id`, `config_hash`, `backend_versions`, `output_hashes`).
3. Add real-ingestion connector interfaces and one pinned source adapter.
4. Add data QA module and baseline thresholds.
5. Add integration test target for RM1 with snapshot fixture.

Completion criteria for this packet:

- New interfaces merged without breaking current commands.
- RM1 ingestion test run reproducible twice with identical hashes.
- Program dashboard document updated with current metric baselines.
