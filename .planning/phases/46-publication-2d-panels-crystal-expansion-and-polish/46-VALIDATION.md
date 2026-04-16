---
phase: 46
slug: publication-2d-panels-crystal-expansion-and-polish
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-16
---

# Phase 46 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | materials-discovery/pyproject.toml |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_matplotlib_pub.py tests/test_expansion.py -x -q` |
| **Full suite command** | `cd materials-discovery && uv run pytest tests/ -x -q` |
| **Estimated runtime** | ~25 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick command
- **After every plan wave:** Run full suite
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 25 seconds

---

## Per-Task Verification Map

> **Non-TDD ordering note:** Implementation tasks run before test tasks because
> tests import the modules at module level. Direct import checks serve as the
> Wave 0 signal for implementation tasks. This follows the Phase 45 precedent.

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 46-01-T1 | 01 | 1 | VIZ-03,VIZ-04,VIZ-05 | import check | `uv run python -c "from materials_discovery.visualization.matplotlib_pub import screening_scatter"` | ⬜ pending |
| 46-01-T2 | 01 | 1 | VIZ-03,VIZ-04,VIZ-05 | unit | `uv run pytest tests/test_matplotlib_pub.py -x -q` | ⬜ pending |
| 46-02-T1 | 02 | 1 | ENRICH-02 | import check | `uv run python -c "from materials_discovery.visualization.expansion import expansion_figure"` | ⬜ pending |
| 46-02-T2 | 02 | 1 | ENRICH-02 | unit | `uv run pytest tests/test_expansion.py -x -q` | ⬜ pending |
| 46-03-T1 | 03 | 2 | VIZ-03,VIZ-04,VIZ-05,ENRICH-02 | structural | python3 notebook cell check | ⬜ pending |
| 46-03-T2 | 03 | 2 | all | manual | jupyter notebook visual inspection | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_matplotlib_pub.py` — stubs for VIZ-03 screening scatter, VIZ-04 RDF, VIZ-05 diffraction
- [ ] `tests/test_expansion.py` — stubs for ENRICH-02 expansion figure

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Screening scatter renders with threshold lines | VIZ-03 | Visual rendering | Open notebook, verify 2D scatter with energy/distance axes |
| RDF peaks annotated at correct shell distances | VIZ-04 | Visual annotation quality | Verify vertical lines at ~5.97, 6.13, 6.57, 6.73, 7.73 Å |
| Diffraction pattern shows peak positions | VIZ-05 | Visual rendering | Verify stem plot with peak labels |
| Crystal expansion shows 2x2x2 tiling | ENRICH-02 | Visual 3D rendering | Verify central cell highlighted, surrounding cells dimmed |
| "Periodic approximant tiling" label present | ENRICH-02 | Visual check | Verify figure title and note |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 25s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
