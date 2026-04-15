# Phase 39 Research: Guided Design, Evaluation, and Visualization Tutorial

## Goal

Produce one honest, runnable tutorial for the current Sc-Zn Zomic-backed
workflow that teaches:

1. how to export and run a design,
2. where each pipeline stage writes its artifacts,
3. how to interpret the current evidence surface, and
4. how the same example stays connected to the vZome/Zomic geometry path.

## Key Findings

### 1. The worked example is already locked and well-backed

Phase 37 already fixed the tutorial scope to one path:

```bash
cd materials-discovery
uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
uv run mdisc generate --config configs/systems/sc_zn_zomic.yaml --count 32
uv run mdisc screen --config configs/systems/sc_zn_zomic.yaml
uv run mdisc hifi-validate --config configs/systems/sc_zn_zomic.yaml --batch all
uv run mdisc hifi-rank --config configs/systems/sc_zn_zomic.yaml
uv run mdisc report --config configs/systems/sc_zn_zomic.yaml
```

The example assets already exist in the repo, so the tutorial can cite concrete
files instead of placeholders.

### 2. The geometry authority chain is clear in the checked assets

Observed artifact chain:

| Stage | Artifact | What it means |
|------|----------|---------------|
| Design source | `designs/zomic/sc_zn_tsai_bridge.zomic` | Human-edited Zomic program. This is the highest-authority geometry source. |
| Design config | `designs/zomic/sc_zn_tsai_bridge.yaml` | Embedding and anchoring contract for the Zomic design. |
| Raw compiled geometry | `data/prototypes/generated/sc_zn_tsai_bridge.raw.json` | `vZome core` export output. Current snapshot contains 52 labeled points and 52 segments in icosahedral symmetry. |
| Generator prototype | `data/prototypes/generated/sc_zn_tsai_bridge.json` | Orbit-library JSON consumed by `mdisc generate`. Current snapshot uses `source_kind: zomic_export_anchor_expanded`, 5 selected anchor orbits, and 100 sites. |
| Candidate population | `data/candidates/sc_zn_candidates.jsonl` | Decorated candidate structures generated from the prototype. First checked candidate uses prototype `sc_zn_tsai_bridge` with 100 sites. |

Implication: the tutorial should explicitly say that downstream candidate and
report artifacts do not replace the `.zomic` file as the geometry source.

### 3. The checked screening and report artifacts provide good interpretation anchors

Current checked snapshot values:

| Artifact | Observation |
|----------|-------------|
| `data/calibration/sc_zn_screen_calibration.json` | `input_count=30`, `passed_count=20`, `shortlisted_count=4` |
| `data/screened/sc_zn_screened.jsonl` first row | `candidate_id=md_000006`, `shortlist_rank=1`, `energy_proxy_ev_per_atom=-2.778674`, `min_distance_proxy=0.751937` |
| `data/hifi_validated/sc_zn_all_validated.jsonl` first row | `candidate_id=md_000006` failed validation, `geometry_prefilter_pass=false`, `phonon_imaginary_modes=99`, `xrd_confidence=0.0` |
| `data/reports/sc_zn_report.json` | `ranked_count=4`, `reported_count=4`, all four are `hold` / `watch` in the current snapshot |
| top report entry | `md_000012`, `recommendation=hold`, `priority=watch`, risk flags include `failed_digital_checks`, `marginal_proxy_hull`, `out_of_distribution`, `pattern_overlap` |

Implication: the tutorial can teach readers how to interpret "not ready yet"
signals instead of pretending the example ends in a perfect candidate.

### 4. The benchmark-pack artifact is optional but present

`data/reports/sc_zn_benchmark_pack.json` exists and records:

- benchmark context,
- backend mode,
- stage manifest paths,
- report metrics.

It does not need to be the main tutorial surface, but it is worth mentioning as
the compact run-comparison artifact when the report includes benchmark context.

### 5. The XRD patterns file exists but may be sparse

The checked first three rows of `data/reports/sc_zn_xrd_patterns.jsonl` have
`candidate_id` values but zero stored peaks in the sampled rows. The tutorial
should describe the file as the place to inspect simulated patterns rather than
promising that every committed snapshot includes rich peak arrays.

### 6. The desktop app already supports `.zomic` load and run

`desktop/src/main/java/org/vorthmann/zome/ui/ZomicEditorPanel.java` exposes a
Zomic editor with `load`, `save`, and `run` actions for `.zomic` files.

Implication: the visualization section can honestly instruct a desktop vZome
user to open the Zomic editor, load `sc_zn_tsai_bridge.zomic`, and run it,
without inventing a new integration path.

## Recommended Tutorial Shape

1. **Before you start**
   - `cd materials-discovery`
   - `uv sync --extra dev`
   - mention local Java runtime for the Sc-Zn Zomic lane

2. **Design and export**
   - show `sc_zn_tsai_bridge.yaml` and `sc_zn_tsai_bridge.zomic`
   - run `mdisc export-zomic`
   - explain raw export vs orbit-library JSON

3. **Generate candidates**
   - run `mdisc generate --config configs/systems/sc_zn_zomic.yaml --count 32`
   - point to `data/candidates/sc_zn_candidates.jsonl` and the generate manifest

4. **Screen**
   - run `mdisc screen`
   - inspect `data/screened/sc_zn_screened.jsonl` and
     `data/calibration/sc_zn_screen_calibration.json`
   - teach `passed_count` and `shortlisted_count`

5. **Validate**
   - run `mdisc hifi-validate --batch all`
   - teach `geometry_prefilter_pass`, `phonon_imaginary_modes`, `md_stability_score`,
     and `xrd_confidence`

6. **Rank and report**
   - run `mdisc hifi-rank`
   - run `mdisc report`
   - teach `recommendation`, `priority`, `risk_flags`, `stability_probability`,
     `release_gate`, and optional benchmark-pack context

7. **Visualize with vZome/Zomic**
   - keep `.zomic` as the editable source
   - use the desktop Zomic editor to load and run the script
   - use `export-zomic` again after edits so the raw export and orbit-library
     JSON catch up before regeneration

## Risks and Guardrails

- Do not imply that the example produces synthesis-ready candidates. The checked
  snapshot does not.
- Do not imply that `sc_zn_xrd_patterns.jsonl` always contains dense peak data
  in the committed snapshot.
- Do not imply that downstream candidate JSONL is the geometry source of truth.
- Do not broaden the tutorial to a second chemistry or to translation/external
  benchmarking flows in this phase.

## Recommendation

Create one tutorial page plus one docs-index link. Keep the prose practical,
date the few exact checked values that anchor interpretation, and end with the
geometry authority chain so users know what to edit and what to regenerate.
