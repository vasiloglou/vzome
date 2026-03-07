# Contributing to materials-discovery

Developer guide for the no-DFT materials discovery pipeline.

## 1. Development Setup

The project uses [hatchling](https://hatch.pypa.io/) as its build backend and [uv](https://docs.astral.sh/uv/) as the project manager. Python 3.11 or later is required.

Clone the repository, then install in one of three configurations depending on the work you are doing.

**Basic (linting, unit tests, schema work):**

```bash
cd materials-discovery
uv sync --extra dev
```

**With ML interatomic potentials (CHGNet, MACE, phonopy, pymatgen):**

```bash
uv sync --extra dev --extra mlip
```

**Full (adds pandas/pyarrow analysis tools):**

```bash
uv sync --extra dev --extra mlip --extra analysis
```

Core dependencies installed in every configuration: `typer`, `pydantic`, `pyyaml`, `numpy`.

## 2. Running Tests

The test suite lives in `tests/` (21 test files). Tests use `pytest` with `src/` on the Python path.

**Unit tests only (default):**

```bash
uv run pytest
```

**Integration tests (snapshot-backed, require fixture data):**

```bash
uv run pytest -m integration
```

**All tests with coverage:**

```bash
uv run pytest --cov=materials_discovery
```

**Single test file:**

```bash
uv run pytest tests/test_schema.py -v
```

Integration tests are marked with `@pytest.mark.integration` and depend on real-mode adapter fixtures. They run against pinned snapshot data so results are deterministic.

## 3. Linting and Type Checking

The project enforces strict static analysis. Run all three checks before opening a PR.

**Ruff lint (E, F, I, UP, B rules at 100-char line length):**

```bash
uv run ruff check src/ tests/
```

**Ruff format check:**

```bash
uv run ruff format --check src/ tests/
```

**Auto-fix lint issues and formatting:**

```bash
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
```

**Mypy (strict mode, all strict options enabled):**

```bash
uv run mypy src/materials_discovery/
```

Ruff is configured for Python 3.11 target. The ignored rules are `B008` (function call in default argument -- required by typer) and `B904` (raise-without-from in exception chains).

## 4. How to Add a New Chemical System

A chemical system (e.g., Al-Cu-Fe) is defined by a YAML configuration file passed to every CLI command via `--config`. To add support for a new system:

### 4a. Register element data

Open `src/materials_discovery/common/chemistry.py`. Add entries to both lookup tables:

- `ELEMENT_PROPERTIES` -- atomic number, covalent radius, Pauling electronegativity, valence electron count for each new element.
- `PAIR_MIXING_ENTHALPY_EV` -- approximate pairwise mixing enthalpy (eV/atom) for every pair of elements in the system. Keys are alphabetically sorted tuples, e.g., `("Al", "Cu")`.

### 4b. Create the system config YAML

The config file declares the system name, element list, composition bounds, lattice parameters, backend mode, and generation parameters. See the `SystemConfig` model in `src/materials_discovery/common/schema.py` for the full schema. Refer to [configuration-reference.md](configuration-reference.md) for field descriptions and examples.

### 4c. (Optional) Add prototype orbit libraries

If the system uses known approximant structure templates, create a JSON orbit library file in `data/prototypes/` and register the path in `SYSTEM_TEMPLATE_PATHS` inside `src/materials_discovery/generator/approximant_templates.py`.

### 4d. (Optional) Add a Zomic-authored design

If the system should be authored procedurally in vZome terms instead of starting from
a fixed prototype JSON:

1. Create a `.zomic` file under `designs/zomic/`.
2. Add a companion design YAML that conforms to `ZomicDesignConfig`.
3. Label every VM location that should become an atomic site.
4. Use orbit-style label prefixes such as `shell.01`, `core.01`, or `shell_01`.
5. Point the system config at the design with `zomic_design: designs/zomic/your_design.yaml`.

Validate the bridge directly:

```bash
uv run mdisc export-zomic --design designs/zomic/your_design.yaml
uv run mdisc generate --config configs/systems/your_system.yaml --count 32
```

### 4e. Validate

Run the full pipeline in mock mode to verify the new system config:

```bash
uv run mdisc generate --config path/to/new_system.yaml --count 100 --seed 42
uv run mdisc screen --config path/to/new_system.yaml
```

## 5. How to Add a New Backend Adapter

Backend adapters implement the Protocol interfaces defined in `src/materials_discovery/backends/types.py`. There are five adapter protocols:

| Protocol | Method | Return type |
|---|---|---|
| `IngestBackend` | `load_rows(config, fixture_path)` | `list[dict[str, Any]]` |
| `CommitteeAdapter` | `evaluate_candidate(config, candidate)` | `CommitteeEvaluation` |
| `PhononAdapter` | `evaluate_candidate(config, candidate)` | `PhononEvaluation` |
| `MdAdapter` | `evaluate_candidate(config, candidate)` | `MdEvaluation` |
| `XrdAdapter` | `evaluate_candidate(config, candidate)` | `XrdEvaluation` |

Every adapter must also expose an `info()` method returning `IngestBackendInfo` or `AdapterInfo` (name + version string).

### Steps

1. **Implement the protocol.** Create a new module in `src/materials_discovery/backends/` (or extend an existing one). Your class must satisfy the protocol structurally -- no base class inheritance required.

2. **Register in the lookup table.** Open `src/materials_discovery/backends/registry.py` and add your adapter instance to the appropriate registry dict (e.g., `_COMMITTEE_ADAPTERS`, `_PHONON_ADAPTERS`). The key is a `(mode, adapter_name)` tuple. Optionally add a default mapping in the corresponding `_DEFAULT_*_ADAPTERS` dict.

3. **Add config YAML entries.** Set the adapter name in the system config under the appropriate field (e.g., `backend.committee_adapter`, `backend.phonon_adapter`). The config `backend.mode` plus the adapter name must match a registered key.

4. **Write tests.** Add test coverage in `tests/`. For adapters that call external tools, use the fixture-backed pattern (`validation_real_fixtures.py`) or the execution-cache pattern (`execution_cache.py`).

See [backend-system.md](backend-system.md) for the full adapter lifecycle and resolution logic.

## 6. How to Add a New Pipeline Stage

The CLI exposes pipeline stages as typer commands. Currently there are seven: `ingest`, `generate`, `screen`, `hifi-validate`, `hifi-rank`, `active-learn`, and `report`.

### Steps

1. **Create the stage module.** Place it in the appropriate subpackage under `src/materials_discovery/`:

   | Subpackage | Purpose |
   |---|---|
   | `data/` | Ingestion, data loading |
   | `generator/` | Candidate structure generation |
   | `screen/` | Fast screening and threshold filtering |
   | `hifi_digital/` | High-fidelity digital validation |
   | `active_learning/` | Surrogate model training and batch selection |
   | `diffraction/` | XRD simulation and reporting |

2. **Define a summary model.** Add a Pydantic `BaseModel` subclass in `src/materials_discovery/common/schema.py` for the stage's JSON output. Follow the existing pattern (`ScreenSummary`, `HifiRankSummary`, etc.). See [data-schema-reference.md](data-schema-reference.md) for the full schema catalog.

3. **Add the typer command.** In `src/materials_discovery/cli.py`, register a new `@app.command("stage-name")` function. Follow the established pattern:
   - Accept `--config` as a required `Path` option.
   - Load and validate `SystemConfig`.
   - Write output to `workspace_root() / "data" / "<stage_dir>/"`.
   - Build a stage manifest via `build_manifest()`.
   - Echo the summary model as JSON.
   - Catch `FileNotFoundError | ValidationError | ValueError` and exit with code 2.

4. **Write tests.** Add a `tests/test_<stage_name>.py` file. Unit tests should run without the `integration` marker; snapshot-backed tests should use `@pytest.mark.integration`.

## 7. Code Style Conventions

### Python version features

Target Python 3.11+. Use modern syntax:

- `match` statements for multi-branch dispatch.
- PEP 604 union syntax: `str | None` instead of `Optional[str]`.
- `from __future__ import annotations` at the top of every module.

### Type safety

Mypy runs in strict mode with all strict flags enabled. Every function must have full type annotations. Use `Protocol` classes for structural subtyping (as in `backends/types.py`). Avoid `Any` except where interfacing with untyped external libraries.

### Data modeling

- Use `pydantic.BaseModel` for serializable schemas (configs, summaries, candidate records).
- Use `@dataclass(frozen=True)` for internal value objects that do not need JSON serialization (e.g., `ElementProperties`, `CommitteeEvaluation`).

### Formatting rules

- 100-character line length.
- Ruff rules: `E` (pycodestyle errors), `F` (pyflakes), `I` (isort), `UP` (pyupgrade), `B` (bugbear).
- Imports are sorted by isort via ruff.

### CLI conventions

- The CLI entry point is `mdisc` (mapped to `materials_discovery.cli:app`).
- All commands emit a JSON summary to stdout on success.
- Errors go to stderr and exit with code 2.
- File paths in summaries are always absolute.

## Quick Reference

```bash
# Install
uv sync --extra dev

# Test
uv run pytest
uv run pytest -m integration
uv run pytest --cov=materials_discovery

# Lint
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/materials_discovery/

# Run a pipeline stage
uv run mdisc generate --config system.yaml --count 1000 --seed 42
uv run mdisc screen --config system.yaml
uv run mdisc hifi-validate --config system.yaml --batch top500
uv run mdisc hifi-rank --config system.yaml
uv run mdisc active-learn --config system.yaml
uv run mdisc report --config system.yaml
```

## Related Documentation

- [backend-system.md](backend-system.md) -- adapter protocols, registry, mock vs. real modes
- [configuration-reference.md](configuration-reference.md) -- YAML config fields and validation rules
- [data-schema-reference.md](data-schema-reference.md) -- Pydantic models, JSONL formats, manifest structure
- [pipeline-stages.md](pipeline-stages.md) -- stage-by-stage data flow and CLI usage
- [architecture.md](architecture.md) -- package layout and design rationale
