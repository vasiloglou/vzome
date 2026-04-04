---
phase: 13
slug: phase-10-verification-and-governance-audit-closure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for closing the Phase 10 audit proof gap.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_campaign_schema.py tests/test_llm_campaign_storage.py tests/test_llm_suggest_core.py tests/test_llm_suggest_cli.py tests/test_llm_campaign_spec.py tests/test_llm_approve_cli.py tests/test_cli.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Doc hygiene command** | `git diff --check` |
| **Estimated runtime** | ~30-180 seconds depending on focused rerun vs full suite |

---

## Sampling Rate

- **After evidence refresh work:** Run the focused Phase 10 governance pytest
  command above.
- **After verification/traceability doc work:** Run `git diff --check`.
- **Before Phase 13 closeout:** Ensure the focused governance pytest command is
  green and recorded in the proof artifacts.
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | LLM-06, OPS-05 | focused regression | `cd materials-discovery && uv run pytest tests/test_llm_campaign_schema.py tests/test_llm_campaign_storage.py tests/test_llm_suggest_core.py tests/test_llm_suggest_cli.py tests/test_llm_campaign_spec.py tests/test_llm_approve_cli.py tests/test_cli.py -x -v` | ✅ | ⬜ pending |
| 13-01-02 | 01 | 1 | LLM-06, OPS-05 | doc consistency | `git diff --check` | ✅ | ⬜ pending |
| 13-02-01 | 02 | 2 | LLM-06 | proof matrix | `git diff --check` | ✅ | ⬜ pending |
| 13-02-02 | 02 | 2 | OPS-05 | proof matrix | `git diff --check` | ✅ | ⬜ pending |
| 13-03-01 | 03 | 3 | LLM-06, OPS-05 | traceability | `git diff --check` | ✅ | ⬜ pending |
| 13-03-02 | 03 | 3 | LLM-06, OPS-05 | state handoff | `git diff --check` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `10-VERIFICATION.md` does not exist yet and must be created by this phase
- [ ] `10-VALIDATION.md` must move from `status: draft` to an audit-ready state
- [ ] `REQUIREMENTS.md` currently maps `LLM-06` and `OPS-05` to Phase 13 as
  pending closure work; those rows should only flip after proof exists
- [ ] Any Phase 13 execution that unexpectedly edits `materials-discovery/`
  must also update `materials-discovery/Progress.md` per `AGENTS.md`
- [ ] Focused pytest evidence should stay offline/deterministic and must not
  require live provider access
- [ ] The milestone audit should not be rerun until Phases 14 and 15 also close
  their proof gaps

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| The final proof chain is understandable to a human auditor | LLM-06, OPS-05 | Audit readability is not just a schema property | Read `10-VERIFICATION.md` after drafting and confirm it can be followed from requirement -> summary -> tests -> docs without side-channel knowledge |
| The governance boundary still reads as a real operator boundary | OPS-05 | The CLI/tests can be green while the proof narrative still feels muddy | Confirm the final verification/report text makes it obvious that `llm-suggest` is dry-run and `llm-approve` materializes artifacts without launching |

---

## Validation Sign-Off

- [ ] All tasks have focused automated verification or doc-hygiene checks
- [ ] Sampling continuity: no 2 consecutive evidence updates without either pytest or doc-hygiene verification
- [ ] Wave 0 captures the actual Phase 10 audit gap, not unrelated implementation work
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter by the end of execution

**Approval:** pending
