---
phase: 04
slug: reference-aware-no-dft-materials-discovery-v1
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — existing repo test infrastructure already present |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_benchmarking.py tests/test_hifi_rank.py tests/test_report.py` |
| **Reference-pack command** | `cd materials-discovery && uv run pytest tests/test_reference_packs.py tests/test_ingest_source_registry.py tests/test_cli.py` |
| **Reference-aware benchmark command** | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py tests/test_hifi_rank.py tests/test_report.py` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~30-180 seconds depending on whether the dedicated reference-aware benchmark lane and the full suite are included |

---

## Sampling Rate

- **After every task commit:** Run the smallest focused command attached to that
  task plus the quick command when `cli.py`, `common/schema.py`,
  `common/manifest.py`, `common/benchmarking.py`, or any benchmark config
  changes.
- **After every plan wave:** Run the quick command plus the plan-specific
  reference-pack or reference-aware benchmark command for that wave.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 180 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | PIPE-02 | unit/integration | `cd materials-discovery && uv run pytest tests/test_reference_packs.py tests/test_ingest_source_registry.py` | ⬜ | ⬜ pending |
| 04-01-02 | 01 | 1 | PIPE-02 | integration | `cd materials-discovery && uv run pytest tests/test_reference_packs.py tests/test_benchmarking.py tests/test_cli.py` | ⬜ | ⬜ pending |
| 04-02-01 | 02 | 2 | PIPE-03 | unit | `cd materials-discovery && uv run pytest tests/test_benchmarking.py tests/test_hifi_rank.py` | ✅ | ⬜ pending |
| 04-02-02 | 02 | 2 | PIPE-03 | integration | `cd materials-discovery && uv run pytest tests/test_report.py tests/test_real_mode_pipeline.py` | ✅ | ⬜ pending |
| 04-02-03 | 02 | 2 | PIPE-03 | integration | `cd materials-discovery && uv run pytest tests/test_benchmarking.py tests/test_hifi_rank.py tests/test_report.py` | ✅ | ⬜ pending |
| 04-03-01 | 03 | 3 | PIPE-02 | integration | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py` | ✅ | ⬜ pending |
| 04-03-02 | 03 | 3 | PIPE-03 | integration | `cd materials-discovery && uv run pytest tests/test_real_mode_pipeline.py tests/test_report.py tests/test_hifi_rank.py` | ✅ | ⬜ pending |
| 04-03-03 | 03 | 3 | PIPE-02, PIPE-03 | full | `cd materials-discovery && uv run pytest` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_reference_packs.py` or an exact equivalent
  must exist to lock reference-pack assembly, reuse, lineage, and deterministic
  dedupe behavior
- [ ] `materials-discovery/tests/test_benchmarking.py` must grow beyond the
  current single-system assertion set to cover both benchmark systems and any
  new benchmark-pack metadata
- [ ] `materials-discovery/tests/test_real_mode_pipeline.py` must cover both
  required Phase 4 benchmark systems and at least one cross-lane comparison,
  with the new reference-aware matrix isolated as a clearly slower lane rather
  than silently stretching the quick path
- [ ] `materials-discovery/tests/test_hifi_rank.py` and
  `materials-discovery/tests/test_report.py` must assert on additive
  benchmark/reference provenance, not only fingerprints and basic metrics
- [ ] The Phase 4 multi-source proof must include at least one thin second-source
  local fixture or staged payload, not only reused HYPOD-X fixture rows
- [ ] No Phase 4 verification may require live network access
- [ ] The `Sc-Zn` benchmark lane must either skip gracefully when Java is absent
  or use a pre-exported orbit-library fixture
- [ ] New benchmark scripts/docs must be runnable from a clean checkout using
  committed configs and local assets

*Existing pytest infrastructure is already present. Wave 0 is about benchmark
coverage, fixtures, and scripts, not tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Reference-pack manifest is readable and clearly identifies member sources/snapshots | PIPE-02 | Human traceability matters as much as schema validity here | Build one reference-pack lane, open the pack manifest, and confirm the source list, snapshot IDs, counts, and fingerprint are easy to follow |
| Benchmark-pack output is operator-comparable across lanes | PIPE-03 | Best checked by reading the produced JSON side by side | Run two benchmark lanes and confirm the benchmark-pack summary exposes backend mode, source keys, reference-pack ID, benchmark corpus, stage paths, and key release metrics |
| Runbook can be followed on a clean checkout | PIPE-02 | Docs quality is easier to judge manually than in unit tests | Follow the benchmark runbook from scratch and confirm the commands match the committed configs/scripts |

---

## Validation Sign-Off

- [ ] All tasks have focused automated verify commands or explicit Wave 0 prerequisites
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all new Phase 4 seams
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 180s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
