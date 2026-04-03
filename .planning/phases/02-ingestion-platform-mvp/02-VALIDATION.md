---
phase: 02
slug: ingestion-platform-mvp
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — existing repo test infrastructure already present |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_ingest.py tests/test_ingest_real_backend.py tests/test_cli.py` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~15-90 seconds depending on scope |

---

## Sampling Rate

- **After every task commit:** Run `cd materials-discovery && uv run pytest tests/test_ingest.py tests/test_ingest_real_backend.py tests/test_cli.py`
- **After every plan wave:** Run `cd materials-discovery && uv run pytest`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | DATA-03 | unit | `cd materials-discovery && uv run pytest tests/test_data_source_schema.py tests/test_data_source_registry.py tests/test_data_source_qa.py` | ✅ | ⬜ pending |
| 02-01-02 | 01 | 1 | OPS-04 | integration | `cd materials-discovery && uv run pytest tests/test_cli.py tests/test_ingest.py tests/test_ingest_real_backend.py` | ✅ | ⬜ pending |
| 02-01-03 | 01 | 1 | DATA-04 | unit | `cd materials-discovery && uv run pytest tests/test_data_source_schema.py tests/test_data_source_qa.py` | ✅ | ⬜ pending |
| 02-02-01 | 02 | 2 | DATA-03 | integration | `cd materials-discovery && uv run pytest tests/test_data_source_hypodx.py tests/test_data_source_cod.py` | ✅ | ⬜ pending |
| 02-02-02 | 02 | 2 | DATA-04 | integration | `cd materials-discovery && uv run pytest tests/test_data_source_hypodx.py tests/test_data_source_cod.py tests/test_data_source_qa.py` | ✅ | ⬜ pending |
| 02-03-01 | 03 | 3 | DATA-03 | integration | `cd materials-discovery && uv run pytest tests/test_data_source_optimade.py tests/test_data_source_materials_project.py tests/test_data_source_api_adapters.py` | ✅ | ⬜ pending |
| 02-03-02 | 03 | 3 | OPS-04 | integration | `cd materials-discovery && uv run pytest tests/test_cli.py tests/test_ingest.py tests/test_ingest_real_backend.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_data_source_schema.py` — canonical raw-source schema validation
- [ ] `materials-discovery/tests/test_data_source_registry.py` — adapter and registry resolution coverage
- [ ] `materials-discovery/tests/test_data_source_qa.py` — duplicate, missing-field, malformed-structure, and drift metrics
- [ ] `materials-discovery/tests/test_data_source_adapters.py` — shared adapter contract behavior across source families

*Existing infrastructure covers pytest execution and CLI integration. Wave 0 is
about new Phase 2 test files, not framework installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Snapshot artifact layout under `data/external/sources/` is understandable and traceable | DATA-03 | Directory ergonomics and lineage readability are hard to judge from tests alone | Run one staged-source flow, inspect snapshot directory, manifest names, and QA report paths |
| Existing configs without an `ingestion` block still behave correctly | OPS-04 | Additive-compatibility regressions are easiest to catch with a real operator check | Run `mdisc ingest --config configs/systems/al_cu_fe.yaml` before and after Phase 2 changes and compare summary/manifests |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
