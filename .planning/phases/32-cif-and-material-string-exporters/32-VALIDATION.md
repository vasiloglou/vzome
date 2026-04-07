---
phase: 32
slug: cif-and-material-string-exporters
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-06
last_updated: "2026-04-07T00:14:06Z"
---

# Phase 32 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` via `uv run pytest` |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_export.py tests/test_llm_translation_cif.py tests/test_llm_translation_material_string.py -x -v` |
| **Full suite command** | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_export.py tests/test_llm_translation_cif.py tests/test_llm_translation_material_string.py tests/test_llm_translation_export_fixtures.py tests/test_llm_translation_schema.py tests/test_llm_translation_core.py tests/test_llm_translation_fixtures.py tests/test_structure_realization.py tests/test_llm_record2zomic.py tests/test_data_source_schema.py -x -v` |
| **Estimated runtime** | ~12 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_export.py tests/test_llm_translation_cif.py tests/test_llm_translation_material_string.py -x -v`
- **After every plan wave:** Run `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_export.py tests/test_llm_translation_cif.py tests/test_llm_translation_material_string.py tests/test_llm_translation_export_fixtures.py tests/test_llm_translation_schema.py tests/test_llm_translation_core.py tests/test_llm_translation_fixtures.py tests/test_structure_realization.py tests/test_llm_record2zomic.py tests/test_data_source_schema.py -x -v`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 32-01-01 | 01 | 1 | LLM-28 | unit/export-core | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_export.py -x -v` | ❌ W0 | ⬜ pending |
| 32-01-02 | 01 | 1 | LLM-28 | unit/cif | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_cif.py -x -v` | ❌ W0 | ⬜ pending |
| 32-02-01 | 02 | 2 | LLM-29 | unit/material-string | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_material_string.py -x -v` | ❌ W0 | ⬜ pending |
| 32-02-02 | 02 | 2 | LLM-28, LLM-29 | unit/dispatch | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_export.py tests/test_llm_translation_material_string.py -x -v` | ❌ W0 | ⬜ pending |
| 32-03-01 | 03 | 3 | LLM-28, LLM-29 | regression/golden | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_export_fixtures.py -x -v` | ❌ W0 | ⬜ pending |
| 32-03-02 | 03 | 3 | LLM-28 | parser/failure | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_translation_cif.py tests/test_llm_translation_export.py tests/test_llm_translation_export_fixtures.py -x -v` | ❌ W0 | ⬜ pending |

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
- [x] Feedback latency < 20s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
