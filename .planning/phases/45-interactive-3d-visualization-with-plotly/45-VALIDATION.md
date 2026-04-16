---
phase: 45
slug: interactive-3d-visualization-with-plotly
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-16
---

# Phase 45 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | materials-discovery/pyproject.toml |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_plotly_3d.py -x -q` |
| **Full suite command** | `cd materials-discovery && uv run pytest tests/ -x -q` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd materials-discovery && uv run pytest tests/test_plotly_3d.py -x -q`
- **After every plan wave:** Run `cd materials-discovery && uv run pytest tests/ -x -q`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

The phase has 4 tasks across 2 plans (not 5 across 3, as originally drafted).

> **Deliberate non-TDD ordering in Plan 01 Task 1:** Task 1 (implementation) runs before
> Task 2 (tests) because the test suite imports `plotly_3d` at module level — tests cannot
> be written as failing stubs without the module itself existing. The direct import checks
> in Task 1's `<verify>` serve as the Wave 0 signal. This is the same pattern used for
> matplotlib_pub.py and expansion.py stubs elsewhere in the phase. `nyquist_compliant`
> remains `false` to acknowledge this deliberate choice; it does not indicate a gap.

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 45-01-T1 | 01 | 1 | ENRICH-03 | import check | `uv run python -c "from materials_discovery.visualization.plotly_3d import orbit_figure"` | ❌ created by task | ⬜ pending |
| 45-01-T2 | 01 | 1 | VIZ-01,VIZ-02,ENRICH-03 | unit | `uv run pytest tests/test_plotly_3d.py -x -q` | ❌ created by task | ⬜ pending |
| 45-02-T1 | 02 | 2 | VIZ-01,VIZ-02 | structural | python3 notebook cell check script | ✅ exists | ⬜ pending |
| 45-02-T2 | 02 | 2 | VIZ-01,VIZ-02 | manual | jupyter notebook visual inspection | ✅ exists | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_plotly_3d.py` — stubs for VIZ-01 orbit figure and VIZ-02 shell figure
- [ ] Verify plotly importable in the venv after [viz] extra added

*plotly_3d.py functions must return plotly Figure objects testable without rendering.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Orbit scatter renders correctly in notebook | VIZ-01 | Visual rendering requires browser | Open notebook, run Section 4 cells, verify 5 orbit traces with distinct colors |
| Shell figure shows toggleable layers | VIZ-02 | Interactive toggle requires browser | Open notebook, run shell figure cell, verify legend toggles shells on/off |
| Hover text shows label+orbit+species+shell | VIZ-01 | Hover interaction requires browser | Hover over sites in orbit figure, verify all 4 fields present |
| Cage wireframes visible at opacity=0.15 | VIZ-02 | Visual opacity requires browser | Verify polyhedral cage faces semi-transparent with edge lines |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
