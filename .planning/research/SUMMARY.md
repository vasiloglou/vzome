# Research Summary: v1.3 Zomic-Native Local Checkpoint MVP

## Milestone direction

The strongest next milestone after `v1.2` is to make at least one
Zomic-adapted local checkpoint a real workflow artifact rather than leaving
adaptation outside the governed serving ladder.

## Stack additions

- No new top-level platform is required.
- Stay with Python 3.11, Typer, Pydantic, and file-backed manifests.
- Extend the existing local-serving lane surface with checkpoint registration,
  lineage, and compatibility checks.

## Feature table stakes

- adapted checkpoint registration with auditable lineage
- deterministic checkpoint-aware serving identity
- adapted-checkpoint execution through `llm-generate` and campaign launch
- adapted-vs-baseline benchmark workflow on one shared context
- operator-visible smoke tests and rollback guidance

## Architecture guidance

- Extend the existing `llm/schema.py`, `llm/runtime.py`, `llm/generate.py`,
  `llm/launch.py`, `llm/replay.py`, and serving-benchmark surfaces rather than
  creating a parallel checkpoint pipeline.
- Keep adapted checkpoints additive to the current lane model.
- Treat checkpoint metadata and lineage as first-class storage contracts, not
  as notes hidden in config comments.

## Watch out for

- weak checkpoint lineage that loses base-model or corpus/eval provenance
- hidden drift between adapted and baseline local lanes
- overstating Zomic-native improvement without a shared benchmark context
- coupling milestone scope to full automated training orchestration too early
- rollback paths that exist in docs but not in actual lane selection behavior

## Recommended scope boundary

Ship one credible adapted-checkpoint MVP now. Defer large-scale training
automation, automated checkpoint promotion, and autonomous campaign execution
until operators can compare adapted checkpoints confidently inside the shipped
workflow.
