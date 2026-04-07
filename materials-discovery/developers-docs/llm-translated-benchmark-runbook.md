# Translated Benchmark Runbook

This runbook explains how to freeze one translated benchmark pack from one or
more translation bundles, how to inspect the resulting included and excluded
rows, and where the benchmark-pack artifacts live.

Phase 34 is deliberately narrow. It freezes and inspects the translated case
slice only. It does not register external runtimes, execute external models, or
emit scorecards yet.

---

## When to freeze a translated benchmark pack

Freeze a benchmark pack after `mdisc llm-translate` has produced the translation
bundle manifests you want to compare later.

Use this step when you need:

- one explicit, reusable benchmark-set ID
- a file-backed rule contract for system, target family, fidelity tier, and
  loss posture
- durable inventories showing which translated rows were included versus
  excluded before later benchmark phases reuse the slice

---

## Required inputs

You need:

1. one or more translation-bundle `manifest.json` files from Phase 33
2. one freeze spec YAML file
3. the normal repo workspace so the CLI can resolve relative artifact paths

The repo now ships a small demo spec at
`configs/llm/al_cu_fe_translated_benchmark_freeze.yaml`.

That sample spec points at two committed Al-Cu-Fe demo bundles:

- `data/llm_translation_exports/phase34_demo_al_cu_fe_cif_v1/manifest.json`
- `data/llm_translation_exports/phase34_demo_al_cu_fe_material_string_v1/manifest.json`

Those demo bundles are fixture-backed examples so operators can exercise the
freeze and inspect flow without writing custom Python first. For real benchmark
work, replace `bundle_manifest_paths` with manifests from your own
`llm-translate` runs.

---

## Freeze a benchmark pack

```bash
cd materials-discovery
uv run mdisc llm-translated-benchmark-freeze \
  --spec configs/llm/al_cu_fe_translated_benchmark_freeze.yaml
```

The command prints a JSON summary with:

- `benchmark_set_id`
- `manifest_path`
- `included_inventory_path`
- `excluded_inventory_path`
- included and excluded counts

The shipped sample spec freezes a CIF-only benchmark pack. It intentionally
keeps one material-string bundle in the source list so the inspect flow exposes
the target-family exclusion contract directly.

---

## Inspect a frozen pack

Inspect the full pack:

```bash
cd materials-discovery
uv run mdisc llm-translated-benchmark-inspect \
  --manifest data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json
```

Inspect only excluded rows:

```bash
uv run mdisc llm-translated-benchmark-inspect \
  --manifest data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json \
  --show excluded
```

Inspect one candidate:

```bash
uv run mdisc llm-translated-benchmark-inspect \
  --manifest data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json \
  --show all \
  --candidate-id al_cu_fe_fixture_periodic_001
```

The inspect command prints:

- benchmark-set ID
- target family
- selected systems
- included and excluded counts
- the persisted contract path
- human-readable included and excluded row traces

---

## Artifact layout

Each frozen benchmark pack writes one directory under:

```text
data/benchmarks/llm_external_sets/{benchmark_set_id}/
```

Files inside that directory:

- `freeze_contract.json` -- the normalized rule contract used for the freeze
- `manifest.json` -- benchmark-pack manifest with source bundle lineage and
  exclusion tallies
- `included.jsonl` -- rows that satisfied the freeze contract
- `excluded.jsonl` -- rows that were rejected, each with one typed exclusion
  reason

This artifact family is the Phase 34 handoff boundary for later benchmark work.

---

## How to interpret included versus excluded rows

Included rows passed every rule in the freeze spec:

- `systems`
- `target_family`
- `allowed_fidelity_tiers`
- `loss_posture`

Excluded rows fail exactly one typed rule and stay visible in `excluded.jsonl`
instead of disappearing silently.

Common exclusion reasons:

- `system_not_selected`
- `target_family_mismatch`
- `fidelity_tier_not_selected`
- `loss_posture_rejected`
- `duplicate_translation_row`

If you see an exclusion you did not intend, update the freeze spec and rerun
the freeze command. Do not patch `included.jsonl` by hand.

---

## Scope boundary

Phase 34 ends here:

- freeze one translated benchmark pack
- inspect the included and excluded inventories
- preserve the contract and lineage as first-class files

Deferred work:

- Phase 35 registers external target runtimes and reproducibility metadata
- Phase 36 executes comparative benchmarks and emits fidelity-aware scorecards

So this runbook does not cover external model registration, benchmark
execution, target smoke checks, or recommendation lines yet.
