# Stack Research: v1.2 Local and Specialized LLM Serving MVP

## Existing base

- Python 3.11 workspace under `materials-discovery/`
- Typer CLI for operator entrypoints
- Pydantic contracts in `common/schema.py` and `llm/schema.py`
- file-backed manifests, run artifacts, and campaign lineage

## Needed additions

- an additive local-serving adapter in `materials_discovery/llm/runtime.py`
- config fields for local endpoint or model/checkpoint identity
- lane-aware resolution that can choose between `general_purpose` and
  `specialized_materials` without changing the CLI contract
- clearer runtime diagnostics for missing local dependencies, invalid endpoints,
  and unavailable checkpoints

## What not to add yet

- a new orchestration service
- a UI control plane
- training infrastructure as part of the serving milestone
- hard vendor lock-in at the contract level

## Practical guidance

- keep the serving seam provider-neutral in the contracts
- record actual runtime identity, not just an abstract lane name
- prefer additive adapter/runtime extension over a second inference stack
