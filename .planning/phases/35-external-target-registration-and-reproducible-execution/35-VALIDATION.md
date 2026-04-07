---
phase: 35
slug: external-target-registration-and-reproducible-execution
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-07
last_updated: "2026-04-07T06:45:00Z"
---

# Phase 35 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` via `uv run pytest` |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_schema.py tests/test_llm_external_target_registry.py tests/test_llm_external_target_cli.py -x -v` |
| **Full suite command** | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_schema.py tests/test_llm_external_target_registry.py tests/test_llm_external_target_cli.py tests/test_cli.py -x -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_schema.py tests/test_llm_external_target_registry.py tests/test_llm_external_target_cli.py -x -v`
- **After every plan wave:** Run `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_schema.py tests/test_llm_external_target_registry.py tests/test_llm_external_target_cli.py tests/test_cli.py -x -v`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 35-01-01 | 01 | 1 | OPS-17 | schema | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_schema.py -x -v` | ❌ W0 | ⬜ pending |
| 35-01-02 | 01 | 1 | OPS-17 | storage | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_schema.py -x -v` | ❌ W0 | ⬜ pending |
| 35-02-01 | 02 | 2 | OPS-17 | registry-core | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_registry.py -x -v` | ❌ W0 | ⬜ pending |
| 35-02-02 | 02 | 2 | OPS-17 | smoke-and-environment | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_registry.py tests/test_llm_external_target_cli.py -x -v` | ❌ W0 | ⬜ pending |
| 35-03-01 | 03 | 3 | OPS-17 | cli-surface | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_cli.py tests/test_cli.py -x -v` | ❌ W0 | ⬜ pending |
| 35-03-02 | 03 | 3 | OPS-17 | docs-example-flow | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_target_cli.py tests/test_cli.py -x -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_llm_external_target_schema.py` — contract and storage expectations
- [ ] `materials-discovery/tests/test_llm_external_target_registry.py` — normalization, fingerprinting, reload, and smoke persistence
- [ ] `materials-discovery/tests/test_llm_external_target_cli.py` — CLI help, register, inspect, and smoke behavior

Existing infrastructure otherwise covers the phase.

---

## Manual-Only Verifications

All Phase 35 behaviors should remain automatable through fixture snapshots,
monkeypatched runtime helpers, and CLI regression tests.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 20s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
