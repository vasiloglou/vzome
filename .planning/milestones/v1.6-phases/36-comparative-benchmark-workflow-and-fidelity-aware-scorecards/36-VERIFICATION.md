---
phase: 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards
verified: 2026-04-07T08:26:52Z
status: passed
score: 4/4 must-haves verified
---

# Phase 36: Comparative Benchmark Workflow and Fidelity-Aware Scorecards Verification Report

**Phase Goal:** Operators can run one comparative benchmark workflow across curated external materials LLMs and current promoted or explicitly pinned internal controls, then inspect fidelity-aware scorecards that support an evidence-based next-milestone decision.
**Verified:** 2026-04-07T08:26:52Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | An operator can run one typed benchmark workflow that replays a frozen translated benchmark set against both external targets and internal controls and writes deterministic per-target artifacts. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/llm/schema.py:2202`, `:2294`, `:2384`, `:2455`, and `:2531` define the typed benchmark spec, case-result, run-manifest, target-summary, and benchmark-summary contracts; `materials-discovery/src/materials_discovery/llm/storage.py:273`, `:278`, `:290`, `:305`, `:313`, and `:321` define the benchmark and per-target artifact layout; `materials-discovery/src/materials_discovery/llm/external_benchmark.py:109`, `:589`, and `:698` load the spec, build the fidelity-aware summary, and execute the benchmark end to end; focused execution coverage in `materials-discovery/tests/test_llm_external_benchmark_core.py:318`, `:403`, and `:480` proves artifact writing, explicit exclusions, and smoke-failure handling. |
| 2 | The benchmark operator surface exposes control-arm identity, eligible/excluded counts, fidelity posture, and environment lineage through shipped CLI and documentation surfaces instead of raw JSON spelunking. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/cli.py:452`, `:467`, `:1823`, and `:1840` add the execute/inspect command pair plus human-readable scorecard trace helpers; `materials-discovery/tests/test_llm_external_benchmark_cli.py:170-292` proves JSON output, inspect output, target filtering, and code-2 failures; `materials-discovery/tests/test_cli.py:288-289` plus a direct `uv run mdisc --help | rg "llm-external-benchmark|llm-inspect-external-benchmark"` spot-check confirm discoverability; the shipped example spec and docs live at `materials-discovery/configs/llm/al_cu_fe_external_benchmark.yaml:1-30`, `materials-discovery/developers-docs/llm-external-benchmark-runbook.md:1-199`, `materials-discovery/developers-docs/configuration-reference.md:439-468`, `materials-discovery/developers-docs/pipeline-stages.md:1486-1576`, and `materials-discovery/developers-docs/index.md:44-99`. |
| 3 | Benchmark scorecards stay target-family-aware and fidelity-aware, and they report internal-control deltas only on the shared eligible slice. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/llm/external_benchmark.py:492` computes shared eligible control deltas, `:589` aggregates overall plus by-target-family and by-fidelity summaries, and `materials-discovery/tests/test_llm_external_benchmark_core.py:403-479` proves unsupported target families become explicit exclusions instead of silent denominator shrinkage. |
| 4 | Recommendation lines are decision-grade but bounded: they privilege the periodic-safe exact/anchored slice and avoid overclaiming from diagnostic-only or lossy evidence. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/llm/external_benchmark.py:540` implements bounded recommendation logic; `materials-discovery/tests/test_llm_external_benchmark_core.py:554-706` proves a target can look better overall yet still be marked not competitive when its periodic-safe slice underperforms; `materials-discovery/tests/test_llm_external_benchmark_cli.py:83`, `:183`, and `:209` lock the same periodic-safe recommendation posture through the CLI surface and typed summary JSON. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/schema.py` | Typed Phase 36 benchmark contracts | ✓ VERIFIED | Benchmark target, spec, case-result, run-manifest, summary, and control-delta models are present at `:2126-2564`. |
| `materials-discovery/src/materials_discovery/llm/storage.py` | Deterministic `llm_external` benchmark artifact layout | ✓ VERIFIED | Benchmark and per-target storage helpers exist at `:273-326`. |
| `materials-discovery/src/materials_discovery/llm/external_benchmark.py` | Spec loading, execution, artifact writing, and scorecard aggregation | ✓ VERIFIED | The Phase 36 core exists at `:109-797`. |
| `materials-discovery/src/materials_discovery/cli.py` | Benchmark execute and inspect commands | ✓ VERIFIED | `llm-external-benchmark` and `llm-inspect-external-benchmark` are implemented at `:1823-1876`. |
| `materials-discovery/configs/llm/al_cu_fe_external_benchmark.yaml` | Shipped benchmark spec example | ✓ VERIFIED | The committed example spec exists at `:1-30` and wires one frozen benchmark pack, one external target arm, and one internal control arm together. |
| `materials-discovery/developers-docs/llm-external-benchmark-runbook.md` | Operator runbook for benchmark execution and inspect flow | ✓ VERIFIED | Documents prerequisites, execute/inspect commands, artifact layout, scorecard interpretation, and advisory scope boundaries at `:1-199`. |
| `materials-discovery/tests/test_llm_external_benchmark_schema.py` | Contract and storage coverage | ✓ VERIFIED | Included in the phase-wide focused verification run that passed `35` tests. |
| `materials-discovery/tests/test_llm_external_benchmark_core.py` | Execution and scorecard coverage | ✓ VERIFIED | Covers artifact writing, exclusions, smoke failures, and periodic-safe recommendation logic at `:318-706`. |
| `materials-discovery/tests/test_llm_external_benchmark_cli.py` | CLI benchmark workflow coverage | ✓ VERIFIED | Covers execute JSON, inspect traces, filtering, and code-2 failures at `:1-292`. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/external_benchmark.py` | `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` | Frozen benchmark-set manifest and included-row reuse | WIRED | Phase 36 loads `TranslatedBenchmarkSetManifest` plus included rows rather than rescanning live bundles, anchored by `external_benchmark.py:109-136`. |
| `materials-discovery/src/materials_discovery/llm/external_benchmark.py` | `materials-discovery/src/materials_discovery/llm/external_targets.py` | Registered external target identity, environment, and smoke reuse | WIRED | Phase 36 resolves registrations, captures environment lineage, and consumes smoke results before execution in `external_benchmark.py:27-30` and `:731-760`. |
| `materials-discovery/src/materials_discovery/llm/external_benchmark.py` | `materials-discovery/src/materials_discovery/llm/launch.py` + `runtime.py` | Internal control lane resolution and `LlmServingIdentity` reuse | WIRED | Internal controls route through `resolve_serving_lane`, `build_serving_identity`, and `resolve_llm_adapter` in `external_benchmark.py:24-25` and `:337-380`. |
| `materials-discovery/src/materials_discovery/cli.py` | `materials-discovery/src/materials_discovery/llm/external_benchmark.py` | Operator execute/inspect entrypoints | WIRED | The CLI executes the benchmark core and prints typed scorecards at `cli.py:1823-1876`. |
| `materials-discovery/developers-docs/llm-external-benchmark-runbook.md` | `materials-discovery/configs/llm/al_cu_fe_external_benchmark.yaml` | Example operator workflow | WIRED | The runbook points operators at the committed example spec and explains its Phase 34/35 prerequisites at `llm-external-benchmark-runbook.md:39-56`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/external_benchmark.py` | `target_manifests`, `target_results`, `summary` | Frozen translated benchmark manifest + registered external targets + internal controls | Yes. Focused execution coverage proves `run_manifest.json`, `case_results.jsonl`, `raw_responses.jsonl`, `scorecard_by_case.jsonl`, and `benchmark_summary.json` are written under the deterministic `llm_external` root. | ✓ FLOWING |
| `materials-discovery/src/materials_discovery/cli.py` | inspect trace lines | Typed `benchmark_summary.json` | Yes. CLI coverage proves the inspect command prints control-arm identity, fidelity slices, control deltas, and recommendation lines from a typed benchmark summary. | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Full Phase 36 focused verification slice stays green | `cd materials-discovery && uv run pytest tests/test_llm_external_benchmark_schema.py tests/test_llm_external_benchmark_core.py tests/test_llm_external_benchmark_cli.py tests/test_cli.py -q` | `35 passed in 0.49s` | ✓ PASS |
| Root CLI help exposes the Phase 36 operator workflow | `cd materials-discovery && uv run mdisc --help \| rg "llm-external-benchmark|llm-inspect-external-benchmark"` | Help output listed both Phase 36 commands with descriptions. | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `LLM-32` | `36-01`, `36-02`, `36-03` | Operator can run one typed benchmark workflow that executes curated downloaded external materials LLMs and current promoted or explicitly pinned internal controls against the same translated benchmark cases and records per-target run artifacts. | ✓ SATISFIED | Typed contracts plus deterministic storage in `schema.py` and `storage.py`, execution/artifact writing in `external_benchmark.py`, CLI access in `cli.py`, example spec/runbook coverage, and the `35 passed` focused phase verification slice satisfy the requirement end to end. |
| `LLM-33` | `36-01`, `36-02`, `36-03` | Benchmark summaries are target-family-aware and fidelity-aware, report eligible/excluded counts plus internal-control deltas, and emit decision-grade recommendation lines about whether deeper external-model investment is justified. | ✓ SATISFIED | `build_external_benchmark_summary(...)`, `_shared_slice_deltas(...)`, and `_recommendation_lines(...)` in `external_benchmark.py` plus the periodic-safe recommendation tests and inspect CLI output satisfy the requirement. |
| `OPS-18` | `36-02`, `36-03` | Operator can inspect translated benchmark sets, external model registrations, and benchmark summaries through CLI and documentation surfaces that expose fidelity posture, control-arm identity, exclusions, and environment capture without reverse-engineering raw artifacts. | ✓ SATISFIED | Phase 34 inspect, Phase 35 inspect/smoke, and the new Phase 36 inspect/runbook/configuration-reference surfaces together complete the operator inspection chain; the direct CLI help spot-check and focused CLI tests verify discoverability and readability. |

Orphaned requirements for Phase 36: none.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| Phase 36 implementation set | n/a | No TODO/FIXME/stub markers or hollow CLI wrappers were required to satisfy the phase goal. | Info | No blocker anti-patterns detected. |

### Human Verification Required

None required for phase-goal verification. The delivered surface is CLI-first
and file-backed, and the critical operator behaviors were verified through the
focused automated benchmark suite plus real CLI help discovery.

### Gaps Summary

No gaps found. Phase 36 now delivers the typed comparative benchmark contract,
the replayable execution core, operator execute/inspect commands, a shipped
example spec, and documentation that keeps scorecard recommendations explicit
and advisory.

---

_Verified: 2026-04-07T08:26:52Z_  
_Verifier: Codex (manual verifier path aligned to gsd-verifier expectations)_
