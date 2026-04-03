# Backend Adapter System

This document describes the backend adapter system used by the materials discovery
pipeline. The system provides a layered abstraction over data ingestion and
candidate validation, allowing the same pipeline stages to run against mock data,
pinned fixture snapshots, external executables, or native Python scientific
libraries.

---

## Protocol Hierarchy

All adapter contracts are defined in `backends/types.py` using frozen dataclasses
for return types and structural-typing protocols for adapter interfaces.

### Dataclasses

Each dataclass is frozen (immutable after construction).

| Dataclass | Fields | Purpose |
|---|---|---|
| `IngestBackendInfo` | `name: str`, `version: str` | Identifies an ingest backend |
| `AdapterInfo` | `name: str`, `version: str` | Identifies a validation adapter |
| `CommitteeEvaluation` | `energies: dict[str, float]` | Result of committee-of-models energy evaluation |
| `PhononEvaluation` | `imaginary_modes: int` | Result of phonon stability check |
| `MdEvaluation` | `stability_score: float` | Result of molecular dynamics stability assessment |
| `XrdEvaluation` | `confidence: float` | Result of X-ray diffraction pattern comparison |

### Protocols

Protocols use structural (duck) typing. Any object that provides the required
methods satisfies the protocol without explicit inheritance.

**IngestBackend**

```python
class IngestBackend(Protocol):
    def info(self) -> IngestBackendInfo: ...
    def load_rows(self, config, fixture_path) -> list[dict]: ...
```

Responsible for loading raw candidate rows from a data source.

**CommitteeAdapter**

```python
class CommitteeAdapter(Protocol):
    def info(self) -> AdapterInfo: ...
    def evaluate_candidate(self, config, candidate) -> CommitteeEvaluation: ...
```

**PhononAdapter**

```python
class PhononAdapter(Protocol):
    def info(self) -> AdapterInfo: ...
    def evaluate_candidate(self, config, candidate) -> PhononEvaluation: ...
```

**MdAdapter**

```python
class MdAdapter(Protocol):
    def info(self) -> AdapterInfo: ...
    def evaluate_candidate(self, config, candidate) -> MdEvaluation: ...
```

**XrdAdapter**

```python
class XrdAdapter(Protocol):
    def info(self) -> AdapterInfo: ...
    def evaluate_candidate(self, config, candidate) -> XrdEvaluation: ...
```

All four validation adapters share the same shape: `info()` returns an
`AdapterInfo`, and `evaluate_candidate()` accepts a config object and a candidate
dict, returning the appropriate evaluation dataclass.

---

## Registry

The registry (`backends/registry.py`) maps `(mode, adapter_name)` tuples to
concrete adapter instances.

### Lookup Tables

```python
_INGEST_BACKENDS = {
    ("mock", "hypodx_fixture"): MockFixtureIngestBackend(),
    ("real", "hypodx_pinned_v2026_03_09"): RealHypodxPinnedIngestBackend(),
}

_COMMITTEE_ADAPTERS = {
    ("real", "committee_fixture_fallback_v2026_03_09"): FixtureBackedCommitteeAdapter(),
    ("real", "committee_exec_cache_v1"): ExecCommitteeAdapter(),
}

# Similar tables exist for _PHONON_ADAPTERS, _MD_ADAPTERS, _XRD_ADAPTERS
```

### Dispatch

Each adapter type has a corresponding resolve function:

- `resolve_ingest_backend(mode, adapter_name)` -- looks up `(mode, adapter_name)`
  in `_INGEST_BACKENDS`
- `resolve_committee_adapter(mode, adapter_name)` -- looks up in
  `_COMMITTEE_ADAPTERS`
- Similar functions for phonon, MD, and XRD adapters

When the requested `(mode, adapter_name)` pair is not found, the resolve function
falls back to the default adapter name for the given mode.

### Default Adapter Names

| Mode | Ingest Default | Validation Default Pattern |
|---|---|---|
| `mock` | `hypodx_fixture` | (handled inline by stage modules) |
| `real` | `hypodx_pinned_v2026_03_09` | `*_fixture_fallback_v2026_03_09` |

---

## Four Adapter Layers

The system is organized into four layers of increasing capability and external
dependency. Each layer builds on the contracts defined in the protocol hierarchy.

### Layer 1: Mock

**Module:** `backends/ingest_mock.py`

`MockFixtureIngestBackend` loads candidate rows from the fixture file at
`data/external/fixtures/hypodx_sample.json`.

For validation stages, mock behavior is handled directly inside the stage modules
(`relax_fast.py`, `committee_relax.py`, etc.) rather than through separate mock
adapter classes. Each stage module checks `config.backend.mode == "mock"` and, when
true, produces deterministic pseudo-random results seeded from a hash of the
candidate ID.

This means no separate mock adapters are needed for the four validation protocols.
The mock path is self-contained within each stage, keeping the mock implementation
simple and avoiding unnecessary adapter boilerplate.

### Layer 2: Fixture-Backed

**Module:** `backends/validation_real_fixtures.py`

Concrete classes:

- `FixtureBackedCommitteeAdapter`
- `FixtureBackedPhononAdapter`
- `FixtureBackedMdAdapter`
- `FixtureBackedXrdAdapter`

These adapters load precomputed results from a pinned validation snapshot JSON file.
When `evaluate_candidate` is called, the adapter looks up the candidate by its
`candidate_id` in the snapshot data. If the candidate is not found, the adapter
falls back to deterministic default values.

This layer is used for reproducible real-mode runs that do not require any external
computational tools. It is particularly useful for CI pipelines and regression
testing, where results must be identical across runs.

### Layer 3: Exec

**Module:** `backends/validation_real_exec.py`

Concrete classes:

- `ExecCommitteeAdapter`
- `ExecPhononAdapter`
- `ExecMdAdapter`
- `ExecXrdAdapter`

These adapters run external commands specified in the pipeline configuration. The
command strings support template placeholders that are expanded at invocation time:

| Placeholder | Expanded To |
|---|---|
| `{input}` | Path to a temporary JSON file containing the candidate data |
| `{output}` | Path where the external command should write its result JSON |
| `{python}` | Path to the Python interpreter in the current environment |
| `{workspace_root}` | Root directory of the workspace |
| `{stage}` | Name of the current pipeline stage |

**Execution flow:**

1. The adapter writes the candidate dict as JSON to a temporary input file.
2. It expands the command template with the placeholder values.
3. It runs the command as a subprocess.
4. It reads the result JSON from the output file path.
5. It constructs the appropriate evaluation dataclass from the result.

**Caching:** Results are cached in the directory
`data/execution_cache/{system}/{stage}/`. Cache keys are computed from the
combination of `candidate_id`, stage name, and a digest of the relevant
configuration values. A cache hit skips the subprocess execution entirely.

### Layer 4: Native

**Module:** `backends/native_providers.py`

Native adapters make direct Python calls to scientific computing libraries:

- **MACE** -- machine-learned interatomic potential evaluations
- **CHGNet** -- graph neural network force field
- **MatterSim** -- materials simulation framework
- **pymatgen** -- Python Materials Genomics library
- **ASE** -- Atomic Simulation Environment

These providers require the `--extra mlip` optional dependencies to be installed.

Structure conversion uses helper functions from `structure_realization.py`:

- `build_ase_atoms(candidate)` -- converts a candidate dict to an ASE `Atoms` object
- `build_pymatgen_structure(candidate)` -- converts a candidate dict to a pymatgen
  `Structure` object

**Provider keys:**

| Key | Library | Purpose |
|---|---|---|
| `ase_committee_v1` | ASE + MACE/CHGNet | Committee energy evaluation |
| `mace_hessian_v1` | MACE | Phonon/Hessian evaluation |
| `ase_langevin_v1` | ASE | MD stability via Langevin dynamics |
| `pymatgen_xrd_v1` | pymatgen | XRD pattern generation and comparison |

Native providers do not run as standalone adapters. Instead, they are invoked behind
the exec adapter layer through dedicated runner modules (`run_committee_backend.py`,
`run_phonon_backend.py`, etc.). The exec adapter spawns a subprocess that imports
and calls the native provider, communicating via the JSON input/output contract
described above.

---

## Config Progression

Pipeline YAML configuration controls which adapter layer is active. The layers are
selected through a combination of `mode`, adapter name, and additional settings.

### 1. Mock Mode

No `backend` section is required in the YAML. The pipeline defaults to mock mode,
which uses `MockFixtureIngestBackend` for ingestion and inline deterministic logic
for validation.

```yaml
# Minimal config -- mock mode is the default
pipeline:
  system: example_system
```

### 2. Real Mode with Fixture Fallback

Set `mode: real` and use the fixture-backed adapters. A pinned snapshot file
provides the validation results.

```yaml
backend:
  mode: real
  # Fixture-fallback adapters are the defaults for real mode
```

### 3. Real Mode with Exec Cache

Set `mode: real`, specify exec adapters, and provide the external commands and cache
directory.

```yaml
backend:
  mode: real
  committee_adapter: committee_exec_cache_v1
  committee_command: "{python} -m runners.run_committee_backend {input} {output}"
  phonon_adapter: phonon_exec_cache_v1
  phonon_command: "{python} -m runners.run_phonon_backend {input} {output}"
  md_adapter: md_exec_cache_v1
  md_command: "{python} -m runners.run_md_backend {input} {output}"
  xrd_adapter: xrd_exec_cache_v1
  xrd_command: "{python} -m runners.run_xrd_backend {input} {output}"
  validation_cache_dir: data/execution_cache
```

### 4. Real Mode with Native Providers

Same as exec cache, but the command lines point to runner modules that load native
Python providers internally.

```yaml
backend:
  mode: real
  committee_adapter: committee_exec_cache_v1
  committee_command: "{python} -m runners.run_committee_backend {input} {output}"
  # ... similar for phonon, md, xrd
  native_provider:
    committee: ase_committee_v1
    phonon: mace_hessian_v1
    md: ase_langevin_v1
    xrd: pymatgen_xrd_v1
```

---

## How to Add a New Adapter

Adding a new adapter involves three steps: implement the protocol, register in the
registry, and add configuration entries.

### Step 1: Implement the Protocol

Create a new class that satisfies the relevant protocol from `backends/types.py`.
No base class inheritance is required -- Python structural typing handles
conformance automatically.

For example, to add a new committee adapter:

```python
# backends/my_new_committee.py

from backends.types import AdapterInfo, CommitteeEvaluation


class MyNewCommitteeAdapter:
    """Committee adapter backed by a new evaluation method."""

    def info(self) -> AdapterInfo:
        return AdapterInfo(name="my_new_committee", version="v1")

    def evaluate_candidate(self, config, candidate) -> CommitteeEvaluation:
        # Perform evaluation logic here.
        energies = _run_my_evaluation(candidate)
        return CommitteeEvaluation(energies=energies)
```

The key requirements are:

- `info()` must return an `AdapterInfo` (or `IngestBackendInfo` for ingest
  backends) with a `name` and `version`.
- `evaluate_candidate()` (or `load_rows()` for ingest backends) must accept a
  `config` object and the appropriate input, returning the correct frozen
  dataclass.
- The returned dataclass must be one of the types defined in `backends/types.py`.

### Step 2: Register in the Registry

Add the adapter instance to the appropriate lookup table in
`backends/registry.py`.

```python
from backends.my_new_committee import MyNewCommitteeAdapter

_COMMITTEE_ADAPTERS = {
    # ... existing entries ...
    ("real", "my_new_committee_v1"): MyNewCommitteeAdapter(),
}
```

The key is a `(mode, adapter_name)` tuple. The `mode` is typically `"real"` for
production adapters or `"mock"` for test adapters. The `adapter_name` is a string
that will be referenced from the pipeline YAML configuration.

If the new adapter should be the default for a given mode, update the default
mapping as well.

### Step 3: Add Config Entries

Update the pipeline YAML to reference the new adapter by name.

```yaml
backend:
  mode: real
  committee_adapter: my_new_committee_v1
```

If the adapter requires additional configuration (command paths, file locations,
provider keys), add those fields to the `backend` section and read them from the
`config` object inside `evaluate_candidate()`.

### Testing the New Adapter

1. **Unit test:** Write a test that constructs the adapter directly and calls
   `evaluate_candidate()` with a sample candidate dict. Verify the returned
   dataclass has the expected field values.
2. **Integration test:** Run the pipeline in real mode with the new adapter name
   in the YAML config. Confirm the adapter is resolved correctly by the registry
   and produces valid stage outputs.
3. **Protocol conformance:** The structural typing system will catch missing
   methods at the call site. If the adapter is missing `info()` or
   `evaluate_candidate()` with the correct signature, the pipeline will raise a
   `TypeError` at dispatch time.
