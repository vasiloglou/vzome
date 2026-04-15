---
phase: 38
slug: narrative-refresh-and-cross-linked-deep-dive
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-15
---

# Phase 38 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | grep-based docs validation plus `pytest` smoke when command references materially change |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `bash -lc 'git diff --check && ! rg -n "4,238 commits|seven commands|60 modules|7,200|21 test files|Seven Pipeline Stages|four execution layers|targets three real alloy systems|full seven-stage pipeline" materials-discovery/developers-docs/podcast-deep-dive-source.md'` |
| **Full suite command** | `bash -lc 'git diff --check && rg -n "export-zomic|llm-serving-benchmark|llm-list-checkpoints|llm-promote-checkpoint|llm-retire-checkpoint|llm-translate|llm-translated-benchmark-freeze|llm-register-external-target|llm-external-benchmark" materials-discovery/developers-docs/podcast-deep-dive-source.md && rg -n "RUNBOOK.md|pipeline-stages.md|backend-system.md|zomic-design-workflow.md|llm-translation-runbook.md|llm-external-benchmark-runbook.md" materials-discovery/developers-docs/podcast-deep-dive-source.md && rg -n "future work|not shipped|planned beyond|not yet|operator-governed" materials-discovery/developers-docs/podcast-deep-dive-source.md && rg -n "^\| .* \|.*Narrative Refresh.*\|^\| .* \|.*podcast-deep-dive.*" materials-discovery/Progress.md && cd materials-discovery && uv run pytest tests/test_cli.py -q'` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run the quick run command
- **After every plan wave:** Run the full suite command
- **Before `$gsd-verify-work`:** Read the refreshed deep dive end-to-end to confirm the shipped/future distinction still reads cleanly to a human
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 38-01-01 | 01 | 1 | DOC-02 | docs narrative audit | `bash -lc 'rg -n "export-zomic|llm-serving-benchmark|llm-list-checkpoints|llm-promote-checkpoint|llm-retire-checkpoint|llm-translate|llm-translated-benchmark-freeze|llm-register-external-target|llm-external-benchmark" materials-discovery/developers-docs/podcast-deep-dive-source.md && ! rg -n "4,238 commits|seven commands|60 modules|7,200|21 test files|Seven Pipeline Stages|four execution layers|targets three real alloy systems|full seven-stage pipeline" materials-discovery/developers-docs/podcast-deep-dive-source.md'` | ✅ | ⬜ pending |
| 38-01-02 | 01 | 1 | DOC-03 | docs link and future-work audit | `bash -lc 'rg -n "RUNBOOK.md|pipeline-stages.md|backend-system.md|zomic-design-workflow.md|llm-translation-runbook.md|llm-external-benchmark-runbook.md" materials-discovery/developers-docs/podcast-deep-dive-source.md && rg -n "future work|not shipped|planned beyond|not yet|operator-governed" materials-discovery/developers-docs/podcast-deep-dive-source.md'` | ✅ | ⬜ pending |
| 38-01-03 | 01 | 1 | DOC-02, DOC-03 | docs progress-log audit | `bash -lc 'test -f materials-discovery/Progress.md && rg -n "podcast-deep-dive|deep-dive|narrative refresh" materials-discovery/Progress.md && git diff --name-only -- materials-discovery | rg "Progress.md|podcast-deep-dive-source.md"'` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Balanced narrative split still feels like a high-level story instead of a runbook | DOC-02, DOC-03 | Grep can prove presence/absence of strings, but not whether the rewritten deep dive preserves the intended 50/50 narrative balance | Read the refreshed `materials-discovery/developers-docs/podcast-deep-dive-source.md` top to bottom and confirm the geometry/vZome origin story remains substantial while the shipped `v1.6` workflow surface carries slightly more weight. |
| Cross-link density feels helpful rather than noisy | DOC-03 | Automated checks can confirm links exist, but not whether they are gracefully placed | Scan each major workflow-family section and confirm at most one or two source-of-truth links appear where readers would naturally want procedural detail. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-15
