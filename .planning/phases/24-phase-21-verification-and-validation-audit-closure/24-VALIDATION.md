---
phase: 24
slug: phase-21-verification-and-validation-audit-closure
status: automated_complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
---

# Phase 24 — Validation Strategy

> Per-phase validation contract for closing the Phase 21 audit proof gap.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Doc hygiene command** | `git diff --check` |
| **Estimated runtime** | ~30-300 seconds depending on focused rerun vs existing summary evidence |

---

## Sampling Rate

- **After evidence refresh work:** Run the focused Phase 21 pytest command
  above.
- **After verification and traceability doc work:** Run `git diff --check`.
- **Before Phase 24 closeout:** Ensure the focused rerun is green and recorded
  in the proof artifacts.
- **Max feedback latency:** 300 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 24-01-01 | 01 | 1 | LLM-17, OPS-10 | focused regression | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v` | ✅ | ✅ green |
| 24-01-02 | 01 | 1 | LLM-17, OPS-10 | doc consistency | `git diff --check` | ✅ | ✅ green |
| 24-02-01 | 02 | 2 | LLM-17 | proof matrix | `git diff --check` | ✅ | ✅ green |
| 24-02-02 | 02 | 2 | OPS-10 | proof matrix | `git diff --check` | ✅ | ✅ green |
| 24-03-01 | 03 | 3 | LLM-17, OPS-10 | traceability | `git diff --check` | ✅ | ✅ green |
| 24-03-02 | 03 | 3 | LLM-17, OPS-10 | state + self-closeout | `git diff --check` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `21-VERIFICATION.md` must exist by the end of execution
- [x] `21-VALIDATION.md` must move from `status: draft` to an audit-ready
  state
- [x] `REQUIREMENTS.md` should only move `LLM-17` and `OPS-10` back to complete
  after proof exists
- [x] No `materials-discovery/` files should change unless the evidence rerun
  exposes a real mismatch
- [x] If `materials-discovery/` changes unexpectedly, `materials-discovery/Progress.md`
  must be updated per `AGENTS.md`
- [x] The focused pytest surface must stay offline and deterministic
- [x] Phase 24 should finalize its own validation state and leave behind a
  closure verdict so it does not create fresh documentary debt

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The final proof chain is understandable to a human auditor | LLM-17, OPS-10 | Audit readability is not just a schema property | Read `21-VERIFICATION.md` after drafting and confirm it can be followed from requirement -> summary -> tests -> docs without side-channel knowledge |
| Benchmark and runbook guidance still read as an operator workflow | OPS-10 | The tests can be green while the narrative still feels muddy | Confirm the verification text makes smoke-first execution, explicit fallback, and tradeoff interpretation obvious |

---

## Evidence Refresh

- Focused rerun completed during Phase 24:
  - `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v`
  - Result: `40 passed in 26.84s`
- Shipped full-suite evidence retained from `21-03-SUMMARY.md`:
  - `cd materials-discovery && uv run pytest`
  - Result: `410 passed, 3 skipped, 1 warning in 37.07s`
- Retroactive finalization note:
  - This validation artifact was finalized by Phase 24 to close the v1.2
    milestone audit gap after the benchmark workflow had already shipped.

---

## Validation Sign-Off

- [x] All tasks have focused automated verification or doc-hygiene checks
- [x] Sampling continuity: no 2 consecutive evidence updates without either
  pytest or doc-hygiene verification
- [x] Wave 0 captures the actual Phase 21 audit gap, not unrelated
  implementation work
- [x] No watch-mode or long-running background commands are required
- [x] Feedback latency < 300s
- [x] `nyquist_compliant: true` set in frontmatter by the end of execution

**Approval:** automated verification complete
