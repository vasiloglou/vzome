# Materials Discovery Concerns

## Highest-Risk Areas

## 1. `cli.py` is the orchestration bottleneck

File:

- `materials-discovery/src/materials_discovery/cli.py`

Concern:

- Nearly all stage wiring, path construction, manifest writing, and user-facing
  error handling live in one module.
- Small changes to stage order, artifact naming, or summary contracts can have
  wide effects.

Why it matters:

- It is the main coordination point for the whole subsystem.
- Refactors here need broader regression coverage than most other files.

## 2. Filesystem naming is part of the contract

Files:

- `materials-discovery/src/materials_discovery/common/io.py`
- `materials-discovery/src/materials_discovery/cli.py`

Concern:

- The system behaves like a file-backed database with implicit contracts encoded
  in filenames, slugs, and expected directory layout.
- `workspace_root()` and `_system_slug()`/`_batch_slug()` are operationally critical.

Why it matters:

- Renaming or relocating artifacts can silently break downstream stages.
- The architecture assumes the subtree layout is stable.

## 3. Zomic export depends on the broader fork staying healthy

File:

- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`

Concern:

- This module assumes the repo-root Gradle wrapper exists and that
  `:core:zomicExport` is callable.
- It also depends on local Java discovery and repo-relative path layout.

Why it matters:

- This is the least self-contained part of the subsystem.
- Failures here are environmental as often as they are logical.

## 4. Real/fixture/exec/native paths can diverge

Files:

- `materials-discovery/src/materials_discovery/backends/registry.py`
- `materials-discovery/src/materials_discovery/backends/validation_real_fixtures.py`
- `materials-discovery/src/materials_discovery/backends/validation_real_exec.py`
- `materials-discovery/src/materials_discovery/backends/native_providers.py`

Concern:

- Multiple runtime modes are intentionally supported, but they are not equally
  exercised in normal fast CI.
- Behavior can drift between fixture-backed determinism and real/native execution.

Why it matters:

- A change that looks harmless in mock mode may fail later in scheduled/manual jobs
  or on a developer machine with different extras installed.

## 5. Schema changes are expensive

File:

- `materials-discovery/src/materials_discovery/common/schema.py`

Concern:

- `SystemConfig`, `CandidateRecord`, and summary models are used across almost
  every stage and many tests.

Why it matters:

- A schema tweak can cascade into config files, persisted JSONL artifacts,
  manifests, reports, and test fixtures.

## Medium-Risk Design Frictions

### Repeated manifest/calibration boilerplate

The manifest-writing pattern is consistent, which is good, but much of it is
repeated per command in `cli.py`.

Risk:

- copy/paste drift across commands
- inconsistent output-path sets between stages

### Report stage picks only one validated artifact path

Relevant code:

- `materials-discovery/src/materials_discovery/cli.py`

Concern:

- `report` gathers matching validated files and only stores the first one in the
  pipeline manifest when multiple validated batches exist.

Risk:

- lineage can become incomplete or misleading in multi-batch workflows

### Checked-in workspace state can blur code vs. data

The subtree contains real runtime directories such as:

- `materials-discovery/data/`
- `materials-discovery/.venv/`
- `materials-discovery/.pytest_cache/`

Risk:

- easier local experimentation
- but also easier confusion about what is source, fixture, cache, or disposable state

## Safest Contribution Areas

If the goal is low-risk contribution, start with:

- tests in `materials-discovery/tests/`
- docs in `materials-discovery/developers-docs/`
- config additions in `materials-discovery/configs/systems/`
- small utilities or metrics work in `materials-discovery/src/materials_discovery/common/`

Delay changes to these until you have the map in your head:

- `materials-discovery/src/materials_discovery/cli.py`
- `materials-discovery/src/materials_discovery/common/schema.py`
- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
