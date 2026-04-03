# Reference-Aware Benchmark Runbook

This document describes the Phase 4 reference-aware no-DFT benchmark workflow:
how to run the two required benchmark lanes (`Al-Cu-Fe` and `Sc-Zn`), where
artifacts are written, and what each artifact represents.

---

## Overview

Phase 4 introduces **reference packs** (multi-source curated inputs) and
**benchmark packs** (comparable output summaries) on top of the existing
stage-by-stage pipeline.  The goal is to make the two benchmark lanes
reproducible and operator-comparable without replacing the `mdisc` stage
interface.

```
Reference pack (input)             Pipeline stages              Benchmark pack (output)
  data/external/sources/    →  ingest → generate → screen   →   data/reports/
  <source>/<snapshot>/          → hifi-validate → hifi-rank      <system>_benchmark_pack.json
  canonical_records.jsonl        → active-learn → report
```

---

## Prerequisites

### Python environment

```bash
cd materials-discovery
uv sync --extra dev
```

For exec-mode or native-mode validation you also need the MLIP extras:

```bash
uv sync --python 3.11 --extra dev --extra mlip
```

### Java / Zomic dependency (Sc-Zn lane only)

The `Sc-Zn` benchmark config includes `zomic_design:`, which means candidate
generation calls `./gradlew :core:zomicExport` in the vZome root.  This
requires a local Java runtime (11+).

If Java is absent the ingest and generate stages fall back to the pinned
fixture data already committed under `data/external/sources/`.  The
validation, rank, and report stages are not affected by the Java dependency.

---

## Running the full two-system benchmark

```bash
cd materials-discovery
./scripts/run_reference_aware_benchmarks.sh
```

This runs both benchmark lanes end to end.  Each lane executes:

1. `mdisc ingest`          — assemble the reference pack from staged sources
2. `mdisc generate`        — generate candidates from Zomic-backed or fixture seed
3. `mdisc screen`          — fast MLIP screening
4. `mdisc hifi-validate`   — committee, phonon, MD, XRD checks
5. `mdisc hifi-rank`       — calibrated ranking with benchmark context
6. `mdisc active-learn`    — active-learning model update
7. `mdisc report`          — experiment report + **benchmark-pack artifact**

At the end the script prints the path to each `benchmark_pack.json`.

---

## Developer smoke run

For a quick local check (fewer candidates, skip active-learn):

```bash
./scripts/run_reference_aware_benchmarks.sh --count 30 --no-active-learn
```

To run only one lane:

```bash
./scripts/run_reference_aware_benchmarks.sh --config-filter al_cu_fe
./scripts/run_reference_aware_benchmarks.sh --config-filter sc_zn
```

Dry-run to inspect commands without executing:

```bash
./scripts/run_reference_aware_benchmarks.sh --dry-run
```

---

## Benchmark configs

| System  | Config                                      | Reference sources             |
|---------|---------------------------------------------|-------------------------------|
| Al-Cu-Fe | `configs/systems/al_cu_fe_reference_aware.yaml` | hypodx + materials_project |
| Sc-Zn   | `configs/systems/sc_zn_reference_aware.yaml`    | hypodx + cod               |

Each config declares an `ingestion.reference_pack` block with:
- `pack_id`        — stable identifier for comparability
- `priority_order` — source merge order (first wins on conflicts)
- `members`        — source key, snapshot ID, and staged canonical path

---

## Reference-pack inputs

Staged canonical source snapshots live under:

```
data/external/sources/<source_key>/<snapshot_id>/canonical_records.jsonl
```

For offline and test runs the following fixtures are committed:

| Source            | Snapshot ID            | Path                                                                          |
|-------------------|------------------------|-------------------------------------------------------------------------------|
| hypodx (Al-Cu-Fe) | `hypodx_pinned_2026_03_09` | `data/external/sources/hypodx/hypodx_pinned_2026_03_09/canonical_records.jsonl` |
| materials_project | `mp_fixture_v1`        | `data/external/sources/materials_project/mp_fixture_v1/canonical_records.jsonl` |
| hypodx (Sc-Zn)    | `hypodx_fixture_local` | `data/external/sources/hypodx/hypodx_fixture_local/canonical_records.jsonl`    |
| cod               | `cod_fixture_v1`       | `data/external/sources/cod/cod_fixture_v1/canonical_records.jsonl`             |

---

## Benchmark-pack outputs

After `mdisc report`, a `benchmark_pack.json` is written to:

```
data/reports/<system_slug>_benchmark_pack.json
```

For example:
- `data/reports/al_cu_fe_reference_aware_benchmark_pack.json`
- `data/reports/sc_zn_reference_aware_benchmark_pack.json`

Each benchmark pack has this structure:

```json
{
  "schema_version": "benchmark-pack/v1",
  "system": "Al-Cu-Fe",
  "backend_mode": "real",
  "benchmark_context": {
    "reference_pack_id": "al_cu_fe_v1",
    "reference_pack_fingerprint": "...",
    "source_keys": ["hypodx", "materials_project"],
    "benchmark_corpus": "data/benchmarks/al_cu_fe_benchmark.json",
    "backend_mode": "real",
    "lane_id": "al_cu_fe_v1:real"
  },
  "stage_manifest_paths": { ... },
  "report_metrics": {
    "report_fingerprint": "...",
    "release_gate": { ... }
  }
}
```

The `benchmark_context` block is the key comparable identifier.  Two runs
from different source adapters or backend modes will have different `lane_id`
values, making cross-lane comparison unambiguous.

---

## Pipeline manifests

The `mdisc report` stage also writes a pipeline-level manifest:

```
data/manifests/<system_slug>_pipeline_manifest.json
```

This manifest links the per-stage `manifest_path` values together into a
single provenance chain.

---

## Running existing single-lane scripts

The pre-Phase 4 operator scripts remain valid for baseline comparison:

```bash
./scripts/run_real_pipeline.sh        # Al-Cu-Fe real mode (baseline)
./scripts/run_exec_pipeline.sh        # Al-Cu-Fe exec mode (command-backed)
./scripts/run_native_pipeline.sh      # Al-Cu-Fe native MLIP mode
```

These scripts use `al_cu_fe_real.yaml`, `al_cu_fe_exec.yaml`, and
`al_cu_fe_native.yaml` respectively.  They do not write benchmark-pack
artifacts (only `mdisc report` triggered from a reference-aware config does).

---

## Stage commands reference

All benchmark stages are thin wrappers around the standard CLI:

```bash
uv run mdisc ingest         --config <config>
uv run mdisc generate       --config <config> [--count N] [--seed N]
uv run mdisc screen         --config <config>
uv run mdisc hifi-validate  --config <config> --batch all
uv run mdisc hifi-rank      --config <config>
uv run mdisc active-learn   --config <config>
uv run mdisc report         --config <config>
```

All commands print a JSON summary to stdout on success.

---

## Running the regression tests

```bash
cd materials-discovery
uv run pytest tests/test_real_mode_pipeline.py tests/test_hifi_rank.py tests/test_report.py
```

The test suite includes:
- End-to-end integration tests for both Phase 4 benchmark systems
- Benchmark-pack artifact assertion (`test_benchmark_pack_written_by_report_command`)
- Cross-lane context key comparison (`test_cross_lane_benchmark_context_keys_match`)
- Rank provenance embedding (`test_rank_embeds_benchmark_context_when_supplied`)
- Report benchmark surfacing (`test_report_emits_benchmark_context_when_ranked_candidates_carry_it`)

Full suite:

```bash
uv run pytest
```

---

## See also

- [Pipeline Stages](pipeline-stages.md) — per-command behavior and output contracts
- [Configuration Reference](configuration-reference.md) — config schema and benchmark-corp options
- [Data Schema Reference](data-schema-reference.md) — manifest and benchmark-pack schema
- [Backend System](backend-system.md) — adapter layers and runtime selection
