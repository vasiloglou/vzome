# Phase 26 Research

## Existing Seams Reused

- `build_serving_identity(...)` already records lane-aware identity.
- `llm-launch` and `llm-replay` already preserve serving metadata across the
  campaign workflow.
- `llm-serving-benchmark` already compares generation targets on a shared
  acceptance-pack context.

## New Requirement

The adapted lane must look operationally real, not just endpoint-selectable.
That means committed configs, replay-safe checkpoint identity, and one offline
workflow proof that exercises launch and compare against the adapted lane.
