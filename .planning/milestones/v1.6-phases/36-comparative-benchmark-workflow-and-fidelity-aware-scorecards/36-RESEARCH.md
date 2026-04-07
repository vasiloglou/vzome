# Phase 36: Comparative Benchmark Workflow and Fidelity-Aware Scorecards - Research

**Researched:** 2026-04-07
**Domain:** Comparative translated-benchmark execution, internal-control deltas, and decision-grade scorecards
**Confidence:** MEDIUM-HIGH

## User Constraints

Phase 36 has an explicit context file: `36-CONTEXT.md`.

Honor the locked decisions from that context and the milestone research:

- keep the phase benchmark-first, CLI-first, operator-governed, and file-backed
- benchmark only the curated external targets already registered in Phase 35
- reuse the frozen translated benchmark-set artifacts from Phase 34 rather than
  live translation bundles
- compare against current promoted or explicitly pinned internal controls on the
  same eligible slice
- keep recommendation lines evidence-backed and modest; this phase decides what
  to invest in next, not what to automate immediately
- any change under `materials-discovery/` must update
  `materials-discovery/Progress.md`

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LLM-32 | Operator can run one typed benchmark workflow that executes curated downloaded external materials LLMs and current promoted or explicitly pinned internal controls against the same translated benchmark cases and records per-target run artifacts. | Add one dedicated external benchmark spec and execution module that loads frozen benchmark rows, resolves external registrations and internal control identities, writes per-target run manifests, raw responses, and case-result rows, and stays additive to current LLM workflows. |
| LLM-33 | Benchmark summaries are target-family-aware and fidelity-aware, report eligible and excluded counts plus internal-control deltas, and emit decision-grade recommendation lines about whether deeper external-model investment is justified. | Define typed scorecard contracts with `overall`, `by_target_family`, `by_fidelity_tier`, and `control_deltas` sections plus bounded recommendation outcomes grounded in shared eligible slices. |
| OPS-18 | Operator can inspect translated benchmark sets, external model registrations, and benchmark summaries through CLI and documentation surfaces that expose fidelity posture, control-arm identity, exclusions, and environment capture without reverse-engineering raw artifacts. | Add one human-readable benchmark inspect command, example benchmark spec, and runbook updates that show how Phase 34 and 35 artifacts feed the new benchmark summary surface. |

</phase_requirements>

## Summary

The cleanest repo-fit for Phase 36 is a dedicated `external_benchmark` module
that sits beside `translated_benchmark.py`, `external_targets.py`, and
`serving_benchmark.py`. The benchmark should not become a generic external
platform or a second campaign system. It should load one frozen translated
benchmark manifest, resolve each benchmark target, execute one prompt per case,
and write a typed summary that stays explicit about family, fidelity, and
shared-slice deltas.

The strongest execution seam is:

1. read the included translated benchmark rows from the Phase 34 manifest
2. resolve each target as either:
   - an external registration from Phase 35, or
   - an internal control resolved through existing serving-lane and checkpoint
     identity helpers
3. render prompt text from a small prompt-contract registry keyed by
   `prompt_contract_id`
4. execute one generation call per eligible case using:
   - a benchmark-specific external runner for registered external models
   - the existing adapter-resolution path for internal controls
5. parse responses with a small parser registry keyed by `response_parser_key`
6. persist raw responses, case results, run manifests, and one typed benchmark
   summary with fidelity-aware scorecards and recommendation lines

This keeps the design honest. External targets stay benchmark subjects with
their own immutable registration lineage. Internal controls stay on the repo's
existing promoted/pinned checkpoint machinery. The new benchmark layer is only
responsible for the shared prompt, response, and scorecard contract.

For metric design, the safest MVP is a narrow, typed set of per-case fields that
are stable in tests and defensible in docs:

- `response_status` / `parse_status`
- `latency_s`
- `response_text_hash`
- `exact_text_match`
- `composition_match` when a parser can recover normalized composition

Those fields are enough to build the roadmap-facing slices Phase 36 needs:

- overall success and parse rates
- by-`target_family` slices
- by-`fidelity_tier` slices
- periodic-safe (`exact` + `anchored`) decision slice
- shared eligible deltas against each control arm

Recommendation lines should be rule-based and conservative. The scorecard should
only emit a strong "deeper investment" message when an external target is
competitive on the periodic-safe slice and has a meaningful shared-slice delta
against the referenced control. Small or unsupported slices should downgrade to
targeted follow-up or blocked-by-benchmark-quality guidance instead of claiming
victory.

**Primary recommendation:** split implementation into three plans:
contract/storage first, execution/scorecard core second, and CLI/docs last.
That keeps the code shape aligned with prior benchmark phases and avoids mixing
schema churn with operator polish.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pydantic` | repo standard | Typed benchmark specs, per-case results, run manifests, and summaries | Matches the repo's existing LLM artifact contracts. |
| `typer` | repo standard | Benchmark run and inspect commands | Keeps the operator surface consistent with earlier phases. |
| `pytest` | repo standard | Schema, core, and CLI regression coverage | Existing test backbone under `materials-discovery/tests/`. |

### Existing Runtime and Identity Helpers

| Module | Recommended Use | Why |
|--------|------------------|-----|
| `materials_discovery.llm.translated_benchmark` | Load the frozen benchmark set manifest and inventories | Phase 34 already solved the benchmark input contract. |
| `materials_discovery.llm.external_targets` | Resolve registrations and capture external environment lineage | Phase 35 already solved external target identity and smoke posture. |
| `materials_discovery.llm.launch` | Resolve internal serving lanes and build `LlmServingIdentity` | Internal controls should stay on existing checkpoint and serving lineage. |
| `materials_discovery.llm.runtime` | Send direct prompt requests through configured adapters | Reuses the repo's existing adapter abstractions for internal controls. |
| `materials_discovery.llm.serving_benchmark` | Follow summary and recommendation-line conventions | Good precedent for typed benchmark summaries without copying the wrong execution model. |

### Supporting Runtime Libraries

| Library | Recommended Use | Why |
|---------|------------------|-----|
| `transformers` | Optional local external-target generation path | Gives the benchmark a plausible local execution path without changing the repo's default dependency story. |
| `torch` | Optional external-target execution backend and hardware capture | Needed only when the external runner actually loads local checkpoints. |
| `pymatgen` | CIF parsing where available | Already part of the repo's scientific stack and useful for parser-backed validation. |

## Architecture Patterns

### Pattern 1: Typed benchmark targets, not loose config blobs

Use one typed benchmark spec with explicit target variants:

- external target references keyed by registered `model_id`
- internal control targets keyed by system config and requested lane or pin

Why: the scorecard needs different identity fields for external registrations
and internal controls, but the benchmark summary should not depend on ad hoc
YAML conventions.

### Pattern 2: Normalize every target into one case-result contract

Every eligible case execution should yield one typed result row carrying:

- target identity
- benchmark-case lineage
- `target_family`
- `fidelity_tier`
- response and parse status
- output hashes
- comparison metrics

Why: this is the seam that makes scorecard aggregation simple and keeps CLI
inspect surfaces from re-deriving facts later.

### Pattern 3: Preserve target eligibility and exclusions explicitly

Record excluded cases per target with typed reasons such as unsupported target
family or system mismatch. Do not infer exclusions only from missing case rows.

Why: `LLM-33` and `OPS-18` require visible eligible and excluded counts, and
the milestone research explicitly warns against silent denominator drift.

### Pattern 4: Reuse internal control identity rather than rebuilding it

Resolve internal controls through the shipped serving-lane and checkpoint
helpers, then store the resulting `LlmServingIdentity` or related lineage in
the benchmark artifacts.

Why: the repo already has the right identity discipline for promoted and pinned
checkpoint controls. Phase 36 should consume that discipline, not replace it.

### Pattern 5: Recommendation logic must privilege periodic-safe slices

Treat `exact` and `anchored` slices as the primary decision surface. Keep
`approximate` and `lossy` slices visible, but do not let them dominate the
headline recommendation.

Why: the milestone research and pitfalls docs explicitly warn against fidelity
misuse and overclaiming from proxy translations.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Benchmark input discovery | Live directory globs over translation exports | Phase 34 manifest + included inventory loading | Keeps benchmark slices reproducible. |
| Internal control identity | Custom benchmark-only control metadata | Existing serving-lane + checkpoint resolution | Preserves the shipped promoted/pinned control path. |
| Scorecards | One flat leaderboard with hidden exclusions | Typed summary sections by family, fidelity, and control delta | Matches `LLM-33` and avoids misleading output. |
| Docs surface | Raw JSON-only operator experience | One inspect command + runbook updates | Required for `OPS-18`. |

## Common Pitfalls

### Pitfall 1: Using different denominators for external and control deltas

**What goes wrong:** The external target and internal control are both reported,
but the delta uses whatever cases happened to succeed instead of the shared
eligible slice.

**How to avoid:** Persist target-level eligibility and compute control deltas
only from cases both sides were allowed to score.

### Pitfall 2: Letting prompt drift masquerade as model drift

**What goes wrong:** Benchmark results change because the prompt template
changed, not because the model or benchmark cases changed.

**How to avoid:** capture `prompt_contract_id` and a stable prompt hash in the
run manifest and treat model-specific wrapper changes as a distinct lane.

### Pitfall 3: Treating tiny or lossy slices as headline evidence

**What goes wrong:** One model looks strong on a tiny or lossy slice and the
summary overstates the strategic conclusion.

**How to avoid:** make periodic-safe slices the main decision surface and
downgrade recommendations when the slice is too small or too fidelity-limited.

## Concise Recommendation

Implement Phase 36 as one narrow comparative benchmark layer:

- typed benchmark spec and scorecard contracts
- deterministic benchmark artifact paths
- one core executor that reads frozen translated cases, resolves external and
  internal targets, writes per-target manifests and case results, and produces
  typed summaries
- one CLI run command and one inspect command
- one example benchmark spec and runbook

That is enough to satisfy `LLM-32`, `LLM-33`, and `OPS-18` without turning the
milestone into a generic runtime platform.

---
*Research completed: 2026-04-07*
*Ready for planning: yes*
