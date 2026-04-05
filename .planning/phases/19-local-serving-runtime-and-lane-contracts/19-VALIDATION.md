---
phase: 19
slug: local-serving-runtime-and-lane-contracts
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_runtime.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_core.py tests/test_llm_launch_cli.py tests/test_llm_replay_core.py tests/test_cli.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~45-240 seconds depending on focused slice vs full suite |

---

## Sampling Rate

- **After Wave 1 runtime/schema work:** Run `cd materials-discovery && uv run pytest tests/test_llm_runtime.py tests/test_llm_launch_schema.py -x -v`
- **Before starting Wave 2:** Run `cd materials-discovery && uv run pytest`
- **After Wave 2 manual-generate / launch work:** Run `cd materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_core.py tests/test_llm_launch_cli.py tests/test_cli.py -x -v`
- **After Wave 3 replay/docs/config work:** Run `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_runtime.py tests/test_llm_generate_cli.py tests/test_cli.py -x -v`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | LLM-14, OPS-08 | schema/unit | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py -x -v` | ✅ | ✅ green |
| 19-01-02 | 01 | 1 | LLM-13, OPS-08 | runtime/unit | `cd materials-discovery && uv run pytest tests/test_llm_runtime.py -x -v` | ✅ | ✅ green |
| 19-02-01 | 02 | 2 | LLM-13, LLM-14 | core/integration | `cd materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_launch_core.py -x -v` | ✅ | ✅ green |
| 19-02-02 | 02 | 2 | LLM-13, LLM-14, OPS-08 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_cli.py -x -v` | ✅ | ✅ green |
| 19-03-01 | 03 | 3 | LLM-14, OPS-08 | replay/config | `cd materials-discovery && uv run pytest tests/test_llm_replay_core.py tests/test_llm_runtime.py -x -v` | ✅ | ✅ green |
| 19-03-02 | 03 | 3 | LLM-13, OPS-08 | compatibility | `cd materials-discovery && uv run pytest tests/test_llm_generate_cli.py tests/test_cli.py -x -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `materials-discovery/tests/test_llm_runtime.py` — covers the local OpenAI-compatible adapter, lazy `httpx` import, readiness probes, default `/v1/models` probe behavior, supported response-shape parsing, endpoint validation, and operator-facing failure messages
- [x] `materials-discovery/tests/test_llm_launch_schema.py` — covers additive config fields, lane-source compatibility, explicit fallback config, serving-identity normalization, and the fact that new writes may populate `serving_identity` while legacy artifacts still deserialize with `serving_identity=None`
- [x] `materials-discovery/tests/test_llm_generate_core.py` and `materials-discovery/tests/test_llm_generate_cli.py` — cover manual `--model-lane` selection, shared precedence (`CLI > config default > explicit fallback > backend default`), standard manifest compatibility, and local-lane preflight behavior without live provider calls
- [x] `materials-discovery/tests/test_llm_launch_core.py` and `materials-discovery/tests/test_llm_launch_cli.py` — cover launch-time lane resolution, explicit fallback semantics, and local-lane diagnostics
- [x] `materials-discovery/tests/test_llm_replay_core.py` — verifies new serving-identity fields do not break strict replay config rebuilds and fail clearly on hard local identity mismatch while surfacing transport/environment drift distinctly
- [x] All local-serving tests remain offline and deterministic via monkeypatched HTTP or committed fixtures; no live local server is required in CI
- [x] Phase 22 only touched planning artifacts, so `materials-discovery/Progress.md` did not need an update during audit closure

*Existing pytest infrastructure covers the repo. Wave 0 is about local-serving contract coverage, not tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Local-serving errors are understandable to an operator | OPS-08 | Message clarity matters beyond structural validation | Trigger a missing-endpoint or unreachable-server local-lane run and confirm the error names the lane, adapter, endpoint/path, and whether fallback was allowed |
| Serving identity is easy to audit from run artifacts | LLM-14 | Structural correctness can still be hard to interpret | Run one local-lane `llm-generate` invocation and inspect the run manifest / launch artifacts for requested lane, resolved lane, adapter/provider/model, endpoint/path, checkpoint/revision, and source |
| Docs make the setup boundary explicit | OPS-08 | The milestone intentionally does not manage local processes | Follow the docs to confirm they say the local server must already be running and that Phase 19 does not start or manage it |

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
    milestone audit gap after the underlying serving behavior had already
    shipped.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all new Phase 19 seams
- [x] No watch-mode or long-running background commands are required
- [x] Feedback latency < 240s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** automated verification complete
