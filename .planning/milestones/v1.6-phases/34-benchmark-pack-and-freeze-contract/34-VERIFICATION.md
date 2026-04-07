---
phase: 34-benchmark-pack-and-freeze-contract
verified: 2026-04-07T06:25:13Z
status: passed
score: 3/3 must-haves verified
---

# Phase 34: Benchmark Pack and Freeze Contract Verification Report

**Phase Goal:** Operators can freeze one trustworthy translated benchmark pack from shipped translation bundles so later external-versus-internal comparisons run on an explicit, fidelity-aware case slice.
**Verified:** 2026-04-07T06:25:13Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Operator can freeze a benchmark set from one or more shipped translation bundles using explicit rules for system, target family, fidelity tier, and representational-loss posture. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/llm/schema.py:1645` defines the typed freeze contract; `materials-discovery/src/materials_discovery/llm/translated_benchmark.py:49-249` loads the spec, reads bundle manifests and inventories, applies `systems` / `target_family` / `allowed_fidelity_tiers` / `loss_posture`, handles duplicates, and writes typed artifacts; shipped spec `materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml:1-13` resolves against committed demo bundle manifests; focused tests passed (`38 passed in 0.47s`). |
| 2 | Operator can inspect the frozen benchmark set and see which translated cases were included or excluded under those rules. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/cli.py:1772-1837` loads `manifest.json`, `included.jsonl`, and `excluded.jsonl`, supports `--show included|excluded|all` plus `--candidate-id`, and prints included/excluded traces with source bundles and exclusion reasons; CLI tests in `materials-discovery/tests/test_llm_translated_benchmark_cli.py:234-327` verify summary output, filtering, and failure behavior; docs in `materials-discovery/developers-docs/pipeline-stages.md:1282-1315` and `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md:67-101` expose the inspect workflow. |
| 3 | The frozen benchmark set records its source translation bundles and filter contract as file-backed lineage that can be reused unchanged in later benchmark runs. | ✓ VERIFIED | `materials-discovery/src/materials_discovery/llm/storage.py:247-275` fixes the artifact layout under `data/benchmarks/llm_external_sets/{benchmark_set_id}/`; `materials-discovery/src/materials_discovery/llm/translated_benchmark.py:156-249` writes `freeze_contract.json`, `manifest.json`, `included.jsonl`, and `excluded.jsonl`, plus manifest lineage fields `source_bundle_manifest_paths`, `source_export_ids`, and `exclusion_reason_counts`; regression coverage in `materials-discovery/tests/test_llm_translated_benchmark_freeze.py:338-419` validates written lineage and repeat-run stability. |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
| --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/schema.py` | Typed freeze contract, inclusion/exclusion rows, manifest, summary | ✓ VERIFIED | Contains substantive models for `TranslatedBenchmarkSetSpec`, `TranslatedBenchmarkIncludedRow`, `TranslatedBenchmarkExcludedRow`, `TranslatedBenchmarkSetManifest`, and `TranslatedBenchmarkSetSummary` at `:1645-1806`. |
| `materials-discovery/src/materials_discovery/llm/storage.py` | Deterministic benchmark-pack storage helpers | ✓ VERIFIED | Exposes `translated_benchmark_set_dir`, `translated_benchmark_contract_path`, `translated_benchmark_manifest_path`, `translated_benchmark_included_path`, and `translated_benchmark_excluded_path` at `:247-275`, all under `llm_external_sets`. |
| `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` | Freeze engine, spec loader, duplicate handling, artifact writers | ✓ VERIFIED | Loads YAML spec, reads shipped translation bundles, evaluates row eligibility, writes persisted artifacts, and returns `TranslatedBenchmarkSetSummary` at `:49-249`. |
| `materials-discovery/src/materials_discovery/cli.py` | Operator freeze and inspect commands | ✓ VERIFIED | `llm-translated-benchmark-freeze` and `llm-translated-benchmark-inspect` are implemented at `:1755-1837` with exit-code-2 error handling. |
| `materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml` | Runnable example spec with explicit rules and shipped bundle inputs | ✓ VERIFIED | Declares `benchmark_set_id`, `bundle_manifest_paths`, `systems`, `target_family`, `allowed_fidelity_tiers`, `loss_posture`, and an operator note at `:1-13`. |
| `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md` | Operator runbook for freeze, inspect, artifact layout, and scope boundary | ✓ VERIFIED | Documents required inputs, CLI commands, artifact layout, exclusion interpretation, and Phase 35/36 deferrals at `:1-170`. |
| `materials-discovery/tests/test_llm_translated_benchmark_schema.py` | Contract and storage validation coverage | ✓ VERIFIED | Covers spec validation, typed vocabularies, lineage rows, manifest fields, and storage layout at `:61-190`. |
| `materials-discovery/tests/test_llm_translated_benchmark_freeze.py` | Freeze-core regression coverage | ✓ VERIFIED | Covers filtering, typed exclusions, duplicate handling, conflict failure, deterministic ordering, persisted lineage, and stable rewrites at `:111-419`. |
| `materials-discovery/tests/test_llm_translated_benchmark_cli.py` | CLI workflow coverage | ✓ VERIFIED | Covers JSON freeze summary, inspect output, filtering, and error cases at `:141-327`. |

### Key Link Verification

| From | To | Via | Status | Details |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/schema.py` | `materials-discovery/src/materials_discovery/llm/translation_bundle.py` | Bundle lineage reuse and translation inventory compatibility | WIRED | `TranslatedBenchmark*` rows reuse `TranslationBundleManifest`, `TranslationInventoryRow`, target-family, fidelity-tier, loss-reason, and diagnostic-code types; plan key-link check passed. |
| `materials-discovery/src/materials_discovery/llm/storage.py` | `materials-discovery/data/benchmarks/llm_external_sets` | Deterministic artifact layout | WIRED | Storage helpers resolve the dedicated `llm_external_sets` root and fixed filenames; plan key-link check passed. |
| `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` | `materials-discovery/src/materials_discovery/llm/schema.py` | Load source bundles and emit typed benchmark manifest/rows | WIRED | Imports `TranslationBundleManifest`, `TranslationInventoryRow`, `TranslatedBenchmarkSetManifest`, `TranslatedBenchmarkIncludedRow`, and `TranslatedBenchmarkExcludedRow`; writes typed artifacts. |
| `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` | `materials-discovery/src/materials_discovery/llm/storage.py` | Persist contract and inventories through fixed path helpers | WIRED | Uses `translated_benchmark_contract_path`, `translated_benchmark_manifest_path`, `translated_benchmark_included_path`, and `translated_benchmark_excluded_path` before writing files. |
| `materials-discovery/src/materials_discovery/cli.py` | `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` | Freeze and inspect command entrypoints | WIRED | Freeze command calls `freeze_translated_benchmark_set(...)`; inspect command reads `TranslatedBenchmarkSetManifest` and inventories shaped by the freeze engine. |
| `materials-discovery/developers-docs/llm-translated-benchmark-runbook.md` | `materials-discovery/configs/llm/al_cu_fe_translated_benchmark_freeze.yaml` | Operator example workflow | WIRED | Runbook points directly at the committed YAML spec and the committed demo bundle manifests. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
| --- | --- | --- | --- | --- |
| `materials-discovery/src/materials_discovery/llm/translated_benchmark.py` | `bundle_rows`, `included_rows`, `excluded_rows` | `_load_translation_bundle()` reads committed `TranslationBundleManifest` JSON plus `inventory.jsonl` rows, then `_evaluate_translation_row()` filters them | Yes. Spot-check on `configs/llm/al_cu_fe_translated_benchmark_freeze.yaml` loaded the shipped demo bundles and resolved `included=1`, `excluded=1`, `reasons={'target_family_mismatch': 1}`. | ✓ FLOWING |
| `materials-discovery/src/materials_discovery/cli.py` | `included_rows`, `excluded_rows` | `_load_translated_benchmark_rows()` loads paths from `TranslatedBenchmarkSetManifest` into typed included/excluded row objects | Yes. CLI tests validate manifest summary output, included/excluded traces, `--show`, and `--candidate-id` behavior against concrete manifest/inventory fixtures. | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| --- | --- | --- | --- |
| Phase 34 schema, freeze, CLI, and help slices pass their focused tests | `cd materials-discovery && uv run pytest tests/test_llm_translated_benchmark_schema.py tests/test_llm_translated_benchmark_freeze.py tests/test_llm_translated_benchmark_cli.py tests/test_cli.py -q` | `38 passed in 0.47s` | ✓ PASS |
| Shipped YAML spec resolves to an explicit CIF-only slice over real committed bundle inputs | `cd materials-discovery && uv run python - <<'PY' ... load_translated_benchmark_spec(...) + _load_translation_bundle(...) + _evaluate_translation_row(...) ... PY` | `{'benchmark_set_id': 'al_cu_fe_translated_benchmark_v1', 'target_family': 'cif', 'systems': ['Al-Cu-Fe'], 'included': 1, 'excluded': 1, 'reasons': {'target_family_mismatch': 1}}` | ✓ PASS |
| Root CLI help exposes the operator workflow | `cd materials-discovery && uv run mdisc --help` | Help output listed both `llm-translated-benchmark-freeze` and `llm-translated-benchmark-inspect` | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| `LLM-31` | `34-01`, `34-02`, `34-03` | Operator can freeze a translated benchmark set from one or more shipped translation bundles with explicit inclusion and exclusion rules by system, target family, fidelity tier, and representational-loss posture. | ✓ SATISFIED | Typed contract in `schema.py`, deterministic storage in `storage.py`, freeze engine in `translated_benchmark.py`, CLI/operator surface in `cli.py`, shipped example spec and demo bundles, and passing focused tests together satisfy the requirement end to end. |

Orphaned requirements for Phase 34: none.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| --- | --- | --- | --- | --- |
| Phase 34 implementation set | n/a | No TODO/FIXME/placeholder/stub markers or hollow implementations found in the phase files scanned from the plan summaries. | Info | No blocker anti-patterns detected. |

### Human Verification Required

None required for phase-goal verification. The delivered surface is CLI-first and file-backed, and the critical behaviors were verified through code inspection plus focused automated spot-checks.

### Gaps Summary

No gaps found. Phase 34 delivers the explicit freeze contract, deterministic benchmark-pack artifact layout, real freeze engine, inspectable included/excluded inventories, operator-facing CLI commands, shipped example inputs, and supporting documentation required by the roadmap goal and `LLM-31`.

---

_Verified: 2026-04-07T06:25:13Z_
_Verifier: Codex (gsd-verifier)_
