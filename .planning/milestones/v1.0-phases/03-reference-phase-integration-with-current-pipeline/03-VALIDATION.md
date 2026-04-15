---
phase: 03
slug: reference-phase-integration-with-current-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — existing repo test infrastructure already present |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_cli.py tests/test_ingest.py tests/test_ingest_real_backend.py tests/test_generate.py` |
| **Bridge command** | `cd materials-discovery && uv run pytest tests/test_data_source_projection.py tests/test_ingest_source_registry.py` |
| **Full pipeline command** | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py tests/test_hull_proxy.py tests/test_report.py tests/test_ingest.py` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~20-120 seconds depending on whether the full real-mode smoke is included |

---

## Sampling Rate

- **After every task commit:** Run the smallest focused command attached to that
  task plus the quick compatibility command when `cli.py`, `common/schema.py`,
  `common/manifest.py`, or `backends/registry.py` changed.
- **After every plan wave:** Run the quick command plus the plan-specific
  bridge/pipeline command for that wave.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | DATA-05 | unit | `cd materials-discovery && uv run pytest tests/test_data_source_projection.py` | ⬜ | ⬜ pending |
| 03-01-02 | 01 | 1 | OPS-03 | unit | `cd materials-discovery && uv run pytest tests/test_data_source_projection.py tests/test_hull_proxy.py` | ✅ | ⬜ pending |
| 03-02-01 | 02 | 2 | PIPE-01 | integration | `cd materials-discovery && uv run pytest tests/test_ingest_source_registry.py tests/test_cli.py tests/test_ingest.py tests/test_ingest_real_backend.py tests/test_generate.py` | ✅ | ⬜ pending |
| 03-02-02 | 02 | 2 | OPS-03 | integration | `cd materials-discovery && uv run pytest tests/test_ingest_source_registry.py tests/test_cli.py` | ⬜ | ⬜ pending |
| 03-03-01 | 03 | 3 | PIPE-01 | integration | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py tests/test_hull_proxy.py tests/test_report.py tests/test_ingest.py` | ✅ | ⬜ pending |
| 03-03-02 | 03 | 3 | DATA-05 | integration | `cd materials-discovery && uv run pytest tests/test_data_source_projection.py tests/test_ingest_source_registry.py tests/test_real_mode_pipeline.py tests/test_ingest.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_data_source_projection.py` — projection,
  system matching, deterministic phase-label derivation, and metadata coverage
- [ ] `materials-discovery/tests/test_ingest_source_registry.py` — source
  bridge ingest, staged-source reuse, manifest lineage, and CLI summary
- [ ] `materials-discovery/tests/test_generate.py` — non-ingest manifest regression guard after additive `ArtifactManifest` changes
- [ ] Source-backed offline payload fixture(s) or inline test data for at least
  one bridge path so no Phase 3 verification depends on live network access
- [ ] Dynamic in-test config generation for the bridge-backed real-mode pipeline
  smoke so Phase 3 does not add permanent YAML config debt

*Existing pytest infrastructure is already present. Wave 0 is about the Phase 3
test files and fixtures, not tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Source-backed ingest manifest is readable and shows snapshot lineage clearly | PIPE-01 | Human traceability of lineage fields is easiest to judge directly | Run one source-backed `mdisc ingest`, open the manifest JSON, and confirm source key, snapshot ID, snapshot manifest path, and canonical-record path are obvious |
| Processed reference-phase JSONL remains operator-friendly despite richer metadata | DATA-05 | Tests can validate shape, but readability still matters | Inspect one projected JSONL and verify `phase_name`, `composition`, and additive metadata are understandable |
| No-DFT boundary remains intact for the bridge path | OPS-03 | Best validated by inspecting what the bridge calls during a real run | Run a source-backed ingest and confirm it stages, projects, and writes manifests without invoking committee/phonon/md/xrd adapters |

---

## Validation Sign-Off

- [ ] All tasks have focused automated verify commands or explicit Wave 0 prerequisites
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all new Phase 3 seams
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
