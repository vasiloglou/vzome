# LLM Translation Runbook

This runbook explains how to export existing `CandidateRecord` JSONL rows into
deterministic CIF or CrystalTextLLM-style material-string bundles, where the
artifacts are written, and how to interpret the resulting fidelity labels.

---

## Overview

Phase 33 adds two operator commands:

- `mdisc llm-translate` writes a translation bundle plus a standard stage manifest
- `mdisc llm-translate-inspect` reads that bundle back and prints a concise
  per-candidate trace

These commands are additive interoperability helpers. They do not replace the
original candidate JSONL or the Zomic/QC-native source representation.

---

## Prerequisites

1. Run any upstream stage that produces `CandidateRecord` JSONL.
2. Choose the explicit input file you want to export.
3. Keep the matching system config available so the translation manifest can
   record the right system slug and benchmark context.

Common input sources:

- `data/candidates/{slug}_candidates.jsonl`
- `data/screened/{slug}_screened.jsonl`
- `data/ranked/{slug}_ranked.jsonl`
- `data/llm_evaluated/{slug}_{batch_slug}_llm_evaluated.jsonl`

---

## Exporting a CIF bundle

```bash
cd materials-discovery
uv run mdisc llm-translate \
  --config configs/systems/al_cu_fe.yaml \
  --input data/ranked/al_cu_fe_ranked.jsonl \
  --target cif \
  --export-id al_cu_fe_ranked_cif_v1
```

Use `--target cif` when the downstream consumer expects a conventional
cell-and-sites crystal text format.

---

## Exporting a CrystalTextLLM-style material-string bundle

```bash
cd materials-discovery
uv run mdisc llm-translate \
  --config configs/systems/al_cu_fe.yaml \
  --input data/ranked/al_cu_fe_ranked.jsonl \
  --target material_string \
  --export-id al_cu_fe_ranked_material_string_v1
```

Use `--target material_string` when the downstream consumer expects the bare
line-oriented `crystaltextllm_material_string` body.

The raw `.material_string.txt` payload stays parser-compatible on purpose.
Provenance, loss posture, and benchmark metadata live in the bundle manifest,
inventory JSONL, and stage manifest instead of being embedded into that raw
body.

---

## Inspecting an existing bundle

```bash
cd materials-discovery
uv run mdisc llm-translate-inspect \
  --manifest data/llm_translation_exports/al_cu_fe_ranked_cif_v1/manifest.json
```

To focus on one candidate:

```bash
uv run mdisc llm-translate-inspect \
  --manifest data/llm_translation_exports/al_cu_fe_ranked_cif_v1/manifest.json \
  --candidate-id al_cu_fe_fixture_periodic_001
```

The inspect command prints:

- export ID and target family
- original input JSONL path
- candidate and lossy counts
- stage manifest path when present
- selected candidate payload paths, fidelity tiers, loss reasons, and diagnostics

---

## Artifact layout

Each export writes a dedicated bundle under:

```text
data/llm_translation_exports/{export_id}/
```

Files inside that bundle:

- `manifest.json` -- bundle-level metadata, counts, lineage, and benchmark context
- `inventory.jsonl` -- one row per exported candidate, including `payload_path`,
  `payload_hash`, `fidelity_tier`, `loss_reasons`, `diagnostic_codes`, and the
  inline `emitted_text`
- `payloads/` -- raw `.cif` or `.material_string.txt` files

The command also writes a standard stage manifest here:

```text
data/manifests/{system_slug}_{export_id}_llm_translate_manifest.json
```

That stage manifest keeps translation bundles visible to the same provenance
and benchmark tooling used by the rest of the pipeline.

---

## Fidelity boundaries

The key translation rule is simple: exported text is a view, not a new source
of truth.

- `exact` means the candidate already had periodic-safe fractional coordinates
  compatible with the requested target
- `anchored` means the structure is still periodic-safe, but one or more
  fractional coordinates were derived from stored cartesian values
- `approximate` means translation succeeded through a weaker periodic proxy
- `lossy` means QC-native semantics could not be preserved in the requested
  target and the export is only a periodic proxy

When a QC-native candidate is forced into `cif` or `material_string`, the raw
payload may still be useful for downstream experiments, but the original
candidate JSONL and Zomic-derived structure remain authoritative.

Common loss reasons:

- `aperiodic_to_periodic_proxy`
- `coordinate_derivation_required`
- `qc_semantics_dropped`

For the deeper serializer contract, see
[LLM Translation Contract](llm-translation-contract.md).

---

## Operator guidance

- Keep `--input` explicit. The translation command does not guess which stage's
  candidate JSONL you intended to export.
- Treat `inventory.jsonl` as the easiest integration surface when another tool
  needs both metadata and the emitted text in one file.
- Use `llm-translate-inspect` before sharing payloads externally so you can
  confirm whether the bundle contains periodic-safe exports or lossy periodic
  proxies.
- If a downstream workflow needs QC-native fidelity, stop at the candidate
  JSONL/Zomic level instead of forcing translation.
