# Phase 25: Zomic Checkpoint Artifact and Lineage Contracts

**Gathered:** 2026-04-05  
**Mode:** Autonomous defaults from the v1.3 roadmap

## Phase Boundary

Treat one Zomic-adapted local checkpoint as a first-class serving lane without
inventing a second runtime or a side-channel outside the current config and
artifact surface.

## Locked Decisions

- Registration is file-backed under `data/llm_checkpoints/{checkpoint_id}/`.
- The existing serving-lane contract remains authoritative; adapted
  checkpoints extend that contract rather than replacing it.
- Backward compatibility matters because Phase 19/20 already use
  `checkpoint_id` as lightweight metadata on older local and specialist lanes.
- Strict adapted-checkpoint enforcement is opt-in through
  `require_checkpoint_registration: true`.

## Success Shape

- Operators can register an adapted checkpoint with pinned lineage.
- Generation, launch, replay, and benchmark surfaces can reuse that
  registration deterministically.
- Missing lineage inputs or incompatible lane identity fail early and clearly.
