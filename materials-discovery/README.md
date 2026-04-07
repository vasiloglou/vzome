# Materials Discovery Workspace

No-DFT materials discovery pipeline for quasicrystal-compatible structures.

For full documentation, see **[developers-docs/](./developers-docs/index.md)**.

## Quickstart

```bash
cd materials-discovery
uv sync --extra dev
uv run pytest

# Export a Zomic-authored prototype and generate from it
uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml
uv run mdisc generate --config configs/systems/sc_zn_zomic.yaml --count 32

# Run the mock-mode pipeline
uv run mdisc ingest    --config configs/systems/al_cu_fe.yaml
uv run mdisc generate  --config configs/systems/al_cu_fe.yaml --count 50
uv run mdisc screen    --config configs/systems/al_cu_fe.yaml
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch all
uv run mdisc hifi-rank --config configs/systems/al_cu_fe.yaml
uv run mdisc active-learn --config configs/systems/al_cu_fe.yaml
uv run mdisc report    --config configs/systems/al_cu_fe.yaml

# Run the first LLM inference path (mock + compile-backed validation)
uv run mdisc llm-generate --config configs/systems/al_cu_fe_llm_mock.yaml --count 5
uv run mdisc llm-evaluate --config configs/systems/al_cu_fe_llm_mock.yaml --batch all
uv run mdisc llm-suggest --acceptance-pack data/benchmarks/llm_acceptance/phase9_acceptance_v1/acceptance_pack.json
uv run mdisc llm-translate --config configs/systems/al_cu_fe.yaml --input data/ranked/al_cu_fe_ranked.jsonl --target cif --export-id al_cu_fe_ranked_cif_v1
uv run mdisc llm-translate-inspect --manifest data/llm_translation_exports/al_cu_fe_ranked_cif_v1/manifest.json
./scripts/run_llm_generate_benchmarks.sh --systems all --count 5
./scripts/run_llm_pipeline_benchmarks.sh --systems all --count 5
./scripts/run_llm_acceptance_benchmarks.sh --systems all --count 5
```

For real-mode execution with MLIP backends:

```bash
uv sync --python 3.11 --extra dev --extra mlip
./scripts/run_exec_pipeline.sh
./scripts/run_native_pipeline.sh
```

For the **Phase 4 reference-aware benchmark workflow** (two-system benchmark
matrix with multi-source reference packs):

```bash
# Full two-system benchmark run (Al-Cu-Fe + Sc-Zn):
./scripts/run_reference_aware_benchmarks.sh

# Quick smoke run (30 candidates, skip active-learn):
./scripts/run_reference_aware_benchmarks.sh --count 30 --no-active-learn

# Only one lane:
./scripts/run_reference_aware_benchmarks.sh --config-filter al_cu_fe
```

See the [reference-aware benchmark runbook](./developers-docs/reference-aware-benchmarks.md)
for full prerequisites, config details, and artifact locations.

See the [LLM translation runbook](./developers-docs/llm-translation-runbook.md)
for CIF and CrystalTextLLM-style export commands, bundle layout, and fidelity
boundaries.

A `Ti-Zr-Ni` icosahedral quasicrystal system is also available:
- `configs/systems/ti_zr_ni.yaml`

Additional checked-in `Sc-Zn` real/native configs are now available:
- `configs/systems/sc_zn_real.yaml`
- `configs/systems/sc_zn_native.yaml`

The shipped `Sc-Zn` Zomic design at
`designs/zomic/sc_zn_tsai_bridge.yaml` is anchor-fitted to the
crystallographic `sc_zn_tsai_sczn6.json` prototype before candidate generation.
That keeps Zomic as the authoring language while tightening the downstream
geometry used by the real/native validation stages.

The current `Sc-Zn` bridge goes one step further: it expands the snapped Zomic
seed geometry into a fuller anchored orbit set (`100` sites across five selected
`ScZn6` anchor orbits) instead of emitting only the reduced labeled subset.

Real/native `hifi-validate` now also applies a cheap geometry prefilter before
phonon. Crowded candidates are failed early with recorded metrics instead of
spending most of the runtime inside the native phonon backend.

`sc_zn_real.yaml` and `sc_zn_native.yaml` use the local
`data/external/fixtures/hypodx_sample.json` ingest source because the pinned
HYPOD-X snapshot does not yet include `Sc-Zn` rows. Their calibrated assets are:
- `data/benchmarks/sc_zn_benchmark.json`
- `data/external/pinned/sc_zn_validation_snapshot_2026_03_07.json`

## What is Implemented

All M1-M6 milestones and RM0-RM6 real-mode execution phases are implemented,
along with the LLM generation/evaluation/governance workflow, serving
benchmarking, checkpoint lifecycle management, and the Phase 33 translation
export and inspection commands. The CLI surface spans the deterministic core
pipeline plus additive LLM/operator commands such as `llm-generate`,
`llm-evaluate`, `llm-suggest`, `llm-approve`, `llm-launch`,
`llm-serving-benchmark`, `llm-translate`, and `llm-translate-inspect`.

`export-zomic` and Zomic-backed generation invoke `vZome core` through
`./gradlew :core:zomicExport`, so they require a local Java runtime.

See the [pipeline stages reference](./developers-docs/pipeline-stages.md)
for per-command details and the [backend system docs](./developers-docs/backend-system.md)
for adapter architecture. The Zomic authoring path is documented in
[zomic-design-workflow.md](./developers-docs/zomic-design-workflow.md).

## Exit Codes

- `0`: success
- `2`: input/config/path validation error
