---
phase: 23
slug: phase-20-verification-audit-closure
status: automated_complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
---

# Phase 23 — Validation Strategy

> Per-phase validation contract for closing the Phase 20 audit proof gap.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run python -m pytest tests/test_llm_evaluate_schema.py tests/test_llm_evaluate_cli.py tests/test_llm_compare_core.py tests/test_llm_compare_cli.py tests/test_llm_campaign_lineage.py tests/test_llm_replay_core.py tests/test_report.py tests/test_real_mode_pipeline.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run python -m pytest` |
| **Doc hygiene command** | `git diff --check` |
| **Estimated runtime** | ~30-300 seconds depending on focused rerun vs existing summary evidence |

---

## Sampling Rate

- **After evidence refresh work:** Run the focused Phase 20 pytest command
  above.
- **After verification and traceability doc work:** Run `git diff --check`.
- **Before Phase 23 closeout:** Ensure the focused rerun is green and recorded
  in the proof artifacts.
- **Max feedback latency:** 300 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 23-01-01 | 01 | 1 | LLM-15, LLM-16, OPS-09 | focused regression | `cd materials-discovery && uv run python -m pytest tests/test_llm_evaluate_schema.py tests/test_llm_evaluate_cli.py tests/test_llm_compare_core.py tests/test_llm_compare_cli.py tests/test_llm_campaign_lineage.py tests/test_llm_replay_core.py tests/test_report.py tests/test_real_mode_pipeline.py -x -v` | ✅ | ✅ green |
| 23-01-02 | 01 | 1 | LLM-15, LLM-16, OPS-09 | doc consistency | `git diff --check` | ✅ | ✅ green |
| 23-02-01 | 02 | 2 | LLM-15, LLM-16 | proof matrix | `git diff --check` | ✅ | ✅ green |
| 23-02-02 | 02 | 2 | OPS-09 | proof matrix | `git diff --check` | ✅ | ✅ green |
| 23-03-01 | 03 | 3 | LLM-15, LLM-16, OPS-09 | traceability | `git diff --check` | ✅ | ✅ green |
| 23-03-02 | 03 | 3 | LLM-15, LLM-16, OPS-09 | state + self-closeout | `git diff --check` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `20-VERIFICATION.md` must exist by the end of execution
- [x] `20-VALIDATION.md` must stay synchronized with the final verification
  story
- [x] `REQUIREMENTS.md` should only move `LLM-15`, `LLM-16`, and `OPS-09` back
  to complete after proof exists
- [x] No `materials-discovery/` files should change unless the evidence rerun
  exposes a real mismatch
- [x] If `materials-discovery/` changes unexpectedly, `materials-discovery/Progress.md`
  must be updated per `AGENTS.md`
- [x] The focused pytest surface must stay offline and deterministic
- [x] Phase 23 should finalize its own validation state and leave behind a
  closure verdict so it does not create fresh documentary debt

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The specialized lane role is explained honestly in the final proof chain | LLM-15 | Audit readability matters beyond test pass/fail | Read `20-VERIFICATION.md` and confirm it makes the evaluation-primary role explicit rather than implying mature direct Zomic generation |
| Serving lineage remains understandable to a human auditor | OPS-09 | Typed provenance can still be hard to interpret | Confirm the final verification text distinguishes generation-lane lineage from evaluation-lane lineage clearly |

---

## Evidence Refresh

- Focused rerun completed during Phase 23:
  - `cd materials-discovery && uv run python -m pytest tests/test_llm_evaluate_schema.py tests/test_llm_evaluate_cli.py tests/test_llm_compare_core.py tests/test_llm_compare_cli.py tests/test_llm_campaign_lineage.py tests/test_llm_replay_core.py tests/test_report.py tests/test_real_mode_pipeline.py -x -v`
  - Result: `53 passed in 24.23s`
- Shipped full-suite evidence retained from `20-03-SUMMARY.md`:
  - `cd materials-discovery && uv run python -m pytest`
  - Result: `393 passed, 3 skipped, 1 warning in 29.32s`
- Retroactive finalization note:
  - This validation artifact was finalized by Phase 23 to close the v1.2
    milestone audit gap after the specialized-lane workflow had already
    shipped.

---

## Validation Sign-Off

- [x] All tasks have focused automated verification or doc-hygiene checks
- [x] Sampling continuity: no 2 consecutive evidence updates without either
  pytest or doc-hygiene verification
- [x] Wave 0 captures the actual Phase 20 audit gap, not unrelated
  implementation work
- [x] No watch-mode or long-running background commands are required
- [x] Feedback latency < 300s
- [x] `nyquist_compliant: true` set in frontmatter by the end of execution

**Approval:** automated verification complete
