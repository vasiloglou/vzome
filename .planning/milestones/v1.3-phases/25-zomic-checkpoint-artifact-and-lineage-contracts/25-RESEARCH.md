# Phase 25 Research

## Existing Code Surface

- Phase 19 already added lane-aware local serving, `LlmServingIdentity`, and
  replay-aware serving metadata.
- Phase 20 already uses `checkpoint_id` for older specialist metadata, so the
  new contract cannot assume every checkpoint id already has a registration
  artifact.
- Phase 21 already benchmarks lanes through the existing launch/evaluate
  machinery, so the checkpoint contract should feed that surface rather than
  fork it.

## Key Constraint

The repository does not ship checkpoint weights. The artifact contract must
therefore capture lineage, identity, and reproducibility without pretending the
checkpoint bytes live in version control.
