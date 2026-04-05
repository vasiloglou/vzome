# Phase 21: Comparative Benchmarks and Operator Serving Workflow - Research

**Researched:** 2026-04-05
**Domain:** operator-facing comparative benchmarks across hosted, local, and specialized serving lanes
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Benchmark context authority
- **D-01:** Hosted, local, and specialized lanes should be benchmarked against
  one shared acceptance-pack or benchmark context per comparison run.
- **D-02:** Phase 21 should avoid lane-specific benchmark inputs for the main
  comparison path because they would weaken the honesty of the benchmark.
- **D-03:** Optional lane extras should not become the default benchmark path
  in this phase.

### Comparison dimensions
- **D-04:** Phase 21 benchmarks should compare quality, cost, latency, and
  operator friction together.
- **D-05:** The benchmark result should help operators decide which lane to use
  in practice, not just whether a lane technically passes.
- **D-06:** Quality-only comparisons are insufficient for this phase because
  `LLM-17` is about real operator tradeoffs across serving lanes.

### Smoke-test posture
- **D-07:** Each requested lane should pass an explicit smoke test or preflight
  check before a benchmark run begins.
- **D-08:** Phase 21 should not silently fall back during a benchmark if a
  requested lane is unavailable or unhealthy.
- **D-09:** If a lane fails smoke testing, the benchmark should stop clearly or
  mark that lane unusable according to explicit workflow rules rather than
  hiding the failure.

### Benchmark surface
- **D-10:** Phase 21 should add one operator-facing benchmark entrypoint that
  orchestrates comparable hosted, local, and specialized runs.
- **D-11:** That benchmark entrypoint should reuse the existing
  `llm-launch` / `llm-replay` / `llm-compare` machinery underneath instead of
  inventing a parallel execution pipeline.
- **D-12:** Docs-only manual stitching is not enough for this phase; the
  comparison workflow should be runnable without hand-assembling artifacts.

### Recommendation output
- **D-13:** Phase 21 should emit both typed benchmark artifacts and concise
  operator guidance.
- **D-14:** The human-readable output should make it clear when to prefer
  hosted, local, or specialized lanes under the measured conditions.
- **D-15:** Machine-readable benchmark outputs remain required so replay,
  auditing, and downstream tooling stay reproducible.

### Inherited constraints
- **D-16:** Config remains authoritative for lane availability and lane
  identities.
- **D-17:** `llm-generate` remains the single generation engine; `llm-launch`
  and `llm-replay` remain wrappers.
- **D-18:** Explicit fallback and drift behavior from Phases 19 and 20 remain
  in force.
- **D-19:** Stable artifact shapes should be preserved; Phase 21 adds richer
  benchmark and reporting outputs rather than a new artifact family.
- **D-20:** The first specialized lane remains evaluation-primary; Phase 21
  compares lanes honestly and does not pretend off-the-shelf specialized models
  are Zomic-native generators.
- **D-21:** The workflow remains operator-governed, file-backed, and
  explicitly no-DFT.

### the agent's Discretion
- The exact benchmark command name and flags
- The exact smoke-test helper breakdown and artifact naming
- The exact benchmark-summary field names and recommendation wording
- The exact way operator friction is represented, provided it stays
  machine-readable and operator-visible

### Deferred Ideas (OUT OF SCOPE)
- Fully autonomous campaign execution on top of the serving workflow
- Lane-specific benchmark contexts as the default comparison mode
- Silent fallback during comparative benchmarking
- Replacing the current CLI/file-backed workflow with a UI-first system
- Treating off-the-shelf specialized models as Zomic-native generators by
  default
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LLM-17 | The platform can benchmark hosted, local, and specialized lanes against the same acceptance-pack or benchmark context so operators can judge quality, cost, and workflow tradeoffs. | Add a typed serving-benchmark spec and summary artifact that anchors all targets to one shared acceptance-pack or campaign/benchmark context, records per-target quality metrics plus measured latency and declared cost/friction metadata, and writes one machine-readable benchmark result with operator guidance. |
| OPS-10 | The workflow ships with an operator runbook for setup, smoke tests, lane fallback, and reproducible benchmark comparison across hosted and local/specialized serving paths. | Add a dedicated benchmark CLI with mandatory smoke checks, explicit no-silent-fallback behavior, example benchmark specs/configs, and runbook/docs sections that explain setup, smoke-only mode, benchmark execution, and interpretation. |
</phase_requirements>

## Summary

Phase 21 is best treated as an operator workflow layer over the serving and
campaign machinery that is already shipped, not as a new inference stack. The
repo already has the core reusable pieces needed for a comparative benchmark:
lane resolution and readiness validation from Phase 19, honest
evaluation-primary specialized behavior from Phase 20, strict replay and
comparison artifacts from Phase 12, and typed acceptance-pack artifacts from
Phase 9. What it does not have yet is one file-backed contract that says “run
these hosted/local/specialized targets against the same context, smoke-test
them explicitly, and write a single comparable summary.”

The most important design choice is to stay honest about the specialized lane’s
role. Because the first `specialized_materials` lane is evaluation-primary, the
benchmark surface should be role-aware rather than forcing every target through
the same generation-only path. The cleanest benchmark contract is a typed spec
that anchors every target to one shared acceptance-pack context while allowing a
target to declare whether it exercises the `campaign_launch` subflow or the
`llm_evaluate` subflow. That preserves the user’s “same context” rule, reuses
the existing launch/replay/compare and evaluation machinery, and avoids
pretending that the specialized lane is already a first-class Zomic generator.

The main missing measurement gaps are cost and operator friction. Current
artifacts already provide quality signals and enough structure to measure
latency with wall-clock timing, but there is no existing repo-native billing or
setup-burden contract. The benchmark spec should therefore carry explicit,
machine-readable target metadata such as `estimated_cost_usd` and an
`operator_friction_tier`, while the runtime measures smoke-test and execution
latencies directly. This keeps the summary reproducible and honest instead of
guessing provider pricing or hiding setup burden in prose.

**Primary recommendation:** add a new typed `llm serving benchmark` contract
and module, require explicit per-target smoke checks via the existing runtime
readiness helper, reuse launch/evaluate/compare artifacts underneath, and ship
one real `Al-Cu-Fe` benchmark spec covering hosted, local, and specialized
targets plus a thinner `Sc-Zn` compatibility recipe in the runbook.

## Project Constraints (from AGENTS.md)

- The repo is a vZome monorepo including the `materials-discovery/` no-DFT
  quasicrystal pipeline.
- Every change under `materials-discovery/` must update
  `materials-discovery/Progress.md`.
- Progress updates must add a Changelog row and append a timestamped Diary
  entry under the current date heading.
- This progress-tracking rule applies to code, config, docs, experiments,
  fixes, refactors, and new systems.

## Standard Stack

### Core

| Library / Contract | Version | Purpose | Why Standard |
|--------------------|---------|---------|--------------|
| Existing campaign launch stack: `resolve_campaign_launch()`, `generate_llm_candidates()`, `LlmCampaignLaunchSummary` | repo current | Reusable launch unit for hosted/local generation targets | Already shipped, already replay-safe, and already records serving identity and acceptance-pack lineage. |
| Existing comparison stack: `build_campaign_outcome_snapshot()` + `build_campaign_comparison()` | repo current | Reusable quality baseline for launch-style targets | Already links launches back to the acceptance pack and emits typed summary lines/operators can read. |
| Existing evaluation stack: `evaluate_llm_candidates()` + `LlmEvaluateSummary` | repo current | Honest workflow role for the current specialized lane | Already lane-aware after Phase 20 and fits the evaluation-primary specialist role. |
| Existing runtime seam: `resolve_serving_lane()` + `validate_llm_adapter_ready()` | repo current | Mandatory per-target smoke tests and explicit fallback behavior | Already captures the local/specialized readiness contract from Phase 19. |
| `typer` CLI | repo current | Operator-facing benchmark entrypoint and smoke-only mode | Existing command surface already uses Typer, JSON summaries, and `_emit_error(...)` conventions. |

### Supporting

| Library / Contract | Version | Purpose | When to Use |
|--------------------|---------|---------|-------------|
| `time.perf_counter()` | stdlib | Measure per-target smoke and execution latency | Use for benchmark latency fields instead of inventing new dependency or timing daemon. |
| Existing acceptance-pack helpers in `materials_discovery.llm.acceptance` | repo current | Shared benchmark context and system-level quality thresholds | Use to validate that all target results map back to one acceptance context. |
| Existing storage helpers in `materials_discovery.llm.storage` | repo current | New benchmark artifact paths under `data/benchmarks/` | Extend rather than hand-rolling new path logic in the CLI. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Typed serving-benchmark spec | Ad hoc repeated CLI flags per target | Faster initially, but much weaker for reproducibility and operator reuse. |
| Explicit per-target smoke checks | Silent fallback or best-effort benchmark execution | Easier demo path, but violates the locked “no silent fallback” decision and makes operator trust worse. |
| Role-aware targets (`campaign_launch` and `llm_evaluate`) | Force all targets through generation only | Simpler on paper, but dishonest for the current specialized lane. |
| Reuse existing launch/evaluate/compare artifacts | Build a parallel benchmark-only runtime | Would fracture the workflow we just stabilized in v1.1/v1.2. |

## Architecture Patterns

### Pattern 1: One Shared Benchmark Spec, Many Targets

**What:** Add a new typed benchmark spec that names a shared acceptance-pack or
campaign/benchmark context once, then enumerates hosted/local/specialized
targets under it.

**When to use:** Always for operator-facing benchmark runs. The whole point of
Phase 21 is to stop hand-assembling comparisons.

**Recommendation:** Put the spec and result models in
`materials-discovery/src/materials_discovery/llm/schema.py` and benchmark path
helpers in `materials-discovery/src/materials_discovery/llm/storage.py`. Keep
artifacts under `data/benchmarks/llm_serving/{benchmark_id}/...`.

### Pattern 2: Smoke-Test Targets with the Existing Runtime Contract

**What:** Run explicit readiness checks for each target before benchmark
execution using the same lane resolution and adapter readiness helper shipped in
Phase 19.

**When to use:** Before every target execution and in a dedicated `--smoke-only`
benchmark mode for operators.

**Recommendation:** A benchmark target should fail before execution if the
requested serving lane is unavailable and no explicit fallback is configured.
Smoke artifacts should record target ID, role, requested lane, resolved lane,
serving identity, latency, and failure detail.

### Pattern 3: Reuse Honest Subflows Per Target Role

**What:** Let benchmark targets declare the honest subflow they exercise:
`campaign_launch` for hosted/local generation lanes and `llm_evaluate` for the
evaluation-primary specialized lane.

**When to use:** Whenever the specialized lane is being compared as a workflow
tool rather than forced into direct Zomic generation.

**Recommendation:** Keep the benchmark summary role-aware. It can compare common
dimensions like latency, cost, and friction across all targets while showing
quality fields that are appropriate to the target role and explicit when a
dimension is unavailable.

### Pattern 4: Operator Guidance Comes from Structured Summary + Runbook

**What:** Emit typed benchmark artifacts first, then derive concise summary
lines and runbook guidance from them.

**When to use:** Always. Operators need both machine-readable data and a quick
decision aid.

**Recommendation:** The benchmark summary should explicitly call out at least:
- fastest target
- cheapest target
- lowest-friction target
- strongest quality signal available under the shared context

## Existing Reusable Surfaces

- `materials-discovery/src/materials_discovery/llm/launch.py` already has a
  stable launch-resolution core and a typed serving-identity contract.
- `materials-discovery/src/materials_discovery/llm/replay.py` already provides
  strict replay and drift handling if benchmark results need to revisit a prior
  launch.
- `materials-discovery/src/materials_discovery/llm/compare.py` already writes
  typed comparison artifacts and human-readable summary lines for launch-style
  targets.
- `materials-discovery/src/materials_discovery/llm/evaluate.py` already
  provides a lane-aware evaluation summary path that fits the specialized lane.
- `materials-discovery/scripts/run_llm_acceptance_benchmarks.sh` already shows
  the repo’s pattern for turning multiple typed comparison inputs into one
  shared acceptance artifact.

## Key Risks and Pitfalls

1. **Benchmarking without one shared context.**
   If targets can quietly diverge in acceptance pack, campaign spec, or ranked
   input, the operator-facing comparison becomes misleading immediately.

2. **Silent fallback will poison the benchmark.**
   If a requested local or specialized lane silently downgrades, the benchmark
   ceases to be about the advertised target.

3. **Cost and operator friction are not currently measured anywhere.**
   They must be represented explicitly in the benchmark spec or summary
   contract; they cannot be inferred from current launch or compare artifacts.

4. **Specialized lane role mismatch.**
   If Phase 21 tries to benchmark the specialized lane as if it were a mature
   Zomic generator, the benchmark will overstate capability and confuse the
   operator guidance.

5. **Parallel benchmark-only code path risk.**
   If the benchmark command bypasses launch/evaluate/compare conventions, Phase
   21 will create a second workflow family instead of strengthening the current
   one.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` |
| Config file | `materials-discovery/pyproject.toml` |
| Quick run command | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py tests/test_llm_serving_benchmark_cli.py -x -v` |
| Full suite command | `cd materials-discovery && uv run pytest` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| LLM-17 | hosted/local/specialized targets run under one shared benchmark context and emit comparable artifacts | schema + integration | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_cli.py -x -v` | ❌ create |
| LLM-17 | benchmark summary records quality, cost, latency, and operator friction in one typed result | core + integration | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_core.py tests/test_llm_serving_benchmark_cli.py -x -v` | ❌ create |
| OPS-10 | smoke-only mode and explicit failure/fallback behavior are operator-visible and reproducible | core + CLI | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_core.py tests/test_llm_serving_benchmark_cli.py tests/test_cli.py -x -v` | ❌ create / ✅ extend |

### Sampling Rate

- **After Wave 1 schema/core work:** `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py -x -v`
- **Before starting Wave 2:** `cd materials-discovery && uv run pytest`
- **After Wave 2 CLI/integration work:** `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_real_mode_pipeline.py -x -v`
- **After Wave 3 docs/config/operator workflow work:** `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v`
- **Phase gate:** full suite green before milestone closeout

### Wave 0 Gaps

- [ ] `materials-discovery/tests/test_llm_serving_benchmark_schema.py` — new schema/storage coverage for benchmark spec, smoke artifacts, and result summary
- [ ] `materials-discovery/tests/test_llm_serving_benchmark_core.py` — offline smoke-check and summary-building coverage
- [ ] `materials-discovery/tests/test_llm_serving_benchmark_cli.py` — new CLI coverage for `--smoke-only`, explicit target failures, and benchmark artifact writing
- [ ] `materials-discovery/tests/test_real_mode_pipeline.py` — add an offline end-to-end serving-benchmark path
- [ ] `materials-discovery/tests/test_cli.py` — keep the CLI help/command surface green after adding the new benchmark entrypoint

## Sources

### Primary (HIGH confidence)

- `.planning/phases/21-comparative-benchmarks-and-operator-serving-workflow/21-CONTEXT.md`
- `.planning/phases/20-specialized-lane-integration-and-workflow-compatibility/20-CONTEXT.md`
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/src/materials_discovery/llm/launch.py`
- `materials-discovery/src/materials_discovery/llm/replay.py`
- `materials-discovery/src/materials_discovery/llm/compare.py`
- `materials-discovery/src/materials_discovery/llm/evaluate.py`
- `materials-discovery/src/materials_discovery/llm/acceptance.py`
- `materials-discovery/src/materials_discovery/llm/benchmark.py`
- `materials-discovery/src/materials_discovery/llm/pipeline_benchmark.py`
- `materials-discovery/src/materials_discovery/llm/storage.py`
- `materials-discovery/src/materials_discovery/llm/schema.py`
- `materials-discovery/scripts/run_llm_acceptance_benchmarks.sh`
- `materials-discovery/RUNBOOK.md`
- `materials-discovery/developers-docs/llm-integration.md`
- `materials-discovery/developers-docs/pipeline-stages.md`
- `materials-discovery/tests/test_real_mode_pipeline.py`
- `materials-discovery/tests/test_llm_compare_cli.py`

### Secondary (MEDIUM confidence)

- `materials-discovery/developers-docs/configuration-reference.md`
- `materials-discovery/configs/systems/al_cu_fe_llm_local.yaml`
- `materials-discovery/configs/systems/sc_zn_llm_local.yaml`

### Tertiary (LOW confidence)

- None. This research pass relied on the local repo and its shipped contracts.

## Metadata

**Confidence breakdown:**

- Benchmark contract: MEDIUM — the repo already has strong acceptance,
  launch, replay, compare, and evaluation seams, but Phase 21 still needs a
  new cross-target summary contract.
- Architecture: HIGH — the recommended reuse path is grounded directly in
  shipped code and current test surfaces.
- Pitfalls: HIGH — the biggest risks are visible directly from current code and
  the locked user decisions.

**Research date:** 2026-04-05
**Valid until:** 2026-04-12

