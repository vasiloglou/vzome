# Materials Discovery Architecture

## System Boundary

Treat `materials-discovery/` as a standalone batch pipeline package embedded in
the larger repo. It has one notable upstream dependency, the Zomic export bridge
to repo-root Gradle/core, but otherwise its architecture is self-contained.

## Top-Level Shape

The subsystem is organized around a single orchestration module and several
stage-focused packages:

- Orchestration: `materials-discovery/src/materials_discovery/cli.py`
- Shared contracts/utilities:
  `materials-discovery/src/materials_discovery/common/`
- Stage logic:
  `data/`, `generator/`, `screen/`, `hifi_digital/`,
  `active_learning/`, `diffraction/`
- Adapter boundary:
  `materials-discovery/src/materials_discovery/backends/`

## Architectural Pattern

This is a config-driven, file-backed, batch pipeline.

The pattern is:

1. Load a YAML config into `SystemConfig`
2. Read the previous stage artifact from `materials-discovery/data/`
3. Transform rows into typed `CandidateRecord` or summary objects
4. Write the next stage artifact back to `materials-discovery/data/`
5. Emit stage manifest + calibration JSON
6. Print a JSON summary to stdout

The CLI is intentionally the pipeline coordinator. There is no separate scheduler,
service layer, or database abstraction.

## Main Data Contract

Primary schema module:

- `materials-discovery/src/materials_discovery/common/schema.py`

Important types:

- `SystemConfig`: config contract for all commands
- `CandidateRecord`: the pipeline's main evolving record
- `DigitalValidationRecord`: nested validation state attached to each candidate
- `*Summary` models: JSON stdout contract per command

Architecture implication:

- Most modules communicate through Pydantic models rather than ad hoc dicts.
- A candidate is enriched stage by stage instead of being rebuilt from scratch.

## Stage Flow

Implemented command flow in
`materials-discovery/src/materials_discovery/cli.py`:

- `ingest`
- `generate`
- `export-zomic`
- `screen`
- `hifi-validate`
- `hifi-rank`
- `active-learn`
- `report`

Nominal artifact flow:

- `ingest` writes `data/processed/*_reference_phases.jsonl`
- `generate` writes `data/candidates/*_candidates.jsonl`
- `screen` writes `data/screened/*_screened.jsonl`
- `hifi-validate` writes `data/hifi_validated/*_validated.jsonl`
- `hifi-rank` writes `data/ranked/*_ranked.jsonl`
- `active-learn` writes surrogate, next-batch, feature-store, model-registry outputs
- `report` writes report/XRD outputs and a pipeline manifest

## Adapter Architecture

The adapter boundary isolates data ingestion and high-fidelity validation from
the stage logic.

Key modules:

- `materials-discovery/src/materials_discovery/backends/types.py`
- `materials-discovery/src/materials_discovery/backends/registry.py`

Pattern:

- Stage code calls protocol-shaped adapters.
- Registry lookup chooses mock, fixture-backed, exec, or native implementations.
- Config names are part of the runtime contract.

This keeps most domain modules independent of the specific backend mechanism.

## State Model

Persistent state is entirely filesystem-based under:

- `materials-discovery/data/`

Operationally important subtrees:

- `processed/`, `candidates/`, `screened/`, `hifi_validated/`, `ranked/`
- `active_learning/`, `reports/`
- `calibration/`, `manifests/`
- `registry/features/`, `registry/models/`
- `execution_cache/`

This makes the system easy to inspect manually, but it also means path naming,
slug conventions, and stage order are part of the architecture.

## External Boundary: Zomic Export

The subsystem has one explicit cross-project bridge:

- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`

Architecture role:

- optional pre-generation path for Zomic-authored prototype libraries
- invokes repo-root Gradle and Java
- writes generated prototype assets back into `materials-discovery/data/prototypes/generated/`

## Entry Points for Safe Architectural Work

Lowest-risk extension seams:

- add a new system config in `materials-discovery/configs/systems/`
- add tests in `materials-discovery/tests/`
- add a new backend adapter in `materials-discovery/src/materials_discovery/backends/`
- add a new summary/schema model in
  `materials-discovery/src/materials_discovery/common/schema.py`

Higher-risk coordination points:

- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
- any code that changes artifact naming or manifest conventions
