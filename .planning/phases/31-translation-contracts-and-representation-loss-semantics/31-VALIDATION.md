---
phase: 31
slug: translation-contracts-and-representation-loss-semantics
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
last_updated: "2026-04-06T15:02:49Z"
---

# Phase 31 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` via `uv run pytest` |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_schema.py tests/test_llm_translation_core.py -x -v` |
| **Full suite command** | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_schema.py tests/test_llm_translation_core.py tests/test_llm_translation_fixtures.py tests/test_structure_realization.py tests/test_llm_record2zomic.py tests/test_data_source_schema.py -x -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_schema.py tests/test_llm_translation_core.py -x -v`
- **After every plan wave:** Run `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_schema.py tests/test_llm_translation_core.py tests/test_llm_translation_fixtures.py tests/test_structure_realization.py tests/test_llm_record2zomic.py tests/test_data_source_schema.py -x -v`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 31-01-01 | 01 | 1 | LLM-27 | unit/schema | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_schema.py -x -v` | ❌ W0 | ⬜ pending |
| 31-01-02 | 01 | 1 | LLM-30 | unit/schema | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_schema.py -x -v` | ❌ W0 | ⬜ pending |
| 31-02-01 | 02 | 2 | LLM-27 | unit/core | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_core.py tests/test_structure_realization.py -x -v` | ❌ W0 | ⬜ pending |
| 31-02-02 | 02 | 2 | LLM-30 | unit/core | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_core.py tests/test_structure_realization.py -x -v` | ❌ W0 | ⬜ pending |
| 31-03-01 | 03 | 3 | LLM-27 | regression | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_fixtures.py -x -v` | ❌ W0 | ⬜ pending |
| 31-03-02 | 03 | 3 | LLM-30 | docs/contract | `cd /Users/nikolaosvasiloglou/github-repos/vzome && rg -n "exact|anchored|approximate|lossy|QC-native|source of truth" materials-discovery/developers-docs/llm-translation-contract.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing `pytest` infrastructure covers all phase requirements.
- No framework installation or harness bootstrap is required before execution.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
