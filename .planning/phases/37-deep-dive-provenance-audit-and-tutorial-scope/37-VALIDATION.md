---
phase: 37
slug: deep-dive-provenance-audit-and-tutorial-scope
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-14
---

# Phase 37 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | grep plus `git diff --check` |
| **Config file** | none — docs-only validation for `.planning/` artifacts |
| **Quick run command** | `git diff --check` |
| **Full suite command** | `bash -lc 'git diff --check && rg -n "Source Document Provenance|Post-Draft Shipped Workflow Deltas|Stale Quantitative Claims|Missing Shipped Surfaces For Phase 38|Tutorial Anchor Scope Lock|Phase 39 Tutorial Scope Lock" .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md && rg -n "359cef57777479fb15652f1f4c702c43a25c4bc6|9d7e7bc8189b067155a147ce2dd1e180688ef96f|f21c17e3c1a246349d0d0171cfa0b9390bcc8c1d|mdisc llm-external-benchmark|sc_zn_zomic.yaml|sc_zn_tsai_bridge.yaml" .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md && test -z "$(git status --short -- materials-discovery)"'` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `git diff --check`
- **After every plan wave:** Run the Phase 37 full suite command
- **Before `$gsd-verify-work`:** Confirm `37-PROVENANCE-AUDIT.md` exists and all required section headings and evidence strings are grep-verifiable
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 37-01-01 | 01 | 1 | DOC-01 | docs/provenance smoke | `bash -lc 'test -f .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md && rg -n "Source Document Provenance|359cef57777479fb15652f1f4c702c43a25c4bc6|9d7e7bc8189b067155a147ce2dd1e180688ef96f|f21c17e3c1a246349d0d0171cfa0b9390bcc8c1d|Post-Draft Shipped Workflow Deltas|v1.0|v1.6|fidelity-aware scorecards" .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md'` | ✅ | ⬜ pending |
| 37-01-02 | 01 | 1 | DOC-01 | docs/content check | `bash -lc 'rg -n "Stale Quantitative Claims|4,238 commits|seven commands|60 modules|7,200 lines of code|21 test files|Stale Capability Descriptions|four execution layers|Missing Shipped Surfaces For Phase 38|mdisc llm-external-benchmark|mdisc llm-register-external-target|Future-Work Labeling Risks|D-01|D-02|D-03|D-04|D-05|D-06" .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md'` | ✅ | ⬜ pending |
| 37-01-03 | 01 | 1 | DOC-01 | docs/tutorial-scope check | `bash -lc 'rg -n "Tutorial Anchor Scope Lock|Only worked tutorial system: Sc-Zn|uv run mdisc export-zomic --design designs/zomic/sc_zn_tsai_bridge.yaml|uv run mdisc report --config configs/systems/sc_zn_zomic.yaml|Tutorial Artifact Set|materials-discovery/data/prototypes/generated/sc_zn_tsai_bridge.raw.json|materials-discovery/data/reports/sc_zn_report.json|Phase 38 Correction Checklist|Phase 39 Tutorial Scope Lock|Evidence Commands" .planning/phases/37-deep-dive-provenance-audit-and-tutorial-scope/37-PROVENANCE-AUDIT.md && test -z "$(git status --short -- materials-discovery)"'` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-14
