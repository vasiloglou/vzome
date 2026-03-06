# Materials Discovery Workspace

This workspace implements a full M1-M6 runnable slice of the no-DFT materials discovery pipeline documented in:

- `developer-docs/materials-discovery-software-scaffold.md`
- `developer-docs/vzome-geometry-tutorial.md` (Section 10.8)

## What is implemented

- `mdisc ingest`: fixture-based ingestion, normalization, deduplication, and JSONL output.
- Ingest backend switch: `backend.mode=mock|real` with pluggable ingest adapter registry.
- Ingest artifact manifests: `data/manifests/*_ingest_manifest.json` with config/backend/output hashes.
- Snapshot-backed RM1 integration test target: `uv run pytest -m integration`.
- `mdisc generate`: deterministic candidate generation with schema validation and JSONL output.
- `mdisc screen`: deterministic fast-screen pipeline (proxy relax, thresholding, shortlist ranking).
- `mdisc hifi-validate`: deterministic no-DFT digital validation (committee, uncertainty, proxy hull, phonon, short MD, XRD checks).
- `mdisc active-learn`: deterministic surrogate fitting + next-batch acquisition from validated candidates.
- `mdisc hifi-rank`: deterministic uncertainty-aware ranking of validated candidates.
- `mdisc report`: experiment-facing report generation with synthetic powder-XRD signatures.
- Stage manifests are emitted for every command under `data/manifests/`.
- Calibration artifacts are emitted under `data/calibration/`.
- Model/feature registry artifacts are emitted under `data/registry/models` and `data/registry/features`.
- Backend capability matrix is tracked in `data/registry/backend_capabilities.yaml`.

## Quickstart

```bash
cd materials-discovery
uv sync --extra dev
uv run mdisc ingest --config configs/systems/al_cu_fe.yaml
uv run mdisc ingest --config configs/systems/al_cu_fe_real.yaml
uv run mdisc generate --config configs/systems/al_cu_fe.yaml --count 50
uv run mdisc screen --config configs/systems/al_cu_fe.yaml
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch all
uv run mdisc hifi-rank --config configs/systems/al_cu_fe.yaml
uv run mdisc active-learn --config configs/systems/al_cu_fe.yaml
uv run mdisc report --config configs/systems/al_cu_fe.yaml
./scripts/run_real_pipeline.sh
uv run pytest
uv run pytest -m integration
uv run ruff check .
uv run mypy src
```

## Exit codes

- `0`: success
- `2`: input/config/path validation error
