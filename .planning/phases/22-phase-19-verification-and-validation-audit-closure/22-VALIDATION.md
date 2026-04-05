---
phase: 22
slug: phase-19-verification-and-validation-audit-closure
status: automated_complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
---

# Phase 22 — Validation Strategy

> Per-phase validation contract for closing the Phase 19 audit proof gap.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_runtime.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_core.py tests/test_llm_launch_cli.py tests/test_llm_replay_core.py tests/test_cli.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Doc hygiene command** | `git diff --check` |
| **Estimated runtime** | ~30-240 seconds depending on focused rerun vs existing summary evidence |

---

## Sampling Rate

- **After evidence refresh work:** Run the focused Phase 19 pytest command
  above.
- **After verification and traceability doc work:** Run `git diff --check`.
- **Before Phase 22 closeout:** Ensure the focused rerun is green and recorded
  in the proof artifacts.
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 22-01-01 | 01 | 1 | LLM-13, LLM-14, OPS-08 | focused regression | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_runtime.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_core.py tests/test_llm_launch_cli.py tests/test_llm_replay_core.py tests/test_cli.py -x -v` | ✅ | ✅ green |
| 22-01-02 | 01 | 1 | LLM-13, LLM-14, OPS-08 | doc consistency | `git diff --check` | ✅ | ✅ green |
| 22-02-01 | 02 | 2 | LLM-13, LLM-14 | proof matrix | `git diff --check` | ✅ | ✅ green |
| 22-02-02 | 02 | 2 | OPS-08 | proof matrix | `git diff --check` | ✅ | ✅ green |
| 22-03-01 | 03 | 3 | LLM-13, LLM-14, OPS-08 | traceability | `git diff --check` | ✅ | ✅ green |
| 22-03-02 | 03 | 3 | LLM-13, LLM-14, OPS-08 | state + self-closeout | `git diff --check` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `19-VERIFICATION.md` must exist by the end of execution
- [x] `19-VALIDATION.md` must move from `status: draft` to an audit-ready state
- [x] `REQUIREMENTS.md` should only move `LLM-13`, `LLM-14`, and `OPS-08` back
  to complete after proof exists
- [x] No `materials-discovery/` files should change unless the evidence rerun
  exposes a real mismatch
- [x] If `materials-discovery/` changes unexpectedly, `materials-discovery/Progress.md`
  must be updated per `AGENTS.md`
- [x] The focused pytest surface must stay offline and deterministic
- [x] Phase 22 should finalize its own validation state and leave behind a
  closure verdict so it does not create fresh documentary debt

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The final proof chain is understandable to a human auditor | LLM-13, LLM-14, OPS-08 | Audit readability is not just a schema property | Read `19-VERIFICATION.md` after drafting and confirm it can be followed from requirement -> summary -> tests -> docs without side-channel knowledge |
| The local-serving boundary still reads as an operator-facing runtime seam | OPS-08 | The tests can be green while the proof narrative still feels muddy | Confirm the verification text makes it obvious that local servers must already be running and that fallback is explicit rather than silent |

---

## Evidence Refresh

- Focused rerun completed during Phase 22:
  - `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_runtime.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_core.py tests/test_llm_launch_cli.py tests/test_llm_replay_core.py tests/test_cli.py -x -v`
  - Result: `70 passed in 1.17s`
- Shipped full-suite evidence retained from `19-03-SUMMARY.md`:
  - `cd materials-discovery && uv run pytest`
  - Result: `388 passed, 3 skipped, 1 warning in 64.27s`
- Retroactive finalization note:
  - This validation artifact was finalized by Phase 22 to close the v1.2
    milestone audit gap after the local-serving workflow had already shipped.

---

## Validation Sign-Off

- [x] All tasks have focused automated verification or doc-hygiene checks
- [x] Sampling continuity: no 2 consecutive evidence updates without either
  pytest or doc-hygiene verification
- [x] Wave 0 captures the actual Phase 19 audit gap, not unrelated
  implementation work
- [x] No watch-mode or long-running background commands are required
- [x] Feedback latency < 240s
- [x] `nyquist_compliant: true` set in frontmatter by the end of execution

**Approval:** automated verification complete
