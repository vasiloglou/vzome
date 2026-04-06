# Phase 29 Research

## Summary

Phase 28 created a real lifecycle registry, but runtime default resolution is
still pinned to the old single-checkpoint behavior. The lowest-risk Phase 29
shape is:

1. extend checkpoint resolution so family-only lanes resolve the promoted
   member and family+checkpoint lanes remain explicit pins
2. record lifecycle selection metadata on the existing serving-identity seam
3. teach replay to reconstruct the recorded checkpoint identity when a family's
   promoted member changes later
4. update the committed adapted config and docs once the runtime/tests are
   already green

## Key Findings

### 1. The main runtime seam is still `resolve_checkpoint_lane(...)`

`materials-discovery/src/materials_discovery/llm/checkpoints.py`

- today it returns early when `lane_config.checkpoint_id is None`
- that means a lane with only `checkpoint_family` does not resolve the promoted
  checkpoint yet
- strict registration, adapter/provider/model validation, and lineage creation
  already live here, so the promoted-family runtime should extend this function
  rather than duplicating its checks elsewhere

### 2. One serving-identity builder fans out to most workflow surfaces

`materials-discovery/src/materials_discovery/llm/launch.py`
`materials-discovery/src/materials_discovery/llm/evaluate.py`
`materials-discovery/src/materials_discovery/cli.py`

- `build_serving_identity(...)` already feeds launch, evaluation, and serving
  benchmark flows
- `_resolve_llm_serving_config(...)` in the CLI uses the same lane resolution
  path for manual `llm-generate`
- adding lifecycle selection metadata there keeps the changes centralized and
  automatically present in launch summaries, run manifests, and benchmark smoke
  output

### 3. Replay currently re-resolves "today's lane", which is wrong after promotion changes

`materials-discovery/src/materials_discovery/llm/replay.py`

- `build_replay_serving_identity(...)` currently resolves the current lane from
  the current config and compares it to the recorded serving identity
- if a lane becomes family-managed and the promoted checkpoint changes after a
  launch, replay would drift or fail even though the recorded checkpoint should
  still be reproducible
- Phase 29 needs a replay-only path that takes the current lane shape but pins
  the recorded checkpoint id inside the recorded family before validating hard
  identity

### 4. Downstream comparison artifacts already have room for lifecycle identity

`materials-discovery/src/materials_discovery/llm/schema.py`
`materials-discovery/src/materials_discovery/llm/compare.py`

- `LlmServingIdentity` already flows into run manifests, launch summaries,
  replay bundles, outcome snapshots, and compare output
- `compare.py` summary lines currently print only lane name and lane source
- adding explicit checkpoint selection metadata there will satisfy the
  requirement that operators can explain which checkpoint actually ran after
  promotions change

### 5. The committed adapted config is still Phase-28 style

`materials-discovery/configs/systems/al_cu_fe_llm_adapted.yaml`

- the main adapted lane still hard-pins `checkpoint_id:
  ckpt-al-cu-fe-zomic-adapted`
- that proves the old one-checkpoint path, but it does not prove a promoted
  family default yet
- a good Phase 29 proof is to move that config to `checkpoint_family:
  adapted-al-cu-fe` while keeping a pinned example for explicit checkpoint
  choice and leaving `al_cu_fe_llm_local.yaml` as the rollback baseline

## Implementation Direction

- Add an internal "resolved checkpoint binding" helper in `llm/checkpoints.py`
  so call sites can keep using the old two-value API where needed while
  `build_serving_identity(...)` gets richer lifecycle metadata.
- Treat new execution differently from replay:
  - new execution may resolve only active promoted/candidate members
  - replay may reconstruct a retired member when the recorded lineage and
    fingerprint still match
- Use the existing committed lifecycle registry and action artifacts as the
  source of truth; do not introduce another runtime state file.

## Risks to Guard

- silent fallback from a family with no promoted member back to the baseline
  backend would hide lifecycle mistakes
- allowing new execution to pin retired checkpoints would undermine the
  retirement contract
- replay must allow transport/path drift but still reject true model or
  fingerprint drift
- config changes to the committed adapted lane must land only with regression
  coverage, because several real-mode and CLI tests assert on that file today
