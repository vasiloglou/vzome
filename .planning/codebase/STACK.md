# Materials Discovery Stack

## Scope

This map treats `/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery`
as the project boundary. The rest of the repo is out of scope except where this
subsystem directly depends on it, most notably the Zomic export bridge in
`materials-discovery/src/materials_discovery/generator/zomic_bridge.py`.

## Primary Language and Runtime

- Python 3.11+ is the main implementation language.
- Packaging/build backend: `hatchling` in
  `materials-discovery/pyproject.toml`.
- Project/env manager: `uv`.
- CLI entrypoint: `mdisc`, mapped to
  `materials_discovery.cli:app`.

## Core Runtime Libraries

Always-on dependencies from `materials-discovery/pyproject.toml`:

- `typer` for the command-line interface in
  `materials-discovery/src/materials_discovery/cli.py`
- `pydantic` for configs, records, summaries, and manifests in
  `materials-discovery/src/materials_discovery/common/schema.py`
- `pyyaml` for YAML config loading in
  `materials-discovery/src/materials_discovery/common/io.py`
- `numpy` for numeric work in geometry/screening/analysis code

Optional dependency groups:

- `dev`: `pytest`, `pytest-cov`, `ruff`, `mypy`, `types-PyYAML`
- `mlip`: `ase`, `pymatgen`, `spglib`, `phonopy`, `pycalphad`, `chgnet`,
  `mace-torch`
- `analysis`: `pandas`, `pyarrow`

## Build, Test, and Quality Tooling

Commands described in
`materials-discovery/developers-docs/contributing.md`
and enforced in
`.github/workflows/materials-discovery.yml`:

- Install: `uv sync --extra dev`
- Unit tests: `uv run pytest -m "not integration"`
- Integration tests: `uv run pytest -m integration`
- Lint: `uv run ruff check .`
- Typecheck: `uv run mypy src`

Static analysis posture:

- Ruff with `E`, `F`, `I`, `UP`, `B`
- 100-character line length
- Mypy strict mode

## Data and File Formats

The subsystem is filesystem-backed. There is no database.

- Config input: YAML in `materials-discovery/configs/systems/`
- Intermediate pipeline records: JSONL in `materials-discovery/data/`
- Manifests/calibration/reports: JSON in `materials-discovery/data/`
- Zomic design input: YAML + `.zomic` files in
  `materials-discovery/designs/zomic/`

The root locator is `workspace_root()` in
`materials-discovery/src/materials_discovery/common/io.py`, which anchors all
relative data writes under the `materials-discovery/` directory.

## Main Execution Surfaces

- CLI orchestration:
  `materials-discovery/src/materials_discovery/cli.py`
- Shared typed contracts:
  `materials-discovery/src/materials_discovery/common/schema.py`
- Stage packages:
  `materials-discovery/src/materials_discovery/data/`
  `materials-discovery/src/materials_discovery/generator/`
  `materials-discovery/src/materials_discovery/screen/`
  `materials-discovery/src/materials_discovery/hifi_digital/`
  `materials-discovery/src/materials_discovery/active_learning/`
  `materials-discovery/src/materials_discovery/diffraction/`
- Backend abstraction layer:
  `materials-discovery/src/materials_discovery/backends/`

## Development Surfaces by Change Type

- Add or change a system: `materials-discovery/configs/systems/`
- Add or change a schema: `materials-discovery/src/materials_discovery/common/schema.py`
- Add or change orchestration: `materials-discovery/src/materials_discovery/cli.py`
- Add or change a backend adapter:
  `materials-discovery/src/materials_discovery/backends/`
- Add or change stage logic:
  stage-specific package under `materials-discovery/src/materials_discovery/`
- Add or change tests: `materials-discovery/tests/`

## Direct Cross-Repo Dependency

The only clearly intentional dependency on the surrounding fork is the Zomic
export bridge:

- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`
- Calls `../gradlew -q :core:zomicExport`
- Requires a working Java runtime and the repo-root Gradle wrapper

For routine pipeline work outside Zomic export, the subsystem behaves like a
mostly standalone Python project.
