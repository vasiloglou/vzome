---
phase: 11
slug: closed-loop-campaign-execution-bridge
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_launch_core.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_cli.py tests/test_llm_campaign_lineage.py -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~45-240 seconds depending on focused wave vs full suite |

---

## Sampling Rate

- **After every task commit:** Run the smallest focused Phase 11 command that
  matches the files changed.
- **After every plan wave:** Run that wave's targeted pytest command.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | LLM-08 | schema/storage | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py -x -v` | ⬜ | ⬜ pending |
| 11-01-02 | 01 | 1 | LLM-08 | core/unit | `cd materials-discovery && uv run pytest tests/test_llm_launch_core.py -x -v` | ⬜ | ⬜ pending |
| 11-02-01 | 02 | 2 | LLM-08, LLM-10 | core/integration | `cd materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py -x -v` | ✅ | ⬜ pending |
| 11-02-02 | 02 | 2 | LLM-08, LLM-10, OPS-06 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_launch_cli.py tests/test_cli.py -x -v` | ⬜ | ⬜ pending |
| 11-03-01 | 03 | 3 | OPS-06 | manifest/integration | `cd materials-discovery && uv run pytest tests/test_llm_campaign_lineage.py tests/test_report.py -x -v` | ⬜ | ⬜ pending |
| 11-03-02 | 03 | 3 | LLM-10, OPS-06 | E2E/integration | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k \"campaign or llm_launch\" -x -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_llm_launch_schema.py` — typed launch
  artifact, lane-config, and storage-path coverage
- [ ] `materials-discovery/tests/test_llm_launch_core.py` — deterministic
  action-to-overlay resolution coverage for prompt, composition, and seed flows
- [ ] `materials-discovery/tests/test_llm_launch_cli.py` — approved
  campaign-spec launch CLI coverage including failure and success paths
- [ ] `materials-discovery/tests/test_llm_campaign_lineage.py` — downstream
  manifest propagation coverage for campaign lineage
- [ ] `materials-discovery/tests/test_llm_generate_core.py` and
  `materials-discovery/tests/test_llm_generate_cli.py` stay green with no
  campaign spec involved
- [ ] Any Phase 11 execution that changes `materials-discovery/` must update
  `materials-discovery/Progress.md` per repo policy
- [ ] Any launch tests must avoid live provider calls unless explicitly
  monkeypatched and should remain offline/deterministic by default
- [ ] Any launch tests that materialize seed Zomic from eval-set examples must
  use committed fixtures or synthetic examples, not Java-dependent exports
- [ ] Any new campaign-lineage tests must verify both run-level artifacts and
  standard stage manifests

*Existing pytest infrastructure covers the repo. Wave 0 is about new campaign
launch and lineage coverage rather than tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Campaign launch summary is understandable to an operator | LLM-08 | Auditability and operator trust are still partly experiential | Launch one approved campaign and inspect `data/llm_campaigns/{campaign_id}/launches/{launch_id}/launch_summary.json` for clear requested lane, resolved lane, config hash, artifact pointers, and failure/success state |
| Downstream lineage remains easy to trace after a manual follow-on stage | OPS-06 | The manifest can validate structurally while still being hard to follow | Run `mdisc llm-launch`, then `mdisc screen`, and inspect both manifests to confirm campaign lineage stays obvious and additive |
| Manual `llm-generate` still feels unchanged | LLM-10 | Regression here is partly a UX/operator contract issue | Run a baseline `mdisc llm-generate --config ... --count 1` and confirm it still writes the standard outputs without requiring campaign inputs |

---

## Validation Sign-Off

- [ ] All tasks have focused automated verify commands or explicit Wave 0 prerequisites
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all new Phase 11 seams
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 240s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
