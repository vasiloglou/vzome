# Materials Discovery Workspace

This workspace implements an M1+M2 runnable slice of the no-DFT materials discovery pipeline documented in:

- `developer-docs/materials-discovery-software-scaffold.md`
- `developer-docs/vzome-geometry-tutorial.md` (Section 10.8)

## What is implemented

- `mdisc ingest`: fixture-based ingestion, normalization, deduplication, and JSONL output.
- `mdisc generate`: deterministic candidate generation with schema validation and JSONL output.
- Full CLI surface for all documented commands, with explicit stage stubs for non-implemented stages.

## Quickstart

```bash
cd materials-discovery
uv sync --extra dev
uv run mdisc ingest --config configs/systems/al_cu_fe.yaml
uv run mdisc generate --config configs/systems/al_cu_fe.yaml --count 50
uv run pytest
uv run ruff check .
uv run mypy src
```

## Exit codes

- `0`: success
- `2`: input/config/path validation error
- `3`: stage is interface-complete but not implemented
