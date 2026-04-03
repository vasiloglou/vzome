---
phase: 06
slug: zomic-training-corpus-pipeline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none — existing repo test infrastructure already present |
| **Quick run command** | `cd materials-discovery && uv run pytest tests/test_zomic_bridge.py tests/test_prototype_import.py tests/test_generate.py` |
| **Corpus foundation command** | `cd materials-discovery && uv run pytest tests/test_llm_corpus_schema.py tests/test_llm_corpus_storage.py tests/test_llm_corpus_manifest.py` |
| **Converter command** | `cd materials-discovery && uv run pytest tests/test_llm_record2zomic.py tests/test_llm_projection2zomic.py tests/test_llm_cif2zomic.py` |
| **Builder command** | `cd materials-discovery && uv run pytest tests/test_llm_corpus_inventory.py tests/test_llm_corpus_qa.py tests/test_llm_corpus_builder.py tests/test_llm_corpus_cli.py` |
| **Full suite command** | `cd materials-discovery && uv run pytest` |
| **Estimated runtime** | ~30-240 seconds depending on whether focused Phase 6 tests only or the full suite is run |

---

## Sampling Rate

- **After every task commit:** Run the smallest focused Phase 6 command that
  matches the files changed. If `cli.py`, `generator/zomic_bridge.py`,
  `generator/prototype_import.py`, `common/schema.py`, or any corpus manifest
  model changes, also run the quick command.
- **After every plan wave:** Run the focused command(s) for that wave plus the
  quick command.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 240 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | LLM-01 | unit | `cd materials-discovery && uv run pytest tests/test_llm_corpus_schema.py tests/test_llm_corpus_storage.py` | ⬜ | ⬜ pending |
| 06-01-02 | 01 | 1 | LLM-01 | unit | `cd materials-discovery && uv run pytest tests/test_llm_corpus_manifest.py` | ⬜ | ⬜ pending |
| 06-02-01 | 02 | 2 | LLM-01 | unit/integration | `cd materials-discovery && uv run pytest tests/test_llm_corpus_inventory.py` | ⬜ | ⬜ pending |
| 06-02-02 | 02 | 2 | LLM-01 | unit | `cd materials-discovery && uv run pytest tests/test_llm_corpus_qa.py` | ⬜ | ⬜ pending |
| 06-03-01 | 03 | 2 | LLM-01 | unit | `cd materials-discovery && uv run pytest tests/test_llm_record2zomic.py` | ⬜ | ⬜ pending |
| 06-03-02 | 03 | 2 | LLM-01 | integration | `cd materials-discovery && uv run pytest tests/test_llm_projection2zomic.py tests/test_zomic_bridge.py` | ✅ | ⬜ pending |
| 06-04-01 | 04 | 3 | LLM-01 | unit/integration | `cd materials-discovery && uv run pytest tests/test_llm_cif2zomic.py tests/test_prototype_import.py tests/test_data_source_cod.py` | ✅ | ⬜ pending |
| 06-04-02 | 04 | 3 | LLM-01 | integration | `cd materials-discovery && uv run pytest tests/test_llm_corpus_builder.py tests/test_llm_corpus_inventory.py tests/test_llm_corpus_qa.py` | ⬜ | ⬜ pending |
| 06-04-03 | 04 | 3 | LLM-01 | CLI/integration | `cd materials-discovery && uv run pytest tests/test_llm_corpus_cli.py tests/test_cli.py` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `materials-discovery/tests/test_llm_corpus_schema.py` — corpus config,
  example, fidelity, and manifest-adjacent contracts
- [ ] `materials-discovery/tests/test_llm_corpus_storage.py` — deterministic
  path helpers under `data/llm_corpus/{build_id}/`
- [ ] `materials-discovery/tests/test_llm_corpus_manifest.py` — manifest writer,
  fingerprinting, and workspace-relative lineage
- [ ] `materials-discovery/tests/test_llm_corpus_inventory.py` — repo-native
  Zomic inventory, candidate inventory, staged-source inventory, and
  `PyQCstrc` payload discovery
- [ ] `materials-discovery/tests/test_llm_corpus_qa.py` — `gold` / `silver` /
  reject tiering, fidelity tags, and dedupe behavior
- [ ] `materials-discovery/tests/test_llm_record2zomic.py` — deterministic
  serializer output and conversion trace coverage
- [ ] `materials-discovery/tests/test_llm_projection2zomic.py` — thin
  `PyQCstrc` projection fixture conversion and compile-validation wiring
- [ ] `materials-discovery/tests/test_llm_cif2zomic.py` — COD/HYPOD-X-style CIF
  conversion coverage with lazy optional imports
- [ ] `materials-discovery/tests/test_llm_corpus_builder.py` — end-to-end corpus
  build for syntax + materials outputs
- [ ] `materials-discovery/tests/test_llm_corpus_cli.py` — `mdisc llm-corpus`
  command contract and summary output
- [ ] `materials-discovery/tests/fixtures/pyqcstrc_projection_sample.json` —
  committed thin projection fixture
- [ ] `materials-discovery/tests/fixtures/hypodx_approximant_sample.cif` or an
  exact equivalent committed structure fixture for open-approximant coverage
- [ ] No Phase 6 verification may require live network access or a live
  `PyQCstrc` installation
- [ ] Any `pymatgen` usage must remain behind lazy imports or fixture-backed
  fallbacks so Phase 6 tests can still run on minimal installs

*Existing pytest infrastructure is already present. Wave 0 is about new corpus
tests, fixtures, and optional-dependency discipline, not tooling installation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `gold` vs `silver` release boundaries are scientifically sensible | LLM-01 | The trust boundary is a product decision as much as a schema rule | Build a sample corpus and inspect `qa.json` plus representative examples from both tiers; confirm downgraded examples are understandable and justified |
| Repo-native syntax corpus is actually useful as language-teaching data | LLM-01 | Human review is the best way to catch low-value but valid scripts | Inspect a sample of regression scripts, part scripts, and materials designs in the built syntax corpus and confirm source-family tagging makes sense |
| The `PyQCstrc` input contract is understandable to a human operator | LLM-01 | Needed because Phase 6 intentionally avoids a live `PyQCstrc` dependency | Read the committed fixture/schema docs and confirm an external projection export could realistically be adapted into the expected payload shape |

---

## Validation Sign-Off

- [ ] All tasks have focused automated verify commands or explicit Wave 0 prerequisites
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all new Phase 6 seams
- [ ] No watch-mode or long-running background commands are required
- [ ] Feedback latency < 240s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
