---
phase: 15
slug: phase-12-replay-and-operator-workflow-audit-closure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for closing the Phase 12 audit proof gap.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick core command** | `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py -x -v` |
| **Quick CLI command** | `cd materials-discovery && uv run pytest tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py tests/test_cli.py -x -v` |
| **Existing workflow evidence** | `.planning/phases/12-replay-comparison-and-operator-workflow/12-03-SUMMARY.md` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Doc hygiene command** | `git diff --check` |
| **Estimated runtime** | ~30-180 seconds depending on focused reruns vs summary/verification drafting |

---

## Sampling Rate

- **After summary-chain refresh work:** Run the focused core replay/compare
  pytest command and the focused CLI/operator command above.
- **After verification/traceability doc work:** Run `git diff --check`.
- **Before Phase 15 closeout:** Ensure the fresh core and CLI reruns are green
  and that `12-VERIFICATION.md` aligns with the already-green
  `12-VALIDATION.md` and `12-03-SUMMARY.md`.
- **Before Phase 15 closeout:** Do not rerun the milestone audit yet; the phase
  should only hand off to that audit.
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | LLM-09, LLM-11 | focused regression | `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py -x -v` | ✅ | ⬜ pending |
| 15-01-02 | 01 | 1 | LLM-09, LLM-11, OPS-07 | focused regression | `cd materials-discovery && uv run pytest tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py tests/test_cli.py -x -v` | ✅ | ⬜ pending |
| 15-01-03 | 01 | 1 | LLM-09, LLM-11, OPS-07 | doc consistency | `git diff --check` | ✅ | ⬜ pending |
| 15-02-01 | 02 | 2 | LLM-09, LLM-11 | proof matrix | `git diff --check` | ✅ | ⬜ pending |
| 15-02-02 | 02 | 2 | OPS-07 | proof matrix | `git diff --check` | ✅ | ⬜ pending |
| 15-03-01 | 03 | 3 | LLM-09, LLM-11, OPS-07 | traceability | `git diff --check` | ✅ | ⬜ pending |
| 15-03-02 | 03 | 3 | LLM-09, LLM-11, OPS-07 | state handoff | `git diff --check` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `12-VERIFICATION.md` does not exist yet and must be created by this phase
- [ ] `12-01-SUMMARY.md` and `12-02-SUMMARY.md` do not exist yet and must be
  created by this phase
- [ ] `12-VALIDATION.md` is already green and should only be edited if the new
  summary chain reveals a real evidence-sync need
- [ ] `REQUIREMENTS.md` currently maps `LLM-09`, `LLM-11`, and `OPS-07` to
  Phase 15 as pending closure work; those rows should only flip after proof exists
- [ ] Any Phase 15 execution that unexpectedly edits `materials-discovery/`
  must also update `materials-discovery/Progress.md` per `AGENTS.md`
- [ ] Focused reruns should stay offline/deterministic and must not require
  live provider access
- [ ] The milestone audit should not be rerun until Phase 15 closes and state
  explicitly hands off to `gsd-audit-milestone`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Replay proof reads as reproducibility rather than mere file reopening | LLM-09 | Auditability depends on how the proof is narrated | Read `12-VERIFICATION.md` and confirm it makes clear that replay is driven by recorded launch artifacts with campaign-spec provenance context |
| Comparison proof makes the dual-baseline operator story obvious | LLM-11 | JSON outputs can exist while the workflow story is still muddy | Confirm the final verification/report text clearly explains acceptance-pack and prior-launch baselines |
| Runbook evidence feels like a usable operator workflow, not just docs presence | OPS-07 | Operator safety is partly a workflow/readability claim | Read the runbook and verification sections together and confirm they show dry-run, approval, launch, replay, compare, and interpretation as one safe loop |

---

## Validation Sign-Off

- [ ] All tasks have focused automated verification or doc-hygiene checks
- [ ] Sampling continuity: no 2 consecutive evidence updates without either pytest or doc-hygiene verification
- [ ] Wave 0 captures the actual Phase 12 audit gap, not unrelated implementation work
- [ ] `12-VERIFICATION.md`, the new summary chain, and `12-VALIDATION.md` tell the same success or blocked story
- [ ] Phase 15 itself leaves a finalized validation artifact and the standard
  per-plan execution summaries expected by the workflow
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter by the end of execution

**Approval:** pending
