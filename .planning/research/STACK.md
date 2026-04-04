# Stack Research: v1.1 Closed-Loop LLM Campaign MVP

## Current stable base

- `materials-discovery/` already provides the core runtime in Python 3.11.
- `cli.py` is the orchestration layer; there is no separate workflow engine.
- `llm/` already owns corpus, generation, evaluation, acceptance-pack, and
  dry-run suggestion logic.
- `active_learning/` already owns batch-oriented feedback concepts that the new
  campaign layer should reuse rather than replace.
- File-backed JSON/JSONL artifacts plus manifests are already the dominant
  contract surface across the repo.

## Recommended stack posture for this milestone

- Stay on the existing Python 3.11 + Typer + Pydantic stack.
- Keep the closed-loop workflow file-backed:
  - campaign specs
  - approval decisions
  - launch manifests
  - replay summaries
- Reuse the current `llm/` and `active_learning/` packages rather than adding a
  new orchestration subsystem.
- Reuse acceptance packs, eval sets, prompt artifacts, compile results, and
  downstream manifests as the campaign lineage backbone.

## Additions that are justified

- Typed campaign schema models in the existing schema layer.
- A small campaign runtime package or `llm/` submodule for:
  - proposal materialization
  - approval state transitions
  - launch planning
  - replay/comparison
- Operator CLI commands that remain explicit and composable.

## Additions to avoid in v1.1

- No persistent database requirement.
- No job queue or external scheduler unless proven necessary later.
- No local-model serving stack in this milestone.
- No fine-tuning infrastructure in this milestone.
- No autonomous mutation of the active-learning loop.

## Why this posture fits

The existing system already proves that file-backed artifacts and manifest-rich
CLI flows scale across ingest, discovery, and LLM surfaces. The next milestone
needs stronger control and reproducibility, not a new runtime model.
