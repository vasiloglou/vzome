# Materials Discovery Workspace

No-DFT materials discovery pipeline for quasicrystal-compatible structures.

For full documentation, see **[developer-docs/materials_discovery/](../developer-docs/materials_discovery/index.md)**.

## Quickstart

```bash
cd materials-discovery
uv sync --extra dev
uv run pytest

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

All M1-M6 milestones and RM0-RM6 real-mode execution phases. Seven CLI commands
(`ingest`, `generate`, `screen`, `hifi-validate`, `hifi-rank`, `active-learn`, `report`)
with mock and real backend modes.

See the [pipeline stages reference](../developer-docs/materials_discovery/pipeline-stages.md)
for per-command details and the [backend system docs](../developer-docs/materials_discovery/backend-system.md)
for adapter architecture.

## Exit Codes

- `0`: success
- `2`: input/config/path validation error
