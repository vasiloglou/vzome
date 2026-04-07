# Phase 33 Research

## Existing Code Surface

- `materials-discovery/src/materials_discovery/llm/translation.py` already
  turns `CandidateRecord` plus a typed target descriptor into a deterministic
  `TranslatedStructureArtifact`.
- `materials-discovery/src/materials_discovery/llm/translation_export.py`
  already emits the two shipped downstream payload families and preserves the
  Phase 32 compatibility decision:
  - CIF may carry comment metadata
  - `crystaltextllm_material_string` raw bodies stay bare and parser-compatible
- `materials-discovery/src/materials_discovery/cli.py` already establishes the
  repo’s operator pattern:
  - `--config PATH` entrypoints
  - explicit file-backed outputs
  - JSON summaries on success
  - `FileNotFoundError` / `ValidationError` / `ValueError` -> exit code `2`
  - stage manifests under `data/manifests/`
- `materials-discovery/src/materials_discovery/llm/storage.py` already creates
  dedicated artifact roots for eval sets, serving benchmarks, campaigns, and
  checkpoints. Translation exports should follow that pattern instead of
  piggybacking on ranked/eval/report directories.
- `materials-discovery/src/materials_discovery/llm/eval_set.py` shows the
  preferred “bundle + manifest” pattern for later experiment reuse, but its
  current schema is intentionally Zomic/example-pack shaped and should not be
  silently repurposed for external CIF/material-string text.

## Recommended Implementation Shape

### 1. Ship flat CLI commands, not a new sub-app

Use:

- `mdisc llm-translate`
- `mdisc llm-translate-inspect`

Why:

- Existing LLM operator commands (`llm-generate`, `llm-evaluate`,
  `llm-serving-benchmark`, `llm-launch`, `llm-replay`, `llm-compare`) are flat.
- A new `llm-translation` sub-app would add a parallel discoverability pattern
  for a single phase-sized workflow.
- Flat names keep the README/help/docs update small and consistent.

### 2. Require both `--config` and an explicit candidate input path

Recommended command posture:

```bash
mdisc llm-translate \
  --config configs/systems/al_cu_fe_llm_mock.yaml \
  --input data/ranked/al_cu_fe_ranked.jsonl \
  --target cif \
  --export-id al_cu_fe_ranked_cif_v1
```

Why this is the best fit:

- `--config` keeps the export run anchored on the repo’s system/backend context,
  lets the workflow attach benchmark context, and makes stage-manifest writing
  consistent with the rest of the CLI.
- `--input` keeps the actual source candidate file explicit and auditable.
  Translation may later be run over candidates, ranked candidates, LLM-evaluated
  candidates, or checked-in fixture JSONL; forcing one hidden default path now
  would be too rigid.

Avoid:

- implicit “always read ranked JSONL”
- notebook-only usage
- commands that accept only stdin/stdout text with no artifact bundle

### 3. Create a dedicated translation artifact family

Recommended storage shape:

```text
materials-discovery/data/llm_translation_exports/{export_id}/
├── manifest.json
├── inventory.jsonl
└── payloads/
    ├── {candidate_id}.cif
    └── {candidate_id}.material_string.txt
```

Recommended supporting stage manifest:

```text
materials-discovery/data/manifests/{system_slug}_{export_id}_llm_translate_manifest.json
```

Rationale:

- matches the repo’s existing “artifact dir + manifest” style
- keeps raw payloads separate from machine-readable bundle metadata
- gives the broader pipeline a standard stage-manifest entry in
  `data/manifests/`

### 4. Use one inventory JSONL as the later external-model hook

The simplest additive benchmark/eval-set hook is a translation inventory JSONL
where each row includes both provenance metadata and the emitted text itself.

Recommended row contents:

- `export_id`
- `candidate_id`
- `system`
- `template_family`
- `target_family`
- `target_format`
- `fidelity_tier`
- `loss_reasons`
- `diagnostic_codes`
- `composition`
- `payload_path`
- `payload_hash`
- `emitted_text`

Why this works well:

- operators still get raw files per candidate
- inspect/tracing stays easy
- later external-model phases can consume one JSONL directly without having to
  redesign the current `llm_eval_set` schema prematurely
- the repo remains honest that current eval-set semantics are still Zomic-first

### 5. Keep provenance in sidecars, not inside the raw material-string body

Phase 32 already proved the raw `crystaltextllm_material_string` body must stay
bare for parser compatibility. Phase 33 should preserve that by storing
provenance in:

- the translation bundle manifest
- the inventory rows
- the stage manifest under `data/manifests/`

Do not:

- prepend repo-only headers to the raw material-string files
- make raw payload bodies carry information that breaks downstream parsers

### 6. Reuse existing lineage/benchmark helpers where available

Recommended CLI integration:

- load candidates from the explicit `--input` JSONL path
- derive `system_slug` from the supplied config
- use `_resolve_campaign_lineage(system_slug, candidates)` to capture any LLM
  campaign lineage already attached to candidate provenance
- use `_load_benchmark_context(config, system_slug)` to attach the benchmark
  context block that other later-stage artifacts already emit

This keeps translation export auditable in the same language as ranking/report.

## Recommended New Models And Helpers

### `llm/schema.py`

Add translation-specific models here so the translation contract stays inside
the LLM/interop boundary:

- `TranslationBundleManifest`
- `TranslationInventoryRow`
- `TranslationExportSummary`

Keep summary + manifest + row types together with the existing translation
artifact models instead of scattering them across unrelated packages.

### `llm/storage.py`

Add deterministic path helpers:

- `llm_translation_export_dir(export_id, root=None)`
- `llm_translation_manifest_path(export_id, root=None)`
- `llm_translation_inventory_path(export_id, root=None)`
- `llm_translation_payload_dir(export_id, root=None)`
- `llm_translate_stage_manifest_path(system_slug, export_id, root=None)`

### `llm/translation_bundle.py`

Add the workflow layer that:

- loads candidate rows
- prepares translated artifacts
- emits text through the Phase 32 seam
- writes payload files
- writes inventory rows
- writes the bundle manifest

Keep the CLI thin by placing the file-writing logic here rather than inside
`cli.py`.

## CLI Recommendations

### `mdisc llm-translate`

Recommended arguments:

- `--config PATH` required
- `--input PATH` required
- `--target {cif,material_string}` required
- `--export-id TEXT` required

Recommended behavior:

- fail early if config or input path is missing
- validate every JSONL row as `CandidateRecord`
- create the translation bundle under
  `data/llm_translation_exports/{export_id}/`
- write a standard stage manifest under `data/manifests/`
- print a JSON summary including `manifest_path`, `inventory_path`, and payload
  count

### `mdisc llm-translate-inspect`

Recommended arguments:

- `--manifest PATH` required
- optional `--candidate-id TEXT` filter

Recommended behavior:

- read the bundle manifest and inventory JSONL
- print a concise operator summary:
  - export id
  - target
  - input path
  - candidate count
  - lossy count
  - stage manifest path if present
- when `--candidate-id` is supplied, print the matching inventory row details

This is enough to satisfy “inspect and trace” without inventing a broader query
language in the same phase.

## Docs Recommendations

Phase 33 docs should be split cleanly:

- **Runbook:** new operator-facing translation workflow note with example
  commands, artifact locations, and “when to trust which format”
- **Pipeline reference:** add `llm-translate` and `llm-translate-inspect` to
  `pipeline-stages.md`
- **Entry points:** update `README.md` and `developers-docs/index.md`
- **Contract note:** keep `llm-translation-contract.md` technical, but link to
  the new runbook for operator usage

## Risks To Design Around

- **Overreaching into external-model runtime work:** this phase should stop at
  reusable payload bundles and docs, not add execution against external models.
- **Silent schema drift from existing eval sets:** do not retrofit current
  `LlmEvalSetExample` rows to hold CIF/material-string text.
- **Losing raw-format compatibility:** especially for material-string output,
  provenance belongs in sidecars.
- **Hiding input provenance:** the bundle must record the candidate input path
  and any available lineage/benchmark context.

## Recommended Plan Split

- **Plan 01:** translation bundle schema/storage/core writer with deterministic
  payload directory + manifest + inventory JSONL
- **Plan 02:** `llm-translate` and `llm-translate-inspect` CLI commands plus
  stage-manifest/tracing integration
- **Plan 03:** operator docs and command-reference updates with lightweight help
  coverage

## Validation Strategy

- Add a focused core suite for bundle writing and manifest/inventory semantics.
- Add a dedicated CLI suite for `llm-translate` and `llm-translate-inspect`.
- Reuse the existing Phase 31/32 fixture candidates so the operator surface is
  anchored on the exact/export-ready and lossy/proxy boundary cases already
  shipped.

