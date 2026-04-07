# Feature Landscape: v1.6 Translator-Backed External Materials-LLM Benchmark MVP

**Domain:** External materials-LLM benchmarking over shipped translation artifacts  
**Researched:** 2026-04-07

## Scope Frame

- This document covers only the net-new features needed for `v1.6`.
- Already shipped and reused: translation artifacts, CIF/material-string
  exporters, file-backed CLI tracing, internal serving lanes, replay/compare,
  and checkpoint promotion/pinning workflows.
- The milestone question is narrow: which downloaded external materials LLMs
  are worth deeper workflow investment after a fair, fidelity-aware benchmark?
- The milestone stays CLI-first, operator-governed, file-backed, and small in
  model and benchmark-set scope.

## Suggested Requirement Categories

| Candidate REQ ID | Theme | Why It Exists In v1.6 |
|------------------|-------|-----------------------|
| `LLM-31` | Fidelity-scoped translated benchmark set | Prevent misleading comparisons across CIF-safe, material-string-safe, and lossy artifacts. |
| `OPS-17` | External model execution contract | Make downloaded external models reproducible, smoke-testable, and auditable instead of notebook-only. |
| `LLM-32` | Shared comparative benchmark workflow | Run external models and internal controls on the same translated inputs under one typed benchmark surface. |
| `LLM-33` | Decision-grade benchmark outputs | Turn raw runs into operator-usable evidence about whether deeper investment is justified. |
| `OPS-18` | Operator docs and inspect surfaces | Keep the new benchmark workflow runnable and interpretable without reverse-engineering artifacts. |

## Table Stakes

Features the milestone needs to feel complete for the external-benchmark goal.

| Category | Candidate REQ IDs | Feature | Why Expected | Milestone-Scoping Notes |
|----------|-------------------|---------|--------------|-------------------------|
| Benchmark-set governance | `LLM-31` | Freeze one small translated benchmark set with explicit inclusion rules, target-family eligibility, fidelity-tier gating, and exclusion reasons per artifact. | Without this, the benchmark will quietly mix honest approximants, lossy proxies, and incompatible formats into one misleading score. | Headline scoring should default to the credible subset. Lossy or unsupported artifacts may exist as diagnostic-only slices, not the main leaderboard. |
| External model registration and smoke checks | `OPS-17` | Register each downloaded external model with file-backed identity, compatible artifact families, local invocation settings, smoke-test behavior, and environment or weights lineage. | Operators need rerunnable executions, not shell history and one-off scripts. | Support only a curated handful of already-downloaded models. Do not build a generic model marketplace or downloader. |
| Shared benchmark spec with internal controls | `LLM-32` | Add one typed benchmark workflow that benchmarks external models and current promoted or explicitly pinned internal controls against the same translated inputs. | This is the core milestone question. If the workflow cannot compare against current internal controls honestly, the milestone has not answered anything useful. | Reuse existing benchmark, compare, and control-resolution seams instead of inventing a second orchestration stack. |
| Representation-aware scoring | `LLM-32`, `LLM-33` | Score results by compatible representation family and fidelity slice rather than forcing one fake apples-to-apples total across CIF-only and material-string-only cases. | Some external models consume CIF-like text, some material strings, and not every translated artifact is benchmark-safe. | Every summary should report eligible counts, excluded counts, and family-specific denominators so operators know what the score really covers. |
| Decision-oriented output artifacts | `LLM-33`, `OPS-18` | Emit typed benchmark summaries plus concise CLI scorecards and recommendation lines that say whether an external model beats, matches, or fails against the control arm. | The milestone goal is a decision about what to do next, not just artifact generation. | The output should clearly answer whether to continue deeper benchmarking or automation work, keep the model exploratory, or stop. |

## Differentiators

High-value additions that make the MVP more decisive, but should not expand the
milestone into a broader platform build.

| Category | Candidate REQ IDs | Feature | Value Proposition | Milestone-Scoping Notes |
|----------|-------------------|---------|-------------------|-------------------------|
| Control-arm clarity | `LLM-32` | Allow one benchmark run to include both the current promoted internal default and an explicit pinned internal control when the operator wants both. | This reduces ambiguity about whether an external-model win is real or just an artifact of which internal baseline was chosen. | Useful for credibility, but the MVP can still ship if one clear internal control path is mandatory and the second is optional. |
| Representation-sensitivity analysis | `LLM-33` | For models that can consume more than one translated artifact family, show whether performance changes between CIF and material-string inputs for the same benchmark slice. | This tells the operator whether the interesting signal is the model or the representation choice. | Keep this as a derived benchmark slice, not a reason to expand into broad format experimentation. |
| Outcome routing for next milestone choice | `LLM-33` | Turn the scorecard into a small rule-based recommendation surface: deeper external-model automation, more internal training investment, benchmark-set cleanup, or no follow-up. | This shortens roadmap handoff and makes the benchmark immediately actionable. | Keep the routing simple and explicit. Do not build an autonomous planner. |

## Anti-Features

Features to explicitly avoid in `v1.6`.

| Anti-Feature | Why Avoid It In v1.6 | What To Do Instead |
|--------------|----------------------|--------------------|
| Full training or fine-tuning automation for external models | The milestone is supposed to decide whether deeper investment is warranted, not assume it upfront. | Benchmark downloaded models first and defer training automation to a later milestone if the evidence justifies it. |
| Autonomous campaign execution based on benchmark winners | This would bypass the current operator-governed workflow before the external-model value proposition is proven. | Keep benchmark outputs advisory and operator-reviewed. |
| Broad model-zoo or plugin-platform support | A generic external-model framework would absorb the milestone and delay the actual benchmark question. | Support a small curated set of explicitly configured downloaded models. |
| Broad chemistry or source expansion as the milestone headline | Expanding the dataset too far would blur whether results changed because of model quality or because the benchmark moved. | Add only the minimum benchmark-set cleanup needed for a credible curated slice. |
| One blended leaderboard across incompatible artifact families and fidelity tiers | This would hide representational mismatch and make the headline score scientifically misleading. | Keep the benchmark family-aware and fidelity-aware, with explicit exclusions and sub-scores. |
| UI-first dashboards or benchmark service infrastructure | The repo already uses a CLI-first, file-backed operator model, and a UI would be extra surface area without answering the milestone question better. | Emit inspectable JSON summaries and concise CLI scorecards. |

## Milestone-Scoping Notes

- Reuse the shipped translation bundle inventory and fidelity metadata as the
  benchmark-set source of truth. Do not invent a second artifact taxonomy.
- External models should declare which translated artifact families they can
  honestly consume. The benchmark should not coerce every model into every
  representation.
- The internal control arm should resolve through the shipped promoted-default
  and explicit-pin checkpoint machinery, not through benchmark-only shortcuts.
- Reproducibility needs to include enough external-runtime capture to explain a
  result later, but not a full deployment platform.
- The main benchmark conclusion should come from the credible benchmark slice.
  Lossy slices are useful diagnostics, not the milestone headline.

## Feature Dependencies

```text
translated bundle inventory + fidelity metadata
-> benchmark-set inclusion rules
-> external model registration and compatibility declaration
-> shared benchmark spec with internal controls
-> representation-aware benchmark summary
-> next-step recommendation
```

## Minimum Credible v1.6 Feature Set

Prioritize:

1. `LLM-31`: freeze one small fidelity-aware translated benchmark set with
   explicit exclusions and compatible target-family rules.
2. `OPS-17`: support a curated handful of downloaded external models with
   reproducible local invocation, smoke checks, and environment lineage.
3. `LLM-32`: run those external models against the current promoted internal
   control, with explicit pinned-control support if it is cheap to add.
4. `LLM-33`: emit representation-aware scorecards that tell the operator
   whether any external model is strong enough to justify deeper follow-on
   investment.

Defer broad model coverage, training automation, campaign automation, and
large benchmark-set expansion. The minimum credible `v1.6` milestone is a
small, honest, reproducible benchmark that can clearly say "continue" or
"stop" for each external model family.

**File changed:** `/Users/nikolaosvasiloglou/github-repos/vzome/.planning/research/FEATURES.md`
