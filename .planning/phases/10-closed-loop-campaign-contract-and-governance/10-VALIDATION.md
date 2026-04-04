---
phase: 10
slug: closed-loop-campaign-contract-and-governance
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_campaign_schema.py tests/test_llm_campaign_storage.py tests/test_llm_suggest_core.py tests/test_llm_suggest_cli.py tests/test_llm_campaign_spec.py tests/test_llm_approve_cli.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~30-180 seconds depending on focused wave vs full suite |

---

## Sampling Rate

- **After every task commit:** Run the smallest focused Phase 10 command that
  matches the files changed.
- **After every plan wave:** Run that wave's targeted pytest command.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | LLM-06 | schema | `cd materials-discovery && uv run pytest tests/test_llm_campaign_schema.py -x -v` | ⬜ | ⬜ pending |
| 10-01-02 | 01 | 1 | OPS-05 | unit/storage | `cd materials-discovery && uv run pytest tests/test_llm_campaign_storage.py -x -v` | ⬜ | ⬜ pending |
| 10-02-01 | 02 | 2 | LLM-06 | unit | `cd materials-discovery && uv run pytest tests/test_llm_suggest_core.py -x -v` | ⬜ | ⬜ pending |
| 10-02-02 | 02 | 2 | OPS-05 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_suggest_cli.py -x -v` | ⬜ | ⬜ pending |
| 10-03-01 | 03 | 3 | OPS-05 | unit/integration | `cd materials-discovery && uv run pytest tests/test_llm_campaign_spec.py -x -v` | ⬜ | ⬜ pending |
| 10-03-02 | 03 | 3 | LLM-06, OPS-05 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_approve_cli.py tests/test_cli.py -x -v` | ⬜ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_llm_campaign_schema.py` — typed proposal,
  approval, spec, action-family, and lineage contract coverage
- [ ] `materials-discovery/tests/test_llm_campaign_storage.py` — deterministic
  artifact-path coverage for suggestion/proposal/approval/spec roots
- [ ] `materials-discovery/tests/test_llm_suggest_core.py` — acceptance-pack to
  proposal mapping coverage across all major failing-metric branches
- [ ] `materials-discovery/tests/test_llm_suggest_cli.py` — dry-run CLI
  contract coverage for bundle/proposal outputs
- [ ] `materials-discovery/tests/test_llm_campaign_spec.py` — approval decision
  and self-contained spec materialization coverage
- [ ] `materials-discovery/tests/test_llm_approve_cli.py` — approval CLI
  contract coverage proving approval writes artifacts but does not launch runs
- [ ] Any Phase 10 execution that changes `materials-discovery/` must update
  `materials-discovery/Progress.md` per repo policy
- [ ] Any approval/spec tests must avoid live provider calls and must not depend
  on Java export availability unless explicitly monkeypatched
- [ ] Any CLI regression that touches shared LLM command routing should keep
  `materials-discovery/tests/test_cli.py` green

*Existing pytest infrastructure already covers the project. Wave 0 is about new
Phase 10 tests and governance-boundary regression coverage rather than tooling
installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Proposal bundle and per-system proposal files are understandable to a human operator | LLM-06 | Readability and operator trust are hard to encode in assertions alone | Run `mdisc llm-suggest` on a known acceptance pack and inspect `suggestions.json` plus `proposals/*.json` for clarity, evidence, and action specificity |
| Approval/spec lineage is clearly audit-friendly | OPS-05 | The schema can validate while the file flow still feels confusing | Approve one proposal manually, then inspect the approval artifact and campaign spec to confirm the acceptance-pack, proposal, approval, eval-set, and config lineage are easy to follow |
| Approval is a real governance boundary, not an implicit launch | OPS-05 | This is partly a product/UX boundary, not just a code behavior | Confirm the Phase 10 CLI/documentation ends at spec materialization and never claims to launch `llm-generate` yet |

---

## Validation Sign-Off

- [ ] All tasks have focused automated verify commands or explicit Wave 0 prerequisites
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all new Phase 10 seams
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
