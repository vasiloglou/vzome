# Progress

## Changelog

| Date | Change | Details |
|------|--------|---------|
| 2026-03-22 | Initial Progress.md created | Tracking document for experiments and actions |
| 2026-03-22 | Added Ti-Zr-Ni system | New ternary icosahedral quasicrystal target; element priors, pair enthalpies, mock config, template path, execution plan updated |
| 2026-03-23 | Added LLM-quasicrystal landscape doc | New developer doc covering how LLMs and AI models interact with quasicrystals: challenges, workflows, MLIP simulation, diffusion models, TSAI, and LLM-QC analogy |
| 2026-03-23 | Ran ingest for Ti-Zr-Ni | 3 reference phases ingested (i-phase, approximant, C14-Laves); QA passed; fixture updated with Ti-Zr-Ni rows |
| 2026-03-23 | Executed Ti-Zr-Ni export-zomic | Zomic design compiled to orbit library: 22 sites (10 icosa, 8 shell, 4 bridge) across 3 orbits |
| 2026-04-02 | Moved materials discovery docs into workspace | Relocated `developer-docs/materials_discovery` to `materials-discovery/developers-docs` and updated links/references |
| 2026-04-03 | Added source staging runtime foundation | Created `materials_discovery.data_sources` core modules, source manifest/QA models, storage/runtime helpers, and ingestion optional dependencies for Phase 2 |
| 2026-04-03 | Added additive ingestion config seam | Extended `SystemConfig` with `ingestion`, reserved the `source_registry_v1` bridge adapter key, and kept the current ingest path unchanged |
| 2026-04-03 | Added source runtime contract tests | Introduced focused pytest coverage for canonical raw-source schema validation, source adapter registry behavior, and QA aggregation edge cases |
| 2026-04-03 | Hardened native provider optional-dependency test | Relaxed the MD-provider missing-dependency assertion so the full suite stays valid whether `ase` or an ASE-compatible calculator is the first unavailable optional component |
| 2026-04-03 | Refreshed ingestion dependency lockfile | Updated `uv.lock` so the new `ingestion` extra resolves `httpx` and its transitive dependencies alongside the existing workspace extras |
| 2026-04-03 | Added HYPOD-X and COD source adapters | Implemented the first offline provider adapters on the new source runtime, including HYPOD-X fixture/pinned staging, CIF conversion, COD staging, and deterministic adapter tests |
| 2026-04-03 | Added API and OPTIMADE source adapters | Implemented shared OPTIMADE normalization plus offline Materials Project, OQMD, and JARVIS adapters, with compatibility tests proving legacy CLI configs still work without `ingestion` |
| 2026-04-03 | Added canonical source projection bridge core | Implemented `data_sources/projection.py`, deterministic system/phase/dedupe rules, a reusable `ProjectionSummary`, and focused tests proving projected rows remain consumable by downstream reference-phase logic |
| 2026-04-03 | Wired source-registry ingest into the CLI | Turned `source_registry_v1` into a real `mdisc ingest` path with staged snapshot reuse, additive ingest-manifest lineage, and offline bridge/CLI regression coverage |
| 2026-04-03 | Added source-backed pipeline compatibility coverage | Extended real-mode, hull, and report regressions for the new bridge, added an explicit no-DFT ingest guard, and hardened `active_learn` test setup against stale validated artifacts |
| 2026-04-03 | Phase 4: reference-pack assembly layer | Added `ReferencePackConfig`/`ReferencePackMemberConfig` schema models to `common/schema.py`, `ReferencePackManifest`/`ReferencePackMemberResult` to `data_sources/schema.py`, pack storage helpers to `storage.py`, and the full `data_sources/reference_packs.py` assembly module with deduplication, priority ordering, caching, and deterministic fingerprinting; covered by `tests/test_reference_packs.py` (15 tests) |
| 2026-04-03 | Phase 4: benchmark-ready reference-aware configs for Al-Cu-Fe and Sc-Zn | Added `al_cu_fe_reference_aware.yaml` and `sc_zn_reference_aware.yaml` with `source_registry_v1`, multi-source `reference_pack` blocks (HYPOD-X + MP for Al-Cu-Fe; HYPOD-X + COD for Sc-Zn), explicit priority ordering, benchmark corpus/validation snapshot hooks; staged thin second-source canonical fixtures; extended CLI to route `source_registry_v1` + `reference_pack` through `_ingest_via_reference_pack`; 31 deterministic benchmark/fixture tests |
| 2026-04-03 | Phase 4 Plan 02: comparable benchmark outputs across pipeline lanes | Added `BenchmarkRunContext` and `build_benchmark_run_context()` to `common/benchmarking.py`; `write_benchmark_pack()` emits a dedicated `benchmark_pack.json` artifact; additive `benchmark_context` field added to `ArtifactManifest`; `hifi-rank` and `report` CLI commands thread context into manifests and ranked/report outputs; `rank_validated_candidates()` embeds `calibration_provenance` and optional `benchmark_context` in candidate provenance; `compile_experiment_report()` surfaces context in evidence blocks and top-level report; 164 tests pass |

| 2026-04-03 | Phase 5 Plan 01: data lake metadata layer | Added `lake` package with `catalog.py` (CatalogEntry, DirectoryCatalog, ARTIFACT_DIRECTORIES with 17 entries, build_directory_catalog, write_catalog), `staleness.py` (hash-based + mtime-hint staleness detection), and `index.py` (LakeIndex, build_lake_index, write_lake_index, lake_stats); wired `mdisc lake index` and `mdisc lake stats` CLI subcommands; 15 new tests pass, 187 total |
| 2026-04-03 | Phase 5 Plan 02: cross-lane comparison engine | Added `lake/compare.py` with lane-centric model (LaneSnapshot, MetricDistribution, GateDelta, MetricDelta, ComparisonResult); dereferences benchmark-pack report paths to compute metric distributions (mean/min/max/std for 8 key metrics); wired `mdisc lake compare` CLI command with dual-format output (JSON + table); graceful fallback for missing report files; 10 new tests, 197 total |

## Diary

### 2026-03-22

- Created this progress document to maintain a timestamped record of all experiments and actions across the materials-discovery pipeline.
- Current state: RM0–RM1 complete; RM2–RM6 have runnable software pathways with four phases of scientific hardening applied. CLI/schema contracts are frozen.
- Target systems: Al-Cu-Fe, Al-Pd-Mn, Sc-Zn.

- **Added Ti-Zr-Ni (titanium-zirconium-nickel) as fourth target system.**
  - Rationale: well-known icosahedral quasicrystal former (Tsai-type, e.g. Ti₄₁.₅Zr₄₁.₅Ni₁₇).
  - Element properties added for Ti, Zr, Ni (atomic number, covalent radius, electronegativity, valence electrons).
  - Pairwise mixing-enthalpy proxies: Ni-Ti (−0.35 eV/atom), Ni-Zr (−0.49 eV/atom), Ti-Zr (~0.00 eV/atom).
  - Composition bounds: Ti 30–50%, Zr 25–45%, Ni 10–25% — covers the icosahedral phase region.
  - Template: icosahedral_approximant_1_1 (same family as Al-Cu-Fe).
  - Mock config: `configs/systems/ti_zr_ni.yaml`.
  - Prototype JSON (`data/prototypes/ti_zr_ni_icosahedral_1_1.json`) not yet authored — will fall back to generic icosahedral template until then.
  - Updated REAL_MODE_EXECUTION_PLAN.md and README.md.

### 2026-03-23

- **Added LLM & quasicrystal landscape documentation.**
  - New file: `materials-discovery/developers-docs/llm-quasicrystal-landscape.md`.
  - Covers: the fundamental challenge of LLMs with aperiodic structures (CIF periodicity assumption), how LLMs are used in QC workflows (CSLLM synthesizability, data interpretation), AI models that simulate/generate QCs (MLIPs, SCIGEN diffusion, NN-VMC electronic QCs, TSAI random forest), and the LLM-quasicrystal analogy.
  - Includes a section connecting the landscape to our pipeline's hybrid approach (Zomic representation, MLIP validation, planned LLM stages).
  - Linked from `materials-discovery/developers-docs/index.md` documentation map.
  - Also updated index.md Chemical Systems table to include Ti-Zr-Ni.

- **Executed Stage 1 (ingest) for Ti-Zr-Ni.**
  - Added 3 Ti-Zr-Ni reference phases to `data/external/fixtures/hypodx_sample.json`:
    - i-phase: Ti₄₁.₅Zr₄₁.₅Ni₁₇ (the canonical icosahedral composition)
    - approximant: Ti₃₆Zr₃₆Ni₂₈
    - C14-Laves: Ti₃₃Zr₃₃Ni₃₄ (competing phase for proxy hull)
  - Ran `mdisc ingest --config configs/systems/ti_zr_ni.yaml` successfully.
  - Output: `data/processed/ti_zr_ni_reference_phases.jsonl` (3 deduped rows).
  - Manifest: `data/manifests/ti_zr_ni_ingest_manifest.json`.
  - QA: 0% invalid rate, 0% duplicate rate, passed.
  - Updated `tests/test_ingest.py` assertion (raw_count 5 → 8) to reflect new fixture rows.

- **Executed Stage 2 (export-zomic) for Ti-Zr-Ni.**
  - Created `designs/zomic/ti_zr_ni_tsai_bridge.zomic`: Tsai-type icosahedral cluster motif with icosa (vertex), shell (outer/inner), and bridge (connector) orbits.
  - Created `designs/zomic/ti_zr_ni_tsai_bridge.yaml`: design config with 14.2A cell, preferred species (Ti/Zr on icosa vertices, Ni/Ti on shells, Ni on bridges).
  - Ran `mdisc export-zomic --design designs/zomic/ti_zr_ni_tsai_bridge.yaml` successfully (JDK 21 installed).
  - Output: `data/prototypes/generated/ti_zr_ni_tsai_bridge.json` — 22 sites across 3 orbits:
    - **icosa**: 10 sites (preferred: Ti, Zr) — icosahedral vertex positions
    - **shell**: 8 sites (preferred: Ni, Ti) — outer/inner shell positions
    - **bridge**: 4 sites (preferred: Ni) — connector positions
  - Raw export: `data/prototypes/generated/ti_zr_ni_tsai_bridge.raw.json`.

### 2026-04-02

- 19:10 EDT — Moved the materials discovery developer documentation from `developer-docs/materials_discovery/` to `materials-discovery/developers-docs/`.
- Updated internal references in `materials-discovery/README.md`, the moved documentation set, and this progress log to point at the new location.

### 2026-04-03

- 09:25 EDT — Started Phase 2 execution for the Material Design Data Ingestion project after the GSD executor stalled; switched to direct execution for Wave 1.
- Landed the `materials_discovery.data_sources` foundation package with canonical raw-source models, source adapter protocols, source registry helpers, storage path helpers, QA aggregation, source snapshot manifests, and a staging runtime entrypoint.
- Added the `ingestion` optional dependency group to `pyproject.toml` with `httpx` and `pymatgen` pinned for later API and structure-conversion adapters.
- 09:41 EDT — Extended `SystemConfig` with an additive `ingestion` block (`source_key`, `adapter_key`, `snapshot_id`, `use_cached_snapshot`, `query`, `artifact_root`) and reserved the `source_registry_v1` ingest adapter key in `backends/registry.py` without wiring it into the existing CLI flow yet.
- 10:02 EDT — Added focused Phase 2 contract tests for `CanonicalRawSourceRecord`, the source adapter registry, and QA duplicate/missing-field/schema-drift accounting so later provider adapters have a stable baseline.
- 10:11 EDT — Hardened `tests/test_native_providers.py` so the full-suite optional-dependency check accepts the clean failure path when `ase` itself is absent, not only the later missing-calculator branch.
- 10:16 EDT — Refreshed `uv.lock` after adding the `ingestion` extra so the lockfile now captures `httpx`, `httpcore`, `anyio`, and the updated extra metadata expected by `uv`.
- 10:34 EDT — Added the first concrete `data_sources` adapters: HYPOD-X fixture/pinned staging on the new runtime plus a local CIF-to-canonical conversion path for COD, together with offline pytest coverage and a checked-in `cod_sample.cif` fixture.
- 10:53 EDT — Added the Wave 3 adapter layer: a shared OPTIMADE adapter base, direct offline Materials Project and OQMD adapters, a dedicated `jarvis.py` OPTIMADE bridge, and test coverage that keeps the legacy `mdisc ingest` CLI path green without an `ingestion` block.
- 09:58 EDT — Added the Phase 3 projection seam in `materials_discovery.data_sources.projection`, including deterministic system matching from canonical source hints, explicit phase-name fallback precedence, additive source provenance in processed `metadata`, a reusable `ProjectionSummary`, and focused pytest coverage plus a downstream `hull_proxy` compatibility check.
- 10:08 EDT — Wired `source_registry_v1` into `mdisc ingest` by branching the CLI onto staged canonical source snapshots, adding cached-snapshot reuse rules, extending the standard ingest manifest with additive `source_lineage`, and covering the bridge path with offline source-registry, CLI, and non-ingest-manifest regression tests.
- 10:27 EDT — Closed Phase 3 with source-backed real-mode smoke coverage, projected-row downstream compatibility checks for `hull_proxy` and `report`, an explicit ingest no-DFT guard, and a deterministic `test_active_learn.py` cleanup that removes stale validated outputs before preparing new fixtures.
- Phase 4 Plan 01 Task 1 — Added the explicit reference-pack assembly layer (commit 0ab3bfce):
  - `common/schema.py`: added `ReferencePackMemberConfig` and `ReferencePackConfig` (config-layer models for `ingestion.reference_pack`); made `IngestionConfig.source_key` optional when `reference_pack` is set.
  - `data_sources/schema.py`: added `ReferencePackMemberResult` and `ReferencePackManifest` (disk-artifact models).
  - `data_sources/storage.py`: added `reference_pack_dir`, `reference_pack_canonical_records_path`, `reference_pack_manifest_path` with an optional `pack_root` override.
  - `data_sources/reference_packs.py` (new): `assemble_reference_pack` — loads staged canonical records per member, deduplicates across sources using explicit priority ordering (QC sources win), writes `canonical_records.jsonl` + `pack_manifest.json`, reuses complete cached packs when configured; `assemble_reference_pack_from_config` convenience wrapper; `load_cached_pack_manifest` helper.
  - `tests/test_reference_packs.py` (new): 15 deterministic offline tests covering config validation, single/multi-source assembly, deduplication, manifest field completeness, member lineage, cache reuse, cache bypass, missing-source errors, fingerprint determinism, and explicit priority ordering.
- Phase 4 Plan 02 — Added output-side comparability layer (3 tasks committed):
  - Task 1 (`BenchmarkRunContext` + `benchmark_pack.json`): introduced `BenchmarkRunContext` dataclass, `build_benchmark_run_context()`, and `write_benchmark_pack()` in `common/benchmarking.py`; added additive `benchmark_context` field to `ArtifactManifest`; updated `build_manifest()` signature; added `_load_benchmark_context()` helper in `cli.py` that reads ingest manifest lineage; wired context into `hifi-rank` manifest and `report` manifest + benchmark-pack artifact.
  - Task 2 (provenance in rank and report): `rank_validated_candidates()` now embeds `calibration_provenance` (source, benchmark_corpus, backend_mode) and optional `benchmark_context` in each ranked candidate's `hifi_rank` block; `compile_experiment_report()` surfaces these in per-entry evidence blocks and at the report top level via `_extract_benchmark_context()`.
  - Task 3 (regression coverage): extended all three test files — `test_benchmarking.py` adds `TestBuildBenchmarkRunContext` (8 tests, both Phase 4 systems, cross-lane key alignment); `test_hifi_rank.py` adds 3 provenance assertions; `test_report.py` adds `test_report_emits_benchmark_context_*`, `test_benchmark_pack_written_by_report_command`, and `test_cross_lane_benchmark_context_keys_match`; total 164 tests passing.

- Phase 4 Plan 03 Task 3 — Locked final cross-lane comparison story for Al-Cu-Fe:
  - `tests/test_report.py`: added `test_cross_lane_comparison_al_cu_fe_baseline_vs_reference_aware` comparing the baseline real lane (`al_cu_fe_real.yaml`) against the reference-aware real lane (`al_cu_fe_reference_aware.yaml`); asserts that both produce identical benchmark_context key sets, that lane_ids and reference_pack_ids differ visibly, that the reference-aware lane surfaces both source_keys (hypodx + materials_project) while the baseline carries none, and that per-entry evidence blocks carry calibration_provenance in both lanes.
  - Total test count: 172 passing (was 171).

- Phase 4 Plan 03 Task 2 — Added two-system end-to-end benchmark regression coverage:
  - `tests/test_real_mode_pipeline.py`: added `test_al_cu_fe_reference_aware_benchmark_e2e` and `test_sc_zn_reference_aware_benchmark_e2e` (both `@pytest.mark.integration @pytest.mark.benchmark_lane`); each runs the full ingest→generate→screen→hifi-validate→hifi-rank→active-learn→report pipeline and asserts on ingest pack lineage (pack_id, member_sources), pipeline manifest, and benchmark_pack.json structure (schema_version, system, backend_mode, benchmark_context, stage_manifest_paths, report_metrics); Sc-Zn test gracefully skips generate+ stages when Java is absent.
  - `tests/test_hifi_rank.py`: added `test_sc_zn_reference_aware_rank_embeds_benchmark_context` (Sc-Zn rank embeds sc_zn_v1 benchmark_context in provenance) and `test_both_phase4_benchmark_configs_have_comparable_context_keys` (both Phase 4 configs produce BenchmarkRunContext with identical key sets and distinct lane_ids).
  - `tests/test_report.py`: added `test_al_cu_fe_reference_aware_benchmark_pack_context`, `test_sc_zn_reference_aware_benchmark_pack_context`, and `test_both_phase4_benchmark_configs_report_context_keys_match` covering both systems' report-level benchmark_context embedding.
  - `pyproject.toml`: registered `benchmark_lane` pytest marker for the slower two-system E2E lane.
  - Total test count: 171 passing (was 164).

- Phase 4 Plan 03 Task 1 — Added operator benchmark runner script and runbook docs:
  - `scripts/run_reference_aware_benchmarks.sh` (new): config-driven two-system benchmark runner for the Phase 4 Al-Cu-Fe and Sc-Zn reference-aware lanes; supports `--count`, `--seed`, `--config-filter`, `--no-active-learn`, and `--dry-run` overrides; reports benchmark-pack artifact paths on completion.
  - `developers-docs/reference-aware-benchmarks.md` (new): operator runbook covering prerequisites (Python env, Java/Zomic dependency for Sc-Zn), full and smoke run commands, benchmark config descriptions, reference-pack input paths, benchmark-pack output structure, and regression test commands.
  - `README.md`: added Phase 4 benchmark runner quickstart section with link to runbook.
  - `developers-docs/index.md`: added runbook to Documentation Map and Phase 4 reference-aware configs to Chemical Systems table.

- Phase 5 Plan 01 — Built data lake metadata layer (Phase 5, Plan 01):
  - `lake/__init__.py` (new): package init.
  - `lake/catalog.py` (new): `CatalogEntry` Pydantic model (artifact_type, directory_path, schema_version, record_count, last_modified_utc, lineage, size_bytes, is_stale, content_hash); `DirectoryCatalog` model; `ARTIFACT_DIRECTORIES` dict with 17 entries covering all artifact subdirectories (addresses review concern #3); `build_directory_catalog()` scanning JSONL lines and JSON files with workspace-relative paths (addresses review concern #5); `write_catalog()` writing `_catalog.json`.
  - `lake/staleness.py` (new): `check_staleness()` with hash-based detection using manifest output_hashes plus mtime hint (addresses review concern #1).
  - `lake/index.py` (new): `LakeIndex` Pydantic model; `build_lake_index()` iterating over all ARTIFACT_DIRECTORIES and building + writing per-directory catalogs; `write_lake_index()` writing `data/lake_index.json`; `lake_stats()` producing summary stats.
  - `cli.py`: added `lake_app` Typer sub-application; `mdisc lake index` command running build+write; `mdisc lake stats` command loading or rebuilding the index and printing a summary table.
  - Tests: `test_lake_catalog.py` (9 tests), `test_lake_index.py` (6 tests). Total: 187 tests passing.

- Phase 4 Plan 01 Task 2 — Added benchmark-ready reference-aware configs and second-source fixtures:
  - `configs/systems/al_cu_fe_reference_aware.yaml` (new): source_registry_v1, real mode, HYPOD-X + Materials Project reference pack (priority order: hypodx > materials_project), benchmark corpus and validation snapshot wired.
  - `configs/systems/sc_zn_reference_aware.yaml` (new): source_registry_v1, real mode, Zomic design path preserved, HYPOD-X + COD reference pack (priority order: hypodx > cod), benchmark corpus and validation snapshot wired.
  - `data/external/sources/materials_project/mp_fixture_v1/canonical_records.jsonl` (new): thin 2-record MP fixture for Al-Cu-Fe multi-source proof.
  - `data/external/sources/cod/cod_fixture_v1/canonical_records.jsonl` (new): thin 1-record COD fixture for Sc-Zn multi-source proof.
  - `data/external/sources/hypodx/hypodx_pinned_2026_03_09/canonical_records.jsonl` (new): staged canonical records from the pinned HYPOD-X snapshot.
  - `data/external/sources/hypodx/hypodx_fixture_local/canonical_records.jsonl` (new): staged canonical records from the local HYPOD-X fixture for Sc-Zn.
  - `cli.py`: added `_ingest_via_reference_pack` function; updated ingest command to detect `ingestion.reference_pack` and route through the reference-pack assembly path.
  - `tests/test_benchmarking.py`: extended with 31 new deterministic tests asserting config validity, pack IDs, member source keys, snapshot IDs, priority ordering, benchmark corpus/validation-snapshot hooks, zomic-design preservation (Sc-Zn), and second-source fixture existence.

### 2026-04-03 (Phase 5 Plan 02)

- Phase 5 Plan 02 — Built cross-lane comparison engine and wired `mdisc lake compare` CLI command:
  - `lake/compare.py` (new): lane-centric internal model with `MetricDistribution` (mean, min, max, std, count), `LaneSnapshot` (loads from benchmark_pack.json, dereferences stage_manifest_paths["report"] to read deeper report entries for per-candidate metric aggregation), `GateDelta` (with status: both_pass/both_fail/regression/improvement), `MetricDelta`, and `ComparisonResult` (schema_version "comparison/v1").
  - `compare_benchmark_packs()`: builds LaneSnapshot for each pack, computes gate deltas and metric distribution diffs (8 key metrics: hifi_score, stability_probability, ood_score, xrd_confidence, xrd_distinctiveness, delta_e_proxy_hull_ev_per_atom, uncertainty_ev_per_atom, md_stability_score).
  - `write_comparison()`: writes JSON to `data/comparisons/` with slugified filename (D-06).
  - `format_comparison_table()`: produces dual-format terminal table with header, gate section, and metric section (D-06).
  - Graceful fallback: if report file missing, warns and falls back to report_metrics embedded in benchmark pack (no crash).
  - `cli.py`: added `@lake_app.command("compare")` with explicit pack_a/pack_b positional args (D-08), optional `--output-dir` and `--json-only` flags.
  - `tests/test_lake_compare.py` (new): 10 tests covering all 7 planned behaviors plus CLI integration. 197 total tests passing.
  - Addresses: PIPE-04, D-06, D-07, D-08, review concern #2 (data depth), review concern #6 (lane-centric model).
