# Materials Discovery Pipeline -- System Architecture

This document describes the architecture of the materials discovery pipeline
as implemented in `materials-discovery/src/materials_discovery/`.

---

## Package Structure

The codebase is organized into seven domain packages and one shared foundation
package. Every domain package depends on `common/`; only `hifi_digital/`
additionally depends on `backends/`. The generator package also has an explicit
bridge into `vZome core` for Zomic-authored designs.

```
materials_discovery/
  common/           Shared schemas, chemistry descriptors, coordinates, IO,
                    manifests, stage metrics, benchmarking
  data/             Ingest pipeline
  generator/        Candidate generation with Z[phi] geometry and Zomic bridge
  screen/           Fast screening: relax, filter, rank shortlist
  hifi_digital/     High-fidelity validation: committee relax, uncertainty,
                    hull proxy, phonon, MD, XRD, ranking
  active_learning/  Surrogate training and batch selection
  diffraction/      XRD simulation and experiment report compilation
  backends/         Adapter system for mock/real/exec/native execution modes
  llm/              [PLANNED] LLM-powered generation, evaluation, and suggestion
                    llm_generate.py     Zomic generation conditioned on composition
                    llm_evaluate.py     Synthesizability scoring and anomaly detection
                    llm_suggest.py      Composition/motif suggestions for active learning
                    converters/         record2zomic, cif2zomic, projection2zomic
  cli.py            Single orchestration layer (8+3 typer commands)
```

Dependency graph:

```
                         +----------+
                         |  common  |
                         +----+-----+
                              |
        +----------+----------+----------+-----------+----------+----------+
        |          |          |          |            |          |          |
   +----+---+ +---+----+ +--+---+ +----+------+ +---+-----+ +--+--------+ +-----+
   |  data  | |generator| |screen| |hifi_digital| |active   | |diffraction| | llm |
   +--------+ +---------+ +------+ +-----+------+ |learning | +-----------+ +--+--+
                                         |         +---------+                 |
                                    +----+----+                                |
                                    | backends | <-----------------------------+
                                    +---------+
```

The planned `llm/` package depends on `common/` (schemas, coordinates) and `backends/`
(LLM adapter selection). It also calls into `generator/zomic_bridge.py` to compile
LLM-generated Zomic scripts into orbit libraries.

---

## Orchestration

There is no separate orchestration framework. `cli.py` is the pipeline. It
defines eight typer commands that wire together the domain packages:

| Command          | Packages used                      | Status |
|------------------|------------------------------------| ------- |
| `ingest`         | `backends`, `data`                 | Implemented |
| `export-zomic`   | `generator`, `core`                | Implemented |
| `generate`       | `generator`                        | Implemented |
| `screen`         | `screen`                           | Implemented |
| `hifi-validate`  | `hifi_digital`, `backends`         | Implemented |
| `hifi-rank`      | `hifi_digital`                     | Implemented |
| `active-learn`   | `active_learning`                  | Implemented |
| `report`         | `diffraction`                      | Implemented |
| `llm-generate`   | `llm`, `generator`, `backends`     | Planned |
| `llm-evaluate`   | `llm`, `backends`                  | Planned |
| `llm-suggest`    | `llm`, `active_learning`, `backends` | Planned |

Each command reads a single YAML configuration file, loads it into a
`SystemConfig` object, invokes the relevant domain functions, and writes
artifacts to the filesystem.

---

## Data Flow

The main pipeline is linear. The optional Zomic-authoring bridge sits before
generation and produces an orbit-library prototype that `generate` can consume.

```
Config YAML
    |
    v
cli.py loads SystemConfig
    |
    v
OPTIONAL ZOMIC EXPORT
    export_zomic_design
    -> ./gradlew :core:zomicExport
    -> data/prototypes/generated/{prototype_key}.raw.json
    -> data/prototypes/generated/{prototype_key}.json
    |
    v
INGEST
    resolve_ingest_backend
    -> backend.load_rows
    -> ingest_rows
    -> data/processed/{slug}_reference_phases.jsonl
    |
    v
GENERATE
    generate_candidates
    -> data/candidates/{slug}_candidates.jsonl
    |
    v
SCREEN
    run_fast_relaxation
    -> apply_screen_thresholds
    -> rank_screen_shortlist
    -> data/screened/{slug}_screened.jsonl
    |
    v
HIFI-VALIDATE
    run_committee_relaxation
    -> compute_committee_uncertainty
    -> compute_proxy_hull
    -> run_mlip_phonon_checks
    -> run_short_md_stability
    -> validate_xrd_signatures
    -> _finalize_validation
    -> data/hifi_validated/{slug}_{batch}_validated.jsonl
    |
    v
HIFI-RANK
    rank_validated_candidates
    -> data/ranked/{slug}_ranked.jsonl
    |
    v
ACTIVE-LEARN
    train_surrogate_model
    + select_next_candidate_batch
    -> data/active_learning/{slug}_surrogate.json
    -> data/active_learning/{slug}_next_batch.jsonl
    |
    v
REPORT
    simulate_powder_xrd_patterns
    + compile_experiment_report
    -> data/reports/{slug}_report.json
    -> data/reports/{slug}_xrd_patterns.jsonl
```

Every stage also emits:

- A **manifest JSON** to `data/manifests/` containing `run_id`,
  `config_hash`, `backend_versions`, and `output_hashes`.
- A **calibration JSON** to `data/calibration/` containing stage-specific
  metrics.
- The **report** stage additionally emits a `pipeline_manifest` that
  aggregates all per-stage manifests.

---

## Artifact Directory Layout

All pipeline state lives on the filesystem. There is no database.

```
data/
  external/
    fixtures/              Mock-mode fixture data
    pinned/                Pinned snapshots for real mode
  prototypes/              System-anchored orbit library JSONs
    generated/             Zomic-exported orbit libraries and raw geometry
  benchmarks/              Pinned benchmark corpora
  processed/               Ingested reference phases         (JSONL)
  candidates/              Generated candidates               (JSONL)
  screened/                Screened shortlists                (JSONL)
  hifi_validated/          Validated candidates per batch     (JSONL)
  ranked/                  Final ranked candidates            (JSONL)
  active_learning/         Surrogate models and next-batch   (JSON + JSONL)
  reports/                 Experiment reports and XRD         (JSON + JSONL)
  calibration/             Per-stage calibration metrics      (JSON)
  manifests/               Stage and pipeline manifests       (JSON)
  registry/
    features/              Feature store per system
    models/                Model registry per system
  execution_cache/         Cached exec-adapter results
```

---

## Core Data Model

`CandidateRecord` is the universal data carrier. A single record is created
during candidate generation and accumulates fields as it passes through
successive stages. When generation came from a Zomic-authored design, the
`provenance` block also carries `zomic_design` and `prototype_library_path`.

```
CandidateRecord
  |
  |-- (generator)  base fields: composition, structure, coordinates, provenance
  |
  |-- (screen)     + screen dict: relaxed energy, filter flags, shortlist rank
  |
  |-- (hifi)       + digital_validation record:
  |                    committee energies, uncertainty estimate,
  |                    hull distance proxy, phonon stability flag,
  |                    MD stability flag, XRD match score
  |
  |-- (rank)       + final rank and score
  |
  |-- (report)     + provenance dict: full lineage of backend versions,
                     config hashes, run IDs
```

All candidate-oriented files use JSONL format (one JSON object per line).
Reports, manifests, and calibration files use plain JSON.

---

## Backend Adapter System

The `backends/` package provides four execution tiers, selectable via the
YAML configuration file:

| Tier             | Behavior                                                    |
|------------------|-------------------------------------------------------------|
| **mock**         | Returns deterministic fixture data. No external calls.      |
| **fixture-backed** | Returns pinned snapshot data from `data/external/pinned/`.|
| **exec**         | Runs external commands (shell subprocesses) with result caching in `data/execution_cache/`. |
| **native**       | Direct Python calls to computational backends (MACE, CHGNet, pymatgen). |

The adapter interface is uniform: domain code calls the same functions
regardless of which tier is active. The tier is resolved at startup from the
configuration and injected into the domain functions by `cli.py`.

## Zomic Bridge Boundary

The Zomic bridge is intentionally narrow:

- `vZome core` compiles and executes `.zomic` scripts
- labeled VM locations are exported as exact geometry JSON
- `materials-discovery` converts those labeled points into orbit-library JSON
- downstream stages operate only on standard `CandidateRecord` structures

This keeps design authoring and visualization in vZome terms without making the
screening, validation, and ranking stages depend on the desktop application.

```
cli.py
  |
  v
resolve_backend(config.backend_mode)
  |
  +---> MockAdapter        (mode: "mock")
  +---> FixtureAdapter     (mode: "fixture")
  +---> ExecAdapter         (mode: "exec")
  +---> NativeAdapter       (mode: "native")
```

---

## Key Architectural Decisions

1. **JSONL as the interchange format.** Candidate files are JSONL (one JSON
   object per line). Reports, manifests, and calibration outputs are plain
   JSON. No binary formats are used for pipeline artifacts.

2. **Accumulative record model.** `CandidateRecord` is not transformed into
   different types between stages. Instead, each stage adds fields to the
   same record, so downstream stages can inspect any upstream result without
   separate lookups.

3. **Backend adapter abstraction.** Four execution tiers (mock,
   fixture-backed, exec, native) share one interface. This allows tests to
   run with deterministic fixtures while production uses real computational
   backends, with no changes to domain logic.

4. **Config-driven pipeline.** A single YAML file controls all pipeline
   behavior, including backend selection, thresholds, batch sizes, and
   output paths. The `SystemConfig` object is the sole configuration
   authority.

5. **Filesystem as the state store.** There is no database. All intermediate
   and final results are files under `data/`. Manifests with content hashes
   provide traceability. The `execution_cache/` directory prevents redundant
   recomputation in exec mode.

6. **CLI as the orchestrator.** `cli.py` is the only file that imports from
   multiple domain packages. Domain packages depend only on `common/` (and
   `hifi_digital/` additionally on `backends/`). This keeps the dependency
   graph shallow and the domain packages independently testable.

7. **Zomic as the LLM representation format.** [PLANNED] Rather than
   generating coordinates or CIF text, LLMs generate Zomic scripts that are
   compiled by the existing vZome core. This ensures that LLM output is either
   syntactically valid (and geometrically exact via the golden field) or
   rejected at parse time — there is no "approximately right" failure mode.
   The Zomic language's native aperiodicity makes it uniquely suited for
   quasicrystal generation, unlike CIF which requires periodic boundary
   conditions. See [LLM Integration](llm-integration.md).
