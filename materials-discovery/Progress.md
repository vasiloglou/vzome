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
- Phase 4 Plan 01 Task 2 — Added benchmark-ready reference-aware configs and second-source fixtures:
  - `configs/systems/al_cu_fe_reference_aware.yaml` (new): source_registry_v1, real mode, HYPOD-X + Materials Project reference pack (priority order: hypodx > materials_project), benchmark corpus and validation snapshot wired.
  - `configs/systems/sc_zn_reference_aware.yaml` (new): source_registry_v1, real mode, Zomic design path preserved, HYPOD-X + COD reference pack (priority order: hypodx > cod), benchmark corpus and validation snapshot wired.
  - `data/external/sources/materials_project/mp_fixture_v1/canonical_records.jsonl` (new): thin 2-record MP fixture for Al-Cu-Fe multi-source proof.
  - `data/external/sources/cod/cod_fixture_v1/canonical_records.jsonl` (new): thin 1-record COD fixture for Sc-Zn multi-source proof.
  - `data/external/sources/hypodx/hypodx_pinned_2026_03_09/canonical_records.jsonl` (new): staged canonical records from the pinned HYPOD-X snapshot.
  - `data/external/sources/hypodx/hypodx_fixture_local/canonical_records.jsonl` (new): staged canonical records from the local HYPOD-X fixture for Sc-Zn.
  - `cli.py`: added `_ingest_via_reference_pack` function; updated ingest command to detect `ingestion.reference_pack` and route through the reference-pack assembly path.
  - `tests/test_benchmarking.py`: extended with 31 new deterministic tests asserting config validity, pack IDs, member source keys, snapshot IDs, priority ordering, benchmark corpus/validation-snapshot hooks, zomic-design preservation (Sc-Zn), and second-source fixture existence.
