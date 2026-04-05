---
phase: 28
slug: checkpoint-lifecycle-and-promotion-contracts
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-05
---

# Phase 28 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_llm_replay_core.py tests/test_cli.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~45-240 seconds depending on focused slice vs full suite |

---

## Sampling Rate

- **After Wave 1 schema/storage work:** Run `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_checkpoint_registry.py -x -v`
- **After Wave 2 lifecycle action and CLI work:** Run `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py tests/test_llm_checkpoint_cli.py tests/test_cli.py -x -v`
- **After Wave 3 compatibility/docs work:** Run `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_checkpoint_cli.py tests/test_cli.py -x -v`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 28-01-01 | 01 | 1 | LLM-23, OPS-13 | schema/unit | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py -x -v` | ✅ | ⬜ pending |
| 28-01-02 | 01 | 1 | LLM-23, OPS-13 | storage/unit | `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py -x -v` | ✅ | ⬜ pending |
| 28-02-01 | 02 | 2 | LLM-23, OPS-13 | registry/core | `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_registry.py -x -v` | ✅ | ⬜ pending |
| 28-02-02 | 02 | 2 | OPS-13 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_cli.py tests/test_cli.py -x -v` | ✅ | ⬜ pending |
| 28-03-01 | 03 | 3 | LLM-23, OPS-13 | compatibility/replay | `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_checkpoint_registry.py -x -v` | ✅ | ⬜ pending |
| 28-03-02 | 03 | 3 | OPS-13 | docs/CLI regression | `cd materials-discovery && uv run pytest tests/test_llm_checkpoint_cli.py tests/test_cli.py -x -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_llm_launch_schema.py` — extend config coverage for checkpoint-family selection and additive lifecycle models without breaking `checkpoint_id`-only lanes
- [ ] `materials-discovery/tests/test_llm_checkpoint_registry.py` — cover lifecycle index writes, promotion evidence references, stale/conflicting state rejection, and retirement semantics
- [ ] `materials-discovery/tests/test_llm_checkpoint_cli.py` — cover file-backed lifecycle action commands and clear operator-facing failure messages
- [ ] `materials-discovery/tests/test_llm_replay_core.py` — prove retired checkpoints remain replayable and lifecycle artifacts do not weaken hard fingerprint identity
- [ ] `materials-discovery/tests/test_cli.py` — cover repo-level command wiring for new lifecycle action commands
- [ ] All lifecycle tests must remain offline and deterministic; no live model server or checkpoint bytes are required in CI
- [ ] Any Phase 28 execution that changes `materials-discovery/` must update `materials-discovery/Progress.md` per repo policy

*Existing pytest infrastructure covers the repo. Wave 0 is about lifecycle-contract coverage, not tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Promotion artifacts are auditable | OPS-13 | Structural validation can still produce hard-to-read evidence references | Promote one checkpoint from a committed spec and inspect the stored artifact for checkpoint family, chosen member, evidence paths, and stale-write guard details |
| Retirement preserves history without staying implicitly selectable | LLM-23 | The policy boundary is partly operator-facing, not just structural | Retire a non-default checkpoint and confirm the registry excludes it from promoted/default selection while replay-facing registration artifacts remain intact |
| Phase boundary remains honest | OPS-13 | This phase should not overclaim workflow integration before Phase 29 | Read the updated docs and confirm they describe lifecycle contracts and diagnostics, but still defer promoted default execution through generation/launch/replay to Phase 29 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all new Phase 28 seams
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 240s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
