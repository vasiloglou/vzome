---
phase: 36
slug: comparative-benchmark-workflow-and-fidelity-aware-scorecards
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-07
last_updated: "2026-04-07T00:00:00Z"
---

# Phase 36 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `pytest` via `uv run pytest` |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_schema.py tests/test_llm_external_benchmark_core.py -x -v` |
| **Full suite command** | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_schema.py tests/test_llm_external_benchmark_core.py tests/test_llm_external_benchmark_cli.py tests/test_cli.py -x -v` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_schema.py tests/test_llm_external_benchmark_core.py -x -v`
- **After every plan wave:** Run `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_schema.py tests/test_llm_external_benchmark_core.py tests/test_llm_external_benchmark_cli.py tests/test_cli.py -x -v`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 25 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 36-01-01 | 01 | 1 | LLM-32, LLM-33 | schema | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_schema.py -x -v` | ✅ yes | ⬜ pending |
| 36-01-02 | 01 | 1 | LLM-32 | storage | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_schema.py -x -v` | ✅ yes | ⬜ pending |
| 36-02-01 | 02 | 2 | LLM-32 | benchmark-execution | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_core.py -x -v` | ✅ yes | ⬜ pending |
| 36-02-02 | 02 | 2 | LLM-33 | scorecard-and-recommendations | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_core.py -x -v` | ✅ yes | ⬜ pending |
| 36-03-01 | 03 | 3 | LLM-32, OPS-18 | cli-run-and-inspect | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_cli.py tests/test_cli.py -x -v` | ✅ yes | ⬜ pending |
| 36-03-02 | 03 | 3 | OPS-18 | docs-example-flow | `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest tests/test_llm_external_benchmark_cli.py tests/test_cli.py -x -v` | ✅ yes | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `materials-discovery/tests/test_llm_external_benchmark_schema.py` — contract and storage expectations
- [x] `materials-discovery/tests/test_llm_external_benchmark_core.py` — benchmark execution, case-result persistence, control deltas, and recommendation logic
- [x] `materials-discovery/tests/test_llm_external_benchmark_cli.py` — CLI run and inspect coverage

Existing infrastructure otherwise covers the phase.

---

## Manual-Only Verifications

All planned Phase 36 behaviors should remain automatable through fixture
benchmark manifests, monkeypatched target runners or adapters, typed artifact
assertions, and CLI regression tests.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 25s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
