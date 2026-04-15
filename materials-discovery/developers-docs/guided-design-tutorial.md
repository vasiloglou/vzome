# Guided Design Tutorial

One checked Sc-Zn walkthrough for designing a Zomic-backed motif, previewing
the compiled geometry, generating candidates, evaluating the resulting
structures, and keeping the geometry tied to the existing vZome/Zomic
workflow.

Use this page with the [Operator Runbook](../RUNBOOK.md),
[Pipeline Stages](pipeline-stages.md), and
[Zomic Design Workflow](zomic-design-workflow.md). This tutorial stays on one
worked example so the commands, artifacts, and geometry authority chain do not
drift.

Use the Markdown page when you want the extensive operator story for the
checked workflow. Use the
[Guided Design Tutorial Notebook](../notebooks/guided_design_tutorial.ipynb)
when you want the more executable companion surface with cell-by-cell helpers.
Phase 43 will deepen that notebook further; this page keeps the whole story
legible in one checked document.

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

This page treats that as the `Sc-Zn deterministic spine`:
`.zomic -> raw export -> orbit library -> candidates`.

The `.zomic` file is the design source. Everything downstream is derived from
it.

That deterministic spine is the authority chain even when you branch into the
repo's LLM workflows later. The branches attach to the same operator story
instead of replacing it:

```text
Sc-Zn deterministic spine
  .zomic -> export-zomic -> preview-zomic -> generate -> screen -> hifi-validate -> hifi-rank -> report
    |
    +-- same-system companion lane
    |     llm-generate -> llm-evaluate
    |
    `-- translation/external benchmark branch
          llm-translate -> llm-translated-benchmark-freeze -> llm-register-external-target -> llm-external-benchmark
```

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

### 3.1 Preview the Checked Geometry

The normal read-only preview path now stays inside the repo:

```bash
uv run mdisc preview-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
```

That command keeps the same export contract and writes a standalone viewer next
to the checked raw export:

- `data/prototypes/generated/sc_zn_tsai_bridge.viewer.html`

If you want the same preview flow from Python, use the library helper directly:

```python
from pathlib import Path

from materials_discovery.visualization import preview_zomic_design

summary = preview_zomic_design(
    Path("designs/zomic/sc_zn_tsai_bridge.yaml"),
    show_labels=True,
)
```

What to inspect:

- the viewer should reflect the checked raw export, not an alternate geometry
  source
- the header metadata should still point back to the `.zomic` source and the
  current symmetry
- the output is a preview seam over `.zomic -> raw export -> orbit library ->
  candidates`, not a replacement for that chain

What the signal means:

- `preview-zomic` is now the happy-path inspection tool for the checked design
- `export-zomic` remains the authoritative refresh path
- the preview helper is the reusable surface for notebook or script-driven
  inspection, not a separate service

For the focused reference page, see
[Programmatic Zomic Visualization](programmatic-zomic-visualization.md).

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

## 9. Where the LLM Workflows Branch from the Spine

The checked Sc-Zn walkthrough above is still the operator baseline. The repo's
LLM commands branch from that evidence chain; they do not replace it.

### 9.1 Same-system companion lane

Use this branch when you want to stay in the Sc-Zn family while adding an LLM
proposal or assessment lane on top of the checked Zomic-backed workflow.

| Path | Role |
|------|------|
| `configs/systems/sc_zn_llm_mock.yaml` | Fixture-backed Sc-Zn lane for dry runs and tests |
| `configs/systems/sc_zn_llm_local.yaml` | Local OpenAI-compatible Sc-Zn lane with general-purpose generation plus specialized evaluation |

Representative commands:

```bash
uv run mdisc llm-generate --config configs/systems/sc_zn_llm_mock.yaml --count 5 \
  --out data/candidates/sc_zn_llm_candidates.jsonl

uv run mdisc llm-evaluate --config configs/systems/sc_zn_llm_local.yaml --batch all
```

Artifact families this branch writes:

- `data/candidates/` for the candidate JSONL emitted by `llm-generate`
- `data/manifests/` for the `llm_generate` and `llm_evaluate` stage manifests
- `data/llm_runs/` for `llm-generate` request, attempt, compile, and run audit
  artifacts
- `data/llm_evaluated/` for the additive evaluated candidate JSONL
- `data/llm_evaluations/` for evaluation requests, assessments, and run-level
  audit artifacts

What to inspect:

- the candidate JSONL and `data/manifests/{slug}_llm_generate_manifest.json`
  when you want to verify that the proposal lane still writes standard
  candidate-stage artifacts
- `data/llm_runs/{run_id}/run_manifest.json` when you want the prompt/request
  side of the generation lane
- `data/llm_evaluated/{slug}_{batch_slug}_llm_evaluated.jsonl` and
  `data/llm_evaluations/{run_id}/run_manifest.json` when you want to inspect
  additive synthesis or precursor assessment

What the signal means:

- `llm-generate` is an alternate proposal source that still feeds the same
  screening and validation stages shown earlier
- `llm-evaluate` is an additive assessment layer on ranked candidates; it does
  not replace the deterministic validation or report evidence
- the `.zomic` design and the deterministic `export-zomic -> generate ->
  screen -> hifi-validate -> hifi-rank -> report` spine remain the cleanest
  first path even when you later compare the LLM branch against it

For the broader architecture, see [LLM Integration](llm-integration.md) and the
command reference in [Pipeline Stages](pipeline-stages.md).

### 9.2 Why this branch switches to Al-Cu-Fe

The next branch changes chemistry on purpose.

The deterministic spine in this tutorial stays Sc-Zn because the checked
programmatic visualization seam and the current watched-batch evidence chain are
already anchored there. The translation and external benchmark branch switches
to Al-Cu-Fe because the repo already ships checked fixture-backed benchmark
artifacts, demo translation bundles, and example benchmark specs for that
family.

Treat this as a fixture-availability context switch, not as a new authority
chain. The lesson is still the same: move through explicit artifact handoffs and
read the loss posture or benchmark evidence honestly.

### 9.3 Translation and external benchmark branch

This branch hands work across four artifact roots:

- `data/llm_translation_exports/` — exported CIF or material-string bundles plus
  translation inventories and payloads
- `data/benchmarks/llm_external_sets/` — frozen benchmark-set manifests plus
  included/excluded inventories
- `data/llm_external_models/` — registered external-target identity, environment
  capture, and smoke artifacts
- `data/benchmarks/llm_external/` — comparative benchmark summaries, scorecards,
  and per-target results

#### Export and inspect translated bundles

```bash
uv run mdisc llm-translate \
  --config configs/systems/al_cu_fe.yaml \
  --input data/ranked/al_cu_fe_ranked.jsonl \
  --target cif \
  --export-id al_cu_fe_ranked_cif_v1

uv run mdisc llm-translate-inspect \
  --manifest data/llm_translation_exports/al_cu_fe_ranked_cif_v1/manifest.json
```

What to inspect:

- `data/llm_translation_exports/al_cu_fe_ranked_cif_v1/manifest.json`
- `data/llm_translation_exports/al_cu_fe_ranked_cif_v1/inventory.jsonl`
- the stage manifest under `data/manifests/`

What the signal means:

- this is an interoperability export, not a new source of truth
- fidelity tiers and loss reasons tell you whether a row stayed periodic-safe or
  became a weaker periodic proxy
- the original candidate JSONL and Zomic/QC-native structure remain
  authoritative

See [LLM Translation Runbook](llm-translation-runbook.md) for the deeper export
contract.

#### Freeze and inspect one benchmark pack

```bash
uv run mdisc llm-translated-benchmark-freeze \
  --spec configs/llm/al_cu_fe_translated_benchmark_freeze.yaml

uv run mdisc llm-translated-benchmark-inspect \
  --manifest data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json
```

What to inspect:

- `data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/manifest.json`
- `data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/included.jsonl`
- `data/benchmarks/llm_external_sets/al_cu_fe_translated_benchmark_v1/excluded.jsonl`

What the signal means:

- `included.jsonl` is the case slice the later benchmark is allowed to score
- `excluded.jsonl` keeps mismatches and rejected rows visible instead of hiding
  them
- the freeze contract is the durable handoff from translation into benchmarking

See [Translated Benchmark Runbook](llm-translated-benchmark-runbook.md) for the
freeze contract and exclusion vocabulary.

#### Register, inspect, and smoke-test the external target

```bash
uv run mdisc llm-register-external-target \
  --spec configs/llm/al_cu_fe_external_cif_target.yaml

uv run mdisc llm-inspect-external-target \
  --model-id al_cu_fe_external_cif_demo

uv run mdisc llm-smoke-external-target \
  --model-id al_cu_fe_external_cif_demo
```

What to inspect:

- `data/llm_external_models/al_cu_fe_external_cif_demo/registration.json`
- `data/llm_external_models/al_cu_fe_external_cif_demo/environment.json`
- `data/llm_external_models/al_cu_fe_external_cif_demo/smoke_check.json`

What the signal means:

- the shipped example specs are templates, so registration only succeeds after
  you replace the placeholder local snapshot paths with a real downloaded model
- `registration.json` is the immutable target identity
- `environment.json` and `smoke_check.json` tell you whether the target is
  currently reproducible and ready to benchmark

See [External Target Runbook](llm-external-target-runbook.md) for the target
registration boundary and failure posture.

#### Run and inspect the comparative benchmark

```bash
uv run mdisc llm-external-benchmark \
  --spec configs/llm/al_cu_fe_external_benchmark.yaml

uv run mdisc llm-inspect-external-benchmark \
  --summary data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/benchmark_summary.json
```

What to inspect:

- `data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/benchmark_summary.json`
- `data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/scorecard_by_case.jsonl`
- `data/benchmarks/llm_external/al_cu_fe_external_benchmark_v1/targets/{target_id}/run_manifest.json`

What the signal means:

- the summary keeps exact/anchored evidence separate from approximate/lossy
  diagnostics
- excluded counts and smoke failures stay visible instead of disappearing
- recommendation lines are advisory milestone evidence, not automatic promotion

See [External Benchmark Runbook](llm-external-benchmark-runbook.md) for the full
scorecard interpretation rules.

## 10. When to open desktop vZome

Use the repo-owned preview first, then open desktop vZome only when the task
actually needs authoring or deeper geometric inspection.

| Question | Use this first | Why |
|----------|----------------|-----|
| "Do I want to inspect the current checked geometry quickly?" | `uv run mdisc preview-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml` | The repo preview is the normal checked read-only inspection path. |
| "Do I need to refresh the compiled artifacts after editing the design?" | `uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml` | `export-zomic` is still the authority for raw export and orbit-library refresh. |
| "Do I need to edit the actual motif, try manual orbit changes, or inspect the script interactively?" | Desktop vZome | Desktop vZome remains the authoring and deeper-inspection tool. |
| "Do I need `.vZome` or `.shapes.json` browser parity?" | Not available in this milestone | `.vZome` and `.shapes.json` parity are future work, not current behavior. |

Keep these files straight while iterating:

| File | Use it for |
|------|-------------|
| `designs/zomic/sc_zn_tsai_bridge.zomic` | Editing and visualizing the intended motif |
| `data/prototypes/generated/sc_zn_tsai_bridge.raw.json` | Inspecting the compiled labeled geometry from `vZome core` |
| `data/prototypes/generated/sc_zn_tsai_bridge.json` | Inspecting the orbit library actually consumed by `mdisc generate` |
| `data/candidates/sc_zn_candidates.jsonl` | Inspecting downstream decorated material candidates, not the original geometry source |

When you do need desktop vZome:

1. Open the Zomic editor and load `designs/zomic/sc_zn_tsai_bridge.zomic`.
2. Make the geometry change there.
3. Re-run `uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml`.
4. Re-run `preview-zomic` or the downstream pipeline only after the raw export
   and orbit-library JSON are current again.

Deeper references:

- [Zomic Design Workflow](zomic-design-workflow.md)
- [vZome Geometry Tutorial](vzome-geometry-tutorial.md)
- [Zomic Language Reference](../../core/docs/ZomicReference.md)

## 11. What a Good Next Iteration Looks Like

After you finish one pass through this tutorial:

1. Edit the `.zomic` source or its embedding YAML.
2. Re-export the design.
3. Regenerate the candidate batch.
4. Re-read the screening calibration and the high-fidelity failure reasons.
5. Compare the new report's `recommendation`, `risk_flags`, and `release_gate`
   against the previous run.

That loop keeps geometry, pipeline evidence, and operator judgment on the same
artifact chain instead of splitting them across unrelated tools.
