# Materials Discovery Operator Runbook

Single source of truth for operating the no-DFT quasicrystal materials discovery
platform.  Covers environment setup, ingestion, reference-pack assembly, pipeline
execution, benchmarking, data lake operations, analytics notebooks, and
troubleshooting.

For deep-dive reference see the developer docs in `developers-docs/`.

---

## Prerequisites

### Python environment

```bash
cd materials-discovery
uv sync --extra dev
```

For exec-mode or native-mode MLIP backends:

```bash
uv sync --python 3.11 --extra dev --extra mlip
```

### API keys for external sources (optional)

Some source adapters (Materials Project, JARVIS) can query live APIs.  Set the
following environment variables before ingestion if you want live data; the
platform works offline with checked-in fixture snapshots otherwise.

```bash
export MP_API_KEY="your_materials_project_api_key"
# No API key required for HYPOD-X, COD, or OQMD with the offline adapters
```

### Java runtime (Sc-Zn Zomic lane only)

Zomic-backed candidate generation calls `./gradlew :core:zomicExport` from the
vZome root and requires a local Java 11+ runtime.  If Java is absent the ingest
and generate stages fall back to the pinned fixture snapshots committed under
`data/external/sources/`.

---

## 1. Ingestion

### 1.1 Configure a System

All pipeline runs are driven by a YAML config in `configs/systems/`.  The
repository ships several reference configs:

| Config file | System | Backend mode |
|---|---|---|
| `al_cu_fe.yaml` | Al-Cu-Fe | mock |
| `al_cu_fe_real.yaml` | Al-Cu-Fe | real (fixture) |
| `al_cu_fe_reference_aware.yaml` | Al-Cu-Fe | real + multi-source ref pack |
| `sc_zn_reference_aware.yaml` | Sc-Zn | real + multi-source ref pack |
| `sc_zn_zomic.yaml` | Sc-Zn | mock + Zomic generation |
| `ti_zr_ni.yaml` | Ti-Zr-Ni | mock |

Minimum config for a new system:

```yaml
system_name: "Al-Cu-Fe"
template_family: icosahedral_approximant_1_1
species: [Al, Cu, Fe]
composition_bounds:
  Al: {min: 0.60, max: 0.75}
  Cu: {min: 0.10, max: 0.20}
  Fe: {min: 0.10, max: 0.20}
coeff_bounds: {min: -3, max: 3}
seed: 42
default_count: 100

backend:
  mode: mock
```

Key `ingestion` fields (when using the source-registry bridge):

```yaml
ingestion:
  source_key: hypodx          # source adapter key
  snapshot_id: hypodx_pinned_2026_03_09
  use_cached_snapshot: true   # reuse staged canonical records if present
```

See `developers-docs/configuration-reference.md` for the full schema.

### 1.2 Run Ingestion (single source)

```bash
uv run mdisc ingest --config configs/systems/al_cu_fe.yaml
```

Expected artifacts:

- `data/processed/<system_slug>_reference_phases.jsonl` — processed ingest rows
- `data/manifests/<system_slug>_ingest_manifest.json` — stage manifest with lineage

Output summary printed to stdout on success:

```json
{
  "schema_version": "ingest/v1",
  "system_name": "Al-Cu-Fe",
  "record_count": 5,
  ...
}
```

### 1.3 Source-backed Ingestion (reference pack)

For benchmark-quality runs with multi-source reference packs:

```bash
uv run mdisc ingest --config configs/systems/al_cu_fe_reference_aware.yaml
```

This triggers reference-pack assembly: each member source is staged separately,
records are deduplicated by composition+phase (higher-priority source wins), and a
combined `reference_pack` artifact is written under `data/external/reference_packs/`.

See Section 2 for reference-pack assembly details.

---

## 2. Reference Pack Assembly

A reference pack is a deduplicated, prioritized merge of canonical records from
multiple source adapters.  Use reference packs when you need:

- Reproducible multi-source ingest for benchmark comparison
- Explicit source priority ordering (e.g. QC database wins over general MP)
- Cached pack reuse across runs without re-staging sources

**When to assemble a new pack vs. reuse cached:**
- New pack: changing `members` sources, snapshot IDs, or priority order
- Reuse cached: same pack_id and all source snapshots unchanged — set `use_cached_snapshot: true`

### Config structure for a reference pack

```yaml
ingestion:
  reference_pack:
    pack_id: al_cu_fe_v1
    priority_order: [hypodx, materials_project]
    members:
      - source_key: hypodx
        snapshot_id: hypodx_pinned_2026_03_09
        use_cached_snapshot: true
      - source_key: materials_project
        snapshot_id: mp_fixture_v1
        use_cached_snapshot: true
```

### Expected artifacts

After assembly the following are written:

```
data/external/reference_packs/<pack_id>/
  canonical_records.jsonl   # merged, deduplicated canonical records
  pack_manifest.json        # pack fingerprint, member lineage, record counts
```

---

## 3. Pipeline Execution

Run stages in order.  Each stage reads the previous stage's output from
`data/` and writes its own artifact.

### 3.1 Generate Candidates

```bash
uv run mdisc generate --config configs/systems/al_cu_fe.yaml
# Override count or seed:
uv run mdisc generate --config configs/systems/al_cu_fe.yaml --count 50 --seed 7
```

Output: `data/candidates/<system_slug>_candidates.jsonl`

### 3.2 Screen

```bash
uv run mdisc screen --config configs/systems/al_cu_fe.yaml
```

Applies fast geometry and energy-proxy filters.  Output:
`data/screened/<system_slug>_screened.jsonl`

### 3.3 High-Fidelity Validation

```bash
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch all
```

Runs committee relaxation, geometry prefilter, phonon MLIP checks, MD stability,
and XRD validation.  Output: `data/hifi_validated/<system_slug>_validated.jsonl`

For validation on a specific batch:

```bash
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch top50
```

### 3.4 Rank

```bash
uv run mdisc hifi-rank --config configs/systems/al_cu_fe.yaml
```

Calibrated ranking with benchmark context embedding.  Output:
`data/ranked/<system_slug>_ranked.jsonl`

### 3.5 Active Learning (optional)

```bash
uv run mdisc active-learn --config configs/systems/al_cu_fe.yaml
```

Updates the surrogate model and records suggestions for the next candidate batch.
Output: `data/active_learning/<system_slug>_active_learn_summary.json`

### 3.6 Report

```bash
uv run mdisc report --config configs/systems/al_cu_fe.yaml
```

Produces the experiment report and (for reference-aware configs) the
benchmark-pack artifact.  Expected outputs:

- `data/reports/<system_slug>_report.json` — full experiment report with per-candidate metrics
- `data/reports/<system_slug>_benchmark_pack.json` — benchmark-pack artifact (reference-aware configs only)
- `data/manifests/<system_slug>_pipeline_manifest.json` — full pipeline provenance chain

---

## 4. Benchmarking

### 4.1 Run the Full Benchmark Suite

The Phase 4 benchmark runner executes both Al-Cu-Fe and Sc-Zn reference-aware lanes:

```bash
bash scripts/run_reference_aware_benchmarks.sh
```

Quick smoke run (30 candidates, skip active-learn):

```bash
bash scripts/run_reference_aware_benchmarks.sh --count 30 --no-active-learn
```

Run a single lane:

```bash
bash scripts/run_reference_aware_benchmarks.sh --config-filter al_cu_fe
bash scripts/run_reference_aware_benchmarks.sh --config-filter sc_zn
```

Dry-run to inspect commands without executing:

```bash
bash scripts/run_reference_aware_benchmarks.sh --dry-run
```

### 4.2 Benchmark Artifacts

Each benchmark lane produces:

| Artifact | Path |
|---|---|
| Benchmark pack | `data/reports/<system_slug>_benchmark_pack.json` |
| Pipeline manifest | `data/manifests/<system_slug>_pipeline_manifest.json` |
| Per-stage manifests | `data/manifests/` (one per stage) |
| Calibration outputs | `data/calibration/` |

**benchmark_pack.json structure:**

```json
{
  "schema_version": "benchmark-pack/v1",
  "system": "Al-Cu-Fe",
  "backend_mode": "real",
  "benchmark_context": {
    "reference_pack_id": "al_cu_fe_v1",
    "reference_pack_fingerprint": "abc123...",
    "source_keys": ["hypodx", "materials_project"],
    "lane_id": "al_cu_fe_v1:real"
  },
  "stage_manifest_paths": {
    "ingest": "data/manifests/al_cu_fe_reference_aware_ingest_manifest.json",
    "report": "data/reports/al_cu_fe_reference_aware_report.json",
    ...
  },
  "report_metrics": {
    "release_gate": { "min_hifi_candidates": true, "min_xrd_confidence": false },
    "summary": { ... }
  }
}
```

The `benchmark_context.lane_id` is the stable identifier for cross-run comparison.
Two runs with different source packs or backend modes produce different `lane_id`
values, making comparison unambiguous.

See `developers-docs/reference-aware-benchmarks.md` for full benchmark workflow details.

---

## 5. Data Lake Operations

The data lake provides a cross-run catalog and comparison layer on top of the
`data/` artifact directories.

### 5.1 Index the Lake

```bash
uv run mdisc lake index
```

This scans all 17 artifact directories, writes `_catalog.json` into each existing
directory, and produces a lake-wide index at `data/lake_index.json`.

**What it produces:**

- `data/<subdir>/_catalog.json` — per-directory catalog with record count, size,
  schema version, lineage pointers, staleness flag, and content hash
- `data/lake_index.json` — rollup index aggregating all directory catalogs

Staleness detection: a catalog entry is marked stale when the manifest's
`output_hashes` no longer match the recorded `content_hash`.  mtime is used as a
secondary hint only.

### 5.2 Check Lake Stats

```bash
uv run mdisc lake stats
```

Prints a summary table:

```
artifact_directories : 5
total_entries        : 12
stale_count          : 2
latest_run_utc       : 2026-04-03T18:00:00+00:00
workspace_root       : materials-discovery
```

Reading the output:
- `stale_count > 0`: some artifacts may need re-indexing or re-running
- `total_entries`: total artifact files catalogued across all directories

### 5.3 Compare Benchmark Runs

```bash
uv run mdisc lake compare data/reports/al_cu_fe_reference_aware_benchmark_pack.json \
                           data/reports/sc_zn_reference_aware_benchmark_pack.json
```

The command prints a dual-format table (gate results + metric distributions) to
stdout and writes a JSON file to `data/comparisons/`.

**Reading the comparison:**

```
Gate results:
  "both_pass"    — both lanes pass this gate
  "both_fail"    — both lanes fail
  "regression"   — lane A passed but lane B fails
  "improvement"  — lane A failed but lane B passes

Metric distributions:
  mean_a / mean_b  — per-lane population mean (from report entries)
  delta            — lane_b.mean - lane_a.mean (positive = B higher)
```

For custom output directory:

```bash
uv run mdisc lake compare pack_a.json pack_b.json --output-dir /path/to/dir
```

JSON-only output (no table):

```bash
uv run mdisc lake compare pack_a.json pack_b.json --json-only
```

**Example: comparing Al-Cu-Fe vs Sc-Zn**

```bash
uv run mdisc lake compare \
  data/reports/al_cu_fe_reference_aware_benchmark_pack.json \
  data/reports/sc_zn_reference_aware_benchmark_pack.json
```

This compares the two Phase 4 benchmark systems across gate results and all 8 key
metrics (hifi_score, stability_probability, ood_score, xrd_confidence,
xrd_distinctiveness, delta_e_proxy_hull_ev_per_atom, uncertainty_ev_per_atom,
md_stability_score).

---

## 6. Analytics Notebooks

Three Jupyter notebooks under `notebooks/` provide operator-facing analytics:

| Notebook | Purpose |
|---|---|
| `source_contribution_analysis.ipynb` | Which source contributed the most high-priority candidates |
| `cross_run_drift_detection.ipynb` | How results shift between two benchmark runs |
| `metric_distribution_deep_dive.ipynb` | Full metric distribution visualizations for one or more reports |

### How to launch

```bash
cd materials-discovery
jupyter notebook notebooks/
# or for JupyterLab:
jupyter lab notebooks/
```

### Configuring notebook parameters

Each notebook has a dedicated **CONFIGURATION** cell at the top (cell 2).  Edit
variables in that cell before running the notebook.  Key variables:

**source_contribution_analysis.ipynb:**
```python
SYSTEM_NAME = "Al-Cu-Fe"   # change to your target system
REPORT_PATH = WORKSPACE / "data" / "reports" / f"{SYSTEM_NAME.lower().replace('-', '_')}_report.json"
HIGH_THRESHOLD = 0.3       # hifi_score <= this = "high" priority
MEDIUM_THRESHOLD = 0.5
```

**cross_run_drift_detection.ipynb:**
```python
PACK_A_PATH = WORKSPACE / "data" / "benchmarks" / "al_cu_fe_benchmark.json"
PACK_B_PATH = WORKSPACE / "data" / "benchmarks" / "sc_zn_benchmark.json"
```

**metric_distribution_deep_dive.ipynb:**
```python
SYSTEM_NAME = "Al-Cu-Fe"
# For overlay mode (multiple reports):
OVERLAY_REPORTS = [
    (WORKSPACE / "data" / "reports" / "al_cu_fe_report.json", "Al-Cu-Fe"),
    (WORKSPACE / "data" / "reports" / "sc_zn_report.json", "Sc-Zn"),
]
```

All notebooks degrade gracefully when data files are absent — they print an
informative message and skip plotting cells rather than crashing.

### Notebook smoke tests

```bash
uv run python -m pytest tests/test_notebooks.py -v
```

Static tests always run (valid JSON, correct imports, workspace_root usage).
Execution smoke tests run if `nbformat` and `nbconvert` are installed:

```bash
pip install nbformat nbconvert
uv run python -m pytest tests/test_notebooks.py -v
```

---

## 7. Troubleshooting

### 7.1 Source Adapter Timeouts

**Symptom:** `mdisc ingest` hangs or raises `httpx.TimeoutException`.

**Cause:** API-backed adapter (Materials Project, OQMD, JARVIS) is trying to
reach a live endpoint with a slow or unavailable network.

**Resolution:**
1. Check `use_cached_snapshot: true` in your config's ingestion block
2. Use the fixture snapshot instead of a live query:
   ```yaml
   ingestion:
     snapshot_id: mp_fixture_v1
     use_cached_snapshot: true
   ```
3. Set a longer timeout via environment variable (adapter-specific):
   ```bash
   HTTPX_TIMEOUT=60 uv run mdisc ingest --config configs/systems/al_cu_fe_reference_aware.yaml
   ```
4. For completely offline operation, use the local HYPOD-X fixture:
   ```bash
   uv run mdisc ingest --config configs/systems/al_cu_fe.yaml
   ```

### 7.2 Re-running Single Stages

The pipeline is file-backed: each stage reads from the previous stage's output
directory.  You can re-run any stage in isolation.

```bash
# Re-run just the screen stage:
uv run mdisc screen --config configs/systems/al_cu_fe.yaml

# Re-run just hifi-validate on the top 50:
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch top50

# Re-run report (regenerates benchmark-pack from existing ranked output):
uv run mdisc report --config configs/systems/al_cu_fe.yaml
```

Each re-run overwrites the stage's output artifacts and updates the stage
manifest.  You do NOT need to re-run earlier stages unless their inputs changed.

### 7.3 Inspecting Stale Catalog Entries

**Symptom:** `mdisc lake stats` shows `stale_count > 0`.

**Cause:** Artifacts on disk have changed since the last `lake index` run, or
manifest `output_hashes` have been updated.

**Resolution:**
```bash
# Re-index the lake to refresh all catalogs:
uv run mdisc lake index

# Check stats again:
uv run mdisc lake stats
```

If stale entries persist after re-indexing, the underlying artifact may have
been modified outside of the pipeline.  Inspect the specific directory:

```bash
# Read the per-directory catalog:
cat data/processed/_catalog.json | python3 -m json.tool | grep -A2 "is_stale"
```

### 7.4 Common Config Errors

**Missing `system_name`:**

```
ValidationError: system_name: Field required
```

Every config must include `system_name`.  Add it to your YAML:

```yaml
system_name: "My-System"
```

**Wrong `backend.mode`:**

```
ValueError: Unknown backend mode: 'exec_mode'
```

Valid modes are: `mock`, `real`, `exec`, `native`.  Use lowercase without underscores.

**Missing benchmark corpus:**

```
FileNotFoundError: Benchmark corpus not found: data/benchmarks/al_cu_fe_benchmark.json
```

The benchmark corpus file is required for `real` mode validation.  Check the path
in your config under `backend.benchmark_corpus` and confirm the file exists.

**Mutually exclusive prototype options:**

```
ValueError: prototype_library and zomic_design are mutually exclusive
```

Remove one of the two fields from your config.

### 7.5 Pipeline Failures

**Reading manifest output_hashes for debugging:**

Each stage writes a manifest with `output_hashes`.  Check if hashes are populated:

```bash
cat data/manifests/al_cu_fe_ingest_manifest.json | python3 -m json.tool | grep -A10 output_hashes
```

Empty `output_hashes` indicates the stage exited early or raised an exception.
Check the stage's stdout/stderr for the error message.

**Checking stage-level manifests:**

```bash
ls -la data/manifests/
# Inspect the most recent:
cat data/manifests/al_cu_fe_screen_manifest.json | python3 -m json.tool
```

**Pipeline manifest linking all stages:**

```bash
cat data/manifests/al_cu_fe_pipeline_manifest.json | python3 -m json.tool
```

This shows the full provenance chain with each stage's manifest path and
whether the stage was run.

**Candidates JSONL is empty after screening:**

```bash
wc -l data/screened/al_cu_fe_screened.jsonl
```

If zero lines, all candidates were filtered out.  Lower the thresholds in your
config or increase candidate count.

**Java not found (Sc-Zn Zomic lane):**

```
FileNotFoundError: No such file or directory: 'java'
```

Install Java 11+, or switch to the fixture-backed config that skips Zomic export:

```bash
uv run mdisc ingest --config configs/systems/sc_zn_reference_aware.yaml
# Falls back to pinned fixture data automatically when Java is absent
```

---

## 8. Closed-Loop LLM Workflow

Phase 12 makes the closed-loop LLM path usable end to end without changing the
manual pipeline contract. The safe operator sequence is:

```bash
uv run mdisc llm-suggest --acceptance-pack data/benchmarks/llm_acceptance/pack_v1/acceptance_pack.json
uv run mdisc llm-approve --proposal data/benchmarks/llm_acceptance/pack_v1/proposals/<proposal_id>.json --decision approved --operator you@example.com --config configs/systems/al_cu_fe_llm_mock.yaml
uv run mdisc llm-launch --campaign-spec data/llm_campaigns/<campaign_id>/campaign_spec.json
uv run mdisc llm-replay --launch-summary data/llm_campaigns/<campaign_id>/launches/<launch_id>/launch_summary.json
uv run mdisc llm-compare --launch-summary data/llm_campaigns/<campaign_id>/launches/<replay_launch_id>/launch_summary.json
```

What each step does:
- `llm-suggest` stays dry-run and writes typed proposals next to the acceptance pack.
- `llm-approve` writes a separate approval artifact and, when approved, a self-contained `campaign_spec.json`.
- `llm-launch` resolves the approved spec into a standard `llm-generate` run without mutating the source YAML.
- `llm-replay` reuses the recorded launch bundle strictly. It records current-vs-source config drift, but Phase 12 exposes no behavioral override flags.
- `llm-compare` always compares the targeted launch against the acceptance-pack baseline and also against the most recent prior launch when one exists.

The audit trail on disk is:

| Artifact | Path |
|---|---|
| Campaign spec | `data/llm_campaigns/{campaign_id}/campaign_spec.json` |
| Resolved launch | `data/llm_campaigns/{campaign_id}/launches/{launch_id}/resolved_launch.json` |
| Launch summary | `data/llm_campaigns/{campaign_id}/launches/{launch_id}/launch_summary.json` |
| Outcome snapshot | `data/llm_campaigns/{campaign_id}/launches/{launch_id}/outcome_snapshot.json` |
| Comparison result | `data/llm_campaigns/{campaign_id}/comparisons/{comparison_id}.json` |

Interpretation notes:
- Replay is strict in Phase 12. If the recorded launch bundle is incomplete or the pinned config path is gone, the replay fails instead of silently changing behavior.
- Missing downstream metrics in `llm-compare` are reported explicitly in `missing_metrics`; they are not treated as zero.
- A replayed run still writes normal candidate JSONL and standard manifests, so later commands like `screen`, `hifi-validate`, `hifi-rank`, and `report` remain manual and unchanged.

See also:
- `developers-docs/llm-integration.md`
- `developers-docs/pipeline-stages.md`

## 9. Quick Reference

### All mdisc commands

| Command | Description |
|---|---|
| `mdisc ingest --config <cfg>` | Ingest reference phases from configured source |
| `mdisc export-zomic --design <yaml>` | Export a Zomic design to an orbit-library JSON |
| `mdisc generate --config <cfg> [--count N] [--seed N]` | Generate candidate structures |
| `mdisc screen --config <cfg>` | Fast geometry and energy-proxy screening |
| `mdisc hifi-validate --config <cfg> --batch <all\|topN>` | High-fidelity MLIP validation |
| `mdisc hifi-rank --config <cfg>` | Calibrated ranking with benchmark context |
| `mdisc active-learn --config <cfg>` | Update surrogate and select next batch |
| `mdisc report --config <cfg>` | Produce experiment report and benchmark pack |
| `mdisc llm-suggest --acceptance-pack <pack>` | Emit dry-run campaign proposals from an acceptance pack |
| `mdisc llm-approve --proposal <proposal> --decision <approved\|rejected> --operator <id>` | Write approval artifacts and optional campaign spec |
| `mdisc llm-launch --campaign-spec <spec>` | Launch an approved campaign through the existing LLM generation runtime |
| `mdisc llm-replay --launch-summary <summary>` | Strictly replay a recorded launch bundle with a fresh launch wrapper |
| `mdisc llm-compare --launch-summary <summary>` | Compare a launch against the acceptance-pack baseline and prior launch |
| `mdisc lake index` | Build per-directory catalogs and lake-wide index |
| `mdisc lake stats` | Print lake artifact counts and staleness summary |
| `mdisc lake compare <pack_a> <pack_b>` | Compare two benchmark packs (gate + metrics) |

### Key file paths

| Path | Description |
|---|---|
| `configs/systems/` | YAML system configs |
| `data/processed/` | Ingested reference phases (JSONL) |
| `data/candidates/` | Generated candidates (JSONL) |
| `data/screened/` | Screened candidates (JSONL) |
| `data/hifi_validated/` | HiFi-validated candidates (JSONL) |
| `data/ranked/` | Ranked candidates (JSONL) |
| `data/reports/` | Experiment reports and benchmark packs (JSON) |
| `data/manifests/` | Stage and pipeline manifests (JSON) |
| `data/calibration/` | Stage calibration outputs (JSON) |
| `data/benchmarks/` | Benchmark corpus files (JSON) |
| `data/benchmarks/llm_acceptance/` | Acceptance packs, dry-run suggestions, proposals, and approvals |
| `data/llm_campaigns/` | Campaign specs, launch wrappers, outcome snapshots, and comparisons |
| `data/llm_runs/` | Raw prompt/completion/compile artifacts for each LLM generation run |
| `data/external/sources/` | Staged canonical source snapshots (JSONL) |
| `data/external/reference_packs/` | Assembled reference packs |
| `data/comparisons/` | Cross-lane comparison results (JSON) |
| `data/lake_index.json` | Lake-wide artifact index |
| `notebooks/` | Analytics notebooks |
| `scripts/run_reference_aware_benchmarks.sh` | Benchmark runner |

### Config file locations

| Config | Purpose |
|---|---|
| `configs/systems/al_cu_fe.yaml` | Al-Cu-Fe mock mode |
| `configs/systems/al_cu_fe_real.yaml` | Al-Cu-Fe real mode |
| `configs/systems/al_cu_fe_reference_aware.yaml` | Al-Cu-Fe with multi-source ref pack |
| `configs/systems/al_cu_fe_llm_mock.yaml` | Al-Cu-Fe mock LLM closed-loop workflow |
| `configs/systems/sc_zn_reference_aware.yaml` | Sc-Zn with multi-source ref pack |
| `configs/systems/sc_zn_zomic.yaml` | Sc-Zn with Zomic generation |
| `configs/systems/ti_zr_ni.yaml` | Ti-Zr-Ni mock mode |

### See also

- `developers-docs/pipeline-stages.md` — per-command behavior and output contracts
- `developers-docs/configuration-reference.md` — full config schema reference
- `developers-docs/reference-aware-benchmarks.md` — Phase 4 benchmark workflow
- `developers-docs/backend-system.md` — adapter layers and runtime mode selection
- `developers-docs/zomic-design-workflow.md` — Zomic structure authoring
- `REAL_MODE_EXECUTION_PLAN.md` — real-mode execution phases and MLIP integration
