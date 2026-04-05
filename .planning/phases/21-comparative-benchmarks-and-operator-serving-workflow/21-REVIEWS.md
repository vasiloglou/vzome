---
phase: 21
reviewers: [gemini, claude]
reviewed_at: 2026-04-05T06:07:28Z
plans_reviewed:
  - 21-01-PLAN.md
  - 21-02-PLAN.md
  - 21-03-PLAN.md
---

# Cross-AI Plan Review — Phase 21

## Gemini Review

# Phase 21: Comparative Benchmarks and Operator Serving Workflow - Plan Review

The implementation plans for Phase 21 provide a robust and well-structured approach to making the hosted, local, and specialized serving lanes measurable and usable for operators. The strategy correctly prioritizes a typed, file-backed contract and reuses existing workflow seams to ensure consistency and maintainability.

### Summary
These plans deliver a comprehensive benchmarking layer that allows operators to evaluate serving lanes based on quality, cost, latency, and setup friction. By utilizing a modular design, separating schema definitions, core orchestration, and the CLI surface, the implementation remains additive and safe. The adherence to the "no silent fallback" decision through mandatory smoke checks and explicit `allow_fallback` settings is a key strength that protects operator trust.

### Strengths
- **Seam Reuse:** Plan 21-02 correctly reuses `llm-launch`, `llm-evaluate`, and `llm-compare` rather than building parallel execution logic, ensuring the benchmark remains consistent with the standard workflow.
- **Typed Contract:** Adding `LlmServingBenchmarkSpec` and `LlmServingBenchmarkSummary` to the schema ensures that benchmarks are reproducible and machine-readable artifacts.
- **Honest Role Representation:** The plans explicitly treat the specialized lane as evaluation-primary in benchmark targets, avoiding the risk of overstating its capabilities as a Zomic generator.
- **Operational Clarity:** The inclusion of `estimated_cost_usd` and `operator_friction_tier` directly addresses the need for real-world tradeoff analysis.
- **Strict Failure Posture:** Mandatory smoke-only mode and explicit failure on unexpected fallback ensure the benchmark honestly represents the requested serving configuration.

### Concerns
- **System Compatibility (LOW):** While the plans anchor targets to a shared `acceptance_pack_path`, the benchmark orchestration should explicitly verify that every target's `system_config` matches the chemical system of the acceptance pack to prevent operator error in the spec file.
- **Shared Data Fixture for Evaluation (LOW):** Since `llm_evaluate` targets in a benchmark assess existing data, the plan should ensure that the `batch` parameter used in benchmarking matches the context of the generation targets being compared to maintain a truly fair comparison.

### Suggestions
- **Target System Validation:** In `load_serving_benchmark_spec` or the CLI entrypoint, add a validation check that confirms all targets reference the same `system_name` as the system defined in the shared acceptance pack.
- **Artifact Cleaning:** Consider adding a flag or note in the runbook regarding the cleanup of the `data/benchmarks/llm_serving/` directory, as repeated benchmark runs might accumulate substantial artifacts.
- **Summary Robustness:** Ensure `build_serving_benchmark_summary` handles `None` values for latency or quality metrics gracefully if a specific target role does not produce them, such as an evaluation target that has no generation success rate.

### Risk Assessment: LOW
The risk is low because the plans are primarily additive and rely on the existing, validated closed-loop LLM infrastructure. The execution is broken into waves that provide early feedback via schema and core unit tests before expanding the CLI surface and integration proof. Adherence to the monorepo's progress-tracking requirements ensures auditability.

**Plan Review Verdict: APPROVED FOR EXECUTION**

---

## Claude Review

Claude was invoked twice, but no usable review body was returned:

1. `claude -p ... --no-input` failed because this local CLI does not support the `--no-input` flag.
2. Retrying with plain `claude -p ...` produced no output and appeared to hang, so the run was terminated.

No substantive Claude review content was available for synthesis.

---

## Codex Review

Skipped intentionally because the current runtime is already Codex, so it would not have been an independent external review.

---

## Consensus Summary

Only Gemini produced a substantive review body this round, so the summary below reflects the available external signal rather than true multi-review consensus.

### Agreed Strengths
- The phase structure looks additive and low risk: typed benchmark contract first, benchmark execution second, and operator docs/regressions last.
- Reusing `llm-launch`, `llm-evaluate`, and `llm-compare` instead of building a parallel benchmark runtime is the right architectural move.
- Treating the specialized lane as evaluation-primary is an honest fit for the current milestone and avoids overstating Zomic-generation capability.

### Agreed Concerns
- The benchmark loader or CLI should validate that every target's `system_config` matches the shared acceptance-pack system so mixed-system specs fail early and clearly.
- The evaluation target's `batch` or candidate set should be tied explicitly to the same shared benchmark context used by generation targets so the comparison stays fair.
- The benchmark summary should preserve role-specific missing metrics explicitly instead of implying parity between generation-role and evaluation-role targets.

### Divergent Views
- No substantive divergence was available because Claude did not return a usable review body and Codex was skipped for independence.
