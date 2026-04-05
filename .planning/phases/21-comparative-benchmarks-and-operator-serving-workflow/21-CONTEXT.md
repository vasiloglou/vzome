# Phase 21: Comparative Benchmarks and Operator Serving Workflow - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 21 makes the new hosted, local, and `specialized_materials` serving
lanes usable and measurable for operators through comparative benchmarks, smoke
tests, and a stable runbook.

This phase should deliver:

- a benchmark workflow that compares hosted, local, and specialized lanes
  against the same acceptance-pack or benchmark context
- operator-facing smoke-test and fallback guidance for serving setup
- runbook updates covering setup, lane selection, failure diagnosis, and
  comparison interpretation
- regression coverage that protects the new operator-serving workflow

This phase does not introduce autonomous campaign execution, replace the
existing CLI/file-backed workflow, or turn Phase 21 into a new generation-model
adaptation phase. It makes the serving surface benchmarkable and operator-usable.

</domain>

<decisions>
## Implementation Decisions

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
- The exact CLI command name and flags for the benchmark entrypoint, provided
  it is clearly operator-facing and distinct from lower-level compare behavior
- The exact smoke-test steps and failure wording, provided they remain explicit
  and do not silently downgrade lane selection
- The exact benchmark artifact field names and summary wording, provided both
  typed outputs and concise operator guidance are preserved
- The exact way operator friction is represented, provided the benchmark makes
  setup and usability tradeoffs visible

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone controls
- `.planning/PROJECT.md` — `v1.2` scope, the operator-serving goal, and the
  note that specialized materials models are not assumed Zomic-native
- `.planning/ROADMAP.md` — Phase 21 goal, deliverables, success criteria, and
  the boundary against autonomous campaign execution
- `.planning/REQUIREMENTS.md` — `LLM-17` and `OPS-10` as the primary Phase 21
  requirements
- `.planning/STATE.md` — current handoff after Phase 20 completion

### Prior phase authority
- `.planning/phases/19-local-serving-runtime-and-lane-contracts/19-CONTEXT.md`
  — local-serving contract, explicit fallback posture, and serving-identity
  rules
- `.planning/phases/20-specialized-lane-integration-and-workflow-compatibility/20-CONTEXT.md`
  — specialized-lane role, compatibility boundaries, and stable artifact-shape
  expectations
- `.planning/milestones/v1.1-phases/12-replay-comparison-and-operator-workflow/12-CONTEXT.md`
  — replay authority, comparison posture, and operator workflow expectations

### Operator and workflow docs
- `materials-discovery/RUNBOOK.md` — current operator workflow surface that
  Phase 21 should extend rather than replace
- `materials-discovery/developers-docs/llm-integration.md` — current serving
  architecture and lane semantics
- `materials-discovery/developers-docs/pipeline-stages.md` — `llm-launch`,
  `llm-replay`, `llm-compare`, and evaluation-stage workflow contracts
- `materials-discovery/developers-docs/configuration-reference.md` — lane and
  local/specialized serving configuration semantics

### Existing contract surface
- `materials-discovery/src/materials_discovery/cli.py` — current operator CLI
  surface for generation, launch, replay, compare, and evaluation
- `materials-discovery/src/materials_discovery/llm/launch.py` — lane-aware
  launch behavior and lineage recording
- `materials-discovery/src/materials_discovery/llm/replay.py` — strict replay
  and drift behavior
- `materials-discovery/src/materials_discovery/llm/compare.py` — typed compare
  artifacts and human-readable comparison surface
- `materials-discovery/src/materials_discovery/llm/evaluate.py` — specialized
  evaluation path and summary behavior
- `materials-discovery/src/materials_discovery/llm/schema.py` — launch, replay,
  compare, and evaluation artifact contracts
- `materials-discovery/src/materials_discovery/common/schema.py` — system and
  lane configuration surfaces used by serving workflows

### Current example configs and tests
- `materials-discovery/configs/systems/al_cu_fe_llm_local.yaml` — current
  local/specialized lane benchmark candidate config
- `materials-discovery/configs/systems/sc_zn_llm_local.yaml` — second example
  lane config for compatibility and lighter operator proof
- `materials-discovery/tests/test_real_mode_pipeline.py` — end-to-end workflow
  regression surface
- `materials-discovery/tests/test_llm_compare_cli.py` — compare CLI behavior
  and operator-visible summaries

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `materials-discovery/src/materials_discovery/llm/compare.py`: already knows
  how to build typed comparison artifacts and operator-readable summaries, so
  Phase 21 should extend it rather than build a new comparison path.
- `materials-discovery/src/materials_discovery/llm/replay.py`: already
  provides the reproducible rerun foundation that a benchmark workflow can
  rely on for consistent comparison context.
- `materials-discovery/src/materials_discovery/llm/launch.py`: already records
  serving identity and lane resolution, giving Phase 21 a stable launch unit
  for hosted, local, and specialized runs.
- `materials-discovery/RUNBOOK.md`: already holds the operator-facing workflow
  narrative and is the right place to document setup, smoke tests, fallback,
  and interpretation.
- `materials-discovery/tests/test_real_mode_pipeline.py`: already proves the
  existing operator workflow offline and is the natural place to protect the
  new benchmark entrypoint.

### Established Patterns
- Keep higher-level operator workflow commands as thin wrappers over the
  existing file-backed generation, launch, replay, and compare machinery.
- Preserve stable artifact contracts and extend lineage or reporting rather
  than creating separate hosted/local/specialized workflow branches.
- Prefer explicit diagnostics and explicit fallback rules over silent
  convenience behavior.
- Keep benchmark evidence reproducible enough that operators can revisit and
  compare results later without rebuilding context manually.

### Integration Points
- `materials-discovery/src/materials_discovery/cli.py` for the operator-facing
  benchmark and smoke-test surface
- `materials-discovery/src/materials_discovery/llm/launch.py`,
  `materials-discovery/src/materials_discovery/llm/replay.py`, and
  `materials-discovery/src/materials_discovery/llm/compare.py` for reusing the
  existing workflow rather than building a parallel benchmark runner
- `materials-discovery/RUNBOOK.md` and
  `materials-discovery/developers-docs/llm-integration.md` for the operator
  explanation of setup, lane choice, failure diagnosis, and comparison meaning

</code_context>

<specifics>
## Specific Ideas

- The benchmark should make hosted, local, and specialized lanes comparable
  under one shared context, not just list separate run outcomes.
- Phase 21 should treat smoke testing as part of the operator workflow, not as
  an optional hidden helper.
- The operator summary should help answer practical questions such as “which
  lane is cheapest to operate here?” and “which lane is worth the setup cost?”

</specifics>

<deferred>
## Deferred Ideas

- Fully autonomous campaign execution on top of the serving workflow
- Lane-specific benchmark contexts as the default comparison mode
- Silent benchmark fallback from specialized/local to hosted behavior
- Replacing the current CLI/file-backed workflow with a UI-first system
- Treating off-the-shelf specialized models as Zomic-native generators by
  default

</deferred>

---

*Phase: 21-comparative-benchmarks-and-operator-serving-workflow*
*Context gathered: 2026-04-05*
