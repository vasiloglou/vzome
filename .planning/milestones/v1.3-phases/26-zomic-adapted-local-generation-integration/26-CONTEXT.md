# Phase 26: Zomic-Adapted Local Generation Integration

**Gathered:** 2026-04-05  
**Mode:** Autonomous defaults from the v1.3 roadmap

## Phase Boundary

Run one adapted checkpoint through the shipped generation and campaign workflow
without introducing a new artifact family or a checkpoint-only execution path.

## Locked Decisions

- Reuse the existing lane-aware `llm-generate` / `llm-launch` / `llm-replay`
  surfaces.
- Treat checkpoint fingerprint as hard replay identity.
- Keep rollback to the baseline local lane explicit and easy.
- Use committed example configs, but keep real checkpoint bytes external to the
  repository.
