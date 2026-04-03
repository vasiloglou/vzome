# Materials Discovery Integrations

## Scope

This document covers integrations used by
`/Users/nikolaosvasiloglou/github-repos/vzome/materials-discovery`.
It intentionally ignores unrelated services elsewhere in the fork.

## Integration Summary

The subsystem is light on remote services and heavy on local integration points.
Most boundaries are one of:

- local file IO under `materials-discovery/data/`
- adapter resolution via config + registry
- subprocess execution for external validation backends
- Gradle/Java invocation for Zomic export

## Config-Driven Backend Resolution

Primary boundary:

- `materials-discovery/src/materials_discovery/backends/registry.py`
- `materials-discovery/src/materials_discovery/backends/types.py`
- `materials-discovery/src/materials_discovery/backends/capabilities.py`

How it works:

- `SystemConfig.backend` selects `mode` plus optional adapter names.
- Registry functions such as `resolve_ingest_backend()` and
  `resolve_committee_adapter()` return protocol-compatible implementations.
- `load_capabilities_matrix()` reads
  `materials-discovery/data/registry/backend_capabilities.yaml`
  so manifests can record which adapter family was active for a stage.

## Ingest Data Sources

Implemented ingest paths:

- Mock ingest from fixture data via
  `materials-discovery/src/materials_discovery/backends/ingest_mock.py`
- Real ingest from pinned snapshot data via
  `materials-discovery/src/materials_discovery/backends/ingest_real_hypodx.py`

Relevant storage:

- `materials-discovery/data/external/fixtures/`
- `materials-discovery/data/external/pinned/`

Current pattern:

- "Real" mode is still reproducible and snapshot-backed, not a live remote API
  integration.

## Validation Backends

Validation adapters are split across two main implementation styles:

- Fixture-backed adapters in
  `materials-discovery/src/materials_discovery/backends/validation_real_fixtures.py`
- Exec/cached adapters in
  `materials-discovery/src/materials_discovery/backends/validation_real_exec.py`

These cover:

- committee relax
- phonon
- MD
- XRD

Exec adapters integrate with external tools through command templates configured
on `SystemConfig.backend.*_command`, with caching handled under:

- `materials-discovery/data/execution_cache/`
- `materials-discovery/src/materials_discovery/backends/execution_cache.py`

Representative tests:

- `materials-discovery/tests/test_validation_exec_adapters.py`
- `materials-discovery/tests/test_validation_adapters.py`

## Native MLIP / Scientific Python Integration

Optional direct Python integrations live behind the `mlip` extra and native
provider support:

- `materials-discovery/src/materials_discovery/backends/native_providers.py`

This is where heavy scientific Python dependencies such as `chgnet`, `mace-torch`,
`phonopy`, `pymatgen`, and related tooling become relevant.

## Zomic / vZome Core Bridge

The most important non-Python boundary is:

- `materials-discovery/src/materials_discovery/generator/zomic_bridge.py`

Behavior:

- Resolves the repo root by walking up from `materials-discovery/`
- Invokes `../gradlew -q :core:zomicExport`
- Requires Java availability, optionally via `JAVA_HOME`
- Writes orbit-library JSON artifacts to
  `materials-discovery/data/prototypes/generated/`

This is the only integration that depends on the broader fork layout being
present and healthy.

## CI Integration

Automation is scoped cleanly to this subsystem in:

- `.github/workflows/materials-discovery.yml`

Two jobs matter:

- `quality-fast`: unit tests, Ruff, Mypy on push/PR/manual runs
- `integration-real`: integration tests and real-mode pipeline on schedule/manual

## Manifest and Provenance Integration

Every stage emits manifest metadata through:

- `materials-discovery/src/materials_discovery/common/manifest.py`
- `materials-discovery/src/materials_discovery/common/pipeline_manifest.py`

This is an internal integration contract rather than an external service, but
it is important operationally because downstream stages and debugging workflows
rely on manifest/provenance consistency.

## What Is Not Integrated

Within the scoped subsystem there is no evidence of:

- a database
- a message queue
- a live web API dependency in the normal path
- an auth provider
- a long-running service process

The architecture is batch-oriented and file-oriented.
