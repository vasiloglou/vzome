# Materials Discovery Software Scaffold

Companion to Chapter 10.8 in [vZome Geometry Tutorial](vzome-geometry-tutorial.md).

This document turns the chapter into an executable software blueprint for quasicrystal/approximant discovery using Z[phi]-aware geometry plus modern materials workflows.

---

## 0. Implementation Status (Current)

- `M1 ingest`: implemented in `materials-discovery/src/materials_discovery/data/ingest_hypodx.py`.
- `M2 generate`: implemented in `materials-discovery/src/materials_discovery/generator/candidate_factory.py`.
- `M3 screen`: implemented in `materials-discovery/src/materials_discovery/screen/`.
- `M4 hifi-validate`: implemented in `materials-discovery/src/materials_discovery/hifi_digital/` and wired through `materials_discovery.cli`.
- `M5 active-learn`: implemented in `materials-discovery/src/materials_discovery/active_learning/` and wired through `materials_discovery.cli`.
- Remaining commands (`hifi-rank`, `report`): interface-complete stubs with explicit exit code `3`.

### Local Quickstart

```bash
cd materials-discovery
uv sync --extra dev
uv run mdisc ingest --config configs/systems/al_cu_fe.yaml
uv run mdisc generate --config configs/systems/al_cu_fe.yaml --count 50
uv run mdisc screen --config configs/systems/al_cu_fe.yaml
uv run mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch all
uv run mdisc active-learn --config configs/systems/al_cu_fe.yaml
uv run pytest
uv run ruff check .
uv run mypy src
```

---

## 1. Scope

### Primary Goal

Build a reproducible pipeline that can:

1. generate candidate quasicrystal-compatible structures,
2. screen them with fast surrogate models,
3. refine top candidates with high-fidelity digital validation (no DFT required),
4. rank candidates for experimental follow-up.

### Non-Goals (v0.1)

- Full autonomous lab integration.
- Guaranteed true aperiodic bulk proof in first release.
- Universal potential quality across all chemistries on day one.

---

## 2. Suggested Repo Layout

Create a new top-level workspace in the repo:

```text
materials-discovery/
  README.md
  pyproject.toml
  configs/
    systems/
      al_cu_fe.yaml
      al_pd_mn.yaml
      sc_zn.yaml
  data/
    raw/
    external/
    processed/
    candidates/
    reports/
  src/
    materials_discovery/
      __init__.py
      common/
        io.py
        schema.py
        logging.py
      data/
        ingest_hypodx.py
        ingest_reference_phases.py
        normalize.py
      generator/
        approximant_templates.py
        decorate_sites.py
        candidate_factory.py
      screen/
        relax_fast.py
        filter_thresholds.py
        rank_shortlist.py
      hifi_digital/
        committee_relax.py
        uncertainty.py
        hull_proxy.py
        phonon_mlip.py
        md_stability.py
        xrd_validate.py
        rank_candidates.py
      active_learning/
        train_surrogate.py
        select_next_batch.py
      diffraction/
        simulate_powder_xrd.py
        compare_patterns.py
      cli.py
  orchestration/
    prefect/
    snakemake/
  notebooks/
  tests/
    test_schema.py
    test_generator.py
    test_screen_filters.py
```

If you do not want a new top-level directory, mirror this structure under `developer-docs/examples/materials-discovery/` first, then promote to production paths later.

---

## 3. Data Contract (Candidate Record)

Use one canonical candidate schema from day one:

```json
{
  "candidate_id": "md_000001",
  "system": "Al-Cu-Fe",
  "template_family": "icosahedral_approximant_1_1",
  "cell": {"a": 14.2, "b": 14.2, "c": 14.2, "alpha": 90, "beta": 90, "gamma": 90},
  "sites": [
    {"label": "S1", "qphi": [[1,0],[0,1],[-1,1]], "species": "Al", "occ": 1.0}
  ],
  "composition": {"Al": 0.7, "Cu": 0.2, "Fe": 0.1},
  "screen": {"model": "MACE", "energy_per_atom_ev": -3.12},
  "digital_validation": {
    "status": "pending",
    "committee": ["MACE", "CHGNet", "MatterSim"],
    "uncertainty_ev_per_atom": null
  },
  "provenance": {"generator_version": "0.1.0", "config_hash": "sha256:..."}
}
```

Notes:

- `qphi` stores `(a,b)` integer pairs for each Cartesian component `a + b*phi`.
- store both generated and relaxed Cartesian coordinates when available.
- never drop provenance fields; they are required for reproducibility.

---

## 4. Module Responsibilities

### `data/`

- Ingest HYPOD-X and reference phase data.
- Normalize composition labels, phase names, and units.
- Produce one deduplicated table for training/screening.

### `generator/`

- Generate periodic approximants or bounded templates.
- Apply decoration rules (species assignments and occupancy constraints).
- Emit validated structure objects plus metadata.

### `screen/`

- Run fast relaxations (MACE/CHGNet/NequIP-based).
- Apply hard filters: minimum distance, charge sanity, composition bounds.
- Rank shortlist for high-fidelity digital validation.

### `hifi_digital/`

- Run committee relaxations across multiple MLIPs.
- Quantify uncertainty via disagreement in energies/forces/stresses.
- Compute proxy hull metrics against known competing phases.
- Run selected MLIP phonon and short MD stability checks.
- Produce uncertainty-aware candidate rankings.

### `active_learning/`

- Train/update surrogate from accumulated digital validation labels.
- Select next candidate batch using uncertainty-aware criteria.

### `diffraction/`

- Simulate powder XRD for top candidates.
- Compare to known signatures; flag experimental distinctness.

---

## 5. Milestones and Definition of Done

| Milestone | Duration | Definition of Done |
|----------|----------|--------------------|
| M1 Data foundation | 2 weeks | HYPOD-X + reference phases ingested; schema validated |
| M2 Candidate generation | 3 weeks | >=10k unique candidates generated for one ternary system |
| M3 Fast screening | 3 weeks | Top 1-5% shortlisted with reproducible ranking reports |
| M4 High-fidelity digital validation | 5 weeks | >=200 candidates validated with committee uncertainty and proxy hull values |
| M5 Active learning loop | 3 weeks | Surrogate retrained and improves top-k hit rate |
| M6 Experiment report | 2 weeks | Ranked list with XRD signatures and provenance bundles |

---

## 6. Metrics to Track

- `screen_to_hifi_yield`: fraction of screened structures that remain competitive after digital validation.
- `top_k_precision`: fraction of top-k surrogate predictions confirmed by committee ranking.
- `DeltaE_proxy_hull_distribution`: stability profile under proxy hull model.
- `committee_disagreement_mean`: average uncertainty for shortlisted candidates.
- `dedupe_rate`: duplicate generation rate (should decline over time).
- `reproducibility_rate`: jobs reproducing same result under rerun.

---

## 7. Initial Command Surface

Expose one CLI entry point:

```bash
mdisc ingest --config configs/systems/al_cu_fe.yaml
mdisc generate --config configs/systems/al_cu_fe.yaml --count 20000
mdisc screen --config configs/systems/al_cu_fe.yaml
mdisc hifi-validate --config configs/systems/al_cu_fe.yaml --batch top500
mdisc hifi-rank --config configs/systems/al_cu_fe.yaml
mdisc active-learn --config configs/systems/al_cu_fe.yaml
mdisc report --config configs/systems/al_cu_fe.yaml
```

---

## 8. Recommended External Resources

- HYPOD-X datasets and metadata: https://www.nature.com/articles/s41597-024-04043-z
- Matbench Discovery benchmark paper: https://www.nature.com/articles/s42256-025-01055-1
- Matbench Discovery project: https://github.com/janosh/matbench-discovery
- CHGNet repository: https://github.com/CederGroupHub/chgnet
- MACE repository: https://github.com/ACEsuit/mace
- MatterSim repository: https://github.com/microsoft/mattersim
- Quasicrystal ML discovery paper: https://doi.org/10.1103/PhysRevMaterials.7.093805
- Optional future first-principles verification reference: https://www.nature.com/articles/s41567-025-02925-6
- Quasicrystal structure prediction review: https://euler.phys.cmu.edu/widom/pubs/PDF/IJCR2023.pdf
- Deep-learning XRD for QC identification: https://pubmed.ncbi.nlm.nih.gov/37964402/

---

## 9. First Implementation Ticket List

1. Add `materials-discovery/` skeleton and package metadata.
2. Implement `schema.py` and round-trip JSON validation tests.
3. Implement HYPOD-X ingestion and normalization.
4. Implement one template generator for a single target system.
5. Implement one fast-screen backend and one ranking report.
6. Implement one `hifi_digital` committee workflow (relax + uncertainty + proxy hull).
7. Add CI test suite for schema, generator determinism, and ranking reproducibility.
8. Add an optional "future verification" interface to plug in first-principles checks later.

This list is intentionally narrow so the first push produces a runnable vertical slice instead of a large unfinished framework.
