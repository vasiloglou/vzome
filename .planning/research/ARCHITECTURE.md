# Architecture Research: v1.3 Zomic-Native Local Checkpoint MVP

## Integration Points

- `materials_discovery/common/schema.py`
- `materials_discovery/llm/schema.py`
- `materials_discovery/llm/runtime.py`
- `materials_discovery/llm/generate.py`
- `materials_discovery/llm/launch.py`
- `materials_discovery/llm/replay.py`
- `materials_discovery/llm/serving_benchmark.py`
- serving config files under `configs/`

## New vs Modified

- new: checkpoint metadata and storage contract
- new: registration and compatibility validation helpers
- modified: serving-lane resolution to understand adapted checkpoint identity
- modified: benchmark/report surfaces to compare adapted vs baseline local lanes

## Build Order

1. define checkpoint and lineage contracts
2. integrate one adapted checkpoint into local generation and campaign launch
3. benchmark adapted vs baseline and document rollback/operator workflow
