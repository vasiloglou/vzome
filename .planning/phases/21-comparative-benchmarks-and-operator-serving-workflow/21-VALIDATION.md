---
phase: 21
slug: comparative-benchmarks-and-operator-serving-workflow
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
---

# Phase 21 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~60-300 seconds depending on focused slice vs full suite |

---

## Sampling Rate

- **After Wave 1 benchmark-contract work:** Run `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py tests/test_llm_serving_benchmark_core.py -x -v`
- **Before starting Wave 2:** Run `cd materials-discovery && uv run pytest`
- **After Wave 2 benchmark CLI and real-proof work:** Run `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_real_mode_pipeline.py -x -v`
- **After Wave 3 docs/config workflow work:** Run `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 300 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 21-01-01 | 01 | 1 | LLM-17, OPS-10 | schema/unit | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_schema.py -x -v` | ✅ | ✅ green |
| 21-01-02 | 01 | 1 | LLM-17, OPS-10 | core/unit | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_core.py -x -v` | ✅ | ✅ green |
| 21-02-01 | 02 | 2 | LLM-17 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py -x -v` | ✅ | ✅ green |
| 21-02-02 | 02 | 2 | LLM-17, OPS-10 | end-to-end/integration | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_real_mode_pipeline.py -x -v` | ✅ | ✅ green |
| 21-03-01 | 03 | 3 | OPS-10 | docs/config regression | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_cli.py -x -v` | ✅ | ✅ green |
| 21-03-02 | 03 | 3 | LLM-17, OPS-10 | real-mode/docs integration | `cd materials-discovery && uv run pytest tests/test_llm_serving_benchmark_cli.py tests/test_cli.py tests/test_real_mode_pipeline.py -x -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `materials-discovery/src/materials_discovery/llm/serving_benchmark.py` — provides the typed benchmark and smoke orchestration core rather than burying logic in `cli.py`
- [x] `materials-discovery/src/materials_discovery/llm/schema.py` — adds typed benchmark spec, smoke artifact, and benchmark result contracts
- [x] `materials-discovery/src/materials_discovery/llm/storage.py` — adds stable artifact roots under `data/benchmarks/llm_serving/{benchmark_id}/...`
- [x] `materials-discovery/tests/test_llm_serving_benchmark_schema.py` — covers shared-context spec rules, target validation, and result serialization
- [x] `materials-discovery/tests/test_llm_serving_benchmark_core.py` — covers explicit smoke failures, no silent fallback, and benchmark recommendation summaries
- [x] `materials-discovery/tests/test_llm_serving_benchmark_cli.py` — covers `--smoke-only`, normal benchmark execution, and human-readable recommendation output
- [x] `materials-discovery/tests/test_real_mode_pipeline.py` — covers one real serving benchmark proof path offline with monkeypatched providers
- [x] All serving-benchmark tests remain offline and deterministic; no live hosted or local model server is required in CI
- [x] `load_serving_benchmark_spec(...)` rejects mixed-system benchmark specs by comparing each target system config against the shared acceptance-pack context
- [x] `llm_evaluate` benchmark targets keep their batch or candidate source aligned with the shared acceptance-pack context; unrelated slices fail clearly
- [x] Benchmark summaries leave role-specific missing metrics explicit rather than fabricating parity between generation and evaluation targets
- [x] Phase 24 only touched planning artifacts, so `materials-discovery/Progress.md` did not need an update during audit closure

*Existing pytest infrastructure covers the repo. Wave 0 is about the new serving-benchmark workflow seams, not test tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Benchmark summary gives useful operator recommendations | LLM-17, OPS-10 | The recommendation quality is partly a product/usability judgment | Run one offline benchmark and confirm the printed guidance clearly distinguishes fastest, cheapest, lowest-friction, and strongest-quality targets without hiding missing data |
| Smoke-test procedure is explicit and operator-usable | OPS-10 | This is partly about runbook ergonomics, not only code | Follow the documented `--smoke-only` workflow from the runbook and confirm it explains setup failures and no-silent-fallback expectations clearly |
| Specialized lane is benchmarked honestly | LLM-17 | The lane role should not be overstated in docs or summaries | Confirm the benchmark docs/specs describe the specialized target as evaluation-primary when appropriate rather than implying mature direct Zomic generation |

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

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all new Phase 21 seams
- [x] No watch-mode or long-running background commands are required
- [x] Feedback latency < 300s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** automated verification complete
