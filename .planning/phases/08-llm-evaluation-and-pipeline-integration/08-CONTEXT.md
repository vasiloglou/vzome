# Phase 8: LLM Evaluation and Pipeline Integration - Context

**Gathered:** 2026-04-03
**Status:** Ready for planning
**Mode:** Autonomous defaults from roadmap + codebase context

## Phase Boundary

Phase 8 connects the new Phase 7 `llm-generate` outputs to the rest of the
materials workflow. The goal is to add an additive `llm-evaluate` stage,
surface LLM assessments in reporting, and prove that LLM-generated candidates
can move cleanly through `screen -> hifi-validate -> hifi-rank -> report`
without introducing a parallel artifact schema.

## Decisions

### Input and output seam

- `llm-evaluate` should read ranked candidates by default.
- It should write a separate additive artifact family under `data/llm_evaluated/`
  rather than mutating ranked JSONL in place.
- `report` should prefer enriched LLM-evaluated artifacts when they exist, but
  continue to work without them.

### Provider/runtime posture

- Reuse the Phase 7 LLM provider seam instead of creating a second provider system.
- Keep mock mode first-class and offline-testable.
- Hosted-provider support may reuse the existing Anthropic HTTP path.

### Ranking/report integration policy

- Phase 8 should not silently change `hifi-rank` scoring weights.
- LLM assessment should be additive context in ranked/report artifacts:
  synthesizability, precursor hints, anomaly flags, and short rationale.
- Any later use of LLM assessment as a ranking feature belongs to a future phase.

### Benchmark scope

- Benchmark both `Al-Cu-Fe` and `Sc-Zn`.
- Compare deterministic vs LLM-generated candidates through downstream pass
  rates, not only parse/compile.
- Keep the benchmark offline by default using committed mock configs and
  monkeypatched compile/provider seams in tests.

## Existing Code Insights

- `llm/generate.py` already produces standard `CandidateRecord` JSONL, stage
  metrics, and run-level audit artifacts.
- `rank_validated_candidates()` already carries additive provenance blocks in
  `candidate.provenance["hifi_rank"]`.
- `compile_experiment_report()` already consumes additive context from candidate
  provenance and emits a report summary/evidence structure that can hold LLM
  assessment without redesigning the report artifact.
- `llm-integration.md` already defines the intended user-facing shape of
  `llm-evaluate`: synthesizability, precursor suggestions, anomaly detection,
  and literature context.

## Specific Ideas

- Add `LlmEvaluateConfig` to `SystemConfig`.
- Add `mdisc llm-evaluate --config PATH [--batch all|topN] [--out PATH]`.
- Add a typed assessment block plus summary/run-manifest models in `llm/schema.py`.
- Build a Phase 8 benchmark helper that compares downstream pass-through and
  report-level acceptance metrics for deterministic vs LLM lanes.
