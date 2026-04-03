# Materials Discovery Structure

## Scope Tree

Primary subtree:

```text
materials-discovery/
  README.md
  pyproject.toml
  Progress.md
  configs/
    systems/
  data/
    active_learning/
    benchmarks/
    calibration/
    candidates/
    execution_cache/
    external/
    hifi_validated/
    manifests/
    processed/
    prototypes/
    ranked/
    registry/
    reports/
    screened/
  designs/
    zomic/
  scripts/
  src/materials_discovery/
    active_learning/
    backends/
    common/
    data/
    diffraction/
    generator/
    hifi_digital/
    screen/
    cli.py
  tests/
```

## Key Files and Why They Matter

- `materials-discovery/pyproject.toml`
  Dependency groups, CLI entrypoint, pytest/mypy/ruff config
- `materials-discovery/README.md`
  Operational overview and quickstart
- `materials-discovery/Progress.md`
  Required progress log when changing anything under `materials-discovery/`
- `materials-discovery/src/materials_discovery/cli.py`
  All stage orchestration and stdout/error contract
- `materials-discovery/src/materials_discovery/common/schema.py`
  Shared typed contract for configs, records, summaries, manifests
- `materials-discovery/src/materials_discovery/backends/registry.py`
  Adapter selection table
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
  Narrow bridge back to repo-root Gradle/core

## Package-Level Responsibilities

- `common/`
  Shared IO, schema, chemistry, metrics, manifest helpers
- `data/`
  Ingestion and normalization
- `generator/`
  Candidate generation from templates or Zomic-backed prototypes
- `screen/`
  Fast prefiltering and shortlist ranking
- `hifi_digital/`
  Committee, hull, geometry prefilter, phonon, MD, XRD, final validation
- `active_learning/`
  Surrogate training and batch proposal
- `diffraction/`
  XRD simulation and experiment-facing reports
- `backends/`
  Mock/fixture/exec/native adapter layer

## Config and Runtime Inputs

Main config entrypoints:

- `materials-discovery/configs/systems/al_cu_fe.yaml`
- `materials-discovery/configs/systems/al_cu_fe_real.yaml`
- `materials-discovery/configs/systems/al_cu_fe_exec.yaml`
- `materials-discovery/configs/systems/al_cu_fe_native.yaml`
- `materials-discovery/configs/systems/sc_zn_zomic.yaml`

Structural observation:

- config files, not code branches, choose most runtime behavior
- system additions are mostly configuration-led unless they require new
  chemistry data, templates, or adapters

## Test Layout

Tests are flat and stage-oriented under `materials-discovery/tests/`.

Examples:

- `materials-discovery/tests/test_cli.py`
- `materials-discovery/tests/test_generate.py`
- `materials-discovery/tests/test_hifi_validate.py`
- `materials-discovery/tests/test_validation_exec_adapters.py`
- `materials-discovery/tests/test_real_mode_pipeline.py`

The naming scheme mirrors source concerns closely, which makes it easy to find
coverage for a given module.

## Safe Starting Points for Contributions

Good first places to work:

- `materials-discovery/configs/systems/`
  Add or tune a chemical system config
- `materials-discovery/tests/`
  Add missing tests around an existing behavior
- `materials-discovery/src/materials_discovery/common/`
  Small schema, manifest, or utility improvements
- `materials-discovery/developers-docs/`
  Clarify workflow or architecture docs

Medium-risk but well-bounded work:

- `materials-discovery/src/materials_discovery/backends/`
  Add a new adapter using the existing protocol + registry pattern
- `materials-discovery/src/materials_discovery/screen/`
  Tune ranking/filter logic with tests

High-coordination areas:

- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
- `materials-discovery/src/materials_discovery/common/schema.py`
  when changing persisted JSON contracts
