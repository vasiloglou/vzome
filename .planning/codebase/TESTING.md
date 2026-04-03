# Materials Discovery Testing

## Test Stack

Primary test tooling is configured in `materials-discovery/pyproject.toml`:

- `pytest`
- `typer.testing.CliRunner`
- `pytest-cov`

Quality gates in CI:

- `.github/workflows/materials-discovery.yml`

## Test Organization

Tests live in:

- `materials-discovery/tests/`

The layout is flat and concern-oriented, with one or more files per stage or
supporting subsystem.

Representative files:

- `materials-discovery/tests/test_cli.py`
- `materials-discovery/tests/test_ingest.py`
- `materials-discovery/tests/test_generate.py`
- `materials-discovery/tests/test_screen.py`
- `materials-discovery/tests/test_hifi_validate.py`
- `materials-discovery/tests/test_hifi_rank.py`
- `materials-discovery/tests/test_active_learn.py`
- `materials-discovery/tests/test_report.py`
- `materials-discovery/tests/test_validation_exec_adapters.py`
- `materials-discovery/tests/test_real_mode_pipeline.py`

## Test Modes

### Unit / fast tests

Run in local dev and CI push/PR jobs:

- `uv run pytest -m "not integration"`

These tests cover:

- schema validation
- CLI success/error behavior
- deterministic stage logic
- adapter registry behavior
- exec-cache behavior with fake subprocess scripts

### Integration tests

Marked with `@pytest.mark.integration`.

Run via:

- `uv run pytest -m integration`

These focus on:

- snapshot-backed real-mode behavior
- end-to-end artifact production across multiple stages

Representative file:

- `materials-discovery/tests/test_real_mode_pipeline.py`

## Common Testing Patterns

### CLI contract tests

`materials-discovery/tests/test_cli.py` uses `CliRunner` to assert:

- exit code behavior
- output file creation
- command argument handling

### Typed fixture tests

Many tests build realistic `SystemConfig` and `CandidateRecord` objects via
Pydantic validation instead of loose dict assertions.

### Exec adapter simulation

`materials-discovery/tests/test_validation_exec_adapters.py` creates a temporary
Python script and passes it through adapter command templates to verify:

- command invocation
- cache population
- cache reuse when commands are removed

This is a strong pattern for future external-tool integrations.

## CI Coverage

Current GitHub Actions behavior:

- push/PR/manual: unit tests, Ruff, Mypy
- scheduled/manual: integration tests + `./scripts/run_real_pipeline.sh`

The subsystem has better automated validation than most of the surrounding fork.

## Likely Testing Gaps

Areas that still deserve extra coverage:

- cross-stage regressions when file naming or slug logic changes in `cli.py`
- Zomic export bridge failures and Java/Gradle environment edge cases in
  `generator/zomic_bridge.py`
- native-provider behavior when optional `mlip` dependencies are partially installed
- report/pipeline-manifest behavior when multiple validated batches coexist

## Recommended Safe Contribution Path

If starting small, add or extend tests in:

- `materials-discovery/tests/test_cli.py`
- the stage-specific test file matching the source module you touch

That gives fast feedback without having to change the whole pipeline at once.
