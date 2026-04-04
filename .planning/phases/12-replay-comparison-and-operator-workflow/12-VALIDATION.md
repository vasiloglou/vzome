---
phase: 12
slug: replay-comparison-and-operator-workflow
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py tests/test_llm_replay_cli.py tests/test_llm_compare_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~60-240 seconds depending on focused wave vs full suite |

---

## Sampling Rate

- **After every task commit:** Run the smallest focused Phase 12 command that
  matches the files changed.
- **After every plan wave:** Run that wave's targeted pytest command.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | LLM-09, LLM-11 | schema/storage | `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py -x -v` | ⬜ | ⬜ pending |
| 12-01-02 | 01 | 1 | LLM-09, LLM-11 | core/unit | `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_compare_core.py -x -v` | ⬜ | ⬜ pending |
| 12-02-01 | 02 | 2 | LLM-09, OPS-07 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_replay_cli.py tests/test_cli.py -x -v` | ⬜ | ⬜ pending |
| 12-02-02 | 02 | 2 | LLM-11, OPS-07 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_compare_cli.py tests/test_cli.py -x -v` | ⬜ | ⬜ pending |
| 12-03-01 | 03 | 3 | LLM-09, LLM-11 | E2E/integration | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "llm_replay or llm_compare or campaign" -x -v` | ✅ | ⬜ pending |
| 12-03-02 | 03 | 3 | OPS-07 | docs/regression | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "llm_replay or llm_compare or campaign" -x -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_llm_replay_core.py` — launch-bundle,
  strict replay, and drift-recording coverage
- [ ] `materials-discovery/tests/test_llm_compare_core.py` — outcome snapshot,
  acceptance-pack baseline, and prior-launch selection coverage
- [ ] `materials-discovery/tests/test_llm_replay_cli.py` — replay command
  coverage for success, missing bundle pieces, and no-override behavior
- [ ] `materials-discovery/tests/test_llm_compare_cli.py` — compare command
  coverage for JSON artifact writing and human-readable summaries
- [ ] Any Phase 12 execution that changes `materials-discovery/` must update
  `materials-discovery/Progress.md` per repo policy
- [ ] Replay and compare tests must remain offline and deterministic by default;
  no live providers or Java-dependent exports
- [ ] Any replay tests that exercise config drift must assert that the drift is
  recorded but does not silently change the effective launch inputs
- [ ] Any comparison tests that rely on prior launches must use committed or
  synthetic launch bundles rather than mutable current workspace artifacts
- [ ] Any comparison snapshot tests must assert explicit missing-metric markers
  when downstream artifacts are absent

*Existing pytest infrastructure covers the repo. Wave 0 is about new replay,
comparison, and operator-workflow coverage rather than tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Replay summary is understandable to an operator | LLM-09, OPS-07 | Structural tests can pass while operator comprehension stays weak | Run `mdisc llm-replay --launch-summary ...` on a mock launch and inspect the emitted JSON plus stderr/stdout summary for source launch identity, replay launch identity, current/source config-hash visibility, and replay-safe output paths |
| Compare output highlights the right signal | LLM-11 | The artifact can be correct but still not useful for decision-making | Run `mdisc llm-compare --launch-summary ...` and confirm the terminal output calls out acceptance-pack deltas, prior-launch availability, and the top improvements/regressions without requiring notebook work |
| Runbook supports the whole operator loop | OPS-07 | Workflow safety is partly documentation quality | Follow the updated runbook from `llm-suggest` through `llm-compare` using the mock configs and confirm the command sequence is complete and internally consistent |

---

## Validation Sign-Off

- [ ] All tasks have focused automated verify commands or explicit Wave 0 prerequisites
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all new Phase 12 seams
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 240s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

