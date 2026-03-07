# Materials Discovery Pipeline Stages

This document describes each CLI command in the `mdisc` materials discovery
pipeline. Every command is defined in
`materials-discovery/src/materials_discovery/cli.py`. All commands share a
common error-handling pattern: `FileNotFoundError`, `ValidationError`, and
`ValueError` are caught, printed to stderr, and the process exits with code 2.
On success every command prints a JSON summary object to stdout.

Path placeholders used below:

| Placeholder | Meaning |
|---|---|
| `{slug}` | `system_name` from the config, lowercased with hyphens replaced by underscores (`_system_slug`) |
| `{batch_slug}` | The `--batch` value normalized to lowercase alphanumeric with underscores (`_batch_slug`) |
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

## 2. `mdisc generate`

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
2. **Generate candidates.** Call `generate_candidates(system_config, out_path,
   count=count, seed=seed)`. This writes candidates to the output path and
   returns a `GenerateSummary`.
3. **Compute generation metrics.** Reload the written JSONL and count unique
   `candidate_id` values. Call `generation_metrics(requested_count,
   generated_count, invalid_filtered_count, unique_count)` to compute the
   deduplication rate and attach it to the summary as `qa_metrics`.
4. **Write calibration.** Serialize the generation metrics dict as JSON to the
   calibration path.
5. **Write manifest.** Build and write a stage manifest with `stage="generate"`,
   recording both the candidates JSONL and calibration JSON as output paths.
6. **Emit summary.** Print the `GenerateSummary` as JSON to stdout.

### Artifacts

| Artifact | Default path |
|---|---|
| Candidates JSONL | `{workspace}/data/candidates/{slug}_candidates.jsonl` |
| Generation metrics (calibration) | `{workspace}/data/calibration/{slug}_generation_metrics.json` |
| Stage manifest | `{workspace}/data/manifests/{slug}_generate_manifest.json` |

### Return type

`GenerateSummary` (JSON to stdout).

---

## 3. `mdisc screen`

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

## 4. `mdisc hifi-validate`

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

## 5. `mdisc hifi-rank`

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

## 6. `mdisc active-learn`

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

## 7. `mdisc report`

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

## Pipeline data flow

The commands are designed to run in sequence. Each stage reads the output of a
prior stage and writes its own artifacts. The canonical ordering is:

```
ingest --> generate --> screen --> hifi-validate --> hifi-rank --> report
                                        |                ^
                                        v                |
                                    active-learn --------+
                                    (loop back to hifi-validate)
```

The `active-learn` command forms a feedback loop: it reads validated candidates,
trains a surrogate, selects the next batch, and the user runs `hifi-validate`
again on that batch before re-ranking and re-reporting.
