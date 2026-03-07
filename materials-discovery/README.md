# Materials Discovery Workspace

No-DFT materials discovery pipeline for quasicrystal-compatible structures.

For full documentation, see **[developer-docs/materials_discovery/](../developer-docs/materials_discovery/index.md)**.

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
```

For real-mode execution with MLIP backends:

```bash
uv sync --extra dev --extra mlip
./scripts/run_exec_pipeline.sh
./scripts/run_native_pipeline.sh
```

## What is Implemented

All M1-M6 milestones and RM0-RM6 real-mode execution phases. Eight CLI commands
(`ingest`, `export-zomic`, `generate`, `screen`, `hifi-validate`, `hifi-rank`,
`active-learn`, `report`) with mock and real backend modes.

`export-zomic` and Zomic-backed generation invoke `vZome core` through
`./gradlew :core:zomicExport`, so they require a local Java runtime.

See the [pipeline stages reference](../developer-docs/materials_discovery/pipeline-stages.md)
for per-command details and the [backend system docs](../developer-docs/materials_discovery/backend-system.md)
for adapter architecture. The Zomic authoring path is documented in
[zomic-design-workflow.md](../developer-docs/materials_discovery/zomic-design-workflow.md).

## Exit Codes

- `0`: success
- `2`: input/config/path validation error
