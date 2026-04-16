---
phase: 44
slug: prose-enrichment-and-zomic-annotation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-15
---

# Phase 44 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | materials-discovery/pyproject.toml |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_labels.py -x -q` |
| **Full suite command** | `cd materials-discovery && uv run pytest tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd materials-discovery && uv run pytest tests/test_labels.py -x -q`
- **After every plan wave:** Run `cd materials-discovery && uv run pytest tests/ -x -q`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 44-01-01 | 01 | 1 | NARR-01 | manual | grep "Tsai" guided-design-tutorial.md | ✅ | ⬜ pending |
| 44-01-02 | 01 | 1 | NARR-02 | manual | grep "← " guided-design-tutorial.md | ✅ | ⬜ pending |
| 44-01-03 | 01 | 1 | NARR-03 | manual | grep "energy_proxy" guided-design-tutorial.md | ✅ | ⬜ pending |
| 44-01-04 | 01 | 1 | NARR-04 | manual | grep "release_gate" guided-design-tutorial.md | ✅ | ⬜ pending |
| 44-01-05 | 01 | 1 | NARR-05 | manual | grep "llm-generate" guided-design-tutorial.md | ✅ | ⬜ pending |
| 44-02-01 | 02 | 1 | ENRICH-01 | unit | uv run pytest tests/test_labels.py -x -q | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_labels.py` — stubs for ENRICH-01 label mapping and palette
- [ ] Verify existing test suite passes before changes

*Prose requirements (NARR-01 through NARR-05) are verified by content grep, not unit tests.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Design-origin narrative reads coherently | NARR-01 | Prose quality requires human judgment | Read the new section; verify it explains Tsai clusters and the Sc-Zn design choice |
| Zomic annotations are accurate | NARR-02 | Geometry explanation correctness requires domain knowledge | Verify each annotation matches the physical result of its Zomic block |
| Screening explanation is understandable | NARR-03 | Plain-language clarity requires human judgment | Read; verify proxy metrics are defined and threshold logic is explained |
| Validation explanation is honest | NARR-04 | Framing of "all gates False" requires nuance judgment | Verify it frames the result as expected early-stage behavior, not failure |
| LLM section has matching depth | NARR-05 | Narrative consistency requires reading both sections | Compare LLM section depth to deterministic spine section depth |
| Notebook condensed versions link correctly | NARR-01-05 | Cross-document links require browser check | Open notebook; verify prose cells link to markdown tutorial |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
