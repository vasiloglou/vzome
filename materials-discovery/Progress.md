# Progress

## Changelog

| Date | Change | Details |
|------|--------|---------|
| 2026-04-04 | Phase 11 Plan 03 launch continuation docs | Documented `mdisc llm-launch`, launch wrapper artifacts, manual downstream continuation, failure posture, and a lineage-audit path in the LLM and pipeline developer docs |
| 2026-04-04 | Phase 11 Plan 03 campaign lineage propagation | Threaded additive `llm_campaign` lineage into launched `llm_generate` manifests, downstream stage manifests, and pipeline manifests, with focused downstream-lineage and mock continuation regression coverage |
| 2026-04-04 | Phase 11 Plan 03 RED tests | Added failing downstream-lineage and mock end-to-end launch regressions in `test_llm_campaign_lineage.py`, `test_report.py`, and `test_real_mode_pipeline.py` before wiring campaign lineage through later pipeline stages |
| 2026-04-04 | Phase 11 Plan 02 Task 2 llm-launch CLI | Added the new `mdisc llm-launch --campaign-spec ...` command, wrote resolved/summary launch artifacts, validated config-hash drift before runtime execution, and preserved partial-failure auditability |
| 2026-04-04 | Phase 11 Plan 02 Task 2 RED tests | Added `tests/test_llm_launch_cli.py` and a shared `test_cli.py` smoke case to lock `llm-launch` success and config-drift failure behavior before wiring the CLI |
| 2026-04-04 | Phase 11 Plan 02 Task 1 campaign-aware llm-generate | Added prompt instruction deltas and campaign launch metadata to the LLM generation request/run-manifest flow while keeping manual `llm-generate` behavior unchanged |
| 2026-04-04 | Phase 11 Plan 02 Task 1 RED tests | Extended `tests/test_llm_generate_core.py` to lock prompt instruction deltas and campaign-aware run/provenance metadata before modifying `llm-generate` |
| 2026-04-04 | Phase 11 Plan 01 Task 2 launch resolution | Added `llm/launch.py` with deterministic lane selection, prompt/composition overlays, eval-set seed materialization, and exported campaign launch helpers |
| 2026-04-04 | Phase 11 Plan 01 Task 2 RED tests | Added `tests/test_llm_launch_core.py` to lock deterministic lane, prompt, composition, and seed resolution behavior before implementing `llm/launch.py` |
| 2026-04-04 | Phase 11 Plan 01 Task 1 launch contracts | Added lane-aware `llm_generate.model_lanes`, typed launch summary models, and deterministic campaign launch storage helpers |
| 2026-04-04 | Phase 11 Plan 01 Task 1 RED tests | Added `tests/test_llm_launch_schema.py` to lock lane-aware config validation, launch summary contracts, and campaign launch storage paths before implementation |
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
| 2026-04-03 | Phase 5 Plan 03 Task 1: analytics notebooks and smoke tests | Three starter notebooks (source_contribution_analysis, cross_run_drift_detection, metric_distribution_deep_dive) under `notebooks/`; each uses workspace_root() and degrades gracefully when data is absent; `tests/test_notebooks.py` with 3 static + 3 conditional execution smoke tests |
| 2026-04-03 | Phase 5 Plan 03 Task 2: unified operator RUNBOOK.md | 8-section runbook covering prerequisites, ingestion, reference-pack assembly, pipeline execution, benchmarking, data lake operations, analytics notebooks, and troubleshooting; 53+ code blocks; full mdisc command quick-reference table |
| 2026-04-03 | Phase 5 complete: data lake and analysis layer | All 3 plans executed across 3 waves; verification passed 15/15 must-haves; 200 tests passing; all 6 cross-AI review concerns addressed; PIPE-04 and PIPE-05 satisfied |
| 2026-04-03 | Phase 6 Plan 01 Task 1: LLM corpus contracts and config | Added the new `materials_discovery.llm` schema package, committed `configs/llm/corpus_v1.yaml`, and introduced schema-focused pytest coverage for corpus config, provenance, inventory rows, validation state, and build summaries |
| 2026-04-03 | Phase 6 Plan 01 Task 2: LLM corpus storage and manifest helpers | Added deterministic `data/llm_corpus/{build_id}` path helpers, corpus fingerprint/manifest builders, and focused pytest coverage for workspace-relative manifest paths and persisted manifest JSON |
| 2026-04-03 | Phase 6 Plan 02 Task 1: LLM corpus inventory layer | Added offline inventory collectors for repo Zomic scripts, candidate JSONL records, generated raw exports, canonical source/reference-pack records, and a committed PyQCstrc projection fixture, with deterministic sorting and focused pytest coverage |
| 2026-04-03 | Phase 6 Plan 02 Task 2: LLM corpus QA grading and dedupe | Added typed gold/silver/reject grading, deterministic duplicate resolution, QA summaries, and focused pytest coverage for release-tier promotion, label validation, and issue tallies |
| 2026-04-03 | Phase 6 Plan 03 Task 1: deterministic record2zomic conversion | Added the shared axis-walk decomposition helper, deterministic `CandidateRecord -> Zomic` serialization with conversion traces, and focused pytest coverage for ordering, label preservation, and duplicate-label disambiguation |
| 2026-04-03 | Phase 6 Plan 03 Task 2: compile helper and projection2zomic | Added a bridge-backed temporary compile helper, a PyQCstrc projection payload conversion path, and focused pytest coverage for compile success/failure reporting and deterministic cell scaling |
| 2026-04-03 | Phase 6 Plan 04 Task 1: CIF/open approximant conversion | Added CIF-driven corpus conversion for COD and HYPOD-X-style fixtures, plus canonical-record fallback handling and focused pytest coverage that stays green with the existing prototype/COD tests |
| 2026-04-03 | Phase 6 Plan 04 Task 2: native and generated source loaders | Added explicit loaders for repo-native `.zomic` files and generated raw export artifacts, with exact vs anchored fidelity handling and focused pytest coverage for loader-hint alignment |
| 2026-04-03 | Phase 6 Plan 04 Task 3: end-to-end corpus builder | Added the inventory-driven corpus builder that routes all loader hints, validates/grades/dedupes examples, and writes syntax/materials/rejects/inventory/QA/manifest artifacts under `data/llm_corpus/{build_id}` |
| 2026-04-03 | Phase 6 Plan 04 Task 4: llm-corpus CLI command | Added the `mdisc llm-corpus build` sub-application/command, JSON summary output, and focused CLI tests for success, invalid configs, and workspace-relative config paths |
| 2026-04-03 | Phase 7 Plan 01: llm-generate contracts and runtime seam | Added additive `llm_generate` config/schema contracts, Phase 7 runtime request/attempt/run-manifest models, the `llm_fixture_v1` / `anthropic_api_v1` adapter seam, configuration docs, and focused schema/runtime pytest coverage |
| 2026-04-03 | Phase 7 Plan 02: llm-generate core path | Added config-driven prompt assembly, bounded retry generation, compile-backed candidate conversion, the `mdisc llm-generate` CLI command, committed mock configs, and focused core/CLI pytest coverage |
| 2026-04-03 | Phase 7 Plan 03: llm benchmark and docs layer | Added the offline deterministic-vs-LLM comparison helper, benchmark runner script, docs refresh, pytest marker, and two-system benchmark regression coverage for Al-Cu-Fe and Sc-Zn |
| 2026-04-03 | Phase 8 Plan 01: llm-evaluate contracts and CLI path | Added additive `llm_evaluate` config/summary contracts, typed evaluation request/assessment/run-manifest models, the `llm/evaluate.py` engine, the `mdisc llm-evaluate` CLI command, and focused schema/CLI pytest coverage |
| 2026-04-03 | Phase 8 Plan 02: report and rank LLM-assessment integration | Taught `report` to prefer `*_all_llm_evaluated.jsonl`, surfaced additive `llm_assessment` context in report entries/calibration, and added regressions proving `hifi-rank` preserves but does not reweight that context |
| 2026-04-03 | Phase 8 Plan 03: downstream LLM pipeline benchmarks | Added the downstream deterministic-vs-LLM benchmark helper, the `run_llm_pipeline_benchmarks.sh` operator script, refreshed LLM docs, and added offline Al-Cu-Fe/Sc-Zn benchmark regression coverage |
| 2026-04-03 | Phase 9 Plan 01: eval-set and acceptance-pack contracts | Added typed eval-set and acceptance-pack models, new storage/helpers for exporting eval sets from the Phase 6 corpus, and focused acceptance-schema pytest coverage |
| 2026-04-03 | Phase 9 Plan 02: conditioned llm-generate prompts | Added optional eval-set-backed example conditioning for `llm-generate`, prompt/run-manifest lineage for selected examples, and focused core/CLI regressions proving the path remains optional |
| 2026-04-03 | Phase 9 Plan 03: acceptance benchmark and llm-suggest | Added the operator acceptance benchmark script, the dry-run `mdisc llm-suggest` command, refreshed LLM docs, and closed the full suite at 297 passed |
| 2026-04-04 | Phase 10 Plan 01 Task 1 RED: campaign schema tests | Added failing pytest coverage for typed campaign proposals, action-family payload validation, separate approvals, and campaign-spec lineage before implementing the new governance contract |
| 2026-04-04 | Phase 10 Plan 01 Task 1 GREEN: campaign governance schema | Added the additive Phase 10 proposal, approval, launch-baseline, lineage, and campaign-spec models in `llm/schema.py`, exported them from `llm/__init__.py`, and aligned them with the new focused schema tests |
| 2026-04-04 | Phase 10 Plan 01 Task 2 RED: campaign storage tests | Added failing pytest coverage for deterministic suggestion, proposal, approval, and campaign-spec artifact paths plus blank-ID rejection before implementing the new storage helpers |
| 2026-04-04 | Phase 10 Plan 01 Task 2 GREEN: campaign storage helpers | Added deterministic acceptance-pack and campaign artifact path helpers in `llm/storage.py`, exported them from `llm/__init__.py`, and made blank artifact IDs fail fast instead of producing malformed paths |
| 2026-04-04 | Phase 10 Plan 02 Task 1 RED: typed llm-suggest core tests | Added failing pytest coverage for acceptance-pack to typed campaign-proposal mapping, deterministic action IDs, release-gate handling, and proposal-summary path emission before migrating `llm-suggest` off the legacy suggestion model |
| 2026-04-04 | Phase 10 Plan 02 Task 1 GREEN: typed proposal mapping and writer | Added `llm/campaigns.py`, migrated `llm-suggest` to typed campaign suggestions plus per-proposal artifact writing, exported the new helpers, and updated the acceptance-benchmark caller to the new contract |
| 2026-04-04 | Phase 10 Plan 02 Task 2 RED: llm-suggest CLI bundle tests | Added failing CLI coverage for typed stdout, default `suggestions.json`, per-system `proposals/` writing, invalid-input exit handling, and the shared `test_cli.py` migration to the new bundle contract |
| 2026-04-04 | Phase 10 Plan 02 Task 2 GREEN: llm-suggest typed CLI contract | Updated `mdisc llm-suggest` to write the typed suggestion bundle plus proposal artifacts through `suggest.py`, print the persisted typed JSON contract, and pass the focused CLI regression slice |
| 2026-04-04 | Phase 10 Plan 03: campaign approval and spec materialization | Added deterministic approval/spec helpers, acceptance-pack-root artifact-root derivation, and focused pytest coverage for approved, rejected, and re-approval campaign flows |
| 2026-04-04 | Phase 10 Plan 03: llm-approve CLI governance boundary | Added the non-launching `mdisc llm-approve` command, refreshed LLM developer docs, updated shared CLI coverage, and closed the full `materials-discovery` suite at 332 passed, 3 skipped |

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

- Phase 5 Plan 03 Task 2 — Wrote unified operator RUNBOOK.md:
  - `RUNBOOK.md` (new, at materials-discovery root for high visibility per D-13).
  - 8 major sections: Prerequisites, Ingestion (single + reference-pack), Reference Pack Assembly, Pipeline Execution (all 6 stages), Benchmarking (runner + artifact structure), Data Lake Operations (index/stats/compare), Analytics Notebooks (launch + config), Troubleshooting (5 sub-sections).
  - Copy-pasteable command blocks throughout (per D-14); troubleshooting entries each have Symptom/Cause/Resolution structure with commands (per D-15).
  - Section 8 Quick Reference: full mdisc command table (11 commands), key file paths, config file locations, and pointers to deep-dive developer docs.
  - 53 code blocks covering all mdisc commands, config YAML examples, artifact JSON structure, and diagnostic commands.

- Phase 5 Plan 03 Task 1 — Created three analytics notebooks and notebook smoke tests:
  - `notebooks/source_contribution_analysis.ipynb` (new): loads report JSON, groups candidates by source (via benchmark_context.source_keys and evidence.calibration_provenance), renders grouped bar chart by priority (high/medium/watch), top-N candidate table, and summary text.
  - `notebooks/cross_run_drift_detection.ipynb` (new): loads two benchmark packs as LaneSnapshots, runs compare_benchmark_packs, renders gate pass/fail comparison bar chart and metric distribution side-by-side bars with error bars, and delta interpretation table.
  - `notebooks/metric_distribution_deep_dive.ipynb` (new): loads one or more report JSONs, renders histograms for hifi_score/stability_probability/ood_score, scatter for xrd_confidence vs xrd_distinctiveness, and a summary statistics table; supports overlay mode for cross-run comparison.
  - All notebooks use `workspace_root()` for data path construction and degrade gracefully when data files are missing.
  - `tests/test_notebooks.py` (new): 6 tests — 3 static (valid JSON, imports from materials_discovery, uses workspace_root) always run; 3 execution smoke tests (via nbconvert + fixture workspace injection) skip gracefully when nbformat/nbconvert not installed.

- Phase 5 Plan 02 — Built cross-lane comparison engine and wired `mdisc lake compare` CLI command:
  - `lake/compare.py` (new): lane-centric internal model with `MetricDistribution` (mean, min, max, std, count), `LaneSnapshot` (loads from benchmark_pack.json, dereferences stage_manifest_paths["report"] to read deeper report entries for per-candidate metric aggregation), `GateDelta` (with status: both_pass/both_fail/regression/improvement), `MetricDelta`, and `ComparisonResult` (schema_version "comparison/v1").
  - `compare_benchmark_packs()`: builds LaneSnapshot for each pack, computes gate deltas and metric distribution diffs (8 key metrics: hifi_score, stability_probability, ood_score, xrd_confidence, xrd_distinctiveness, delta_e_proxy_hull_ev_per_atom, uncertainty_ev_per_atom, md_stability_score).
  - `write_comparison()`: writes JSON to `data/comparisons/` with slugified filename (D-06).
  - `format_comparison_table()`: produces dual-format terminal table with header, gate section, and metric section (D-06).
  - Graceful fallback: if report file missing, warns and falls back to report_metrics embedded in benchmark pack (no crash).
  - `cli.py`: added `@lake_app.command("compare")` with explicit pack_a/pack_b positional args (D-08), optional `--output-dir` and `--json-only` flags.
  - `tests/test_lake_compare.py` (new): 10 tests covering all 7 planned behaviors plus CLI integration. 197 total tests passing.
  - Addresses: PIPE-04, D-06, D-07, D-08, review concern #2 (data depth), review concern #6 (lane-centric model).

### 2026-04-03 (Phase 5 Complete)

- **Phase 5 execution complete — platform is analytically useful.**
  - All 3 plans executed across 3 waves: catalog/index layer (Wave 1), comparison engine (Wave 2), notebooks + RUNBOOK (Wave 3).
  - Verification passed: 15/15 must-haves verified, 200 tests passing, 0 regressions.
  - All 6 cross-AI review concerns addressed: hash-based staleness (HIGH), comparison data depth via benchmark-pack dereferencing (HIGH), 17-directory artifact inventory (HIGH), notebook smoke tests (MEDIUM), workspace-relative lineage (MEDIUM), lane-centric comparison model (MEDIUM).
  - Requirements satisfied: PIPE-04 (source-aware reference-phase enrichment analytics), PIPE-05 (unified operator runbook).
  - New CLI commands: `mdisc lake index`, `mdisc lake stats`, `mdisc lake compare`.
  - New artifacts: 3 analytics notebooks, RUNBOOK.md, `lake/` package (catalog.py, index.py, staleness.py, compare.py).
  - Next phase: Phase 6 (Zomic Training Corpus Pipeline).

- Phase 6 Plan 01 Task 1 — Added the foundation corpus contracts and committed starter config:
  - New package: `src/materials_discovery/llm/` with `schema.py` and `__init__.py`.
  - `schema.py` defines `CorpusBuildConfig`, `CorpusInventoryRow`, `CorpusProvenance`, `CorpusValidationState`, `CorpusConversionTrace`, `CorpusExample`, `CorpusQaSummary`, `CorpusManifest`, and `CorpusBuildSummary`.
  - Locked the review-driven contract updates up front: typed validation state, record-addressable inventory rows, and neutral `release_tier="pending"` before QA promotion.
  - Added `configs/llm/corpus_v1.yaml` covering Phase 6 source-family toggles, systems, thresholds, source keys, and reference-pack IDs.
  - Added `tests/test_llm_corpus_schema.py`; focused verification passed with `6 passed`.

- Phase 6 Plan 01 Task 2 — Added deterministic corpus storage and manifest helpers:
  - New modules: `llm/storage.py` and `llm/manifests.py`.
  - Locked the on-disk artifact family under `data/llm_corpus/{build_id}/` with helpers for syntax/materials/rejects/inventory/qa/manifest paths.
  - Added deterministic `corpus_build_fingerprint()`, `build_corpus_manifest()`, and `write_corpus_manifest()` using workspace-relative paths and output hashes.
  - Extended `llm/__init__.py` to export the new helper surface.
  - Added `tests/test_llm_corpus_storage.py` and `tests/test_llm_corpus_manifest.py`; combined `06-01` validation passed with `11 passed`.

- Phase 6 Plan 02 Task 1 — Added the deterministic LLM corpus inventory layer:
  - New module: `llm/inventory.py` with dedicated collectors for repo regression scripts, part scripts, materials-design `.zomic` files, candidate JSONL rows, generated raw exports, canonical source records, reference-pack records, and the committed PyQCstrc projection payload.
  - Added `tests/fixtures/pyqcstrc_projection_sample.json` as the offline fixture backing the required `pyqcstrc_projection` source family.
  - Extended `llm/__init__.py` to export the public inventory helpers so later builder code can reuse them directly.
  - Added `tests/test_llm_corpus_inventory.py`; focused verification passed with `7 passed`.

- Phase 6 Plan 02 Task 2 — Added the QA grading and dedupe layer:
  - New module: `llm/qa.py` with `grade_corpus_example()`, `dedupe_corpus_examples()`, and `summarize_corpus_quality()`.
  - Locked the release policy around pending -> gold/silver/reject promotion, label/orbit validation via `_infer_orbit_name`, and deterministic duplicate precedence on release tier, fidelity tier, source family, and example id.
  - Extended `llm/__init__.py` to export the QA helpers for the later builder flow.
  - Added `tests/test_llm_corpus_qa.py`; focused verification passed with `5 passed`.

- Phase 6 Plan 03 Task 1 — Added deterministic record2zomic conversion:
  - New modules: `llm/converters/axis_walk.py` and `llm/converters/record2zomic.py`, plus the new `llm/converters/` package surface.
  - Added a bounded, auditable qphi axis-walk decomposition strategy with explicit `direct_basis`, `bounded_search`, `anchored_fallback`, and `heuristic_fallback` trace labels.
  - Added deterministic `CandidateRecord -> CorpusExample` serialization with orbit-grouped branch blocks, comment preambles, preserved `source_label_map`, and anchored/approximate/heuristic fidelity visibility through `CorpusConversionTrace`.
  - Added `tests/test_llm_record2zomic.py`; focused verification passed with `12 passed` alongside the companion projection/compiler slice.

- Phase 6 Plan 03 Task 2 — Added the compile helper and PyQCstrc projection path:
  - New module: `llm/compiler.py` for temporary `.zomic` + design-YAML generation and bridge-backed compile validation with deterministic cell scaling from qphi bounds.
  - New module: `llm/converters/projection2zomic.py` for committed PyQCstrc-style projection payload conversion into `CorpusExample` records without a live PyQCstrc dependency.
  - Restored `projection_payload_to_zomic` to the public `llm/converters/__init__.py` exports for later builder dispatch.
  - Added `tests/test_llm_projection2zomic.py`; focused verification passed with `12 passed` alongside the companion record2zomic slice.

- Phase 6 Plan 04 Task 1 — Added CIF/open approximant conversion:
  - New module: `llm/converters/cif2zomic.py` reusing `expand_cif_orbits()` when symmetry metadata is present and falling back to `parse_cif()` on thin offline fixtures without a symmetry loop.
  - Added `tests/fixtures/hypodx_approximant_sample.cif` as the committed HYPOD-X-style approximant sample for offline coverage.
  - Added `canonical_record_to_zomic()` support for CIF-backed canonical source records plus a deterministic composition-only fallback for staged records that do not carry a structure representation.
  - Added `tests/test_llm_cif2zomic.py`; focused verification passed with `9 passed` together with `test_prototype_import.py` and `test_data_source_cod.py`.

- Phase 6 Plan 04 Task 2 — Added native-Zomic and generated-export source loaders:
  - New module: `llm/converters/native_zomic.py` with direct label extraction and exact-fidelity corpus examples for repo-native `.zomic` scripts.
  - New module: `llm/converters/generated_export.py` for raw export artifacts, preserving direct source metadata and choosing `exact` only when a source `.zomic` file is available.
  - Added loader-hint metadata (`native_zomic`, `generated_export`) so the final builder can dispatch from inventory rows without re-inferring source type.
  - Added `tests/test_llm_native_sources.py`; focused verification passed with `5 passed`.

- Phase 6 Plan 04 Task 3 — Added the end-to-end corpus builder:
  - New module: `llm/corpus_builder.py` that starts from `build_inventory()`, dispatches by `loader_hint`, compiles/validates generated examples, grades them, dedupes them, and writes `syntax_corpus.jsonl`, `materials_corpus.jsonl`, `rejects.jsonl`, `inventory.json`, `qa.json`, and `manifest.json`.
  - Tightened the CIF conversion seam so CIF-derived orbit names line up with label-derived orbit validation inside the shared QA rules, preventing valid canonical-source examples from being rejected downstream.
  - Added `tests/test_llm_corpus_builder.py`; focused verification passed with `17 passed` together with the inventory and QA slices.

- Phase 6 Plan 04 Task 4 — Added the operator-facing corpus CLI:
  - `cli.py` now mounts `llm_corpus_app` under `mdisc llm-corpus` and exposes `mdisc llm-corpus build --config ...`.
  - The new command validates the YAML as `CorpusBuildConfig`, calls `build_llm_corpus()`, prints `CorpusBuildSummary` as JSON, and follows the existing CLI error path with exit code 2 on invalid configs.
  - Added `tests/test_llm_corpus_cli.py`; focused verification passed with `11 passed` together with the existing `test_cli.py` contract suite.

### 2026-04-03 (Phase 7 Plan 01)

- Added the Phase 7 llm-generate contract layer:
  - `common/schema.py` now includes additive `BackendConfig.llm_*` fields, optional `LlmGenerateConfig`, and `LlmGenerateSummary` without requiring existing system configs to change.
  - `llm/schema.py` now defines `LlmGenerationRequest`, `LlmGenerationAttempt`, `LlmGenerationResult`, and `LlmRunManifest`, reusing `CompositionBound` and `ValidationStatus` instead of creating a parallel taxonomy.
- 20:01 EDT — Started Phase 8 Plan 01 by adding the first `llm-evaluate` contract and runtime slice.
- Added additive `LlmEvaluateConfig` and `LlmEvaluateSummary` models to `common/schema.py`, keeping the new evaluation path optional in `SystemConfig`.
- Added typed Phase 8 models in `llm/schema.py` for `LlmEvaluationRequest`, `LlmAssessment`, and `LlmEvaluationRunManifest`, plus new schema-version constants.
- Added `llm/evaluate.py` with ranked-candidate loading, structured prompt assembly, mock/real provider reuse, typed request/assessment JSONL artifacts, additive `CandidateRecord.provenance["llm_assessment"]`, and run-manifest persistence under `data/llm_evaluations/`.
- Added `mdisc llm-evaluate` to `cli.py`, including default output under `data/llm_evaluated/` and CLI-written calibration/manifest artifacts.
- Added focused Phase 8 tests in `tests/test_llm_evaluate_schema.py` and `tests/test_llm_evaluate_cli.py` covering schema validation, end-to-end mock evaluation artifacts, CLI success, and the missing-config error path.
- 20:20 EDT — Landed Phase 8 Plan 02 to thread LLM assessment through downstream artifacts without changing ranking weights.
- `cli.py` now prefers `data/llm_evaluated/{system}_all_llm_evaluated.jsonl` during `mdisc report` when that additive artifact exists, while keeping the ranked JSONL fallback unchanged.
- `diffraction/compare_patterns.py` now surfaces `llm_assessment` in report entries/evidence and adds summary-level LLM counts and synthesizability aggregates.
- `common/stage_metrics.py` now records additive LLM-assessment calibration metrics so report calibration captures assessed/failed counts, anomaly flags, and mean synthesizability.
- `hifi_digital/rank_candidates.py` now documents the Phase 8 rule explicitly: existing `llm_assessment` provenance is preserved but never used to reweight scores in this phase.
- Added Plan 02 regressions in `tests/test_report.py` and `tests/test_hifi_rank.py` covering report enrichment, `llm_evaluated` preference, calibration visibility, and score/order invariance when LLM assessment context is present.
- 20:43 EDT — Closed Phase 8 Plan 03 with the downstream deterministic-vs-LLM benchmark lane.
- Added `llm/pipeline_benchmark.py` with a dedicated comparison artifact over `screen`, `hifi-validate`, `hifi-rank`, and `report`, including downstream validity, novelty, top-rank quality, and report acceptance deltas.
- Added `scripts/run_llm_pipeline_benchmarks.sh`, which injects temporary offline `llm_evaluate` configs, runs both deterministic and LLM lanes, snapshots calibration JSON per stage, and writes `data/benchmarks/llm_pipeline/{system}_comparison.json`.
- Added `tests/test_llm_pipeline_benchmarks.py` with helper-level coverage plus offline two-system end-to-end benchmark proofs for `Al-Cu-Fe` and `Sc-Zn`.
- Refreshed `README.md`, `developers-docs/index.md`, `developers-docs/llm-integration.md`, and `developers-docs/pipeline-stages.md` so Phase 8 is documented as implemented and the new pipeline benchmark workflow is discoverable.
- 21:08 EDT — Started Phase 9 by adding the formal eval-set and acceptance-pack artifact layer.
- Added `llm/eval_set.py` and `llm/acceptance.py` so Phase 6 corpus artifacts can be exported into deterministic eval sets and Phase 7/8 benchmark outputs can be summarized into a typed acceptance pack.
- Extended `llm/schema.py`, `llm/storage.py`, and `llm/__init__.py` with Phase 9 eval-set, acceptance-threshold, and suggestion-facing models and artifact paths.
- Added `tests/test_llm_acceptance_schema.py`; focused verification passed with `2 passed`.
- 21:24 EDT — Landed Phase 9 Plan 02 to make `llm-generate` example-conditioned without changing its default path.
- `common/schema.py` now lets `llm_generate` point at an eval-set file plus a deterministic maximum number of conditioning examples.
- `llm/prompting.py` now selects same-system examples by composition distance and injects them into the prompt in a reproducible block.
- `llm/generate.py` now records `example_pack_path` and `conditioning_example_ids` in both `prompt.json` and the run manifest.
- Added Plan 02 regressions in `tests/test_llm_generate_core.py` and `tests/test_llm_generate_cli.py`; focused verification passed with `12 passed`.
- 21:46 EDT — Closed Phase 9 with the operator acceptance benchmark and dry-run suggestion workflow.
- Added `llm/suggest.py` plus the `mdisc llm-suggest --acceptance-pack ...` CLI command so typed acceptance packs now produce structured next-step recommendations without launching an autonomous loop.
- Added `scripts/run_llm_acceptance_benchmarks.sh`, which composes the Phase 7 and Phase 8 benchmark lanes into a typed acceptance pack under `data/benchmarks/llm_acceptance/{pack_id}/acceptance_pack.json`.
- Added `tests/test_llm_acceptance_benchmarks.py` and extended `tests/test_cli.py`; focused verification passed with `11 passed`, and the full `materials-discovery` suite closed at `297 passed, 3 skipped, 1 warning`.
- Refreshed `README.md`, `developers-docs/index.md`, `developers-docs/llm-integration.md`, and `developers-docs/pipeline-stages.md` so the Phase 9 acceptance-pack and dry-run suggestion workflow is documented as implemented.
- `llm/runtime.py` adds the provider-neutral adapter seam with deterministic `llm_fixture_v1` behavior and the first hosted adapter path, `anthropic_api_v1`, via lazy `httpx`.
- `llm/__init__.py` now exports the new Phase 7 runtime/schemas alongside the existing Phase 6 corpus surface.
- `developers-docs/configuration-reference.md` now documents the `llm_generate:` block, mock-only defaulting, and the requirement that real hosted configs set `llm_provider` and `llm_model`.
  - Added focused coverage in `tests/test_llm_generate_schema.py` and `tests/test_llm_runtime.py` for config validation, schema typing, adapter resolution, missing secret handling, lazy imports, and API-base override behavior.

### 2026-04-03 (Phase 7 Plan 02)

- Implemented the first full `mdisc llm-generate` path:
  - Added `llm/prompting.py` for config-driven prompt construction and optional seed-script loading.
  - Added `llm/generate.py` for bounded retries, per-attempt raw completion persistence, compile-result tracking, run-manifest emission, and conversion of valid compiled orbit libraries into standard `CandidateRecord` JSONL.
  - Extended `llm/compiler.py` so compile attempts now return explicit parse/compile status, stable error kinds, and persisted raw-export/orbit-library paths when the caller supplies an artifact root.
  - Extended `generator/candidate_factory.py` with `build_candidate_from_prototype_library(...)` so compiled template geometry can become normal candidates without reusing the Z[phi] perturbation branch.
  - Added `llm_generation_metrics(...)` and wired the new `llm-generate` Typer command into `cli.py`, including calibration JSON and stage-manifest output.
  - Added committed mock configs for `Al-Cu-Fe` and `Sc-Zn`, plus focused tests in `tests/test_llm_generate_core.py`, `tests/test_llm_generate_cli.py`, and `tests/test_cli.py`.

### 2026-04-03 (Phase 7 Plan 03)

- Added the Phase 7 benchmark comparison layer:
  - New `llm/benchmark.py` builds deterministic-vs-LLM comparison payloads and writes comparison JSON under `data/benchmarks/llm_generate/`.
  - Added `scripts/run_llm_generate_benchmarks.sh` as the thin operator wrapper around `mdisc generate`, `mdisc llm-generate`, and `mdisc screen`.
  - Added the `llm_lane` pytest marker plus `tests/test_llm_generate_benchmarks.py` for offline two-system benchmark coverage across `Al-Cu-Fe` and `Sc-Zn`.
- Refreshed docs so the first LLM inference path is described as implemented rather than planned:
  - `README.md`
  - `developers-docs/index.md`
  - `developers-docs/pipeline-stages.md`
  - `developers-docs/llm-integration.md`
- Re-verified the whole `materials-discovery` suite after landing the benchmark layer to keep Phase 7 closed with a project-wide green state.

### 2026-04-04

- 12:47 EDT — Completed the Phase 11 Plan 03 lineage propagation and launch-continuation docs pass.
- Normalized additive `llm_campaign` lineage once, wrote it into launched `llm_generate` manifests, reused it across `screen`, `hifi-validate`, `hifi-rank`, `active-learn`, `report`, and the pipeline manifest, and documented the `llm-launch` wrapper plus manual continuation flow in the developer docs.
- Focused verification passed with `16 passed` across `tests/test_llm_campaign_lineage.py` and `tests/test_report.py`, plus `1 passed` for the offline `tests/test_real_mode_pipeline.py -k "campaign or llm_launch"` slice.
- 12:47 EDT — Started Phase 11 Plan 03 in TDD RED mode by adding downstream lineage and mock launch continuation regressions.
- Added `tests/test_llm_campaign_lineage.py`, extended `tests/test_report.py`, and extended `tests/test_real_mode_pipeline.py` to lock campaign-lineage propagation into downstream manifests plus the offline `llm-launch -> screen` continuation lane.
- Open item: normalize campaign lineage once, thread it into downstream manifests and the pipeline manifest, then update docs for the Phase 11 manual continuation flow.
- 12:47 EDT — Implemented the Phase 11 Plan 02 Task 2 `llm-launch` CLI bridge.
- Added `mdisc llm-launch --campaign-spec ...`, config-hash drift validation with pinned/current hash detail, early `launch_id` visibility, `resolved_launch.json` / `launch_summary.json` writing, and additive execution through the existing `generate_llm_candidates()` path.
- Focused verification passed with `13 passed` across `tests/test_llm_launch_cli.py` and `tests/test_cli.py`.
- 12:52 EDT — Started Phase 11 Plan 02 Task 2 in TDD RED mode by adding `tests/test_llm_launch_cli.py` and a shared `tests/test_cli.py` smoke case.
- The new failing coverage locks successful `llm-launch` artifact writing, config-drift failure messaging, and the requirement that generation must not start when the pinned config hash no longer matches.
- Open item: add the `llm-launch` command, write resolved/summary artifacts, and preserve partial-failure auditability without reusing `llm-approve`.
- 12:47 EDT — Implemented the Phase 11 Plan 02 Task 1 additive `llm-generate` bridge.
- Threaded prompt instruction deltas through `build_generation_prompt()` and `LlmGenerationRequest`, added campaign-aware fields to `LlmRunManifest`, and recorded additive `llm_campaign` provenance on launched candidates.
- Also widened the run hash so campaign launches with different overlays do not silently collide with otherwise identical manual generation runs.
- 12:42 EDT — Started Phase 11 Plan 02 Task 1 in TDD RED mode by extending `tests/test_llm_generate_core.py`.
- The new failing coverage locks prompt instruction-delta placement plus campaign-aware run-manifest and candidate-provenance fields before changing the existing `llm-generate` runtime.
- Open item: thread additive prompt/campaign launch metadata through `llm_generate` without disturbing the manual path.
- 13:12 EDT — Implemented the Phase 11 Plan 01 Task 2 launch resolution layer.
- Added `materials_discovery.llm.launch` with deterministic action ordering, configured-lane vs baseline-fallback resolution, heuristic composition-window shrinking, and eval-set-backed seed materialization into the campaign launch directory.
- Exported `resolve_campaign_launch()`, `resolve_campaign_model_lane()`, and `materialize_campaign_seed()` from `materials_discovery.llm` so later CLI and runtime work can use a single additive launch overlay surface.
- 12:30 EDT — Started Phase 11 Plan 01 Task 2 in TDD RED mode by adding `tests/test_llm_launch_core.py`.
- The new failing coverage locks deterministic lane selection and fallback, ordered prompt deltas, exact vs heuristic composition overlays, seed reuse/materialization, and the requirement that source `SystemConfig` objects stay unmodified.
- Open item: implement `materials_discovery.llm.launch`, export its helpers, and keep all resolution logic file-backed and additive over the existing `llm-generate` path.
- 12:27 EDT — Started Phase 11 Plan 01 Task 1 in TDD RED mode by adding `tests/test_llm_launch_schema.py`.
- The new failing coverage locks the additive `model_lanes` config seam, typed launch-summary/resolved-launch artifacts, and deterministic `data/llm_campaigns/{campaign_id}/launches/{launch_id}/` path helpers before touching the implementation.
- Open item: add the lane-aware schema fields, launch artifact models, storage helpers, and exports without breaking legacy `llm-generate` configs.
- 12:30 EDT — Implemented the Phase 11 Plan 01 Task 1 launch contracts and storage helpers.
- Added `LlmModelLaneConfig` plus `llm_generate.model_lanes`, introduced `CampaignLaunchStatus`, `LlmCampaignResolvedLaunch`, and `LlmCampaignLaunchSummary`, and wired deterministic launch helper paths under `data/llm_campaigns/{campaign_id}/launches/{launch_id}/`.
- Exported the new launch models and storage helpers from `materials_discovery.llm` while keeping legacy manual `llm-generate` configs valid when `model_lanes` is absent.
- 01:28 EDT — Started Phase 10 Plan 01 Task 1 in TDD RED mode by adding `tests/test_llm_campaign_schema.py`.
- The new failing coverage locks the intended governance contract for typed campaign actions, system-scoped proposals, separate approval artifacts, and self-contained campaign specs before touching `llm/schema.py`.
- Open item: implement the additive Phase 10 schema models in `materials_discovery.llm.schema` and export them without disturbing the existing Phase 6-9 contracts.
- 01:29 EDT — Implemented the Phase 10 campaign governance schema in `materials_discovery.llm.schema` and exported the new models and constants from `materials_discovery.llm`.
- Added typed payloads for the three action families, proposal and suggestion contracts, separate approval artifacts, and self-contained campaign specs with pinned launch baselines and lineage.
- Validators now reject blank IDs and paths, require the payload that matches each action family, reject non-matching payloads, normalize evidence/failing-metric lists, and enforce `default_count >= 1` for launch baselines.
- 01:30 EDT — Started Phase 10 Plan 01 Task 2 in TDD RED mode by adding `tests/test_llm_campaign_storage.py`.
- The new failing storage tests lock the deterministic artifact layout for acceptance-pack-rooted suggestions, proposals, approvals, and dedicated `data/llm_campaigns/{campaign_id}/campaign_spec.json` outputs.
- Open item: add the new storage helpers to `materials_discovery.llm.storage`, reject blank artifact IDs, and export the helper surface from `materials_discovery.llm`.
- 01:31 EDT — Implemented the Phase 10 storage helpers in `materials_discovery.llm.storage` and exported them from `materials_discovery.llm`.
- Added deterministic helpers for `suggestions.json`, `proposals/{proposal_id}.json`, `approvals/{approval_id}.json`, and `data/llm_campaigns/{campaign_id}/campaign_spec.json`.
- Blank `pack_id`, `proposal_id`, `approval_id`, and `campaign_id` inputs now raise immediately so the storage layer cannot quietly point at malformed artifact roots.
- 01:42 EDT — Started Phase 10 Plan 02 Task 1 in TDD RED mode by adding `tests/test_llm_suggest_core.py`.
- The new failing coverage locks the acceptance-pack to typed-campaign-proposal mapping rules, deterministic action IDs, release-gate posture, specialized-materials routing, and summary path emission before touching the implementation.
- Open item: add `llm/campaigns.py`, migrate `llm/suggest.py` to the typed campaign bundle, and update in-repo callers away from the legacy `LlmSuggestion` contract.
- 01:47 EDT — Implemented the Phase 10 Plan 02 Task 1 typed suggestion mapping layer.
- Added `llm/campaigns.py` with deterministic system-scoped proposal IDs, stable per-proposal action IDs, heuristic-to-action-family mapping, and acceptance-pack to proposal-summary helpers.
- Migrated `llm/suggest.py` so it now builds `LlmCampaignSuggestion`, writes sibling `proposals/{proposal_id}.json` artifacts under the acceptance-pack root, and keeps directory creation/writing out of the CLI.
- Updated `llm/__init__.py` exports and `tests/test_llm_acceptance_benchmarks.py` so in-repo callers move with the contract instead of silently expecting the legacy `LlmSuggestion` surface.
- 01:48 EDT — Started Phase 10 Plan 02 Task 2 in TDD RED mode by adding `tests/test_llm_suggest_cli.py` and updating the shared `tests/test_cli.py` llm-suggest coverage.
- The new failing CLI tests lock the typed stdout contract, default `suggestions.json` writing, sibling `proposals/{proposal_id}.json` artifact creation, and the requirement that shared CLI callers move with the Wave 2 migration instead of expecting legacy plain-language items.
- Open item: update `cli.py` to call the new typed suggestion writer and keep `mdisc llm-suggest` dry-run with clear exit-2 handling on invalid input.
- 01:50 EDT — Implemented the Phase 10 Plan 02 Task 2 CLI migration.
- `cli.py` now sends `mdisc llm-suggest` through the typed suggestion writer, preserves dry-run behavior, and prints the persisted campaign-bundle JSON instead of the legacy plain-language suggestion surface.
- Added `tests/test_llm_suggest_cli.py`, updated the shared `tests/test_cli.py` contract, and confirmed the focused CLI slice passes with proposal artifacts written under the acceptance-pack root.
- 10:56 EDT — Started Phase 10 Plan 03 in TDD RED mode by adding `tests/test_llm_campaign_spec.py`, `tests/test_llm_approve_cli.py`, and a new shared `test_cli.py` smoke case for `llm-approve`.
- The new failing coverage locked deterministic approval IDs, campaign-spec lineage, approved-vs-rejected behavior, and the requirement that Phase 10 approval must not call `llm-generate` or `llm-evaluate`.
- 10:56 EDT — Implemented the Phase 10 Plan 03 governance boundary.
- Added `create_campaign_approval()` and `materialize_campaign_spec()` to `llm/campaigns.py`, plus artifact-root derivation in `llm/storage.py` so approvals stay under the acceptance-pack root and campaign specs land under `data/llm_campaigns/{campaign_id}/`.
- Added `mdisc llm-approve` to `cli.py`; approved decisions now require `--config`, rejected decisions stop at the approval artifact, and the command emits a JSON summary without launching any downstream run.
- Refreshed `developers-docs/llm-integration.md` and `developers-docs/pipeline-stages.md` to document the new dry-run vs approval/spec boundary.
- Re-verified Phase 10 locally with focused tests plus the full suite: `332 passed, 3 skipped, 1 warning`.
