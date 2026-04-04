# Architecture Research: v1.1 Closed-Loop LLM Campaign MVP

## Existing integration points

- `materials-discovery/src/materials_discovery/llm/`
  Already owns:
  - eval sets
  - prompting
  - generation
  - evaluation
  - acceptance packs
  - dry-run suggestions
- `materials-discovery/src/materials_discovery/active_learning/`
  Already owns batch-oriented feedback concepts and should remain the reference
  for feedback-loop semantics.
- `materials-discovery/src/materials_discovery/common/schema.py`
  Already hosts many cross-cutting typed contracts.
- `materials-discovery/src/materials_discovery/cli.py`
  Must remain the operator entrypoint for new commands.

## Recommended integration approach

### 1. Campaign contract first

Add typed models for:
- campaign proposal
- approval decision
- campaign spec
- campaign launch summary
- replay/comparison summary

These should be additive, not disruptive to existing LLM run contracts.

### 2. Execution bridge second

Bridge approved campaign specs into `llm-generate` by:
- resolving the selected proposal actions into standard generation config
- recording the source acceptance pack and approval lineage
- writing campaign manifests alongside existing LLM run artifacts

### 3. Replay and comparison third

Compare campaign results against:
- the originating acceptance pack
- the originating eval set
- prior benchmark lane artifacts
- downstream screen/evaluate/report summaries

## Suggested build order

1. Campaign schema and approval-state design
2. CLI proposal -> approval -> launch flow
3. Replay/comparison and operator docs

## Boundaries to preserve

- No direct mutation of the active-learning loop without operator intent.
- No replacement of `llm-generate`; campaign execution should be a controlled
  wrapper over it.
- No provider-specific logic baked into campaign contracts.
