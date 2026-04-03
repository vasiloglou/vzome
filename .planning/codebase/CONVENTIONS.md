# Materials Discovery Conventions

## Language and Typing

The codebase consistently uses modern Python typing and annotation patterns:

- `from __future__ import annotations` at module top
- PEP 604 unions such as `Path | None`
- explicit return types on functions
- strict mypy posture from `materials-discovery/pyproject.toml`

Serializable contracts use Pydantic:

- `materials-discovery/src/materials_discovery/common/schema.py`

Internal protocol/value objects use dataclasses and `Protocol`:

- `materials-discovery/src/materials_discovery/backends/types.py`

## CLI Contract

Command conventions in
`materials-discovery/src/materials_discovery/cli.py`:

- every stage is a Typer command
- success path prints a JSON summary to stdout
- user/config/input errors are emitted to stderr and exit with code `2`
- `--config` is the standard required option
- file paths returned in summaries are absolute strings

## Filesystem Conventions

Relative paths are normalized against `workspace_root()` from
`materials-discovery/src/materials_discovery/common/io.py`.

Common write pattern:

1. compute a deterministic output path under `materials-discovery/data/`
2. call `ensure_parent()`
3. write JSON/JSONL
4. emit manifest and optional calibration sidecar

Naming is slug-based:

- system names become filenames via `_system_slug()`
- validation batches use `_batch_slug()`

## Data Modeling Conventions

- `SystemConfig` is the source of truth for runtime configuration
- `CandidateRecord` is enriched across stages rather than replaced
- `provenance` carries lineage metadata
- validation status accumulates under `digital_validation`

This means schema changes are high-impact and should be paired with test updates.

## Error Handling Style

Common error pattern in `cli.py`:

- expected operational failures raise `FileNotFoundError`, `ValidationError`,
  or `ValueError`
- command wrapper catches them and exits cleanly with code `2`
- unexpected failures are generally not swallowed

## Testing Style

Common patterns in `materials-discovery/tests/`:

- `CliRunner` for command-level tests
- `tmp_path` for isolated filesystem writes
- `MonkeyPatch` when isolating external behavior
- direct `model_validate()` usage to build realistic typed fixtures
- `@pytest.mark.integration` for slower snapshot-backed flows

## Style and Tooling Rules

From `materials-discovery/pyproject.toml` and
`materials-discovery/developers-docs/contributing.md`:

- 100-character line length
- Ruff rules `E`, `F`, `I`, `UP`, `B`
- mypy strict mode
- target Python version `py311`

## Extension Conventions

When adding a new pipeline stage:

- add stage logic under the relevant source package
- add a summary model in `common/schema.py`
- add a command in `cli.py`
- write stage outputs under a dedicated `data/<stage>/` area
- write a manifest via `build_manifest()`
- add a `tests/test_<stage>.py` file

When adding a backend adapter:

- implement the relevant protocol from `backends/types.py`
- register it in `backends/registry.py`
- configure it through YAML, not hard-coded branching

## Repo-Specific Workflow Rule

If you change anything under `materials-discovery/`, update:

- `materials-discovery/Progress.md`

That repo rule applies to code, configs, docs, experiments, and refactors.
