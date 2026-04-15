---
phase: 4
reviewers: [gemini, claude]
reviewed_at: 2026-04-03T15:01:58Z
plans_reviewed:
  - 04-01-PLAN.md
  - 04-02-PLAN.md
  - 04-03-PLAN.md
---

# Cross-AI Plan Review — Phase 4

`codex` CLI was available locally but intentionally skipped for independence
because this planning run is already being orchestrated from Codex.

## Gemini Review

# Phase 4 Plan Review: Reference-Aware No-DFT Materials Discovery v1

This review evaluates the three execution plans proposed for Phase 4 of the Materials Design Program. The plans aim to transition the `materials-discovery` pipeline into a benchmarkable, operator-credible workflow using `Al-Cu-Fe` and `Sc-Zn` as target systems.

## Summary

The proposed plans provide a comprehensive and technically sound path for achieving Phase 4 goals. By separating input-side **reference packs** from output-side **benchmark packs**, the plans establish a clear lifecycle for data curation and run comparison. The strategy is surgically focused on two well-provisioned systems, ensuring high-fidelity results without diluting effort. The additive approach to schemas ensures backward compatibility while significantly improving the provenance required for operator trust.

## Strengths

- **Artifact Distinction:** Correctly distinguishes between `reference packs` (curated inputs) and `benchmark packs` (comparable summaries), avoiding the "God manifest" anti-pattern.
- **System Focus:** Wisely locks the scope to `Al-Cu-Fe` and `Sc-Zn`, where deterministic assets already exist, ensuring a "success-first" posture for v1.
- **Additive Evolution:** Adheres to the mandate of additive schema changes, preserving existing pipeline stability while layering in benchmarking context.
- **Offline Reproducibility:** Maintains the program's commitment to deterministic, offline verification using local fixtures and staged snapshots.
- **Operator-Centricity:** Plan 03 explicitly prioritizes runbooks and generalized scripts, moving the feature set from "test-only" to "operator-ready."

## Concerns

- **Redundancy Between Artifacts (LOW):** Plan 02 suggests either a new `benchmark_pack.json` or an upgraded `pipeline_manifest.json`. If both exist, there is a risk of data fragmentation or confusion about which is the "source of truth" for run comparison.
- **Deduplication Complexity (MEDIUM):** Reference pack assembly (Plan 01) involves merging staged snapshots. The deduplication logic must be robust to handle cases where the same structure appears across different sources with slightly different metadata.
- **Script Maintainability (LOW):** Generalizing Bash scripts (`run_reference_aware_benchmarks.sh`) can lead to complexity. Ensure these scripts remain thin wrappers around the `mdisc` CLI.

## Suggestions

- **Unified Summary Artifact:** Lean toward making the `benchmark_pack` a specialized, high-level summary that *references* stage manifests rather than duplicating their entire content. It should serve as the "Index" for a benchmark lane.
- **Provenance in CLI Output:** In Plan 02, ensure that the `mdisc report` and `mdisc hifi-rank` CLI text outputs (not just the JSON files) surface the active `benchmark_id` or `reference_pack_id` to provide immediate operator feedback.
- **Deduplication Policy:** Explicitly define a "source priority" in the `reference_pack` assembly logic so that if a record exists in both a QC-specific source (e.g., HYPOD-X) and a general source (e.g., MP), the richer metadata is preserved.
- **Parameter Injection:** Ensure the generalized benchmark runner in Plan 03 allows for easy injection of overrides (e.g., `--count`) to facilitate quick developer smoke tests versus full-scale benchmark runs.

## Risk Assessment: LOW

The plans are grounded in empirical research and leverage the stable Phase 3 bridge. The dependency ordering (Inputs -> Provenance -> Workflow) is logical and reduces the risk of rework. By enforcing deterministic verification and locking the system matrix, the plans significantly mitigate the risk of environmental or scientific noise.

---
*Review Date: 2026-04-03*
*Phase: 04-reference-aware-no-dft-materials-discovery-v1*

---

## Claude Review

# Phase 4 Plan Review: Reference-Aware No-DFT Materials Discovery v1

## Plan 01: Assemble Two-System Reference Packs And Benchmark Configs

### Summary

A well-scoped Wave 1 plan that introduces the input-side reference-pack abstraction and commits two benchmark configs. The plan correctly builds on the Phase 3 source-registry bridge rather than creating parallel plumbing, and the task decomposition (pack assembly first, then configs+tests) follows a natural dependency order. The scope is appropriately narrow for a foundation wave.

### Strengths

- Explicitly constrains itself to the Phase 3 bridge — no second ingest architecture
- Clear separation between reference packs (input-side) and benchmark packs (output-side, deferred to Plan 02)
- Pack fingerprinting and deterministic assembly enable reproducibility from day one
- Acceptance criteria include a negative constraint (must not import hifi validation adapters), which guards the no-DFT boundary
- Fixture-backed test strategy keeps verification offline and fast

### Concerns

- **MEDIUM**: Task 1 is large — it touches 5 source files across schema, runtime, storage, and a new module. If the reference-pack config shape turns out to be awkward after implementation, Task 2 (configs) will need rework. Consider whether the config shape deserves its own micro-task or at least an explicit "schema freeze" checkpoint before Task 2 begins.
- **MEDIUM**: The plan says "extend the additive ingestion config with an optional `reference_pack` block" but doesn't specify whether this is a new top-level `SystemConfig` field, a nested field under `ingestion`, or something else. The executor has discretion here per D-context, but the lack of a concrete schema sketch increases the risk of a shape that doesn't compose well with Plan 02's benchmark-context threading.
- **LOW**: The plan doesn't mention how the second source for each system (D-07/D-08: "one QC/approximant-friendly source plus at least one periodic/open materials source") will be represented in test fixtures. If only the existing `hypodx_sample.json` fixture is used for both pack members, the "multi-source" story is technically met but scientifically hollow. A thin second-source fixture (even synthetic) would strengthen the proof.
- **LOW**: No explicit mention of what happens when pack members have overlapping records across sources. The projection module already has dedupe logic, but the pack-level merge needs its own dedupe story documented in the acceptance criteria.

### Suggestions

- Add a brief schema sketch (even pseudocode) for the reference-pack config block in the plan body so Plan 02's executor doesn't have to reverse-engineer the shape
- Add a thin second-source fixture file (e.g., a synthetic COD or Materials Project fixture with 3-5 records) to make multi-source pack assembly testable without the "same source twice" ambiguity
- Add an acceptance criterion for pack-level dedupe behavior (what happens when two member snapshots contribute the same record for the same system)
- Consider splitting Task 1 into "schema + storage helpers" and "assembly + reuse logic" if the executor finds the scope unwieldy

### Risk Assessment

**LOW-MEDIUM**. The plan is well-grounded in existing infrastructure and the scope is reasonable. The main risk is Task 1's breadth — if the config shape doesn't land well on the first pass, downstream plans pay the cost. The offline/deterministic posture and clear acceptance criteria reduce execution risk significantly.

---

## Plan 02: Make Calibration, Ranking, And Report Outputs Comparable

### Summary

This is the most architecturally consequential plan in the phase. It threads benchmark/reference context through the full output pipeline — manifests, calibration, rank provenance, report payloads, and a new benchmark-pack summary artifact. The additive-evolution constraint is well-chosen: existing consumers shouldn't break. The three-task split (infrastructure, provenance threading, regression coverage) is logical, though the middle task carries significant surface area.

### Strengths

- Additive schema evolution is explicitly required — no breaking changes to existing manifests/summaries
- The benchmark-pack artifact design answers the right operator questions (which pack, which sources, which backend, which corpus)
- Task 3 (regression coverage) is a separate task rather than being buried inside Tasks 1-2, which keeps test quality from being an afterthought
- Cross-lane comparison assertions (Task 3) go beyond "files exist" to "structures are comparable"
- The plan explicitly mentions threading context into active-learning rows if needed, preventing a comparability gap downstream

### Concerns

- **HIGH**: Task 2 touches `rank_candidates.py` and `compare_patterns.py` to add provenance, but doesn't specify how the benchmark context reaches those functions. Currently `rank_validated_candidates` takes `(config, candidates)` and loads its own calibration profile internally. The benchmark-pack context (reference_pack_id, source_keys, etc.) isn't available from `SystemConfig` alone — it comes from the ingest/pack-assembly stage. The plan needs to clarify the plumbing: does the CLI pass context through? Does the rank function read it from a manifest on disk? Does the config carry it? This is the most likely place for the executor to make an awkward architectural choice under time pressure.
- **MEDIUM**: The plan lists `test_active_learn.py` in Task 2's files but doesn't describe what active-learning changes are needed. If the active-learning stage also needs benchmark context for comparability, the acceptance criteria should say so explicitly. If it doesn't, remove the file from the list to avoid confusion.
- **MEDIUM**: Task 1 says "write a dedicated benchmark-pack JSON artifact at the end of the pipeline (or make the existing pipeline manifest serve this role)." This either/or leaves too much ambiguity. The research document already recommends keeping them separate. The plan should commit to one approach — a dedicated artifact is cleaner and avoids overloading the pipeline manifest with a second responsibility.
- **LOW**: The cross-lane comparison test in Task 3 ("preferably Al-Cu-Fe real vs exec, or baseline real vs reference-aware real") requires running two full pipeline lanes in a single test. This could push test runtime past the 180s feedback-latency target from the validation strategy. Consider whether the comparison can be done at the artifact-structure level without a full second pipeline run.

### Suggestions

- Resolve the context-plumbing question explicitly: recommend that `cli.py` assembles a `benchmark_context` dict from the config + ingest manifest + pack manifest and passes it to downstream stages, rather than having each stage independently reconstruct it
- Commit to a dedicated benchmark-pack artifact rather than leaving the "or exact equivalent" escape hatch — this matches the research recommendation and keeps the pipeline manifest's contract stable
- Clarify whether `test_active_learn.py` needs real changes or is just listed defensively; if the latter, remove it from Task 2's file list
- For Task 3's cross-lane comparison, consider comparing artifact structures from two lanes that were already run by other tests (e.g., reading the outputs of `test_real_mode_pipeline.py`'s parametrized runs) rather than running two fresh full pipelines

### Risk Assessment

**MEDIUM**. The plan's goals are correct and well-motivated, but the context-plumbing gap (how benchmark context flows from ingest to rank/report) is a real architectural decision that could produce either a clean solution or a messy one depending on executor judgment. The additive constraint helps — it prevents breaking changes — but doesn't guarantee the new context flows elegantly. This is the plan most likely to need a mid-execution course correction.

---

## Plan 03: Ship Benchmark Runbooks And End-To-End Verification

### Summary

The capstone plan that turns Phase 4's internals into an operator-usable workflow. It generalizes the benchmark runner, documents the operator path, and adds the final two-system end-to-end regression coverage plus a cross-lane comparison proof. The scope is appropriate for a closing wave — it's about proving and documenting, not building new abstractions.

### Strengths

- Preserves existing single-lane scripts instead of replacing them — respects the operator's current muscle memory
- Config-driven benchmark runner avoids hard-coding system names
- End-to-end tests cover both required benchmark systems, not just one
- The cross-lane comparison task (Task 3) is structure-focused rather than metric-equality-focused — correct for comparing different backend modes
- Explicit requirement that the full suite passes before phase sign-off

### Concerns

- **MEDIUM**: Task 2 says "run end-to-end benchmark flows for both committed Phase 4 benchmark configs" in `test_real_mode_pipeline.py`. The existing parametrized test already runs `al_cu_fe_real.yaml` and `al_cu_fe_exec.yaml`. Adding `al_cu_fe_reference_aware.yaml` and `sc_zn_reference_aware.yaml` to that parametrized set means 4 full pipeline runs in one test module. With the 180s feedback-latency target, this may be tight. Consider whether the reference-aware configs should be in a separate test function or marked with a slower-allowed marker.
- **MEDIUM**: The `Sc-Zn` reference-aware config uses the Zomic bridge, which requires a local Java runtime for `export-zomic`/`generate`. The plan doesn't mention this dependency. If CI or a clean-checkout user doesn't have Java, the `Sc-Zn` end-to-end test will fail. The test should either skip gracefully when Java is absent or use a pre-exported orbit library fixture.
- **LOW**: The runbook task (Task 1) lists both script changes and documentation. Mixing code and docs in one task is fine, but the acceptance criteria don't mention testing the script itself — only running `test_real_mode_pipeline.py`. If the script has a bug (e.g., wrong config path), the test won't catch it. Consider adding a basic smoke test or at least a `bash -n` syntax check.
- **LOW**: The plan doesn't mention updating `developers-docs/index.md` to link the new runbook, though Task 1's action text says "link it from the README." Both the README and the docs index should be updated for discoverability.

### Suggestions

- Add the Java runtime dependency to the test prerequisites or add a `pytest.importorskip`-style guard for the Zomic-dependent `Sc-Zn` end-to-end test
- Consider splitting the end-to-end test parametrization so reference-aware configs are a separate test function with a clear marker (e.g., `@pytest.mark.phase4_benchmark`)
- Add `developers-docs/index.md` to the files-modified list for the runbook task
- Add a basic `bash -n scripts/run_reference_aware_benchmarks.sh` check in the verify step

### Risk Assessment

**LOW-MEDIUM**. This is the most straightforward plan — it's mostly connecting existing pieces and documenting the result. The main risks are test runtime and the Java dependency for Sc-Zn, both of which are manageable with the suggested mitigations. The plan achieves its stated goals if Plans 01 and 02 land cleanly.

---

## Cross-Plan Assessment

### Overall Architecture

The three-wave split is sound: inputs first, outputs second, operator proof third. Each wave has a clear deliverable that the next wave depends on. The dependency chain is explicit in the frontmatter.

### Requirement Coverage

| Requirement | Plan Coverage | Confidence |
|-------------|--------------|------------|
| PIPE-02 (two-system non-mock benchmarks) | Plans 01 + 03 | High — both systems are explicitly targeted |
| PIPE-03 (comparable manifests/calibrations/benchmark packs) | Plans 02 + 03 | Medium-High — depends on Plan 02's context-plumbing quality |

### Cross-Plan Risks

- **Context-plumbing contract (HIGH)**: Plan 01 defines the reference-pack shape, Plan 02 consumes it for benchmark context. If the shapes don't compose well, Plan 02's executor will either hack around it or need to refactor Plan 01's output. **Suggestion**: Add a brief interface contract (even just field names) to Plan 01's acceptance criteria that Plan 02 can rely on.
- **Test runtime budget (MEDIUM)**: The cumulative test additions across all three plans could push the full suite well past the 180s feedback-latency target. Plans should specify which tests are "quick feedback" vs "full verification" more explicitly.
- **Second-source fixture gap (MEDIUM)**: The multi-source reference-pack story is only as credible as the test fixtures. If all plans use only the existing `hypodx_sample.json` fixture as the sole source, the "multi-source" claim is structurally satisfied but scientifically trivial. At least one plan should commit to creating or committing a thin second-source fixture.

### Overall Risk Level

**MEDIUM**. The plans are well-structured, well-scoped, and clearly grounded in the existing codebase. The primary risk is in Plan 02's context-plumbing design — this is the plan where an executor under time pressure is most likely to make a choice that creates maintenance burden later. The other plans are lower risk. The phase should succeed if the executor reads the research document carefully and commits to clean context flow rather than ad hoc threading.

---

## Consensus Summary

Both reviewers agree that the Phase 4 split is strong: `reference packs` first,
then comparable provenance, then operator-ready scripts and two-system
verification. They also agree that locking the phase to `Al-Cu-Fe` and `Sc-Zn`
is the right success-first scope and that the additive, offline, no-DFT posture
is a major strength.

### Agreed Strengths

- The three-wave dependency order is sound and closely aligned with the current
  codebase state.
- The distinction between input-side `reference packs` and output-side
  `benchmark packs` is the right design move.
- Scope is appropriately constrained to the two systems that already have the
  best real-mode assets and deterministic coverage.
- The plans preserve backward compatibility and deterministic offline
  verification rather than introducing a second orchestration or ingest stack.

### Agreed Concerns

- The pack/benchmark context contract needs to be more explicit.
  Gemini raised pack dedupe/source-priority concerns, and Claude raised a
  higher-severity concern about how benchmark context actually reaches
  downstream rank/report stages.
- The multi-source proof needs stronger fixture realism.
  Both reviews point toward making overlap/dedupe behavior explicit and using a
  real second-source thin fixture instead of satisfying the multi-source story
  with one source repeated twice.
- The output artifact boundary should be unambiguous.
  Gemini warned against duplicating `benchmark_pack` and `pipeline_manifest`
  responsibilities, and Claude recommended committing to a dedicated
  benchmark-pack artifact rather than leaving the plan ambiguous.
- The final operator/test lane should guard against runtime surprises.
  Claude called out full-matrix runtime growth and the `Sc-Zn` Java/Zomic
  dependency; Gemini separately warned to keep the benchmark runner thin and
  maintainable.

### Divergent Views

- **Overall risk:** Gemini assessed the phase as `LOW` risk overall, while
  Claude assessed it as `MEDIUM`, mainly because of the unresolved
  benchmark-context plumbing in Plan 02.
- **Primary emphasis:** Gemini focused more on artifact clarity and operator
  ergonomics, while Claude focused more on execution risk, concrete schema
  shape, and test/runtime implications.
- **Operator output suggestion:** Gemini recommended surfacing pack IDs directly
  in CLI output; Claude focused instead on explicit `cli.py` context assembly
  and downstream function interfaces.
