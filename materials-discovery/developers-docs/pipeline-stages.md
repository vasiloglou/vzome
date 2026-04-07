# Materials Discovery Pipeline Stages

This document describes each CLI command in the `mdisc` materials discovery
pipeline. Every command is defined in
`materials-discovery/src/materials_discovery/cli.py`. All commands share a
common error-handling pattern: `FileNotFoundError`, `ValidationError`, and
`ValueError` are caught, printed to stderr, and the process exits with code 2.
`mdisc export-zomic` also catches `RuntimeError` so subprocess export failures are
reported with the same exit code. Most commands print a JSON summary object to
stdout on success; `mdisc llm-translate-inspect` intentionally prints a
human-readable bundle summary instead.

Path placeholders used below:

| Placeholder | Meaning |
|---|---|
| `{slug}` | `system_name` from the config, lowercased with hyphens replaced by underscores (`_system_slug`) |
| `{batch_slug}` | The `--batch` value normalized to lowercase alphanumeric with underscores (`_batch_slug`) |
| `{export_id}` | The explicit translation export identifier passed to `mdisc llm-translate` |
| `{workspace}` | The workspace root directory resolved by `workspace_root()` |

---

## 1. `mdisc ingest`

Ingest and normalize fixture metadata into processed JSONL.

### CLI syntax

```
mdisc ingest --config PATH [--fixture PATH] [--out PATH]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |
| `--fixture` | PATH | No | `None` | Path to an optional fixture file for the ingest backend |
| `--out` | PATH | No | `data/processed/{slug}_reference_phases.jsonl` | Output path for the processed JSONL |

### Internal steps

1. **Load configuration.** Read the YAML file at `--config` and validate it as
   a `SystemConfig` via Pydantic.
2. **Resolve the ingest backend.** Call `resolve_ingest_backend(mode,
   ingest_adapter)` using the backend mode and optional ingest adapter from the
   config. Retrieve backend metadata via `backend.info()`.
3. **Load raw rows.** Call `backend.load_rows(system_config, fixture)` to
   obtain the raw data. When `--fixture` is provided the backend reads from
   that path; otherwise it uses its default data source.
4. **Ingest rows.** Call `ingest_rows(system_config, raw_rows, out_path,
   backend_mode, backend_adapter)` to normalize and write the processed JSONL.
   This function returns an `IngestSummary`.
5. **Write manifest.** Build a stage manifest via `build_manifest(stage="ingest", ...)`
   including backend version information and the output path. Write it with
   `write_manifest`. Attach the manifest path to the summary.
6. **Emit summary.** Print the `IngestSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Processed JSONL | `{workspace}/data/processed/{slug}_reference_phases.jsonl` |
| Stage manifest | `{workspace}/data/manifests/{slug}_ingest_manifest.json` |

### Return type

`IngestSummary` (JSON to stdout).

---

## 2. `mdisc export-zomic`

Compile a Zomic-authored design into an orbit-library JSON prototype.

### CLI syntax

```
mdisc export-zomic --design PATH [--out PATH] [--force]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--design` | PATH | Yes | -- | Path to the Zomic design YAML (`ZomicDesignConfig`) |
| `--out` | PATH | No | Value of `export_path` in the design YAML, or `data/prototypes/generated/{prototype_key}.json` | Override for the orbit-library JSON output |
| `--force` | FLAG | No | `False` | Force raw export and orbit-library regeneration even if cached artifacts are newer than the design and `.zomic` source |

### Internal steps

1. **Load design YAML.** Parse the YAML file at `--design` into `ZomicDesignConfig`.
2. **Resolve source paths.** Resolve `zomic_file`, `raw_export_path`, and orbit-library output path.
3. **Run vZome export when stale.** Invoke `./gradlew -q :core:zomicExport -PzomicFile=... -PzomicOut=...` if the raw export is missing or older than the design inputs.
4. **Convert labeled points to orbits.** Group labeled VM locations by label prefix (`orbit.site` -> `orbit`, `orbit_01` -> `orbit`), embed them into the specified cell, and write the orbit-library JSON.
5. **Emit summary.** Print the `ZomicExportSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Raw labeled geometry | Design `raw_export_path` or `{workspace}/data/prototypes/generated/{prototype_key}.raw.json` |
| Orbit-library prototype | Design `export_path` or `{workspace}/data/prototypes/generated/{prototype_key}.json` |

### Return type

`ZomicExportSummary` (JSON to stdout).

---

## 3. `mdisc generate`

Generate deterministic candidate structures into JSONL.

### CLI syntax

```
mdisc generate --config PATH --count INT [--seed INT] [--out PATH]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |
| `--count` | INT | Yes (min=1) | -- | Number of candidates to generate |
| `--seed` | INT | No | `None` | Random seed for reproducible generation |
| `--out` | PATH | No | `data/candidates/{slug}_candidates.jsonl` | Output path for the candidates JSONL |

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig` from the YAML file.
2. **Resolve the template source.** If the config sets `zomic_design`, export or
   refresh the design-derived orbit library first. If the config sets
   `prototype_library`, load that override directly. Otherwise fall back to the
   anchored or generic template resolution path.
3. **Generate candidates.** Call `generate_candidates(system_config, out_path,
   count=count, seed=seed, config_path=config)`. This writes candidates to the
   output path and returns a `GenerateSummary`.
4. **Compute generation metrics.** Reload the written JSONL and count unique
   `candidate_id` values. Call `generation_metrics(requested_count,
   generated_count, invalid_filtered_count, unique_count)` to compute the
   deduplication rate and attach it to the summary as `qa_metrics`.
5. **Write calibration.** Serialize the generation metrics dict as JSON to the
   calibration path.
6. **Write manifest.** Build and write a stage manifest with `stage="generate"`,
   recording both the candidates JSONL and calibration JSON as output paths.
7. **Emit summary.** Print the `GenerateSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Candidates JSONL | `{workspace}/data/candidates/{slug}_candidates.jsonl` |
| Generation metrics (calibration) | `{workspace}/data/calibration/{slug}_generation_metrics.json` |
| Stage manifest | `{workspace}/data/manifests/{slug}_generate_manifest.json` |

### Return type

`GenerateSummary` (JSON to stdout).

---

## 4. `mdisc screen`

Run fast screening: proxy relaxation, threshold filtering, and shortlist
ranking.

### CLI syntax

```
mdisc screen --config PATH
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Candidates JSONL | `{workspace}/data/candidates/{slug}_candidates.jsonl` | `mdisc generate` |

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig`.
2. **Locate input.** Resolve the candidates JSONL path from the slug. Raise
   `FileNotFoundError` if it does not exist.
3. **Parse candidates.** Load every row and validate as `CandidateRecord`.
4. **Fast relaxation.** Call `run_fast_relaxation(system_config, candidates)` to
   compute proxy energy and distance values for each candidate.
5. **Determine thresholds.** Threshold selection depends on the backend mode:
   - **Mock mode** (`mode != "real"`): Use fixed defaults --
     `min_distance_proxy = 0.55`, `max_energy_proxy = -2.65`.
   - **Real mode** (`mode == "real"`): Compute adaptive thresholds from the
     relaxed population -- `max_energy` is the 65th percentile of
     `energy_proxy_ev_per_atom` values; `min_distance` is the 30th percentile
     of `min_distance_proxy` values.
6. **Apply thresholds.** Call `apply_screen_thresholds(relaxed,
   min_distance_proxy, max_energy_proxy)` to partition candidates into passing
   and failing sets.
7. **Rank shortlist.** Call `rank_screen_shortlist(passing)` to assign
   `shortlist_rank` values.
8. **Write output.** Serialize the shortlisted candidates to the screened JSONL
   path.
9. **Write calibration.** Call `screening_calibration(...)` and write the
   resulting dict as JSON. The calibration records input count, relaxed count,
   passed count, shortlisted count, and the threshold values used.
10. **Write manifest.** Build and write a stage manifest with `stage="screen"`.
11. **Emit summary.** Print the `ScreenSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Screened JSONL | `{workspace}/data/screened/{slug}_screened.jsonl` |
| Screen calibration | `{workspace}/data/calibration/{slug}_screen_calibration.json` |
| Stage manifest | `{workspace}/data/manifests/{slug}_screen_manifest.json` |

### Return type

`ScreenSummary` (JSON to stdout).

---

## 5. `mdisc hifi-validate`

Run high-fidelity digital validation on shortlisted candidates using committee
models, phonon checks, MD stability, and XRD signature validation.

### CLI syntax

```
mdisc hifi-validate --config PATH --batch BATCH
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |
| `--batch` | STR | Yes | -- | Batch selector: `"all"` for every candidate, or `"topN"` (e.g. `top500`) for the first N by shortlist rank |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Screened JSONL | `{workspace}/data/screened/{slug}_screened.jsonl` | `mdisc screen` |

### Batch selection

The `_select_hifi_batch` helper sorts candidates by `(shortlist_rank,
candidate_id)` and then selects based on the `--batch` value:

- `all` -- select every candidate.
- `topN` (e.g. `top500`) -- select the first N candidates. N must be >= 1.

Any other value raises `ValueError`.

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig`.
2. **Locate input.** Resolve the screened JSONL path. Raise
   `FileNotFoundError` if missing.
3. **Parse and select candidates.** Validate all rows as `CandidateRecord`,
   then call `_select_hifi_batch(candidates, batch)` to apply the batch
   selector.
4. **Committee relaxation.** Call `run_committee_relaxation(system_config,
   selected, batch)` to relax structures using committee MLIP models.
5. **Uncertainty estimation.** Call `compute_committee_uncertainty(validated)`
   to compute per-atom energy uncertainty from the committee disagreement.
6. **Proxy hull.** Call `compute_proxy_hull(validated, config=system_config)` to
   evaluate distance to the convex hull.
7. **Phonon checks.** Call `run_mlip_phonon_checks(validated,
   config=system_config)` to verify dynamical stability.
8. **MD stability.** Call `run_short_md_stability(validated,
   config=system_config)` to run short molecular dynamics and check structural
   integrity.
9. **XRD validation.** Call `validate_xrd_signatures(system_config, validated)`
   to compare simulated XRD patterns against reference data.
10. **Finalize validation.** Call `_finalize_validation(validated)`. A
    candidate passes if **all** of the following are true:
    - `uncertainty_ev_per_atom <= 0.04`
    - `delta_e_proxy_hull_ev_per_atom <= 0.08`
    - `phonon_pass is True`
    - `md_pass is True`
    - `xrd_pass is True`

    Each candidate receives `passed_checks` (bool) and `status` (`"passed"` or
    `"failed"`).
11. **Write output.** Serialize validated candidates to the output JSONL.
12. **Write calibration.** Call `validation_calibration(validated)` and write as
    JSON.
13. **Write manifest.** Build and write a stage manifest with
    `stage="hifi_validate"`.
14. **Emit summary.** Print the `HifiValidateSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Validated JSONL | `{workspace}/data/hifi_validated/{slug}_{batch_slug}_validated.jsonl` |
| Validation calibration | `{workspace}/data/calibration/{slug}_{batch_slug}_validation_calibration.json` |
| Stage manifest | `{workspace}/data/manifests/{slug}_{batch_slug}_hifi_validate_manifest.json` |

### Return type

`HifiValidateSummary` (JSON to stdout).

---

## 6. `mdisc hifi-rank`

Rank validated candidates with deterministic, uncertainty-aware scoring.

### CLI syntax

```
mdisc hifi-rank --config PATH
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| All validated JSONL files | `{workspace}/data/hifi_validated/{slug}_*_validated.jsonl` | `mdisc hifi-validate` (one or more batches) |

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig`.
2. **Load validated candidates.** Call `_load_validated_candidates(system_slug)`.
   This globs all matching `{slug}_*_validated.jsonl` files in the
   `hifi_validated` directory, loads them in sorted path order, and deduplicates
   by `candidate_id` (first occurrence wins).
3. **Rank.** Call `rank_validated_candidates(system_config, validated)` to
   produce the final ranked ordering.
4. **Write output.** Serialize ranked candidates to the ranked JSONL path.
5. **Write calibration.** Call `ranking_calibration(ranked)` and write as JSON.
6. **Write manifest.** Build and write a stage manifest with
   `stage="hifi_rank"`.
7. **Emit summary.** Print the `HifiRankSummary` as JSON to stdout. The
   `passed_count` field counts candidates where
   `digital_validation.passed_checks is True`.

### Artifacts

| Artifact | Default path |
|---|---|
| Ranked JSONL | `{workspace}/data/ranked/{slug}_ranked.jsonl` |
| Ranking calibration | `{workspace}/data/calibration/{slug}_ranking_calibration.json` |
| Stage manifest | `{workspace}/data/manifests/{slug}_hifi_rank_manifest.json` |

### Return type

`HifiRankSummary` (JSON to stdout).

---

## 7. `mdisc active-learn`

Train a surrogate model on validated candidates and propose the next batch of
candidates for high-fidelity validation.

### CLI syntax

```
mdisc active-learn --config PATH
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Candidates JSONL (pool) | `{workspace}/data/candidates/{slug}_candidates.jsonl` | `mdisc generate` |
| Validated JSONL files | `{workspace}/data/hifi_validated/{slug}_*_validated.jsonl` | `mdisc hifi-validate` |
| Ranked JSONL (optional enrichment) | `{workspace}/data/ranked/{slug}_ranked.jsonl` | `mdisc hifi-rank` (optional) |
| Screened JSONL (preferred pool) | `{workspace}/data/screened/{slug}_screened.jsonl` | `mdisc screen` (optional) |

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig`.
2. **Verify candidate pool exists.** Confirm
   `data/candidates/{slug}_candidates.jsonl` exists; raise `FileNotFoundError`
   otherwise.
3. **Load validated candidates.** Call `_load_validated_candidates(system_slug)`
   to load and deduplicate all validated JSONL files.
4. **Enrich with ranking data.** Call
   `_enrich_validated_with_ranked(system_slug, validated)`. If a ranked JSONL
   exists, validated candidates are replaced with their ranked versions (which
   carry additional provenance such as `hifi_rank` scores). If the ranked file
   does not exist, validated candidates are returned unchanged.
5. **Load active learning pool.** Call
   `_load_active_learning_pool(system_slug, validated_ids)`. The pool selection
   prefers the screened JSONL if it exists and contains candidates not yet
   validated; otherwise falls back to the raw candidates JSONL.
6. **Check remaining pool.** Count candidates in the pool whose IDs are not in
   the validated set. Raise `ValueError` if none remain.
7. **Train surrogate model.** Call `train_surrogate_model(system_config,
   validated)` to fit a lightweight surrogate on the validated data. Returns a
   surrogate model object.
8. **Select next batch.** Call `select_next_candidate_batch(system_config,
   candidate_pool, validated_ids, surrogate, batch_size)` where `batch_size` is
   `min(system_config.default_count, remaining)`.
9. **Write surrogate JSON.** Serialize the surrogate model dict to
   `data/active_learning/{slug}_surrogate.json`.
10. **Write next batch JSONL.** Serialize the selected candidates to
    `data/active_learning/{slug}_next_batch.jsonl`.
11. **Write feature store.** For each validated candidate, compute a feature map
    via `candidate_feature_map(system_config, candidate)` and write a feature
    row (including `candidate_id`, `composition`, `features`, uncertainty,
    hull distance, rank scores, and `passed_checks`) to
    `data/registry/features/{slug}_validated_features.jsonl`.
12. **Write model registry entry.** Compute a SHA-256 digest of the surrogate
    JSON and append a registry row (with `model_id`, system name, timestamp,
    training statistics, and the surrogate path) to
    `data/registry/models/{slug}_models.jsonl`.
13. **Write manifest.** Build and write a stage manifest with
    `stage="active_learn"`.
14. **Emit summary.** Print the `ActiveLearnSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Surrogate model JSON | `{workspace}/data/active_learning/{slug}_surrogate.json` |
| Next batch JSONL | `{workspace}/data/active_learning/{slug}_next_batch.jsonl` |
| Feature store JSONL | `{workspace}/data/registry/features/{slug}_validated_features.jsonl` |
| Model registry JSONL | `{workspace}/data/registry/models/{slug}_models.jsonl` |
| Stage manifest | `{workspace}/data/manifests/{slug}_active_learn_manifest.json` |

### Return type

`ActiveLearnSummary` (JSON to stdout).

---

## 8. `mdisc report`

Build an experiment-facing report with ranked candidates and synthetic XRD
signatures.

### CLI syntax

```
mdisc report --config PATH
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Ranked JSONL | `{workspace}/data/ranked/{slug}_ranked.jsonl` | `mdisc hifi-rank` |

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig`.
2. **Load ranked candidates.** Call `_load_ranked_candidates(system_slug)`.
   Raises `FileNotFoundError` if the ranked JSONL does not exist, or
   `ValueError` if it is empty.
3. **Simulate XRD patterns.** Call `simulate_powder_xrd_patterns(ranked)` to
   generate synthetic powder X-ray diffraction patterns for every ranked
   candidate.
4. **Compile report.** Call `compile_experiment_report(system_config, ranked,
   xrd_patterns)` to assemble the final report dict.
5. **Write XRD patterns.** Serialize the XRD pattern list to the XRD JSONL
   path.
6. **Write report.** Serialize the report dict as JSON to the report path.
7. **Write calibration.** Call `report_calibration(report)` and write as JSON.
8. **Write stage manifest.** Build and write a stage manifest with
   `stage="report"`.
9. **Write pipeline manifest.** Build a pipeline-level manifest via
   `build_pipeline_manifest(...)`. This manifest references output paths across
   the entire pipeline (report, XRD patterns, ranked, candidates, screened,
   and the first validated JSONL if one exists). Only paths that exist on disk
   are included.
10. **Emit summary.** Print the `ReportSummary` as JSON to stdout. The summary
    includes `report_fingerprint` (from the report dict) and the pipeline
    manifest path.

### Artifacts

| Artifact | Default path |
|---|---|
| Report JSON | `{workspace}/data/reports/{slug}_report.json` |
| XRD patterns JSONL | `{workspace}/data/reports/{slug}_xrd_patterns.jsonl` |
| Report calibration | `{workspace}/data/calibration/{slug}_report_calibration.json` |
| Stage manifest | `{workspace}/data/manifests/{slug}_report_manifest.json` |
| Pipeline manifest | `{workspace}/data/manifests/{slug}_pipeline_manifest.json` |

### Return type

`ReportSummary` (JSON to stdout).

---

## Error handling

All seven commands share identical error handling. The following exception types
are caught at the top level of each command function:

| Exception | Typical cause |
|---|---|
| `FileNotFoundError` | A required input file or the config file does not exist |
| `ValidationError` | Pydantic validation of `SystemConfig` or `CandidateRecord` failed |
| `ValueError` | An empty dataset, invalid batch selector, or other logic error |

On any of these exceptions:

1. The error message is printed to **stderr** via `typer.echo(..., err=True)`.
2. The process exits with **code 2** via `typer.Exit(code=2)`.

---

---

## 9. `mdisc llm-generate`

Generate candidate structures using an LLM that outputs Zomic scripts conditioned
on composition constraints.

### CLI syntax

```
mdisc llm-generate --config PATH --count INT [--seed-zomic PATH] [--temperature FLOAT] [--model-lane LANE] [--out PATH]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |
| `--count` | INT | Yes (min=1) | -- | Number of candidates to generate |
| `--seed-zomic` | PATH | No | `None` | Optional seed Zomic script to extend or vary |
| `--temperature` | FLOAT | No | `0.7` | LLM sampling temperature |
| `--model-lane` | STR | No | `None` | Optional serving-lane override (`general_purpose` or `specialized_materials`) |
| `--out` | PATH | No | `data/candidates/{slug}_candidates.jsonl` | Output path |

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig`.
2. **Resolve serving lane.** Use the explicit Phase 19 precedence contract:
   CLI `--model-lane` > `llm_generate.default_model_lane` >
   `llm_generate.fallback_model_lane` > backend default tuple.
3. **Resolve LLM backend.** Select the effective adapter/provider/model tuple
   from the resolved lane or backend default.
4. **Run local-serving readiness checks when needed.** For `openai_compat_v1`,
   probe the configured endpoint before generation attempts begin. The local
   server must already be running; `mdisc` does not launch it for you.
5. **Validate optional seed input.** If `--seed-zomic` or
   `llm_generate.seed_zomic` is present, load the seed script and validate it
   once through the compile bridge before any provider call.
6. **Format prompt.** Build a config-driven prompt containing system name,
   template family, composition bounds, and an optional `SEED_ZOMIC` block.
7. **Run bounded retries.** Attempt up to `requested_count * max_attempts`
   generations. Every raw completion is persisted even if provider, parse,
   compile, or conversion fails.
8. **Compile via vZome authority.** For each raw completion, call the Zomic
   bridge and record explicit parse/compile status, error classification, and
   persisted raw-export/orbit-library artifact paths.
9. **Convert valid outputs.** Successful orbit-library outputs are wrapped as
   standard `CandidateRecord` rows with additive LLM provenance fields so
   `mdisc screen` can consume them without a schema fork.
10. **Write run artifacts.** Persist `prompt.json`, `attempts.jsonl`,
   `compile_results.jsonl`, and `run_manifest.json` under
   `data/llm_runs/{slug}_{request_hash}/`. The run manifest now records nested
   `serving_identity` in addition to the legacy flat adapter/provider/model
   fields.
11. **Write calibration.** Record attempt count, parse pass rate, compile pass
   rate, and generation success rate in the calibration JSON.
12. **Write Stage manifest.** Stage manifest with `stage="llm_generate"` hashes
   the candidates JSONL, calibration JSON, and run manifest.
13. **Emit summary.** Print `LlmGenerateSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| LLM candidates JSONL | `{workspace}/data/candidates/{slug}_candidates.jsonl` |
| LLM generation metrics | `{workspace}/data/calibration/{slug}_llm_generation_metrics.json` |
| Stage manifest | `{workspace}/data/manifests/{slug}_llm_generate_manifest.json` |
| Run manifest | `{workspace}/data/llm_runs/{slug}_{request_hash}/run_manifest.json` |

### Return type

`LlmGenerateSummary` (JSON to stdout).

---

## 10. `mdisc llm-evaluate`

Enrich ranked candidates with LLM-powered assessment: synthesizability scoring,
precursor suggestions, anomaly detection, and short literature-style context.

### CLI syntax

```
mdisc llm-evaluate --config PATH [--batch BATCH] [--model-lane LANE] [--out PATH]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |
| `--batch` | STR | No | `"all"` | Batch selector (same semantics as `hifi-validate`) |
| `--model-lane` | STR | No | `None` | Optional evaluation-lane override (`general_purpose` or `specialized_materials`) |
| `--out` | PATH | No | computed | Output JSONL override |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Ranked JSONL | `{workspace}/data/ranked/{slug}_ranked.jsonl` | `mdisc hifi-rank` |

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig`.
2. **Load ranked candidates.** Read the ranked JSONL and optionally select `all` or `topN`.
3. **Resolve evaluation lane.** Use the explicit precedence contract:
   CLI `--model-lane` > `llm_evaluate.model_lane` > shared `llm_generate`
   lane defaults/fallbacks > backend default tuple.
4. **Resolve LLM backend.** Select the adapter/provider/model tuple from the
   resolved lane. Evaluation reuses the same `llm_generate.model_lanes`
   registry; it does not maintain a second lane registry.
5. **Run local-serving readiness checks when needed.** For `openai_compat_v1`,
   probe the configured endpoint before assessment begins. The endpoint must
   already be running.
6. **For each candidate:**
   a. Serialize structure, composition, and validation results as a structured prompt.
   b. When the resolved lane is `specialized_materials`, switch to the thinner
      Phase 20 specialist payload seam instead of sending the same generic
      prompt shape.
   c. LLM assesses synthesizability (inspired by CSLLM: can this be made in a lab?).
   d. LLM suggests chemical precursors for synthesis.
   e. LLM checks for anomalies (inconsistent validation results, unusual compositions).
   f. LLM provides literature context (does this match known QC families?).
7. **Attach assessments.** Add `llm_assessment` to each `CandidateRecord`,
   including additive requested/resolved lane identity plus typed
   `serving_identity`.
8. **Write output.** Serialize enriched candidates to output JSONL.
9. **Persist audit artifacts.** Write `requests.jsonl`, `assessments.jsonl`, raw responses,
   and `run_manifest.json` under `data/llm_evaluations/`.
10. **Write calibration.** Record assessed/failed counts and success rate.
11. **Write manifest.** Stage manifest with `stage="llm_evaluate"`.
12. **Emit summary.** Print `LlmEvaluateSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| LLM-evaluated JSONL | `{workspace}/data/llm_evaluated/{slug}_{batch_slug}_llm_evaluated.jsonl` |
| Evaluation requests | `{workspace}/data/llm_evaluations/{run_id}/requests.jsonl` |
| Evaluation assessments | `{workspace}/data/llm_evaluations/{run_id}/assessments.jsonl` |
| Evaluation run manifest | `{workspace}/data/llm_evaluations/{run_id}/run_manifest.json` |
| LLM evaluation metrics | `{workspace}/data/calibration/{slug}_{batch_slug}_llm_evaluation_metrics.json` |
| Stage manifest | `{workspace}/data/manifests/{slug}_{batch_slug}_llm_evaluate_manifest.json` |

### Return type

`LlmEvaluateSummary` (JSON to stdout).

### Compatibility notes

- Generation and evaluation may intentionally use different lanes in the same
  config. Phase 20 uses this to keep generation on `general_purpose` while
  routing `llm-evaluate` through `specialized_materials`.
- Compare and report keep the existing artifact roots, but they now surface
  additive generation-lane and evaluation-lane lineage separately when
  `llm_assessment` provenance is present.

---

## 11. `mdisc llm-suggest`

Emit dry-run next-step proposal bundles from a typed acceptance pack.

### CLI syntax

```
mdisc llm-suggest --acceptance-pack PATH [--out PATH]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--acceptance-pack` | PATH | Yes | -- | Path to the typed acceptance pack JSON |
| `--out` | PATH | No | sibling file | Output JSON override for the dry-run suggestions |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Acceptance pack JSON | `{workspace}/data/benchmarks/llm_acceptance/{pack_id}/acceptance_pack.json` | `./scripts/run_llm_acceptance_benchmarks.sh` |

### Internal steps

1. **Load acceptance pack.** Parse the typed per-system benchmark summary.
2. **Assess weak spots.** Check validity, generation success, shortlist/validation pass-through, synthesizability, and release-gate readiness.
3. **Emit dry-run suggestions.** Produce typed system-scoped campaign proposals for the next model-improvement pass without launching a search loop.
4. **Write suggestion artifact.** Persist the suggestion bundle JSON plus sibling `proposals/{proposal_id}.json` artifacts next to the acceptance pack by default.
5. **Emit summary.** Print the typed `LlmCampaignSuggestion` JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Acceptance pack | `{workspace}/data/benchmarks/llm_acceptance/{pack_id}/acceptance_pack.json` |
| Suggestion JSON | `{workspace}/data/benchmarks/llm_acceptance/{pack_id}/suggestions.json` |
| Proposal JSON | `{workspace}/data/benchmarks/llm_acceptance/{pack_id}/proposals/{proposal_id}.json` |

### Return type

`LlmCampaignSuggestion` (JSON to stdout).

---

## 12. `mdisc llm-approve`

Write an explicit approval artifact for a typed proposal and, when approved,
materialize a self-contained campaign spec without launching generation.

### CLI syntax

```
mdisc llm-approve --proposal PATH --decision approved|rejected --operator TEXT [--config PATH] [--notes TEXT]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--proposal` | PATH | Yes | -- | Path to a typed campaign proposal JSON |
| `--decision` | STR | Yes | -- | `approved` or `rejected` |
| `--operator` | STR | Yes | -- | Operator identity recorded on the approval artifact |
| `--config` | PATH | Approved only | `None` | Required for approved proposals so the campaign spec can pin a launch baseline |
| `--notes` | STR | No | `None` | Optional approval notes |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Proposal JSON | `{workspace}/data/benchmarks/llm_acceptance/{pack_id}/proposals/{proposal_id}.json` | `mdisc llm-suggest` |
| System config YAML | user-selected | Required only for `approved` decisions |

### Internal steps

1. **Load proposal.** Parse the typed `LlmCampaignProposal` artifact.
2. **Create approval artifact.** Build a separate `LlmCampaignApproval` with a deterministic approval ID.
3. **Write approval JSON.** Persist the approval artifact under `approvals/{approval_id}.json` next to the acceptance-pack root.
4. **Materialize campaign spec when approved.** Load `SystemConfig`, hash it, pin the launch baseline, and write `campaign_spec.json` under `data/llm_campaigns/{campaign_id}/`.
5. **Stop at governance artifacts.** Do not call `llm-generate`, `llm-evaluate`, or any downstream pipeline stage.
6. **Emit summary.** Print a small JSON object containing the approval path and optional campaign-spec path.

### Artifacts

| Artifact | Default path |
|---|---|
| Approval JSON | `{workspace}/data/benchmarks/llm_acceptance/{pack_id}/approvals/{approval_id}.json` |
| Campaign spec JSON | `{workspace}/data/llm_campaigns/{campaign_id}/campaign_spec.json` |

### Return type

JSON summary with `proposal_id`, `decision`, `approval_id`, `approval_path`, optional `campaign_id`, and optional `campaign_spec_path`.

---

## 13. `mdisc llm-launch`

Launch an approved campaign spec through the existing `llm-generate` runtime.

### CLI syntax

```
mdisc llm-launch --campaign-spec PATH [--out PATH]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--campaign-spec` | PATH | Yes | -- | Path to a typed campaign spec JSON created by `mdisc llm-approve` |
| `--out` | PATH | No | `{workspace}/data/candidates/{slug}_candidates.jsonl` | Optional override for the launched candidate JSONL |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Campaign spec JSON | `{workspace}/data/llm_campaigns/{campaign_id}/campaign_spec.json` | `mdisc llm-approve --decision approved --config ...` |
| System config YAML | pinned inside the campaign spec | must still match the stored config hash |

### Internal steps

1. **Load campaign spec.** Parse the typed `LlmCampaignSpec`.
2. **Load pinned config.** Resolve `launch_baseline.system_config_path`, load `SystemConfig`, and recompute its hash.
3. **Reject config drift before execution.** If the current hash differs from the pinned hash, exit with code 2 and an operator-facing message that includes the config path, the pinned hash, the current hash, and re-approval guidance.
4. **Create launch wrapper.** Allocate a new `launch_id`, print it immediately to stderr, and resolve the launch artifact directory under `data/llm_campaigns/{campaign_id}/launches/{launch_id}/`.
5. **Resolve additive overlay.** Call `resolve_campaign_launch(...)` to derive prompt deltas, lane selection, composition-window changes, seed handling, and the resolved provider/model lane without mutating the source YAML.
6. **Run readiness checks when needed.** If the resolved launch uses
   `openai_compat_v1`, probe the endpoint before generation attempts begin.
   Local-serving failures name the lane and endpoint; they do not start the
   server for you.
7. **Write `resolved_launch.json`.** Persist the resolved overlay before any provider call begins.
8. **Launch through the existing runtime.** Call `generate_llm_candidates(...)` with the copied config, the resolved additive prompt/campaign metadata, the resolved serving identity, and the requested candidate count from the campaign spec.
9. **Write standard stage artifacts.** Persist the standard candidate JSONL, calibration JSON, `llm_generate` stage manifest, and the run-level artifacts already produced by `llm-generate`.
10. **Write `launch_summary.json`.** Record success or failure in the launch wrapper summary and print the typed `LlmCampaignLaunchSummary` JSON to stdout on success.
11. **Preserve partial artifacts on failure.** If launch fails after wrapper creation, keep any partial outputs and still write a failed launch summary. Phase 11 does not implement `--resume`.

### Artifacts

| Artifact | Default path |
|---|---|
| Campaign spec JSON | `{workspace}/data/llm_campaigns/{campaign_id}/campaign_spec.json` |
| Resolved launch JSON | `{workspace}/data/llm_campaigns/{campaign_id}/launches/{launch_id}/resolved_launch.json` |
| Launch summary JSON | `{workspace}/data/llm_campaigns/{campaign_id}/launches/{launch_id}/launch_summary.json` |
| Candidates JSONL | `{workspace}/data/candidates/{slug}_candidates.jsonl` unless `--out` is supplied |
| LLM generation metrics | `{workspace}/data/calibration/{slug}_llm_generation_metrics.json` |
| LLM generate stage manifest | `{workspace}/data/manifests/{slug}_llm_generate_manifest.json` |
| LLM run artifacts | `{workspace}/data/llm_runs/{run_id}/...` |

### Return type

`LlmCampaignLaunchSummary` (JSON to stdout).

### Manual downstream continuation

Phase 11 keeps downstream execution operator-driven. After `llm-launch`
succeeds, continue with the standard commands:

```
mdisc screen --config PATH
mdisc hifi-validate --config PATH --batch all
mdisc hifi-rank --config PATH
mdisc report --config PATH
```

Those later stages read the standard JSONL artifacts and preserve additive
campaign lineage in their manifests rather than requiring a campaign-specific
execution mode.

### Lineage Audit

To trace a downstream result back to the governing campaign:
1. inspect a downstream stage manifest or pipeline manifest for `source_lineage.llm_campaign`
2. open the referenced `launch_summary.json`
3. follow `resolved_launch_path` and `campaign_spec_path`
4. inspect the approval and acceptance-pack paths referenced by the campaign spec

This audit path is additive: non-campaign runs continue to emit manifests with
`source_lineage = null`.

---

## 14. `mdisc llm-replay`

Strictly replay a recorded launch bundle through the existing `llm-generate`
runtime.

### CLI syntax

```
mdisc llm-replay --launch-summary PATH
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--launch-summary` | PATH | Yes | -- | Path to an existing `launch_summary.json` from `mdisc llm-launch` or a previous replay |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Launch summary JSON | `{workspace}/data/llm_campaigns/{campaign_id}/launches/{launch_id}/launch_summary.json` | `mdisc llm-launch` or a prior `mdisc llm-replay` |
| Resolved launch JSON | referenced by the launch summary | must still exist and agree with the launch summary |
| Run manifest JSON | referenced by the launch summary | must still exist and agree with the launch summary |
| Prompt JSON | referenced by the run manifest | must still exist and contain the original request |

### Internal steps

1. **Load the recorded launch bundle.** Read `launch_summary.json`, `resolved_launch.json`, `run_manifest.json`, and `prompt.json` as a single replay authority.
2. **Load current config.** Resolve `system_config_path` from the recorded launch, load `SystemConfig`, and compute the current config hash.
3. **Rebuild the effective replay config.** Reapply the recorded adapter/provider/model, prompt template, resolved composition bounds, seed path, conditioning-example cap, and request count without mutating the source YAML.
   Phase 19 makes this replay-safe for richer local-serving identity: model and
   checkpoint drift fail clearly, while endpoint/path drift is treated
   separately.
4. **Allocate a fresh launch wrapper.** Create a new `launch_id` and a new launch directory under `data/llm_campaigns/{campaign_id}/launches/{launch_id}/`.
5. **Write `resolved_launch.json`.** Persist the strict replay wrapper, including `replay_of_launch_id`, `replay_of_launch_summary_path`, and the current config hash.
6. **Launch through the existing runtime.** Call `generate_llm_candidates(...)` with the rebuilt config, replay metadata, and the resolved replay serving identity so new artifacts do not lose local lane details.
7. **Write standard stage artifacts.** Persist the normal candidate JSONL, `llm_generate` stage manifest, and run-level artifacts.
8. **Write `launch_summary.json`.** Record the replay result and point back to the source launch.
9. **Preserve partial artifacts on failure.** Failed replays still write a failed launch summary; Phase 12 does not implement replay overrides or `--resume`.

### Artifacts

| Artifact | Default path |
|---|---|
| Replay resolved launch JSON | `{workspace}/data/llm_campaigns/{campaign_id}/launches/{launch_id}/resolved_launch.json` |
| Replay launch summary JSON | `{workspace}/data/llm_campaigns/{campaign_id}/launches/{launch_id}/launch_summary.json` |
| Replay candidates JSONL | `{workspace}/data/candidates/{slug}_replay_{launch_id}.jsonl` |
| Replay `llm_generate` manifest | `{workspace}/data/manifests/{slug}_llm_generate_manifest.json` |
| Replay run artifacts | `{workspace}/data/llm_runs/{run_id}/...` |

### Return type

`LlmCampaignLaunchSummary` (JSON to stdout).

### Strict replay contract

Phase 12 replay is intentionally strict:
- the recorded launch bundle is the authority
- the current config hash is recorded for auditability
- there are no behavioral override flags
- family-based launches keep replaying the recorded checkpoint identity even if
  that checkpoint family later promotes a different member
- missing or inconsistent launch-bundle files are surfaced as operator-facing failures

---

## 15. `mdisc llm-compare`

Compare a launch or replay against its acceptance-pack baseline and, when
available, the most recent prior launch for the same campaign/system.

### CLI syntax

```
mdisc llm-compare --launch-summary PATH
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--launch-summary` | PATH | Yes | -- | Path to the launch summary whose outcome should be compared |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Launch summary JSON | `{workspace}/data/llm_campaigns/{campaign_id}/launches/{launch_id}/launch_summary.json` | `mdisc llm-launch` or `mdisc llm-replay` |
| Acceptance pack JSON | referenced by the campaign spec | must contain metrics for the launch system |
| Prior launch summary | discovered automatically under the same campaign | optional; used only when an older launch exists |

### Internal steps

1. **Load the target launch bundle.** Resolve the same strict launch bundle used by replay.
2. **Build or reuse `outcome_snapshot.json`.** Freeze the current launch metrics into an immutable typed snapshot.
3. **Load the acceptance baseline.** Always compare against the originating acceptance-pack metrics for the same system.
4. **Find a prior launch baseline when available.** Reuse the most recent earlier launch for the same campaign/system and its outcome snapshot.
5. **Compute deltas.** Produce `delta_vs_acceptance` and `delta_vs_prior` only for metrics that exist on both sides.
6. **Report missing metrics explicitly.** Keep unavailable downstream metrics in `missing_metrics`; do not coerce them to zero.
7. **Write the comparison artifact.** Persist the typed comparison JSON under the campaign root and print concise summary lines to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Outcome snapshot JSON | `{workspace}/data/llm_campaigns/{campaign_id}/launches/{launch_id}/outcome_snapshot.json` |
| Comparison JSON | `{workspace}/data/llm_campaigns/{campaign_id}/comparisons/comparison_{launch_id}.json` |

### Return type

Human-readable summary lines to stdout plus explicit `Outcome snapshot:` and
`Comparison artifact:` paths.

### Baseline rules

- The acceptance-pack baseline is always included.
- The prior-launch baseline is included only when a previous launch for the same campaign/system exists.
- Missing downstream metrics remain explicit in `missing_metrics` and summary lines.

---

## 16. `mdisc llm-register-checkpoint`

Register a Zomic-adapted local checkpoint as a file-backed serving artifact.

### CLI syntax

```
mdisc llm-register-checkpoint --spec PATH
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--spec` | PATH | Yes | -- | Path to the typed checkpoint registration YAML |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Registration spec YAML | e.g. `configs/llm/al_cu_fe_zomic_adapted_checkpoint.yaml` | must describe one adapted checkpoint |
| Adaptation artifact | referenced by the spec | must exist |
| Corpus manifest | referenced by the spec | must exist |
| Eval-set manifest | referenced by the spec | must exist |
| Acceptance pack JSON | referenced by the spec when provided | optional, but if present it must exist |

### Internal steps

1. **Load the typed spec.** Validate the checkpoint registration payload and normalize relative paths against the spec location.
2. **Verify lineage inputs exist.** Fail early if the adaptation artifact, corpus manifest, eval-set manifest, or optional acceptance pack is missing.
3. **Normalize storage paths.** Persist workspace-relative lineage paths when the artifacts live under the repository workspace.
4. **Build the checkpoint fingerprint.** Hash the pinned serving and lineage identity so replay and later runs can detect true checkpoint drift.
5. **Write `registration.json`.** Persist the typed registration artifact under `data/llm_checkpoints/{checkpoint_id}/`.
6. **Protect the checkpoint id.** If the same `checkpoint_id` already exists with a different fingerprint, fail instead of overwriting the existing registration.

### Artifacts

| Artifact | Default path |
|---|---|
| Checkpoint registration JSON | `{workspace}/data/llm_checkpoints/{checkpoint_id}/registration.json` |

### Return type

`LlmCheckpointRegistrationSummary` (JSON to stdout).

### Failure rules

- A strict adapted lane with `require_checkpoint_registration: true` may not run without this registration artifact.
- Registration fails on missing lineage inputs, adapter/provider/model mismatch, or fingerprint conflict for an already registered `checkpoint_id`.

---

## 17. `mdisc llm-serving-benchmark`

Smoke-test and compare hosted, local, specialized, or checkpoint-lifecycle
serving targets under one shared benchmark context.

### CLI syntax

```
mdisc llm-serving-benchmark --spec PATH [--smoke-only] [--out PATH]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--spec` | PATH | Yes | -- | Path to the typed serving benchmark YAML |
| `--smoke-only` | FLAG | No | `False` | Run only the readiness/smoke phase and stop after writing the smoke artifact |
| `--out` | PATH | No | computed | Optional override for the final benchmark summary JSON |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Benchmark spec YAML | e.g. `configs/llm/al_cu_fe_serving_benchmark.yaml` | committed operator spec or operator-authored equivalent |
| Acceptance pack JSON | referenced by the spec | must exist and match the benchmark system |
| Campaign spec JSON | referenced by each `campaign_launch` target | produced earlier by `mdisc llm-approve` |

### Internal steps

1. **Load the benchmark spec.** Validate the typed spec and reject mixed-system targets against the shared acceptance-pack context.
2. **Run smoke checks first.** Probe every requested serving target and record a typed smoke artifact before any benchmark execution begins.
3. **Stop on strict smoke failures.** If any target fails readiness or resolves through a disallowed fallback lane, exit with code 2 instead of silently benchmarking the wrong lane.
4. **Honor role-specific execution paths.**
   a. `campaign_launch` targets reuse the shipped launch/generate/compare flow.
   b. `llm_evaluate` targets reuse `mdisc llm-evaluate` core behavior with an acceptance-pack-aligned batch such as `top1`.
5. **Keep role-specific metrics honest.** Launch targets and evaluation targets only report the quality metrics they actually observed; missing role-specific metrics remain explicit.
6. **Emit role-aware lifecycle guidance when requested.** If `campaign_launch`
   targets declare `checkpoint_benchmark_role`, the summary can recommend
   whether to promote a candidate checkpoint, keep the current promoted
   default, and which target remains the rollback baseline.
7. **Write benchmark artifacts.** Persist smoke checks and the final benchmark summary under `data/benchmarks/llm_serving/{benchmark_id}/...`.
8. **Emit operator guidance.** Print concise recommendation lines plus the final benchmark summary path.

### Artifacts

| Artifact | Default path |
|---|---|
| Smoke artifact JSON | `{workspace}/data/benchmarks/llm_serving/{benchmark_id}/smoke_checks.json` |
| Benchmark summary JSON | `{workspace}/data/benchmarks/llm_serving/{benchmark_id}/benchmark_summary.json` |

### Return type

Human-readable smoke or recommendation lines to stdout plus explicit artifact
paths.

### Fairness and failure rules

- Every target in the benchmark spec must match the shared acceptance-pack system.
- Evaluation targets must keep their `batch` aligned with that same context.
- `checkpoint_benchmark_role` is reserved for `campaign_launch` targets; it is
  how checkpoint lifecycle benchmarks declare baseline, promoted-default, and
  candidate roles explicitly.
- Smoke failure stops the benchmark unless the target explicitly allows fallback.
- No silent fallback is allowed during benchmark comparison.

---

## 18. `mdisc llm-translate`

Export candidate JSONL rows into deterministic translation bundles for external
crystal-oriented workflows.

### CLI syntax

```
mdisc llm-translate --config PATH --input PATH --target cif|material_string --export-id TEXT
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--config` | PATH | Yes | -- | Path to the YAML system configuration file |
| `--input` | PATH | Yes | -- | Explicit candidate JSONL to translate; the command does not infer this path |
| `--target` | STR | Yes | -- | Translation target family (`cif` or `material_string`) |
| `--export-id` | STR | Yes | -- | Stable bundle identifier used in output paths |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Candidate JSONL | operator-selected, e.g. `{workspace}/data/ranked/{slug}_ranked.jsonl` | any prior stage that produced `CandidateRecord` rows |
| System config YAML | operator-selected | used for system slug, benchmark context, and stage-manifest hashing |

### Internal steps

1. **Load configuration.** Parse and validate `SystemConfig`.
2. **Require an explicit input file.** Refuse to guess the candidate JSONL path; missing input exits with code 2.
3. **Load candidates.** Read the JSONL at `--input` and validate every row as `CandidateRecord`.
4. **Recover additive lineage.** Merge any `llm_campaign` lineage already present on the candidates with the current `llm_generate` stage manifest when available.
5. **Recover benchmark context.** Read the ingest manifest when present and build the benchmark-context block carried into the new translation artifacts.
6. **Write the translation bundle.** Resolve the target family, emit raw payload files, and write `inventory.jsonl` plus `manifest.json` under `data/llm_translation_exports/{export_id}/`.
7. **Write the standard stage manifest.** Persist a normal `llm_translate` manifest under `data/manifests/` so the export stays visible to later provenance tooling.
8. **Emit summary.** Print `TranslationExportSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Bundle manifest | `{workspace}/data/llm_translation_exports/{export_id}/manifest.json` |
| Bundle inventory | `{workspace}/data/llm_translation_exports/{export_id}/inventory.jsonl` |
| Raw payload directory | `{workspace}/data/llm_translation_exports/{export_id}/payloads/` |
| Stage manifest | `{workspace}/data/manifests/{slug}_{export_id}_llm_translate_manifest.json` |

### Return type

`TranslationExportSummary` (JSON to stdout).

### Fidelity notes

- `cif` and `material_string` are interoperability views, not new sources of truth.
- Periodic-safe candidates may export as `exact` or `anchored`.
- Mixed-origin periodic proxies may export as `approximate`.
- QC-native candidates forced into either target remain explicitly `lossy`; later operator guidance should still treat the original candidate JSONL and Zomic-derived structure as authoritative.

---

## 19. `mdisc llm-translate-inspect`

Print a human-readable summary of an existing translation bundle and, when
requested, one candidate's payload trace.

### CLI syntax

```
mdisc llm-translate-inspect --manifest PATH [--candidate-id TEXT]
```

### Arguments

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `--manifest` | PATH | Yes | -- | Path to a translation bundle `manifest.json` |
| `--candidate-id` | STR | No | `None` | Optional filter that narrows output to one translated candidate |

### Inputs

| Input | Path | Prerequisite |
|---|---|---|
| Bundle manifest JSON | `{workspace}/data/llm_translation_exports/{export_id}/manifest.json` | `mdisc llm-translate` |
| Bundle inventory JSONL | path referenced by the bundle manifest | must still exist and match the manifest |

### Internal steps

1. **Load the bundle manifest.** Parse `TranslationBundleManifest` from the supplied path.
2. **Load the inventory rows.** Read and validate `TranslationInventoryRow` objects from the manifest-linked inventory JSONL.
3. **Filter optionally.** If `--candidate-id` is present, keep only matching rows and fail clearly when the ID is absent.
4. **Print a concise summary.** Emit export ID, target, source input path, candidate count, lossy count, and stage manifest path when present.
5. **Print per-candidate trace lines.** Show fidelity tier, raw payload path, loss reasons, and diagnostic codes for each selected row.

### Artifacts

This command is read-only. It does not write new files.

### Return type

Human-readable summary lines to stdout.

### Failure rules

- Missing manifest path exits with code 2.
- Invalid manifest or inventory JSON exits with code 2.
- Unknown `--candidate-id` exits with code 2 instead of silently printing an empty report.

---

## Pipeline data flow

The commands are designed to run in sequence. Each stage reads the output of a
prior stage and writes its own artifacts. The canonical ordering is:

```
                                  llm-generate (Zomic via LLM)
                                       |
ingest --> generate ------+            |
                          |            |
                          v            v
                    screen (merges all candidates)
                          |
                          v
                    hifi-validate --> llm-evaluate (enrichment)
                          |                |
                          v                v
                    hifi-rank <--- (optional merge)
                          |
                          v
                    active-learn / llm-suggest
                          |
                          v
                       report
```

The `active-learn` command forms a feedback loop: it reads validated candidates,
trains a surrogate, selects the next batch, and the user runs `hifi-validate`
again on that batch before re-ranking and re-reporting.

The implemented `llm-generate` command provides an alternative candidate source
alongside `generate`. Both produce CandidateRecord JSONL that feeds into
`screen`. The implemented `llm-evaluate` command enriches ranked candidates with
synthesizability and precursor information before reporting, and `report`
prefers the additive `*_all_llm_evaluated.jsonl` artifact when it exists. The
implemented `llm-suggest` command now reads typed acceptance packs and emits
dry-run proposal bundles, `llm-approve` materializes separate approval
artifacts and self-contained campaign specs, `llm-launch` executes those
approved specs through the existing `llm-generate` runtime, `llm-replay`
strictly reruns recorded launch bundles, and `llm-compare` writes immutable
outcome/comparison artifacts while keeping later pipeline stages
manual/operator-driven. Phase 21 adds `llm-serving-benchmark` as an operator
comparison wrapper over those same launch/evaluate surfaces; it does not
replace them with a separate serving-only pipeline. Phase 33 adds
`llm-translate` and `llm-translate-inspect` as an interoperability side branch
for external crystal-oriented consumers; those commands read existing
`CandidateRecord` JSONL but do not replace the main Zomic-first pipeline.
