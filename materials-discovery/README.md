# Materials Discovery Workspace

This workspace implements an M1-M4 runnable slice of the no-DFT materials discovery pipeline documented in:

- `developer-docs/materials-discovery-software-scaffold.md`
- `developer-docs/vzome-geometry-tutorial.md` (Section 10.8)

## What is implemented

- `mdisc ingest`: fixture-based ingestion, normalization, deduplication, and JSONL output.
- `mdisc generate`: deterministic candidate generation with schema validation and JSONL output.
- `mdisc screen`: deterministic fast-screen pipeline (proxy relax, thresholding, shortlist ranking).
- `mdisc hifi-validate`: deterministic no-DFT digital validation (committee, uncertainty, proxy hull, phonon, short MD, XRD checks).
- `mdisc hifi-rank`, `mdisc active-learn`, `mdisc report`: interface-complete stage stubs.

## Quickstart

```bash
cd materials-discovery
uv sync --extra dev
uv run mdisc ingest --config configs/systems/al_cu_fe.yaml
uv run mdisc generate --config configs/systems/al_cu_fe.yaml --count 50
uv run mdisc screen --config configs/systems/al_cu_fe.yaml
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch all
uv run pytest
uv run ruff check .
uv run mypy src
```

## Exit codes

- `0`: success
- `2`: input/config/path validation error
- `3`: stage is interface-complete but not implemented
