# Phase 4 Research: Reference-Aware No-DFT Materials Discovery v1

**Phase:** 04  
**Date:** 2026-04-03  
**Goal:** Plan the first operationally credible, benchmarked version of the
reference-aware no-DFT discovery workflow.

## Research Question

What do we need to know to plan Phase 4 well so that the team can implement:

- two non-mock benchmark lanes
- explicit multi-source reference packs for richer reference-phase inputs
- comparable manifests, calibrations, and report outputs across source adapters
  and backend modes
- reproducible scripts and runbooks for source selection and backend selection

## Key Findings

### 1. Phase 4 already has a strong two-system base, but only for two systems

The repo currently ships the ingredients needed for a credible Phase 4 target
on exactly two systems:

- `Al-Cu-Fe`
  - `configs/systems/al_cu_fe_real.yaml`
  - `configs/systems/al_cu_fe_exec.yaml`
  - `data/external/pinned/al_cu_fe_validation_snapshot_2026_03_09.json`
  - `data/benchmarks/al_cu_fe_benchmark.json`
- `Sc-Zn`
  - `configs/systems/sc_zn_real.yaml`
  - `configs/systems/sc_zn_native.yaml`
  - `data/external/pinned/sc_zn_validation_snapshot_2026_03_07.json`
  - `data/benchmarks/sc_zn_benchmark.json`

`Al-Pd-Mn` and `Ti-Zr-Ni` do not yet have the same package of real configs,
benchmark corpora, and validation snapshots. That makes them poor v1 Phase 4
targets. The strongest plan is to lock Phase 4 to `Al-Cu-Fe` and `Sc-Zn`.

### 2. The source-backed ingest bridge exists, but the operator paths still mostly use legacy ingest

Phase 3 already proved that:

- `source_registry_v1` is a real `mdisc ingest` path
- staged canonical snapshots can be projected into processed reference phases
- source-backed real-mode tests stay green and offline

However, the currently shipped benchmark/operator surfaces are still centered
around legacy/pinned configs and single-system scripts:

- `scripts/run_real_pipeline.sh` hard-codes `al_cu_fe_real.yaml`
- `scripts/run_exec_pipeline.sh` hard-codes `al_cu_fe_exec.yaml`
- `scripts/run_native_pipeline.sh` hard-codes `al_cu_fe_native.yaml`

Phase 4 therefore needs to productize the source-backed path into committed
benchmark configs and runbooks rather than leaving it only in tests.

### 3. The current benchmarking layer calibrates one system at a time, but it does not yet support cross-lane comparison well

`common/benchmarking.py` currently does two things well:

- resolve one benchmark corpus for a system
- convert that corpus into a `CalibrationProfile`

That is enough for stage-local calibration, but it does not yet answer:

- which reference pack fed the run
- which source adapters contributed
- which backend mode or lane should be compared to which
- how to bundle stage manifests/calibrations into one operator-facing benchmark
  artifact

Phase 4 should not replace the current calibration logic. It should wrap it in
clearer context and comparison artifacts.

### 4. Rank and report outputs carry useful metrics, but not enough benchmark/reference provenance

The current rank/report stages already emit strong internal signals:

- `rank_candidates.py` computes stability probability, OOD, novelty, benchmark
  alignment, and penalties
- `compare_patterns.py` emits priority, recommendation, risk flags, evidence,
  and report release-gate decisions

But the outputs do not yet make the full run context explicit. In particular,
they do not surface enough about:

- benchmark corpus identity/version
- reference-pack identity/fingerprint
- contributing source keys
- backend-mode comparison lane

That limits operator trust and makes cross-lane comparison harder than it
should be.

### 5. Phase 4 needs two new artifact concepts, not just richer manifests

The roadmap language implicitly points to two different artifacts:

1. **Reference pack**
   - input-side artifact
   - curated from one or more staged source snapshots
   - used to feed `mdisc ingest`
2. **Benchmark pack**
   - output-side artifact
   - bundles comparable run context and the important downstream outputs

Keeping these separate matters:

- input curation and output comparison have different lifecycles
- later phases can reuse reference packs without rerunning every benchmark lane
- later analytics can reason about benchmark packs without re-deriving run
  context from many individual stage files

### 6. The best minimum comparison matrix is asymmetric by design

The repo does not currently support the same execution richness for both
benchmark systems, and Phase 4 should not pretend it does.

The strongest minimum matrix is:

| System | Required lanes | Why |
|--------|----------------|-----|
| `Al-Cu-Fe` | baseline real, richer source-pack real, exec comparison | best-provisioned system and existing operator scripts already target it |
| `Sc-Zn` | real calibrated, richer source-pack real | second benchmark system with Zomic bridge; good proof that Phase 4 is not single-system |

`native` is useful, but it is better treated as optional Phase 4 bonus coverage
than as part of the minimum acceptance matrix.

### 7. Offline reproducibility should stay the verification default

Phase 2/3 established a strong pattern:

- tests use local fixtures or pinned snapshots
- real-mode integration stays deterministic
- the no-DFT boundary is explicit during ingest

Phase 4 should keep that posture. Live providers may be used by humans during
manual experiments, but the committed configs, integration tests, and benchmark
packs should remain reproducible from local artifacts.

## Recommended Runtime Shape

### Input-side additions

Phase 4 should add a small, explicit reference-pack layer without replacing the
Phase 2 source runtime:

```text
materials_discovery/
  data_sources/
    runtime.py
    projection.py
    reference_packs.py      # new helper for pack assembly/reuse
    schema.py               # additive pack summary/manifest models
    storage.py              # additive reference-pack path helpers
```

Recommended artifact layout:

```text
data/
  external/
    sources/{source_key}/{snapshot_id}/...
    reference_packs/{system_slug}/{pack_id}/
      canonical_records.jsonl
      pack_manifest.json
      pack_qa.json
```

The reference-pack builder should:

- consume already staged canonical source snapshots
- merge and dedupe deterministically
- preserve lineage for every member snapshot
- stay upstream of the existing Phase 3 projection seam

### Output-side additions

Phase 4 should add a benchmark-pack summary artifact layered on top of the
existing manifests/calibrations:

```text
data/
  manifests/
    {system_slug}_pipeline_manifest.json
    {system_slug}_benchmark_pack.json   # new or exact equivalent
```

That artifact should answer, in one place:

- which config/lane ran
- which backend mode and adapters were active
- which reference pack fed ingest
- which benchmark corpus/calibration profile was loaded
- where the stage manifests/calibration JSONs live
- the key release-gate metrics and report fingerprint

## Recommended Phase 4 Scope

### Must-have implementation targets

1. **Two committed benchmark configs**
   - `Al-Cu-Fe` richer/reference-aware config
   - `Sc-Zn` richer/reference-aware config
2. **Reference-pack assembly**
   - additive config seam
   - deterministic pack manifests
   - no-DFT integration with the Phase 3 bridge
3. **Comparable run context**
   - manifests
   - calibration outputs
   - rank provenance
   - report outputs
4. **Operator runner + docs**
   - reusable benchmark script(s)
   - runbook documenting source-pack selection and backend selection
5. **Two-system verification**
   - end-to-end integration on `Al-Cu-Fe` and `Sc-Zn`
   - comparison assertions for at least one mode/source-lane contrast

### Should-not-expand targets

- Do not add a third required benchmark system in Phase 4
- Do not build a database or analytics service
- Do not make live network access a required integration path
- Do not collapse benchmark corpora, reference packs, and pipeline manifests
  into one overloaded file

## Risks And Mitigations

### Risk 1: Trying to benchmark too many systems

**Why it matters:** The repo only has credible real-mode assets for two systems.

**Mitigation:** Lock Phase 4 to `Al-Cu-Fe` and `Sc-Zn`.

### Risk 2: Overloading `benchmark_corpus` to also represent source-pack lineage

**Why it matters:** Input curation and calibration provenance are distinct.

**Mitigation:** Keep reference-pack identity separate from benchmark-corpus
identity and only connect them in a benchmark-pack summary artifact.

### Risk 3: Burying pack/source context only inside ingest manifests

**Why it matters:** Operators compare ranked/report outcomes, not only ingest
artifacts.

**Mitigation:** Propagate benchmark/reference context additively into rank,
report, and pipeline-summary outputs.

### Risk 4: Requiring live providers in tests

**Why it matters:** It would weaken reproducibility and slow down verification.

**Mitigation:** Use local staged snapshots or committed thin fixtures for
reference-pack tests and integration coverage.

### Risk 5: Replacing the current operator scripts instead of upgrading them

**Why it matters:** Existing scripts are already part of the operator workflow.

**Mitigation:** Treat the current scripts as a baseline and generalize them into
multi-system benchmark runners and runbooks.

## Recommended Plan Split

### Wave 1

Build explicit reference-pack inputs and benchmark configs for `Al-Cu-Fe` and
`Sc-Zn`.

### Wave 2

Thread benchmark/reference context through manifests, calibration outputs,
ranked candidate provenance, and report outputs; emit a comparable benchmark
pack summary.

### Wave 3

Add operator benchmark scripts and runbooks, then prove the two-system benchmark
matrix with deterministic end-to-end tests.

## Planning Recommendation

Phase 4 should be planned as **3 waves / 3 plans**:

1. reference-pack assembly + committed benchmark configs
2. comparable provenance + benchmark-pack output artifact
3. operator runbooks/scripts + two-system benchmark verification

That split keeps the critical path clear:

- first make richer inputs real
- then make outputs comparable and inspectable
- then make the full operator workflow reproducible

