---
phase: 11
slug: closed-loop-campaign-execution-bridge
status: automated_complete
nyquist_compliant: true
wave_0_complete: true
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
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_launch_core.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_cli.py tests/test_llm_campaign_lineage.py tests/test_report.py -x -v` |
| **Focused downstream command** | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "campaign or llm_launch" -x -v` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~45-240 seconds depending on focused wave vs full suite |

---

## Sampling Rate

- **After evidence refresh work:** Run the focused Phase 11 launch/lineage
  slices plus the downstream compatibility check.
- **After verification or traceability doc work:** Run `git diff --check`.
- **Before the Phase 11 audit gap closes:** Ensure `11-VALIDATION.md` and
  `11-VERIFICATION.md` tell the same success or blocked story.
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | LLM-08 | schema/storage | `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py -x -v` | ✅ | ✅ green |
| 11-01-02 | 01 | 1 | LLM-08 | core/unit | `cd materials-discovery && uv run pytest tests/test_llm_launch_core.py -x -v` | ✅ | ✅ green |
| 11-02-01 | 02 | 2 | LLM-08, LLM-10 | core/integration | `cd materials-discovery && uv run pytest tests/test_llm_generate_core.py tests/test_llm_generate_cli.py -x -v` | ✅ | ✅ green |
| 11-02-02 | 02 | 2 | LLM-08, LLM-10, OPS-06 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_launch_cli.py tests/test_cli.py -x -v` | ✅ | ✅ green |
| 11-03-01 | 03 | 3 | OPS-06 | manifest/integration | `cd materials-discovery && uv run pytest tests/test_llm_campaign_lineage.py tests/test_report.py -x -v` | ✅ | ✅ green |
| 11-03-02 | 03 | 3 | LLM-10, OPS-06 | E2E/integration | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k \"campaign or llm_launch\" -x -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `materials-discovery/tests/test_llm_launch_schema.py` — typed launch
  artifact, lane-config, lane-resolution-source, and storage-path coverage
- [x] `materials-discovery/tests/test_llm_launch_core.py` — deterministic
  action-to-overlay resolution coverage for prompt, composition, precision-safe
  shrink heuristics, lane fallback, and seed flows
- [x] `materials-discovery/tests/test_llm_launch_cli.py` — approved
  campaign-spec launch CLI coverage including config-drift detail, `--out`
  override recording, launch-id visibility, and failure/success paths
- [x] `materials-discovery/tests/test_llm_campaign_lineage.py` — downstream
  manifest propagation coverage for campaign lineage without duplicate nesting
- [x] `materials-discovery/tests/test_llm_generate_core.py` and
  `materials-discovery/tests/test_llm_generate_cli.py` stay green with no
  campaign spec involved
- [x] Any Phase 11 execution that changes `materials-discovery/` must update
  `materials-discovery/Progress.md` per repo policy
- [x] Any launch tests must avoid live provider calls unless explicitly
  monkeypatched and should remain offline/deterministic by default
- [x] Any launch tests that materialize seed Zomic from eval-set examples must
  use committed fixtures or synthetic examples, not Java-dependent exports
- [x] Any new campaign-lineage tests must verify both run-level artifacts and
  standard stage manifests
- [x] Any config-drift test failures must assert operator-facing context:
  config path, pinned/current hash detail when available, and re-approval guidance
- [x] Any `resolved_launch.json` checks must assert both the effective
  candidates path and whether the resolved lane came from a configured-lane
  match or baseline fallback

*Existing pytest infrastructure covers the repo. Wave 0 is about new campaign
launch and lineage coverage rather than tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Campaign launch summary is understandable to an operator | LLM-08 | Auditability and operator trust are still partly experiential | Launch one approved campaign and inspect `data/llm_campaigns/{campaign_id}/launches/{launch_id}/launch_summary.json` for clear requested lane, resolved lane, whether fallback was used, config hash, artifact pointers, and failure/success state |
| Downstream lineage remains easy to trace after a manual follow-on stage | OPS-06 | The manifest can validate structurally while still being hard to follow | Run `mdisc llm-launch`, then `mdisc screen`, and inspect both manifests to confirm campaign lineage stays obvious and additive |
| Lineage audit is understandable from docs and on-disk artifacts | OPS-06 | The artifact chain can be technically correct while still being hard for an operator to follow | Follow the documented Lineage Audit path from a downstream manifest or report entry back to `campaign_spec.json`, the approval artifact, and the launch wrapper directory |
| Manual `llm-generate` still feels unchanged | LLM-10 | Regression here is partly a UX/operator contract issue | Run a baseline `mdisc llm-generate --config ... --count 1` and confirm it still writes the standard outputs without requiring campaign inputs |

---

## Verification Results

- Focused Phase 11 rerun performed during Phase 14 audit closure:
  - `cd materials-discovery && uv run pytest tests/test_llm_launch_schema.py tests/test_llm_launch_core.py tests/test_llm_generate_core.py tests/test_llm_generate_cli.py tests/test_llm_launch_cli.py tests/test_cli.py tests/test_llm_campaign_lineage.py tests/test_report.py -x -v`
  - Result: `60 passed in 1.42s`
- Focused downstream compatibility rerun performed during Phase 14 audit closure:
  - `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py -k "campaign or llm_launch" -x -v`
  - Result: `2 passed, 6 deselected in 13.18s`
- Existing full-suite evidence from
  [11-03-SUMMARY.md](/Users/nikolaosvasiloglou/github-repos/vzome/.planning/phases/11-closed-loop-campaign-execution-bridge/11-03-SUMMARY.md):
  - `cd /Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery && uv run pytest`
  - Result: `357 passed, 3 skipped, 1 warning`

This validation artifact was finalized retroactively in Phase 14 to close the
v1.1 milestone audit gap for Phase 11.

---

## Validation Sign-Off

- [x] All tasks have focused automated verify commands or explicit Wave 0 prerequisites
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all new Phase 11 seams
- [x] No watch-mode or long-running background commands are required
- [x] Feedback latency < 240s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** automated verification complete
