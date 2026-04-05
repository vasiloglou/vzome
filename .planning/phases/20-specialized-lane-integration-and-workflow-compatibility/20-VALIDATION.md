---
phase: 20
slug: specialized-lane-integration-and-workflow-compatibility
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
---

# Phase 20 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run python -m pytest tests/test_llm_evaluate_schema.py tests/test_llm_evaluate_cli.py tests/test_llm_compare_core.py tests/test_llm_compare_cli.py tests/test_llm_campaign_lineage.py tests/test_llm_replay_core.py tests/test_report.py tests/test_real_mode_pipeline.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run python -m pytest` |
| **Estimated runtime** | ~60-300 seconds depending on focused slice vs full suite |

---

## Sampling Rate

- **After Wave 1 evaluation-contract work:** Run `cd materials-discovery && uv run pytest tests/test_llm_evaluate_schema.py -x -v`
- **Before starting Wave 2:** Run `cd materials-discovery && uv run pytest`
- **After Wave 2 specialized-lane proof and compare/report work:** Run `cd materials-discovery && uv run pytest tests/test_llm_evaluate_cli.py tests/test_llm_compare_core.py tests/test_llm_compare_cli.py tests/test_llm_campaign_lineage.py tests/test_llm_replay_core.py tests/test_report.py -x -v`
- **After Wave 3 second-system compatibility proof and docs wiring:** Run `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py tests/test_cli.py tests/test_llm_compare_cli.py -x -v`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 300 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 20-01-01 | 01 | 1 | LLM-15, OPS-09 | schema/unit | `cd materials-discovery && uv run python -m pytest tests/test_llm_evaluate_schema.py -x -v` | ✅ | ✅ green |
| 20-01-02 | 01 | 1 | LLM-15, OPS-09 | evaluation/core | `cd materials-discovery && uv run python -m pytest tests/test_llm_evaluate_schema.py -x -v` | ✅ | ✅ green |
| 20-02-01 | 02 | 2 | LLM-15 | CLI/integration | `cd materials-discovery && uv run python -m pytest tests/test_llm_evaluate_cli.py -x -v` | ✅ | ✅ green |
| 20-02-02 | 02 | 2 | LLM-16, OPS-09 | compare/report/replay integration | `cd materials-discovery && uv run python -m pytest tests/test_llm_compare_core.py tests/test_llm_compare_cli.py tests/test_llm_campaign_lineage.py tests/test_llm_replay_core.py tests/test_report.py -x -v` | ✅ | ✅ green |
| 20-03-01 | 03 | 3 | LLM-16, OPS-09 | real-mode/integration | `cd materials-discovery && uv run python -m pytest tests/test_real_mode_pipeline.py -x -v` | ✅ | ✅ green |
| 20-03-02 | 03 | 3 | LLM-16 | docs/CLI regression | `cd materials-discovery && uv run python -m pytest tests/test_real_mode_pipeline.py tests/test_cli.py tests/test_llm_compare_cli.py -x -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_llm_evaluate_schema.py` — cover `llm_evaluate.model_lane`, additive evaluation serving identity, and backward-compatible evaluation artifact reads
- [ ] `materials-discovery/src/materials_discovery/llm/specialist.py` — provide a thin specialized-evaluation payload seam so the specialized lane is not only differentiated by endpoint selection
- [ ] `materials-discovery/tests/test_llm_evaluate_cli.py` — cover `mdisc llm-evaluate --model-lane ...`, explicit fallback behavior, and specialized-lane summary output
- [ ] `materials-discovery/tests/test_llm_compare_core.py` and `materials-discovery/tests/test_llm_compare_cli.py` — cover additive generation/evaluation lane lineage in outcome snapshots and compare artifacts
- [ ] `materials-discovery/tests/test_llm_replay_core.py` — cover replay compatibility when specialized evaluation lineage is present
- [ ] `materials-discovery/tests/test_llm_campaign_lineage.py` and `materials-discovery/tests/test_report.py` — cover campaign/report visibility of specialized evaluation lineage without mutating standard artifact shapes
- [ ] `materials-discovery/tests/test_real_mode_pipeline.py` — cover one real system plus one thin compatibility proof with offline monkeypatched specialized endpoints
- [ ] All specialized-lane tests must remain offline and deterministic via monkeypatched OpenAI-compatible responses; no live model server is required in CI
- [ ] Any Phase 20 execution that changes `materials-discovery/` must update `materials-discovery/Progress.md` per repo policy

*Existing pytest infrastructure covers the repo. Wave 0 is about specialized-lane workflow coverage, not test tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Specialized lane role is described honestly | LLM-15 | The distinction between evaluation-primary and direct-generation is partly a documentation/product-truth question | Read updated docs/configs and confirm they describe the first specialized lane as evaluation-primary rather than implying mature direct Zomic generation |
| Specialized endpoint guidance is operational, not aspirational | LLM-15, OPS-09 | The phase now claims a real specialized lane path, so operators need at least one concrete endpoint recipe | Read the updated configuration and integration docs and confirm they include a concrete OpenAI-compatible specialized endpoint recipe with placeholder-safe examples |
| Compare/report outputs make lane provenance understandable | OPS-09 | Machine-readable lineage can still be hard for operators to interpret | Run one specialized-lane evaluation flow and inspect compare/report outputs to confirm both generation and evaluation lane identity are visible and distinct |
| One deep proof plus one thin proof is explicit | LLM-16 | Scope discipline matters for this milestone | Confirm the docs and summaries clearly show which system is the primary proof and which is the thinner compatibility guard |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all new Phase 20 seams
- [x] No watch-mode or long-running background commands are required
- [x] Feedback latency < 300s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** passed
