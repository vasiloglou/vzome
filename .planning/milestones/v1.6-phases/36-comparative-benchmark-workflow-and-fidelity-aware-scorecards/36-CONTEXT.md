# Phase 36: Comparative Benchmark Workflow and Fidelity-Aware Scorecards - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning
**Mode:** Autonomous defaults from roadmap + milestone research

<domain>
## Phase Boundary

Phase 36 should turn the frozen translated benchmark sets from Phase 34 and the
registered external benchmark targets from Phase 35 into one decision-grade,
file-backed comparative benchmark workflow. The phase should deliver:

- one typed benchmark spec that runs curated external targets and current
  promoted or explicitly pinned internal controls against the same frozen
  translated benchmark cases
- per-target run artifacts that preserve control-arm identity, environment
  lineage, eligible counts, excluded counts, and raw per-case results
- benchmark summaries and inspect surfaces that stay explicit about
  `target_family`, `fidelity_tier`, and shared eligible slices
- recommendation lines that tell the operator whether each external target
  merits deeper follow-up, limited exploration, or no further milestone
  expansion

This phase should not build a generic external serving platform, broad model
zoo, training automation, campaign automation, or UI dashboard layer. It is
the milestone decision surface, not the next milestone itself.

</domain>

<decisions>
## Implementation Decisions

### Scope and benchmark posture

- **D-01:** Keep the benchmark small, curated, CLI-first, and file-backed.
  Support only the handful of registered external targets already prepared in
  Phase 35 and one or more explicit internal controls.
- **D-02:** Materialize benchmark artifacts under
  `materials-discovery/data/benchmarks/llm_external/{benchmark_id}/` with one
  benchmark-level summary and per-target subdirectories for run artifacts.
- **D-03:** Treat translated benchmark manifests and external-target
  registrations as the upstream source of truth. Phase 36 should consume those
  immutable artifacts rather than inventing parallel config or lineage stores.

### Prompt, parsing, and eligibility posture

- **D-04:** Benchmark execution must use versioned prompt contracts and capture
  the prompt-contract identity or hash in per-target run manifests so later
  reruns can explain prompt drift.
- **D-05:** A target is only scored on cases it explicitly supports. Unsupported
  `target_family` or system rows must be counted as excluded with typed reasons
  instead of disappearing from the summary.
- **D-06:** Per-case results must preserve the benchmark row's
  `target_family`, `fidelity_tier`, `loss_reasons`, and `diagnostic_codes` so
  later scorecards cannot collapse mixed-fidelity evidence into one flat score.

### Comparative scorecard posture

- **D-07:** Scorecards must stay target-family-aware and fidelity-aware. Do not
  emit one blended leaderboard across incompatible families or mixed
  exact/anchored versus approximate/lossy slices.
- **D-08:** Internal-control deltas must be computed only on the shared eligible
  slice for the target and the referenced control arm.
- **D-09:** Recommendation lines must stay within explicit outcome classes:
  not competitive, competitive only on periodic-safe slices, worthy of deeper
  follow-up or runtime investment, or blocked by translation or benchmark
  quality rather than model quality.

### Runtime seam posture

- **D-10:** External target execution remains benchmark-only and additive. Use
  Phase 35 registration facts plus thin benchmark execution helpers rather than
  extending `SystemConfig` or building a generic serving layer.
- **D-11:** Internal controls must reuse existing serving-lane, checkpoint, and
  `LlmServingIdentity` resolution so the benchmark references the shipped
  promoted/pinned control machinery instead of reimplementing it.
- **D-12:** Tests should rely on fixture benchmark sets, monkeypatched target
  runners, and typed artifact assertions. The production path may use optional
  runtime libraries, but the contract and scorecard tests must not require
  downloaded model weights.

### Operator surface posture

- **D-13:** Ship one example benchmark spec, one execution command, and one
  inspect command. The inspect surface should make control-arm identity,
  benchmark slice counts, environment lineage, and recommendation lines visible
  without reverse-engineering raw JSONL artifacts.
- **D-14:** Keep the summary surface honest about benchmark size and fidelity
  boundaries. The docs should explicitly say that the result is a milestone
  gating experiment, not proof that broad external-model automation is ready.

### the agent's Discretion

- Exact benchmark metric names and scorecard field layout, as long as the
  summary remains typed, slice-aware, and delta-aware
- Whether prompt rendering and response parsing live in one module or a small
  helper split, as long as the public workflow stays narrow
- The precise threshold logic for recommendation lines, as long as periodic-safe
  slices are privileged and unsupported or tiny slices do not yield overclaims

</decisions>

<specifics>
## Specific Ideas

- Use simple, explicit per-case metrics that are stable in tests and honest in
  docs: non-empty response status, parse success, exact-text match, and
  composition match where the parser can recover composition from the output.
- Treat `exact` and `anchored` fidelity tiers as the main decision slice and
  keep `approximate` or `lossy` slices visible as diagnostics.
- Reuse `resolve_serving_lane(...)`, `build_serving_identity(...)`, and the
  existing LLM adapter resolution for internal controls, but keep external
  execution on a benchmark-specific path that defaults to the Phase 35
  registration contract.

</specifics>

<canonical_refs>
## Canonical References

### Milestone scope
- `.planning/ROADMAP.md` — Phase 36 goal, requirements, and success criteria
- `.planning/REQUIREMENTS.md` — `LLM-32`, `LLM-33`, and `OPS-18`
- `.planning/STATE.md` — current milestone state and inherited decisions
- `.planning/PROJECT.md` — benchmark-first milestone framing and out-of-scope boundaries
- `.planning/research/SUMMARY.md` — milestone-level rationale for comparative scorecards
- `.planning/research/FEATURES.md` — benchmark-first scope, anti-features, and recommendation posture
- `.planning/research/ARCHITECTURE.md` — recommended benchmark artifact layout, execution lineage, and scorecard shape
- `.planning/research/PITFALLS.md` — fidelity misuse, apples-to-oranges comparison, and recommendation-overreach warnings

### Prior phase handoff
- `.planning/phases/34-benchmark-pack-and-freeze-contract/34-VERIFICATION.md` — verified translated benchmark-pack contract and artifact family
- `.planning/phases/35-external-target-registration-and-reproducible-execution/35-CONTEXT.md` — locked external-target registration and runtime-boundary decisions
- `.planning/phases/35-external-target-registration-and-reproducible-execution/35-VERIFICATION.md` — verified external-target registration, smoke, CLI, and docs handoff

### Existing repo patterns
- `materials-discovery/src/materials_discovery/llm/schema.py` — translated benchmark rows, external target registrations, and serving benchmark summary precedents
- `materials-discovery/src/materials_discovery/llm/storage.py` — benchmark and external-target artifact path helpers
- `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` — frozen translated benchmark set loading and manifest handling
- `materials-discovery/src/materials_discovery/llm/external_targets.py` — external-target registration, environment capture, and smoke artifact helpers
- `materials-discovery/src/materials_discovery/llm/serving_benchmark.py` — benchmark-summary and recommendation-line precedent
- `materials-discovery/src/materials_discovery/llm/compare.py` — existing comparison and outcome-snapshot aggregation style
- `materials-discovery/src/materials_discovery/llm/launch.py` — serving-lane resolution and `LlmServingIdentity`
- `materials-discovery/src/materials_discovery/llm/runtime.py` — direct adapter execution helpers for internal control paths
- `materials-discovery/src/materials_discovery/cli.py` — operator command style and exit-code-2 failure posture
- `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md` — Phase 34 operator boundary
- `materials-discovery/developers-docs/llm-external-target-runbook.md` — Phase 35 operator boundary and external-target artifact layout

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `translated_benchmark.py` already gives Phase 36 a stable manifest and typed
  included-row inventory instead of live bundle scanning.
- `external_targets.py` already resolves immutable external registrations and
  reproducibility artifacts that benchmark execution can reference directly.
- `launch.py` and `runtime.py` already provide the repo's preferred path for
  resolving internal control identity and sending direct prompt requests through
  configured adapters.
- `serving_benchmark.py` already demonstrates the repo's preferred pattern for
  per-target smoke checks, benchmark summaries, and recommendation lines.

### Established Patterns
- New LLM workflow slices start in `schema.py`, gain deterministic storage
  helpers, then add a focused execution module, CLI commands, tests, and docs.
- Operator errors fail with exit code 2 and a clear `failed:` prefix rather than
  partial artifact writes.
- Benchmark artifacts stay file-backed and typed. Human-readable inspect flows
  sit on top of the typed artifacts rather than replacing them.

### Integration Points
- Phase 36 should read benchmark cases from
  `data/benchmarks/llm_external_sets/{benchmark_set_id}/manifest.json` and the
  included inventory it points to.
- External benchmark targets should resolve via
  `data/llm_external_models/{model_id}/registration.json` and its related
  `environment.json` / `smoke_check.json`.
- Internal control arms should surface `LlmServingIdentity` and checkpoint
  lineage through existing serving-lane resolution rather than custom benchmark
  fields.

</code_context>

<deferred>
## Deferred Ideas

- Broad model-zoo support, download automation, or long-lived serving
- UI dashboards or service-backed benchmark reporting
- Autonomous follow-on decisions such as training, promotion, or campaign
  execution based on benchmark winners
- Large benchmark-set expansion beyond the curated milestone slice

</deferred>

---

*Phase: 36-comparative-benchmark-workflow-and-fidelity-aware-scorecards*
*Context gathered: 2026-04-07*
