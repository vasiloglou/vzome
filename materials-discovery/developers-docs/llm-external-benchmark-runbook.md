# External Benchmark Runbook

This runbook explains how to execute one translated comparative benchmark
across curated external materials LLMs and current internal controls, how to
inspect the resulting scorecard, and where the Phase 36 artifacts live.

Phase 36 is deliberately benchmark-first. It executes and inspects one
comparative benchmark workflow, but it does not auto-promote models, schedule
future milestones, or build a generic serving platform.

---

## When to run the comparative benchmark

Run this workflow after:

- Phase 34 has frozen the translated benchmark pack you want to reuse
- Phase 35 has registered and smoke-tested the external target models you want
  to compare
- one or more internal control lanes already exist in `configs/systems/`

Use this step when you need:

- one file-backed benchmark spec for external-versus-internal comparison
- per-target run artifacts with explicit eligibility, exclusion, and lineage
- fidelity-aware scorecards that separate exact or anchored evidence from
  approximate or lossy diagnostics
- recommendation lines that stay advisory instead of pretending to decide the
  roadmap automatically

---

## Required inputs

You need:

1. one frozen translated benchmark-set `manifest.json` from Phase 34
2. one or more Phase 35 external-target registrations identified by `model_id`
3. one or more internal control arms defined by `system_config_path` plus
   `generation_model_lane`
4. one benchmark spec YAML file

The repo ships a small example spec at:

`configs/llm/al_cu_fe_external_benchmark.yaml`

That sample spec reuses:

- `data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json`
- `al_cu_fe_external_cif_demo` as the example external target model ID
- `configs/systems/al_cu_fe_llm_local.yaml` as the internal control config

The sample spec is intentionally narrow. It gives operators one reproducible
benchmark path without implying that every external model or every target
family should be compared at once.

---

## Run the benchmark

```bash
cd materials-discovery
uv run mdisc llm-external-benchmark \
  --spec configs/llm/al_cu_fe_external_benchmark.yaml
```

The command prints the typed benchmark summary JSON. That summary includes:

- `benchmark_id`
- `benchmark_set_id`
- benchmark-level recommendation lines
- failed target IDs
- one typed target summary per external arm or internal control

To write the summary JSON to a custom path:

```bash
uv run mdisc llm-external-benchmark \
  --spec configs/llm/al_cu_fe_external_benchmark.yaml \
  --out /tmp/al_cu_fe_external_benchmark_summary.json
```

---

## Inspect the scorecard

Inspect the full scorecard:

```bash
cd materials-discovery
uv run mdisc llm-inspect-external-benchmark \
  --summary data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/benchmark_summary.json
```

Inspect one target only:

```bash
uv run mdisc llm-inspect-external-benchmark \
  --summary data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/benchmark_summary.json \
  --target-id crystallm_cif_demo
```

The inspect command prints a concise human-readable trace showing:

- benchmark ID and benchmark-set ID
- target kind and control-arm identity
- eligible and excluded counts
- overall scorecard metrics
- target-family slices
- fidelity-tier slices
- shared eligible control deltas
- recommendation lines

---

## Artifact layout

Each comparative benchmark writes one directory under:

```text
data/benchmarks/llm_external/{benchmark_id}/
```

Benchmark-level files:

- `benchmark_summary.json` -- typed benchmark summary used by the inspect
  command
- `scorecard_by_case.jsonl` -- combined per-case scorecard rows across every
  target
- `smoke_checks.json` -- benchmark-level capture of the external-target smoke
  results observed during execution

Per-target files:

- `targets/{target_id}/run_manifest.json`
- `targets/{target_id}/case_results.jsonl`
- `targets/{target_id}/raw_responses.jsonl`

These artifacts are the Phase 36 handoff boundary. Later milestone decisions
should read from them instead of reconstructing benchmark state from terminal
output.

---

## How to interpret the scorecard

### Eligible versus excluded counts

- `eligible_count` means the target was allowed to attempt that slice
- `excluded_count` means the case stayed visible but was not scored because of
  explicit target-family or system mismatch, or because an external target
  failed its smoke gate

Excluded cases are part of the benchmark story. They should not disappear from
the denominator silently.

### Target-family and fidelity slices

- `by_target_family` separates CIF and material-string evidence instead of
  blending incompatible representations
- `by_fidelity_tier` keeps exact or anchored evidence visible as the
  periodic-safe decision surface and leaves approximate or lossy rows visible
  as diagnostics

If a target looks strong only on lossy rows, treat that as a lead to explore,
not proof that the model is ready for broader automation.

### Control deltas

Control deltas compare one external target against one internal control only on
the shared eligible slice. They tell you whether the target was better, worse,
or roughly similar on the cases both sides were actually allowed to answer.

### Recommendation lines

Recommendation lines intentionally stay bounded:

- deeper investment
- targeted follow-up
- not competitive
- diagnostic-only because the periodic-safe slice is missing
- runtime-first when smoke or execution failed

These lines are milestone evidence, not autonomous product decisions.

---

## Scope boundary

Phase 36 ends here:

- run one typed comparative benchmark from a spec file
- inspect typed benchmark summaries and per-target artifacts
- keep recommendation lines explicit and advisory

Deferred work:

- automatic checkpoint promotion or external-target rollout
- generic model downloads or server lifecycle management
- campaign automation triggered directly from benchmark winners
- dashboard or service-backed reporting

So this runbook does not authorize autonomous roadmap changes. It provides one
benchmark-first decision surface for later milestone selection.
