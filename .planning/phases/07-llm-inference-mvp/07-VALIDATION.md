---
phase: 07
slug: llm-inference-mvp
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_generate_schema.py tests/test_llm_runtime.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py` |
| **Benchmark command** | `cd materials-discovery && uv run pytest tests/test_llm_generate_benchmarks.py tests/test_cli.py` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~30-240 seconds depending on whether focused Phase 7 tests or the full suite are run |

---

## Sampling Rate

- **After every task commit:** Run the smallest focused Phase 7 command that
  matches the files changed.
- **After every plan wave:** Run the focused command(s) for that wave. Run the
  benchmark command after the benchmark/evaluation wave.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | LLM-02 | unit | `cd materials-discovery && uv run pytest tests/test_llm_generate_schema.py -x -v` | ⬜ | ⬜ pending |
| 07-01-02 | 01 | 1 | LLM-02 | unit | `cd materials-discovery && uv run pytest tests/test_llm_runtime.py -x -v` | ⬜ | ⬜ pending |
| 07-02-01 | 02 | 2 | LLM-02 | unit/integration | `cd materials-discovery && uv run pytest tests/test_llm_generate_core.py -x -v` | ⬜ | ⬜ pending |
| 07-02-02 | 02 | 2 | LLM-02 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_generate_cli.py tests/test_cli.py -x -v` | ⬜ | ⬜ pending |
| 07-03-01 | 03 | 3 | LLM-02 | benchmark/integration | `cd materials-discovery && uv run pytest tests/test_llm_generate_benchmarks.py -x -v` | ⬜ | ⬜ pending |
| 07-03-02 | 03 | 3 | LLM-02 | benchmark/CLI | `cd materials-discovery && uv run pytest tests/test_llm_generate_benchmarks.py tests/test_cli.py -x -v` | ⬜ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_llm_generate_schema.py` — config,
  summary, provenance, and run-artifact contract coverage
- [ ] `materials-discovery/tests/test_llm_runtime.py` — mock adapter, hosted
  adapter seam, lazy optional imports, and retry/attempt model coverage
- [ ] `materials-discovery/tests/test_llm_generate_core.py` — prompt assembly,
  compile classification, candidate conversion, and bounded retry behavior
- [ ] `materials-discovery/tests/test_llm_generate_cli.py` — `mdisc
  llm-generate` command contract and JSON summary output
- [ ] `materials-discovery/tests/test_llm_generate_benchmarks.py` — offline
  `Al-Cu-Fe` and `Sc-Zn` benchmark comparison coverage
- [ ] Any real-provider tests must be fixture-backed or monkeypatched so no live
  network access is required in repo verification
- [ ] Any `httpx` import for the hosted adapter must stay lazy so the minimal
  install path and mock-only tests remain viable
- [ ] Any Phase 7 execution that changes `materials-discovery/` must update
  `materials-discovery/Progress.md` per repo policy
- [ ] Any new pytest marker used for slower LLM benchmark tests must be declared
  in `materials-discovery/pyproject.toml`

*Existing pytest infrastructure already covers the project. Wave 0 is about new
Phase 7 tests, fixtures, and optional-dependency discipline rather than tooling
installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Run-level prompt/raw-output lineage is understandable to operators | LLM-02 | Human inspection is the best way to catch provenance bloat or missing context | Build a mock run, inspect `data/llm_runs/{run_id}/`, and confirm prompt, attempts, and compile outcomes can be followed without reading code |
| Generated candidate provenance stays additive and compact | LLM-02 | The schema can pass tests while still being awkward for downstream use | Inspect one generated candidate JSONL row and confirm it links back to the run without embedding raw transcripts |
| The first hosted-provider config is usable by a human operator | LLM-02 | Secret/env-var ergonomics are hard to judge purely from fixtures | Review the example config and README/runbook notes, then run `mdisc llm-generate` manually in a real-provider environment if credentials exist |

*If credentials are not available locally, document the real-provider setup path and rely on fixture-backed automated tests.*

---

## Validation Sign-Off

- [ ] All tasks have focused automated verify commands or explicit Wave 0 prerequisites
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all new Phase 7 seams
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 240s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
