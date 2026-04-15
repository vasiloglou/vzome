# Guided Design Tutorial

One checked Sc-Zn walkthrough for designing a Zomic-backed motif, generating
candidates, evaluating the resulting structures, and keeping the geometry tied
to the existing vZome/Zomic workflow.

Use this page with the [Operator Runbook](../RUNBOOK.md),
[Pipeline Stages](pipeline-stages.md), and
[Zomic Design Workflow](zomic-design-workflow.md). This tutorial stays on one
worked example so the commands, artifacts, and geometry authority chain do not
drift.

## 1. Before You Start

Run everything from the `materials-discovery/` workspace:

```bash
cd materials-discovery
uv sync --extra dev
```

If your local validation lane needs real or native MLIP providers, follow the
extra environment setup in the [Operator Runbook](../RUNBOOK.md).

The Sc-Zn Zomic lane also needs a local Java runtime for `mdisc export-zomic`
and for `mdisc generate` when the system config points at a Zomic design.

## 2. Know the Worked Example

The tutorial uses these checked inputs:

| Path | Role |
|------|------|
| `configs/systems/sc_zn_zomic.yaml` | Activates the Sc-Zn Zomic-backed generation lane |
| `designs/zomic/sc_zn_tsai_bridge.yaml` | Design embedding, anchoring, and export contract |
| `designs/zomic/sc_zn_tsai_bridge.zomic` | Editable geometry source |
| `data/prototypes/sc_zn_tsai_sczn6.json` | Anchor prototype used during export |

The geometry authority chain in this tutorial is:

`sc_zn_tsai_bridge.zomic` -> `sc_zn_tsai_bridge.raw.json` -> `sc_zn_tsai_bridge.json` -> candidate and report artifacts

The `.zomic` file is the design source. Everything downstream is derived from it.

## 3. Export the Zomic Design

Compile the Zomic design into the raw labeled geometry export and the
orbit-library JSON that `mdisc generate` consumes:

```bash
uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
```

Primary outputs:

| Artifact | Meaning |
|----------|---------|
| `data/prototypes/generated/sc_zn_tsai_bridge.raw.json` | Raw labeled geometry emitted by `vZome core` |
| `data/prototypes/generated/sc_zn_tsai_bridge.json` | Orbit-library prototype used by the generator |

Helpful inspection commands:

```bash
jq '{zomic_file, symmetry, labeled_points: (.labeled_points | length), segments: (.segments | length)}' \
  data/prototypes/generated/sc_zn_tsai_bridge.raw.json

jq '{prototype_key, source_kind, orbit_count: (.orbits | length), anchor_orbit_summary}' \
  data/prototypes/generated/sc_zn_tsai_bridge.json
```

What to look for:

- The raw export should point back to `sc_zn_tsai_bridge.zomic`.
- The orbit-library JSON should report `source_kind:
  "zomic_export_anchor_expanded"`.
- As of 2026-04-15, the checked raw export contains 52 labeled points and 52
  segments, and the orbit-library JSON expands to 5 anchor-selected orbits with
  100 total sites.

## 4. Generate Candidates

Generate one candidate batch from the exported Sc-Zn prototype:

```bash
uv run mdisc generate --config configs/systems/sc_zn_zomic.yaml --count 32
```

Primary outputs:

| Artifact | Meaning |
|----------|---------|
| `data/candidates/sc_zn_candidates.jsonl` | Candidate population |
| `data/calibration/sc_zn_generation_metrics.json` | Generation QA summary |
| `data/manifests/sc_zn_generate_manifest.json` | Generate-stage provenance |

Helpful inspection commands:

```bash
head -n 1 data/candidates/sc_zn_candidates.jsonl | jq '{candidate_id, composition, prototype: .provenance.prototype_key, source_kind: .provenance.prototype_source_kind, site_count: (.sites | length)}'

jq '{stage, system, created_at_utc, output_hashes}' \
  data/manifests/sc_zn_generate_manifest.json
```

What to look for:

- The candidate provenance should still name the `sc_zn_tsai_bridge` prototype.
- The `source_kind` should stay tied to the Zomic export path.
- The manifest is your run-level fingerprint for later comparisons.

## 5. Screen the Candidate Population

Apply the fast screening stage:

```bash
uv run mdisc screen --config configs/systems/sc_zn_zomic.yaml
```

Primary outputs:

| Artifact | Meaning |
|----------|---------|
| `data/screened/sc_zn_screened.jsonl` | Candidates that survived fast screening |
| `data/calibration/sc_zn_screen_calibration.json` | Screening thresholds and pass counts |
| `data/manifests/sc_zn_screen_manifest.json` | Screen-stage provenance |

Helpful inspection commands:

```bash
jq '{input_count, relaxed_count, passed_count, shortlisted_count, min_distance_proxy, max_energy_proxy}' \
  data/calibration/sc_zn_screen_calibration.json

head -n 1 data/screened/sc_zn_screened.jsonl | jq '{candidate_id, shortlist_rank: .screen.shortlist_rank, energy_proxy_ev_per_atom: .screen.energy_proxy_ev_per_atom, min_distance_proxy: .screen.min_distance_proxy, passed_thresholds: .screen.passed_thresholds}'
```

How to interpret the screening artifacts:

- `passed_count` tells you how many candidates cleared the fast thresholds.
- `shortlisted_count` tells you how many remain in the ranked screening slice
  that feeds high-fidelity validation.
- `shortlist_rank` is the ordering used when later batch selectors use `topN`.
- `energy_proxy_ev_per_atom` and `min_distance_proxy` are fast filters, not the
  final high-fidelity verdict.

As of 2026-04-15, the checked `sc_zn_screen_calibration.json` snapshot records
30 input candidates, 20 passing thresholds, and 4 shortlisted candidates.

## 6. Run High-Fidelity Validation

Validate the shortlisted Sc-Zn candidates:

```bash
uv run mdisc hifi-validate --config configs/systems/sc_zn_zomic.yaml --batch all
```

Primary outputs:

| Artifact | Meaning |
|----------|---------|
| `data/hifi_validated/sc_zn_all_validated.jsonl` | High-fidelity validation results |
| `data/calibration/sc_zn_all_validation_calibration.json` | Validation batch counts |
| `data/manifests/sc_zn_all_hifi_validate_manifest.json` | Validation-stage provenance |

Helpful inspection command:

```bash
head -n 1 data/hifi_validated/sc_zn_all_validated.jsonl | jq '{candidate_id, status: .digital_validation.status, passed_checks: .digital_validation.passed_checks, geometry_prefilter_pass: .digital_validation.geometry_prefilter_pass, phonon_imaginary_modes: .digital_validation.phonon_imaginary_modes, md_stability_score: .digital_validation.md_stability_score, xrd_confidence: .digital_validation.xrd_confidence}'
```

How to interpret the validation fields:

- `geometry_prefilter_pass`: whether the cheap crowding check passed before the
  expensive phonon work.
- `phonon_imaginary_modes`: a nonzero count is a stability warning.
- `md_stability_score`: short-MD structural stability signal.
- `xrd_confidence`: how strongly the simulated pattern matches the reference.
- `passed_checks`: the all-gates result across uncertainty, proxy hull, phonon,
  MD, and XRD.

As of 2026-04-15, the first checked validated row is `md_000006`, and it fails
with `geometry_prefilter_pass=false`, `phonon_imaginary_modes=99`,
`md_stability_score=0.0`, and `xrd_confidence=0.0`. That is a useful tutorial
outcome: the current tooling is showing you why the candidate should not be
promoted.

## 7. Rank the Validated Candidates

Produce the ranked candidate list:

```bash
uv run mdisc hifi-rank --config configs/systems/sc_zn_zomic.yaml
```

Primary outputs:

| Artifact | Meaning |
|----------|---------|
| `data/ranked/sc_zn_ranked.jsonl` | Final ranked candidates |
| `data/calibration/sc_zn_ranking_calibration.json` | Ranking counts |
| `data/manifests/sc_zn_hifi_rank_manifest.json` | Ranking-stage provenance |

What to look for:

- Ranking deduplicates validated candidates by `candidate_id`.
- Candidates can still receive a ranking even when `passed_checks` is false;
  the important question is what recommendation and risk flags they carry into
  the report.

## 8. Build and Read the Report

Produce the report bundle:

```bash
uv run mdisc report --config configs/systems/sc_zn_zomic.yaml
```

Primary outputs:

| Artifact | Meaning |
|----------|---------|
| `data/reports/sc_zn_report.json` | Report summary and ranked entries |
| `data/reports/sc_zn_xrd_patterns.jsonl` | Stored simulated XRD pattern rows |
| `data/reports/sc_zn_benchmark_pack.json` | Compact benchmark-context bundle when present |
| `data/manifests/sc_zn_pipeline_manifest.json` | Full pipeline provenance chain |

Helpful inspection commands:

```bash
jq '{system, ranked_count, reported_count, summary, release_gate}' \
  data/reports/sc_zn_report.json

jq '{backend_mode, benchmark_context, report_metrics}' \
  data/reports/sc_zn_benchmark_pack.json

head -n 3 data/reports/sc_zn_xrd_patterns.jsonl | jq -s 'map({candidate_id, peaks: (.pattern.peaks | length)})'
```

How to interpret the report:

- `recommendation` is the operator-facing next-step signal.
- `priority` is the sorting lane (`watch`, `secondary`, `medium`, `high`).
- `risk_flags` tells you why a candidate is being held back.
- `stability_probability` is the current summary signal for structural promise.
- `release_gate` tells you whether the run has enough evidence to move into a
  more serious experimental or benchmark handoff.

As of 2026-04-15, the checked `sc_zn_report.json` snapshot reports 4 ranked and
4 reported candidates. All four remain in `hold` / `watch`, and the current top
entry is `md_000012` with risk flags including `failed_digital_checks`,
`marginal_proxy_hull`, `out_of_distribution`, and `pattern_overlap`.

That is the right reading of the current example: the tooling is not telling you
"ship this"; it is telling you why the batch is still a watchlist rather than a
promotion candidate set.

## 9. Visualize with vZome and Zomic

Use the existing vZome/Zomic path for visualization and iteration:

1. Keep `designs/zomic/sc_zn_tsai_bridge.zomic` as the editable geometry source.
2. Open the vZome desktop app's Zomic editor and load that `.zomic` file.
3. Run the script in the editor to inspect the current motif directly in the
   existing vZome workflow.
4. After you edit the script, rerun:

   ```bash
   uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
   ```

5. Regenerate candidates only after the raw export and orbit-library JSON are
   current again.

Use these files for different questions:

| File | Use it for |
|------|-------------|
| `designs/zomic/sc_zn_tsai_bridge.zomic` | Editing and visualizing the intended motif |
| `data/prototypes/generated/sc_zn_tsai_bridge.raw.json` | Inspecting the compiled labeled geometry from `vZome core` |
| `data/prototypes/generated/sc_zn_tsai_bridge.json` | Inspecting the orbit library actually consumed by `mdisc generate` |
| `data/candidates/sc_zn_candidates.jsonl` | Inspecting downstream decorated material candidates, not the original geometry source |

If you need deeper reference while iterating, use:

- [Zomic Design Workflow](zomic-design-workflow.md)
- [vZome Geometry Tutorial](vzome-geometry-tutorial.md)
- [Zomic Language Reference](../../core/docs/ZomicReference.md)

## 10. What a Good Next Iteration Looks Like

After you finish one pass through this tutorial:

1. Edit the `.zomic` source or its embedding YAML.
2. Re-export the design.
3. Regenerate the candidate batch.
4. Re-read the screening calibration and the high-fidelity failure reasons.
5. Compare the new report's `recommendation`, `risk_flags`, and `release_gate`
   against the previous run.

That loop keeps geometry, pipeline evidence, and operator judgment on the same
artifact chain instead of splitting them across unrelated tools.
