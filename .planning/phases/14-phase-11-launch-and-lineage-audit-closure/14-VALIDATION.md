---
phase: 14
slug: phase-11-launch-and-lineage-audit-closure
status: automated_complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-04
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for closing the Phase 11 audit proof gap.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_launch_core.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_cli.py tests/test_llm_campaign_lineage.py tests/test_report.py -x -v` |
| **Focused downstream command** | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "campaign or llm_launch" -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Doc hygiene command** | `git diff --check` |
| **Estimated runtime** | ~45-240 seconds depending on focused reruns vs full suite |

---

## Sampling Rate

- **After evidence refresh work:** Run the focused Phase 11 launch/lineage
  pytest slices above.
- **After verification/traceability doc work:** Run `git diff --check`.
- **Before Phase 14 closeout:** Ensure both the focused launch/lineage rerun and
  the focused downstream compatibility rerun are green and recorded.
- **Before Phase 14 closeout:** Ensure the final `11-VERIFICATION.md` caveats
  do not contradict the final state recorded in `11-VALIDATION.md`.
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | LLM-08, LLM-10 | focused regression | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_launch_core.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_cli.py tests/test_llm_campaign_lineage.py tests/test_report.py -x -v` | ✅ | ✅ green |
| 14-01-02 | 01 | 1 | LLM-10, OPS-06 | downstream compatibility | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "campaign or llm_launch" -x -v` | ✅ | ✅ green |
| 14-01-03 | 01 | 1 | LLM-08, LLM-10, OPS-06 | doc consistency | `git diff --check` | ✅ | ✅ green |
| 14-02-01 | 02 | 2 | LLM-08 | proof matrix | `git diff --check` | ✅ | ✅ green |
| 14-02-02 | 02 | 2 | LLM-10, OPS-06 | proof matrix | `git diff --check` | ✅ | ✅ green |
| 14-03-01 | 03 | 3 | LLM-08, LLM-10, OPS-06 | traceability | `git diff --check` | ✅ | ✅ green |
| 14-03-02 | 03 | 3 | LLM-08, LLM-10, OPS-06 | state handoff | `git diff --check` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `11-VERIFICATION.md` now exists and closes the Phase 11 proof gap
- [x] `11-VALIDATION.md` moved from `status: draft` to an audit-ready state
- [x] `11-VALIDATION.md` includes a retroactive-finalization note
- [x] `REQUIREMENTS.md` only flipped after proof existed
- [x] No `materials-discovery/` files changed during Phase 14 execution, so
  `materials-discovery/Progress.md` did not require an update
- [x] Focused reruns stayed offline/deterministic and required no live provider
  access
- [x] The milestone audit stayed deferred until the later closure work completed
- [x] This validation artifact was finalized retroactively in Phase 17 to close
  the remaining documentary tech debt on Phase 14 itself

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Launch summary remains understandable to an operator | LLM-08 | Auditability is not purely structural | Inspect `launch_summary.json` and `resolved_launch.json` from a known mock launch and confirm the resolved lane, config-hash context, and artifact pointers are easy to follow |
| Downstream lineage still reads as a clean additive trail | OPS-06 | Manifests can be structurally correct while still confusing | Follow one launched candidate through downstream manifests and confirm the lineage path back to approval/spec artifacts remains readable |
| Manual `llm-generate` still feels unchanged | LLM-10 | Compatibility is partly an operator contract, not just a type contract | Compare the documented baseline manual path against the Phase 11 docs and ensure the audit narrative makes that compatibility explicit |

---

## Validation Sign-Off

- [x] All tasks have focused automated verification or doc-hygiene checks
- [x] Sampling continuity: no 2 consecutive evidence updates without either pytest or doc-hygiene verification
- [x] Wave 0 captures the actual Phase 11 audit gap, not unrelated implementation work
- [x] `11-VALIDATION.md` and `11-VERIFICATION.md` tell the same success story
- [x] No watch-mode or long-running background commands are required
- [x] Feedback latency < 240s
- [x] `nyquist_compliant: true` set in frontmatter by the end of execution

**Approval:** automated verification complete
