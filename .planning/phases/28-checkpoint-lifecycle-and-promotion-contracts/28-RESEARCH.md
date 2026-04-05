# Phase 28 Research

## Existing Code Surface

- `v1.3` already established file-backed checkpoint registration in
  `data/llm_checkpoints/{checkpoint_id}/registration.json` through
  `materials-discovery/src/materials_discovery/llm/checkpoints.py` and
  `materials-discovery/src/materials_discovery/llm/storage.py`.
- `LlmModelLaneConfig` already carries `checkpoint_id` and
  `require_checkpoint_registration`, but there is no checkpoint-family or
  promoted-default concept yet.
- Launch, replay, and benchmark flows already depend on checkpoint fingerprint
  and typed checkpoint lineage, so lifecycle state cannot weaken replay
  identity or remove historical auditability.
- The CLI currently supports `llm-register-checkpoint`, but no lifecycle action
  surface exists for listing, promoting, or retiring checkpoints.

## Key Constraints

- The hybrid lifecycle contract must remain additive to the shipped `v1.3`
  one-checkpoint workflow; older `checkpoint_id`-only lanes and artifacts still
  need to load.
- Config must stay authoritative for which adapted-checkpoint family a lane can
  use, while the new lifecycle registry resolves the promoted member for that
  family.
- Retired checkpoints must never be chosen implicitly for new work, but they
  must remain replayable and auditable.
- Promotion needs typed evidence references now, but hard scoring thresholds are
  intentionally deferred to Phase 30.
