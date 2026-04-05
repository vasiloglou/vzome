# Architecture Research: v1.2 Local and Specialized LLM Serving MVP

## Integration points

- `materials-discovery/src/materials_discovery/common/schema.py`
  for lane-aware serving config
- `materials-discovery/src/materials_discovery/llm/runtime.py`
  for adapter resolution and provider/local dispatch
- `materials-discovery/src/materials_discovery/llm/generate.py`
  for additive execution through the existing generation path
- `materials-discovery/src/materials_discovery/llm/launch.py`
  for campaign-spec resolution into serving overlays
- `materials-discovery/src/materials_discovery/llm/replay.py`
  and `materials-discovery/src/materials_discovery/llm/benchmark.py`
  for comparability across serving modes

## Preferred build order

1. Add local-serving contracts and diagnostics.
2. Make lane resolution real for manual and campaign-driven runs.
3. Integrate specialized materials lanes into at least one meaningful workflow
   role.
4. Add hosted/local/specialized comparison and operator runbook hardening.

## Architectural guardrails

- preserve `llm-generate` as the single generation engine
- preserve `llm-launch` and `llm-replay` as wrappers, not forks
- keep all new serving metadata additive in manifests and lineage payloads
- avoid coupling the milestone to one exact serving backend at the contract
  layer
