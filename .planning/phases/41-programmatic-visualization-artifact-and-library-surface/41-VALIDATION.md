---
phase: 41
slug: programmatic-visualization-artifact-and-library-surface
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-15
---

# Phase 41 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + Typer CLI tests |
| **Config file** | `materials-discovery/pyproject.toml` |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_zomic_visualization.py tests/test_cli.py -q` |
| **Full suite command** | `cd materials-discovery && uv run pytest tests/test_zomic_bridge.py tests/test_llm_native_sources.py tests/test_zomic_visualization.py tests/test_cli.py -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd materials-discovery && uv run pytest tests/test_zomic_visualization.py tests/test_cli.py -q`
- **After every plan wave:** Run `cd materials-discovery && uv run pytest tests/test_zomic_bridge.py tests/test_llm_native_sources.py tests/test_zomic_visualization.py tests/test_cli.py -q`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 41-01-01 | 01 | 1 | VIS-02 | unit | `cd materials-discovery && uv run pytest tests/test_zomic_visualization.py -q` | ❌ W0 | ⬜ pending |
| 41-01-02 | 01 | 1 | VIS-01, VIS-02 | cli | `cd materials-discovery && uv run pytest tests/test_cli.py -q -k "preview_zomic or export_zomic"` | ✅ | ⬜ pending |
| 41-01-03 | 01 | 1 | VIS-01, VIS-02 | docs + policy | `bash -lc 'rg -n "preview-zomic|sc_zn_tsai_bridge.raw.json|desktop vZome|\\.vZome|\\.shapes.json" materials-discovery/developers-docs/programmatic-zomic-visualization.md materials-discovery/developers-docs/zomic-design-workflow.md && rg -n "Phase 41 raw export viewer" materials-discovery/Progress.md'` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_zomic_visualization.py` — focused coverage for VIS-02 raw export loading, malformed segment rejection, and a guarded smoke test against `sc_zn_tsai_bridge.raw.json`
- [ ] `materials-discovery/tests/test_cli.py` — preview-zomic command cases for VIS-01 and VIS-02, including both-provided input rejection and patched browser opening
- [ ] Existing pytest + Typer infrastructure covers the phase after those test additions

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Interactive rotate / zoom / label toggle in generated `.viewer.html` | VIS-02 | Browser canvas interaction is not covered by the Python-only fast loop | Generate the checked Sc-Zn viewer HTML, open it in a browser, drag to rotate, use mouse wheel to zoom, toggle labels, and confirm the design remains legible |
| Boundary between preview surface and desktop vZome authoring | VIS-01, VIS-02 | This is a wording/product-boundary check, not a code-path check | Read `programmatic-zomic-visualization.md` and confirm it says the new viewer is for programmatic preview while desktop vZome remains the editing tool |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
