---
phase: 18
slug: phase-15-self-verification-closure
status: automated_complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for closing the last residual v1.1 documentary
> tech debt.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Primary checks** | cross-file consistency, doc-hygiene, artifact existence |
| **Target validation file** | `.planning/phases/15-phase-12-replay-and-operator-workflow-audit-closure/15-VALIDATION.md` |
| **Target verification file** | `.planning/phases/15-phase-12-replay-and-operator-workflow-audit-closure/15-VERIFICATION.md` |
| **Doc hygiene command** | `git diff --check` |
| **Existence check** | `test -f .planning/phases/15-phase-12-replay-and-operator-workflow-audit-closure/15-VERIFICATION.md` |
| **Consistency check** | `rg -n "status: automated_complete|nyquist_compliant: true" .planning/phases/15-phase-12-replay-and-operator-workflow-audit-closure/15-VALIDATION.md` |

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-----------|-------------------|-------------|--------|
| 18-01-01 | 01 | 1 | consistency | `rg -n "status: automated_complete|nyquist_compliant: true" .planning/phases/15-phase-12-replay-and-operator-workflow-audit-closure/15-VALIDATION.md` | ✅ | ✅ green |
| 18-01-02 | 01 | 1 | doc hygiene | `git diff --check` | ✅ | ✅ green |
| 18-02-01 | 02 | 2 | existence | `test -f .planning/phases/15-phase-12-replay-and-operator-workflow-audit-closure/15-VERIFICATION.md` | ✅ | ✅ green |
| 18-02-02 | 02 | 2 | doc hygiene | `git diff --check` | ✅ | ✅ green |
| 18-03-01 | 03 | 3 | existence | `test -f .planning/phases/18-phase-15-self-verification-closure/18-VERIFICATION.md` | ✅ | ✅ green |
| 18-03-02 | 03 | 3 | doc hygiene | `git diff --check` | ✅ | ✅ green |

---

## Wave 0 Requirements

- [x] Phase 18 stays docs-only and does not touch `materials-discovery/`
- [x] `15-VALIDATION.md` remains finalized and consistent
- [x] `15-VERIFICATION.md` exists
- [x] Phase 18 leaves behind its own finalized validation and verification
  artifacts
- [x] `STATE.md` returns the milestone to `ready_for_milestone_audit`

---

## Validation Sign-Off

- [x] All tasks have an automated doc-hygiene or consistency check
- [x] Wave 0 captures only the actual Phase 15 tech debt
- [x] No product code or `materials-discovery/` changes were required
- [x] `15-VALIDATION.md`, `15-VERIFICATION.md`, and `18-VERIFICATION.md` tell a consistent story
- [x] `nyquist_compliant: true` set in frontmatter by the end of execution

**Approval:** automated verification complete
